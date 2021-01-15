from django.db import models
from user.models import User


class Category(models.Model):
    name = models.CharField(max_length=32)
   
    class Meta:
        db_table = "categories"

class Tag(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        db_table = "tags"

class Topic(models.Model):
    name = models.CharField(max_length=32)

    class Meta:
        db_table = "topics"

class Board(models.Model):
    category   = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    topic      = models.ForeignKey("Topic", on_delete=models.SET_NULL, null=True)
    user       = models.ForeignKey("user.User", on_delete=models.CASCADE)
    title      = models.CharField(max_length=64)
    content    = models.TextField()
    image      = models.URLField(max_length=512, null=True)
    hit        = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    solution   = models.BooleanField(default=False)

    class Meta:
        db_table = "boards"

class BoardTag(models.Model):
    tag = models.ForeignKey("Tag", on_delete=models.SET_NULL, null=True)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
     
    class Meta:
        db_table = "board_tags"

class BoardLike(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    board = models.ForeignKey("Board", on_delete=models.CASCADE)
     
    class Meta:
        db_table = "board_likes"

class Comment(models.Model):
    user     = models.ForeignKey("user.User", on_delete=models.CASCADE)
    board    = models.ForeignKey("Board", on_delete=models.CASCADE)
    content  = models.TextField()
    reply    = models.ForeignKey('self', on_delete = models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    solution = models.BooleanField(default=False)
    
    class Meta:
        db_table = "coments"

class CommentLike(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    coment = models.ForeignKey("Comment", on_delete=models.CASCADE)
     
    class Meta:
        db_table = "comment_likes"