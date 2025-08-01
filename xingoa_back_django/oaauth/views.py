from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.permissions import IsAuthenticated

from .serializers import LoginSerializer, UserSerializer, ResetPwdSerializer
from .authentications import JWTAuthentication, generate_jwt


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = datetime.now()
            user.save()

            token = generate_jwt(user=user)
            return Response({'token': token, 'user': UserSerializer(user).data})

        else:
            print(serializer.errors)
            return Response({"message": "参数验证失败"}, status=status.HTTP_400_BAD_REQUEST)
        

class ResetPwdView(APIView):
    # permission_classes = IsAuthenticated[]
    def post(self, request):
        serializer = ResetPwdSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            pwd1 = serializer.validated_data.get('pwd1')
            request.user.set_password(pwd1)
            request.user.save()
            return Response({'message': '修改成功'}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            detail = list(serializer.errors.values())[0][0]
            return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
