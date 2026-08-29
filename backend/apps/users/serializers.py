from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import UserAccount, EnterpriseProfile, PilotProfile, PilotResume, CreditReview


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'username', 'role', 'phone', 'email', 'avatar', 'credit_score', 'date_joined']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['enterprise', 'pilot'])
    phone = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    real_name = serializers.CharField(required=False, allow_blank=True)

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        role = validated_data['role']
        user = UserAccount.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=role,
            phone=validated_data.get('phone', ''),
        )
        if role == UserAccount.Role.ENTERPRISE:
            EnterpriseProfile.objects.create(
                user=user,
                company_name=validated_data.get('company_name') or f'{user.username}企业',
            )
        else:
            pilot = PilotProfile.objects.create(
                user=user,
                real_name=validated_data.get('real_name') or user.username,
                online_status=PilotProfile.OnlineStatus.IDLE,
            )
            PilotResume.objects.create(pilot=pilot)
        return user


class EnterpriseProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EnterpriseProfile
        fields = '__all__'


class PilotProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PilotProfile
        fields = '__all__'


class PilotResumeSerializer(serializers.ModelSerializer):
    pilot_id = serializers.IntegerField(source='pilot.id', read_only=True)
    real_name = serializers.CharField(source='pilot.real_name', read_only=True)
    license_level = serializers.CharField(source='pilot.license_level', read_only=True)
    years_exp = serializers.IntegerField(source='pilot.years_exp', read_only=True)
    skills = serializers.JSONField(source='pilot.skills', read_only=True)

    class Meta:
        model = PilotResume
        fields = [
            'id', 'pilot_id', 'real_name', 'license_level', 'years_exp', 'skills',
            'summary', 'projects', 'portfolio', 'education', 'updated_at',
        ]


class CreditReviewSerializer(serializers.ModelSerializer):
    from_username = serializers.CharField(source='from_user.username', read_only=True)

    class Meta:
        model = CreditReview
        fields = '__all__'
        read_only_fields = ['from_user']
