from django.shortcuts import render

# Create your views here.

# django视图集
# 1. 发起考勤
# 2. 处理考勤
# 3. 查看自己的考勤
# 4. 查看下属的考勤列表

from rest_framework import viewsets, permissions, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Absent, AbsentType
from .serializers import AbsentSerializer, AbsentTypeSerializer
from .utils import get_responder
from oaauth.serializers import UserSerializer


class AbsentViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
        POST PUT GET
        虽然视图使用了 CreateModelMixin 的默认 create 方法，
        但核心业务逻辑（如设置申请人、审批人、状态）是在序列化器的 create 方法中实现的。
    """

    queryset = Absent.objects.all()
    serializer_class = AbsentSerializer
    
    def update(self, request, *args, **kwargs):
        """
        审批下属的请假
        当客户端发送 PUT 或 PATCH 请求到ViewSet注册的详情 URL（包含具体资源的主键 pk）时，会调用自定义的 update 方法
        """

        # 允许 “部分更新”，不需要提交所有字段，只传要改的字段即可；
        # 无论客户端发的是 PUT 请求还是 PATCH 请求，都会被当作 “部分更新” 处理，不需要传所有字段
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        查看请假列表
        当客户端发送 GET 请求到 ViewSet 注册的列表 URL 时，会调用自定义的 list 方法;
        如果没有重写此方法，每个请求都会返回所有的请假信息
        """
        queryset = self.get_queryset()
        who = request.query_params.get('who')
        if who and who == 'sub':
            # 返回下属的考勤信息
            result = queryset.filter(responder=request.user)
        else:
            # 返回我的考勤信息
            result = queryset.filter(requester=request.user)

        # result：代表符合要求的数据
        # pageinage_queryset方法：会做分页的逻辑处理
        page = self.paginate_queryset(result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response：除了返回序列化后的数据外，还会返回总数据多少，上一页url是什么
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(result, many=True)
        return Response(data=serializer.data)


# 查看请假类型
class AbsentTypeView(APIView):
    def get(self, request):
        types = AbsentType.objects.all()
        serializer = AbsentTypeSerializer(types, many=True)
        return Response(data=serializer.data)


# 显示审批者
class ResponderView(APIView):
    def get(self, request):
        responder = get_responder(request)
        # Serializer：如果序列化的对象是一个None，那么不会报错，而是返回一个包含除了主键外的所有字段的空字典
        serializer = UserSerializer(responder)
        return Response(data=serializer.data)

