from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.user.username
    


class Post(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    tags = models.ForeignKey(Owner, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.owner.user.username} at {self.created_at}"



class PostLike(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('laugh', 'Laugh'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'post')

    def __str__(self):
        return f"{self.reaction_type.capitalize()} by {self.owner.user.username} on {self.post}"



class PostComment(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.owner.user.username} on {self.post}"

    @property
    def is_reply(self):
        return self.parent_comment is not None

    @property
    def replies_count(self):
        return self.replies.count()


class UserFollow(models.Model):
    FOLLOW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
    ]
    
    follower = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='followers')
    status = models.CharField(max_length=10, choices=FOLLOW_STATUS_CHOICES, default='accepted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.user.username} follows {self.following.user.username} ({self.status})"

    @property
    def is_accepted(self):
        return self.status == 'accepted'


class Notification(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    related_post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.owner.user.username}"
    
    

class Message(models.Model):
    sender = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='message_attachments/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.sender.user.username} to {self.receiver.user.username} at {self.created_at}"

    def clean(self):
        """Model validation"""
        # Allow empty content if there's an attachment
        if not self.content and not self.attachment:
            raise ValidationError("Message must have either content or an attachment")
        
        if self.content:
            self.content = self.content.strip()
            if not self.content and not self.attachment:
                raise ValidationError("Message content cannot be empty unless there's an attachment")
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
        
    def mark_as_read(self):
        """Mark message as read and set read timestamp"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
        
    @classmethod
    def start_chat(cls, sender, receiver, initial_message):
        
        if not initial_message.strip():
            raise ValueError("Message content cannot be empty")
            
        message = cls(
            sender=sender,
            receiver=receiver,
            content=initial_message
        )
        message.save()
        
        # Create a notification for the receiver
        Notification.objects.create(
            owner=receiver,
            content=f"New message from {sender.user.username}",
            is_read=False
        )
        
        return message