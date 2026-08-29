from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.users.models import UserAccount
from apps.orders.models import WorkOrder
from apps.rental.models import DroneDevice, RentalOrder
from apps.jobs.models import JobPost


@api_view(['GET'])
@permission_classes([AllowAny])
def platform_stats(request):
    return Response({
        'order_count': WorkOrder.objects.count(),
        'pilot_count': UserAccount.objects.filter(role=UserAccount.Role.PILOT).count(),
        'enterprise_count': UserAccount.objects.filter(role=UserAccount.Role.ENTERPRISE).count(),
        'renting_device_count': RentalOrder.objects.filter(status=RentalOrder.Status.RENTING).count()
        or DroneDevice.objects.filter(status=DroneDevice.Status.RENTED).count(),
        'open_jobs': JobPost.objects.filter(status=JobPost.Status.OPEN).count(),
        'device_total': DroneDevice.objects.count(),
    })
