
## celery 任务
```bash
# 在项目根目录下执行
celery -A utils.celery_app:celery_app worker --loglevel=info

```

## AES加密
q：加密后的token存在+等特殊字符，不能在url中，导致参数传递错误













