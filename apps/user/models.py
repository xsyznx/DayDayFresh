from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser, BaseModel):
    """
    用户模型类
    """
    class Meta:
        db_table = "t_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class Address(BaseModel):
    """收货地址类"""
    user = models.ForeignKey(to='User', on_delete=models.CASCADE, verbose_name="用户")
    receiver = models.CharField(max_length=100, verbose_name="收件人")
    addr = models.CharField(max_length=100, verbose_name="地址")
    zip_code = models.CharField(max_length=6, verbose_name="邮政编码", null=True)
    phone = models.CharField(max_length=11, verbose_name="联系电话")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")

    class Meta:
        db_table = "t_address"
        verbose_name = "地址"
        verbose_name_plural = verbose_name