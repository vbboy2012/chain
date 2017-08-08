from django.contrib import admin
from .models import User,UserAddress,CoinLog
# Register your models here.


admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(CoinLog)