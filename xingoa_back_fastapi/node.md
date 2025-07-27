
## celery 任务
```bash
# 在项目根目录下执行
celery -A utils.celery_app:celery_app worker --loglevel=info

```

