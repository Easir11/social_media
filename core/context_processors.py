"""
Context processors for the Barta social media application.
These functions provide common data to all templates.
"""

from django.contrib.auth.models import AnonymousUser
from .models import Message, Notification, Owner


def unread_counts(request):
    """
    Add unread message and notification counts to template context.
    """
    context = {
        'unread_message_count': 0,
        'unread_notification_count': 0,
    }
    
    # Only process for authenticated users
    if not request.user.is_authenticated:
        return context
    
    try:
        # Get the owner object for the current user
        owner = request.user.owner
        
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
        
        context.update({
            'unread_message_count': unread_messages,
            'unread_notification_count': unread_notifications,
        })
        
    except (Owner.DoesNotExist, AttributeError):
        # Handle case where user doesn't have an owner profile
        pass
    
    return context


def user_profile(request):
    """
    Add current user's profile information to template context.
    """
    context = {
        'current_user_owner': None,
    }
    
    if request.user.is_authenticated:
        try:
            context['current_user_owner'] = request.user.owner
        except (Owner.DoesNotExist, AttributeError):
            pass
    
    return context