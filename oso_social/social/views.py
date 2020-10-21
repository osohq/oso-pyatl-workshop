from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group

from django_oso.auth import authorize

from .models import Post
from .forms import PostForm

# Create your views here.


def list_posts(request):
    posts = Post.objects.all().order_by("-created_at")
    groups = Group.objects.all()

    # STEP 1: Add check that user is an admin before they can see a post.
    try:
        authorize(request, action="list", resource="Post")
    except PermissionDenied:
        posts = []

    return render(request, "social/list.html", {"posts": posts, "groups": groups})

# STEP 2: Add group list view.
def list_group(request, group_id):
    group = Group.objects.get(id=group_id)
    posts = Post.objects.filter(group=group_id).order_by("-created_at")

    # Check that user is in the group
    try:
        authorize(request, action="list_posts", resource=group)
    except PermissionDenied:
        posts = []

    return render(request, "social/list.html", {"posts": posts, "group": group})

@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        post = form.save(commit=False)

        # STEP 3: Restrict post creation by group.
        authorize(request, action="create", resource=post)

        post.created_by = request.user
        post.save()

        return HttpResponseRedirect(reverse("index"))
    elif request.method == "GET":
        form = PostForm()
        return render(request, "social/new_post.html", {"form": form})
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
