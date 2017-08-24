from django.contrib import admin
from .models import User, UserAddress, CoinLog, Icolock, Config, Contact
# Register your models here.

class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'yt', 'addr', 'money', 'frozen_num','remark','status')
    search_fields = ['type','yt','addr']

class CoinLogAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'addr', 'money', 'fee', 'create_time', 'status')
    search_fields = ['type','addr']

class IcolockAdmin(admin.ModelAdmin):
    list_display = ('uid', 'type', 'addr', 'money', 'ris', 'create_time', 'status')
    search_fields = ['uid','type','addr']

class ConfigAdmin(admin.ModelAdmin):
    list_display = ('title', 'isOpen')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'message')


admin.site.register(User)
admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(CoinLog, CoinLogAdmin)
admin.site.register(Icolock, IcolockAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(Contact, ContactAdmin)