from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post

# ModelForm that handles new posts
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


# Default route to load the index.html template with the modelform
def index(request):
    if request.user.is_authenticated:
        form = NewPostForm()
    else:
        form = None
    return render(request, "network/index.html", {
        "form": form
    })


# Route that handles JSON requests to save posts with the POST method
# and to return all posts via the GET method
def post_view(request):

    # Creates a post when the request method is post and ensures it is a user doing so
    if request.method == "POST" and request.user.is_authenticated:

        # Gets the data from the request
        data = json.loads(request.body)

        # Validates the data from the request and, on failure, returns errors
        form = NewPostForm(data)
        if not form.is_valid():
            return JsonResponse({
                "is_error": True,
                "message": form.errors
            }, status=400)

        # Validates that it is a valid user creating the post
        try:
            user = User.objects.get(pk=int(request.user.id))
        except User.DoesNotExist:
            return JsonResponse({
                "is_error": True,
                "message": "No user found as author of the post"
            }, status=400)
        
        # Saves the post in the database
        Post(
            content=form.cleaned_data["content"],
            user=user
        ).save()

        # Returns success message
        return JsonResponse({
            "is_error": False,
            "message": "Your post has been successfully saved"
        }, status=201)
    
    # If the method of the request is GET, loads posts from the database
    # Non-authenticated users may access
    if request.method == "GET":

        # Tries to get the page from the request
        if request.GET.get("p"):
            page = int(request.GET.get("p"))
        else:
            page = 1

        # Gets and paginates the posts
        posts = Paginator(Post.objects.all().order_by('-timestamp'), 10)

        # Returns posts to the client
        return JsonResponse(
            {
                "posts": [post.serialize() for post in posts.get_page(page)],
                "max_page": posts.num_pages
            },
        status=200)


# Route to edit a post
@login_required
def edit_view(request):

    # Ensures that the request method is PUT
    if request.method == "PUT":

        # Gets the data from the request
        data = json.loads(request.body)

        # Validates the data from the request and, on failure, returns errors
        form = NewPostForm({"content": data.get("content")})
        if not form.is_valid():
            return JsonResponse({
                "is_error": True,
                "message": form.errors
            }, status=400)
        
        # Finds the post in the database to be edited
        mypost = Post.objects.get(pk=int(data.get("id")))

        # Validates that it is the author of the post that is trying to edit it
        if mypost.user != request.user:
            return JsonResponse({
                "is_error": True,
                "message": "Only the author of the post is allowed to edit the post"
            })

        # Changes the content of the post
        mypost.content = form.cleaned_data["content"]

        # Saves the post to the database
        mypost.save()

        # Returns success message
        return JsonResponse({
            "is_error": False,
            "message": "Your post has been successfully edited"
        }, status=200)


@login_required
def profile_view(request):

    # Ensures the method is GET
    if request.method != "GET":
        return JsonResponse(
            {
                "error" : "Only get method is allowed"
            },
        status=400)
    
    # Tries to get the page from the request
    if request.GET.get("p"):
        page = int(request.GET.get("p"))
    else:
        page = 1

    # Gets and paginates the posts
    posts = Paginator(Post.objects.filter(user=request.user).order_by('-timestamp'), 10)

    # Returns profile data to the client
    return JsonResponse(
        {
            "followers_number": User.objects.filter(following=request.user).count(),
            "following_number": User.objects.get(pk=request.user.id).following.count(),
            "posts": [post.serialize() for post in posts.get_page(page)],
            "max_page": posts.num_pages,
            "users": [user.serialize(request.user) for user in User.objects.exclude(pk=request.user.id)]
        },
    status=200)


@login_required
def follow_view(request):

    # Ensures the method is PUT
    if request.method != "PUT":
        return JsonResponse(
            {
                "error" : "Only put method is allowed"
            },
        status=400)
    
    # Gets the data from the request
    data = json.loads(request.body)

    # Gets and validates the users from the database to assign followed status
    logged_user = User.objects.get(pk=request.user.id)
    try:
        followed_user = User.objects.get(pk=data.get("user_id"))
    except User.DoesNotExist:
            return JsonResponse({
                "is_error": True,
                "message": "No user found as author of the post"
            }, status=400)

    # Modifies the users from the database
    if data.get("start_following"):
        logged_user.following.add(followed_user)
    else:
        logged_user.following.remove(followed_user)

    # Returns sucess message
    return JsonResponse({
        "message": "The follow status was successfully updated"
    }, status=200)


@login_required
def like_view(request):

    # Ensures the request method is PUT
    if request.method != "PUT":
        return JsonResponse(
            {
                "error" : "Only put method is allowed"
            },
        status=400)
    
    # Gets the data from the request
    data = json.loads(request.body)

    # Gets the post from the database
    post = Post.objects.get(pk=int(data.get("post_id")))

    # Modifies the liked status of the post in regard to the user
    if post.likedby.filter(id=request.user.id).exists():
        post.likedby.remove(request.user)
    else:
        post.likedby.add(request.user)

    # Saves the post
    post.save()

    # Returns the amount of likes
    return JsonResponse({
        "likes": post.likedby.count()
    }, status=200)


@login_required
def following_view(request):

    # Ensures that the request method is GET
    if request.method != "GET":
        return JsonResponse(
            {
                "error" : "Only get method is allowed"
            },
        status=400)
    
    # Tries to get the page from the request
    if request.GET.get("p"):
        page = int(request.GET.get("p"))
    else:
        page = 1

    # Gets the posts from the database and paginates them
    followed_users = User.objects.get(pk=request.user.id).following.all()
    posts = Paginator(Post.objects.filter(user__in=followed_users).order_by('-timestamp'), 10)

    # Sends posts to the client
    return JsonResponse(
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
