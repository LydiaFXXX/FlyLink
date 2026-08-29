from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.users.models import UserAccount, EnterpriseProfile, PilotProfile, PilotResume
from apps.orders.models import WorkOrder
from apps.orders.services import smart_match_and_push, gen_order_no
from apps.jobs.models import JobPost
from apps.rental.models import DroneDevice


class Command(BaseCommand):
    help = '初始化 FlyLink 演示账号与样例数据'

    def handle(self, *args, **options):
        admin, created = UserAccount.objects.get_or_create(
            username='admin',
            defaults={'role': UserAccount.Role.ADMIN, 'is_staff': True, 'is_superuser': True, 'credit_score': 900},
        )
        admin.role = UserAccount.Role.ADMIN
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('admin123')
        admin.save()

        ent, created = UserAccount.objects.get_or_create(
            username='enterprise1',
            defaults={'role': UserAccount.Role.ENTERPRISE, 'phone': '13800001111', 'credit_score': 720},
        )
        ent.set_password('demo1234')
        ent.save()
        if created:
            EnterpriseProfile.objects.create(
                user=ent, company_name='天穹农业科技有限公司', contact_name='张经理',
                license_no='91310000MA1FLYL01', address='上海市浦东新区张江路88号', verified=True,
            )
        elif not hasattr(ent, 'enterprise_profile'):
            EnterpriseProfile.objects.create(
                user=ent, company_name='天穹农业科技有限公司', contact_name='张经理', verified=True,
            )

        pilot, created = UserAccount.objects.get_or_create(
            username='pilot1',
            defaults={'role': UserAccount.Role.PILOT, 'phone': '13900002222', 'credit_score': 680},
        )
        pilot.set_password('demo1234')
        pilot.save()
        if created:
            p = PilotProfile.objects.create(
                user=pilot, real_name='李飞', license_level='CAAC-超视距', years_exp=4,
                online_status=PilotProfile.OnlineStatus.IDLE, lat=31.230400, lng=121.473700,
                skills=['植保', '巡检', '航拍'], verified=True,
            )
            PilotResume.objects.create(
                pilot=p,
                summary='持证四年，擅长大田植保与电力巡检，服务态度专业。',
                projects=[{'name': '苏南万亩水稻飞防', 'year': 2025}, {'name': '浦东变电站巡检', 'year': 2024}],
                portfolio=[
                    'https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=400',
                    'https://images.unsplash.com/photo-1508614589041-895b88991e7f?w=400',
                ],
                education='无人机应用技术专科',
            )
        elif not hasattr(pilot, 'pilot_profile'):
            p = PilotProfile.objects.create(
                user=pilot, real_name='李飞', license_level='CAAC-超视距', years_exp=4,
                online_status=PilotProfile.OnlineStatus.IDLE, lat=31.230400, lng=121.473700,
                skills=['植保', '巡检', '航拍'], verified=True,
            )
            PilotResume.objects.create(pilot=p, summary='持证飞手')

        if not WorkOrder.objects.exists():
            order = WorkOrder.objects.create(
                order_no=gen_order_no(),
                enterprise=ent,
                work_type=WorkOrder.WorkType.PLANT,
                location='上海市崇明区竖新镇农田A区',
                lat=31.622400, lng=121.397200,
                execute_time=timezone.now() + timedelta(days=2),
                area_or_duration='120亩',
                budget=Decimal('6800.00'),
                license_req='CAAC',
                urgent=True,
                status=WorkOrder.Status.PENDING,
            )
            smart_match_and_push(order)
            WorkOrder.objects.create(
                order_no=gen_order_no(),
                enterprise=ent,
                work_type=WorkOrder.WorkType.INSPECT,
                location='上海市闵行区莘庄工业区线路段',
                lat=31.111500, lng=121.381000,
                execute_time=timezone.now() + timedelta(days=5),
                area_or_duration='8小时',
                budget=Decimal('3200.00'),
                license_req='CAAC-视距内',
                urgent=False,
                status=WorkOrder.Status.PENDING,
            )

        if not JobPost.objects.exists():
            JobPost.objects.create(
                enterprise=ent,
                title='资深植保飞手（全职）',
                job_type=JobPost.JobType.FULLTIME,
                location='上海·崇明',
                salary_min=12000, salary_max=18000,
                license_req='CAAC-超视距',
                benefits='五险一金、年度体检、飞行津贴、宿舍',
                responsibilities='负责区域农田植保作业执行、设备日检与安全合规。',
                tags=['植保', '全职', '五险一金'],
            )

        if not DroneDevice.objects.exists():
            DroneDevice.objects.create(
                model_name='DJI Agras T40 植保机',
                specs={'载荷': '40kg', '续航': '15min', '喷幅': '11m', 'RTK': '支持'},
                daily_price=Decimal('680.00'), monthly_price=Decimal('12800.00'),
                deposit=Decimal('15000.00'), stock=3, cover_image='',
                description='大田植保主力机型，适合大面积作业。',
            )
            DroneDevice.objects.create(
                model_name='DJI Mavic 3 Enterprise',
                specs={'传感器': '4/3 CMOS', '续航': '45min', '红外': '可选', '重量': '915g'},
                daily_price=Decimal('320.00'), monthly_price=Decimal('5600.00'),
                deposit=Decimal('8000.00'), stock=5,
                description='轻便航拍巡检一体机，适合城市与园区作业。',
            )
            DroneDevice.objects.create(
                model_name='大疆经纬 M300 RTK',
                specs={'续航': '55min', '防护': 'IP45', '负载': '多负载', 'RTK': '厘米级'},
                daily_price=Decimal('880.00'), monthly_price=Decimal('16800.00'),
                deposit=Decimal('25000.00'), stock=2,
                description='行业旗舰，测绘巡检首选。',
            )

        self.stdout.write(self.style.SUCCESS(
            '演示数据已就绪：admin/admin123, enterprise1/demo1234, pilot1/demo1234'
        ))
