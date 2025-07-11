from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from .models import Inform
from .serializers import InformSerializer


class InformViewsets(viewsets.ModelViewSet):
    queryset = Inform.objects.all()
    serializer_class = InformSerializer
