# Supreme Court Decision Tracker with AI Analysis

Automatically tracks new Supreme Court decisions and uses Google's Gemini AI to classify them on a 5-point political scale with comprehensive topic tagging.

## What it does:

1. **Fetches** recent Supreme Court opinions from CourtListener API (authenticated access)
2. **Analyzes** each decision using Gemini 2.0 Flash AI to determine political leaning
3. **Saves** results to a CSV file with comprehensive metadata and AI analysis
4. **Avoids duplicates** - only analyzes new cases, appends to existing data
5. **Runs automatically** every Monday, Tuesday, and Wednesday at 1:00 PM EST

## Setup Instructions:

### 1. Get a Free Gemini API Key

1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Copy your API key

### 2. Get a Free CourtListener API Token

1. Go to https://www.courtlistener.com/
2. Create a free account (or sign in)
3. Go to your profile → API Access
4. Copy your API token

### 3. Add Secrets to GitHub Repository

1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add both:
   - Name: `GOOGLE_API_KEY` | Value: Your Gemini API key
   - Name: `COURTLISTENER_TOKEN` | Value: Your CourtListener token
3. Click **"Add secret"** for each

### 4. Set Up the GitHub Action

1. Create folder structure in your repository:
   ```
   .github/workflows/
   ```

2. Copy the workflow YAML to `.github/workflows/scotus-tracker.yml`

3. Copy `supreme_court_decisions.py` to the root of your repository

4. Commit and push:
   ```bash
   git add .
   git commit -m "Add Supreme Court tracker"
   git push
   ```

### 5. Run It!

**Automatic:** Runs every Monday, Tuesday, Wednesday at 1:00 PM EST / 2:00 PM EDT

**Manual:** 
1. Go to **Actions** tab in GitHub
2. Click "SCOTUS Decisions"
3. Click "Run workflow"

## Output:

Results saved to `supreme_court_decisions.csv` with **18 comprehensive fields**:

### CourtListener Metadata (10 fields):
| Field | Description |
|-------|-------------|
| `opinion_id` | Unique CourtListener database ID |
| `cluster_id` | Groups related opinions together |
| `date_filed` | When the case was filed |
| `case_name` | Name of the case (e.g., "Dobbs v. Jackson") |
| `author` | Justice who authored the opinion |
| `type` | Opinion type (combined/lead/concurrence/dissent) |
| `citation` | Official case citation (e.g., "597 U.S. 215") |
| `page_count` | Length of the opinion in pages |
| `url` | CourtListener web page URL |
| `download_url` | Direct PDF download link |

### AI Analysis Fields (6 fields):
| Field | Description |
|-------|-------------|
| `classification` | Political leaning (5-point scale) |
| `confidence` | AI's confidence level (High/Medium/Low) |
| `tags` | Topic tags, semicolon-separated |
| `notes` | Tag-specific descriptions, semicolon-separated |
| `summary` | 1-2 paragraph case summary |
| `reasoning` | Why it was classified this way |

### Processing Metadata (2 fields):
| Field | Description |
|-------|-------------|
| `text_length` | Number of characters analyzed |
| `analyzed_date` | When the AI analysis was performed |

### Example Row:

| opinion_id | date_filed | case_name | author | classification | confidence | tags | summary |
|------------|------------|-----------|--------|----------------|------------|------|---------|
| 8234567 | 2024-06-24 | Dobbs v. Jackson | Alito | Very Conservative | High | Fourteenth Amendment;Abortion;State Rights | The Court was asked whether all pre-viability prohibitions on elective abortions are unconstitutional. The Court held that the Constitution does not confer a right to abortion and overruled Roe v. Wade and Planned Parenthood v. Casey... |

The **summary** field provides comprehensive context including:
- The legal question presented to the Court
- What the Court decided
- Key reasoning from the majority opinion

The **notes** field explains each tag's relevance:
```
Fourteenth Amendment - Due process analysis of abortion rights;Abortion - Overturns Roe v Wade precedent;State Rights - Returns regulation to individual states
```

## 5-Point Classification Scale:

- **Very Conservative** - Strongly aligns with conservative legal principles (strict originalism, significant limitation of federal power, strong protection of gun rights/religious liberty, major restriction of abortion/regulatory power)
- **Conservative** - Moderately aligns with conservative legal principles  
- **Center** - Balanced decision or doesn't clearly align with either ideology
- **Liberal** - Moderately aligns with liberal legal principles
- **Very Liberal** - Strongly aligns with liberal legal principles (broad constitutional interpretation, significant expansion of civil rights/federal power/environmental protection, strong restriction of gun rights)

## Comprehensive Tagging System (47 total tags):

### Constitutional Amendments (19 tags):
1. **First Amendment** - Speech, press, religion, assembly, petition
2. **Second Amendment** - Gun rights, militia, firearms regulation
3. **Third Amendment** - Quartering of soldiers (rare)
4. **Fourth Amendment** - Search and seizure, warrants, privacy
5. **Fifth Amendment** - Self-incrimination, due process, eminent domain, double jeopardy
6. **Sixth Amendment** - Right to counsel, jury trials, speedy trial, confrontation
7. **Seventh Amendment** - Civil jury trials
8. **Eighth Amendment** - Cruel and unusual punishment, excessive bail/fines
9. **Ninth Amendment** - Unenumerated rights retained by people
10. **Tenth Amendment** - Powers reserved to states and people
11. **Eleventh Amendment** - Sovereign immunity, limitations on federal courts
12. **Thirteenth Amendment** - Abolition of slavery, involuntary servitude
13. **Fourteenth Amendment** - Equal protection, due process, citizenship, incorporation
14. **Fifteenth Amendment** - Voting rights (racial discrimination)
15. **Sixteenth Amendment** - Federal income tax authority
16. **Nineteenth Amendment** - Women's suffrage and voting rights
17. **Twenty-First Amendment** - Alcohol regulation, repeal of prohibition
18. **Twenty-Fourth Amendment** - Poll tax prohibition in federal elections
19. **Twenty-Sixth Amendment** - Voting age lowered to 18

### Other Legal Topics (28 tags, alphabetical):
20. **Abortion** - Reproductive rights, access, restrictions
21. **Administrative Law** - Agency authority, regulations, deference doctrines
22. **Antitrust** - Monopolies, market competition, mergers
23. **Bankruptcy** - Debt discharge, creditor rights, reorganization
24. **Business/Commerce** - Corporate law, contracts, commerce clause
25. **Capital Punishment** - Death penalty constitutionality and procedures
26. **Civil Rights** - Discrimination, equality, protected classes
27. **Criminal Justice** - Sentencing, procedure, defendant rights
28. **Education** - School policy, student rights, funding
29. **Election Law** - Campaign finance, redistricting, ballot access
30. **Employment** - Labor relations, workplace rights, discrimination
31. **Environment** - EPA authority, climate regulation, pollution
32. **Family Law** - Marriage, custody, adoption, parental rights
33. **Federal Power** - Scope of federal authority vs. state sovereignty
34. **Healthcare** - Medical law, insurance, patient rights
35. **Immigration** - Deportation, asylum, border enforcement, citizenship
36. **Intellectual Property** - Patents, copyrights, trademarks
37. **International Law** - Treaties, foreign relations, extraterritorial application
38. **LGBTQ Rights** - Marriage equality, discrimination, identity
39. **Native American Law** - Tribal sovereignty, treaties, jurisdiction
40. **National Security** - War powers, military tribunals, surveillance
41. **Police Power** - Qualified immunity, use of force, police conduct
42. **Privacy** - Data protection, surveillance, informational privacy
43. **Property Rights** - Takings clause, land use, eminent domain
44. **State Rights** - Federalism, state sovereignty, Tenth Amendment
45. **Taxation** - Tax law, IRS authority, tax challenges
46. **Technology** - Internet regulation, social media, AI, digital rights
47. **Voting Rights** - Access, restrictions, gerrymandering, voter ID

**Tags** are semicolon-delimited: `First Amendment;Technology;Free Speech`

**Notes** provide context for each tag: `First Amendment - Platform content moderation standards;Technology - Social media regulation;Free Speech - Government pressure on private platforms`

## How It Works:

### Smart Duplicate Prevention
- Uses `opinion_id` to track which cases have been analyzed
- Only processes new decisions
- Appends to existing CSV file, preserving all historical data

### Intelligent Data Fetching
- Looks back 8 days (perfect for Mon/Tue/Wed schedule)
- Captures up to 15,000 characters of decision text
- Falls back to detailed API calls if text not immediately available
- Extracts robust case name from multiple sources

### Comprehensive AI Analysis
The script sends each decision to Gemini 2.0 Flash with detailed instructions to:
1. Read and understand the legal reasoning
2. Classify on the 5-point scale with specific criteria
3. Select ALL applicable tags from 47 topics (19 Amendments + 28 legal areas)
4. Provide tag-specific notes explaining relevance
5. Generate a comprehensive 1-2 paragraph summary
6. Assess confidence level and provide reasoning

## View Your Data:

The CSV file will be automatically committed to your repository after each run. You can:
- Download it directly from GitHub
- View it in GitHub's CSV viewer
- Import into Google Sheets or Excel
- Analyze with Python/R/Julia
- Build visualizations and dashboards
- Track court trends over time

## Free API Limits:

- **CourtListener API:** Free tier with authentication, generous limits for research
- **Gemini 2.0 Flash API:** Free tier = 1,500 requests/day, plenty for this use case

## Troubleshooting:

**No decisions found:**
- The Supreme Court doesn't release opinions every week
- Most opinions released Oct-June during court term
- Summer (July-Sept) typically has fewer decisions

**API errors:**
- Check that both `GOOGLE_API_KEY` and `COURTLISTENER_TOKEN` secrets are set correctly
- Verify secrets don't have extra quotes or whitespace
- Check you haven't exceeded free tier limits
- Check Actions tab for detailed error logs

**Permission denied (403) when pushing:**
- Add `permissions: contents: write` to workflow file
- Or: Settings → Actions → General → Workflow permissions → "Read and write"

**CSV not updating:**
- Check the Actions tab for error logs
- Verify the workflow file is on the main/default branch
- Ensure scheduled workflows are enabled in repo settings

## Technical Stack:

- **Python 3.11** - Main programming language
- **CourtListener API** - Supreme Court opinion data source
- **Google Gemini 2.0 Flash** - AI analysis model
- **GitHub Actions** - Automation and scheduling
- **CSV** - Simple, universal data format

## Educational Value:

Students learn about:
- ✅ GitHub Actions automation and CI/CD
- ✅ Working with government/legal APIs
- ✅ AI prompt engineering for complex analysis
- ✅ Data collection, deduplication, and management
- ✅ Political science + technology intersection
- ✅ CSV data manipulation and analysis
- ✅ Environment variables and secrets management
- ✅ Git workflows and version control

## Data Source:

**CourtListener** by Free Law Project - a non-profit creating open legal data
- Website: https://www.courtlistener.com/
- API Docs: https://www.courtlistener.com/api/
- All Supreme Court opinions are public domain

## Extend This Project:

Ideas for enhancement:
- Add sentiment analysis of dissenting opinions
- Track which justices wrote majority/dissent/concurrence
- Create visualizations showing court ideological trends over time
- Compare AI classification vs legal expert opinions
- Build a website/dashboard to display results interactively
- Send email notifications for new decisions
- Add more detailed natural language processing
- Generate statistical summaries by term/year
- Link cases by citations and precedent
- Create a mobile app interface

## Research Applications:

This dataset can be used to study:
- Ideological drift of the Court over time
- Consistency of individual justices
- Impact of Court composition changes
- Frequency of different constitutional issues
- Correlation between case topics and political leaning
- Writing styles and persuasive techniques
- Citation patterns and precedent usage

## License:

Public domain - use freely for educational, research, or commercial purposes!

## Acknowledgments:

- **Free Law Project** for CourtListener API
- **Google** for Gemini AI access
- **GitHub** for Actions automation
- **Supreme Court of the United States** for public domain opinions

---

**Questions or improvements?** Open an issue or submit a pull request!
