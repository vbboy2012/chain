from django.contrib import admin
from .models import User,UserAddress,CoinLog
# Register your models here.

class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'yt', 'addr', 'money', 'frozen_num','remark','status')

class CoinLogAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'addr', 'money', 'fee', 'create_time', 'status')


admin.site.register(User)
admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(CoinLog, CoinLogAdmin)