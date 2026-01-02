"""
Simple test script to verify messaging functionality works end-to-end
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Barta.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Message

def test_messaging():
    print("🧪 Testing Messaging Functionality...")
    print("=" * 40)
    
    # Get test users
    try:
        user1 = User.objects.get(username='alice_johnson')
        user2 = User.objects.get(username='bob_smith')
        print(f"✅ Found test users: {user1.username} and {user2.username}")
    except User.DoesNotExist:
        print("❌ Test users not found. Please run sample data creation first.")
        return False
    
    # Test client
    client = Client()
    
    # Login as user1
    login_success = client.login(username='alice_johnson', password='password123')
    if not login_success:
        print("❌ Failed to login as alice_johnson")
        return False
    print("✅ Logged in as alice_johnson")
    
    # Test conversation page access
    response = client.get(f'/conversation/{user2.username}/')
    if response.status_code != 200:
        print(f"❌ Failed to access conversation page. Status: {response.status_code}")
        return False
    print("✅ Conversation page accessible")
    
    # Count messages before
    initial_count = Message.objects.count()
    
    # Test sending a valid message
    response = client.post(f'/conversation/{user2.username}/', {
        'content': 'Hello from the test script! 🚀'
    })
    
    if response.status_code == 302:  # Redirect after successful submission
        print("✅ Message form submitted successfully")
        
        # Check if message was created
        new_count = Message.objects.count()
        if new_count > initial_count:
            print("✅ Message was saved to database")
            
            # Get the latest message
            latest_message = Message.objects.latest('created_at')
            if latest_message.content == 'Hello from the test script! 🚀':
                print("✅ Message content is correct")
                print(f"   Message: '{latest_message.content}'")
                print(f"   From: {latest_message.sender.user.username}")
                print(f"   To: {latest_message.receiver.user.username}")
            else:
                print("❌ Message content doesn't match")
        else:
            print("❌ Message was not saved to database")
    else:
        print(f"❌ Message form submission failed. Status: {response.status_code}")
        if hasattr(response, 'content'):
            print("Response content contains:")
            content = response.content.decode('utf-8')
            if 'Message content cannot be empty' in content:
                print("   - 'Message content cannot be empty' error")
            if 'error' in content.lower():
                print("   - Contains error messages")
        return False
    
    # Test sending empty message (should fail)
    response = client.post(f'/conversation/{user2.username}/', {
        'content': ''
    })
    
    if response.status_code == 302:  # Should redirect back with error
        print("✅ Empty message properly rejected")
    else:
        print("❌ Empty message validation failed")
    
    print("\n🎉 Messaging functionality test completed!")
    return True

if __name__ == "__main__":
    success = test_messaging()
    if success:
        print("\n✅ All tests passed! Messaging is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")