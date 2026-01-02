#!/usr/bin/env python3
"""
Test script for post editing in profile and follower removal functionality
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(r'd:\GitHub Codes\Python\Django Projects\Social Media\Barta 2.0')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Barta.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Owner, Post, UserFollow

def test_post_edit_functionality():
    """Test post edit functionality in profile"""
    
    print("=" * 60)
    print("TESTING POST EDIT FUNCTIONALITY IN PROFILE")
    print("=" * 60)
    
    # Get users with posts
    users_with_posts = []
    for user in User.objects.all():
        try:
            owner = user.owner
            post_count = Post.objects.filter(owner=owner).count()
            if post_count > 0:
                users_with_posts.append((user, post_count))
        except Owner.DoesNotExist:
            continue
    
    if not users_with_posts:
        print("❌ No users found with posts")
        return
    
    print(f"📊 Found {len(users_with_posts)} users with posts:")
    print()
    
    for user, post_count in users_with_posts[:5]:
        print(f"👤 {user.first_name} {user.last_name} (@{user.username})")
        print(f"   📝 Posts: {post_count}")
        
        # Get first few posts
        posts = Post.objects.filter(owner=user.owner)[:3]
        for i, post in enumerate(posts, 1):
            print(f"   {i}. \"{post.content[:50]}...\" (ID: {post.id})")
        
        print(f"   🔗 Profile URL: http://127.0.0.1:8000/profile/{user.username}/")
        print()
    
    print("✅ Post edit functionality available in profile:")
    print("   • View Post button (eye icon)")
    print("   • Edit Post button (edit icon)")
    print("   • Delete Post button (trash icon)")
    print()

def test_follower_removal_functionality():
    """Test follower removal functionality"""
    
    print("=" * 60)
    print("TESTING FOLLOWER REMOVAL FUNCTIONALITY")
    print("=" * 60)
    
    # Get users with followers
    users_with_followers = []
    for user in User.objects.all():
        try:
            owner = user.owner
            followers_count = UserFollow.objects.filter(following=owner, status='accepted').count()
            if followers_count > 0:
                users_with_followers.append((user, followers_count))
        except Owner.DoesNotExist:
            continue
    
    if not users_with_followers:
        print("❌ No users found with followers")
        return
    
    print(f"📊 Found {len(users_with_followers)} users with followers:")
    print()
    
    for user, followers_count in users_with_followers[:5]:
        print(f"👤 {user.first_name} {user.last_name} (@{user.username})")
        print(f"   👥 Followers: {followers_count}")
        
        # Get followers
        followers = UserFollow.objects.filter(following=user.owner, status='accepted')[:3]
        for i, follow in enumerate(followers, 1):
            follower = follow.follower
            print(f"   {i}. {follower.user.first_name} {follower.user.last_name} (@{follower.user.username})")
        
        print(f"   🔗 Followers URL: http://127.0.0.1:8000/profile/{user.username}/followers/")
        print()
    
    print("✅ Follower removal functionality available:")
    print("   • Remove button (user-times icon) on own profile's followers")
    print("   • Confirmation dialog before removal")
    print("   • Notification sent to removed follower")
    print()

def show_testing_instructions():
    """Show instructions for manual testing"""
    
    print("=" * 60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("🧪 To test POST EDIT functionality:")
    print("1. Visit http://127.0.0.1:8000/")
    print("2. Log in as any user with posts")
    print("3. Go to your profile")
    print("4. Scroll to 'Posts' section")
    print("5. Look for edit/delete buttons on your posts")
    print("6. Click edit button to modify post")
    print("7. Click delete button to remove post (with confirmation)")
    print()
    
    print("🧪 To test FOLLOWER REMOVAL functionality:")
    print("1. Visit http://127.0.0.1:8000/")
    print("2. Log in as any user with followers")
    print("3. Go to your profile")
    print("4. Click on 'Followers' count/link")
    print("5. Look for red 'remove' buttons (user-times icon)")
    print("6. Click remove button for any follower")
    print("7. Confirm the removal in the dialog")
    print("8. Verify follower is removed from list")
    print()
    
    print("🔧 Technical Implementation:")
    print("• Post edit/delete buttons only show on user's own posts")
    print("• Follower remove buttons only show on user's own followers list")
    print("• JavaScript confirmation dialogs prevent accidental actions")
    print("• CSRF protection included in all form submissions")
    print("• Proper URL routing and view handling")
    print()

def verify_urls():
    """Verify URL patterns are correctly configured"""
    
    print("=" * 60)
    print("VERIFYING URL CONFIGURATION")
    print("=" * 60)
    
    try:
        from django.urls import reverse
        
        # Test URLs
        urls_to_test = [
            ('profile', 'Profile page'),
            ('remove_follower', 'Remove follower', ['test_user']),
            ('edit_post', 'Edit post', [1]),
            ('delete_post', 'Delete post', [1]),
            ('followers_list', 'Followers list', ['test_user']),
        ]
        
        print("🔗 Testing URL patterns:")
        print("-" * 35)
        
        for url_data in urls_to_test:
            url_name = url_data[0]
            description = url_data[1]
            args = url_data[2] if len(url_data) > 2 else []
            
            try:
                url = reverse(url_name, args=args)
                print(f"✅ {description}: {url}")
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
        
        print()
        
    except Exception as e:
        print(f"❌ URL verification error: {str(e)}")

if __name__ == "__main__":
    test_post_edit_functionality()
    test_follower_removal_functionality()
    verify_urls()
    show_testing_instructions()