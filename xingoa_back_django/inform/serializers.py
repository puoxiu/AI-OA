from rest_framework import serializers

from oaauth.serializers import UserSerializer, DepartmentSerializer
from oaauth.models import OADepartment
from .models import Inform, InformRead

class InformSerializer(serializers.Serializer):
    author = UserSerializer(read_only=True)
    departments = DepartmentSerializer(many=True, read_only=True)
    # 包含了所有可以看到该通知的部门id
    department_ids = serializers.ListField(write_only=True)
    
    class Meta:
        model = Inform
        fields = '__all__'

    # 重写create方法
    def create(self, validated_data):
        request = self.context['request']
        department_ids = validated_data.pop('department_ids')

        department_ids = [int(id) for id in department_ids]

        if 0 in department_ids:
            # 如果包含0，则说明该通知所有部门可见--》public = true
            inform = Inform.objects.create(public=True, author=request.user, **validated_data)
        else:
            departments = OADepartment.objects.filter(id__in=department_ids).all()
            inform = Inform.objects.create(public=False, author=request.user, **validated_data)
            inform.departments.set(departments)
            inform.save()
        
        return inform