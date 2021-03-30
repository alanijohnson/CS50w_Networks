from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from .forms import UserProfileForm, PostForm
from .models import Post, User
import json
from django.core import serializers
from .serializers import UserSerializer, PostSerializer


def index(request):
    users = {}
    for user in User.objects.all():
        users[user.id] = UserSerializer(user).data
        
    if request.user.is_authenticated:
        url = User.objects.get(username=request.user).profile.picture
    else:
        url = ""
    
    return render(request, "network/index.html", {
            "compose_form": PostForm(),
            "user_url": url,
            "users": users
        })


# method to validate the login redirect URL
def valid_next_url(next, allowed_hosts):
    # next may be None because the page may have been reached directly
    if next is None:
        return False
    # return whether or not the url is safe to access
    return is_safe_url(
        url=next, allowed_hosts=allowed_hosts
    )
    

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
    
    # determine if there is a next url parameter and validate
    next_url = request.GET.get('next')
    if not valid_next_url(next_url, request.get_host()):
        next_url = "/"
    
    if request.method == "POST":
        
        # get the next url from the post dictionary and validate
        next_url = request.POST.get("next")
        print(f"{next_url}")
        if not valid_next_url(next_url, request.get_host()):
            next_url = "/"
        
        # when the form is subitted validate the user profile form
        profile_form = UserProfileForm(request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
        
        else:
                return render(request, "network/register.html", {
                "message": "Failed to create Account.",
                "profile_form": profile_form,
                "next_url": next_url
            })
        
        # validate standard user credentials
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match.",
                "profile_form": profile_form,
                "next_url": next_url
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile.user = user
            profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken.",
                "profile_form": profile_form,
                "next_url":next_url
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        profile_form = UserProfileForm(initial={"picture":''})
        return render(request, "network/register.html", {
            "profile_form": profile_form,
            "next_url":next_url
        })

# Get Methods
def posts(request):
     
    if request.method == "GET":
        
        start = request.GET.get("start")
        count = request.GET.get("count")
        print(request.GET)
        if start != None and count == None:
            return JsonResponse({"error": "Must supply count if using start."}, status=400)
        
        
        user_id = request.GET.get("user")

        try:
            if user_id is None:
                posts = Post.objects.order_by("-date_posted","-id")
            else:
                posts = Post.objects.filter(user=user_id).order_by("-date_posted")
        except:
            return JsonResponse({"error": "Can't Retrieve Posts."}, status=400)
        
        if start == None:
            start = 0
            end = posts.count()
        else:
            start = int(start)
            print(int(count))
            end = start + int(count)
        print(start)
        print(end)
        posts = posts[start:end]
        # Return emails in reverse chronologial order
        return JsonResponse([PostSerializer(post).data for post in posts],safe=False)
    
    return JsonResponse({"error": "Must retrieve posts."}, status=400)
    
def post(request,id):
    print(f"{id}")
    if request.method == "GET":
        try:
            post = Post.objects.get(id=id)
        except:
            return JsonResponse({"error": "Can't Retrieve Post."}, status=400)
        
        # Return emails in reverse chronologial order
        return JsonResponse(PostSerializer(post).data,safe=False)
    
    return JsonResponse({"error": "Must retrieve post."}, status=400)
    
def following(request):
     
    if request.method == "GET":
        start = request.GET.get("start")
        count = request.GET.get("count")
        if start != None and count == None:
            return JsonResponse({"error": "Must supply count if using start."}, status=400)
        
        
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return JsonResponse({"error": "User must be logged in."}, status=400)
        
        try:
            posts = Post.objects.filter(root=None,user__in=user.get_following()).order_by("-date_posted","-id")
        except:
            return JsonResponse({"error": "Can't Retrieve Posts."}, status=400)
        
        if start == None:
            start = 0
            end = posts.count()
        else:
            start = int(start)
            print(int(count))
            end = start + int(count)
        print(start)
        print(end)
        posts = posts[start:end]
        
        # Return emails in reverse chronologial order
        return JsonResponse([PostSerializer(post).data for post in posts],safe=False)
    
    
    return JsonResponse({"error": "Must retrieve posts."}, status=400)




@csrf_protect
@login_required
def submit(request):
    # Composing a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Load Json data
    data = json.loads(request.body)
    print(f"{data}\n")
    
    # Get contents of post
    content = data.get("content")
    id = data.get("id")
    if content is None:
        return JsonResponse({
                "error": "Must enter text prior to posting"
            }, status=400)
    
    if id is None:
        # Create a post
        root = data.get("root")
        if root != None:
            root = Post.objects.get(id=root)
        root_type = data.get("root_type")
        if root_type == None:
            root_type = 0
        print(f"root:{root}\nroot_type:{root_type}\n")
        post = Post(user=request.user, date_posted=timezone.now(), content=content, root=root, root_type=root_type)
        
    else:
        #update existing post
        post = Post.objects.get(id=id)
        if post.content == content:
            return JsonResponse({
                "error": "Content was not edited"
            }, status=400)
        else:
            post.content = content
    
    # Save Post
    try:
        post.save()
        return JsonResponse({"message": "Post submitted.","id":post.id}, status=201)
    except:
        return JsonResponse({
                "error": "Error Saving Post"
            }, status=400)
    
    return



def users(request):
    
    if request.method == "GET":
        try:
            users = User.objects.all().order_by("-id")
        except:
            return JsonResponse({"error": "Can't retrieve users."}, status=400)
        
        # Return users
        return JsonResponse([UserSerializer(user).data for user in users],safe=False)
    
    return JsonResponse({"error": "Must use GET."}, status=400)


def user(request,id):
    
    if request.method == "GET":
        try:
            user = User.objects.get(id=id)
        except:
            return JsonResponse({"error": "Can't retrieve user."}, status=400)
        
        # Return user
        return JsonResponse(UserSerializer(user).data,safe=False)
    
    return JsonResponse({"error": "Must use GET."}, status=400)


# Post Methods
def follow(request):

    #print(f"\nmethod:{request.method}\nuser:{request.user.username}\nrequest body:{request.body}")
    
    # following must be a post request
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    
    # get the users
    try:
        user_to_act = User.objects.get(username=request.user.username);
    except:
        return JsonResponse({"error": "User not found."}, status=400)
    
    
    data = json.loads(request.body)
    action = data.get("action")
    user = User.objects.get(id=data.get("user"))
    # print(f"\nUser to act:{user_to_act}\nUser:{user}")
    if action is None:
        return JsonResponse({"error": "Must supply an action."}, status=400)
    
    
    # Save
    try:
        if action == "follow":
            user_to_act.follow(user)
        elif action == "unfollow":
            user_to_act.unfollow(user)
        return JsonResponse({"message": f"{action} successful."}, status=200)
    except:
        return JsonResponse({
                "error": f"Error {action}ing user"
            }, status=400)
        


def like(request):
    # following must be a post request
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=411)
    
    
    # get the users
    try:
        user_to_act = User.objects.get(username=request.user.username);
    except:
        return JsonResponse({"error": "User not found."}, status=412)
    
    
    data = json.loads(request.body)
    action = data.get("action")
    post = Post.objects.get(id=data.get("post"))
    
    if action is None:
        return JsonResponse({"error": "Must supply an action."}, status=413)
        
    if post is None:
        return JsonResponse({"error": "Must supply a post."}, status=414)
    
    # Save
    try:
        if action == "like":
            post.likes.add(user_to_act)
        elif action == "unlike":
            post.likes.remove(user_to_act)
        return JsonResponse({"message": f"{action} successful."}, status=200)
    except:
        return JsonResponse({
                "error": f"Error {action}ing user"
            }, status=415)

def delete(request):

    #print(f"\nmethod:{request.method}\nuser:{request.user.username}\nrequest body:{request.body}")
    
    # following must be a post request
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    
    # get the users
    try:
        user_to_act = User.objects.get(username=request.user.username);
    except:
        return JsonResponse({"error": "User not found."}, status=400)
    
    
    data = json.loads(request.body)
    post = Post.objects.get(id=data.get("post"))
    # print(f"\nUser to act:{user_to_act}\nUser:{user}")
    if post.user != user_to_act:
        return JsonResponse({"error": "Can only delete your own posts."}, status=400)
    
    
    # Save
    try:
        post.delete()
        return JsonResponse({"message": f"Post deleted successful."}, status=200)
    except:
        return JsonResponse({
                "error": f"Error deleting post."
            }, status=400)
