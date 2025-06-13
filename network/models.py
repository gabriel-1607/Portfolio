from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", symmetrical=False)

    def serialize(self, logged_user):
        if User.objects.get(id=logged_user.id).following.filter(id=self.id).exists():
              is_followed = True
        else:
             is_followed = False
        return {
              "id": self.id,
              "username": self.username,
              "is_followed": is_followed
        }

class Post(models.Model):
    content = models.CharField(max_length=1028)
    likedby = models.ManyToManyField(User, blank=True, related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "likes": self.likedby.all().count(),
            "timestamp": self.timestamp.strftime("%b %#d" ) + self.ordinalsuffix() + self.timestamp.strftime(" %Y, %I:%M %p"),
            "user": self.user.username
        }

    def ordinalsuffix(self):
        day = self.timestamp.day
        if day >= 11 and day <= 13:
             return "th"
        elif day % 10 == 1:
                return "st"
        elif day % 10 == 2:
                return "nd"
        elif day % 10 == 3:
             return "rd"
        else:
             return "th"