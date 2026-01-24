import os
import requests
from datetime import datetime, timedelta

def get_clean_env(key_name):
    val = os.environ.get(key_name, "")
    return val.strip().replace('"', '').replace("'", "") if val else None

CL_TOKEN = get_clean_env('COURTLISTENER_TOKEN')

headers = {
    'Authorization': f'Token {CL_TOKEN}',
    'User-Agent': 'Test'
}

print("Testing basic API connectivity...")

try:
    # Simplest possible query - just get 5 opinions, no filters
    response = requests.get(
        "https://www.courtlistener.com/api/rest/v4/opinions/",
        params={'page_size': 5},
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ API is responding!")
        print(f"  Got {len(data.get('results', []))} results")
    else:
        print(f"✗ Error: {response.text[:200]}")
        
except requests.Timeout:
    print("✗ Request timed out after 30 seconds")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nTesting SCOTUS filter...")

try:
    response = requests.get(
        "https://www.courtlistener.com/api/rest/v4/opinions/",
        params={
            'cluster__docket__court': 'scotus',
            'page_size': 5
        },
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SCOTUS filter works!")
        print(f"  Got {len(data.get('results', []))} results")
        if data.get('results'):
            print(f"  First case: {data['results'][0].get('case_name', 'N/A')}")
            print(f"  Date: {data['results'][0].get('date_filed', 'N/A')}")
    else:
        print(f"✗ Error: {response.text[:200]}")
        
except requests.Timeout:
    print("✗ SCOTUS query timed out after 30 seconds")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nTesting SCOTUS filter WITH date filter...")

date_after = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
print(f"  Filtering for dates >= {date_after}")

try:
    response = requests.get(
        "https://www.courtlistener.com/api/rest/v4/opinions/",
        params={
            'cluster__docket__court': 'scotus',
            'date_filed__gte': date_after,
            'page_size': 5
        },
        headers=headers,
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Date filter works!")
        print(f"  Got {len(data.get('results', []))} results")
    else:
        print(f"✗ Error: {response.text[:200]}")
        
except requests.Timeout:
    print("✗ Date filter query TIMED OUT - this is the problem!")
except Exception as e:
    print(f"✗ Error: {e}")