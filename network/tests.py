from django.urls import reverse
from django.test import TestCase, Client

from .models import User, Post

# Create your tests here.
class TestUserModel(TestCase):
    """
    From the User model,
    tests that the "following" ManyToMany field is properly working
    and that the serialize method has proper output
    """

    def setUp(self):
        u1 = User.objects.create(username="TestUser1")
        u2 = User.objects.create(username="TestUser2")
        u3 = User.objects.create(username="TestUser3")
    
    def test_following_add(self):
        """ Checks that users are properly added to a user's following list """
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        u1.following.add(u2)
        self.assertEqual(u1.following.get(pk=2), u2)

    def test_following_remove(self):
        """ Checks that users are properly removed from a user's following list """
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        u1.following.add(u2)
        u1.following.remove(u2)
        self.assertFalse(u1.following.filter(pk=2).exists())
    
    def test_following_count(self):
        """ Checks that a user's followers' list is properly counted """
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        u3 = User.objects.get(pk=3)
        u1.following.add(u2, u3)
        self.assertEqual(u1.following.count(), 2)

    def test_serialize_dict(self):
        """ Checks that the output of the serialize method is a dictionary """
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        self.assertTrue(isinstance(u1.serialize(u2), dict))

    def test_serialize_values(self):
        """ Checks that the values of the output of the serialize method match those of the user """
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        u1s = u1.serialize(u2)
        self.assertEqual(u1s["id"], u1.pk)
        self.assertEqual(u1s["username"], u1.username)

    def test_serialize_is_followed(self):
        """ Checks that the is_followed logic works properly """
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        # User 2 now follows user 1
        u2.following.add(u1)
        # Asserts that user 1 is being followed by user 2
        self.assertTrue(u1.serialize(u2)["is_followed"])


class TestPostModel(TestCase):
    """
    From the Post model,
    tests that the "likedby" ManyToMany field is properly working
    and that the serialize method has proper output
    """
    
    def setUp(self):
        u1 = User.objects.create(username="TestUser1")
        u2 = User.objects.create(username="TestUser2")
        p1 = Post.objects.create(content="Hello, world!", user=u1)

    def test_likedby_add(self):
        """ Checks that posts are properly added to a post's likedby list """
        p1 = Post.objects.get(pk=1)
        u1 = User.objects.get(pk=1)
        p1.likedby.add(u1)
        self.assertEqual(p1.likedby.get(pk=u1.pk), u1)

    def test_likedby_remove(self):
        """ Checks that posts are properly removed to a post's likedby list """
        p1 = Post.objects.get(pk=1)
        u1 = User.objects.get(pk=1)
        p1.likedby.add(u1)
        p1.likedby.remove(u1)
        self.assertFalse(p1.likedby.filter(pk=u1.pk).exists())
    
    def test_likedby_count(self):
        """ Checks that likes on a post are properly counted """
        p1 = Post.objects.get(pk=1)
        u1 = User.objects.get(pk=1)
        u2 = User.objects.get(pk=2)
        # The post is now liked by users 1 and 2
        p1.likedby.add(u1, u2)
        self.assertEqual(p1.likedby.count(), 2)

    def test_serialize_dict(self):
        """ Checks that the output of the serialize method is a python dictionary """
        p1 = Post.objects.get(pk=1)
        self.assertTrue(isinstance(p1.serialize(), dict))
    
    def test_serialize_values(self):
        """ Checks that the output values of the serialize method matches the original values of the post, while also checking the ordinalsuffix method """
        p1 = Post.objects.get(pk=1)
        p1s = p1.serialize()
        self.assertEqual(p1s["id"], p1.pk)
        self.assertEqual(p1s["content"], p1.content)
        self.assertEqual(p1s["likes"], p1.likedby.count())
        self.assertEqual(p1s["timestamp"], p1.timestamp.strftime("%b %#d" ) + p1.ordinalsuffix() + p1.timestamp.strftime(" %Y, %I:%M %p"))
        self.assertEqual(p1s["user"], p1.user.username)

class TestViews(TestCase):

    def setUp(self):
        u1 = User.objects.create(username="TestUser1")
        p1 = Post.objects.create(content="Hello, world!", user=u1)
        u1.set_password("password")
        u1.save()
    
    def test_index_template(self):
        """ Checks that the correct template is returned by the index view """
        c = Client()
        c.login(username="TestUser1", password="password")
        response = c.get(reverse("index"))
        self.assertTrue("index.html" in [template.name.split("/")[-1] for template in response.templates])
        self.assertTrue(response.context["form"])