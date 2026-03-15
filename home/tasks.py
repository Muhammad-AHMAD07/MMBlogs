# home/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscription

@shared_task
def send_new_post_notification(post_id):
    try:
        from .models import Post
        post = Post.objects.get(id=post_id, is_published=True)
        
        # Get all subscribers of the author
        subscriptions = Subscription.objects.filter(writer=post.author)
        recipient_list = [
            sub.subscriber.email for sub in subscriptions
            if sub.subscriber.email
        ]

        if not recipient_list:
            return "No subscribers to notify."

        # Send email
        subject = f"New Post: {post.title}"
        message = f"""
        Hi {post.author.username},

        {post.author.username} has published a new blog post:

        "{post.title}"

        Read it here: http://127.0.0.1:8000/post/{post.id}/

        — MMBlogs Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return f"Sent {len(recipient_list)} emails for post '{post.title}'"
    except Exception as e:
        return f"Error: {str(e)}"