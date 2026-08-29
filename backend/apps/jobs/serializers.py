from rest_framework import serializers
from .models import JobPost, JobApplication, ChatMessage, LaborContract, AgencyFee


class JobPostSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    job_type_display = serializers.CharField(source='get_job_type_display', read_only=True)

    class Meta:
        model = JobPost
        fields = '__all__'
        read_only_fields = ['enterprise']

    def get_company_name(self, obj):
        if hasattr(obj.enterprise, 'enterprise_profile'):
            return obj.enterprise.enterprise_profile.company_name
        return obj.enterprise.username


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['sender']


class LaborContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborContract
        fields = '__all__'


class AgencyFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyFee
        fields = '__all__'


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    pilot_name = serializers.CharField(source='pilot.username', read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    contract = LaborContractSerializer(read_only=True)
    agency_fee = AgencyFeeSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['pilot', 'match_score', 'source']
