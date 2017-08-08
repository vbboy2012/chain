from django.db import models
from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone

# Create your models here.
# python3 manage.py makemigrations
# python3 manage.py migrate

class User(AbstractUser):
    checkEmail = models.BooleanField('邮箱验证',default=False)
    safe_password = models.CharField('资金密码',max_length=128,default='')

class UserAddress(models.Model):
    uid = models.IntegerField()
    type = models.IntegerField()    #1btc，2eth ，3SEC
    yt = models.IntegerField()      #1 充值地址 2 提币地址
    addr = models.CharField(max_length=50)
    money = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.IntegerField('状态', default=1)  #1启用 0 删除

    def __str__(self):
        return self.uid

class CoinLog(models.Model):
    uid = models.IntegerField()
    addr = models.CharField(max_length=50)
    type = models.IntegerField()    # 1 充值记录，2提现记录
    money = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8)
    create_time = models.DateTimeField('时间', default=timezone.now())
    status = models.IntegerField('状态', default=0)  # 1成功 0 审核中 2取消