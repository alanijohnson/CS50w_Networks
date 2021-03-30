# https://medium.com/@raaj.akshar/creating-reverse-related-objects-with-django-rest-framework-b1952ddff1c
# https://www.geeksforgeeks.org/modelserializer-in-serializers-django-rest-framework/

#from django.core import serializers
from .models import Post, User, UserProfile, FollowModel
from rest_framework import serializers
import datetime


class ProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = ('first_name','last_name','picture')



class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(method_name='get_profile')
    followers = serializers.SerializerMethodField(method_name='get_followers')
    following = serializers.SerializerMethodField(method_name='get_following')
    
    
    class Meta:
        model = User
        fields = ('id','username','profile','followers','following')
    
    def get_profile(self,obj):
        return ProfileSerializer(obj.profile).data
        
    def get_followers(self,obj):
        return [followSet.follower.id for followSet in FollowModel.objects.filter(followed=obj)]
        
    def get_following(self,obj):
        return [followSet.followed.id for followSet in FollowModel.objects.filter(follower=obj)]
    

class PostSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField(method_name='get_children')
    username = serializers.SerializerMethodField(method_name='get_username')
    picture = serializers.SerializerMethodField(method_name='get_picture')
    name = serializers.SerializerMethodField(method_name='get_name')
    root = serializers.SerializerMethodField(method_name='get_root')
    root_type_text = serializers.SerializerMethodField(method_name='get_root_type_text')
    date_posted = serializers.DateTimeField(format="%b %-d, %y %I:%M%p")
    stats = serializers.SerializerMethodField(method_name='get_stats')
    children_ids = serializers.SerializerMethodField(method_name='get_children_ids')
    
    class Meta:
        model = Post
        exclude = ('')
    
    def get_children(self,obj):
        children = {}
        for child in obj.child.order_by("-date_posted"):
            children[child.id] = ChildSerializer(child).data
        return children
    
    def get_children_ids(self,obj):
        children = []
        for child in obj.child.order_by("-date_posted"):
            children.append(child.id)
        return children

    def get_username(self,obj):
        return obj.user.username
        
    def get_picture(self,obj):
        return obj.user.profile.picture

    def get_name(self, obj):
        return f"{obj.user.profile.first_name} {obj.user.profile.last_name}"
        
    def get_root(self, obj):
        return RootSerializer(obj.root).data
        
    def get_root_type_text(self, obj):
        if obj.root_type == 2:
            return f"{obj.user.username} reshared"
            
        return ""
    
    def get_stats(self, obj):
        children = Post.objects.filter(root=obj.id)
        print(children)
        return {
            'likes': obj.likes.count(),
            'comments': children.filter(root_type = 1).count(),
            'reshares': children.filter(root_type = 2).count()
        }
    
class ChildSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        fields = ('user','date_posted','content','root_type')

class RootSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(method_name='get_username')
    name = serializers.SerializerMethodField(method_name='get_name')
    children = serializers.SerializerMethodField(method_name='get_children')
    picture = serializers.SerializerMethodField(method_name='get_picture')
    class Meta:
        model = Post
        fields = ('id','user','username','picture','name','date_posted','content','children')

    def get_username(self,obj):
        return obj.user.username
    
    def get_name(self, obj):
        return f"{obj.user.profile.first_name} {obj.user.profile.last_name}"
    
    def get_children(self, obj):
        children = {}
        for child in obj.child.all():
            children[child.id] = {'content': child.content}
        return children

    def get_picture(self,obj):
        return obj.user.profile.picture
