from django.shortcuts import render
from rest_framework.generics import ListAPIView
from oaauth.serializers import DepartmentSerializer
from oaauth.models import OADepartment


class DepartmentListView(ListAPIView):
    queryset = OADepartment.objects.all()
    serializer_class = DepartmentSerializer

