from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg

from .models import UserAccount, EnterpriseProfile, PilotProfile, PilotResume, CreditReview
from .serializers import (
    UserSerializer, RegisterSerializer, EnterpriseProfileSerializer,
    PilotProfileSerializer, PilotResumeSerializer, CreditReviewSerializer,
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    data = UserSerializer(request.user).data
    if request.user.role == UserAccount.Role.ENTERPRISE and hasattr(request.user, 'enterprise_profile'):
        data['profile'] = EnterpriseProfileSerializer(request.user.enterprise_profile).data
    if request.user.role == UserAccount.Role.PILOT and hasattr(request.user, 'pilot_profile'):
        data['profile'] = PilotProfileSerializer(request.user.pilot_profile).data
        if hasattr(request.user.pilot_profile, 'resume'):
            data['resume'] = PilotResumeSerializer(request.user.pilot_profile.resume).data
    return Response(data)


class PilotProfileViewSet(viewsets.ModelViewSet):
    queryset = PilotProfile.objects.select_related('user').all()
    serializer_class = PilotProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['patch'], url_path='me/location')
    def update_my_location(self, request):
        if request.user.role != UserAccount.Role.PILOT:
            return Response({'detail': '仅飞手可更新位置'}, status=403)
        profile = request.user.pilot_profile
        profile.lat = request.data.get('lat', profile.lat)
        profile.lng = request.data.get('lng', profile.lng)
        profile.online_status = request.data.get('online_status', profile.online_status)
        profile.save()
        return Response(PilotProfileSerializer(profile).data)


class PilotResumeViewSet(viewsets.ModelViewSet):
    queryset = PilotResume.objects.select_related('pilot__user').all()
    serializer_class = PilotResumeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('mine') == '1' and self.request.user.is_authenticated:
            if hasattr(self.request.user, 'pilot_profile'):
                return qs.filter(pilot=self.request.user.pilot_profile)
        return qs

    def perform_update(self, serializer):
        serializer.save()
        pilot = serializer.instance.pilot
        for field in ('license_level', 'years_exp', 'skills', 'real_name'):
            if field in self.request.data:
                setattr(pilot, field, self.request.data[field])
        pilot.save()


class CreditReviewViewSet(viewsets.ModelViewSet):
    queryset = CreditReview.objects.select_related('from_user', 'to_user').all()
    serializer_class = CreditReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        review = serializer.save(from_user=self.request.user)
        avg = CreditReview.objects.filter(to_user=review.to_user).aggregate(a=Avg('score'))['a'] or 3
        # 评价映射到信用画像：基础 500 + 均分*100
        review.to_user.credit_score = min(1000, max(300, int(500 + float(avg) * 100)))
        review.to_user.save(update_fields=['credit_score'])
