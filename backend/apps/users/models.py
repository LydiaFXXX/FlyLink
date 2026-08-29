from django.contrib.auth.models import AbstractUser
from django.db import models


class UserAccount(AbstractUser):
    class Role(models.TextChoices):
        ENTERPRISE = 'enterprise', '需求企业方'
        PILOT = 'pilot', '个人飞手'
        ADMIN = 'admin', '平台管理员'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PILOT)
    phone = models.CharField(max_length=20, blank=True, default='')
    avatar = models.URLField(blank=True, default='')
    credit_score = models.IntegerField(default=600)

    class Meta:
        db_table = 'user_account'
        verbose_name = '用户账号'


class EnterpriseProfile(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='enterprise_profile')
    company_name = models.CharField(max_length=128)
    license_no = models.CharField(max_length=64, blank=True, default='')
    contact_name = models.CharField(max_length=64, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'enterprise_profile'


class PilotProfile(models.Model):
    class OnlineStatus(models.TextChoices):
        IDLE = 'idle', '空闲'
        BUSY = 'busy', '作业中'
        OFFLINE = 'offline', '离线'

    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='pilot_profile')
    real_name = models.CharField(max_length=64, blank=True, default='')
    license_level = models.CharField(max_length=32, blank=True, default='')
    years_exp = models.IntegerField(default=0)
    online_status = models.CharField(max_length=20, choices=OnlineStatus.choices, default=OnlineStatus.OFFLINE)
    lat = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    skills = models.JSONField(default=list, blank=True)
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'pilot_profile'


class PilotResume(models.Model):
    pilot = models.OneToOneField(PilotProfile, on_delete=models.CASCADE, related_name='resume')
    summary = models.TextField(blank=True, default='')
    projects = models.JSONField(default=list, blank=True)
    portfolio = models.JSONField(default=list, blank=True)
    education = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pilot_resume'


class CreditReview(models.Model):
    class BizType(models.TextChoices):
        ORDER = 'order', '商单'
        JOB = 'job', '招聘'

    from_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='reviews_given')
    to_user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='reviews_received')
    biz_type = models.CharField(max_length=20, choices=BizType.choices)
    biz_id = models.BigIntegerField()
    score = models.IntegerField()
    tags = models.JSONField(default=list, blank=True)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'credit_review'
        unique_together = ('from_user', 'biz_type', 'biz_id')
