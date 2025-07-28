from django.db import models
from rest_framework.authtoken.admin import User


# Create your models here.

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')


    def __str__(self):
        return str(self.follower) + " is following " + str(self.following)
    class Meta:
        unique_together = (('follower', 'following'),)
