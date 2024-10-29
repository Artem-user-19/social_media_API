from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.settings import api_settings

from api_social.serializers import (
    UserSerializer,
    UserFollowingListSerializer,
    PostSerializer,
    CommentSerializer,
    FollowSerializer,
)
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .models import Post, Follow, Comment, Like
from rest_framework.authtoken.views import ObtainAuthToken


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Token.objects.create(user=user)
        return Response(
            {
                "user": serializer.data,
                "token": user.auth_token.key
            }
        )


class UserFollowersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        followers = Follow.objects.filter(
            followed=user
        ).select_related("follower")
        follower_users = [follow.follower for follow in followers]
        serializer = UserFollowingListSerializer(follower_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowView(generics.GenericAPIView):
    serializer_class = FollowSerializer

    def post(self, request, *args, **kwargs):
        user_to_follow_id = kwargs.get("user_id")
        user_to_follow = User.objects.get(id=user_to_follow_id)

        follow_instance, created = Follow.objects.get_or_create(
            follower=request.user, followed=user_to_follow
        )

        if not created:
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(follow_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_to_unfollow_id = kwargs.get("user_id")
        user_to_unfollow = User.objects.get(id=user_to_unfollow_id)

        follow_instance = Follow.objects.filter(
            follower=request.user, followed=user_to_unfollow
        ).first()

        if not follow_instance:
            return Response(
                {"detail": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_instance.delete()
        return Response(
            {
                "detail": "Unfollowed successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )


class UnfollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_unfollow = User.objects.get(id=user_id)
            follow_instance = Follow.objects.filter(
                follower=request.user,
                followed=user_to_unfollow
            ).first()

            if follow_instance:
                follow_instance.delete()
                return Response(
                    {
                        "detail": f"You have unfollowed {user_to_unfollow.username}."
                    },
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "detail": "You are not following this user."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request):
        user = request.user
        following_users = user.following.all()
        posts = Post.objects.filter(
            user__following__in=following_users
        ).order_by(
            "-created_at"
        )
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )
        if created:
            return Response(
                {
                    "message": "Post liked"
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "Post already liked"
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, post_id):
        post = Post.objects.get(id=post_id)
        try:
            like = Like.objects.get(post=post, user=request.user)
            like.delete()
            return Response(
                {
                    "message": "Post unliked"
                },
                status=status.HTTP_200_OK
            )
        except Like.DoesNotExist:
            return Response(
                {"message": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UnlikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like_instance = Like.objects.filter(user=request.user, post=post).first() #

            if like_instance:
                like_instance.delete()
                return Response(
                    {
                        "detail": f"You have unliked the post with ID {post_id}."
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "detail": "You have not liked this post."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Post.DoesNotExist:
            return Response(
                {
                    "detail": "Post not found."
                }, status=status.HTTP_404_NOT_FOUND
            )


class ObtainAuthTokenView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
