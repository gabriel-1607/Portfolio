import json
from django.http import JsonResponse
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post

class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "user"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Write the contents of your post here"
                }),
            "user": forms.HiddenInput(),
        }
        labels = {
            "content" : ""
        }


def index(request):
    if request.user.id:
        form = NewPostForm(initial={"user": request.user.pk})
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
            user = User.objects.get(pk=int(data.get("user")))
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

        # Return success message
        return JsonResponse({
            "is_error": False,
            "message": "Your post has been successfully saved"
        }, status=201)
    
    # If the method of the request is GET, loads posts from the database
    if request.method == "GET":
        return JsonResponse(
            {"posts": [post.serialize() for post in Post.objects.all().order_by('-timestamp')]},
        status=200)


def profile_view(request):
    # TODO: Properly validate the request method for the other routes and improve this one + validate client side
    if request.method != "GET":
        return JsonResponse(
            {
                "error" : "Only get method is allowed"
            },
        status=400)
    
    # TODO: Modify the serialize function for users to identify wether they are following the user and wether the user is following them
    return JsonResponse(
        {
            "followers_number": User.objects.filter(following=request.user).count(),
            "following_number": User.objects.get(pk=request.user.id).following.count(),
            "posts": [post.serialize() for post in Post.objects.filter(user=request.user).order_by('-timestamp')],
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


def following_view(request):
    if request.method != "GET":
        return JsonResponse(
            {
                "error" : "Only get method is allowed"
            },
        status=400)
    followed_users = User.objects.get(pk=request.user.id).following.all()
    return JsonResponse(
        {"posts": [post.serialize() for post in Post.objects.filter(user__in=followed_users).order_by('-timestamp')]},
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
