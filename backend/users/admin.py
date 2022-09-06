from django.contrib import admin

from .models import User, Follow

admin.site.register(Follow)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email')
    list_filter = ('email', 'first_name', 'last_name')
