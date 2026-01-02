#!/usr/bin/env python3
"""
Test script for message attachment functionality
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
from core.models import Owner, Message

def test_message_attachments():
    """Test message attachment functionality"""
    
    print("=" * 60)
    print("TESTING MESSAGE ATTACHMENT FUNCTIONALITY")
    print("=" * 60)
    
    # Get all users
    users = User.objects.all()
    
    if users.count() < 2:
        print("❌ Need at least 2 users to test messaging")
        return
    
    print(f"📊 Found {users.count()} users in database")
    print()
    
    # Check existing messages with attachments
    messages_with_attachments = Message.objects.exclude(attachment='').exclude(attachment__isnull=True)
    messages_without_attachments = Message.objects.filter(attachment='').count() + Message.objects.filter(attachment__isnull=True).count()
    
    print(f"📧 Messages with attachments: {messages_with_attachments.count()}")
    print(f"📝 Messages without attachments: {messages_without_attachments}")
    print()
    
    if messages_with_attachments.exists():
        print("📎 Messages with attachments:")
        print("-" * 40)
        for msg in messages_with_attachments:
            print(f"   From: {msg.sender.user.username}")
            print(f"   To: {msg.receiver.user.username}")
            print(f"   Content: {msg.content[:50]}..." if msg.content else "   Content: (attachment only)")
            print(f"   Attachment: {msg.attachment.name}")
            print(f"   File size: {msg.attachment.size} bytes")
            print()
    
    # Test message validation
    print("🧪 Testing message validation:")
    print("-" * 35)
    
    user1 = users[0].owner
    user2 = users[1].owner
    
    # Test 1: Message with content only
    try:
        test_msg = Message(sender=user1, receiver=user2, content="Test message")
        test_msg.clean()
        print("✅ Content-only message validation: PASSED")
    except Exception as e:
        print(f"❌ Content-only message validation: FAILED - {e}")
    
    # Test 2: Message with empty content and no attachment
    try:
        test_msg = Message(sender=user1, receiver=user2, content="")
        test_msg.clean()
        print("❌ Empty message validation: FAILED (should have been rejected)")
    except Exception as e:
        print("✅ Empty message validation: PASSED (correctly rejected)")
    
    # Test 3: Message with empty content but with attachment (simulated)
    try:
        test_msg = Message(sender=user1, receiver=user2, content="")
        test_msg.attachment = "test_file.pdf"  # Simulate attachment
        test_msg.clean()
        print("✅ Attachment-only message validation: PASSED")
    except Exception as e:
        print(f"❌ Attachment-only message validation: FAILED - {e}")
    
    print()
    print("=" * 60)
    print("WEB INTERFACE TESTING")
    print("=" * 60)
    
    print("🌐 To test the attachment feature in browser:")
    print("1. Visit http://127.0.0.1:8000/messages/")
    print("2. Start a conversation with any user")
    print("3. Look for the paperclip icon (📎) next to the message input")
    print("4. Click the paperclip to attach a file")
    print("5. Supported file types:")
    print("   • Documents: PDF, DOC, DOCX, TXT")
    print("   • Images: JPG, JPEG, PNG, GIF")
    print("   • Media: MP4, MP3")
    print("   • Archives: ZIP, RAR")
    print("6. File size limit: 10MB")
    print("7. You can send:")
    print("   • Message with text only")
    print("   • Message with attachment only")
    print("   • Message with both text and attachment")
    print()
    print("✨ Features to test:")
    print("   📎 File attachment with preview")
    print("   🗑️  Remove attachment before sending")
    print("   📁 Download attachments from received messages")
    print("   👁️  File type icons in messages")
    print("   📏 File size display")

def check_media_settings():
    """Check Django media settings for file uploads"""
    
    print("\n" + "=" * 60)
    print("CHECKING MEDIA SETTINGS")
    print("=" * 60)
    
    from django.conf import settings
    
    try:
        print(f"📁 MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
        print(f"📂 MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
        
        # Check if media directory exists
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            print(f"✅ Media directory exists: {media_root}")
            
            # Check message_attachments folder
            attachments_dir = os.path.join(media_root, 'message_attachments')
            if os.path.exists(attachments_dir):
                print(f"✅ Attachments directory exists: {attachments_dir}")
                files = os.listdir(attachments_dir)
                print(f"📎 Existing attachments: {len(files)} files")
            else:
                print(f"ℹ️  Attachments directory will be created when first file is uploaded")
        else:
            print("❌ Media directory not found")
            
    except Exception as e:
        print(f"❌ Error checking media settings: {e}")

if __name__ == "__main__":
    test_message_attachments()
    check_media_settings()