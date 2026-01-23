#!/usr/bin/env python3
"""
Test V4 API - SCOTUS Filter
"""

import os
import requests
from datetime import datetime, timedelta


def get_clean_env(key_name):
    val = os.environ.get(key_name, "")
    return val.strip().replace('"', '').replace("'", "") if val else None


CL_TOKEN = get_clean_env('COURTLISTENER_TOKEN')


def test_scotus_filter():
    """Test if court='scotus' filter works in V4"""
    
    if not CL_TOKEN:
        print("[!] ERROR: COURTLISTENER_TOKEN required")
        return
    
    print("="*80)
    print("TESTING V4 API - SCOTUS FILTER")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'Authorization': f'Token {CL_TOKEN}',
        'User-Agent': 'SupremeCourtTracker/V4Test'
    }
    
    date_after = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print("Querying: court='scotus', last 90 days\n")
    
    try:
        response = requests.get(
            "https://www.courtlistener.com/api/rest/v4/opinions/",
            params={'court': 'scotus', 'date_filed__gte': date_after, 'page_size': 10},
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"Found {len(results)} results\n")
            
            if results:
                print("Checking actual courts for these results...\n")
                
                court_counts = {}
                
                for idx, res in enumerate(results[:5], 1):
                    cluster_url = res.get('cluster')
                    
                    if cluster_url:
                        try:
                            # Get cluster
                            cluster_res = requests.get(cluster_url, headers=headers, timeout=10)
                            cluster_data = cluster_res.json()
                            
                            # Get docket
                            docket_url = cluster_data.get('docket')
                            if docket_url:
                                docket_res = requests.get(docket_url, headers=headers, timeout=10)
                                docket_data = docket_res.json()
                                
                                court_id = docket_data.get('court', 'Unknown')
                                case_name = cluster_data.get('case_name', 'N/A')
                                date_filed = cluster_data.get('date_filed', 'N/A')
                                author_str = res.get('author_str', 'N/A')
                                
                                print(f"[{idx}] {case_name[:60]}")
                                print(f"    Actual Court: {court_id}")
                                print(f"    Date: {date_filed}")
                                print(f"    Author: {author_str}")
                                print()
                                
                                court_counts[court_id] = court_counts.get(court_id, 0) + 1
                                
                        except Exception as e:
                            print(f"[{idx}] Error checking court: {e}\n")
                
                print("="*80)
                print("COURT DISTRIBUTION")
                print("="*80)
                for court, count in sorted(court_counts.items()):
                    print(f"{court:30s} : {count} cases")
                
                print("\n" + "="*80)
                if 'scotus' in court_counts or 'https://www.courtlistener.com/api/rest/v4/courts/scotus/' in court_counts:
                    print("✓ SCOTUS filter is working!")
                else:
                    print("✗ SCOTUS filter is BROKEN - returning wrong courts")
                print("="*80)
            else:
                print("No results found - might not be any recent SCOTUS decisions")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_scotus_filter()