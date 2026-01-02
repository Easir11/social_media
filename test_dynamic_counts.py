#!/usr/bin/env python3
"""
Test script for dynamic message and notification counts
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
from core.models import Owner, Message, Notification

def test_unread_counts():
    """Test unread message and notification counts"""
    
    print("=" * 60)
    print("TESTING DYNAMIC MESSAGE & NOTIFICATION COUNTS")
    print("=" * 60)
    
    # Get all users
    users = User.objects.all()
    
    if users.count() < 2:
        print("❌ Need at least 2 users to test messaging")
        return
    
    print(f"📊 Found {users.count()} users in database")
    print()
    
    # Test for each user
    for user in users[:5]:  # Test first 5 users
        try:
            owner = user.owner
            
            # Count unread messages
            unread_messages = Message.objects.filter(
                receiver=owner,
                is_read=False
            ).count()
            
            # Count unread notifications
            unread_notifications = Notification.objects.filter(
                owner=owner,
                is_read=False
            ).count()
            
            # Count total messages and notifications
            total_messages = Message.objects.filter(receiver=owner).count()
            total_notifications = Notification.objects.filter(owner=owner).count()
            
            print(f"👤 {user.first_name} {user.last_name} (@{user.username})")
            print(f"   📧 Messages: {unread_messages} unread / {total_messages} total")
            print(f"   🔔 Notifications: {unread_notifications} unread / {total_notifications} total")
            
            # Badge display logic
            if unread_messages > 0:
                print(f"   🔴 Message badge will show: {unread_messages}")
            else:
                print(f"   ⚪ No message badge (no unread messages)")
                
            if unread_notifications > 0:
                print(f"   🔵 Notification badge will show: {unread_notifications}")
            else:
                print(f"   ⚪ No notification badge (no unread notifications)")
                
            print()
            
        except Owner.DoesNotExist:
            print(f"❌ {user.username} has no owner profile")
            print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Overall statistics
    total_unread_messages = Message.objects.filter(is_read=False).count()
    total_unread_notifications = Notification.objects.filter(is_read=False).count()
    
    print(f"📊 System-wide unread counts:")
    print(f"   📧 Total unread messages: {total_unread_messages}")
    print(f"   🔔 Total unread notifications: {total_unread_notifications}")
    print()
    
    if total_unread_messages > 0 or total_unread_notifications > 0:
        print("✅ Dynamic badges should be visible for users with unread items")
    else:
        print("ℹ️  No unread items - badges will be hidden")
    
    print()
    print("🌐 To test in browser:")
    print("1. Visit http://127.0.0.1:8000/")
    print("2. Log in as any user")
    print("3. Check the header for message/notification badges")
    print("4. Send messages or create posts to generate notifications")
    print("5. Observe badges update dynamically")

def create_test_unread_data():
    """Create some unread messages and notifications for testing"""
    
    print("\n" + "=" * 60)
    print("CREATING TEST UNREAD DATA")
    print("=" * 60)
    
    users = User.objects.all()
    
    if users.count() < 2:
        print("❌ Need at least 2 users to create test data")
        return
    
    user1 = users[0]
    user2 = users[1]
    
    try:
        owner1 = user1.owner
        owner2 = user2.owner
        
        # Create unread message
        message = Message.objects.create(
            sender=owner1,
            receiver=owner2,
            content="This is a test unread message for dynamic badge testing! 📧",
            is_read=False
        )
        
        # Create unread notification
        notification = Notification.objects.create(
            owner=owner2,
            content=f"{user1.first_name} {user1.last_name} sent you a test message",
            is_read=False
        )
        
        print(f"✅ Created test unread message: {owner1.user.username} → {owner2.user.username}")
        print(f"✅ Created test unread notification for: {owner2.user.username}")
        print()
        print(f"🔍 {owner2.user.username} should now see:")
        print(f"   📧 Message badge: 1")
        print(f"   🔔 Notification badge: 1")
        
    except Owner.DoesNotExist as e:
        print(f"❌ Error creating test data: {e}")

if __name__ == "__main__":
    test_unread_counts()
    
    # Ask if user wants to create test data
    create_test = input("\n🔧 Create test unread data? (y/n): ").lower().strip()
    if create_test == 'y':
        create_test_unread_data()
        print("\n🔄 Re-running count test with new data...")
        test_unread_counts()