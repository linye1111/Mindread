from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_phone = models.CharField(max_length=64)
    user_email = models.EmailField(null=True, blank=True)
    user_name = models.CharField(max_length=64, blank=True)
    user_gender = models.SmallIntegerField(null=True, blank=True)
    user_password = models.CharField(max_length=64, null=True)
    user_avatar = models.CharField(max_length=256, null=True, blank=True)
    user_createdat = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    user_updatedat = models.DateTimeField(auto_now=True, null=True, blank=True)
    user_selfintro = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user_name

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class User_focus(models.Model):
    user_focus_id = models.AutoField(primary_key=True)
    u_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column="u_id")
    focused_id = models.IntegerField()


class Book(models.Model):
    book_ISBN = models.CharField(max_length=64, primary_key=True)
    book_title = models.CharField(max_length=64)
    book_subtitle = models.CharField(max_length=64, null=True, blank=True)
    book_translator = models.CharField(max_length=64, null=True, blank=True)
    book_img = models.CharField(max_length=64, null=True, blank=True)
    book_press = models.CharField(max_length=64, null=True, blank=True)
    book_date = models.CharField(max_length=64, null=True, blank=True)
    book_price = models.CharField(max_length=64, null=True, blank=True)
    book_brief = models.TextField(null=True, blank=True)
    book_catalog = models.TextField(null=True, blank=True)
    book_author = models.CharField(max_length=64, null=True, blank=True)
    book_orititle = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.book_title

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = verbose_name


class User_book(models.Model):
    user_book_id = models.AutoField(primary_key=True)
    user_book_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="user_book_user_id")
    user_book_book_ISBN = models.ForeignKey(
        Book, on_delete=models.CASCADE, db_column="user_book_book_ISBN")


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_name = models.CharField(max_length=64)

    def __str__(self):
        return self.tag_name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    blog_id = models.CharField(max_length=32, primary_key=True)
    blog_title = models.CharField(max_length=64)
    blog_content = models.TextField()
    blog_book_ISBN = models.ForeignKey(
        Book, on_delete=models.CASCADE, db_column="blog_book_ISBN")
    blog_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="blog_user_id")
    blog_createdat = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    blog_updatedat = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.blog_title

    class Meta:
        verbose_name = '读书笔记'
        verbose_name_plural = verbose_name


class User_blog(models.Model):
    user_blog_id = models.AutoField(primary_key=True)
    user_blog_like = models.NullBooleanField(default=False, null=True)
    user_blog_focus = models.NullBooleanField(default=False, null=True)
    user_blog_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="user_blog_user_id")
    user_blog_blog_id = models.ForeignKey(
        Blog, on_delete=models.CASCADE, db_column="user_blog_blog_id")
    user_blog_createdat = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    user_blog_updatedat = models.DateTimeField(
        auto_now=True, null=True, blank=True)


class Book_tag(models.Model):
    book_tag_id = models.AutoField(primary_key=True)
    book_tag_book_ISBN = models.ForeignKey(
        Book, on_delete=models.CASCADE, db_column="book_tag_book_ISBN")
    book_tag_tag_id = models.ForeignKey(
        Tag, on_delete=models.CASCADE, db_column="book_tag_tag_id")

    class Meta:
        verbose_name = '图书关联标签'
        verbose_name_plural = verbose_name


class User_tag(models.Model):
    user_tag_id = models.AutoField(primary_key=True)
    user_tag_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="user_tag_user_id")
    user_tag_tag_id = models.ForeignKey(
        Tag, on_delete=models.CASCADE, db_column="user_tag_tag_id")


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    comment_content = models.TextField()
    comment_iscomplained = models.NullBooleanField(default=False, blank=True)
    comment_blog_id = models.ForeignKey(
        Blog, on_delete=models.CASCADE, db_column="comment_blog_id")
    comment_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="comment_user_id")
    comment_createdat = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    comment_updatedat = models.DateTimeField(
        auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.comment_id

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
