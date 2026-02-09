# Veracity

A fact-checking platform for football transfer rumours that tracks journalists' claims and scores them on truthfulness and speed.

## Project Overview

Veracity helps football fans determine which journalists are most reliable when it comes to transfer news. The platform:

- Tracks claims made by journalists about player transfers
- Validates claims when transfers are confirmed or denied
- Scores journalists on two axes:
  - **Truthfulness**: Percentage of claims that proved true
  - **Speed**: Percentage of times they were first to break a story

## Tech Stack

### Backend
- **Django 5.0**: Web framework
- **Django REST Framework**: API
- **PostgreSQL**: Database
- **Python 3.10+**

### Frontend (Coming in Phase 3)
- **React 18**: UI framework
- **Vite**: Build tool
- **TanStack Query**: Data fetching
- **Tailwind CSS**: Styling

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip and virtualenv

### Backend Setup

1. **Clone the repository** (or navigate to the veracity directory)
   ```bash
   cd veracity/backend
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update the following:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=veracity
   DB_USER=your-postgres-username
   DB_PASSWORD=your-postgres-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Create the PostgreSQL database**
   ```bash
   # Login to PostgreSQL
   psql -U postgres

   # Create database
   CREATE DATABASE veracity;

   # Exit PostgreSQL
   \q
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Admin panel: http://localhost:8000/admin
   - API (coming soon): http://localhost:8000/api

## Usage

### Adding Journalists

1. Log in to the Django admin at http://localhost:8000/admin
2. Click on "Journalists" > "Add Journalist"
3. Enter journalist details (name, publications, bio, etc.)
4. Save

### Adding Claims

1. In the admin panel, click on "Claims" > "Add Claim"
2. Fill in the claim details:
   - **Journalist**: Select the journalist who made the claim
   - **Claim Text**: The actual statement made
   - **Claim Date**: When the claim was made
   - **Publication**: Where it was published
   - **Article URL**: Link to the source
   - **Player Details**: Player name, clubs, transfer fee
   - **Certainty Level**: How confident was the journalist?
   - **Source Type**: Original scoop or citing another source?
   - **Is First Claim**: Was this journalist first to report?
3. Save

### Validating Claims

1. When a transfer is confirmed or denied, edit the claim
2. Update the **Validation Status**:
   - Confirmed True: The transfer happened as claimed
   - Proven False: The transfer didn't happen
   - Partially True: Some details were correct
3. Add **Validation Notes** and **Validation Source URL**
4. Save - scores will update automatically!

## How Scoring Works

### Truthfulness Score
```
truthfulness_score = (confirmed_true_claims / total_validated_claims) * 100
```

Example: If a journalist made 100 claims, 80 have been validated, and 65 were true:
- Truthfulness Score = (65 / 80) * 100 = 81.25%

### Speed Score
```
speed_score = (first_claims / total_original_scoops) * 100
```

Example: If a journalist had 50 original scoops and was first to report 30 times:
- Speed Score = (30 / 50) * 100 = 60%

### Automatic Updates

Scores are automatically recalculated when:
- A claim's validation status changes
- A claim's `is_first_claim` status changes

## Project Structure

```
veracity/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── apps/
│       └── claims/
│           ├── models.py              # Database models
│           ├── admin.py               # Admin interface
│           ├── signals.py             # Auto-score updates
│           ├── services/
│           │   └── scoring.py         # Scoring algorithms
│           └── migrations/
└── frontend/ (Coming soon)
```

## Database Models

### Journalist
- Basic info (name, publications, bio)
- Cached scores (truthfulness, speed)
- Auto-generated slug for URLs

### Claim
- Journalist who made the claim
- Claim details (text, date, publication, URL)
- Transfer details (player, clubs, fee)
- Claim characteristics (certainty level, source type)
- Validation info (status, date, notes, proof URL)
- Speed tracking (is_first_claim)

### ScoreHistory
- Historical record of journalist scores
- Tracks score changes over time
- Used for analytics and charts

### Transfer
- Groups claims about the same transfer
- Tracks transfer outcome
- Identifies first journalist to report

## Development Status

- [x] Phase 1: Backend Foundation
  - [x] Django project structure
  - [x] Database models
  - [x] Scoring algorithms
  - [x] Admin interface
  - [x] Auto-updating signals
- [ ] Phase 2: REST API
- [ ] Phase 3: Frontend Setup
- [ ] Phase 4: UI Components
- [ ] Phase 5: Pages
- [ ] Phase 6: Polish & Testing

## Next Steps

1. Test the admin interface by adding sample journalists and claims
2. Implement REST API (Phase 2)
3. Build React frontend (Phases 3-5)
4. Add web scraping for automation (Future)

## License

This project is for personal use.

## Contact

Julian Smilg - juliansmilg@gmail.com
