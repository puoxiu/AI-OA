from django.urls import path

from . import views

app_name = 'oaauth'

urlpatterns = [
    path('login', view=views.LoginView.as_view(), name='login')
]
