from django.core.management.base import BaseCommand
from oaauth.models import OAUser, OADepartment


class Command(BaseCommand):
    def handle(self, *args, **options):
        border = OADepartment.objects.get(name='董事会')
        developer = OADepartment.objects.get(name='开发部')
        operator = OADepartment.objects.get(name='运营部')
        saler = OADepartment.objects.get(name='销售部')
        hr = OADepartment.objects.get(name='人事部')
        finance = OADepartment.objects.get(name='财务部')

        # 1. 星总：属于董事会的leader, 董事会都是超级
        xingxing = OAUser.objects.create_superuser(
            username='xingxing',
            email='xingxing@example.com',
            password='123456',
            department=border,
        )
        # 2. 明总：董事会成员
        mingzong = OAUser.objects.create_superuser(
            username='mingzong',
            email='mingzong@example.com',
            password='123456',
            department=border,
        )

        # 3. 张三：产品开发部的leader
        zhangsan = OAUser.objects.create_superuser(
            username='zhangsan',
            email='zhangsan@example.com',
            password='123456',
            department=developer,
        )

        # 4. 李四： 运营部的leader
        lisi = OAUser.objects.create_superuser(
            username='lisi',
            email='lisi@example.com',
            password='123456',
            department=operator,
        )

        # 5. 王五：销售部的leader
        wangwu = OAUser.objects.create_superuser(
            username='wangwu',
            email='wangwu@example.com',
            password='123456',
            department=saler,
        )

        # 6. 赵六：人事部的leader
        zhaoliu = OAUser.objects.create_superuser(
            username='zhaoliu',
            email='zhaoliu@example.com',
            password='123456',
            department=hr,
        )

        # 7. 钱七：财务部的leader
        qianqi = OAUser.objects.create_superuser(
            username='qianqi',
            email='qianqi@example.com',
            password='123456',
            department=finance,
        )


        # 给部门指定leader和manager
        # 星星分管：产品开发部、运营部、销售部
        # 明总分管：人事部、财务部
        # 董事会
        border.leader = xingxing
        border.manager = None

        # 产品开发部
        developer.leader = zhangsan
        developer.manager = xingxing

        # 运营部
        operator.leader = lisi
        operator.manager = xingxing

        # 销售部
        saler.leader = wangwu
        saler.manager = xingxing

        # 人事部
        hr.leader = zhaoliu
        hr.manager = mingzong

        # 财务部
        finance.leader = qianqi
        finance.manager = mingzong

        # 保存部门
        border.save()
        developer.save()
        operator.save()
        saler.save()
        hr.save()
        finance.save()

        # 打印结果
        self.stdout.write(self.style.SUCCESS('部门初始化完成'))
