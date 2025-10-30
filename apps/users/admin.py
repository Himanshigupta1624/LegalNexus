from django.contrib import admin
from .models import User, OTPLogin, PasswordResetCode


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'password', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'mobile')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    readonly_fields = ('password',)


@admin.register(OTPLogin)
class OTPLoginAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'otp', 'created_at', 'is_verified', 'expires_at')
    search_fields = ('mobile',)
    list_filter = ('is_verified', 'created_at')


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'code', 'created_at', 'is_used', 'expires_at')
    search_fields = ('user__email', 'user__username', 'code')
    list_filter = ('is_used', 'created_at')


