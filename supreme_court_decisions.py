#!/usr/bin/env python3
"""
Version C - Supreme Court Decision Tracker with AI Political Analysis
Combines best features from Versions A and B
Fetches recent Supreme Court opinions and uses Gemini AI to classify them as conservative or liberal.
"""

import os
import csv
import requests
from google import genai
from datetime import datetime, timedelta
import time


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
        client = None


def print_troubleshooting_header():
    """Display diagnostic information about configuration"""
    print("="*60)
    print("SUPREME COURT DECISION TRACKER - DIAGNOSTIC CHECK")
    print("-" * 60)
    print(f"Gemini API Key Found:      {'YES' if GOOGLE_API_KEY else 'NO'}")
    print(f"CourtListener Token Found: {'YES' if CL_TOKEN else 'NO'}")
    print(f"Gemini Client Initialized: {'YES' if client else 'NO'}")
    print(f"Current Time:              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


def fetch_recent_decisions(days_back=8):
    """Fetch Supreme Court decisions from the last N days with comprehensive metadata"""
    if not CL_TOKEN:
        print("[!] ERROR: COURTLISTENER_TOKEN required. Set it in your environment variables.")
        return []

    print(f"[*] Fetching Supreme Court decisions from last {days_back} days...")
    
    date_after = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    params = {
        'court': 'scotus',
        'date_filed__gte': date_after,
        'order_by': '-date_filed'
    }
    
    headers = {
        'Authorization': f'Token {CL_TOKEN}',
        'User-Agent': 'SupremeCourtTracker/2.0 (Educational Research)'
    }
    
    try:
        response = requests.get(COURTLISTENER_API, params=params, headers=headers)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        print(f"[*] Found {len(results)} total results, processing top 10...")
        
        decisions = []
        for res in results[:10]:
            # Robust case name extraction
            case_name = res.get('case_name')
            if not case_name:
                url_path = res.get('absolute_url', '')
                case_name = url_path.split('/')[-2].replace('-', ' ').title() if url_path else "Unknown Case"
            
            # Get text - try plain_text first, then fallback to detail fetch
            text = res.get('plain_text', '')
            opinion_id = res.get('id')
            
            if not text and opinion_id:
                try:
                    detail_url = f"{COURTLISTENER_API}{opinion_id}/"
                    detail_res = requests.get(detail_url, headers=headers)
                    if detail_res.status_code == 200:
                        text = detail_res.json().get('plain_text', '')
                except Exception as e:
                    print(f"    [!] Could not fetch detail for opinion {opinion_id}: {e}")
            
            # Extract all metadata
            decisions.append({
                'opinion_id': opinion_id or 'N/A',
                'cluster_id': res.get('cluster', 'N/A'),
                'case_name': case_name or "Unknown Case",
                'date_filed': res.get('date_filed', 'N/A'),
                'author': res.get('author_str', 'N/A'),
                'type': res.get('type', 'N/A'),
                'citation': res.get('cluster_citation', 'N/A'),
                'page_count': res.get('page_count', 'N/A'),
                'url': f"https://www.courtlistener.com{res.get('absolute_url', '')}",
                'download_url': res.get('download_url', 'N/A'),
                'plain_text': text[:15000]  # First 15,000 characters
            })
        
        print(f"[*] Successfully retrieved {len(decisions)} decisions")
        return decisions
        
    except Exception as e:
        print(f"[!] Error fetching from CourtListener: {e}")
        return []


def analyze_political_leaning(case_name, decision_text):
    """Use Gemini AI to classify decision on a 5-point political scale with comprehensive tags"""
    
    if not client:
        return ("Error", "N/A", "Gemini client not initialized", "", "", "No analysis available")
    
    if not decision_text or len(decision_text) < 200:
        return ("Insufficient Text", "N/A", "Not enough text to analyze", "", "", "No text available for summary")
    
    prompt = f"""Analyze this Supreme Court decision and classify its political leaning on a 5-point scale.

Case: {case_name}

Decision excerpt (first 15,000 characters):
{decision_text}

Based on this decision, classify it as:
- "Very Conservative" - Strongly aligns with conservative legal principles (strict originalism, significant limitation of federal power, strong protection of gun rights/religious liberty, major restriction of abortion/regulatory power)
- "Conservative" - Moderately aligns with conservative legal principles
- "Center" - Balanced decision or doesn't clearly align with either ideology
- "Liberal" - Moderately aligns with liberal legal principles
- "Very Liberal" - Strongly aligns with liberal legal principles (broad constitutional interpretation, significant expansion of civil rights/federal power/environmental protection, strong restriction of gun rights)

Also identify relevant topic tags from this list (select ALL that apply, semicolon-separated):

AMENDMENTS (in order):
First Amendment;Second Amendment;Third Amendment;Fourth Amendment;Fifth Amendment;Sixth Amendment;Seventh Amendment;Eighth Amendment;Ninth Amendment;Tenth Amendment;Eleventh Amendment;Thirteenth Amendment;Fourteenth Amendment;Fifteenth Amendment;Sixteenth Amendment;Nineteenth Amendment;Twenty-First Amendment;Twenty-Fourth Amendment;Twenty-Sixth Amendment

OTHER TOPICS (alphabetical):
Abortion;Administrative Law;Antitrust;Bankruptcy;Business/Commerce;Capital Punishment;Civil Rights;Criminal Justice;Education;Election Law;Employment;Environment;Family Law;Federal Power;Healthcare;Immigration;Intellectual Property;International Law;LGBTQ Rights;Native American Law;National Security;Police Power;Privacy;Property Rights;State Rights;Taxation;Technology;Voting Rights

Create notes for each selected tag with semicolon-delimited descriptions:
Format: TagName - brief description of how it applies to this case

Respond in this exact format:
Classification: [Very Conservative/Conservative/Center/Liberal/Very Liberal]
Confidence: [High/Medium/Low]
Tags: [tag1;tag2;tag3]
Notes: [Tag1 - description;Tag2 - description;Tag3 - description]
Summary: [1-2 paragraph summary of the case: what was the legal question, what did the Court decide, and what was the key reasoning?]
Reasoning: [1-2 sentence explanation of classification]

Be objective and base your analysis only on the legal reasoning in the decision."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        result_text = response.text.strip()
        
        # Parse the response
        lines = result_text.split('\n')
        classification = "Unknown"
        confidence = "N/A"
        tags = ""
        notes = ""
        summary = ""
        reasoning = "N/A"
        
        # Handle multi-line summary by collecting all lines between Summary: and Reasoning:
        in_summary = False
        summary_lines = []
        
        for line in lines:
            if line.startswith('Classification:'):
                classification = line.split(':', 1)[1].strip()
            elif line.startswith('Confidence:'):
                confidence = line.split(':', 1)[1].strip()
            elif line.startswith('Tags:'):
                tags = line.split(':', 1)[1].strip()
            elif line.startswith('Notes:'):
                notes = line.split(':', 1)[1].strip()
            elif line.startswith('Summary:'):
                in_summary = True
                summary_part = line.split(':', 1)[1].strip()
                if summary_part:
                    summary_lines.append(summary_part)
            elif line.startswith('Reasoning:'):
                in_summary = False
                reasoning = line.split(':', 1)[1].strip()
            elif in_summary and line.strip():
                summary_lines.append(line.strip())
        
        summary = ' '.join(summary_lines) if summary_lines else "No summary available"
        
        return classification, confidence, reasoning, tags, notes, summary
        
    except Exception as e:
        print(f"[!] Error analyzing with Gemini: {e}")
        return ("Error", "N/A", str(e), "", "", "Error generating summary")


def load_existing_data(filename='supreme_court_decisions.csv'):
    """Load existing data to avoid re-analyzing same cases (using opinion_id)"""
    existing_ids = set()
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_ids.add(row.get('opinion_id', ''))
            print(f"[*] Loaded {len(existing_ids)} existing case IDs from {filename}")
        except Exception as e:
            print(f"[!] Error loading existing data: {e}")
    
    return existing_ids


def save_to_csv(decisions_data, filename='supreme_court_decisions.csv'):
    """Save analyzed decisions to CSV (append mode to preserve history)"""
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(filename)
    
    fieldnames = [
        'opinion_id', 'cluster_id', 'date_filed', 'case_name', 'author', 'type',
        'citation', 'page_count', 'url', 'download_url',
        'classification', 'confidence', 'tags', 'notes', 'summary', 'reasoning',
        'text_length', 'analyzed_date'
    ]
    
    mode = 'a' if file_exists else 'w'
    
    with open(filename, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for decision in decisions_data:
            writer.writerow(decision)
    
    print(f"[+] Saved {len(decisions_data)} decisions to {filename}")


def main():
    print("="*60)
    print("SUPREME COURT DECISION TRACKER WITH AI ANALYSIS")
    print("Version C - Enhanced Hybrid")
    print("="*60)
    print()
    
    # Display diagnostics
    print_troubleshooting_header()
    
    # Check requirements
    if not GOOGLE_API_KEY:
        print("[!] ERROR: GOOGLE_API_KEY not found in environment variables")
        return
    
    if not CL_TOKEN:
        print("[!] ERROR: COURTLISTENER_TOKEN not found in environment variables")
        return
    
    if not client:
        print("[!] ERROR: Could not initialize Gemini client")
        return
    
    # Fetch recent decisions (8 days covers Mon/Tue/Wed schedule with buffer)
    decisions = fetch_recent_decisions(days_back=8)
    
    if not decisions:
        print("[!] No decisions found")
        return
    
    # Load existing data to avoid duplicates
    existing_ids = load_existing_data()
    
    # Filter out already-analyzed cases
    new_decisions = [d for d in decisions if d['opinion_id'] not in existing_ids]
    
    if not new_decisions:
        print("[*] All recent decisions have already been analyzed")
        return
    
    print(f"\n[*] Analyzing {len(new_decisions)} new decisions...")
    print("-" * 60)
    
    analyzed_decisions = []
    
    for i, decision in enumerate(new_decisions, 1):
        print(f"\n[{i}/{len(new_decisions)}] Analyzing: {decision['case_name']}")
        print(f"    Author: {decision['author']}")
        print(f"    Date: {decision['date_filed']}")
        
        # Analyze with AI
        classification, confidence, reasoning, tags, notes, summary = analyze_political_leaning(
            decision['case_name'],
            decision['plain_text']
        )
        
        # Prepare complete record
        analyzed_decisions.append({
            'opinion_id': decision['opinion_id'],
            'cluster_id': decision['cluster_id'],
            'date_filed': decision['date_filed'],
            'case_name': decision['case_name'],
            'author': decision['author'],
            'type': decision['type'],
            'citation': decision['citation'],
            'page_count': decision['page_count'],
            'url': decision['url'],
            'download_url': decision['download_url'],
            'classification': classification,
            'confidence': confidence,
            'tags': tags,
            'notes': notes,
            'summary': summary,
            'reasoning': reasoning,
            'text_length': len(decision['plain_text']),
            'analyzed_date': datetime.now().strftime('%Y-%m-%d')
        })
        
        print(f"    Classification: {classification}")
        print(f"    Confidence: {confidence}")
        print(f"    Tags: {tags[:80]}{'...' if len(tags) > 80 else ''}")
        print(f"    Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
        
        # Rate limiting - be nice to the API
        if i < len(new_decisions):
            time.sleep(2)
    
    # Save results
    if analyzed_decisions:
        save_to_csv(analyzed_decisions)
        
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        
        # Count by classification
        very_conservative = sum(1 for d in analyzed_decisions if 'very conservative' in d['classification'].lower())
        conservative = sum(1 for d in analyzed_decisions if d['classification'].lower() == 'conservative')
        center = sum(1 for d in analyzed_decisions if 'center' in d['classification'].lower())
        liberal = sum(1 for d in analyzed_decisions if d['classification'].lower() == 'liberal')
        very_liberal = sum(1 for d in analyzed_decisions if 'very liberal' in d['classification'].lower())
        
        print(f"Very Conservative decisions: {very_conservative}")
        print(f"Conservative decisions:      {conservative}")
        print(f"Center decisions:            {center}")
        print(f"Liberal decisions:           {liberal}")
        print(f"Very Liberal decisions:      {very_liberal}")
        print(f"\n[SUCCESS] All data saved to supreme_court_decisions.csv")
        print("="*60)


if __name__ == "__main__":
    main()