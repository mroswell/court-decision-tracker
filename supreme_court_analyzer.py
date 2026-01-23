#!/usr/bin/env python3
"""
Version A
Supreme Court Decision Tracker with AI Political Analysis
Fetches recent Supreme Court opinions and uses Gemini AI to classify them as conservative or liberal.
"""

import os
import csv
import requests
import feedparser
import google.generativeai as genai
from datetime import datetime, timedelta
import time


# Configure Gemini
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY not found in environment variables")
    exit(1)

genai.configure(api_key=GOOGLE_API_KEY)
# model = genai.GenerativeModel('gemini-pro')
model = genai.GenerativeModel('gemini-1.5-pro')


# CourtListener API (free, no key required)
COURTLISTENER_API = "https://www.courtlistener.com/api/rest/v3/opinions/"

def fetch_recent_decisions(days_back=30):
    """Fetch Supreme Court decisions from the last N days"""
    print(f"Fetching Supreme Court decisions from last {days_back} days...")
    
    date_filed_after = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    params = {
        'court': 'scotus',  # Supreme Court of the United States
        'date_filed__gte': date_filed_after,
        'order_by': '-date_filed',
        'type': '010combined'  # Combined opinions (most important)
    }
    
    headers = {'User-Agent': 'SupremeCourtTracker/1.0 (Educational Project)'}
    
    try:
        response = requests.get(COURTLISTENER_API, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        decisions = []
        for result in data.get('results', [])[:10]:  # Limit to 10 most recent
            decisions.append({
                'case_name': result.get('case_name', 'Unknown Case'),
                'date_filed': result.get('date_filed', ''),
                'url': f"https://www.courtlistener.com{result.get('absolute_url', '')}",
                'plain_text': result.get('plain_text', '')[:5000],  # First 5000 chars
                'html': result.get('html', '')
            })
        
        print(f"Found {len(decisions)} recent decisions")
        return decisions
        
    except Exception as e:
        print(f"Error fetching decisions: {e}")
        return []

def analyze_political_leaning(case_name, decision_text):
    """Use Gemini AI to classify decision on a 5-point political scale"""
    
    if not decision_text or len(decision_text) < 100:
        return "Insufficient text", "N/A", "Not enough text to analyze", "", "", "No text available for summary"
    
    prompt = f"""Analyze this Supreme Court decision and classify its political leaning on a 5-point scale.

Case: {case_name}

Decision excerpt (first 5000 characters):
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
        response = model.generate_content(prompt)
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
        print(f"Error analyzing with Gemini: {e}")
        return "Error", "N/A", str(e), "", "", "Error generating summary"

def load_existing_data(filename='supreme_court_decisions.csv'):
    """Load existing data to avoid re-analyzing same cases"""
    existing_cases = set()
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_cases.add(row['case_name'])
    
    return existing_cases

def save_to_csv(decisions_data, filename='supreme_court_decisions.csv'):
    """Save analyzed decisions to CSV"""
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(filename)
    
    fieldnames = ['date_filed', 'case_name', 'classification', 'confidence', 
                  'tags', 'notes', 'summary', 'reasoning', 'url', 'analyzed_date']
    
    mode = 'a' if file_exists else 'w'
    
    with open(filename, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for decision in decisions_data:
            writer.writerow(decision)
    
    print(f"Saved {len(decisions_data)} decisions to {filename}")

def main():
    print("="*60)
    print("Supreme Court Decision Tracker with AI Analysis")
    print("="*60)
    
    # Fetch recent decisions
    decisions = fetch_recent_decisions(days_back=30)
    
    if not decisions:
        print("No new decisions found")
        return
    
    # Load existing data to avoid duplicates
    existing_cases = load_existing_data()
    
    # Filter out already-analyzed cases
    new_decisions = [d for d in decisions if d['case_name'] not in existing_cases]
    
    if not new_decisions:
        print("All recent decisions have already been analyzed")
        return
    
    print(f"\nAnalyzing {len(new_decisions)} new decisions...")
    
    analyzed_decisions = []
    
    for i, decision in enumerate(new_decisions, 1):
        print(f"\n[{i}/{len(new_decisions)}] Analyzing: {decision['case_name']}")
        
        # Use plain_text if available, otherwise try to get summary
        decision_text = decision['plain_text'] if decision['plain_text'] else "No text available"
        
        classification, confidence, reasoning, tags, notes, summary = analyze_political_leaning(
            decision['case_name'],
            decision_text
        )
        
        analyzed_decisions.append({
            'date_filed': decision['date_filed'],
            'case_name': decision['case_name'],
            'classification': classification,
            'confidence': confidence,
            'tags': tags,
            'notes': notes,
            'summary': summary,
            'reasoning': reasoning,
            'url': decision['url'],
            'analyzed_date': datetime.now().strftime('%Y-%m-%d')
        })
        
        print(f"  Classification: {classification}")
        print(f"  Confidence: {confidence}")
        print(f"  Tags: {tags}")
        print(f"  Summary: {summary[:100]}...")
        print(f"  Reasoning: {reasoning[:100]}...")
        
        # Rate limiting - be nice to the API
        if i < len(new_decisions):
            time.sleep(2)
    
    # Save results
    if analyzed_decisions:
        save_to_csv(analyzed_decisions)
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        very_conservative = sum(1 for d in analyzed_decisions if 'very conservative' in d['classification'].lower())
        conservative = sum(1 for d in analyzed_decisions if d['classification'].lower() == 'conservative')
        center = sum(1 for d in analyzed_decisions if 'center' in d['classification'].lower())
        liberal = sum(1 for d in analyzed_decisions if d['classification'].lower() == 'liberal')
        very_liberal = sum(1 for d in analyzed_decisions if 'very liberal' in d['classification'].lower())
        
        print(f"Very Conservative decisions: {very_conservative}")
        print(f"Conservative decisions: {conservative}")
        print(f"Center decisions: {center}")
        print(f"Liberal decisions: {liberal}")
        print(f"Very Liberal decisions: {very_liberal}")
        print(f"\nAll data saved to supreme_court_decisions.csv")

if __name__ == "__main__":
    main()
