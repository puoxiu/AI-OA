from rest_framework import serializers
from .models import Absent, AbsentType, AbsentStatusChoices
from oaauth.serializers import UserSerializer
from rest_framework import exceptions
from .utils import get_responder


class AbsentTypeSerializer(serializers.ModelSerializer):
    """
    用于将 AbsentType 模型（请假类型）转为 JSON，或者将 JSON 解析为模型对象;
    fields = "__all__" 表示包括该模型的所有字段
    """
    class Meta:
        model = AbsentType
        fields = "__all__"


class AbsentSerializer(serializers.ModelSerializer):
    # 嵌套序列化
    absent_type = AbsentTypeSerializer(read_only=True)
    absent_type_id = serializers.IntegerField(write_only=True)
    requester = UserSerializer(read_only=True)
    responder = UserSerializer(read_only=True)

    class Meta:
        model = Absent
        fields = "__all__"

    # 验证absent_type_id是否在数据库中存在
    # DRF 会自动在执行 .is_valid() 时调用它，用来验证字段 absent_type_id
    def validate_absent_type_id(self, value):
        if not AbsentType.objects.filter(pk=value).exists():
            raise exceptions.ValidationError("考勤类型不存在！")
        return value

    # create 在视图层使用 serializer.save() 创建新对象时（创建新的考勤事件），会自动调用 create() 方法
    def create(self, validated_data):
        request = self.context['request']
        # 发起者就是当前用户
        user = request.user
        # 获取审批者
        responder = get_responder(request)

        # 如果是董事会的leader，请假就直接通过
        if responder is None:
            validated_data['status'] = AbsentStatusChoices.PASS
        else:
            validated_data['status'] = AbsentStatusChoices.AUDITING
        absent = Absent.objects.create(**validated_data, requester=user, responder=responder)
        return absent

    # update--审批考勤
    def update(self, instance, validated_data):
        if instance.status != AbsentStatusChoices.AUDITING:
            raise exceptions.APIException(detail='不能修改已经确定的请假数据！')
        request = self.context['request']
        user = request.user
        if instance.responder.uid != user.uid:
            raise exceptions.AuthenticationFailed(detail='您无权处理该考勤！')
        instance.status = validated_data['status']
        instance.response_content = validated_data['response_content']
        instance.save()
        return instance