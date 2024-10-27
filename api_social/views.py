from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import User, Post, Comment, Follow
from .serializers import UserSerializer, PostSerializer, CommentSerializer, FollowSerializer
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        user = self.get_serializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save()
        Token.objects.create(user=user.instance)
        return Response(user.data)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid credentials'}, status=400)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def follow(self, request):
        followed_user_id = request.data.get('followed')
        followed_user = User.objects.get(id=followed_user_id)
        Follow.objects.create(follower=request.user, followed=followed_user)
        return Response({'message': 'Followed successfully'})

    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        followed_user_id = request.data.get('followed')
        Follow.objects.filter(follower=request.user, followed_id=followed_user_id).delete()
        return Response({'message': 'Unfollowed successfully'})

    @action(detail=False, methods=['get'])
    def following(self, request):
        followed_users = request.user.following.all()
        return Response({'following': [followed.followed.username for followed in followed_users]})


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user__in=self.request.user.following.all())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
