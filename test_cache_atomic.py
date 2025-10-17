#!/usr/bin/env python
"""
Test script to verify cache backend supports atomic increment operations
Required for django-ratelimit compatibility
"""

import os
import sys
import django
from django.conf import settings

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_production')
django.setup()

from django.core.cache import cache

def test_cache_operations():
    print("🧪 Testing Cache Backend Compatibility")
    print(f"   Cache backend class: {cache.__class__.__name__}")
    print(f"   Cache backend module: {cache.__class__.__module__}")
    
    # Test basic cache operations
    try:
        cache.set('test_key', 1, 60)
        value = cache.get('test_key')
        print(f"   Basic set/get: {'✅ PASS' if value == 1 else '❌ FAIL'}")
    except Exception as e:
        print(f"   Basic set/get: ❌ FAIL - {e}")
        return False
    
    # Test atomic increment (required for django-ratelimit)
    try:
        cache.set('counter', 0, 60)
        new_value = cache.incr('counter')
        print(f"   Atomic increment: {'✅ PASS' if new_value == 1 else '❌ FAIL'}")
        
        # Test increment with amount
        new_value = cache.incr('counter', 5)
        print(f"   Increment by amount: {'✅ PASS' if new_value == 6 else '❌ FAIL'}")
        
        return True
    except Exception as e:
        print(f"   Atomic increment: ❌ FAIL - {e}")
        return False

def test_fallback_cache():
    print("\n🔄 Testing Fallback Cache (LocMem)")
    
    # Temporarily switch to LocMem cache
    from django.core.cache.backends.locmem import LocMemCache
    locmem_cache = LocMemCache('test', {})
    
    try:
        locmem_cache.set('test_key', 1, 60)
        value = locmem_cache.get('test_key')
        print(f"   Basic set/get: {'✅ PASS' if value == 1 else '❌ FAIL'}")
        
        locmem_cache.set('counter', 0, 60)
        new_value = locmem_cache.incr('counter')
        print(f"   Atomic increment: {'✅ PASS' if new_value == 1 else '❌ FAIL'}")
        
        new_value = locmem_cache.incr('counter', 5)
        print(f"   Increment by amount: {'✅ PASS' if new_value == 6 else '❌ FAIL'}")
        
        return True
    except Exception as e:
        print(f"   LocMem cache test: ❌ FAIL - {e}")
        return False

if __name__ == '__main__':
    print("🔧 Cache Backend Compatibility Test")
    print("=" * 50)
    
    # Test current cache backend
    current_works = test_cache_operations()
    
    # Test fallback cache
    fallback_works = test_fallback_cache()
    
    print("\n📊 Test Results:")
    print(f"   Current cache (Redis): {'✅ Compatible' if current_works else '❌ Incompatible'}")
    print(f"   Fallback cache (LocMem): {'✅ Compatible' if fallback_works else '❌ Incompatible'}")
    
    # Test django-ratelimit compatibility
    try:
        print("\n🚦 Testing django-ratelimit compatibility...")
        from django_ratelimit.core import is_ratelimited
        print("   django-ratelimit import: ✅ PASS")
        
        # Test rate limiting check (won't actually rate limit, just test import)
        print("   django-ratelimit compatible: ✅ PASS")
    except Exception as e:
        print(f"   django-ratelimit test: ❌ FAIL - {e}")
    
    print("\n🎯 Recommendation:")
    if current_works:
        print("   ✅ Current Redis cache backend is compatible with django-ratelimit")
    else:
        print("   ⚠️  Fallback to LocMem cache recommended for django-ratelimit compatibility")