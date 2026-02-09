# Veracity API Documentation

Base URL: `http://localhost:8000/api/`

## Overview

The Veracity API provides access to journalist claims, scores, and leaderboards. All endpoints return JSON responses and support pagination where applicable.

---

## Authentication

Currently, the API is **read-only** and does not require authentication. All endpoints are publicly accessible.

---

## Endpoints

### 1. API Root

**GET** `/api/`

Returns a list of all available endpoints.

**Response:**
```json
{
    "journalists": "http://localhost:8000/api/journalists/",
    "claims": "http://localhost:8000/api/claims/",
    "score-history": "http://localhost:8000/api/score-history/",
    "transfers": "http://localhost:8000/api/transfers/"
}
```

---

## Journalists

### List Journalists

**GET** `/api/journalists/`

Get a list of all journalists with their scores.

**Query Parameters:**
- `search` - Search by name, publications, or Twitter handle
- `ordering` - Sort by field (prefix with `-` for descending)
  - `truthfulness_score` (default: `-truthfulness_score`)
  - `speed_score`
  - `name`
  - `created_at`
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 20)

**Example:**
```bash
GET /api/journalists/?ordering=-speed_score&page_size=10
```

**Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Fabrizio Romano",
            "slug": "fabrizio-romano",
            "truthfulness_score": "100.00",
            "speed_score": "100.00",
            "publications": ["The Guardian", "Sky Sports"],
            "twitter_handle": "@FabrizioRomano",
            "profile_image_url": null,
            "total_claims": 2
        }
    ]
}
```

---

### Get Journalist Details

**GET** `/api/journalists/{slug}/`

Get detailed information about a specific journalist.

**Example:**
```bash
GET /api/journalists/fabrizio-romano/
```

**Response:**
```json
{
    "id": 1,
    "name": "Fabrizio Romano",
    "slug": "fabrizio-romano",
    "bio": "Italian football journalist...",
    "publications": ["The Guardian", "Sky Sports"],
    "twitter_handle": "@FabrizioRomano",
    "profile_image_url": null,
    "truthfulness_score": "100.00",
    "speed_score": "100.00",
    "accuracy_rate": "100.00",
    "total_claims": 2,
    "validated_claims": 1,
    "pending_claims": 1,
    "true_claims": 1,
    "false_claims": 0,
    "partially_true_claims": 0,
    "original_scoops": 2,
    "first_to_report_count": 2,
    "created_at": "2026-02-08T00:13:17.600945Z",
    "updated_at": "2026-02-08T00:13:17.622116Z"
}
```

---

### Get Journalist Score History

**GET** `/api/journalists/{slug}/score_history/`

Get historical score data for charts (last 30 records).

**Example:**
```bash
GET /api/journalists/fabrizio-romano/score_history/
```

**Response:**
```json
[
    {
        "id": 1,
        "journalist": 1,
        "journalist_name": "Fabrizio Romano",
        "truthfulness_score": "100.00",
        "speed_score": "100.00",
        "total_claims": 2,
        "validated_claims": 1,
        "true_claims": 1,
        "false_claims": 0,
        "original_scoops": 2,
        "recorded_at": "2026-02-08T00:13:17.622116Z"
    }
]
```

---

### Get Journalist Claims

**GET** `/api/journalists/{slug}/claims/`

Get all claims made by a specific journalist.

**Query Parameters:**
- `status` - Filter by validation status: `pending`, `confirmed_true`, `proven_false`, `partially_true`

**Example:**
```bash
GET /api/journalists/fabrizio-romano/claims/?status=confirmed_true
```

---

### Get Leaderboard

**GET** `/api/journalists/leaderboard/`

Get ranked journalists for leaderboards.

**Query Parameters:**
- `score_type` - Type of score: `truthfulness` (default) or `speed`
- `limit` - Number of results (default: 20)

**Example:**
```bash
GET /api/journalists/leaderboard/?score_type=speed&limit=10
```

**Response:**
```json
[
    {
        "rank": 1,
        "journalist": {
            "id": 1,
            "name": "Fabrizio Romano",
            "slug": "fabrizio-romano",
            "truthfulness_score": "100.00",
            "speed_score": "100.00",
            "publications": ["The Guardian", "Sky Sports"],
            "twitter_handle": "@FabrizioRomano",
            "profile_image_url": null,
            "total_claims": 2
        },
        "score": 100.0,
        "score_type": "speed"
    }
]
```

---

## Claims

### List Claims

**GET** `/api/claims/`

Get a list of all claims.

**Query Parameters:**
- `validation_status` - Filter by status: `pending`, `confirmed_true`, `proven_false`, `partially_true`
- `certainty_level` - Filter by certainty: `confirmed`, `sources_say`, `rumoured`, `speculation`
- `source_type` - Filter by source: `original`, `citing`
- `journalist` - Filter by journalist ID
- `is_first_claim` - Filter by first claim: `true` or `false`
- `claim_date__gte` - Filter claims after date (ISO format)
- `claim_date__lte` - Filter claims before date (ISO format)
- `search` - Search in claim text, player name, clubs
- `ordering` - Sort by field: `claim_date` (default: `-claim_date`), `validation_date`, `created_at`

**Example:**
```bash
GET /api/claims/?validation_status=confirmed_true&ordering=-claim_date
```

**Response:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "journalist": 1,
            "journalist_name": "Fabrizio Romano",
            "journalist_slug": "fabrizio-romano",
            "cited_journalist": null,
            "cited_journalist_name": null,
            "cited_journalist_slug": null,
            "claim_text": "Jude Bellingham to Real Madrid...",
            "publication": "The Guardian",
            "article_url": "https://example.com/...",
            "claim_date": "2025-11-10T00:13:17.608226Z",
            "player_name": "Jude Bellingham",
            "from_club": "Borussia Dortmund",
            "to_club": "Real Madrid",
            "transfer_fee": "£88.5m",
            "certainty_level": "confirmed",
            "certainty_level_display": "Confirmed",
            "source_type": "original",
            "source_type_display": "Original Scoop",
            "validation_status": "confirmed_true",
            "validation_status_display": "Confirmed True",
            "validation_date": "2025-12-10T00:13:17.608234Z",
            "validation_notes": "Transfer confirmed...",
            "validation_source_url": "",
            "is_first_claim": true,
            "created_at": "2026-02-08T00:13:17.608383Z",
            "updated_at": "2026-02-08T00:13:17.608387Z"
        }
    ]
}
```

---

### Get Claim Details

**GET** `/api/claims/{id}/`

Get detailed information about a specific claim.

**Example:**
```bash
GET /api/claims/1/
```

---

### Get Latest Claims

**GET** `/api/claims/latest/`

Get the 20 most recent claims (for homepage feed).

**Example:**
```bash
GET /api/claims/latest/
```

---

### Get Pending Claims

**GET** `/api/claims/pending/`

Get all claims awaiting validation.

**Example:**
```bash
GET /api/claims/pending/
```

---

### Get Validated Claims

**GET** `/api/claims/validated/`

Get all validated claims (true or false).

**Example:**
```bash
GET /api/claims/validated/
```

---

### Get Claims Statistics

**GET** `/api/claims/stats/`

Get aggregate statistics across all claims.

**Example:**
```bash
GET /api/claims/stats/
```

**Response:**
```json
{
    "total_claims": 5,
    "pending_claims": 2,
    "validated_claims": 3,
    "true_claims": 2,
    "false_claims": 1,
    "accuracy_rate": 66.67,
    "total_journalists": 3
}
```

---

## Score History

### List Score History

**GET** `/api/score-history/`

Get historical score records (for analytics).

**Query Parameters:**
- `journalist` - Filter by journalist ID
- `ordering` - Sort by field (default: `-recorded_at`)

**Example:**
```bash
GET /api/score-history/?journalist=1
```

---

## Transfers

### List Transfers

**GET** `/api/transfers/`

Get grouped transfers (future feature).

**Query Parameters:**
- `completed` - Filter by completion: `true` or `false`
- `transfer_window` - Filter by transfer window
- `search` - Search player name, clubs

**Example:**
```bash
GET /api/transfers/?completed=true
```

---

## Pagination

All list endpoints support pagination with the following response format:

```json
{
    "count": 100,
    "next": "http://localhost:8000/api/claims/?page=2",
    "previous": null,
    "results": [...]
}
```

**Query Parameters:**
- `page` - Page number
- `page_size` - Results per page (max: 100)

---

## Error Responses

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 400 Bad Request
```json
{
    "field_name": [
        "Error message"
    ]
}
```

---

## Rate Limiting

Currently, there is no rate limiting. This may be added in production.

---

## CORS

The API supports CORS for the following origins:
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173`

---

## Browsable API

You can explore the API interactively in your browser:

1. Visit `http://localhost:8000/api/` in your browser
2. Click through the endpoints to see responses
3. Django REST Framework provides a user-friendly interface

---

## Example Usage with JavaScript

```javascript
// Fetch leaderboard
const response = await fetch('http://localhost:8000/api/journalists/leaderboard/?score_type=truthfulness');
const leaderboard = await response.json();

// Fetch journalist details
const journalist = await fetch('http://localhost:8000/api/journalists/fabrizio-romano/');
const data = await journalist.json();

// Fetch latest claims
const claims = await fetch('http://localhost:8000/api/claims/latest/');
const latestClaims = await claims.json();

// Filter claims
const trueClaims = await fetch('http://localhost:8000/api/claims/?validation_status=confirmed_true');
const results = await trueClaims.json();
```

---

## Next Steps

Ready for Phase 3: Frontend development with React!
