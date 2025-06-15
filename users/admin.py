from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from users.models import AbstractUser, FaceComparison

from.models import AbstractUser


@admin.register(AbstractUser)
class UserAdmin(BaseUserAdmin):
    model = AbstractUser
    list_display = ('id', 'full_name', 'phone', 'role', 'is_active', 'is_staff', 'temp_passport')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('full_name', 'phone')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Shaxsiy Ma\'lumotlar'), {
            'fields': (
                'full_name', 'role', 'gmail', 'telegram', 'image',
                'passport_scan', 'passport_back_scan', 'passport_scan_with_face',
                'passport_seria', 'temp_passport'
            )
        }),
        (_('Ruxsatlar'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Muhim Sana'), {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'password1', 'password2', 'role', 'is_active', 'is_staff')}
        ),
    )

    readonly_fields = ('created_at', 'last_login')


@admin.register(FaceComparison)
class FaceComparisonAdmin(admin.ModelAdmin):
    list_display = ('match_result', 'created_at')

