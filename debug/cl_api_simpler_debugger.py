#!/usr/bin/env python3
"""
What's actually in the API? - No filters
"""

import os
import requests
from datetime import datetime, timedelta


def get_clean_env(key_name):
    val = os.environ.get(key_name, "")
    return val.strip().replace('"', '').replace("'", "") if val else None


CL_TOKEN = get_clean_env('COURTLISTENER_TOKEN')


def check_whats_available():
    """Query without court filter to see what's actually there"""
    
    if not CL_TOKEN:
        print("[!] ERROR: COURTLISTENER_TOKEN required")
        return
    
    print("="*80)
    print("CHECKING WHAT'S ACTUALLY AVAILABLE (NO COURT FILTER)")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'Authorization': f'Token {CL_TOKEN}',
        'User-Agent': 'SupremeCourtTracker/Debug'
    }
    
    date_after = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print("Querying opinions with: NO court filter (just recent date)")
    print(f"Date range: {date_after} to today\n")
    
    try:
        response = requests.get(
            "https://www.courtlistener.com/api/rest/v3/opinions/",
            params={'date_filed__gte': date_after, 'order_by': '-date_filed'},
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            print(f"Found {len(results)} results\n")
            
            court_samples = {}
            
            for idx, res in enumerate(results[:20], 1):
                cluster_url = res.get('cluster')
                if not cluster_url:
                    continue
                
                try:
                    cluster_res = requests.get(cluster_url, headers=headers, timeout=10)
                    cluster_data = cluster_res.json()
                    
                    docket_url = cluster_data.get('docket')
                    if docket_url:
                        docket_res = requests.get(docket_url, headers=headers, timeout=10)
                        docket_data = docket_res.json()
                        
                        court_id = docket_data.get('court', 'Unknown')
                        case_name = cluster_data.get('case_name', 'N/A')
                        
                        if court_id not in court_samples:
                            court_samples[court_id] = []
                        court_samples[court_id].append(case_name[:60])
                        
                except Exception as e:
                    continue
            
            # Show what courts we found
            print("="*80)
            print("COURTS FOUND IN RECENT DATA")
            print("="*80)
            for court_id in sorted(court_samples.keys()):
                cases = court_samples[court_id]
                print(f"\n{court_id}:")
                for case in cases[:2]:  # Show first 2 cases per court
                    print(f"  - {case}")
                if len(cases) > 2:
                    print(f"  ... and {len(cases)-2} more")
            
            print("\n" + "="*80)
            if 'scotus' in court_samples:
                print("✓ SCOTUS data exists in the API")
            else:
                print("✗ No SCOTUS data found in recent 7 days")
            print("="*80)
            
        else:
            print(f"Error: Got status code {response.status_code}")
            print(f"Response: {response.text[:500]}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_whats_available()