"""Classifiers for transfer rumour claims.

- 6-tier confidence classifier (classify_claim_confidence)
- Club direction classifier (classify_club_direction)
"""

import re

TIER_PHRASES = {
    'tier_1_done_deal': [
        'here we go',
        'done deal',
        'deal completed',
        'deal done',
        'transfer completed',
        'transfer confirmed',
        'officially announced',
        'official announcement',
        'has signed',
        'have signed',
        'has completed',
        'have completed',
        'medical completed',
        'passed his medical',
        'passed medical',
        'medical done',
        'contract signed',
        'signed a contract',
        'signed his contract',
        'signed a new',
        'put pen to paper',
        'deal is done',
        'deal agreed and signed',
        'confirmed the signing',
        'confirm the signing',
        'confirmed the transfer',
        'confirm the transfer',
        'completed his move',
        'completed her move',
        'completed the transfer',
        'completed a move',
        'joins on a permanent',
        'officially joins',
        'announced as',
        'unveiled as',
        'agreed a deal',
        'agreed a fee',
        'agreed a move',
        'agreed a transfer',
        'agreed to sign',
        'agreed to sell',
        'agreed to buy',
        'agreed to send',
        'agreed to pay',
        'agreed to loan',
        'deal agreed',
        'jumped at the chance to join',
        'made the move',
    ],
    'tier_2_advanced': [
        'close to signing',
        'close to completing',
        'close to agreeing',
        'close to finalising',
        'close to sealing',
        'on the verge of',
        'set to sign',
        'set to complete',
        'set to join',
        'set to leave',
        'expected to sign',
        'expected to complete',
        'expected to join',
        'will sign',
        'will complete',
        'will join',
        'agreed personal terms',
        'personal terms agreed',
        'terms agreed',
        'fee agreed',
        'total agreement',
        'full agreement',
        'agreement reached',
        'agreement in place',
        'medical scheduled',
        'medical booked',
        'set for medical',
        'due to have medical',
        'travelling for medical',
        'undergo a medical',
        'final details',
        'finalising deal',
        'finalising the deal',
        'deal is close',
        'almost done',
        'imminent',
        'all but done',
        'a matter of time',
        'formalities away',
        'decided to make',
        'in pole position',
        'confident of getting',
        'confident they will',
        'confident of resolving',
        'loan move permanent',
        'make the move permanent',
        'made the move permanent',
    ],
    'tier_3_active': [
        'in negotiations',
        'in talks',
        'in advanced talks',
        'in discussions',
        'negotiating',
        'bid submitted',
        'bid accepted',
        'bid rejected',
        'bid turned down',
        'offer submitted',
        'offer accepted',
        'offer rejected',
        'offer turned down',
        'made a bid',
        'made an offer',
        'made an approach',
        'made contact',
        'tabled a bid',
        'tabled an offer',
        'tabled',
        'submitted a bid',
        'submitted an offer',
        'submitted',
        'formal offer',
        'formal bid',
        'opening bid',
        'set to offer',
        'preparing a bid',
        'preparing an offer',
        'ready to bid',
        'working on a deal',
        'trying to sign',
        'trying to agree',
        'pushing to sign',
        'pushing for a deal',
        'pushing for',
        'progressing',
        'talks ongoing',
        'talks underway',
        'talks have begun',
        'turned down',
        'rejected',
        'knocked back',
        'understand',
        'sources say',
        'approached',
        'enquired',
        'have enquired',
        'given permission',
    ],
    'tier_4_concrete_interest': [
        'interested in',
        'interested in signing',
        'expressed interest',
        'express interest',
        'shown interest',
        'showing interest',
        'concrete interest',
        'strong interest',
        'genuine interest',
        'serious interest',
        'stepping up interest',
        'stepping up their interest',
        'ramping up',
        'keen on',
        'keen to sign',
        'want to sign',
        'wants to sign',
        'want to bring',
        'wants to bring',
        'target',
        'targeting',
        'have targeted',
        'tracking',
        'scouting',
        'have scouted',
        'monitoring',
        'closely monitoring',
        'watching',
        'keeping tabs',
        'on their radar',
        'on the radar',
        'shortlisted',
        'on the shortlist',
        'identified as a target',
        'have identified',
        'admirers',
        'joined the growing',
        'joined the race',
        'joined the battle',
        'entered the race',
        'enter the race',
        'in the race',
        'in the hunt',
        'leading the race',
        'frontrunners',
        'front-runners',
        'in the market for',
        'set their sights',
        'are hopeful',
        'remain hopeful',
        'priority',
        'prioritising',
        'turned their attention',
    ],
    'tier_5_early_intent': [
        'eyeing',
        'eyeing a move',
        'eyeing up',
        'considering',
        'considering a move',
        'weighing up',
        'lining up',
        'lining up a move',
        'planning a move',
        'could move for',
        'could sign',
        'could make a move',
        'could target',
        'may move for',
        'may sign',
        'may target',
        'might move for',
        'might sign',
        'might target',
        'exploring',
        'exploring a deal',
        'looking at',
        'looking to sign',
        'looking to bring',
        'being looked at',
        'contemplating',
        'assessing',
        'open to signing',
        'open to a move',
        'willing to listen',
        'willing to sell',
        'prepared to sell',
        'prepared to listen',
        'available for',
        'on the market',
        'hoping to',
        'hope to sign',
        'hoping to sign',
        'hoping to strike',
        'want',
    ],
    'tier_6_speculation': [
        'linked with',
        'linked to',
        'has been linked',
        'have been linked',
        'rumoured',
        'rumoured to',
        'rumours linking',
        'rumours suggest',
        'touted',
        'touted as',
        'touted for',
        'tipped to',
        'tipped for',
        'could be an option',
        'an option for',
        'a possibility',
        'dream signing',
        'dream target',
        'wish list',
        'wishlist',
        'among the candidates',
        'one of the candidates',
        'in the frame',
        'in the running',
        'believed to',
        'thought to',
        'said to',
        'understood to',
        'reportedly',
        'according to reports',
        'speculation',
    ],
}

# Sort phrases longest-first within each tier so longer matches take priority
for _tier, _phrases in TIER_PHRASES.items():
    _phrases.sort(key=len, reverse=True)

# Regex-based tier patterns for phrases that need wildcard matching
_TIER_REGEX = {
    'tier_1_done_deal': [
        re.compile(r'decided to make.*permanent', re.IGNORECASE),
    ],
    'tier_2_advanced': [
        re.compile(r'make.*permanent', re.IGNORECASE),
    ],
}


def classify_claim_confidence(text: str) -> str:
    """Classify claim text into a 6-tier confidence taxonomy.

    On multi-tier matches, returns the LOWEST confidence tier (conservative).
    i.e. the highest tier number wins.

    Returns one of:
        tier_1_done_deal, tier_2_advanced, tier_3_active,
        tier_4_concrete_interest, tier_5_early_intent, tier_6_speculation
    """
    lower = text.lower()
    matched_tiers = set()

    for tier, phrases in TIER_PHRASES.items():
        for phrase in phrases:
            if phrase in lower:
                matched_tiers.add(tier)
                break  # One match per tier is enough

    # Check regex-based patterns
    for tier, patterns in _TIER_REGEX.items():
        if tier not in matched_tiers:
            for pattern in patterns:
                if pattern.search(lower):
                    matched_tiers.add(tier)
                    break

    if not matched_tiers:
        return 'tier_6_speculation'

    # Highest tier number = lowest confidence = most conservative
    return max(matched_tiers)


# ---------------------------------------------------------------------------
# Club direction classifier — determines FROM (selling) vs TO (buying) clubs
# ---------------------------------------------------------------------------

# Patterns where the club BEFORE the keyword is the selling side (FROM)
_SELLING_AFTER_CLUB = [
    r'are open to allowing .{0,40} to leave',
    r'willing to sell',
    r'prepared to sell',
    r'could sell',
    r'ready to sell',
    r'want .{0,20} for',
    r'are demanding',
    r'are willing to let .{0,30} go',
    r'reject(?:ed)? (?:a |the )?bid',
    r'turned down (?:a |the )?bid',
    r'turned down (?:a |an )?offer',
    r'have rejected',
    r'set to release',
    r'looking to offload',
    r'open to offers',
    r'open to letting',
    r'prepared to let .{0,30} go',
    r'willing to listen to offers',
    r'could (?:let|allow) .{0,30} (?:leave|go)',
    r"'s (?:forward|midfielder|defender|goalkeeper|striker|winger|star|player)",
    r'open to sending',
    r'look(?:ing)? for buyers',
    r'set to look for buyers',
    r'want(?:s)? to offload',
    r'trying to move .{0,30} on',
    r'trying to offload',
    r'ready to let .{0,30} (?:leave|go)',
    r'could be sold',
    r'could be offloaded',
    r'available for transfer',
    r'(?:ward|fend) off interest',
    r'have offered',
    r'offered .{0,40} to\b',
    r'have accepted .{0,20} offer',
    r'accepted .{0,20} offer',
    r'accepted .{0,20} bid',
]

# Long-range selling patterns (checked with a wider context window)
_SELLING_AFTER_LONG = [
    r'are planning to offer .{0,80} (?:a )?(?:new |lucrative )?contract',
    r'(?:planning|looking) to (?:offer|give) .{0,80} (?:a )?(?:new |lucrative )?(?:contract|deal)',
]
_SELLING_AFTER_LONG_RE = [(re.compile(p, re.IGNORECASE), -1) for p in _SELLING_AFTER_LONG]

# Patterns where the club BEFORE the keyword is the buying side (TO)
_BUYING_AFTER_CLUB = [
    r'are interested in',
    r'interested in signing',
    r'want to sign',
    r'wants to sign',
    r'keen on',
    r'keen to sign',
    r'targeting',
    r'tracking',
    r'keeping tabs on',
    r'scouting',
    r'monitoring',
    r'are trying to sign',
    r'pushing for',
    r'plotting',
    r'have made (?:a |an )?(?:bid|offer)',
    r'made (?:a |an )?(?:bid|offer)',
    r'tabled (?:a |an )?(?:bid|offer)',
    r'preparing (?:a |an )?(?:bid|offer)',
    r'eyeing',
    r'considering (?:a move for|signing)',
    r'lining up',
    r'looking to sign',
    r'looking to bring',
    r'are looking for',
    r'\btrying\b',
    r'hoping to sign',
    r'in the race for',
    r'in the hunt for',
    r'entered the race for',
    r'joined the race for',
    r'leading the race for',
    r'set their sights on',
    r"'s .{0,25}(?:targets|target list|radar|shortlist|wishlist|wish list)",
    r"'s (?:offer|bid)",
]

# Patterns where the club AFTER the keyword is the buying side (TO)
# Anchored to end ($) so they only match immediately before the club name
_BUYING_BEFORE_CLUB = [
    r'join $',
    r'move to $',
    r'sign for $',
    r'switch to $',
    r'transfer to $',
    r'heading to $',
    r'set to join $',
    r'expected to join $',
    r'close to joining $',
    r'(?:bid|offer) from $',
    r'wanted by $',
    r'sought by $',
    r'targeted by $',
    r'interest from $',
    r'interest of $',
    r'interesting $',
    r'sending .{0,60}to $',
    r'loan .{0,40}to $',
    r'sell .{0,40}to $',
    r'offered .{0,60}to $',
]

# Patterns where the club AFTER the keyword is the selling side (FROM)
# Anchored to end ($) so they only match immediately before the club name
_SELLING_BEFORE_CLUB = [
    r'leave $',
    r'exit $',
    r'depart $',
    r'quit $',
    r'set to leave $',
    r'expected to leave $',
    r'not (?:be )?staying at $',
    r'will not stay at $',
    r'loan (?:spell|deal|move) at $',
]

# Phrases that mark subsequent clubs as destinations (TO)
_DESTINATION_PHRASES = [
    'possible destinations',
    'potential destinations',
    'among the interested clubs',
    'among those interested',
]

# Compile patterns once
_SELLING_AFTER_RE = [(re.compile(p, re.IGNORECASE), -1) for p in _SELLING_AFTER_CLUB]
_BUYING_AFTER_RE = [(re.compile(p, re.IGNORECASE), +1) for p in _BUYING_AFTER_CLUB]
_BUYING_BEFORE_RE = [(re.compile(p, re.IGNORECASE), +1) for p in _BUYING_BEFORE_CLUB]
_SELLING_BEFORE_RE = [(re.compile(p, re.IGNORECASE), -1) for p in _SELLING_BEFORE_CLUB]

_CONTEXT_WINDOW = 80


def classify_club_direction(text: str, clubs: list[str]) -> tuple[str, str]:
    """Determine from_club and to_club from claim text and extracted clubs.

    Uses keyword proximity scoring: for each club, checks surrounding context
    for selling (FROM) vs buying (TO) language.

    Returns (from_club, to_club) where to_club may be comma-separated for
    multiple destination clubs.
    """
    if not clubs:
        return ('', '')

    lower = text.lower()

    if len(clubs) == 1:
        # Single club — check for selling/leaving language to determine direction
        club = clubs[0]
        club_lower = club.lower()
        _leaving_patterns = [
            rf'(?:set to|expected to|wants to|looking to|hoping to|ready to)\s+leave\s+{re.escape(club_lower)}',
            rf'leave\s+{re.escape(club_lower)}',
            rf'depart(?:ing|s|)\s+{re.escape(club_lower)}',
            rf'exit(?:ing|s|)\s+{re.escape(club_lower)}',
            rf'(?:leaving|left)\s+{re.escape(club_lower)}',
            rf'{re.escape(club_lower)}.*\b(?:departure|exit)',
            rf'(?:out of|away from)\s+{re.escape(club_lower)}',
        ]
        for pat in _leaving_patterns:
            if re.search(pat, lower):
                return (club, '')
        # Check selling-after patterns (e.g. "Club prepared to sell")
        pos = lower.find(club_lower)
        if pos != -1:
            end = pos + len(club_lower)
            after = lower[end:end + _CONTEXT_WINDOW]
            for pattern, score in _SELLING_AFTER_RE:
                if pattern.search(after):
                    return (club, '')
        # Default: single club is the interested/buying party
        return ('', club)

    # Detect "former [Club]" / "ex-[Club]" — these clubs should be neutralised
    former_clubs: set[str] = set()
    for club in clubs:
        club_lower = club.lower()
        if re.search(rf'\bformer\s+{re.escape(club_lower)}\b', lower):
            former_clubs.add(club)
        if re.search(rf'\bex-{re.escape(club_lower)}\b', lower):
            former_clubs.add(club)
        if re.search(rf'\bold\s+{re.escape(club_lower)}\b', lower):
            former_clubs.add(club)

    # Score each club: negative = selling (FROM), positive = buying (TO)
    scores: dict[str, float] = {club: 0.0 for club in clubs}

    for club in clubs:
        # Former clubs get zero score — they are neither from nor to
        if club in former_clubs:
            continue

        club_lower = club.lower()
        # Find all positions of this club in the text
        start = 0
        positions = []
        while True:
            idx = lower.find(club_lower, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + 1

        if not positions:
            continue

        for pos in positions:
            # Skip this occurrence if it's preceded by "former"/"ex-"
            before_check = lower[max(0, pos - 10):pos]
            if re.search(r'\bformer\s+$', before_check) or before_check.rstrip().endswith('ex-'):
                continue
            end = pos + len(club_lower)
            # Context window after the club name
            after_context = lower[end:end + _CONTEXT_WINDOW]
            # Context window before the club name
            before_start = max(0, pos - _CONTEXT_WINDOW)
            before_context = lower[before_start:pos]

            # Check "club + selling pattern" (club is FROM)
            for pattern, score in _SELLING_AFTER_RE:
                if pattern.search(after_context):
                    scores[club] += score
                    break

            # Check long-range selling patterns (wider context window)
            long_after = lower[end:end + 140]
            for pattern, score in _SELLING_AFTER_LONG_RE:
                if pattern.search(long_after):
                    scores[club] += score
                    break

            # Check "club + buying pattern" (club is TO)
            for pattern, score in _BUYING_AFTER_RE:
                if pattern.search(after_context):
                    scores[club] += score
                    break

            # Check "buying keyword + club" (club is TO)
            for pattern, score in _BUYING_BEFORE_RE:
                if pattern.search(before_context):
                    scores[club] += score
                    break

            # Check "selling keyword + club" (club is FROM)
            for pattern, score in _SELLING_BEFORE_RE:
                if pattern.search(before_context):
                    scores[club] += score
                    break

            # "[Club] forward/midfielder/skipper/..." (immediately after) = current club (FROM)
            immediate = lower[end:end + 15]
            if re.match(
                r'\s+(?:forward|midfielder|defender|goalkeeper|striker|winger|star|player|skipper|captain)\b',
                immediate,
            ):
                scores[club] -= 1

            # "[Club]'s [age]-year-old" or "[Club]'s [position]" = current club (FROM)
            # BBC text sometimes has a space before 's: "Manchester City 's"
            possessive = lower[end:end + 30]
            if re.match(
                r"\s?'s\s+\d{1,2}-year-old\b",
                possessive,
            ) or re.match(
                r"\s?'s\s+(?:forward|midfielder|defender|goalkeeper|striker|winger|star|captain|skipper)\b",
                possessive,
            ):
                scores[club] -= 1.5  # Strong signal: possessive = current club

            # Destination phrase appears shortly after club (e.g. "Juve, Napoli and Roma possible destinations")
            for phrase in _DESTINATION_PHRASES:
                if phrase in lower[end:end + _CONTEXT_WINDOW]:
                    scores[club] += 1
                    break

    # Conjunction propagation: "Arsenal and Manchester United" sharing a signal
    # If a club with score 0 is adjacent (via and/or/,) to a scored club, inherit
    for club in clubs:
        if club in former_clubs or scores[club] != 0:
            continue
        club_lower = club.lower()
        pos = lower.find(club_lower)
        if pos == -1:
            continue
        # Check what comes before this club: ", " or "and " or "or "
        before_snippet = lower[max(0, pos - 5):pos]
        if not re.search(r'(?:,\s*|and\s+|or\s+)$', before_snippet):
            continue
        # Find the nearest scored club that appears before this one
        for other in clubs:
            if other == club or other in former_clubs or scores[other] == 0:
                continue
            other_lower = other.lower()
            other_pos = lower.find(other_lower)
            if other_pos == -1 or other_pos >= pos:
                continue
            # Check they're close and connected
            gap = lower[other_pos + len(other_lower):pos]
            if re.match(r'^[\s,]*(?:and|or)?\s*$', gap):
                scores[club] = scores[other]
                break

    # Determine from_club and to_club based on scores
    from_clubs = []
    to_clubs = []

    for club in clubs:
        # Former clubs are excluded from direction assignment entirely
        if club in former_clubs:
            continue
        if scores[club] < 0:
            from_clubs.append(club)
        elif scores[club] > 0:
            to_clubs.append(club)

    # If we got clear signals, use them
    # Exclude former clubs from remaining pools
    active_clubs = [c for c in clubs if c not in former_clubs]

    if from_clubs or to_clubs:
        # If no explicit from but we have to, pick the most negative unassigned
        if not from_clubs and to_clubs:
            remaining = [c for c in active_clubs if c not in to_clubs]
            if remaining:
                from_clubs = [min(remaining, key=lambda c: scores[c])]
        if not to_clubs and from_clubs:
            remaining = [c for c in active_clubs if c not in from_clubs]
            to_clubs = remaining

        from_club = ', '.join(from_clubs) if from_clubs else ''
        to_club = ', '.join(to_clubs) if to_clubs else ''
        return (from_club, to_club)

    # Fallback: no signals detected — use positional heuristic (first = to, second = from)
    # Only consider active (non-former) clubs
    if len(active_clubs) >= 2:
        return (active_clubs[1], active_clubs[0])
    elif len(active_clubs) == 1:
        return ('', active_clubs[0])
    return (clubs[1] if len(clubs) > 1 else '', clubs[0])


# ---------------------------------------------------------------------------
# Negative claim detector — identifies claims that say a deal WON'T happen
# ---------------------------------------------------------------------------

_NEGATIVE_PHRASES = [
    # Contract extensions (staying, not moving)
    'signed a contract extension',
    'signed a new deal',
    'signed a new contract',
    'extended his contract',
    'extended her contract',
    'renewed his contract',
    'renewed her contract',
    'penned a new deal',
    'penned a new contract',
    'contract extension',
    # Explicit negations
    'will not',
    "won't",
    'not going to',
    'ruled out a move',
    'decided to stay',
    'staying at',
    'not leaving',
    'no intention of leaving',
    'committed to',
    'committed his future',
    # Blocks and rejections
    'blocked',
    'rejected the chance to',
    'turned down a move',
    'turned down the chance',
    'no interest in leaving',
    'not for sale',
    'deal is off',
    'deal collapsed',
    'move has collapsed',
    'transfer is off',
    'move is off',
    'pulled out',
    'walked away',
]

_NEGATIVE_REGEX = [
    re.compile(r'will not (?:be )?(?:joining|moving|leaving|signing)', re.IGNORECASE),
    re.compile(r'not (?:interested in|keen on) (?:a move|leaving|joining)', re.IGNORECASE),
]


def detect_negative_claim(text: str) -> bool:
    """Detect if a claim indicates a transfer will NOT happen.

    Covers contract extensions, explicit denials, blocked moves, etc.
    """
    lower = text.lower()

    for phrase in _NEGATIVE_PHRASES:
        if phrase in lower:
            return True

    for pattern in _NEGATIVE_REGEX:
        if pattern.search(lower):
            return True

    return False
