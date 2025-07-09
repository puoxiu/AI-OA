from django.core.management.base import BaseCommand
from absent.models import AbsentType

# class AbsentType(models.Model):
#     name = models.CharField(max_length=100)
#     create_time = models.DateTimeField(auto_now_add=True)

class Command(BaseCommand):
    def handle(self, *args, **options):
        absent_types = [
            '事假',
            '病假',
            '年假',
            '婚假',
            '产假',
            '陪产假',
            '丧假',
            '调休',
            '工伤假',
            '探亲假',
        ]
        absents = []
        for type in absent_types:
            absents.append(AbsentType(name=type))
        
        AbsentType.objects.bulk_create(absents)

        self.stdout.write(self.style.SUCCESS('考勤类型 初始化完成'))