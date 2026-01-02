from random import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.utils import timezone
from .models import Owner, Post, UserFollow, PostLike, PostComment, Notification, Message

@login_required
def home(request):
    # Only show posts from people the user follows (accepted) + their own posts
    if request.user.is_authenticated:
        try:
            current_user_owner = request.user.owner
            followed_user_ids = list(
                UserFollow.objects.filter(
                    follower=current_user_owner,
                    status='accepted'
                ).values_list('following_id', flat=True)
            )

            # include own posts in the feed
            followed_user_ids.append(current_user_owner.id)

            posts = Post.objects.filter(
                owner_id__in=followed_user_ids
            ).select_related('owner__user').order_by('-created_at')[:10]

            # Get suggested users (users not followed by current user)
            suggested_users = Owner.objects.exclude(
                id__in=followed_user_ids
            )[:5]
        except Owner.DoesNotExist:
            current_user_owner = None
            suggested_users = []
            posts = []
    else:
        posts = []
        current_user_owner = None
        suggested_users = []
    
    context = {
        'posts': posts,
        'current_user_owner': current_user_owner,
        'suggested_users': suggested_users,
    }
    return render(request, 'core/home.html', context)

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        bio = request.POST.get('bio', '')
        profile_picture = request.FILES.get('profile_picture', None)
        
        error = None
        if not (username and email and password1 and password2):
            error = "All fields are required"
        elif password1 != password2:
            error = "Passwords don't match"
        elif len(password1) < 8:
            error = "Password must be at least 8 characters long"
        elif User.objects.filter(username=username).exists():
            error = "Username already exists"
        elif User.objects.filter(email=email).exists():
            error = "Email already exists"
        
        if error:
            messages.error(request, error)
            return render(request, 'core/signup.html')
            
        # Create user and owner
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        owner = Owner.objects.create(user=user, bio=bio, profile_picture=profile_picture)
        
        login(request, user)
        messages.success(request, 'Account created successfully! Welcome to Barta 2.0!')
        return redirect('home')
    
    return render(request, 'core/signup.html')

def signin_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not (username and password):
            messages.error(request, 'Both username and password are required')
            return render(request, 'core/signin.html')
            
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'core/signin.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('signin')



@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
        
    owner = get_object_or_404(Owner, user=user)
    posts = Post.objects.filter(owner=owner).order_by('-created_at')
    
    # Count followers and following with accepted status
    followers = UserFollow.objects.filter(following=owner, status='accepted').count()
    following = UserFollow.objects.filter(follower=owner, status='accepted').count()
    
    # Check if current user is following this profile
    is_following = False
    follow_status = None
    if user != request.user and hasattr(request.user, 'owner'):
        try:
            follow_obj = UserFollow.objects.get(
                follower=request.user.owner,
                following=owner
            )
            is_following = follow_obj.status == 'accepted'
            follow_status = follow_obj.status
        except UserFollow.DoesNotExist:
            is_following = False
            follow_status = None
    
    context = {
        'profile_user': user,
        'owner': owner,
        'posts': posts,
        'post_count': posts.count(),
        'followers_count': followers,
        'following_count': following,
        'is_own_profile': user == request.user,
        'is_following': is_following,
        'follow_status': follow_status
    }
    
    return render(request, 'core/profile.html', context)

@login_required
def profile_edit(request):
    owner = get_object_or_404(Owner, user=request.user)
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        website = request.POST.get('website', '')
        phone_number = request.POST.get('phone_number', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        is_private = request.POST.get('is_private') == 'on'
        
        # Handle file uploads
        profile_picture = request.FILES.get('profile_picture', None)
        cover_photo = request.FILES.get('cover_photo', None)
        
        # Update user information
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        # Update owner information
        owner.bio = bio
        owner.location = location
        owner.website = website
        owner.phone_number = phone_number
        owner.is_private = is_private
        
        # Handle date of birth
        if date_of_birth:
            try:
                from datetime import datetime
                owner.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
                return render(request, 'core/profile_edit.html', {'owner': owner})
        
        # Handle file uploads
        if profile_picture:
            owner.profile_picture = profile_picture
        if cover_photo:
            owner.cover_photo = cover_photo
            
        owner.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
        
    context = {
        'owner': owner
    }
    
    return render(request, 'core/profile_edit.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content')
        image = request.FILES.get('image', None)
        location = request.POST.get('location', '')
        
        if content and content.strip():
            try:
                owner = request.user.owner
                post = Post.objects.create(
                    owner=owner,
                    title=title.strip() if title else None,
                    content=content.strip(),
                    image=image,
                    location=location.strip() if location else None
                )
                messages.success(request, 'Post created successfully!')
                return redirect('home')
            except Owner.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact support.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error creating post: {str(e)}')
        else:
            messages.error(request, 'Post content cannot be empty')
            
    return render(request, 'core/create_post.html')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    try:
        owner = request.user.owner
        like, created = PostLike.objects.get_or_create(owner=owner, post=post)
        
        if not created:
            # User already liked the post, so unlike it
            like.delete()
            liked = False
        else:
            liked = True
            
        # Create notification for post owner if someone else liked their post
        if liked and post.owner != owner:
            Notification.objects.create(
                owner=post.owner,
                content=f"{owner.user.username} liked your post",
                related_post=post,
                is_read=False
            )
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home')
    
    # Get the referring page to redirect back to it
    referer = request.META.get('HTTP_REFERER')
    if referer and 'post_detail' in referer:
        return redirect('post_detail', post_id=post_id)
    else:
        return redirect('home')




@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Get all comments for this post, including replies
    all_comments = PostComment.objects.filter(
        post=post
    ).select_related('owner__user').prefetch_related('replies').order_by('created_at')
    
    # Separate top-level comments and replies
    top_level_comments = all_comments.filter(parent_comment=None).order_by('-created_at')
    
    # Create a dictionary to organize comments with their replies
    comments_with_replies = []
    for comment in top_level_comments:
        comment_data = {
            'comment': comment,
            'replies': comment.replies.all().order_by('created_at')
        }
        comments_with_replies.append(comment_data)
    
    try:
        owner = request.user.owner
        is_liked = PostLike.objects.filter(owner=owner, post=post).exists()
        current_user_owner = owner
    except (Owner.DoesNotExist, AttributeError):
        is_liked = False
        current_user_owner = None
    
    context = {
        'post': post,
        'comments_with_replies': comments_with_replies,
        'total_comments_count': all_comments.count(),
        'is_liked': is_liked,
        'likes_count': post.likes.count(),
        'current_user_owner': current_user_owner,
    }
    
    return render(request, 'core/post_detail.html', context)

# Keep the random import at the top (it's already there)
# from random import random

# Fix the comment_post function - just complete the line with None for top-level comments
@login_required
def comment_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content and content.strip():
            try:
                owner = request.user.owner                
                               
                comment = PostComment.objects.create(
                    owner=owner,
                    post=post,
                    content=content.strip(),
                    parent_comment=None  # Always None for top-level comments
                )
                
                # Regular comment notification - notify post owner only
                if post.owner != owner:
                    Notification.objects.create(
                        owner=post.owner,
                        content=f"{owner.user.username} commented on your post",
                        related_post=post,
                        is_read=False
                    )
                
                messages.success(request, 'Comment added successfully!')
                    
            except Owner.DoesNotExist:
                messages.error(request, 'User profile not found.')
        else:
            messages.error(request, 'Comment content cannot be empty')
    
    return redirect('post_detail', post_id=post_id)

@login_required
def reply_comment(request, post_id, comment_id):
    """Handle replies to specific comments"""
    post = get_object_or_404(Post, id=post_id)
    parent_comment = get_object_or_404(PostComment, id=comment_id, post=post)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content and content.strip():
            try:
                owner = request.user.owner
                reply = PostComment.objects.create(
                    owner=owner,
                    post=post,
                    content=content.strip(),
                    parent_comment=parent_comment
                )
                
                # Create notifications
                if parent_comment.owner != owner:
                    Notification.objects.create(
                        owner=parent_comment.owner,
                        content=f"{owner.user.username} replied to your comment",
                        related_post=post,
                        is_read=False
                    )
                if post.owner != owner and post.owner != parent_comment.owner:
                    Notification.objects.create(
                        owner=post.owner,
                        content=f"{owner.user.username} replied to a comment on your post",
                        related_post=post,
                        is_read=False
                    )
                
                messages.success(request, 'Reply added successfully!')
            except Owner.DoesNotExist:
                messages.error(request, 'User profile not found.')
        else:
            messages.error(request, 'Reply content cannot be empty')
    
    return redirect('post_detail', post_id=post_id)


@login_required
def messages_view(request):
    """Redirect to inbox view for better user experience"""
    return redirect('inbox')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, owner=request.user.owner)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image', None)
        
        if content and content.strip():
            post.content = content.strip()
            if image:
                post.image = image
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', post_id=post.id)
        else:
            messages.error(request, 'Post content cannot be empty')
    
    context = {'post': post}
    return render(request, 'core/edit_post.html', context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, owner=request.user.owner)
    
    if request.method == 'POST':
        # Get the username for redirect
        username = post.owner.user.username
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        
        # Check if request came from profile page
        referer = request.META.get('HTTP_REFERER', '')
        if f'/profile/{username}/' in referer:
            return redirect('profile_user', username=username)
        else:
            return redirect('home')
    
    context = {'post': post}
    return render(request, 'core/delete_post.html', context)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    current_user = request.user
    
    # Don't allow users to follow themselves
    if user_to_follow == current_user:
        messages.error(request, "You cannot follow yourself.")
        return redirect('profile_user', username=username)
    
    try:
        following = get_object_or_404(Owner, user=user_to_follow)
        follower = get_object_or_404(Owner, user=current_user)
        
        follow, created = UserFollow.objects.get_or_create(
            follower=follower,
            following=following
        )
        
        if not created:
            # User is already following, so unfollow
            follow.delete()
            messages.success(request, f"You have unfollowed {user_to_follow.first_name} {user_to_follow.last_name}.")
        else:
            messages.success(request, f"You are now following {user_to_follow.first_name} {user_to_follow.last_name}.")
            
            # Create notification
            Notification.objects.create(
                owner=following,
                content=f"{current_user.username} started following you",
                is_read=False
            )
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
    
    return redirect('profile_user', username=username)

@login_required
def remove_follower(request, username):
    """Remove a follower from the current user's followers list"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('followers_list', username=request.user.username)
    
    follower_user = get_object_or_404(User, username=username)
    current_user = request.user
    
    # Don't allow users to remove themselves
    if follower_user == current_user:
        messages.error(request, "You cannot remove yourself.")
        return redirect('followers_list', username=current_user.username)
    
    try:
        current_user_owner = get_object_or_404(Owner, user=current_user)
        follower_owner = get_object_or_404(Owner, user=follower_user)
        
        # Find the follow relationship where follower_user follows current_user
        follow = UserFollow.objects.filter(
            follower=follower_owner,
            following=current_user_owner,
            status='accepted'
        ).first()
        
        if follow:
            follow.delete()
            messages.success(request, f"You have removed {follower_user.first_name} {follower_user.last_name} from your followers.")
            
            # Optional: Create notification for the removed follower
            Notification.objects.create(
                owner=follower_owner,
                content=f"{current_user.username} removed you from their followers",
                is_read=False
            )
        else:
            messages.error(request, f"{follower_user.first_name} {follower_user.last_name} is not following you.")
    
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
    
    return redirect('followers_list', username=current_user.username)

@login_required
def followers_list(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    try:
        owner = get_object_or_404(Owner, user=user)
        followers = UserFollow.objects.filter(following=owner).select_related('follower__user')
        
        context = {
            'profile_user': user,
            'owner': owner,
            'followers': followers,
            'is_own_profile': user == request.user,
            'followers_count': followers.count()
        }
        
        return render(request, 'core/followers.html', context)
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')

@login_required
def following_list(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    try:
        owner = get_object_or_404(Owner, user=user)
        following = UserFollow.objects.filter(follower=owner).select_related('following__user')
        
        context = {
            'profile_user': user,
            'owner': owner,
            'following': following,
            'is_own_profile': user == request.user,
            'following_count': following.count()
        }
        
        return render(request, 'core/following.html', context)
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')

@login_required
def inbox_view(request):
    """View to display user's message inbox with conversation list"""
    try:
        user_owner = request.user.owner
        
        # Get unique users who have conversations with the current user
        conversations = Message.objects.filter(
            sender=user_owner
        ).values_list('receiver_id', flat=True).distinct()
        
        received_conversations = Message.objects.filter(
            receiver=user_owner
        ).values_list('sender_id', flat=True).distinct()
        
        # Combine and remove duplicates
        all_conversation_ids = set(list(conversations) + list(received_conversations))
        
        # Get those users' profiles
        conversation_partners = Owner.objects.filter(id__in=all_conversation_ids).select_related('user')
        
        # For each conversation partner, get their most recent message
        partners_with_last_message = []
        for partner in conversation_partners:
            last_message = Message.objects.filter(
                (models.Q(sender=user_owner) & models.Q(receiver=partner)) | 
                (models.Q(sender=partner) & models.Q(receiver=user_owner))
            ).order_by('-created_at').first()
            
            unread_count = Message.objects.filter(
                sender=partner, 
                receiver=user_owner, 
                is_read=False
            ).count()
            
            partners_with_last_message.append({
                'partner': partner,
                'last_message': last_message,
                'unread_count': unread_count
            })
        
        # Sort by the most recent message
        partners_with_last_message.sort(
            key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(), 
            reverse=True
        )
        
        context = {
            'conversations': partners_with_last_message
        }
        
        return render(request, 'core/inbox.html', context)
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')


@login_required
def find_friend(request):
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        
        if not query:
            return render(request, 'core/find_friend.html', {'results': [], 'query': ''})
        
        try:
            current_user_owner = request.user.owner
            
            # Get all potential users (excluding current user and already followed)
            followed_ids = UserFollow.objects.filter(
                follower=current_user_owner
            ).values_list('following_id', flat=True)
            
            potential_users = Owner.objects.exclude(
                id__in=followed_ids
            ).exclude(
                id=current_user_owner.id
            ).select_related('user')
            
            # Fuzzy matching algorithm
            def calculate_fuzzy_score(person, query):
                """Calculate fuzzy matching score based on multiple criteria"""
                score = 0.0
                query_lower = query.lower()
                
                # Name matching (40% weight)
                full_name = f"{person.user.first_name} {person.user.last_name}".lower()
                username = person.user.username.lower()
                
                # Exact name match gets highest score
                if query_lower in full_name:
                    score += 0.4 * (len(query_lower) / len(full_name))
                
                # Username match
                if query_lower in username:
                    score += 0.3 * (len(query_lower) / len(username))
                
                # Fuzzy string matching for names
                def fuzzy_string_match(text, pattern):
                    """Simple fuzzy string matching algorithm"""
                    if not pattern or not text:
                        return 0.0
                    
                    # Character frequency matching
                    pattern_chars = set(pattern.lower())
                    text_chars = set(text.lower())
                    common_chars = len(pattern_chars.intersection(text_chars))
                    char_similarity = common_chars / max(len(pattern_chars), len(text_chars))
                    
                    # Subsequence matching
                    subseq_score = 0.0
                    pattern_idx = 0
                    for char in text.lower():
                        if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                            pattern_idx += 1
                    subseq_score = pattern_idx / len(pattern)
                    
                    # Levenshtein-like distance (simplified)
                    def edit_distance(s1, s2):
                        if len(s1) < len(s2):
                            return edit_distance(s2, s1)
                        if len(s2) == 0:
                            return len(s1)
                        
                        previous_row = list(range(len(s2) + 1))
                        for i, c1 in enumerate(s1):
                            current_row = [i + 1]
                            for j, c2 in enumerate(s2):
                                insertions = previous_row[j + 1] + 1
                                deletions = current_row[j] + 1
                                substitutions = previous_row[j] + (c1 != c2)
                                current_row.append(min(insertions, deletions, substitutions))
                            previous_row = current_row
                        
                        return previous_row[-1]
                    
                    edit_dist = edit_distance(text.lower(), pattern.lower())
                    max_len = max(len(text), len(pattern))
                    edit_similarity = 1 - (edit_dist / max_len) if max_len > 0 else 0
                    
                    # Combine all similarity measures
                    return (char_similarity * 0.3 + subseq_score * 0.4 + edit_similarity * 0.3)
                
                # Apply fuzzy matching to full name
                name_fuzzy = fuzzy_string_match(full_name, query_lower)
                score += 0.2 * name_fuzzy
                
                # Apply fuzzy matching to username
                username_fuzzy = fuzzy_string_match(username, query_lower)
                score += 0.1 * username_fuzzy
                
                # Location matching (10% weight)
                if person.location:
                    location_lower = person.location.lower()
                    if query_lower in location_lower:
                        score += 0.1 * (len(query_lower) / len(location_lower))
                
                # Bio matching (15% weight)
                if person.bio:
                    bio_lower = person.bio.lower()
                    if query_lower in bio_lower:
                        score += 0.15 * (len(query_lower) / len(bio_lower))
                    
                    # Fuzzy bio matching
                    bio_fuzzy = fuzzy_string_match(bio_lower, query_lower)
                    score += 0.05 * bio_fuzzy
                
                # Social connection boost (15% weight)
                # Users with more followers/following get slight boost
                follower_count = UserFollow.objects.filter(following=person).count()
                following_count = UserFollow.objects.filter(follower=person).count()
                social_score = min((follower_count + following_count) / 100, 1.0)  # Cap at 1.0
                score += 0.15 * social_score
                
                # Mutual connections boost (10% weight)
                current_user_following = set(UserFollow.objects.filter(
                    follower=current_user_owner
                ).values_list('following_id', flat=True))
                
                person_followers = set(UserFollow.objects.filter(
                    following=person
                ).values_list('follower_id', flat=True))
                
                mutual_connections = len(current_user_following.intersection(person_followers))
                mutual_score = min(mutual_connections / 10, 1.0)  # Cap at 1.0
                score += 0.1 * mutual_score
                
                # Recent activity boost (5% weight)
                # Users with recent posts get slight boost
                recent_posts = Post.objects.filter(
                    owner=person,
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
                activity_score = min(recent_posts / 20, 1.0)  # Cap at 1.0
                score += 0.05 * activity_score
                
                return min(score, 1.0)  # Cap total score at 1.0
            
            # Calculate scores for all potential users
            scored_users = []
            for person in potential_users:
                score = calculate_fuzzy_score(person, query)
                if score > 0.1:  # Only include users with meaningful similarity
                    scored_users.append((person, score))
            
            # Sort by score (descending) and get top 5
            scored_users.sort(key=lambda x: x[1], reverse=True)
            top_5_results = scored_users[:5]
            
            # Prepare results with additional info
            results = []
            for person, score in top_5_results:
                # Get mutual connections count
                current_user_following = set(UserFollow.objects.filter(
                    follower=current_user_owner
                ).values_list('following_id', flat=True))
                person_followers = set(UserFollow.objects.filter(
                    following=person
                ).values_list('follower_id', flat=True))
                mutual_count = len(current_user_following.intersection(person_followers))
                
                # Get recent activity
                recent_posts_count = Post.objects.filter(
                    owner=person,
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
                
                results.append({
                    'person': person,
                    'score': round(score * 100, 1),  # Convert to percentage
                    'mutual_connections': mutual_count,
                    'recent_posts': recent_posts_count,
                    'followers_count': UserFollow.objects.filter(following=person).count(),
                    'following_count': UserFollow.objects.filter(follower=person).count(),
                })
            
            context = {
                'results': results,
                'query': query,
                'total_found': len(scored_users)
            }
            
            return render(request, 'core/find_friend.html', context)
            
        except Owner.DoesNotExist:
            messages.error(request, 'User profile not found')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Search error: {str(e)}')
            return render(request, 'core/find_friend.html', {'results': [], 'query': query})
    
    return render(request, 'core/find_friend.html', {'results': [], 'query': ''})



@login_required
def conversation_view(request, username):
    """View to display conversation between current user and another user"""
    try:
        user_owner = request.user.owner
        partner_user = get_object_or_404(User, username=username)
        partner_owner = get_object_or_404(Owner, user=partner_user)
        
        # Get all messages between these users
        conversation_messages = Message.objects.filter(
            (models.Q(sender=user_owner) & models.Q(receiver=partner_owner)) | 
            (models.Q(sender=partner_owner) & models.Q(receiver=user_owner))
        ).order_by('created_at')
        
        # Mark all received messages as read
        unread_messages = Message.objects.filter(
            sender=partner_owner, 
            receiver=user_owner, 
            is_read=False
        )
        unread_messages.update(is_read=True, read_at=timezone.now())
        
        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            attachment = request.FILES.get('attachment')
            
            # Validate that either content or attachment is provided
            if not content and not attachment:
                messages.error(request, 'Please enter a message or attach a file')
                return redirect('conversation', username=username)
            
            # Validate content if provided
            if content:
                if len(content) > 1000:
                    messages.error(request, 'Message is too long (maximum 1000 characters)')
                    return redirect('conversation', username=username)
            
            # Validate attachment if provided
            if attachment:
                # Check file size (10MB limit)
                max_size = 10 * 1024 * 1024  # 10MB in bytes
                if attachment.size > max_size:
                    messages.error(request, 'File is too large. Maximum size is 10MB.')
                    return redirect('conversation', username=username)
                
                # Check file type
                allowed_types = [
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain',
                    'image/jpeg',
                    'image/png',
                    'image/gif',
                    'video/mp4',
                    'audio/mpeg',
                    'audio/mp3',
                    'application/zip',
                    'application/x-rar-compressed'
                ]
                
                if attachment.content_type not in allowed_types:
                    messages.error(request, 'File type not supported. Please select a valid file type.')
                    return redirect('conversation', username=username)
            
            try:
                # Create message with content and/or attachment
                message = Message.objects.create(
                    sender=user_owner,
                    receiver=partner_owner,
                    content=content if content else '',  # Allow empty content if there's an attachment
                    attachment=attachment
                )
                
                # Create notification for the receiver
                notification_content = f"{user_owner.user.first_name} {user_owner.user.last_name} sent you a message"
                if attachment:
                    notification_content += f" with attachment: {attachment.name}"
                
                Notification.objects.create(
                    owner=partner_owner,
                    content=notification_content,
                    is_read=False
                )
                
                messages.success(request, 'Message sent successfully!')
                return redirect('conversation', username=username)
            except Exception as e:
                messages.error(request, f'Failed to send message: {str(e)}')
                return redirect('conversation', username=username)
            
            return redirect('conversation', username=username)
        
        context = {
            'partner': partner_owner,
            'messages': conversation_messages,
            'current_user_owner': user_owner,
        }
        
        return render(request, 'core/conversation.html', context)
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')

@login_required
def start_chat_view(request, username):
    """View to start a new chat with another user"""
    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('home')
    
    try:
        # Get the receiver's profile
        receiver_user = get_object_or_404(User, username=username)
        receiver_owner = get_object_or_404(Owner, user=receiver_user)
        
        # Get current user's owner object
        sender_owner = request.user.owner
        
        # Don't allow messaging yourself
        if sender_owner == receiver_owner:
            messages.error(request, "You cannot send a message to yourself")
            return redirect('profile_user', username=username)
        
        # Get the message content from the form
        initial_message = request.POST.get('initial_message', '').strip()
        
        if not initial_message:
            messages.error(request, "Message cannot be empty")
            return redirect('profile_user', username=username)
        
        # Create the first message using the model's method
        Message.start_chat(
            sender=sender_owner,
            receiver=receiver_owner,
            initial_message=initial_message
        )
        
        messages.success(request, f"Started a new conversation with {receiver_user.first_name} {receiver_user.last_name}")
        return redirect('conversation', username=username)
        
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')
    except Exception as e:
        messages.error(request, f"Error starting conversation: {str(e)}")
        return redirect('profile_user', username=username)

@login_required
def notifications_view(request):
    """View to display user's notifications with filtering options"""
    try:
        user_owner = request.user.owner
        filter_type = request.GET.get('filter', '')
        
        # Base queryset
        notifications = Notification.objects.filter(owner=user_owner).order_by('-created_at')
        
        # Apply filters
        if filter_type == 'unread':
            notifications = notifications.filter(is_read=False)
        elif filter_type == 'likes':
            notifications = notifications.filter(content__icontains='liked')
        elif filter_type == 'comments':
            notifications = notifications.filter(content__icontains='comment')
        elif filter_type == 'follows':
            notifications = notifications.filter(content__icontains='following')
        
        # Get counts for tabs
        total_count = Notification.objects.filter(owner=user_owner).count()
        unread_count = Notification.objects.filter(owner=user_owner, is_read=False).count()
        
        context = {
            'notifications': notifications[:20],  # Limit to 20 for performance
            'filter_type': filter_type,
            'total_count': total_count,
            'unread_count': unread_count,
        }
        
        return render(request, 'core/notifications.html', context)
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(
                Notification, 
                id=notification_id, 
                owner=request.user.owner
            )
            notification.is_read = True
            notification.save()
            messages.success(request, 'Notification marked as read')
        except Notification.DoesNotExist:
            messages.error(request, 'Notification not found')
    
    return redirect('notifications')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        try:
            user_owner = request.user.owner
            updated_count = Notification.objects.filter(
                owner=user_owner, 
                is_read=False
            ).update(is_read=True)
            
            if updated_count > 0:
                messages.success(request, f'Marked {updated_count} notifications as read')
            else:
                messages.info(request, 'No unread notifications to mark')
        except Owner.DoesNotExist:
            messages.error(request, 'User profile not found')
    
    return redirect('notifications')

@login_required
def friends_view(request):
    """View to display friends, followers, following, and suggestions"""
    try:
        user_owner = request.user.owner
        tab = request.GET.get('tab', 'following')
        search_query = request.GET.get('search', '')
        
        people = []
        
        if tab == 'following':
            # People the user is following
            following_relationships = UserFollow.objects.filter(
                follower=user_owner
            ).select_related('following__user')
            people = [rel.following for rel in following_relationships]
            
        elif tab == 'followers':
            # People following the user
            follower_relationships = UserFollow.objects.filter(
                following=user_owner
            ).select_related('follower__user')
            people = [rel.follower for rel in follower_relationships]
            
        elif tab == 'suggestions':
            # Suggest people not already followed
            followed_ids = UserFollow.objects.filter(
                follower=user_owner
            ).values_list('following_id', flat=True)
            
            people = Owner.objects.exclude(
                id__in=followed_ids
            ).exclude(
                id=user_owner.id
            ).select_related('user')[:20]
            
        elif tab == 'mutual':
            # Find mutual connections
            user_following = set(UserFollow.objects.filter(
                follower=user_owner
            ).values_list('following_id', flat=True))
            
            mutual_people = []
            for person_id in user_following:
                person_following = set(UserFollow.objects.filter(
                    follower_id=person_id
                ).values_list('following_id', flat=True))
                
                mutual_connections = user_following.intersection(person_following)
                if mutual_connections:
                    person = Owner.objects.get(id=person_id)
                    person.mutual_friends_count = len(mutual_connections)
                    mutual_people.append(person)
            
            people = mutual_people
        
        # Apply search filter if provided
        if search_query and people:
            people = [
                person for person in people 
                if (search_query.lower() in person.user.first_name.lower() or 
                    search_query.lower() in person.user.last_name.lower() or 
                    search_query.lower() in person.user.username.lower())
            ]
        
        # Get counts for tabs
        following_count = UserFollow.objects.filter(follower=user_owner).count()
        followers_count = UserFollow.objects.filter(following=user_owner).count()
        
        context = {
            'people': people,
            'tab': tab,
            'following_count': following_count,
            'followers_count': followers_count,
            'search_query': search_query,
        }
        
        return render(request, 'core/friends.html', context)
    except Owner.DoesNotExist:
        messages.error(request, 'User profile not found')
        return redirect('home')

