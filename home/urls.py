from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
   path('',views.index, name='home'),
   path('Blogs',views.Blogs, name='Blogs'),
   path('Work With Us',views.Workwithus, name='Workwithus'),
   path('About',views.About, name='About'),
   path('Subscribe',views.Subscribe, name='Subscribe'),
   path('signup', views.signup, name='signup'),
   path('signin', views.signin, name='signin'),
   path('signout', views.signout, name='signout'),
   path('submit', views.submit_post, name='submit_post'),
   path('dashboard', views.dashboard, name='dashboard'),
   path('admin-review', views.admin_review, name='admin_review'),
   path('approve/<int:post_id>/', views.approve_post, name='approve_post'),
   path('reject/<int:post_id>/', views.reject_post, name='reject_post'),
   path('post/<int:id>/', views.post_detail, name='post_detail'),
   path('post/<int:id>/like/', views.like_post, name='like_post'),
   path('post/<int:id>/comment/', views.add_comment, name='add_comment'),
   path('post/<int:id>/delete/', views.delete_post, name='delete_post'),
   path('subscribe/<int:writer_id>/', views.toggle_subscribe, name='toggle_subscribe'),
   path('post/<int:id>/dislike/', views.dislike_post, name='dislike_post'),
]
