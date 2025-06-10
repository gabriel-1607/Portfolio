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

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": [self.likedby.all().count()],
            "timestamp": self.timestamp.strftime("%b %#d" ) + self.ordinalsuffix() + self.timestamp.strftime(" %Y, %I:%M %p"),
            "user": self.user.username
        }

    def ordinalsuffix(self):
        day = self.timestamp.day
        if day % 10 == 1:
                return "st"
        elif day % 10 == 2:
                return "nd"
        elif day % 10 == 3:
             return "rd"
        else:
             return "th"