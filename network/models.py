from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", symmetrical=False)
    pass

class Post(models.Model):
    content = models.CharField(max_length=1028)
    likedby = models.ManyToManyField(User, blank=True, related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)