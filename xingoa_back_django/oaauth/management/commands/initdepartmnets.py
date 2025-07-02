from django.core.management.base import BaseCommand
from oaauth.models import OADepartment

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 初始化部门数据
        border = OADepartment.objects.create(name='董事会', intro='负责组织协调oa的各项工作')
        developer = OADepartment.objects.create(name='开发部', intro='负责产品开发')
        operator = OADepartment.objects.create(name='运营部', intro='负责运营')
        saler = OADepartment.objects.create(name='销售部', intro='负责o售')
        hr = OADepartment.objects.create(name='人事部', intro='负责人事')
        finance = OADepartment.objects.create(name='财务部', intro='负责财务')

        self.stdout.write(self.style.SUCCESS('部门初始化完成'))
       