# home/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseForbidden
from django.contrib.admin.views.decorators import staff_member_required
from .models import Post, Comment, Like, ActivityLog, Subscription, Dislike
from django.core.mail import send_mail
from django.conf import settings
from home.tasks import send_new_post_notification




# ===========================
# Public Views
# ===========================

def index(request):
    published_posts = Post.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'home.html', {'posts': published_posts})

def Blogs(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'blog.html', {'posts': posts})

def About(request):
    return render(request, 'About.html')

def Workwithus(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'wwu.html')

def Subscribe(request):
    return render(request, 'Subscribe.html')


# ===========================
# Authentication Views
# ===========================

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')
        role = request.POST.get('role', 'viewer')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                mobile_number=mobile_number,
                role=role,
                password=password1
            )
            user.save()

            # Log registration
            ActivityLog.objects.create(
                action='user_registered',
                user=user,
                content_object={'username': user.username, 'role': user.role}
            )

            login(request, user)
            messages.success(request, f"Welcome, {first_name}! Your account has been created.")
            return redirect('home')
    return render(request, 'wwu.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'wwu.html')


def signout(request):
    username = request.user.username
    logout(request)
    messages.info(request, f"{username}, you've been logged out.")
    return redirect('home')


def notify_subscribers(post):
    """Send email to all subscribers when a writer publishes a new post"""
    subscribers = User.objects.filter(subscriptions__writer=post.author)
    for subscriber in subscribers:
        send_mail(
            subject=f"New Post from {post.author.username}: {post.title}",
            message=f"""
            Hi {subscriber.username},

            {post.author.username} has published a new blog post:

            "{post.title}"

            Read it here: http://127.0.0.1:8000/post/{post.id}/

            — MMBlogs Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=False,
        )

# ===========================
# Blog Post Views
# ===========================

@login_required
def submit_post(request):
    # ✅ Check if user is a Writer
    if request.user.role != 'writer':
      messages.error(request, "Only writers can create blog posts.")
      return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        content = request.POST.get('content')
        action = request.POST.get('action')  # 'save_draft' or 'publish'

        if not title or not content:
            messages.error(request, "Title and content are required.")
        else:
            is_published = False

            # ✅ Create the post (saves to DB, assigns ID)
            post = Post.objects.create(
                title=title,
                subtitle=subtitle,
                content=content,
                author=request.user,
                is_published=is_published
            )

        ActivityLog.objects.create(
           action='post_created',
           user=request.user,
           content_type=ContentType.objects.get_for_model(Post),
           object_id=post.id,
           content_object={'title': post.title},
           status='live'  # ✅ Post is now live
)
        if is_published:
                messages.success(request, "Your post has been submitted for review!")
        else:
                messages.success(request, "Draft saved successfully.")
        return redirect('dashboard')
    return render(request, 'submit_post.html')


@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'posts': posts})


@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    subscribed_writers = []
    if request.user.is_authenticated:
        subscribed_writers = User.objects.filter(subscribers__subscriber=request.user)
    return render(request, 'post_detail.html', {'post': post, 'subscribed_writers': subscribed_writers})


@login_required
def like_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user == post.author:
        messages.warning(request, "You cannot like your own post.")
    elif not Like.objects.filter(post=post, user=request.user).exists():
        Like.objects.create(post=post, user=request.user)
        # Log like
        ActivityLog.objects.create(
            action='like_added',
            user=request.user,
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id,
            content_object={'post_title': post.title}
        )
        messages.success(request, "You liked this post.")
    else:
        messages.info(request, "You already liked this post.")
    return redirect('post_detail', id=id)


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user == post.author:
        messages.warning(request, "You cannot comment on your own post.")
    elif request.method == 'POST':
        text = request.POST.get('text')
        if text.strip():
            comment = Comment.objects.create(post=post, author=request.user, text=text)
            # Log comment
            ActivityLog.objects.create(
                action='comment_added',
                user=request.user,
                content_type=ContentType.objects.get_for_model(Comment),
                object_id=comment.id,
                content_object={'post_title': post.title, 'text': text[:50] + '...'}
            )
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect('post_detail', id=id)


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.author:
        messages.error(request, "You don't have permission to delete this post.")
    else:
        title = post.title
    ActivityLog.objects.create(
    action='post_deleted',
    user=request.user,
    content_type=ContentType.objects.get_for_model(Post),
    object_id=post.id,
    content_object={'title': post.title},
    status='deleted'  # ✅ Mark as deleted
)
    post.delete()  # CASCADE removes likes & comments
    messages.success(request, f"Post '{title}' and all associated likes & comments have been deleted.")
    return redirect('dashboard')
# home/views.py


@login_required
def toggle_subscribe(request, writer_id):
    writer = get_object_or_404(User, id=writer_id)
    if request.user == writer:
        messages.error(request, "You can't subscribe to yourself.")
    else:
        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            writer=writer
        )
        if not created:
            subscription.delete()
            messages.success(request, f"You've unsubscribed from {writer.username}.")
        else:
            messages.success(request, f"You're now subscribed to {writer.username}!")
    return redirect('post_detail', id=request.GET.get('post_id', 1))
# home/views.py
@login_required
def dislike_post(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user == post.author:
        messages.warning(request, "You cannot dislike your own post.")
    else:
        # Remove like if exists
        Like.objects.filter(post=post, user=request.user).delete()

        # Toggle dislike
        dislike, created = Dislike.objects.get_or_create(post=post, user=request.user)
        if not created:
            dislike.delete()
            messages.success(request, "You removed your dislike.")
        else:
            messages.success(request, "You disliked this post.")

    return redirect('post_detail', id=id)
# ===========================
# Admin Views
# ===========================

@staff_member_required
def admin_review(request):
    # ✅ Show only posts that are NOT published (awaiting review)
    pending_posts = Post.objects.filter(is_published=False).order_by('-created_at')
    return render(request, 'admin_review.html', {'posts': pending_posts})

@staff_member_required
def approve_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_published = True  # ← Now it goes live
    post.save()
    send_new_post_notification.delay(post.id)
    messages.success(request, f"Post '{post.title}' has been approved and is now live!")
    notify_subscribers(post)
    messages.success(request, f"Post '{post.title}' is now live and subscribers have been notified!")
    return redirect('admin_review')


@staff_member_required
def reject_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_published = False
    post.save()
    messages.success(request, f"Post '{post.title}' has been rejected and moved to drafts.")
    return redirect('admin_review')