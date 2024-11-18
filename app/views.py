from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.db.models import Q
from fuzzywuzzy import process
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



def user_register(request):
    if request.method == 'POST':
        email = request.POST["email"]
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "email already exist")
                return redirect("register")
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'username already exists')
                return redirect("register")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password1)
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                Profile.objects.create(bio="default", user=request.user)

                messages.success(
                    request, 'Your account has been activated successfully.')
                return redirect('home')
        else:
            messages.info(request, "password does not match")
            return redirect("register")
    return render(request, "auth/register.html", {})


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user_auth = authenticate(username=username, password=password)

        if user_auth is not None:
            login(request, user_auth)
            return redirect("home")
        else:
            messages.error(request, "invalid credentials")
            return redirect("login")

    return render(request, 'auth/login.html', {})


def user_logout(request):
    logout(request)
    return render(request, 'auth/logout.html', {})


def home(request):
    return render(request, 'home.html', {})


@login_required(login_url='login')
def profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    my_post = Post.objects.filter(user=request.user)

    if request.method == 'POST':
        profile_pic = request.FILES.get("profile_pic")
        bio = request.POST.get("bio")
        contact_info = request.POST.get("contact_info")
        phone_number = request.POST.get("phone_number")

        if profile_pic:
            profile.profile_picture = profile_pic
        if bio:
            profile.bio = bio
        if contact_info:
            profile.contact_info = contact_info
        if phone_number:
            profile.phone_number = phone_number
        profile.save()
        return redirect("profile")
    followers = profile.followers.all()
    followers_count = followers.count()

    return render(request, 'auth/profile.html', {'profile': profile, 'post': my_post, 'followers_count' : followers_count , 'followers' : followers})


# @login_required(login_url='login')
# def create_post(request):
#     if request.method == 'POST':
#         content  = request.POST.get("content")
#         file = request.FILES.get("file")

#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.user = request.user
#             post.save()
#             return redirect('profile')
#     else:
#         form = PostForm()
#     return render(request, 'create_post.html', {'form': form})


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        content  = request.POST.get("content")
        file = request.FILES.get("files")
        post = Post.objects.create(media = file, content = content, user = request.user)
        post.save()
        return redirect("profile")
    else:
        pass
    return render(request, 'create_post.html', {})
    
        


@login_required(login_url='login')
def posts(request):
    posts = Post.objects.all()

    # Create a list of dictionaries where each dictionary contains a post and its creator's profile
    post_profile_data = []
    for post in posts:
        creator_profile = Profile.objects.get(user=post.user)
        post_profile_data.append({'post': post, 'creator_profile': creator_profile})

    return render(request, 'post.html', {
        'post_profile_data': post_profile_data,
    })




# @login_required(login_url='login')
# def post_detail(request, id):
#     posts = Post.objects.get(id=id)
#     if request.method == 'POST':
#         comment_form = CommentForm(request.POST)

#         if comment_form.is_valid():
#             post_id = request.POST.get('post_id')
#             post = get_object_or_404(Post, id=post_id)
#             comment = comment_form.save(commit=False)
#             comment.post = post
#             comment.user = request.user
#             comment.save()
#             if post.user != request.user:  # Avoid notifying self-comments
#                 Notifications.objects.create(
#                     receiver=post.user,  # The post owner
#                     sender=request.user,  # The commenter
#                     post=post,
#                     notification_type='comment',
#                     message=f"{request.user.username} commented on your post."
#                 )
#                 channel_layer = get_channel_layer()
#                 async_to_sync(channel_layer.group_send)(
#                 f"notifications_{post.user.username}",
#                 {
#                     "type": "send_notification",
#                     "message": f"{request.user.username} commented on your post.",
#                 }
#             )
#             # notification = Notification.objects.create(posts=posts, user = comment.user)
#             # notification.save()
            
#             return redirect('posts_detail' , id=id)

#     else:
#         comment_form = CommentForm()

#     comments = Comment.objects.filter(post=posts)
#     creator = posts.user
#     creator_profile = Profile.objects.get(user=creator)

#     return render(request, 'post_details.html', {
#         'post': posts,
#         'creator_profile': creator_profile,
#         'comments': comments,
#         'comment_form': comment_form,
#     })

# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Post, Comment, Reply, Notifications
from .forms import CommentForm, ReplyForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required(login_url='login')
def post_detail(request, id):
    posts = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        if 'comment_form' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = posts
                comment.user = request.user
                comment.save()
                # Send notification for comment
                if posts.user != request.user:
                    Notifications.objects.create(
                        receiver=posts.user,
                        sender=request.user,
                        post=posts,
                        notification_type='comment',
                        message=f"{request.user.username} commented on your post."
                    )
                    # Send real-time notification
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"notifications_{posts.user.username}",
                        {"type": "send_notification", "message": f"{request.user.username} commented on your post."}
                    )
                return redirect('posts_detail', id=id)

        elif 'reply_form' in request.POST:
            reply_form = ReplyForm(request.POST)
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.comment = comment
                reply.user = request.user
                reply.save()
                # Notification for reply
                if comment.user != request.user:
                    Notifications.objects.create(
                        receiver=comment.user,
                        sender=request.user,
                        post=posts,
                        notification_type='reply',
                        message=f"{request.user.username} replied to your comment  {comment.post}."
                    )
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                    f"notifications_{comment.user.username}",
                    {
                        "type": "send_notification",
                        "message": f"{request.user.username}  replied to your comment {comment.post}.",
                    }
            )
                return redirect('posts_detail', id=id)
    else:
        comment_form = CommentForm()
        reply_form = ReplyForm()

    comments = Comment.objects.filter(post=posts).prefetch_related('replies')
    creator_profile = Profile.objects.get(user=posts.user)
    

    return render(request, 'post_details.html', {
        'post': posts,
        'creator_profile': creator_profile,
        'comments': comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
    })

@login_required(login_url='login')
def creator_profile(request, id):
    profile = Profile.objects.get(id=id)
    post = Post.objects.filter(user = profile.user)
    return render(request, 'user_profile.html', {'profile': profile, 'post': post})


@login_required(login_url='login')
def commenter_profile(request, id):
    # Get the comment by its ID
    # comment = get_object_or_404(Comment, id=id)

    # Get the profile of the user who made the comment
    profile = get_object_or_404(Profile, id=id)
    post = Post.objects.filter(user = profile.user)
    

    
    # Render the profile in the template
    return render(request, 'commenter_profile.html', {'profile': profile, 'post': post})


@login_required(login_url='login')
def Savedposts(request, id):
    posts = get_object_or_404(Post, id=id)
    saved, created  = savedPosts.objects.get_or_create(name = posts, user = request.user)
    context = {
        'posts' : posts
    }
    if created :
        saved.is_added = True
        saved.save()
        return render(request, 'saved_posts.html', context)
    else:
        return render(request, 'post_saved_already.html', context)
        
@login_required(login_url='login')
def search(request):
    if request.method == "POST":
        query = request.POST["search_query"]
        posts = Post.objects.filter(Q(content__contains = query ))
        user = User.objects.filter(Q(username__contains = query))

        count = posts.count()
        count_user = user.count()
        
        context = {
            'query' : query,
            'posts' : posts,
            'count': count,
            'user' : user,
            'count_user' : count_user
        }
        return render(request, 'Base.html', context)
    else:
        return render(request, 'Base.html')
    
    
# @login_required(login_url='login')
# def search_term(request):
#     if request.method == "POST":
#         query = request.POST["search_query"]
#         posts = Post.objects.filter(Q(content__contains = query ))
#         user = User.objects.filter(Q(username__contains = query))

#         count = posts.count()
#         count_user = user.count()
        
#         if query:
#              SearchHistory.objects.create(user=request.user, query=query)
#         search_history = SearchHistory.objects.filter(user= request.user).order_by("-timestamp")[:5]
#         context = {
#             'query' : query,
#             'posts' : posts,
#             'count': count,
#             'user' : user,
#             'count_user' : count_user,
#             'history' : search_history
#         }
#         return render(request, 'search.html', context)
#     else:
#         return render(request, 'search.html')




@login_required(login_url='login')
def search_term(request):
    if request.method == "POST":
        query = request.POST.get("search_query", "")
        
        # Perform exact search with the query
        posts = Post.objects.filter(Q(content__icontains=query))
        users = User.objects.filter(Q(username__icontains=query))

        # Count the results
        count = posts.count()
        count_user = users.count()

        # Save search history if query is valid
        if query:
            SearchHistory.objects.create(user=request.user, query=query)

        # Fetch the last 5 searches for the user
        search_history = SearchHistory.objects.filter(user=request.user).order_by("-timestamp")[:5]

        # Fuzzy matching for post content
        all_posts = Post.objects.all()  # Get all Post objects
        all_users = User.objects.all()  # Get all User objects

        # Extract content strings for fuzzy matching
        all_post_contents = [post.content for post in all_posts]
        all_usernames = [user.username for user in all_users]

        # Get top 5 fuzzy matches for posts and users
        post_matches = process.extract(query, all_post_contents, limit=5)
        user_matches = process.extract(query, all_usernames, limit=5)

        # Find corresponding objects for fuzzy matches
        post_suggestions = []
        user_suggestions = []

        for match in post_matches:
            post = next((p for p in all_posts if p.content == match[0]), None)
            if post and match[1] > 60:  # Only include matches with > 60% similarity
                post_suggestions.append(post)

        for match in user_matches:
            user = next((u for u in all_users if u.username == match[0]), None)
            if user and match[1] > 60:
                user_suggestions.append(user)

        context = {
            'query': query,
            'posts': posts,
            'count': count,
            'users': users,
            'count_user': count_user,
            'history': search_history,
            'post_suggestions': post_suggestions,
            'user_suggestions': user_suggestions
        }

        return render(request, 'search.html', context)
    else:
        # Show search history if no search is performed
        search_history = SearchHistory.objects.filter(user=request.user).order_by("-timestamp")[:5]
        context = {
            'history': search_history,
        }
        return render(request, 'search.html', context)



    
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Notifications
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@login_required(login_url='login')
def like_posts(request, id):
    post = get_object_or_404(Post, id=id)
    user = request.user

    # Toggle like/unlike
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        if post.user != user:  # Avoid notifying oneself
            Notifications.objects.create(
                sender=user,
                receiver=post.user,
                notification_type="like",
                post=post,
                message=f"{user.username} liked your post"
            )

            # Send WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{post.user.username}",
                {
                    "type": "send_notification",
                    "message": f"{user.username} liked your post",
                }
            )
    total_likes = post.total_likes  # Ensure this property is being used correctly

    # Return JSON response
    return JsonResponse({
        'liked': liked,
        'total_likes': total_likes,
        
        'like_count_text': f"{total_likes} Like{'s' if total_likes != 1 else ''}",
    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Post, Notifications

@login_required(login_url='login')
def like_post(request, id):
    post = get_object_or_404(Post, id=id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
        # Create a notification if the user liked someone else's post
        if post.user != user:
            Notifications.objects.create(
                sender=user,
                receiver=post.user,
                notification_type="like",
                post=post,
                message=f"{user.username} liked your post"
            )

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{post.user.username}",
                {
                    "type": "send_notification",
                    "message": f"{user.username} liked your post",
                }
            )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return JSON response if it’s an AJAX request
        return JsonResponse({
            "liked": liked,
            "total_likes": post.likes.count()
        })
    
    # Otherwise, redirect to the post detail page
    return redirect('posts_detail', id=id)



from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Profile, Notifications

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Profile, Notifications, User

@login_required(login_url='login')
def follow_user(request, user_id):
    user = request.user

    # Get the profile and user to follow
    profile = get_object_or_404(Profile, user_id=user_id)
    user_to_follow = get_object_or_404(User, id=user_id)
    
        # Check if the current user is already following the user
    if user in profile.followers.all():
        # Unfollow the user
        profile.followers.remove(user)
        message = f"{user.username} started unfollowing you"
    else:
        # Follow the user
        profile.followers.add(user)
        message = f"{user.username} started following you"

    # Create a notification for the follow/unfollow event
    if user_to_follow != user:  # Prevent user from following themselves

        Notifications.objects.create(
            sender=user,
            receiver=user_to_follow,
            notification_type="follow",
            message=message
        )

        # Send the notification via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user_to_follow.username}",  # User's notification group
            {
                "type": "send_notification",
                "message": message,
            }
        )

    # Redirect back to the user's profile page
    return redirect('creator_profile', id=user_id)


@login_required(login_url='login')
def saved_posts_list(request):
    saved_posts = savedPosts.objects.filter(user=request.user)
    return render(request, 'saved_post_list.html', {'saved_post' : saved_posts})
    
    
    
@login_required(login_url='login')
def history_list(request):
    hisory = SearchHistory.objects.filter(user= request.user).order_by('-timestamp')
    return render(request, 'search_history.html', {'history' : hisory})
    
# @login_required(login_url='login')
# def notification(request):
#     notifications = Notification.objects.all().order_by('-created_at') 
#     context = {
#         'notifications' : notifications
#     }
#     return render(request, 'notifications.html', context )
    
@login_required(login_url='login')
def chatPage(request):
    context = {}
    return render(request, "chatpage.html", context)


from django.shortcuts import get_object_or_404, redirect

@login_required
def delete_search_history_item(request, id):
    history_item = get_object_or_404(SearchHistory, id=id, user=request.user)
    history_item.delete()
    return redirect('history_list')


@login_required
def clear_search_history(request):
    SearchHistory.objects.filter(user=request.user).delete()
    return redirect('history_list')

# views.py
@login_required
def notifications_view(request):
    notifications = Notifications.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

def function_name():
    pass