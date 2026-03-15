# home/models.py
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from accounts.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,          # ✅ This ensures cascade delete
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,          # ✅ This ensures cascade delete
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'Like by {self.user.username} on {self.post.title}'



# home/models.py
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('user_registered', 'User Registered'),
        ('post_created', 'Post Created'),
        ('post_deleted', 'Post Deleted'),
        ('comment_added', 'Comment Added'),
        ('like_added', 'Like Added'),
    ]

    STATUS_CHOICES = [
        ('live', 'Live'),
        ('deleted', 'Deleted'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='live')  # ← New field

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.get_status_display()}"
class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'writer')  # One subscription per user-writer pair

    def __str__(self):
        return f"{self.subscriber.username} → {self.writer.username}"    
class Dislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # One dislike per user per post

    def __str__(self):
        return f'Dislike by {self.user.username} on {self.post.title}'