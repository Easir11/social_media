#!/usr/bin/env python3
"""
Simple test script for the fuzzy logic friend search functionality
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
from core.models import Owner

def test_user_search():
    """Test user search functionality via Django shell simulation"""
    
    print("=" * 60)
    print("TESTING FUZZY LOGIC FRIEND SEARCH - USER DATA")
    print("=" * 60)
    
    # Get all users in database
    users = User.objects.all().select_related('owner')
    print(f"📊 Total users in database: {users.count()}")
    print()
    
    if users.count() == 0:
        print("❌ No users found. Please ensure sample data exists.")
        return
    
    print("👥 Available users for search testing:")
    print("-" * 40)
    
    for i, user in enumerate(users, 1):
        try:
            owner = user.owner
            print(f"{i}. {user.first_name} {user.last_name} (@{user.username})")
            if owner.location:
                print(f"   📍 Location: {owner.location}")
            if owner.bio:
                print(f"   📝 Bio: {owner.bio[:60]}...")
            print()
        except Owner.DoesNotExist:
            print(f"{i}. {user.username} (No profile created yet)")
            print()
    
    # Test query examples
    print("🔍 Suggested test queries for the web interface:")
    print("-" * 50)
    
    test_queries = []
    
    # Extract search terms from actual user data
    for user in users[:10]:  # Limit to first 10 users
        try:
            owner = user.owner
            
            # Add name-based queries
            if user.first_name:
                test_queries.append(f"'{user.first_name.lower()}'")
            if user.last_name:
                test_queries.append(f"'{user.last_name.lower()}'")
            
            # Add location-based queries
            if owner.location:
                location_words = owner.location.lower().split()
                for word in location_words:
                    if len(word) > 3:  # Only meaningful words
                        test_queries.append(f"'{word}'")
            
            # Add bio-based queries
            if owner.bio:
                bio_words = owner.bio.lower().split()
                for word in bio_words:
                    if len(word) > 4:  # Only meaningful words
                        test_queries.append(f"'{word}'")
                        
        except Owner.DoesNotExist:
            continue
    
    # Remove duplicates and limit
    unique_queries = list(set(test_queries))[:15]
    
    for i, query in enumerate(unique_queries, 1):
        print(f"{i:2d}. Search for: {query}")
    
    print()
    print("🧪 Additional test queries:")
    print("-" * 30)
    additional_tests = [
        "'johnn' (typo test)",
        "'dev' (partial match)",
        "'photo' (interest search)",
        "'new york' (location search)",
        "'alice' (common name)"
    ]
    
    for test in additional_tests:
        print(f"• {test}")
    
    print()
    print("=" * 60)
    print("To test the fuzzy search:")
    print("1. Open http://127.0.0.1:8000/find-friends/ in your browser")
    print("2. Log in as any user")
    print("3. Try the suggested queries above")
    print("4. Check how fuzzy matching handles typos and partial matches")
    print("=" * 60)

def verify_web_urls():
    """Verify that the web URLs are properly configured"""
    
    print("\n" + "=" * 60)
    print("VERIFYING WEB INTERFACE CONFIGURATION")
    print("=" * 60)
    
    try:
        from django.urls import reverse
        
        # Test URL reversing
        urls_to_test = [
            ('home', 'Home page'),
            ('find_friend', 'Find friends page'),
            ('friends', 'Friends page'),
            ('signin', 'Sign in page'),
        ]
        
        print("🔗 Testing URL configuration:")
        print("-" * 35)
        
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {description}: {url}")
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
        
        print()
        print("🌐 Direct URLs to test:")
        print("-" * 25)
        print("• Home: http://127.0.0.1:8000/")
        print("• Find Friends: http://127.0.0.1:8000/find-friends/")
        print("• Sign In: http://127.0.0.1:8000/signin/")
        
    except Exception as e:
        print(f"❌ URL configuration error: {str(e)}")

if __name__ == "__main__":
    test_user_search()
    verify_web_urls()