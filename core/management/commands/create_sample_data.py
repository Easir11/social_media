from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from core.models import Owner, Post, Message, UserFollow, Notification, PostComment, PostLike

class Command(BaseCommand):
    help = 'Create sample data for Barta 2.0 social media platform'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting sample data creation for Barta 2.0...")
        self.stdout.write("=" * 50)
        
        # Clear existing sample data
        self.stdout.write("Clearing existing sample data...")
        Owner.objects.filter(user__username__in=[
            'alice_johnson', 'bob_smith', 'carol_davis', 'david_wilson', 'emma_brown',
            'frank_miller', 'grace_taylor', 'henry_anderson', 'ivy_thomas', 'jack_white'
        ]).delete()
        
        # Create sample data
        users = self.create_sample_users()
        posts = self.create_sample_posts(users)
        self.create_social_connections(users)
        
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS("✅ Sample data creation completed!"))
        self.stdout.write(f"📊 Created {len(users)} users")
        self.stdout.write(f"📝 Created {len(posts)} posts")
        self.stdout.write(f"👥 Created {UserFollow.objects.count()} follow relationships")
        self.stdout.write(f"❤️ Created {PostLike.objects.count()} post likes")
        self.stdout.write(f"💬 Created {PostComment.objects.count()} comments")
        self.stdout.write(f"📩 Created {Message.objects.count()} messages")
        self.stdout.write(f"🔔 Created {Notification.objects.count()} notifications")
        self.stdout.write("\n🎉 Your Barta 2.0 platform is ready for testing!")
        self.stdout.write("\nTest accounts (all use password: password123):")
        for user in users:
            self.stdout.write(f"  - {user.user.username} ({user.user.first_name} {user.user.last_name})")

    def create_sample_users(self):
        """Create sample users with profiles"""
        self.stdout.write("Creating sample users...")
        
        users_data = [
            {'username': 'alice_johnson', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'bob_smith', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
            {'username': 'carol_davis', 'email': 'carol@example.com', 'first_name': 'Carol', 'last_name': 'Davis'},
            {'username': 'david_wilson', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Wilson'},
            {'username': 'emma_brown', 'email': 'emma@example.com', 'first_name': 'Emma', 'last_name': 'Brown'},
            {'username': 'frank_miller', 'email': 'frank@example.com', 'first_name': 'Frank', 'last_name': 'Miller'},
            {'username': 'grace_taylor', 'email': 'grace@example.com', 'first_name': 'Grace', 'last_name': 'Taylor'},
            {'username': 'henry_anderson', 'email': 'henry@example.com', 'first_name': 'Henry', 'last_name': 'Anderson'},
            {'username': 'ivy_thomas', 'email': 'ivy@example.com', 'first_name': 'Ivy', 'last_name': 'Thomas'},
            {'username': 'jack_white', 'email': 'jack@example.com', 'first_name': 'Jack', 'last_name': 'White'},
        ]
        
        bios = [
            "Passionate about technology and innovation 🚀",
            "Love traveling and discovering new cultures 🌍",
            "Coffee enthusiast and book lover ☕📚",
            "Fitness coach helping people achieve their goals 💪",
            "Digital artist creating beautiful experiences 🎨",
            "Photographer capturing life's moments 📷",
            "Chef sharing delicious recipes 👨‍🍳",
            "Teacher inspiring the next generation 📝",
            "Entrepreneur building the future 💼",
            "Music lover and part-time DJ 🎵"
        ]
        
        locations = [
            "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
            "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA"
        ]
        
        created_users = []
        
        for i, user_data in enumerate(users_data):
            # Create or get Django User
            user, created_user = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            # Ensure the sample password is set/updated
            user.set_password('password123')
            user.save()

            # Create or get Owner profile
            owner, created_owner = Owner.objects.get_or_create(
                user=user,
                defaults={
                    'bio': bios[i],
                    'location': locations[i],
                    'website': f"https://{user_data['username']}.com"
                }
            )
            if not created_owner:
                # Update basic profile fields if Owner already exists
                owner.bio = bios[i]
                owner.location = locations[i]
                owner.website = f"https://{user_data['username']}.com"
                owner.save()
            
            created_users.append(owner)
            self.stdout.write(f"Created user: {user.username}")
        
        return created_users

    def create_sample_posts(self, users):
        """Create sample posts for users"""
        self.stdout.write("Creating sample posts...")
        
        post_contents = [
            "Just had an amazing day exploring the city! 🌆 #adventure #citylife",
            "Working on some exciting new projects. Can't wait to share them with you all! 💼✨",
            "Beautiful sunset today. Nature never fails to amaze me 🌅 #sunset #nature",
            "Coffee and coding - perfect combination for a productive morning ☕💻 #coding #productivity",
            "Weekend vibes are here! Time to relax and recharge 🎉 #weekend #relax",
            "Just finished reading an incredible book. Highly recommend! 📚 #reading #books",
            "Trying out a new recipe today. Wish me luck! 👨‍🍳 #cooking #foodie",
            "Morning workout done! Starting the day with positive energy 💪 #fitness #motivation",
            "Grateful for all the amazing people in my life 🙏 #gratitude #friends",
            "Learning something new every day keeps life interesting 🧠 #learning #growth",
            "Music has the power to change your entire mood 🎵 #music #inspiration",
            "Sometimes the best therapy is a long walk in nature 🚶‍♀️🌳 #nature #wellness",
            "Excited to announce my latest project! Details coming soon... 🚀 #announcement #project",
            "Pizza night with friends - simple pleasures are the best 🍕👥 #friends #pizza",
            "Reflecting on the week and feeling accomplished 📈 #reflection #progress"
        ]
        
        created_posts = []
        
        for i, user in enumerate(users):
            # Create 2-3 posts per user
            num_posts = random.randint(2, 3)
            user_posts = random.sample(post_contents, num_posts)
            
            for j, content in enumerate(user_posts):
                # Create posts with different timestamps
                post_date = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
                
                post = Post.objects.create(
                    owner=user,
                    content=content,
                    created_at=post_date
                )
                created_posts.append(post)
                self.stdout.write(f"Created post by {user.user.username}: {content[:50]}...")
        
        return created_posts

    def create_social_connections(self, users):
        """Create follows, likes, comments, and messages between users"""
        self.stdout.write("Creating social connections...")
        
        # Create follows
        self.stdout.write("Creating follow relationships...")
        for user in users:
            # Each user follows 3-5 random other users
            num_follows = random.randint(3, 5)
            other_users = [u for u in users if u != user]
            follows = random.sample(other_users, min(num_follows, len(other_users)))
            
            for followed_user in follows:
                UserFollow.objects.get_or_create(
                    follower=user,
                    following=followed_user
                )
                self.stdout.write(f"{user.user.username} follows {followed_user.user.username}")
        
        # Create likes on posts
        self.stdout.write("Creating post likes...")
        posts = Post.objects.all()
        for post in posts:
            # Each post gets 1-5 random likes
            num_likes = random.randint(1, 5)
            potential_likers = [u for u in users if u != post.owner]
            likers = random.sample(potential_likers, min(num_likes, len(potential_likers)))
            
            for liker in likers:
                PostLike.objects.get_or_create(
                    owner=liker,
                    post=post
                )
        
        # Create comments on posts
        self.stdout.write("Creating post comments...")
        comment_texts = [
            "Great post! 👍", "Love this! ❤️", "So inspiring!", "Thanks for sharing!",
            "Amazing! 🔥", "Couldn't agree more!", "This made my day 😊", "Absolutely beautiful!",
            "Well said! 💯", "This is exactly what I needed to hear today!"
        ]
        
        for post in posts:
            # Each post gets 1-3 random comments
            num_comments = random.randint(1, 3)
            potential_commenters = [u for u in users if u != post.owner]
            commenters = random.sample(potential_commenters, min(num_comments, len(potential_commenters)))
            
            for commenter in commenters:
                comment_text = random.choice(comment_texts)
                PostComment.objects.create(
                    owner=commenter,
                    post=post,
                    content=comment_text
                )
        
        # Create messages between users
        self.stdout.write("Creating messages...")
        message_contents = [
            "Hey! How are you doing?", "Thanks for the follow!", "Love your latest post!",
            "Want to grab coffee sometime?", "Hope you're having a great day!",
            "Your content is really inspiring!", "Thanks for connecting!"
        ]
        
        # Create 10-15 random messages
        for _ in range(15):
            sender = random.choice(users)
            potential_receivers = [u for u in users if u != sender]
            receiver = random.choice(potential_receivers)
            content = random.choice(message_contents)
            
            Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                created_at=timezone.now() - timedelta(days=random.randint(0, 7))
            )
        
        # Create notifications
        self.stdout.write("Creating notifications...")
        notification_types = ['follow', 'like', 'comment', 'message']
        
        for user in users:
            # Create 2-4 notifications for each user
            num_notifications = random.randint(2, 4)
            for _ in range(num_notifications):
                other_user = random.choice([u for u in users if u != user])
                notification_type = random.choice(notification_types)
                
                if notification_type == 'follow':
                    message = f"{other_user.user.username} started following you"
                elif notification_type == 'like':
                    message = f"{other_user.user.username} liked your post"
                elif notification_type == 'comment':
                    message = f"{other_user.user.username} commented on your post"
                else:  # message
                    message = f"{other_user.user.username} sent you a message"
                
                Notification.objects.create(
                    owner=user,
                    content=message,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 5))
                )