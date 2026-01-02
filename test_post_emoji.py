#!/usr/bin/env python3
"""
Test script to verify JavaScript functionality for post creation
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
from core.models import Owner, Post

def test_post_creation():
    """Test post creation functionality"""
    
    print("=" * 60)
    print("TESTING POST CREATION WITH EMOJI FUNCTIONALITY")
    print("=" * 60)
    
    # Get a test user
    try:
        test_user = User.objects.first()
        if not test_user:
            print("❌ No users found in database")
            return
            
        print(f"🔍 Testing with user: {test_user.username}")
        print()
        
        # Create some test posts with emojis
        test_posts = [
            "😀 Just had an amazing day at the beach! The weather was perfect and I got some great photos.",
            "🤔 Thinking about starting a new project. Any suggestions for a beginner-friendly programming language?",
            "🥳 Celebrating my promotion today! Hard work really pays off!",
            "😍 Love this new coffee shop downtown. Their latte art is incredible!",
            "Just a regular post without any emoji at the beginning."
        ]
        
        owner = test_user.owner
        
        for i, content in enumerate(test_posts, 1):
            # Create test post
            post = Post.objects.create(
                owner=owner,
                content=content
            )
            
            print(f"✅ Created test post {i}:")
            print(f"   Content: {content[:60]}...")
            
            # Check if post starts with emoji
            emoji_regex = r'^[\U00001F600-\U00001F64F]|^[\U00001F300-\U00001F5FF]|^[\U00001F680-\U00001F6FF]|^[\U00001F1E0-\U00001F1FF]|^[\U00002600-\U000026FF]|^[\U00002700-\U000027BF]'
            import re
            if re.match(emoji_regex, content):
                print(f"   📊 Contains emoji: ✅")
            else:
                print(f"   📊 Contains emoji: ❌")
            print()
            
        print(f"📊 Total posts created: {len(test_posts)}")
        print(f"📊 Total posts in database: {Post.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        
    print()
    print("=" * 60)
    print("TESTING INSTRUCTIONS:")
    print("1. Open http://127.0.0.1:8000/create-post/ in your browser")
    print("2. Log in as any user")
    print("3. Test the following features:")
    print("   • Click 'Feeling' button to open emoji picker")
    print("   • Select an emoji - it should appear at start of content")
    print("   • Click 'Remove' to clear the emoji")
    print("   • Upload an image and see preview")
    print("   • Submit form with/without content and image")
    print("4. Check character counter and auto-resize textarea")
    print("=" * 60)

def show_recent_posts():
    """Show recent posts to verify emoji functionality"""
    
    print("\n" + "=" * 60)
    print("RECENT POSTS WITH EMOJI DISPLAY")
    print("=" * 60)
    
    recent_posts = Post.objects.order_by('-created_at')[:10]
    
    for i, post in enumerate(recent_posts, 1):
        print(f"{i}. {post.owner.user.first_name} {post.owner.user.last_name}")
        print(f"   Content: {post.content[:80]}...")
        print(f"   Created: {post.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for emoji
        emoji_regex = r'^[\U00001F600-\U00001F64F]|^[\U00001F300-\U00001F5FF]|^[\U00001F680-\U00001F6FF]|^[\U00001F1E0-\U00001F1FF]|^[\U00002600-\U000026FF]|^[\U00002700-\U000027BF]'
        import re
        if re.match(emoji_regex, post.content):
            print(f"   📊 Has emoji: ✅")
        else:
            print(f"   📊 Has emoji: ❌")
        print()

if __name__ == "__main__":
    test_post_creation()
    show_recent_posts()