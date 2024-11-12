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




@login_required(login_url='login')
def post_detail(request, id):
    posts = Post.objects.get(id=id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            post_id = request.POST.get('post_id')
            post = get_object_or_404(Post, id=post_id)
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            notification = Notification.objects.create(posts=posts, user = comment.user)
            notification.save()
            
            return redirect('posts_detail' , id=id)

    else:
        comment_form = CommentForm()

    comments = Comment.objects.filter(post=posts)
    creator = posts.user
    creator_profile = Profile.objects.get(user=creator)

    return render(request, 'post_details.html', {
        'post': posts,
        'creator_profile': creator_profile,
        'comments': comments,
        'comment_form': comment_form,
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



    
@login_required(login_url='login')
def like_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('posts_detail', id=id)

@login_required(login_url='login')
def follow_user(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)
    return redirect('creator_profile', id = user_id)

@login_required(login_url='login')
def saved_posts_list(request):
    saved_posts = savedPosts.objects.filter(user=request.user)
    return render(request, 'saved_post_list.html', {'saved_post' : saved_posts})
    
    
    
@login_required(login_url='login')
def history_list(request):
    hisory = SearchHistory.objects.filter(user= request.user).order_by('-timestamp')
    return render(request, 'search_history.html', {'history' : hisory})
    
@login_required(login_url='login')
def notification(request):
    notifications = Notification.objects.all().order_by('-created_at') 
    context = {
        'notifications' : notifications
    }
    return render(request, 'notifications.html', context )
    
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

