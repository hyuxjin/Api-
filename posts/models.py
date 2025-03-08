from django.contrib.auth.models import AbstractUser  # ✅ Import AbstractUser
from django.db import models

class User(AbstractUser):  # ✅ Inherit from AbstractUser
    email = models.EmailField(unique=True)  # Ensure email is unique
    created_at = models.DateTimeField(auto_now_add=True)

    # REQUIRED_FIELDS is needed for Django authentication
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # Track likes

    def __str__(self):
        return f"Post by {self.author.username}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
