from django.urls import path, re_path
from .views import *


urlpatterns = [
    path("register/", UserRegisterAPIView().as_view()),
    path("profile/", ProfileView().as_view()),
    path('create-post/', CreatePostView.as_view(), name='create_post_api'),
    path('list-post/', PostsAPIView.as_view(), name='list_post_api'),
    path('detail/<int:id>/', PostDetailAPIView.as_view(), name='detail_post_api'),
    path('save-post/<int:id>/', SavedPostsAPIView.as_view(), name='save_post_api'),
    path('post/<int:id>/like/', LikePostAPIView.as_view(), name='like_post_api'),
    path('user/<int:user_id>/follow/', FollowUserAPIView.as_view(), name='follow_user_api'),
    path('saved-posts/', SavedPostsListAPIView.as_view(), name='saved_posts_list_api'),
    path('creator-profile/<int:id>/',
         CreatorProfileAPIView.as_view(), name='creator_profile_api'),
    path('commenter-profile/<int:id>/',
         CommenterProfileAPIView.as_view(), name='commenter_profile_api'),
    path('search/', SearchAPIView.as_view(), name='search_api'),
    path('search-history/', SearchHistoryAPIView.as_view(), name='search_history_api'),
    path('search-history/delete/<int:id>/', DeleteSearchHistoryItemAPIView.as_view(), name='delete_search_history_item_api'),
    path('search-history/clear/', ClearSearchHistoryAPIView.as_view(), name='clear_search_history_api'),
    
    

]
