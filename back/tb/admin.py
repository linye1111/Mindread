from django.contrib import admin
from .models import User, Book, Tag, Blog, Comment, Book_tag
# Register your models here.


class MyAdminSite(admin.AdminSite):
    site_header = '铭阅 线上读书交流平台'
    site_title = '铭阅'


admin_site = MyAdminSite(name='management')
admin.site = admin_site


class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'user_phone', 'user_name', 'user_email',
                    'user_password', 'user_gender']
    list_display_links = ['user_id', 'user_phone']
    list_editable = ['user_name', 'user_email',
                     'user_password', 'user_gender']
    search_fields = ['user_id', 'user_phone', 'user_name', 'user_email',
                     'user_password', 'user_gender']


class BookAdmin(admin.ModelAdmin):
    list_display = ['book_ISBN', 'book_title',
                    'book_subtitle', 'book_orititle']
    list_display_links = ['book_ISBN', 'book_title',
                          'book_subtitle', 'book_orititle']
    search_fields = ['book_ISBN', 'book_title',
                     'book_subtitle', 'book_orititle']


class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_id', 'tag_name']
    list_display_links = ['tag_id']
    list_editable = ['tag_name']
    search_fields = ['tag_id', 'tag_name']


class BlogAdmin(admin.ModelAdmin):
    list_display = ['blog_id', 'blog_title']
    list_display_links = ['blog_id']
    list_editable = ['blog_title']
    search_fields = ['blog_id', 'blog_title']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'comment_content', 'comment_iscomplained']
    list_display_links = ['comment_id']
    list_editable = ['comment_content', 'comment_iscomplained']
    search_fields = ['comment_id', 'comment_content', 'comment_iscomplained']


class Book_tagAdmin(admin.ModelAdmin):
    list_display = ['book_tag_id', 'book_tag_book_ISBN', 'book_tag_tag_id']
    list_display_links = ['book_tag_id', ]
    list_editable = ['book_tag_book_ISBN', 'book_tag_tag_id']
    search_fields = ['book_tag_id', 'book_tag_book_ISBN', 'book_tag_book_ISBN']


admin_site.register(User, UserAdmin)
admin_site.register(Book, BookAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(Blog, BlogAdmin)
admin_site.register(Comment, CommentAdmin)
admin_site.register(Book_tag, Book_tagAdmin)
