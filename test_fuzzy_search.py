#!/usr/bin/env python3
"""
Test script for the fuzzy logic friend search functionality
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
from core.views import find_friend_candidates

def test_fuzzy_search():
    """Test the fuzzy logic friend search functionality"""
    
    print("=" * 60)
    print("TESTING FUZZY LOGIC FRIEND SEARCH FUNCTIONALITY")
    print("=" * 60)
    
    # Get a test user
    try:
        test_user = User.objects.first()
        if not test_user:
            print("❌ No users found in database")
            return
            
        print(f"🔍 Testing with user: {test_user.username}")
        print()
        
        # Test cases
        test_queries = [
            "john",        # Name search
            "smith",       # Last name search
            "new york",    # Location search
            "developer",   # Bio/interest search
            "alice",       # Another name
            "photography", # Interest
            "london",      # Location
            "johnn",       # Typo test
            "smth",        # Partial/typo test
        ]
        
        for query in test_queries:
            print(f"🔎 Searching for: '{query}'")
            print("-" * 40)
            
            try:
                # Get the fuzzy search results
                results = find_friend_candidates(test_user, query)
                
                if results:
                    print(f"✅ Found {len(results)} match(es):")
                    for i, result in enumerate(results, 1):
                        person = result['person']
                        score = result['score']
                        print(f"  {i}. {person.user.first_name} {person.user.last_name} (@{person.user.username})")
                        print(f"     Score: {score}%")
                        if person.location:
                            print(f"     Location: {person.location}")
                        if person.bio:
                            print(f"     Bio: {person.bio[:60]}...")
                        print()
                else:
                    print("❌ No matches found")
                    
            except Exception as e:
                print(f"❌ Error during search: {str(e)}")
                
            print()
            
    except Exception as e:
        print(f"❌ Error setting up test: {str(e)}")
        
    print("=" * 60)
    print("FUZZY SEARCH TEST COMPLETED")
    print("=" * 60)

def test_search_components():
    """Test individual components of the fuzzy search"""
    
    print("\n" + "=" * 60)
    print("TESTING FUZZY SEARCH COMPONENTS")
    print("=" * 60)
    
    # Import the helper functions from the view
    from core.views import (
        calculate_char_frequency_similarity,
        calculate_subsequence_similarity,
        calculate_edit_distance
    )
    
    # Test cases for string matching
    test_cases = [
        ("john", "john", "Exact match"),
        ("john", "johnn", "Single typo"),
        ("smith", "smth", "Missing letters"),
        ("alice", "allice", "Extra letter"),
        ("developer", "dev", "Partial match"),
        ("photography", "photo", "Prefix match"),
        ("new york", "newyork", "Space difference"),
    ]
    
    print("🧪 Testing string similarity functions:")
    print()
    
    for query, target, description in test_cases:
        print(f"Testing: '{query}' vs '{target}' ({description})")
        
        # Test character frequency similarity
        char_freq = calculate_char_frequency_similarity(query, target)
        print(f"  Character Frequency: {char_freq:.2f}")
        
        # Test subsequence similarity
        subseq = calculate_subsequence_similarity(query, target)
        print(f"  Subsequence: {subseq:.2f}")
        
        # Test edit distance (normalized)
        edit_dist = calculate_edit_distance(query, target)
        normalized_edit = max(0, 1 - (edit_dist / max(len(query), len(target))))
        print(f"  Edit Distance: {edit_dist} (normalized: {normalized_edit:.2f})")
        
        print()

if __name__ == "__main__":
    test_search_components()
    test_fuzzy_search()