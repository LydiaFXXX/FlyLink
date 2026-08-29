from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import UserAccount, PilotProfile
from .models import JobPost, JobApplication, ChatMessage, LaborContract, AgencyFee
from .serializers import (
    JobPostSerializer, JobApplicationSerializer, ChatMessageSerializer,
    LaborContractSerializer, AgencyFeeSerializer,
)


def ai_match_score(job: JobPost, pilot: PilotProfile) -> float:
    score = 50.0
    if job.license_req and job.license_req.lower() in (pilot.license_level or '').lower():
        score += 25
    elif not job.license_req:
        score += 10
    skill_set = set(pilot.skills or [])
    tag_set = set(job.tags or [])
    if skill_set and tag_set:
        overlap = len(skill_set & tag_set) / max(len(tag_set), 1)
        score += overlap * 25
    score += min(pilot.years_exp, 10) * 1.5
    return round(min(score, 100), 2)


class JobPostViewSet(viewsets.ModelViewSet):
    queryset = JobPost.objects.select_related('enterprise').all()
    serializer_class = JobPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('status'):
            qs = qs.filter(status=self.request.query_params['status'])
        if self.request.query_params.get('mine') == '1' and self.request.user.is_authenticated:
            qs = qs.filter(enterprise=self.request.user)
        return qs

    def perform_create(self, serializer):
        job = serializer.save(enterprise=self.request.user)
        # 创建后自动 AI 推荐飞手给企业
        self._ai_recommend(job)

    def _ai_recommend(self, job: JobPost):
        pilots = PilotProfile.objects.select_related('user').all()[:50]
        for p in pilots:
            score = ai_match_score(job, p)
            if score < 55:
                continue
            JobApplication.objects.get_or_create(
                job=job, pilot=p.user,
                defaults={
                    'match_score': score,
                    'status': JobApplication.Status.RECOMMENDED,
                    'source': JobApplication.Source.AI,
                },
            )

    @action(detail=True, methods=['post'])
    def recommend(self, request, pk=None):
        job = self.get_object()
        self._ai_recommend(job)
        apps = job.applications.filter(source=JobApplication.Source.AI)
        return Response(JobApplicationSerializer(apps, many=True).data)


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related('job', 'pilot').prefetch_related('messages').all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == UserAccount.Role.PILOT:
            return qs.filter(pilot=user)
        if user.role == UserAccount.Role.ENTERPRISE:
            return qs.filter(job__enterprise=user)
        return qs

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        pilot = self.request.user
        score = 60.0
        if hasattr(pilot, 'pilot_profile'):
            score = ai_match_score(job, pilot.pilot_profile)
        serializer.save(pilot=pilot, match_score=score, source=JobApplication.Source.SELF,
                        status=JobApplication.Status.APPLIED)

    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        app = self.get_object()
        msg = ChatMessage.objects.create(
            application=app,
            sender=request.user,
            content=request.data.get('content', ''),
            msg_type=request.data.get('msg_type', ChatMessage.MsgType.TEXT),
        )
        if msg.msg_type == ChatMessage.MsgType.INTERVIEW:
            app.status = JobApplication.Status.INTERVIEW
            app.save(update_fields=['status'])
        return Response(ChatMessageSerializer(msg).data)

    @action(detail=True, methods=['post'], url_path='sign-contract')
    def sign_contract(self, request, pk=None):
        app = self.get_object()
        contract, _ = LaborContract.objects.get_or_create(
            application=app,
            defaults={
                'contract_content': f'劳务合同：{app.job.title} - {app.pilot.username}',
                'contract_url': f'/contracts/{app.id}.pdf',
            },
        )
        role = request.user.role
        if role == UserAccount.Role.ENTERPRISE:
            contract.signed_enterprise = True
        if role == UserAccount.Role.PILOT:
            contract.signed_pilot = True
        contract.save()
        if contract.signed_enterprise and contract.signed_pilot:
            app.status = JobApplication.Status.OFFERED
            app.save(update_fields=['status'])
        return Response(LaborContractSerializer(contract).data)

    @action(detail=True, methods=['post'])
    def onboard(self, request, pk=None):
        """入职确认 → 中介费结算。"""
        app = self.get_object()
        if request.user != app.job.enterprise and request.user.role != UserAccount.Role.ADMIN:
            return Response({'detail': '仅企业可确认入职'}, status=403)
        app.status = JobApplication.Status.HIRED
        app.save(update_fields=['status'])
        contract, _ = LaborContract.objects.get_or_create(application=app)
        contract.onboarded_at = timezone.now()
        contract.signed_enterprise = True
        contract.signed_pilot = True
        contract.save()
        mid = (app.job.salary_min + app.job.salary_max) / 2
        rate = Decimal(str(settings.AGENCY_FEE_RATE))
        amount = (Decimal(str(mid)) * rate).quantize(Decimal('0.01'))
        fee, _ = AgencyFee.objects.update_or_create(
            application=app,
            defaults={'fee_rate': rate, 'amount': amount, 'status': AgencyFee.Status.PAID, 'paid_at': timezone.now()},
        )
        return Response({
            'application': JobApplicationSerializer(app).data,
            'agency_fee': AgencyFeeSerializer(fee).data,
        })
