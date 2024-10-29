from django.contrib import admin

from api_social.models import (
    Post,
    User,
    Follow,
    Comment,
    Like
)

admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
