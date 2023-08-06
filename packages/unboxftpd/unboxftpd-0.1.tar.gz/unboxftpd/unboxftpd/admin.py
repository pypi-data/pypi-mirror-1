from django.contrib import admin

from models import FTPUserGroup, FTPUser, FTPLog

class FTPUserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'permission',)
    search_fields = ('name', 'permission',)

class FTPUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'usergroup', 'last_login')
    search_fields = ('user', 'usergroup', 'last_login')

class FTPLogAdmin(admin.ModelAdmin):
    list_display = ('filename', 'mode', 'user', 'remote_path', 'created_at',)
    list_filter = ('mode', 'user', 'created_at')
    search_fields = ('remote_path', 'local_path',)

admin.site.register(FTPUserGroup, FTPUserGroupAdmin)
admin.site.register(FTPUser, FTPUserAdmin)
admin.site.register(FTPLog, FTPLogAdmin)
