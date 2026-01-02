#!/usr/bin/env python3
"""
Test script for "People You May Know" section to verify only unfollowed users are shown
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
from core.models import Owner, UserFollow

def test_people_you_may_know():
    """Test the People You May Know logic"""
    
    print("=" * 60)
    print("TESTING 'PEOPLE YOU MAY KNOW' SECTION")
    print("=" * 60)
    
    # Get all users
    users = User.objects.all()
    
    if users.count() < 3:
        print("❌ Need at least 3 users to test properly")
        return
    
    print(f"📊 Found {users.count()} users in database")
    print()
    
    # Test for each user
    for user in users[:3]:  # Test first 3 users
        try:
            current_user_owner = user.owner
            
            print(f"👤 Testing for: {user.first_name} {user.last_name} (@{user.username})")
            print("-" * 50)
            
            # Get users that current user is following
            followed_user_ids = UserFollow.objects.filter(
                follower=current_user_owner,
                status='accepted'
            ).values_list('following_id', flat=True)
            
            following_usernames = []
            if followed_user_ids:
                following_users = Owner.objects.filter(id__in=followed_user_ids)
                following_usernames = [owner.user.username for owner in following_users]
            
            print(f"   👥 Currently following ({len(following_usernames)}): {', '.join(following_usernames) if following_usernames else 'None'}")
            
            # Get suggested users (same logic as home view)
            suggested_users = Owner.objects.exclude(
                id__in=followed_user_ids
            ).exclude(
                id=current_user_owner.id
            )[:5]
            
            suggested_usernames = [owner.user.username for owner in suggested_users]
            print(f"   💡 Suggested users ({len(suggested_usernames)}): {', '.join(suggested_usernames) if suggested_usernames else 'None'}")
            
            # Verify no overlap
            overlap = set(following_usernames).intersection(set(suggested_usernames))
            if overlap:
                print(f"   ❌ ERROR: Suggested users include already followed users: {', '.join(overlap)}")
            else:
                print(f"   ✅ GOOD: No overlap between followed and suggested users")
            
            print()
            
        except Owner.DoesNotExist:
            print(f"❌ {user.username} has no owner profile")
            print()
    
    print("=" * 60)
    print("OVERALL FOLLOW RELATIONSHIPS")
    print("=" * 60)
    
    # Show all follow relationships
    follows = UserFollow.objects.filter(status='accepted').select_related('follower__user', 'following__user')
    
    if follows.exists():
        print("Current follow relationships:")
        for follow in follows:
            print(f"   {follow.follower.user.username} → {follow.following.user.username}")
    else:
        print("No follow relationships found")
    
    print()
    print("🌐 To test in browser:")
    print("1. Visit http://127.0.0.1:8000/")
    print("2. Log in as any user")
    print("3. Check 'People You May Know' section")
    print("4. Verify only unfollowed users are shown")
    print("5. Follow someone and refresh to see them disappear from suggestions")

def create_test_follows():
    """Create some test follow relationships"""
    
    print("\n" + "=" * 60)
    print("CREATING TEST FOLLOW RELATIONSHIPS")
    print("=" * 60)
    
    users = User.objects.all()
    
    if users.count() < 3:
        print("❌ Need at least 3 users to create test relationships")
        return
    
    user1 = users[0]  # Easir
    user2 = users[1]  # Alice
    user3 = users[2]  # Bob
    
    try:
        owner1 = user1.owner
        owner2 = user2.owner
        owner3 = user3.owner
        
        # Create follow relationships
        follow1, created1 = UserFollow.objects.get_or_create(
            follower=owner1,
            following=owner2,
            defaults={'status': 'accepted'}
        )
        
        follow2, created2 = UserFollow.objects.get_or_create(
            follower=owner1,
            following=owner3,
            defaults={'status': 'accepted'}
        )
        
        if created1:
            print(f"✅ Created: {user1.username} follows {user2.username}")
        else:
            print(f"ℹ️  Already exists: {user1.username} follows {user2.username}")
            
        if created2:
            print(f"✅ Created: {user1.username} follows {user3.username}")
        else:
            print(f"ℹ️  Already exists: {user1.username} follows {user3.username}")
        
        print()
        print(f"🔍 {user1.username} should now see fewer suggestions in 'People You May Know'")
        
    except Owner.DoesNotExist as e:
        print(f"❌ Error creating test relationships: {e}")

if __name__ == "__main__":
    test_people_you_may_know()
    
    # Ask if user wants to create test follows
    create_test = input("\n🔧 Create test follow relationships? (y/n): ").lower().strip()
    if create_test == 'y':
        create_test_follows()
        print("\n🔄 Re-running test with new relationships...")
        test_people_you_may_know()