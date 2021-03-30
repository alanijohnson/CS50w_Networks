
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # path("profile/<str:username>", views.profile, name="profile"),
    
    # API routes
    path("posts", views.posts, name="posts"),
    path("post/<int:id>", views.post, name="post"),
    # path("posts/<string:username", views.user_posts, name="user_posts"),
    path("submit/post", views.submit, name="submit"),
    path("follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("users", views.users, name="users"),
    path("user/<int:id>", views.user, name="user"),
    path("like", views.like, name="like"),
    path("delete", views.delete, name="delete")
    
    
    
]
