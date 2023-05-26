from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='user_profile')
    profile_photo = models.ImageField(blank=True)
    follows = models.ManyToManyField("self",related_name='followed_by',symmetrical=False,blank=True)

    def __str__(self):
        return self.user.username

class Posts(models.Model):
    user = models.ForeignKey(User,related_name='posts',on_delete=models.CASCADE)
    tittle = models.CharField(max_length=40)
    post = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} {self.tittle}'