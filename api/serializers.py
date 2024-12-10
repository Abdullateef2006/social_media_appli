from rest_framework import serializers
from app.models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token


class UserRegisterSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField()
    # first_name = serializers.CharField()
    # last_name = serializers.CharField()20
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username",  "email", "password", "password2"]
        extra_kwargs = {
            'password': {"write_only": True}
        }

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            detail = {
                "detail": "User Already exist!"
            }
            raise ValidationError(detail=detail)
        return username

    def validate(self, instance):
        if instance['password'] != instance['password2']:
            raise ValidationError({"message": "Both password must match"})

        if User.objects.filter(email=instance['email']).exists():
            raise ValidationError({"message": "Email already taken!"})

        return instance

    def create(self, validated_data):
        passowrd = validated_data.pop('password')
        passowrd2 = validated_data.pop('password2')
        user = User.objects.create(**validated_data)
        user.set_password(passowrd)
        user.save()
        Token.objects.create(user=user)
        return user
    


# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Post
#         fields = ['id', 'media', 'content', 'user'] 
#         read_only_fields = ['user']+


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']


class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.ReadOnlyField()
    images = PostImageSerializer(many=True)

    
    class Meta:
        model = Post
        fields = ['id', 'user', 'media', 'content', 'created_at', 'total_likes', 'images',]



class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'media', 'created_at', 'user']
        read_only_fields = ['user']


        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',]  # Add any other fields you need


 # Adjust fields according to your Post model


# class ProfileSerializer(serializers.ModelSerializer):
#     # posts = PostSerializer(many=True, read_only=True) 
#     user = UserSerializer(read_only=True)
#     followers_count = serializers.SerializerMethodField()
#     followers = UserSerializer(many=True, read_only=True)

#     class Meta:
#         model = Profile
#         fields = ['user', 'profile_picture', 'bio', 'contact_info', 'phone_number', 'followers', 'followers_count',]

#     def get_followers_count(self, obj):
#         return obj.followers.count()



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'user', 'post']

        
class SavedPostsSerializer(serializers.ModelSerializer):
    post = PostSerializer(source='name', read_only=True)  # 'name' is the Post foreign key field

    class Meta:
        model = savedPosts
        fields = ['id', 'post', 'is_added', ]  # Include necessary fields
        
        
        
        


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total_followers = serializers.ReadOnlyField()
    total_following = serializers.ReadOnlyField()
    followers = UserSerializer(many=True, read_only=True)
    following = UserSerializer(many=True, read_only=True)

    
    class Meta:
        model = Profile
        fields = ['user', 'profile_picture', 'bio', 'contact_info', 'phone_number', 'total_followers', 'total_following', 'followers', 'following',]



class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'query', 'timestamp']
        


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    post = PostListSerializer()

    class Meta:
        model  = Notifications
        fields = "__all__"
    