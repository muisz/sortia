from django.contrib import admin

from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'username', 'is_active', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email', 'username')
