import os
import django
import random
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Barta.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from core.models import Owner, Post, PostLike, PostComment, UserFollow, Notification, Message

def create_fake_data():
    print("🚀 Starting to create fake data...\n")
    
    # Clear existing data (optional)
    print("🗑️  Clearing existing data...")
    Message.objects.all().delete()
    Notification.objects.all().delete()
    PostComment.objects.all().delete()
    PostLike.objects.all().delete()
    Post.objects.all().delete()
    UserFollow.objects.all().delete()
    Owner.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    print("✅ Existing data cleared\n")
    
    # Create Users and Owners
    print("👥 Creating users and owners...")
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'bob_wilson', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Wilson'},
        {'username': 'alice_brown', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Brown'},
        {'username': 'charlie_davis', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Davis'},
    ]
    
    owners = []
    for user_data in users_data:
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password='testpass123'
        )
        
        owner = Owner.objects.create(
            user=user,
            bio=f"Hi, I'm {user_data['first_name']}! I love sharing my thoughts and connecting with people.",
            location=random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami']),
            website=f"https://{user_data['username']}.com",
            is_verified=random.choice([True, False]),
            is_private=random.choice([True, False, False])  # More public accounts
        )
        owners.append(owner)
        print(f"   ✓ Created user: {user.username}")
    
    print(f"✅ Created {len(owners)} users and owners\n")
    
    # Create Posts
    print("📝 Creating posts...")
    posts = []
    post_contents = [
        "Just had the best coffee ever! ☕",
        "Beautiful sunset today 🌅",
        "Working on my new project, feeling excited! 💻",
        "Love spending time with family ❤️",
        "Anyone else love pizza as much as I do? 🍕",
        "New blog post coming soon! Stay tuned 📱",
        "Hiking is the best therapy 🏔️",
        "Reading a great book right now 📚",
        "Fitness journey update: feeling stronger! 💪",
        "Travel is the only thing you buy that makes you richer ✈️",
        "Music makes everything better 🎵",
        "Grateful for today 🙏",
        "Code, coffee, repeat! 👨‍💻",
        "Weekend vibes are the best! 🎉",
        "Just finished an amazing meal 🍽️",
    ]
    
    for i, owner in enumerate(owners):
        # Each user creates 2-4 posts
        num_posts = random.randint(2, 4)
        for j in range(num_posts):
            content = random.choice(post_contents)
            post = Post.objects.create(
                owner=owner,
                title=f"Post {i * 10 + j + 1}",
                content=content,
                location=random.choice(['', 'Central Park', 'Beach', 'Coffee Shop', 'Home', '']),
                is_pinned=random.choice([True, False, False, False])  # Rarely pinned
            )
            posts.append(post)
    
    print(f"✅ Created {len(posts)} posts\n")
    
    # Create Post Likes
    print("❤️  Creating post likes...")
    likes_count = 0
    reactions = ['like', 'love', 'laugh', 'wow', 'sad', 'angry']
    
    for post in posts:
        # Each post gets 1-5 likes from different users
        num_likes = random.randint(1, min(5, len(owners)))
        likers = random.sample(owners, num_likes)
        
        for liker in likers:
            if liker != post.owner:  # Don't like own posts
                PostLike.objects.create(
                    owner=liker,
                    post=post,
                    reaction_type=random.choice(reactions)
                )
                likes_count += 1
    
    print(f"✅ Created {likes_count} post likes\n")
    
    # Create Comments
    print("💬 Creating comments...")
    comments = []
    comment_texts = [
        "Great post!",
        "I totally agree!",
        "Thanks for sharing!",
        "Love this!",
        "Awesome!",
        "Interesting perspective!",
        "This made my day!",
        "So true!",
        "Can't wait for more!",
        "Amazing content!",
    ]
    
    for post in posts:
        # Each post gets 1-3 comments
        num_comments = random.randint(1, 3)
        commenters = random.sample(owners, min(num_comments, len(owners)))
        
        for commenter in commenters:
            comment = PostComment.objects.create(
                owner=commenter,
                post=post,
                content=random.choice(comment_texts),
                is_edited=random.choice([True, False, False, False])
            )
            comments.append(comment)
    
    print(f"✅ Created {len(comments)} comments\n")
    
    # Create Comment Replies
    print("↩️  Creating comment replies...")
    replies_count = 0
    
    for comment in comments[:10]:  # Only add replies to first 10 comments
        if random.choice([True, False]):
            replier = random.choice([o for o in owners if o != comment.owner])
            PostComment.objects.create(
                owner=replier,
                post=comment.post,
                parent_comment=comment,
                content="Thanks for your comment!",
                is_edited=False
            )
            replies_count += 1
    
    print(f"✅ Created {replies_count} comment replies\n")
    
    # Create User Follows
    print("👫 Creating user follows...")
    follows_count = 0
    statuses = ['pending', 'accepted', 'accepted', 'accepted']  # Most accepted
    
    for owner in owners:
        # Each user follows 2-3 other users
        num_follows = random.randint(2, 3)
        to_follow = random.sample([o for o in owners if o != owner], num_follows)
        
        for following in to_follow:
            UserFollow.objects.create(
                follower=owner,
                following=following,
                status=random.choice(statuses)
            )
            follows_count += 1
    
    print(f"✅ Created {follows_count} user follows\n")
    
    # Create Notifications
    print("🔔 Creating notifications...")
    notification_types = ['like', 'comment', 'follow', 'mention', 'system']
    notification_contents = [
        "liked your post",
        "commented on your post",
        "started following you",
        "mentioned you in a comment",
        "Welcome to Barta 2.0!",
    ]
    
    notifications_count = 0
    for owner in owners:
        # Each user gets 3-5 notifications
        num_notifications = random.randint(3, 5)
        
        for _ in range(num_notifications):
            Notification.objects.create(
                owner=owner,
                title="New Activity",
                content=random.choice(notification_contents),
                is_read=random.choice([True, False, False]),
                related_post=random.choice(posts) if random.choice([True, False]) else None
            )
            notifications_count += 1
    
    print(f"✅ Created {notifications_count} notifications\n")
    
    # Create Messages
    print("💌 Creating messages...")
    message_texts = [
        "Hey! How are you?",
        "Thanks for connecting!",
        "I loved your recent post!",
        "Let's catch up soon!",
        "Great to see your updates!",
        "Hope you're having a great day!",
        "Your content is amazing!",
        "Let me know if you want to collaborate!",
    ]
    
    messages_count = 0
    for i in range(len(owners)):
        # Create some message exchanges
        sender = owners[i]
        receiver = owners[(i + 1) % len(owners)]
        
        # Send 2-3 messages
        num_messages = random.randint(2, 3)
        for j in range(num_messages):
            message = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=random.choice(message_texts),
                is_read=random.choice([True, False]),
                created_at=timezone.now() - timedelta(hours=random.randint(1, 48))
            )
            
            if message.is_read:
                message.read_at = message.created_at + timedelta(minutes=random.randint(5, 120))
                message.save()
            
            messages_count += 1
    
    print(f"✅ Created {messages_count} messages\n")
    
    # Display Statistics
    print("=" * 60)
    print("📊 DATA CREATION SUMMARY")
    print("=" * 60)
    print(f"👥 Users/Owners:     {Owner.objects.count()}")
    print(f"📝 Posts:            {Post.objects.count()}")
    print(f"❤️  Post Likes:       {PostLike.objects.count()}")
    print(f"💬 Comments:         {PostComment.objects.count()}")
    print(f"↩️  Replies:          {PostComment.objects.filter(parent_comment__isnull=False).count()}")
    print(f"👫 Follows:          {UserFollow.objects.count()}")
    print(f"🔔 Notifications:    {Notification.objects.count()}")
    print(f"💌 Messages:         {Message.objects.count()}")
    print("=" * 60)
    
    # Test some model methods
    print("\n🧪 TESTING MODEL METHODS")
    print("=" * 60)
    
    # Test Post properties
    first_post = Post.objects.first()
    if first_post:
        print(f"\n📝 Post by {first_post.owner.user.username}:")
        print(f"   Content: {first_post.content[:40]}...")
        print(f"   Location: {first_post.location or 'Not specified'}")
        print(f"   Is Pinned: {first_post.is_pinned}")
    
    # Test PostComment properties
    first_comment = PostComment.objects.first()
    if first_comment:
        print(f"\n💬 Comment by {first_comment.owner.user.username}:")
        print(f"   Content: {first_comment.content}")
        print(f"   Is Reply: {first_comment.is_reply}")
        print(f"   Replies Count: {first_comment.replies_count}")
    
    # Test UserFollow properties
    first_follow = UserFollow.objects.first()
    if first_follow:
        print(f"\n👫 Follow: {first_follow.follower.user.username} → {first_follow.following.user.username}")
        print(f"   Status: {first_follow.status}")
        print(f"   Is Accepted: {first_follow.is_accepted}")
    
    # Test Message method
    unread_message = Message.objects.filter(is_read=False).first()
    if unread_message:
        print(f"\n💌 Unread Message:")
        print(f"   From: {unread_message.sender.user.username}")
        print(f"   To: {unread_message.receiver.user.username}")
        print(f"   Content: {unread_message.content}")
        print(f"   Marking as read...")
        unread_message.mark_as_read()
        print(f"   Is Read: {unread_message.is_read}")
        print(f"   Read At: {unread_message.read_at}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    create_fake_data()
