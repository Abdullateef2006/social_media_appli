from django.urls import path, re_path
from .views import *


urlpatterns = [
    path('register/', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('create_post/', create_post, name='create_post'),
    path('posts/', posts, name='posts'),
    path('notification/', notification, name='notification'),
    path('chat/', chatPage, name='chat'),
    path('posts/<int:id>/', post_detail, name='posts_detail'),
    path('creator_profile/<int:id>/', creator_profile, name='creator_profile'),
    path('commenter_profile/<int:id>/', commenter_profile, name='commenter_profile'),
    path('saved_post/<int:id>/', Savedposts,  name='saved_post'),
    path('search/', search, name='search'),
    path('posts/<int:id>/like/', like_post, name='like_post'),
    path('follow/<int:user_id>/', follow_user, name='follow_user'),
    path('favourite_post/', saved_posts_list, name='favourite_post'),
    path('search_term/' , search_term, name='search_term' ),
    path('history/', history_list, name='history_list'),
     path('delete_history/<int:id>/', delete_search_history_item, name='delete_search_history_item'),
    path('clear_history/', clear_search_history, name='clear_search_history'),
]
