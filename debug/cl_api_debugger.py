#!/usr/bin/env python3
"""
Supreme Court API Debugging Tool - Enhanced
Tests different query parameters to get actual SCOTUS cases
"""

import os
import json
import requests
from datetime import datetime, timedelta


def get_clean_env(key_name):
    """Retrieve and strip quotes/whitespace from environment variables."""
    val = os.environ.get(key_name, "")
    return val.strip().replace('"', '').replace("'", "") if val else None


CL_TOKEN = get_clean_env('COURTLISTENER_TOKEN')
COURTLISTENER_API = "https://www.courtlistener.com/api/rest/v3/opinions/"


def test_query(query_name, params, headers):
    """Test a specific query configuration"""
    print(f"\n{'='*80}")
    print(f"TESTING: {query_name}")
    print(f"{'='*80}")
    print(f"Parameters: {params}\n")
    
    try:
        response = requests.get(COURTLISTENER_API, params=params, headers=headers)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        print(f"[*] Found {len(results)} results\n")
        
        if results:
            # Show first 3 results summary
            for idx, res in enumerate(results[:3], 1):
                cluster_url = res.get('cluster')
                cluster_data = {}
                
                if cluster_url:
                    try:
                        cluster_res = requests.get(cluster_url, headers=headers)
                        if cluster_res.status_code == 200:
                            cluster_data = cluster_res.json()
                    except:
                        pass
                
                case_name = res.get('case_name') or cluster_data.get('case_name', 'N/A')
                date_filed = cluster_data.get('date_filed', res.get('date_filed', 'N/A'))
                per_curiam = res.get('per_curiam') or cluster_data.get('per_curiam', False)
                author_str = cluster_data.get('author_str', res.get('author_str', ''))
                
                print(f"  [{idx}] {case_name}")
                print(f"      Date: {date_filed}")
                print(f"      Type: {res.get('type', 'N/A')}")
                print(f"      Per Curiam: {per_curiam}")
                print(f"      Author: {author_str if author_str else 'None/Per Curiam'}")
                print(f"      URL: {res.get('absolute_url', 'N/A')}")
                print()
        else:
            print("  [!] No results found\n")
            
        return len(results)
        
    except Exception as e:
        print(f"  [!] Error: {e}\n")
        return 0


def debug_api_response():
    """Test multiple query configurations to find actual SCOTUS cases"""
    
    if not CL_TOKEN:
        print("[!] ERROR: COURTLISTENER_TOKEN required. Set it in your environment variables.")
        return
    
    print("="*80)
    print("COURTLISTENER API DEBUGGING TOOL - QUERY TESTING")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    headers = {
        'Authorization': f'Token {CL_TOKEN}',
        'User-Agent': 'SupremeCourtTracker/Debug (Educational Research)'
    }
    
    # Try looking back further since SCOTUS doesn't issue daily
    date_after_30 = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    date_after_90 = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    results_counts = {}
    
    # Test 1: Original query
    results_counts['Original (scotus, 30 days)'] = test_query(
        "Original Query (scotus, 30 days)",
        {
            'court': 'scotus',
            'date_filed__gte': date_after_30,
            'order_by': '-date_filed'
        },
        headers
    )
    
    # Test 2: Add court_id
    results_counts['With court_id (30 days)'] = test_query(
        "With court_id parameter (30 days)",
        {
            'court': 'scotus',
            'court_id': 'scotus',
            'date_filed__gte': date_after_30,
            'order_by': '-date_filed'
        },
        headers
    )
    
    # Test 3: Lead opinions only
    results_counts['Lead opinions only (30 days)'] = test_query(
        "Lead opinions only (30 days)",
        {
            'court': 'scotus',
            'type': '020lead',
            'date_filed__gte': date_after_30,
            'order_by': '-date_filed'
        },
        headers
    )
    
    # Test 4: 90 days back
    results_counts['90 days back'] = test_query(
        "90 days lookback (scotus)",
        {
            'court': 'scotus',
            'date_filed__gte': date_after_90,
            'order_by': '-date_filed'
        },
        headers
    )
    
    # Test 5: Try the clusters endpoint instead
    print(f"\n{'='*80}")
    print(f"TESTING: Clusters Endpoint (Alternative)")
    print(f"{'='*80}")
    print("Using /api/rest/v3/clusters/ instead of /opinions/\n")
    
    try:
        clusters_url = "https://www.courtlistener.com/api/rest/v3/clusters/"
        response = requests.get(
            clusters_url,
            params={
                'court': 'scotus',
                'date_filed__gte': date_after_30,
                'order_by': '-date_filed'
            },
            headers=headers
        )
        response.raise_for_status()
        cluster_results = response.json().get('results', [])
        
        print(f"[*] Found {len(cluster_results)} cluster results\n")
        
        if cluster_results:
            for idx, cluster in enumerate(cluster_results[:3], 1):
                print(f"  [{idx}] {cluster.get('case_name', 'N/A')}")
                print(f"      Date: {cluster.get('date_filed', 'N/A')}")
                print(f"      Author: {cluster.get('author_str', 'None/Per Curiam')}")
                print(f"      Docket ID: {cluster.get('docket_id', 'N/A')}")
                print()
                
        results_counts['Clusters endpoint (30 days)'] = len(cluster_results)
        
    except Exception as e:
        print(f"  [!] Error: {e}\n")
        results_counts['Clusters endpoint'] = 0
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY OF RESULTS")
    print("="*80)
    for query_name, count in results_counts.items():
        print(f"{query_name:40s} : {count:3d} results")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("1. Check if any query returned actual Supreme Court cases")
    print("2. If all show state courts, file issue with CourtListener")
    print("3. Consider using clusters endpoint if it works better")
    print("4. May need to use docket endpoint with 'court' filter")
    print("="*80)


if __name__ == "__main__":
    debug_api_response()