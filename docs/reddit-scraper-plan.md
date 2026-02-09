# Reddit r/soccer Scraper — Future Feature

## Overview
Use https://old.reddit.com/r/soccer/new/ as an additional source of transfer rumours.

## How r/soccer Works as a Source
- Transfer rumour posts typically link to articles from journalists/publications
- Post titles usually contain `[Source Name]` or `(Source Name)` followed by the claim text
- `old.reddit.com` has simple HTML, easy to parse with BeautifulSoup

## Two Approaches

### Option 1: Scrape old.reddit.com HTML
- Simple, no API key needed, same pattern as the BBC gossip scraper
- Filter posts by flair ("Transfer" / "Rumour") or title patterns
- Risk: Reddit may rate-limit or block scrapers

### Option 2: Reddit API (via `praw`)
- More reliable, supports filtering/sorting properly
- Requires creating a Reddit app (free) to get API credentials
- More robust but needs credentials setup

## What the Scraper Would Do
1. Fetch recent posts from r/soccer/new
2. Filter for transfer-related posts (by flair or title patterns like `[Source]` tags + club/player names)
3. Extract journalist/publication from the `[brackets]` in the title
4. Use existing pipeline: `_extract_clubs`, `_extract_players`, `classify_claim_confidence`, `classify_club_direction`
5. Dedup against existing claims (same as gossip scraper)
6. Wire into `scrape_claims` management command as `--sources reddit`

## Key Considerations
- Reddit's content policy allows scraping public pages for non-commercial use, but they've been tightening API access
- HTML scraping (option 1) is simpler but more fragile
- API route (option 2) is more robust but needs credentials
- Need to handle Reddit's rate limits gracefully
- Should add `('reddit', 'Reddit')` to `ScrapedArticle.SOURCE_TYPE_CHOICES`

## Files to Create/Modify
- New: `backend/apps/claims/scrapers/reddit_scraper.py`
- Modify: `backend/apps/claims/management/commands/scrape_claims.py` (add `reddit` source)
- Modify: `backend/apps/claims/models.py` (add reddit source type)
