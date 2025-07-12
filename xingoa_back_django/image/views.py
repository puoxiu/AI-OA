from rest_framework.views import APIView
from .serializers import UploadImageSerializer
from rest_framework.response import Response
from shortuuid import uuid
import os
from django.conf import settings


class UploadImageView(APIView):
    def post(self, request):
        # 初始化序列化器并验证请求数据
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            # 从验证后的数据中获取上传的图片文件
            file = serializer.validated_data.get('image')
            
            # 生成唯一文件名：使用shortuuid生成随机字符串 + 原文件扩展名
            # 例如：原文件abc.png → 转换为 sdfsdafsdjag.png
            filename = uuid() + os.path.splitext(file.name)[-1]
            
            # 构建服务器存储路径：MEDIA_ROOT/随机文件名
            path = settings.MEDIA_ROOT / filename
            print(f"path={path}")

            try:
                # 分块写入文件到服务器
                with open(path, 'wb') as fp:
                    for chunk in file.chunks():
                        fp.write(chunk)
            except Exception:
                # 文件写入失败时返回错误响应
                return Response({
                    "errno": 1,
                    "message": "图片保存失败！请检查权限问题."
                })
            
            # 构建客户端访问URL：MEDIA_URL + 文件名
            # 例如：/media/sdfsdafsdjag.png
            file_url = settings.MEDIA_URL + filename
            
            # 返回成功响应，包含图片URL等信息
            return Response({
                "errno": 0,  # 错误码0表示成功
                "data": {
                    "url": file_url,  # 图片URL（必选字段）
                    "alt": "",        # 图片描述（可选字段）
                    "href": file_url  # 图片链接（可选字段）
                }
            })
        else:
            # 打印序列化器验证错误（调试用）
            print(serializer.errors)
            
            # 返回验证失败的错误响应，提取第一个错误信息
            return Response({
                "errno": 1,  # 错误码非0表示失败
                "message": list(serializer.errors.values())[0][0]
            })