#!/usr/bin/env python3
"""
Test CourtListener API V4 - Simple Version
"""

import os
import requests
from datetime import datetime, timedelta


def get_clean_env(key_name):
    val = os.environ.get(key_name, "")
    return val.strip().replace('"', '').replace("'", "") if val else None


CL_TOKEN = get_clean_env('COURTLISTENER_TOKEN')


def test_v4_simple():
    """Test V4 API with minimal parameters"""
    
    if not CL_TOKEN:
        print("[!] ERROR: COURTLISTENER_TOKEN required")
        return
    
    print("="*80)
    print("TESTING COURTLISTENER API V4 - SIMPLE")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'Authorization': f'Token {CL_TOKEN}',
        'User-Agent': 'SupremeCourtTracker/V4Test'
    }
    
    # Test 1: Just get recent opinions, no court filter
    print("Test 1: Recent opinions (no court filter, last 3 days)...\n")
    
    try:
        date_after = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        response = requests.get(
            "https://www.courtlistener.com/api/rest/v4/opinions/",
            params={'date_filed__gte': date_after, 'page_size': 5},
            headers=headers,
            timeout=30  # Longer timeout
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✓ Found {len(results)} results\n")
            
            if results:
                print("Sample result structure:")
                print(f"  Keys available: {list(results[0].keys())}\n")
        else:
            print(f"✗ Error: {response.text[:500]}\n")
            
    except requests.Timeout:
        print("✗ Request timed out after 30 seconds\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 2: Try clusters endpoint
    print("\nTest 2: Clusters endpoint (no filters, last 3 days)...\n")
    
    try:
        response = requests.get(
            "https://www.courtlistener.com/api/rest/v4/clusters/",
            params={'date_filed__gte': date_after, 'page_size': 5},
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✓ Found {len(results)} results\n")
            
            if results:
                print("Sample cluster structure:")
                print(f"  Keys available: {list(results[0].keys())}\n")
        else:
            print(f"✗ Error: {response.text[:500]}\n")
            
    except requests.Timeout:
        print("✗ Request timed out after 30 seconds\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    print("="*80)
    print("If both timed out, the V4 API might be slow/overloaded.")
    print("Check CourtListener's status or documentation for V4 migration.")
    print("="*80)


if __name__ == "__main__":
    test_v4_simple()