from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, EnterpriseProfile, PilotProfile, PilotResume, CreditReview

admin.site.register(UserAccount, UserAdmin)
admin.site.register(EnterpriseProfile)
admin.site.register(PilotProfile)
admin.site.register(PilotResume)
admin.site.register(CreditReview)
