from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post

# TODO: Specifying the user is unnecessary, requestuser.id is enough: change here, in the view function, in the js.
class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Write the contents of your post here"
                })
        }
        labels = {
            "content" : ""
        }


def index(request):
    if request.user.id:
        form = NewPostForm(initial={"id": 1})
    else:
        form = None
    return render(request, "network/index.html", {
        "form": form
    })

# TODO: decorate routes with login required
def post_view(request):

    # TODO: Use Django's validation form.is_valid()
    # Creates an email when the request method is post
    if request.method == "POST":

        # Gets the data from the request
        data = json.loads(request.body)

        # Validates the data from the request and, on failure, returns custom message
        if not data.get("content"):
            return JsonResponse({
                "is_error": True,
                "message": "Empty posts are not valid"
            }, status=400)
        try:
            user = User.objects.get(pk=int(request.user.id))
        except User.DoesNotExist:
            return JsonResponse({
                "is_error": True,
                "message": "No user found with that ID"
            }, status=400)
        
        # Saves the post in the database
        Post(
            content=data.get("content"),
            user=user
        ).save()

        # Returns success message
        return JsonResponse({
            "is_error": False,
            "message": "Your post has been successfully saved"
        }, status=201)
    
    # If the method of the request is GET, loads posts from the database
    if request.method == "GET":

        if request.GET.get("p"):
            page = int(request.GET.get("p"))
        else:
            page = 1

        posts = Paginator(Post.objects.all().order_by('-timestamp'), 10)
        return JsonResponse(
            # Sends posts to the client
            {
                "posts": [post.serialize() for post in posts.get_page(page)],
                "max_page": posts.num_pages
            },
        status=200)


def edit_view(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        mypost = Post.objects.get(pk=int(data.get("id")))

        # Validates that it is the author of the post that is trying to edit it
        if mypost.user != request.user:
            return JsonResponse({
                "is_error": True,
                "message": "Only the author of the post is allowed to edit the post"
            })
        mypost.content = data.get("content")
        mypost.save()
        return JsonResponse({
            "is_error": False,
            "message": "Your post has been successfully edited"
        }, status=200)


def profile_view(request):
    # TODO: Properly validate the request method for the other routes and improve this one + validate client side
    if request.method != "GET":
        return JsonResponse(
            {
                "error" : "Only get method is allowed"
            },
        status=400)
    
    if request.GET.get("p"):
        page = int(request.GET.get("p"))
    else:
        page = 1

    posts = Paginator(Post.objects.filter(user=request.user).order_by('-timestamp'), 10)
    return JsonResponse(
        {
            "followers_number": User.objects.filter(following=request.user).count(),
            "following_number": User.objects.get(pk=request.user.id).following.count(),
            # Sends posts to the client
            "posts": [post.serialize() for post in posts.get_page(page)],
            "max_page": posts.num_pages,
            "users": [user.serialize(request.user) for user in User.objects.exclude(pk=request.user.id)]
        },
    status=200)


def follow_view(request):
    if request.method != "PUT":
        return JsonResponse(
            {
                "error" : "Only put method is allowed"
            },
        status=400)
    
    data = json.loads(request.body)
    logged_user = User.objects.get(pk=request.user.id)
    followed_user = User.objects.get(pk=data.get("user_id"))
    if data.get("start_following"):
        logged_user.following.add(followed_user)
    else:
        logged_user.following.remove(followed_user)

    return JsonResponse({
        "message": "The follow status was successfully updated"
    }, status=200)

def like_view(request):
    if request.method != "PUT":
        return JsonResponse(
            {
                "error" : "Only put method is allowed"
            },
        status=400)
    data = json.loads(request.body)
    post = Post.objects.get(pk=int(data.get("post_id")))
    if post.likedby.filter(id=request.user.id).exists():
        post.likedby.remove(request.user)
    else:
        post.likedby.add(request.user)
    post.save()
    return JsonResponse({
        "likes": post.likedby.count()
    }, status=200)


def following_view(request):
    if request.method != "GET":
        return JsonResponse(
            {
                "error" : "Only get method is allowed"
            },
        status=400)
    
    if request.GET.get("p"):
        page = int(request.GET.get("p"))
    else:
        page = 1

    followed_users = User.objects.get(pk=request.user.id).following.all()
    posts = Paginator(Post.objects.filter(user__in=followed_users).order_by('-timestamp'), 10)
    return JsonResponse(
        # Sends posts to the client
        {
            "posts": [post.serialize() for post in posts.get_page(page)],
            "max_page": posts.num_pages
        },
    status=200)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
