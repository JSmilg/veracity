import logging
from datetime import datetime, timedelta, timezone

from django.conf import settings

from .base import Article, BaseScraper

logger = logging.getLogger(__name__)

TARGET_ACCOUNTS = {
    'FabrizioRomano': 'Fabrizio Romano',
    'David_Ornstein': 'David Ornstein',
    'Plettigoal': 'Florian Plettenberg',
    'MatteMoretto': 'Matteo Moretto',
    'JacobsBen': 'Ben Jacobs',
}


class TwitterScraper(BaseScraper):
    """Scrapes tweets from target journalists. Requires TWITTER_BEARER_TOKEN."""

    def __init__(self, accounts: dict[str, str] | None = None):
        self.accounts = accounts or TARGET_ACCOUNTS

    def fetch_articles(self) -> list[Article]:
        bearer_token = getattr(settings, 'TWITTER_BEARER_TOKEN', '')
        if not bearer_token:
            logger.warning(
                "TWITTER_BEARER_TOKEN not configured. Skipping Twitter scraping."
            )
            return []

        try:
            import tweepy
        except ImportError:
            logger.warning("tweepy not installed. Skipping Twitter scraping.")
            return []

        client = tweepy.Client(bearer_token=bearer_token)
        all_articles = []

        start_time = datetime.now(timezone.utc) - timedelta(days=7)

        for handle, journalist_name in self.accounts.items():
            try:
                articles = self._fetch_user_tweets(
                    client, handle, journalist_name, start_time
                )
                all_articles.extend(articles)
                logger.info("Fetched %d tweets from @%s", len(articles), handle)
            except Exception:
                logger.exception("Error fetching tweets from @%s", handle)

        return self.filter_transfer_articles(all_articles)

    def _fetch_user_tweets(
        self, client, handle: str, journalist_name: str, start_time: datetime
    ) -> list[Article]:
        # Look up user ID
        user = client.get_user(username=handle)
        if not user.data:
            logger.warning("Twitter user not found: @%s", handle)
            return []

        user_id = user.data.id

        tweets = client.get_users_tweets(
            id=user_id,
            start_time=start_time.isoformat(),
            max_results=100,
            exclude=['retweets', 'replies'],
            tweet_fields=['created_at', 'text'],
        )

        if not tweets.data:
            return []

        articles = []
        for tweet in tweets.data:
            tweet_url = f"https://twitter.com/{handle}/status/{tweet.id}"
            articles.append(Article(
                url=tweet_url,
                title=f"Tweet by @{handle}",
                content=tweet.text,
                source_name=f"Twitter @{handle}",
                source_type='twitter',
                published_at=tweet.created_at,
                journalist_name=journalist_name,
            ))

        return articles
