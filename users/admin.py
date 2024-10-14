from django.contrib import admin

from users.models import User, Follow, Post, Like, Comment

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Like)
admin.site.register(Comment)
