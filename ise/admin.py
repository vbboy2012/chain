from django.contrib import admin
from .models import User,UserAddress,CoinLog, Icolock, Config
# Register your models here.

class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'yt', 'addr', 'money', 'frozen_num','remark','status')

class CoinLogAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'addr', 'money', 'fee', 'create_time', 'status')

class IcolockAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'addr', 'money', 'sec', 'create_time', 'status')

class ConfigAdmin(admin.ModelAdmin):
    list_display = ('title', 'isOpen')


admin.site.register(User)
admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(CoinLog, CoinLogAdmin)
admin.site.register(Icolock, IcolockAdmin)
admin.site.register(Config, ConfigAdmin)