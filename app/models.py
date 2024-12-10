from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

    
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.FileField(upload_to='medias/',blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)
    tags = TaggableManager()
    def __str__(self):
     return self.content
    def total_likes(self):
        return self.likes.count()
    
    
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.post.content}"

 
 
 
 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/')
    bio = models.TextField(blank=True, default='no bio avaiable')
    contact_info = models.CharField(max_length=100, blank=True, default='No contact info available')
    phone_number = models.CharField(max_length=20, blank=True, default='no phone number available')
    posts = models.ManyToManyField(Post)
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    

    class Meta:

        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.user.username
    def total_followers(self):
        return self.followers.count()

    def total_following(self):
        return self.user.following.count()
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post,  on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Comment by {self.user} on {self.post}'
    
# models.py
class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user} on {self.comment}"

    
class savedPosts(models.Model):
    '''Model definition for savedPosts.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    is_added = models.BooleanField(default=False)
    name = models.ForeignKey(Post, on_delete=models.CASCADE, default='')

    class Meta:
        '''Meta definition for savedPosts.'''

        verbose_name = 'savedPosts'
        verbose_name_plural = 'savedPostss'

    def __str__(self):
        return self.name.content
    
    
    # models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

# models.py
class Notifications(models.Model):
    NOTIFICATION_TYPE = (
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),

    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user", null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user", null=True, blank=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE, default='follow')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)  # Only for 'like' notifications
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.message}"


# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
#     created_at = models.DateTimeField(default=timezone.now)
#     posts = models.ForeignKey(Post, on_delete=models.CASCADE, default='')
#     is_read = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Notification for {self.user.username}: {self.posts.content}"


from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched for {self.query} on {self.timestamp}"
