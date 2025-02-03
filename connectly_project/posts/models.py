from django.core.validators import RegexValidator
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100,
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$',
        message='Usernames can only contain letters and numbers.',
        code="invalid_username"),],
        unique=True)
  # User's unique username
    email = models.EmailField(unique=True)  # User's unique email
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created


    def __str__(self):
        return self.username

