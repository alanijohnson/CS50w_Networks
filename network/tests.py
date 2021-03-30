from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import Client,TestCase
from .models import User, UserProfile, Post, FollowModel
import json
from unittest import skip

# Create your tests here.
class UserTestCase(TestCase):
    
    def setUp(self):
        
        #create user 1
        u1 = User(username="user1", password="test", email="user1@network.com")
        u1.save()
        up1 = UserProfile(user=u1, first_name="A", last_name="J")
        up1.save()
        
        #create user 2
        u2 = User(username="user2", password="test", email="user2@network.com")
        u2.save()
        up2 = UserProfile(user=u2, first_name="W", last_name="P")
        up2.save()
        
    
    def test_user_count(self):
        """ Ensure all Users have been Created """
        self.assertEquals(User.objects.all().count(), 2)
        
    def test_userprofile_count(self):
        """ Ensure all User Profiles have been created """
        self.assertEquals(User.objects.all().count(), 2)
    
    def test_get_user(self):
        u1 = User.objects.get(username="user1")
        self.assertIsInstance(u1,User)
    
    def test_user_access_profile(self):
        """ Ensure User1 profile can be accessed """
        u1 = User.objects.get(username="user1")
        self.assertIsInstance(u1.profile,UserProfile)
    
    def test_user_profile(self):
        """ Access UserProfile Data """
        u1 = User.objects.get(username="user1")
        up1 = UserProfile.objects.get(user=u1)
        self.assertIsInstance(up1, UserProfile)
        self.assertEquals(up1.first_name,"A")
        self.assertEquals(up1.last_name,"J")
    
    
    def test_followers(self):
        """
        Test following user and accessing the follow model object
        1. Follow user
        2. Create the same follow model
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        f = FollowModel(follower=u1, followed=u2)
        f.save()
        
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 1)
        self.assertEqual(len(u2.get_followers()), 1)
        self.assertEqual(len(u2.get_following()), 0)
        
        self.assertEqual(u2.get_followers()[0], u1)
        self.assertEqual(u1.get_following()[0], u2)
        
    def test_add_follower(self):
        """
        Test add follower using following.create()
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        u1.following.create(followed=u2)
        
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 1)
        self.assertEqual(len(u2.get_followers()), 1)
        self.assertEqual(len(u2.get_following()), 0)
        
    def test_remove_follower(self):
        """
        Test removing follower
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        u1.following.create(followed=u2)
        
        u = u1.following.get(followed=u2)
        self.assertIsInstance(u,FollowModel)
        
        u.delete()
        
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 0)
        self.assertEqual(len(u2.get_followers()), 0)
        self.assertEqual(len(u2.get_following()), 0)
        
    def test_follow(self):
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        u3 = User(username="user3", password="test", email="user1@network.com")
        u3.save()
        
        u1.follow(u2)
        u1.follow(u3)
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 2)
       
    def test_unfollow(self):
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        u3 = User(username="user3", password="test", email="user1@network.com")
        u3.save()
        
        u1.follow(u2)
        u1.follow(u3)
        u1.unfollow(u2)
        
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 1)
        self.assertEqual(u1.get_following()[0], u3)
        
class PostTestCase(TestCase):

    def setUp(self):
        
        # create a user
        u1 = User(username="user1", password="test", email="user1@network.com")
        u1.save()
        up1 = UserProfile(user=u1, first_name="A", last_name="J")
        up1.save()
        
        # create a post
        p1 = Post(user=u1, content="Test Content")
        p1.save()
        
    def test_post_count(self):
        """Ensure 1 post was created"""
        self.assertEquals(Post.objects.all().count(),1)
    
    def test_get_post(self):
        """ Ensure post can be accessed and has correct data """
        p1 = Post.objects.get(id=1)
        u1 = User.objects.get(username="user1")
        self.assertIsInstance(p1,Post)
        self.assertEqual(p1.content,"Test Content")
        self.assertEqual(p1.user, u1)
        self.assertIsNotNone(p1.date_posted)
        
    def test_like_post(self):
        #create user 2
        u2 = User(username="user2", password="test", email="user2@network.com")
        u2.save()
        up2 = UserProfile(user=u2, first_name="W", last_name="P")
        up2.save()
        
        p1 = Post.objects.get(id=1)
        u1 = User.objects.get(username="user1")
        
        self.assertEqual(p1.likes.all().count(), 0)
        
        p1.likes.add(u2)
        
        self.assertEqual(p1.likes.all().count(), 1)
        
        p1.likes.remove(u2)
        
        self.assertEqual(p1.likes.all().count(), 0)
        
class FollowModelTestCase(TestCase):

    def setUp(self):
        #create user 1
        u1 = User(username="user1", password="test", email="user1@network.com")
        u1.save()
        up1 = UserProfile(user=u1, first_name="A", last_name="J")
        up1.save()
        
        #create user 2
        u2 = User(username="user2", password="test", email="user2@network.com")
        u2.save()
        up2 = UserProfile(user=u2, first_name="W", last_name="P")
        up2.save()
        
    
    def test_follow(self):
        """
        Test following user
        1. Follow user
        2. Create the same follow model
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        
        f = FollowModel(follower=u1, followed=u2)
        f.save()
        self.assertIsInstance(f,FollowModel)
        f2 = FollowModel(follower=u1, followed=u2)
        self.assertRaises(IntegrityError,f2.save)
        
    def test_related_name(self):
        """
        Test following user and accessing the follow model object
        1. Follow user
        2. Create the same follow model
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        f = FollowModel(follower=u1, followed=u2)
        f.save()
        
        self.assertEqual(u1.followers.count(),0)
        self.assertEqual(u1.following.count(),1)
        self.assertEqual(u2.followers.count(),1)
        self.assertEqual(u2.following.count(),0)
        
class ViewTest(TestCase):
    
    def setUp(self):
        #create user 1
        u1 = User(username="user1", email="user1@network.com")
        u1.set_password("test")
        u1.save()
        up1 = UserProfile(user=u1, first_name="A", last_name="J")
        up1.save()
        
        #create user 2
        u2 = User(username="user2", password="test", email="user2@network.com")
        u2.save()
        up2 = UserProfile(user=u2, first_name="W", last_name="P")
        up2.save()
        
        self.user = u1
        
    def test_users(self):
        # set up client
        c = Client()

        # Send get request to index page and store response
        response = c.get("/users")

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)
        
    def test_post(self):
        """
        test accessing post view
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        p = Post(user=u2, content="test content")
        p.save()
        
        
        # set up client
        c = Client()

        # Send get request to index page and store response
        response = c.get(f"/post/{p.id}")

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        """
        test deleting post from view
        """
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        p = Post(user=u1, content="test content")
        p.save()
        
        
        # set up client
        c = Client()
        success = c.login(username="user1",password="test")
        self.assertTrue(success)
        self.assertEqual(Post.objects.all().count(),1)
        dict = {
            "post": p.id
        }
        response = c.post("/delete", json.dumps(dict),content_type="application/json")

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.all().count(),0)
    
    def test_follow(self):
        u1 = User.objects.get(username="user1")
        
        c = Client()
        success = c.login(username="user1",password="test")
        self.assertTrue(success)
        
        u2 = User.objects.get(username="user2")
        dict = {
            "action":"follow",
            "user": u2.id
        }
        response = c.post("/follow", json.dumps(dict),content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 1)
        
    def test_unfollow(self):
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        
        u1.follow(u2)
        
        c = Client()
        success = c.login(username="user1",password="test")
        self.assertTrue(success)
        
        
        dict = {
            "action":"unfollow",
            "user": u2.id
        }
        response = c.post("/follow", json.dumps(dict),content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(u1.get_followers()), 0)
        self.assertEqual(len(u1.get_following()), 0)
        
    def test_following(self):
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        p = Post(user=u2, content="test content")
        p.save()
        
        self.assertEqual(u2.posts.all().count(),1)
        
        
        c = Client()
        success = c.login(username="user1",password="test")
        self.assertTrue(success)
        self.assertEqual(len(u1.get_following()),0)
        
        
        response = c.get("/following")
        self.assertEqual(len(json.loads(response.content)),0)

        u1.follow(u2)

        response = c.get("/following")
        data = json.loads(response.content)
        #print(f"{data[0]}")
        self.assertEqual(len(data),1)
        self.assertEqual(data[0].get("user"), 2)
        
        
    def test_liking(self):
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        p = Post(user=u2, content="test content")
        p.save()
        
        self.assertEqual(p.likes.all().count(),0)
        
        
        c = Client()
        success = c.login(username="user1",password="test")
        self.assertTrue(success)
        
        dict = {
            "action":"like",
            "post": p.id
        }
        response = c.post("/like", json.dumps(dict),content_type="application/json")
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(p.likes.all().count(),1)
        
        
        dict = {
            "action":"unlike",
            "post": p.id
        }
        response = c.post("/like", json.dumps(dict),content_type="application/json")
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(p.likes.all().count(),0)
        
        
        

if __name__ == "__main__":
    unittest.main()
