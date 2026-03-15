# home/admin.py  OR  blog/admin.py
from django.contrib import admin
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import ActivityLog
from .models import Post, Comment, Like, Dislike

# ✅ Get the custom user model
User = get_user_model()

# Optional: Customize admin view
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'mobile_number', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'mobile_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'mobile_number')}),
    )

# Unregister default User if already registered (Django does it by default)
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register your custom User
admin.site.register(User, CustomUserAdmin)



@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'get_content_summary', 'status')
    list_filter = ('action', 'status', 'timestamp', 'user')
    search_fields = ('user__username', 'content_object__title')
    readonly_fields = ('timestamp', 'user', 'action', 'content_object', 'status')

    def get_content_summary(self, obj):
        if obj.content_object:
            return obj.content_object.get('title', obj.content_object.get('text', ''))
        return "-"
    get_content_summary.short_description = "Content"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('text', 'author__username', 'post__title')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('user__username', 'post__title')
@admin.register(Dislike)
class DislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('user__username', 'post__title')