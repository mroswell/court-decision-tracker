
"""
Version B
Supreme Court Decision Tracker with AI Political Analysis
Fetches recent Supreme Court opinions and uses Gemini AI to classify them as conservative or liberal.
"""

import os
import csv
import requests
from google import genai
from datetime import datetime, timedelta
import time

# Version Assumption: Using Gemini API from google-genai package

# --- CONFIGURATION & CLEANING ---
def get_clean_env(key_name):
    """Retrieve and strip quotes/whitespace from environment variables."""
    val = os.environ.get(key_name, "")
    return val.strip().replace('"', '').replace("'", "") if val else None

GOOGLE_API_KEY = get_clean_env('GOOGLE_API_KEY')
CL_TOKEN = get_clean_env('COURTLISTENER_TOKEN')
COURTLISTENER_API = "https://www.courtlistener.com/api/rest/v3/opinions/"

# Initialize Gemini Client
client = None
if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini: {e}")

def print_troubleshooting_header():
    print("="*60)
    print("DIAGNOSTIC CHECK")
    print("-" * 60)
    print(f"Gemini Key Found:      {'YES' if GOOGLE_API_KEY else 'NO'}")
    print(f"CourtListener Token:   {'YES' if CL_TOKEN else 'NO'}")
    print(f"Current Time:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

def fetch_recent_decisions(days_back=60):
    if not CL_TOKEN:
        print("[!] ERROR: Set COURTLISTENER_TOKEN to fetch data.")
        return []

    print(f"[*] Fetching decisions from last {days_back} days...")
    date_after = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    params = {'court': 'scotus', 'date_filed__gte': date_after, 'order_by': '-date_filed'}
    headers = {'Authorization': f'Token {CL_TOKEN}', 'User-Agent': 'SupremeCourtTracker/1.0'}
    
    try:
        response = requests.get(COURTLISTENER_API, params=params, headers=headers)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        decisions = []
        for res in results[:10]:
            # FIX: Robust Case Name Extraction
            case_name = res.get('case_name')
            if not case_name and res.get('cluster'):
                # Try to get it from the URL if field is empty
                url_path = res.get('absolute_url', '')
                case_name = url_path.split('/')[-2].replace('-', ' ').title() if url_path else "Unknown Case"
            
            text = res.get('plain_text', '')
            if not text and res.get('id'):
                detail_res = requests.get(f"{COURTLISTENER_API}{res.get('id')}/", headers=headers)
                text = detail_res.json().get('plain_text', '') if detail_res.status_code == 200 else ""

            decisions.append({
                'case_name': case_name or "Unknown Case",
                'date_filed': res.get('date_filed', 'N/A'),
                'url': f"https://www.courtlistener.com{res.get('absolute_url', '')}",
                'plain_text': text[:15000]
            })
        return decisions
    except Exception as e:
        print(f"[!] CourtListener Error: {e}")
        return []

def analyze_leaning(case_name, text):
    if not client: return ("Error", "N/A", "Client not initialized", "", "", "")
    if not text or len(text) < 200: return ("No Text", "N/A", "Content missing", "", "", "")

    prompt = f"Analyze the political leaning of this SCOTUS case: {case_name}\n\nContent: {text}\n\n" \
             "Respond exactly: \nClassification: [Leaning]\nConfidence: [High/Med/Low]\n" \
             "Tags: [Topic list]\nSummary: [Brief summary]\nReasoning: [Explanation]"

    try:
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        r = response.text
        lines = {l.split(':', 1)[0].strip().lower(): l.split(':', 1)[1].strip() for l in r.split('\n') if ':' in l}
        return (lines.get('classification', 'Unknown'), lines.get('confidence', 'Low'), 
                lines.get('reasoning', 'N/A'), lines.get('tags', ''), "", lines.get('summary', ''))
    except Exception as e:
        return ("Error", "N/A", str(e), "", "", "Analysis failed")

def main():
    print_troubleshooting_header()
    if not GOOGLE_API_KEY or not CL_TOKEN: return

    cases = fetch_recent_decisions()
    processed = []
    
    for i, c in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}] Analyzing: {c['case_name']}")
        res = analyze_leaning(c['case_name'], c['plain_text'])
        processed.append({
            'date_filed': c['date_filed'], 'case_name': c['case_name'],
            'classification': res[0], 'confidence': res[1], 'reasoning': res[2],
            'tags': res[3], 'summary': res[5], 'url': c['url']
        })
        time.sleep(2)

    if processed:
        with open('scotus_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=processed[0].keys())
            writer.writeheader()
            writer.writerows(processed)
        print("\n[SUCCESS] Results saved to scotus_decisions.csv")

if __name__ == "__main__":
    main()