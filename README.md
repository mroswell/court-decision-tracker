# Supreme Court Decision Tracker with AI Analysis

Automatically tracks new Supreme Court decisions and uses Google's Gemini AI to classify them as conservative or liberal.

## What it does:

1. **Fetches** recent Supreme Court opinions from CourtListener (free public database)
2. **Analyzes** each decision using Gemini AI to determine political leaning
3. **Saves** results to a CSV file with:
   - Case name
   - Date filed
   - Classification (Conservative/Liberal/Mixed)
   - Confidence level
   - AI reasoning
   - Link to full opinion

## Setup Instructions:

### 1. Get a Free Gemini API Key

1. Go to https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Copy your API key

### 2. Add Secret to GitHub Repository

1. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `GEMINI_API_KEY`
4. Value: Paste your Gemini API key
5. Click **"Add secret"**

### 3. Set Up the GitHub Action

1. Create folder structure in your repository:
   ```
   .github/workflows/
   ```

2. Copy `supreme-court-tracker.yml` to `.github/workflows/`

3. Copy `supreme_court_analyzer.py` to the root of your repository

4. Commit and push:
   ```bash
   git add .
   git commit -m "Add Supreme Court tracker"
   git push
   ```

### 4. Run It!

**Automatic:** Runs every Monday at 10 AM UTC

**Manual:** 
1. Go to **Actions** tab in GitHub
2. Click "Supreme Court Decision Tracker"
3. Click "Run workflow"

## Output:

Results saved to `supreme_court_decisions.csv`:

| date_filed | case_name | classification | confidence | tags | notes | summary | reasoning | url | analyzed_date |
|------------|-----------|----------------|------------|------|-------|---------|-----------|-----|---------------|
| 2024-06-24 | Dobbs v. Jackson | Very Conservative | High | Fourteenth Amendment;Abortion;State Rights | Fourteenth Amendment - Due process analysis;Abortion - Overturns Roe v Wade;State Rights - Returns regulation to states | The Court was asked whether all pre-viability prohibitions on elective abortions are unconstitutional. The Court held that the Constitution does not confer a right to abortion and overruled Roe v. Wade and Planned Parenthood v. Casey. The majority opinion, written by Justice Alito, argued that the right to abortion is not deeply rooted in the Nation's history and tradition, and therefore not protected under the Fourteenth Amendment's Due Process Clause. | Decision overturns Roe, finding no constitutional right to abortion and returning regulation to states | https://... | 2024-06-25 |

The **summary** field provides a 1-2 paragraph overview including:
- The legal question presented
- What the Court decided
- Key reasoning from the majority opinion

## 5-Point Classification Scale:

- **Very Conservative** - Strongly aligns with conservative legal principles
- **Conservative** - Moderately aligns with conservative principles  
- **Center** - Balanced or doesn't clearly align
- **Liberal** - Moderately aligns with liberal principles
- **Very Liberal** - Strongly aligns with liberal legal principles

## Available Tags (47 total):

**Constitutional Amendments (in order):**
1. First Amendment - Speech, press, religion, assembly, petition
2. Second Amendment - Gun rights
3. Third Amendment - Quartering of soldiers
4. Fourth Amendment - Search and seizure
5. Fifth Amendment - Self-incrimination, due process, eminent domain
6. Sixth Amendment - Right to counsel, jury trials, speedy trial
7. Seventh Amendment - Civil jury trials
8. Eighth Amendment - Cruel and unusual punishment, excessive bail
9. Ninth Amendment - Unenumerated rights
10. Tenth Amendment - Reserved powers to states
11. Eleventh Amendment - Sovereign immunity, state lawsuits
12. Thirteenth Amendment - Abolition of slavery, involuntary servitude
13. Fourteenth Amendment - Equal protection, due process, citizenship
14. Fifteenth Amendment - Voting rights (race)
15. Sixteenth Amendment - Income tax
16. Nineteenth Amendment - Women's voting rights
17. Twenty-First Amendment - Alcohol regulation
18. Twenty-Fourth Amendment - Poll tax prohibition
19. Twenty-Sixth Amendment - Voting age (18)

**Other Legal Topics (alphabetical):**
20. Abortion
21. Administrative Law - Agency power, regulations
22. Antitrust - Monopolies, competition
23. Bankruptcy
24. Business/Commerce - Corporate law, contracts
25. Capital Punishment - Death penalty cases
26. Civil Rights - Discrimination, equality
27. Criminal Justice - Sentencing, procedure
28. Education - Schools, student rights
29. Election Law - Campaign finance, redistricting
30. Employment - Labor, workplace rights
31. Environment - EPA, climate, pollution
32. Family Law - Marriage, custody, adoption
33. Federal Power - Scope of federal authority
34. Healthcare - Medical law, insurance
35. Immigration - Deportation, asylum, borders
36. Intellectual Property - Patents, copyright, trademarks
37. International Law - Treaties, foreign relations
38. LGBTQ Rights - Marriage equality, discrimination
39. Native American Law - Tribal sovereignty, treaties
40. National Security - War powers, military, surveillance
41. Police Power - Qualified immunity, police conduct
42. Privacy - Data, surveillance, personal rights
43. Property Rights - Takings, land use
44. State Rights - Federalism, state sovereignty
45. Taxation - Tax law, IRS
46. Technology - Internet, social media, AI
47. Voting Rights - Access, restrictions, gerrymandering

**Tags** are semicolon-delimited (e.g., `First Amendment;Free Speech;Technology`)

**Notes** provide context for each tag with semicolon-delimited descriptions (e.g., `First Amendment - Social media regulation;Technology - Platform content moderation`)

## View Your Data:

The CSV file will be automatically committed to your repository after each run. You can:
- Download it
- View it on GitHub
- Import into Google Sheets
- Visualize with Python/R

## Free API Limits:

- **CourtListener API:** Free, no key required, generous limits
- **Gemini API:** Free tier = 60 requests/minute, plenty for this use case

## Troubleshooting:

**No decisions found:**
- The Supreme Court doesn't release opinions every week
- Try running manually or check back during court session (Oct-June)

**API errors:**
- Check that your GEMINI_API_KEY secret is set correctly
- Make sure you haven't exceeded free tier limits

**CSV not updating:**
- Check the Actions tab for error logs
- Make sure the workflow has write permissions

## How the AI Analysis Works:

The script sends each decision text to Gemini with instructions to:
1. Identify conservative legal principles (strict originalism, limiting federal power, etc.)
2. Identify liberal legal principles (broad interpretation, civil rights expansion, etc.)
3. Classify on a 5-point scale: Very Conservative → Conservative → Center → Liberal → Very Liberal
4. Select all applicable tags from 47 topics (19 Amendments + 28 legal topics)
5. Provide notes explaining how each tag applies to the case
6. Give confidence level and reasoning

## Educational Value:

Students learn about:
- ✅ GitHub Actions automation
- ✅ Working with government APIs
- ✅ AI prompt engineering
- ✅ Data collection and analysis
- ✅ Political science + technology
- ✅ CSV data manipulation

## Data Source:

**CourtListener** by Free Law Project - a non-profit creating open legal data
- Website: https://www.courtlistener.com/
- All Supreme Court opinions are public domain

## Extend This Project:

- Add sentiment analysis of dissenting opinions
- Track which justices wrote majority/dissent
- Compare AI classification vs legal expert opinions
- Create visualizations of court trends over time
- Build a website to display results

## License:

Public domain - use for educational purposes!
