"""
Comprehensive test suite for Barta 2.0 social media platform
Tests all major functionality including models, views, and features
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import json

from core.models import Owner, Post, PostLike, PostComment, UserFollow, Message, Notification
# Import SocialApp for testing allauth
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class ModelTestCase(TestCase):
    """Test all model functionality and relationships"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User2'
        )
        
        # Create owner profiles
        self.owner1 = Owner.objects.create(
            user=self.user1,
            bio='Test bio for user 1',
            location='Test City'
        )
        self.owner2 = Owner.objects.create(
            user=self.user2,
            bio='Test bio for user 2',
            location='Another City'
        )
    
    def test_owner_model(self):
        """Test Owner model functionality"""
        self.assertEqual(str(self.owner1), 'testuser1')
        self.assertEqual(self.owner1.user.username, 'testuser1')
        self.assertEqual(self.owner1.bio, 'Test bio for user 1')
        self.assertFalse(self.owner1.is_verified)
        self.assertFalse(self.owner1.is_private)
    
    def test_post_model(self):
        """Test Post model functionality"""
        post = Post.objects.create(
            owner=self.owner1,
            content='Test post content',
            title='Test Post'
        )
        self.assertEqual(post.owner, self.owner1)
        self.assertEqual(post.content, 'Test post content')
        self.assertFalse(post.is_pinned)
        self.assertIn('testuser1', str(post))
    
    def test_post_like_model(self):
        """Test PostLike model functionality"""
        post = Post.objects.create(
            owner=self.owner1,
            content='Test post for liking'
        )
        like = PostLike.objects.create(
            owner=self.owner2,
            post=post,
            reaction_type='like'
        )
        self.assertEqual(like.owner, self.owner2)
        self.assertEqual(like.post, post)
        self.assertEqual(like.reaction_type, 'like')
        
        # Test unique constraint
        with self.assertRaises(Exception):
            PostLike.objects.create(owner=self.owner2, post=post)
    
    def test_post_comment_model(self):
        """Test PostComment model functionality"""
        post = Post.objects.create(
            owner=self.owner1,
            content='Test post for commenting'
        )
        comment = PostComment.objects.create(
            owner=self.owner2,
            post=post,
            content='Test comment'
        )
        self.assertEqual(comment.owner, self.owner2)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.content, 'Test comment')
        self.assertFalse(comment.is_reply)
        self.assertEqual(comment.replies_count, 0)
        
        # Test reply functionality
        reply = PostComment.objects.create(
            owner=self.owner1,
            post=post,
            parent_comment=comment,
            content='Test reply'
        )
        self.assertTrue(reply.is_reply)
        self.assertEqual(comment.replies_count, 1)
    
    def test_user_follow_model(self):
        """Test UserFollow model functionality"""
        follow = UserFollow.objects.create(
            follower=self.owner1,
            following=self.owner2
        )
        self.assertEqual(follow.follower, self.owner1)
        self.assertEqual(follow.following, self.owner2)
        self.assertTrue(follow.is_accepted)
        self.assertIn('testuser1', str(follow))
        self.assertIn('testuser2', str(follow))
        
        # Test unique constraint
        with self.assertRaises(Exception):
            UserFollow.objects.create(follower=self.owner1, following=self.owner2)
    
    def test_message_model(self):
        """Test Message model functionality"""
        message = Message.objects.create(
            sender=self.owner1,
            receiver=self.owner2,
            content='Test message content'
        )
        self.assertEqual(message.sender, self.owner1)
        self.assertEqual(message.receiver, self.owner2)
        self.assertEqual(message.content, 'Test message content')
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)
        
        # Test mark as read
        message.mark_as_read()
        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
    
    def test_notification_model(self):
        """Test Notification model functionality"""
        notification = Notification.objects.create(
            owner=self.owner1,
            content='Test notification',
            title='Test Title'
        )
        self.assertEqual(notification.owner, self.owner1)
        self.assertEqual(notification.content, 'Test notification')
        self.assertFalse(notification.is_read)


class ViewTestCase(TestCase):
    """Test all view functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.owner = Owner.objects.create(
            user=self.user,
            bio='Test bio'
        )
        
        # Create another user for testing interactions
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.owner2 = Owner.objects.create(
            user=self.user2,
            bio='Test bio 2'
        )
    
    def test_home_view_anonymous(self):
        """Test home view for anonymous users"""
        response = self.client.get(reverse('home'))
        # Home view requires login, so should redirect
        self.assertEqual(response.status_code, 302)
        # Check redirect to login page
        self.assertIn('/signin/', response.url)
    
    def test_home_view_authenticated(self):
        """Test home view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_signup_view(self):
        """Test signup functionality"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        
        # Test successful signup
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Owner.objects.filter(user__username='newuser').exists())
    
    def test_signin_view(self):
        """Test signin functionality"""
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        
        # Test successful login
        response = self.client.post(reverse('signin'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_profile_view(self):
        """Test profile view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_friends_view(self):
        """Test friends view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('friends'))
        self.assertEqual(response.status_code, 200)
        # Check for key elements in friends page
        self.assertContains(response, 'Friends')
        self.assertContains(response, 'Following')
    
    def test_messages_view(self):
        """Test messages view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('messages'))
        # Messages view redirects to inbox
        self.assertEqual(response.status_code, 302)
        self.assertIn('/inbox/', response.url)
    
    def test_notifications_view(self):
        """Test notifications view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
    
    def test_post_creation(self):
        """Test post creation"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('create_post'), {
            'content': 'Test post content'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Post.objects.filter(content='Test post content').exists())
    
    def test_follow_functionality(self):
        """Test follow/unfollow functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test follow
        response = self.client.post(reverse('follow_user', args=['testuser2']))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserFollow.objects.filter(
            follower=self.owner,
            following=self.owner2
        ).exists())


class IntegrationTestCase(TestCase):
    """Test integrated functionality and workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        self.owner1 = Owner.objects.create(user=self.user1)
        self.owner2 = Owner.objects.create(user=self.user2)
    
    def test_social_workflow(self):
        """Test complete social media workflow"""
        # User1 logs in
        self.client.login(username='user1', password='testpass123')
        
        # User1 creates a post
        post_response = self.client.post(reverse('create_post'), {
            'content': 'Hello world! This is my first post.'
        })
        self.assertEqual(post_response.status_code, 302)
        
        post = Post.objects.get(content='Hello world! This is my first post.')
        
        # User1 follows User2
        follow_response = self.client.post(reverse('follow_user', args=['user2']))
        self.assertEqual(follow_response.status_code, 302)
        
        # Logout User1, login User2
        self.client.logout()
        self.client.login(username='user2', password='testpass123')
        
        # User2 likes the post
        like_response = self.client.post(reverse('like_post', args=[post.id]))
        self.assertEqual(like_response.status_code, 302)
        
        # User2 comments on the post
        comment_response = self.client.post(reverse('comment_post', args=[post.id]), {
            'content': 'Great first post!'
        })
        self.assertEqual(comment_response.status_code, 302)
        
        # Verify data integrity
        self.assertTrue(PostLike.objects.filter(post=post, owner=self.owner2).exists())
        self.assertTrue(PostComment.objects.filter(post=post, owner=self.owner2).exists())
        self.assertTrue(UserFollow.objects.filter(
            follower=self.owner1,
            following=self.owner2
        ).exists())


class PerformanceTestCase(TestCase):
    """Test performance and data handling"""
    
    def test_large_dataset_handling(self):
        """Test handling of larger datasets"""
        # Create multiple users
        users = []
        for i in range(50):
            user = User.objects.create_user(
                username=f'user{i}',
                password='testpass123'
            )
            owner = Owner.objects.create(user=user)
            users.append(owner)
        
        # Create multiple posts
        for i, owner in enumerate(users[:10]):  # First 10 users create posts
            for j in range(5):  # 5 posts each
                Post.objects.create(
                    owner=owner,
                    content=f'Post {j} by {owner.user.username}'
                )
        
        # Verify data creation
        self.assertEqual(User.objects.count(), 50)
        self.assertEqual(Owner.objects.count(), 50)
        self.assertEqual(Post.objects.count(), 50)
        
        # Test home view performance with data
        client = Client()
        user = users[0].user
        client.login(username=user.username, password='testpass123')
        
        response = client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class SecurityTestCase(TestCase):
    """Test security measures"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.owner = Owner.objects.create(user=self.user)
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.other_owner = Owner.objects.create(user=self.other_user)
    
    def test_authentication_required(self):
        """Test that protected views require authentication"""
        protected_urls = [
            reverse('profile'),
            reverse('friends'),
            reverse('messages'),
            reverse('notifications'),
            reverse('create_post'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            # Should redirect to login or return 403
            self.assertIn(response.status_code, [302, 403])
    
    def test_post_ownership(self):
        """Test that users can only edit their own posts"""
        # Create post by user1
        self.client.login(username='testuser', password='testpass123')
        post = Post.objects.create(
            owner=self.owner,
            content='Original content'
        )
        
        # Try to edit as other user
        self.client.logout()
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.post(reverse('edit_post', args=[post.id]), {
            'content': 'Modified content'
        })
        
        # Should not allow editing
        post.refresh_from_db()
        self.assertNotEqual(post.content, 'Modified content')


class SocialAuthTestCase(TestCase):
    """Test social authentication functionality"""

    def setUp(self):
        """Set up test data for social auth"""
        self.client = Client()
        # Ensure the site used by allauth matches the test host
        site, _ = Site.objects.update_or_create(
            pk=settings.SITE_ID,
            defaults={'domain': 'testserver', 'name': 'testserver'}
        )
        # Create a social app
        if not SocialApp.objects.filter(provider='google').exists():
            app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
                secret=settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
            )
            app.sites.add(site)

    def test_google_login_redirect(self):
        """Test that the Google login URL redirects correctly"""
        response = self.client.get('/accounts/google/login/')
        # When provider is configured correctly, we should be redirected to Google
        self.assertEqual(response.status_code, 302, "Google login should redirect externally")
        self.assertIn('accounts.google.com', response.url)

    def test_oauth_provider_configuration(self):
        """Test that the OAuth provider is properly configured"""
        # Check if Google app exists
        google_app = SocialApp.objects.filter(provider='google').first()
        self.assertIsNotNone(google_app, "Google social app should be configured")
        self.assertEqual(google_app.client_id, settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'])
        self.assertEqual(google_app.secret, settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'])
        
    def test_allauth_urls_configured(self):
        """Test that allauth URLs are properly configured"""
        # Test that we can access the accounts root
        response = self.client.get('/accounts/login/')
        # Login view should exist (200 OK) or redirect (302) depending on config
        self.assertIn(response.status_code, [200, 302])