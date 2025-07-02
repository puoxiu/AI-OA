from django.db import models

# Create your models here.

# 重写User类
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password
from shortuuidfield import ShortUUIDField

class OAUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user_object(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("用户名不能为空")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, username, email, password, **extra_fields):
        """
            创建用户
        """
        user = self._create_user_object(username, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        创建普通用户， 默认未激活
        """
        extra_fields.setdefault('status', UserStatusChioces.UNACTIVED)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    create_user.alters_data = True

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
            创建超级用户， 默认激活
        """
        extra_fields.setdefault('status', UserStatusChioces.ACTIVED)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置 is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置 is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


 
class UserStatusChioces(models.IntegerChoices):
    """用户状态枚举（使用IntegerChoices正确映射数值和标签）"""
    ACTIVED = (1, '已激活')     # 格式：(值, '标签')
    UNACTIVED = (2, '未激活')
    LOCK = (3, '已锁定')

class OAUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    uid = ShortUUIDField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=False)
    phone = models.CharField(max_length=20, blank=True)
    is_staff = models.BooleanField(default=True)
    status = models.IntegerField(choices=UserStatusChioces.choices, default=UserStatusChioces.UNACTIVED, blank=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    department = models.ForeignKey('OADepartment', null=True, on_delete=models.SET_NULL, related_name='staffs', related_query_name='staffs')
    
    objects = OAUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]


    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username



class OADepartment(models.Model):
    name = models.CharField(max_length=64)
    intro = models.CharField(max_length=200)
    # 每个部门只能有一个leader
    leader = models.OneToOneField(OAUser, null=True, on_delete=models.SET_NULL, related_name='leader_department', related_query_name='leader_department')
    manager = models.ForeignKey(OAUser, null=True, on_delete=models.SET_NULL, related_name='manager_departments', related_query_name = 'manager_departments')
