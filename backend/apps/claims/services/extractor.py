import json
import logging

import anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
You are a football transfer news analyst. Analyze the following article and extract \
any transfer-related claims made by journalists.

For each transfer claim found, extract:
- journalist_name: The journalist making or being cited for the claim
- claim_text: A concise summary of the claim (1-2 sentences)
- player_name: The player involved
- from_club: The player's current/selling club (if mentioned)
- to_club: The destination/buying club (if mentioned)
- transfer_fee: The reported fee (if mentioned, e.g. "50M", "Free transfer")
- certainty_level: One of "tier_1_done_deal", "tier_2_advanced", "tier_3_active", \
"tier_4_concrete_interest", "tier_5_early_intent", "tier_6_speculation"
- source_type: "original" if this journalist is breaking the news, "citing" if they are \
reporting another journalist's claim
- cited_journalist: If source_type is "citing", the name of the original journalist

Rules:
- Only extract claims about player transfers, loans, or contract negotiations
- If no transfer claims are found, return an empty claims array
- Be precise with player and club names
- Determine certainty from language: "done deal"/"signed"/"here we go" = tier_1_done_deal, \
"close to signing"/"expected to sign"/"agreed terms" = tier_2_advanced, \
"in talks"/"bid submitted"/"sources say" = tier_3_active, \
"interested"/"target"/"tracking" = tier_4_concrete_interest, \
"eyeing"/"considering"/"looking at" = tier_5_early_intent, \
"linked with"/"rumoured"/"could"/"might" = tier_6_speculation

Publication: {publication}
Known journalist: {journalist_name}

Article text:
{article_text}

Respond with ONLY valid JSON in this exact format:
{{"claims": [...]}}
"""


class ClaudeExtractor:
    """Extracts structured transfer claims from article text using Claude API."""

    def __init__(self):
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured in settings.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_claims(
        self,
        article_text: str,
        publication: str = '',
        journalist_name: str = '',
    ) -> list[dict]:
        """Extract transfer claims from article text.

        Returns a list of claim dicts, or empty list if no claims found.
        """
        if not article_text.strip():
            return []

        # Truncate very long articles to stay within token limits
        truncated = article_text[:15000]

        prompt = EXTRACTION_PROMPT.format(
            publication=publication or 'Unknown',
            journalist_name=journalist_name or 'Unknown',
            article_text=truncated,
        )

        try:
            message = self.client.messages.create(
                model='claude-sonnet-4-5-20250929',
                max_tokens=4096,
                temperature=0,
                messages=[{'role': 'user', 'content': prompt}],
            )

            response_text = message.content[0].text.strip()

            # Handle potential markdown code blocks
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])

            data = json.loads(response_text)
            claims = data.get('claims', [])

            logger.info("Extracted %d claims from article", len(claims))
            return claims

        except json.JSONDecodeError:
            logger.exception("Failed to parse Claude response as JSON")
            return []
        except anthropic.APIError:
            logger.exception("Claude API error during claim extraction")
            return []
