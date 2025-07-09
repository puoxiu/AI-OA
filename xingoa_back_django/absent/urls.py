from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'absent'

router = DefaultRouter()
router.register('absent', viewset=views.AbsentViewSet, basename='absent')

urlpatterns = [
    path('absent/types', views.AbsentTypeView.as_view(), name='absenttypes'),
    path('absent/responder', views.ResponderView.as_view(), name='responder'),
]  + router.urls
