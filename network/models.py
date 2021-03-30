from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core import serializers
from django.db import models


class User(AbstractUser):
    
    def get_followers(self):
        return [fm.follower for fm in self.followers.all()]
        
    def get_following(self):
        return [fm.followed for fm in self.following.all()]
        
    def follow(self, user):
        return self.following.create(followed=user)
    
    def unfollow(self, user):
        fm = self.following.get(followed=user)
        fm.delete()
    
    pass


class UserProfile(models.Model):
    DEFAULT_PIC = "https://moonvillageassociation.org/wp-content/uploads/2018/06/default-profile-picture1.jpg"
    # User
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, primary_key=True, related_name='profile')
    # First Name
    first_name = models.CharField('first name', unique=False, max_length = 64, null=False)
    # Last Name
    last_name = models.CharField('last name', unique=False, max_length = 64, null=False)
    # Location
    # Profile Picture
    picture = models.URLField('profile picture URL', unique=False, default=DEFAULT_PIC, blank=True)
    # Followers
    # following = models.ManyToManyField('self', related_name='followers');
    pass


class Post(models.Model):
    
    class Type(models.IntegerChoices):
        ORIGINAL = 0, "Initial Post"
        REPLY = 1, "Reply"
        RESHARE = 2, "Reshare"
      
    # User
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='posts')
    # Content
    content = models.TextField('Enter Content', null=False, default="",blank=True)
    #date posted / edited
    date_posted = models.DateTimeField('Date Posted', default=timezone.now(), null=False)
    # Root Comment - Default NULL
    root = models.ForeignKey('self', on_delete = models.CASCADE, blank=True, default=None, null=True, related_name = 'child')
    # Likes
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    # root type - reply or retweet. Will allow access to meta data about other post and allow differnt type of view.
    root_type = models.IntegerField('type', default=Type.ORIGINAL, choices=Type.choices)
    
#    class Meta:
#        constraints = [models.CheckConstraint(
#                        name = "Original Post cannot have root",
#                        check = models.Q(models.F('root_type') == 0) & models.Q(models.F('root') == None )),
#                      models.CheckConstraint(
#                        name = "Non Original Post must have root",
#                        check = models.Q(models.F('root_type') != 0) & models.Q(models.F('root') != None ))
#        ]
    
    
    def __str__(self):
        return f"{self.user.username}: {self.content}"


class FollowModel(models.Model):
    # The follower is the user that follows another user. To access this model (i.e. who they follow), use following
    follower = models.ForeignKey(User, on_delete = models.CASCADE, related_name='following')
    # The followed is the user that is followed by another. To access this model (i.e who follows them), use followers
    followed = models.ForeignKey(User, on_delete = models.CASCADE, related_name='followers')
    date = models.DateTimeField('Date Followed', default=timezone.now(), null=False)
    
    class Meta:
        # a person can only follow a person once. Do not allow this.
        unique_together = ['follower','followed']
        constraints = [models.CheckConstraint(
                        name = "Follower matches following",
                        check = ~models.Q(follower=
                            models.F('followed')
                    ))]
