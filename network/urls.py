
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("post", views.post_view, name="post"),
    path("profile", views.profile_view, name="profile"),
    path("follow", views.follow_view, name="follow"),
    path("following", views.following_view, name="following"),
    path("edit", views.edit_view, name="edit")
]
