from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.users.models import UserAccount


class JobPost(models.Model):
    class JobType(models.TextChoices):
        FULLTIME = 'fulltime', '全职'
        PARTTIME = 'parttime', '长期兼职'

    class Status(models.TextChoices):
        OPEN = 'open', '招聘中'
        CLOSED = 'closed', '已关闭'

    enterprise = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='job_posts')
    title = models.CharField(max_length=128)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULLTIME)
    location = models.CharField(max_length=255)
    salary_min = models.IntegerField()
    salary_max = models.IntegerField()
    license_req = models.CharField(max_length=64, blank=True, default='')
    benefits = models.TextField(blank=True, default='')
    responsibilities = models.TextField(blank=True, default='')
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_post'
        ordering = ['-created_at']


class JobApplication(models.Model):
    class Status(models.TextChoices):
        RECOMMENDED = 'recommended', 'AI推荐'
        APPLIED = 'applied', '已投递'
        INTERVIEW = 'interview', '面试中'
        OFFERED = 'offered', '已发Offer'
        HIRED = 'hired', '已入职'
        REJECTED = 'rejected', '已拒绝'

    class Source(models.TextChoices):
        SELF = 'self', '主动投递'
        AI = 'ai', 'AI推荐'

    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    pilot = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='job_applications')
    match_score = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.SELF)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_application'
        unique_together = ('job', 'pilot')


class ChatMessage(models.Model):
    class MsgType(models.TextChoices):
        TEXT = 'text', '文本'
        INTERVIEW = 'interview_invite', '面试邀约'

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    content = models.TextField()
    msg_type = models.CharField(max_length=20, choices=MsgType.choices, default=MsgType.TEXT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']


class LaborContract(models.Model):
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='contract')
    contract_url = models.URLField(blank=True, default='')
    contract_content = models.TextField(blank=True, default='')
    signed_enterprise = models.BooleanField(default=False)
    signed_pilot = models.BooleanField(default=False)
    onboarded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'labor_contract'


class AgencyFee(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '待结算'
        PAID = 'paid', '已结算'

    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='agency_fee')
    fee_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.12)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'agency_fee'
