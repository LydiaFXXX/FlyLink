from rest_framework import serializers
from .models import DroneDevice, MaintenanceRecord, RentalOrder


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = '__all__'


class DroneDeviceSerializer(serializers.ModelSerializer):
    maintenances = MaintenanceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = DroneDevice
        fields = '__all__'


class RentalOrderSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.model_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    device_detail = DroneDeviceSerializer(source='device', read_only=True)

    class Meta:
        model = RentalOrder
        fields = '__all__'
        read_only_fields = [
            'order_no', 'user', 'deposit_paid', 'deposit_waived', 'insurance_fee',
            'rent_amount', 'status', 'damage_fee', 'credit_score_snapshot',
        ]
