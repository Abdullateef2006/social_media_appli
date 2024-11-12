from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from .serializers import *
from app.models import *
from rest_framework import generics


from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser


class UserRegisterAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny,]
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                'success': True,
                'user': serializer.data,
                'token': Token.objects.get(user=User.objects.get(username=serializer.data['username'])).key
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError(
            serializer.errors, code=status.HTTP_406_NOT_ACCEPTABLE)


# class ProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ProfileSerializer

#     def get(self, request):
#         profile, created  = Profile.objects.get_or_create(user = request.user)
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data)

#     def put(self, request):
#         profile, created  = Profile.objects.get_or_create(user = request.user)
#         serializer = ProfileSerializer(profile, data = request.data, partial = True )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProfileSerializer


    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        my_posts = Post.objects.filter(user=request.user)
        profile_data = ProfileSerializer(profile).data
        profile_data['posts'] = my_posts.values()  # Or serialize them properly if you have a PostSerializer

        return Response(profile_data)

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile_pic = request.FILES.get("profile_pic")
        bio = request.data.get("bio")
        contact_info = request.data.get("contact_info")
        phone_number = request.data.get("phone_number")

        if profile_pic:
            profile.profile_picture = profile_pic
        if bio:
            profile.bio = bio
        if contact_info:
            profile.contact_info = contact_info
        if phone_number:
            profile.phone_number = phone_number
        profile.save()

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)




class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        content = request.data.get("content")
        file = request.FILES.get("files")

        post = Post.objects.create(
            media=file,
            content=content,
            user=request.user
        )
        post.save()

        return Response({"message": "Post created successfully!"}, status=status.HTTP_201_CREATED)


# class Postlist(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = PostListSerializer
    
#     def get(self, request):
#         post = Post.objects.all()
#         serializer = PostListSerializer(post, many=True)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
        

        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import PostSerializer, ProfileSerializer

class PostsAPIView(APIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = PostListSerializer

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        post_profile_data = []
        for post in posts:
            creator_profile = Profile.objects.get(user=post.user)
            post_serializer = PostListSerializer(post)
            profile_serializer = ProfileSerializer(creator_profile)

            post_profile_data.append({
                'post': post_serializer.data,
                'creator_profile': profile_serializer.data
            })

        # Return the response as JSON
        return Response({'post_profile_data': post_profile_data}, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404
class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get(self, request, id, *args, **kwargs):
        post = get_object_or_404(Post, id=id)
        comments = Comment.objects.filter(post=post)
        creator_profile = Profile.objects.get(user=post.user)

        post_serializer = PostSerializer(post)
        comments_serializer = CommentSerializer(comments, many=True)
        creator_profile_serializer = ProfileSerializer(creator_profile)

        return Response({
            'post': post_serializer.data,
            'comments': comments_serializer.data,
            'creator_profile': creator_profile_serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, id, *args, **kwargs):
        post = get_object_or_404(Post, id=id)
        
        # Get the content of the comment from request data
        comment_data = request.data.get("content")
        
        # Create the comment with the post and user info
        # comment = Comment(post=post, user=request.user, content=comment_data)
        
        # Serialize the comment data and validate
        comment_serializer = CommentSerializer(data={'post': post.id, 'user': request.user.id, 'content': comment_data})
        
        if comment_serializer.is_valid():
            comment = comment_serializer.save()

            # Create a notification for the post creator
            Notification.objects.create(posts=post, user=request.user)

            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatorProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        profile = get_object_or_404(Profile, id=id)
        posts = Post.objects.filter(user=profile.user)
        
        profile_serializer = ProfileSerializer(profile)
        post_serializer = PostSerializer(posts, many=True)
        
        return Response({
            'profile': profile_serializer.data,
            'posts': post_serializer.data
        })

class CommenterProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        profile = get_object_or_404(Profile, id=id)
        posts = Post.objects.filter(user=profile.user)
        
        profile_serializer = ProfileSerializer(profile)
        post_serializer = PostSerializer(posts, many=True)
        
        return Response({
            'profile': profile_serializer.data,
            'posts': post_serializer.data
        })


# views.py


class SavedPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)
        saved, created = savedPosts.objects.get_or_create(name=post, user=request.user)

        if created:
            saved.is_added = True
            saved.save()
            serializer = SavedPostsSerializer(saved)
            return Response({'message': 'Post saved successfully!', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Post already saved!'}, status=status.HTTP_200_OK)
class LikePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        post = get_object_or_404(Post, id=id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            message = "Unliked the post"
        else:
            post.likes.add(request.user)
            message = "Liked the post"
        post.save()
        return Response({'message': message, 'total_likes': post.total_likes()}, status=status.HTTP_200_OK)
    
    
    
class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        profile = get_object_or_404(Profile, user_id=user_id)
        if request.user in profile.followers.all():
            profile.followers.remove(request.user)
            message = "Unfollowed the user"
        else:
            profile.followers.add(request.user)
            message = "Followed the user"
        profile.save()
        return Response({'message': message, 'total_followers': profile.total_followers()}, status=status.HTTP_200_OK)
    
    
class SavedPostsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved_posts = savedPosts.objects.filter(user=request.user)
        serializer = SavedPostsSerializer(saved_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# views.py


from django.db.models import Q

from fuzzywuzzy import process

class SearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    

    def post(self, request):
        query = request.data.get("search_query", "")

        # Perform regular search with the query
        posts = Post.objects.filter(Q(content__icontains=query))
        users = User.objects.filter(Q(username__icontains=query))

        # Count the results
        count = posts.count()
        count_user = users.count()

        # If query is valid, save the search history
        if query:
            SearchHistory.objects.create(user=request.user, query=query)

        # Fetch the last 5 searches for the user
        search_history = SearchHistory.objects.filter(user=request.user).order_by("-timestamp")[:5]
        search_history_serializer = SearchHistorySerializer(search_history, many=True)

        # Fuzzy matching for post content
        all_posts = Post.objects.all()  # Get all Post objects
        all_users = User.objects.all()  # Get all User objects

        post_suggestions = []
        for post in all_posts:
            match = process.extractOne(query, [post.content])
            if match and match[1] > 60:  # Only include matches with > 60% similarity
                post_suggestions.append(post)

        user_suggestions = []
        for user in all_users:
            match = process.extractOne(query, [user.username])
            if match and match[1] > 60:
                user_suggestions.append(user)

        # Serialize the results
        posts_serializer = PostSerializer(posts, many=True)
        users_serializer = UserSerializer(users, many=True)
        post_suggestions_serializer = PostSerializer(post_suggestions, many=True)
        user_suggestions_serializer = UserSerializer(user_suggestions, many=True)

        # Response data
        context = {
            'query': query,
            'posts': posts_serializer.data,
            'count': count,
            'users': users_serializer.data,
            'count_user': count_user,
            'history': search_history_serializer.data,
            'post_suggestions': post_suggestions_serializer.data,
            'user_suggestions': user_suggestions_serializer.data
        }

        return Response(context, status=status.HTTP_200_OK)
class SavedPostsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved_posts = savedPosts.objects.filter(user=request.user)
        serializer = SavedPostsSerializer(saved_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SearchHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_history = SearchHistory.objects.filter(user=request.user)
        serializer = SearchHistorySerializer(search_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class DeleteSearchHistoryItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        history_item = get_object_or_404(SearchHistory, id=id, user=request.user)
        history_item.delete()
        return Response({"message": "Search history item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
class ClearSearchHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        SearchHistory.objects.filter(user=request.user).delete()
        return Response({"message": "All search history cleared successfully"}, status=status.HTTP_204_NO_CONTENT)
