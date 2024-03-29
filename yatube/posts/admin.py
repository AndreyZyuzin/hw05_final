from django.contrib import admin

from .models import Group, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group', 'image')
    search_fields = ('text', )
    list_filter = ('pub_date', )
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'post', 'author', 'created')
    search_fields = ('text', )
    list_filter = ('created', )
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)

admin.site.register(Group)

admin.site.register(Comment, CommentAdmin)
