from django.urls import path
from api_social.views import (
    UserViewSet,
    UserFollowersView,
    FollowView,
    PostViewSet,
    CommentViewSet,
    LikeView,
)

urlpatterns = [
    path(
        "users/",
        UserViewSet.as_view({"get": "list", "post": "create"}),
        name="user-list",
    ),
    path("followers/", UserFollowersView.as_view(), name="get_followers"),
    path("follow/<int:user_id>/", FollowView.as_view(), name="follow"),
    path("unfollow/<int:user_id>/", FollowView.as_view(), name="unfollow"),
    path(
        "posts/",
        PostViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        ),
        name="post-list",
    ),
    path("posts/<int:post_id>/like/",
         LikeView.as_view(),
         name="like-post"
         ),
    path(
        "posts/<int:post_id>/unlike/",
        LikeView.as_view(),
        name="unlike-post"
    ),
    path(
        "comments/",
        CommentViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        ),
        name="comment-list",
    ),
    path(
        "comments/<int:pk>/",
        CommentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy"
            }
        ),
        name="comment-detail",
    ),
]
