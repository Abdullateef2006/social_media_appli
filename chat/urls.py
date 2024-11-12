from django.urls import path
from . import views
app_name = 'chat'

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('chat/<str:room_name>/', views.room, name='room'),
    path('groupchat/<str:room_name>/', views.groupchat, name='groupchat'),
 path('groups/create/', views.create_group, name='create_group'),
    path('groups/delete/<int:group_id>/', views.delete_group, name='delete_group'),
    path('chat/<str:room_name>/', views.room, name='room'), 
    path('list', views.group_list, name='group_list' ),
        path('groups/join/<int:group_id>/', views.join_group, name='join_group'),
        path('groups/leave/<int:group_id>/', views.leave_group, name='leave_group'),

    # Already existing chat view
]
