from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
# python3 manage.py makemigrations
# python3 manage.py migrate

class User(AbstractUser):
    checkEmail = models.BooleanField('邮箱验证',default=False)
    safe_password = models.CharField('资金密码',max_length=128,default='')

class UserAddress(models.Model):
    uid = models.IntegerField()
    type = models.IntegerField()    #1btc，2eth ，3RIS
    yt = models.IntegerField()      #1 充值地址 2 提币地址
    addr = models.CharField(max_length=50)
    money = models.DecimalField(max_digits=20, decimal_places=8)        #余额
    frozen_num = models.DecimalField(max_digits=20, decimal_places=8, default=0)   #冻结数量
    remark = models.CharField(max_length=50, default='')
    status = models.IntegerField('状态', default=1)  #1启用 0 删除

class CoinLog(models.Model):
    uid = models.IntegerField()
    addr = models.CharField(max_length=50)
    type = models.IntegerField()    # 1 充值记录，2提现记录
    coin_type = models.IntegerField()  # 币种 1BTC 2 ETH 3 RIS
    money = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8)
    create_time = models.DateTimeField('时间', default=timezone.now)
    status = models.IntegerField('状态', default=0)  # 1成功 0 审核中 2取消

class Icolock(models.Model):
    uid = models.IntegerField()
    addr = models.CharField(max_length=50)
    type = models.IntegerField()  # 1 阶段类型
    coin_type = models.IntegerField()  # 1 支持币种
    money = models.DecimalField(max_digits=20, decimal_places=8)
    ris = models.DecimalField(max_digits=20, decimal_places=8)
    ok_ris = models.DecimalField(max_digits=20, decimal_places=8,default=0)
    create_time = models.DateTimeField('时间', default=timezone.now)
    status = models.IntegerField('状态', default=0)  # 1，成功，待解冻，2发放1/3，3发放2/3，4发放完成

class Config(models.Model):
    title = models.CharField(max_length=50)
    btcRate = models.IntegerField('BTC兑换率', default=0)
    ethRate = models.IntegerField('ETH兑换率', default=0)
    risCount = models.IntegerField('RIS总量', default=0)
    icoCount = models.IntegerField('RIS已发量', default=0)
    start_time = models.DateTimeField('开始时间', default=timezone.now)
    end_time = models.DateTimeField('结束时间', default=timezone.now)
    isOpen = models.BooleanField(default=False)

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.CharField(max_length=50)
