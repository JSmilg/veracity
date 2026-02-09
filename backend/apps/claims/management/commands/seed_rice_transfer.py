"""Seed the Declan Rice to Arsenal transfer story based on real reporting timeline.

Sources:
- Sky Sports transfer centre reports
- Ornstein tweets (@David_Ornstein) on The Athletic
- Romano tweets (@FabrizioRomano) "here we go" confirmation
- Football365, TNT Sports, ESPN reporting
- r/Gunners community tracking
"""

from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.claims.classifiers import classify_claim_confidence
from apps.claims.models import Journalist, Claim, Transfer


JOURNALISTS = [
    {'name': 'Fabrizio Romano', 'twitter': '@FabrizioRomano', 'pubs': ['The Guardian', 'CaughtOffside'], 'truth': 88, 'speed': 92},
    {'name': 'David Ornstein', 'twitter': '@David_Ornstein', 'pubs': ['The Athletic'], 'truth': 91, 'speed': 85},
    {'name': 'Dharmesh Sheth', 'twitter': '@DhsrmeshSheth', 'pubs': ['Sky Sports'], 'truth': 75, 'speed': 60},
    {'name': 'John Cross', 'twitter': '@johncrossmirror', 'pubs': ['Daily Mirror'], 'truth': 62, 'speed': 45},
    {'name': 'Charles Watts', 'twitter': '@charles_watts', 'pubs': ['Goal', 'Football.london'], 'truth': 78, 'speed': 70},
    {'name': 'Ben Jacobs', 'twitter': '@JacobsBen', 'pubs': ['CBS Sports'], 'truth': 72, 'speed': 68},
    {'name': 'Sami Mokbel', 'twitter': '@SamiMokbel81_DM', 'pubs': ['Daily Mail'], 'truth': 65, 'speed': 50},
    {'name': 'Florian Plettenberg', 'twitter': '@Plettigoal', 'pubs': ['Sky Germany'], 'truth': 80, 'speed': 75},
    {'name': 'Graeme Bailey', 'twitter': '@GraemeBailey', 'pubs': ['90min'], 'truth': 55, 'speed': 58},
    {'name': 'Dean Jones', 'twitter': '@DeanJonesBR', 'pubs': ['GiveMeSport'], 'truth': 60, 'speed': 52},
]

# Verified timeline from Sky Sports, The Athletic, and cross-referenced reporting
CLAIMS = [
    # ===== EARLY LINKS (late 2022 / Jan 2023) =====
    {'journalist': 'Graeme Bailey', 'date': '2022-10-18 08:00', 'certainty': 'speculation', 'source_type': 'original',
     'text': 'Arsenal are among the clubs monitoring Declan Rice ahead of a potential summer move. The West Ham captain has entered the final 18 months of his contract.',
     'first': True},
    {'journalist': 'John Cross', 'date': '2022-12-05 07:00', 'certainty': 'rumoured', 'source_type': 'original',
     'text': 'Arsenal manager Mikel Arteta is a huge admirer of Declan Rice and the club see him as the ideal midfielder to complete their rebuild.'},

    # ===== ORNSTEIN BREAKS IT — FEB 2023 =====
    {'journalist': 'David Ornstein', 'date': '2023-02-02 10:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Declan Rice could be available this summer for a fee between £75m and £85m. Arsenal are leading the race and see him as their priority midfield target. West Ham have accepted he will leave.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-02-04 19:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal are pushing to be in the best position to sign Declan Rice. He is the priority target for the summer. Manchester City are also monitoring the situation.'},
    {'journalist': 'Sami Mokbel', 'date': '2023-02-06 22:30', 'certainty': 'rumoured', 'source_type': 'citing',
     'text': 'Declan Rice is understood to be keen on a move to Arsenal with the Gunners leading the race for the West Ham captain.'},
    {'journalist': 'Dean Jones', 'date': '2023-02-10 14:00', 'certainty': 'rumoured', 'source_type': 'citing',
     'text': 'Arsenal are in pole position for Declan Rice. The player has made it clear he wants to play in the Champions League.'},

    # ===== MARCH/APRIL — BUILDING MOMENTUM =====
    {'journalist': 'Charles Watts', 'date': '2023-03-12 14:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal sources confirm Declan Rice is the club\'s number one summer target. Mikel Arteta has personally spoken to the player about his plans for him at the Emirates.'},
    {'journalist': 'Dharmesh Sheth', 'date': '2023-03-20 18:30', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Sky Sports understands Arsenal are leading the race for Declan Rice. West Ham are resigned to losing their captain this summer.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-04-15 20:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Declan Rice has already told his camp he wants to join Arsenal. Personal terms are not expected to be an issue. It is just about the fee between the two clubs now.'},
    {'journalist': 'Ben Jacobs', 'date': '2023-04-22 11:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'West Ham value Declan Rice at over £100m. Arsenal are confident of reaching an agreement but expect protracted negotiations this summer.'},
    {'journalist': 'John Cross', 'date': '2023-04-28 07:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Declan Rice has told close friends he wants to join Arsenal. The midfielder sees his long-term future at the Emirates Stadium.'},

    # ===== MAY — MAN CITY ENTER, COMPETITION HEATS UP =====
    {'journalist': 'David Ornstein', 'date': '2023-05-08 09:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Manchester City have registered interest in Declan Rice alongside Arsenal. However, Rice\'s preference is understood to be Arsenal where he sees a clearer path to regular football.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-05-15 21:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Manchester City are now seriously exploring a move for Declan Rice. But Arsenal remain confident — personal terms have been discussed with Rice\'s camp for weeks.'},
    {'journalist': 'Dharmesh Sheth', 'date': '2023-05-22 12:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'The battle for Declan Rice is intensifying with Manchester City making contact with West Ham. Arsenal remain favourites.'},
    {'journalist': 'Charles Watts', 'date': '2023-05-30 10:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal are preparing their opening bid for Declan Rice. The club are confident of getting a deal done despite Man City\'s interest.'},

    # ===== JUNE 7 — SULLIVAN CONFIRMS DEPARTURE =====
    {'journalist': 'David Ornstein', 'date': '2023-06-07 20:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'David Sullivan has confirmed Declan Rice has played his last game for West Ham following the Europa Conference League final. Arsenal and Man City set for bidding war.'},
    {'journalist': 'Sami Mokbel', 'date': '2023-06-08 07:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'West Ham chairman David Sullivan confirms Declan Rice\'s departure is imminent. Arsenal and Manchester City both preparing bids.'},

    # ===== JUNE 15 — ARSENAL'S 1ST BID REJECTED =====
    {'journalist': 'David Ornstein', 'date': '2023-06-15 09:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal have made an opening bid of around £80m plus add-ons for Declan Rice. West Ham have rejected the offer as insufficient. The Hammers want at least £100m.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-06-15 12:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal\'s first official bid for Declan Rice has been rejected by West Ham. The offer was around £80m. West Ham want significantly more. Arsenal will return with an improved offer.'},
    {'journalist': 'Dharmesh Sheth', 'date': '2023-06-15 14:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Sky Sports News: Arsenal\'s opening bid for Declan Rice has been turned down by West Ham. The Gunners are expected to come back with an improved offer.'},

    # ===== JUNE 20 — 2ND BID £90M REJECTED =====
    {'journalist': 'David Ornstein', 'date': '2023-06-20 08:30', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal have had a second bid rejected for Declan Rice. The offer was worth up to £90m — a £75m fee plus £15m in add-ons. West Ham remain firm on their £100m+ valuation.'},
    {'journalist': 'Ben Jacobs', 'date': '2023-06-20 13:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'West Ham have rejected Arsenal\'s improved £90m bid for Declan Rice. The gap remains significant but Arsenal are not giving up.'},
    {'journalist': 'John Cross', 'date': '2023-06-21 06:30', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Arsenal will not be deterred after second Rice bid rejected. The club are willing to break their transfer record and go north of £100m.'},

    # ===== JUNE 26 — MAN CITY BID, ALSO REJECTED =====
    {'journalist': 'David Ornstein', 'date': '2023-06-26 10:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Manchester City have made an official bid for Declan Rice worth £80m up front plus £10m in add-ons. The offer has been rejected by West Ham.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-06-26 14:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Manchester City\'s official bid for Declan Rice — £90m total package — has been rejected by West Ham. Arsenal remain in the stronger position.'},
    {'journalist': 'Florian Plettenberg', 'date': '2023-06-26 16:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Bayern Munich have decided not to submit an offer for Declan Rice after all. The club feel the fee is too high. It is now between Arsenal and Man City.'},

    # ===== JUNE 27-28 — MAN CITY DROP OUT, ARSENAL'S 3RD BID =====
    {'journalist': 'Fabrizio Romano', 'date': '2023-06-28 11:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Manchester City will NOT enter a bidding war for Declan Rice. Internal discussions today — City have decided not to match Arsenal\'s record proposal. Over to Arsenal and West Ham now.'},
    {'journalist': 'David Ornstein', 'date': '2023-06-28 15:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal have lodged a third bid for Declan Rice worth £100m guaranteed plus £5m in performance add-ons. This is a club-record offer. West Ham are considering the proposal.'},
    {'journalist': 'Dharmesh Sheth', 'date': '2023-06-28 18:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Sky Sports: Arsenal have submitted a third offer for Declan Rice worth up to £105m. Man City have withdrawn from the race.'},

    # ===== JUNE 29 — FEE AGREED =====
    {'journalist': 'David Ornstein', 'date': '2023-06-29 08:45', 'certainty': 'confirmed', 'source_type': 'original',
     'text': 'Arsenal have agreed a fee with West Ham to sign Declan Rice. Arsenal made £100m + £5m add-ons offer for the 24yo England midfielder last night and that has been accepted. Record for a British player. Clubs now working to resolve payment terms.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-06-29 09:30', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Arsenal and West Ham have a verbal agreement in place for Declan Rice — £100m plus £5m in add-ons. Payment structure still being finalised. Personal terms not an issue.'},
    {'journalist': 'Ben Jacobs', 'date': '2023-06-29 12:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Fee agreed between Arsenal and West Ham for Declan Rice. Deal worth £105m. But payment structure negotiations are ongoing — West Ham want the money faster.'},
    {'journalist': 'Dean Jones', 'date': '2023-06-29 15:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Declan Rice to Arsenal is on. Fee agreed at £105m. Now just paperwork and a medical standing between Rice and his move to the Emirates.'},
    {'journalist': 'Charles Watts', 'date': '2023-06-29 16:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Arsenal have agreed a club-record deal for Declan Rice. The midfielder is expected to undergo a medical in the coming days.'},

    # ===== EARLY JULY — PAYMENT STRUCTURE DELAYS =====
    {'journalist': 'David Ornstein', 'date': '2023-07-01 10:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Declan Rice deal update: Arsenal and West Ham still negotiating payment structure. West Ham want two instalments by start of 2025. Arsenal initially proposed four-year payments. Deal not in doubt — just terms.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-07-02 20:00', 'certainty': 'sources_say', 'source_type': 'original',
     'text': 'Declan Rice deal is NOT in doubt despite payment talks. Arsenal and West Ham are confident of resolving the structure. Rice has already agreed personal terms — five-year contract.'},
    {'journalist': 'Sami Mokbel', 'date': '2023-07-03 23:00', 'certainty': 'sources_say', 'source_type': 'citing',
     'text': 'Fears that Declan Rice deal could collapse are unfounded. Arsenal and West Ham in daily contact over payment structure. Completion expected within days.'},

    # ===== JULY 4 — HERE WE GO! DEAL DONE =====
    {'journalist': 'Fabrizio Romano', 'date': '2023-07-04 18:26', 'certainty': 'confirmed', 'source_type': 'original',
     'text': 'Declan Rice to Arsenal, here we go! Deal in place between Arsenal and West Ham and Gunners sign their top target. £100m plus £5m add-ons. It\'s the most expensive signing ever for Arsenal and most expensive English player ever. Arteta and Edu, crucial to make it happen.'},
    {'journalist': 'David Ornstein', 'date': '2023-07-04 18:30', 'certainty': 'confirmed', 'source_type': 'original',
     'text': 'EXCLUSIVE: Arsenal have reached total agreement with West Ham to sign Declan Rice. West Ham have now accepted Arsenal payment structure on record £100m + £5m fee. 24yo England midfielder given permission to do medical and finalise personal terms.'},
    {'journalist': 'Dharmesh Sheth', 'date': '2023-07-04 19:00', 'certainty': 'confirmed', 'source_type': 'citing',
     'text': 'Sky Sports News: Arsenal have reached full agreement with West Ham for Declan Rice in a deal worth up to £105m. Rice set to undergo medical.'},
    {'journalist': 'Charles Watts', 'date': '2023-07-04 19:30', 'certainty': 'confirmed', 'source_type': 'citing',
     'text': 'Declan Rice to Arsenal is done! Full agreement in place. Club-record deal worth £105m. The biggest transfer of the summer window.'},
    {'journalist': 'Ben Jacobs', 'date': '2023-07-04 20:00', 'certainty': 'confirmed', 'source_type': 'citing',
     'text': 'Declan Rice deal fully agreed. Arsenal pay £100m guaranteed plus £5m in add-ons. West Ham receive £50m immediately and a further £50m in summer 2024.'},
    {'journalist': 'John Cross', 'date': '2023-07-05 06:30', 'certainty': 'confirmed', 'source_type': 'citing',
     'text': 'Declan Rice is an Arsenal player in all but name. The £105m deal is done, medical arranged. The biggest signing in Arsenal\'s history.'},
    {'journalist': 'Sami Mokbel', 'date': '2023-07-05 07:00', 'certainty': 'confirmed', 'source_type': 'citing',
     'text': 'Arsenal confirm record £105m agreement for Declan Rice from West Ham United. Medical to take place before official announcement.'},

    # ===== JULY 15 — OFFICIAL ANNOUNCEMENT =====
    {'journalist': 'David Ornstein', 'date': '2023-07-15 10:00', 'certainty': 'confirmed', 'source_type': 'original',
     'text': 'Declan Rice has officially signed for Arsenal from West Ham. Five-year contract until 2028 with option for a further year. Wears the No. 41 shirt. Club-record £105m transfer complete.'},
    {'journalist': 'Fabrizio Romano', 'date': '2023-07-15 10:15', 'certainty': 'confirmed', 'source_type': 'citing',
     'text': 'Official and confirmed. Declan Rice is a new Arsenal player. Contract until June 2028 with option for further year. £100m plus £5m add-ons. Done deal, as expected.'},
]


class Command(BaseCommand):
    help = 'Seed the Declan Rice to Arsenal transfer story with verified timeline data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing Rice claims and transfer before re-seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted_claims, _ = Claim.objects.filter(
                player_name='Declan Rice', to_club='Arsenal',
            ).delete()
            deleted_transfers, _ = Transfer.objects.filter(
                player_name='Declan Rice', to_club='Arsenal',
            ).delete()
            self.stdout.write(self.style.WARNING(
                f'  Reset: deleted {deleted_claims} claims, {deleted_transfers} transfer(s)'
            ))

        # Create journalists
        journalist_objs = {}
        for j in JOURNALISTS:
            obj, created = Journalist.objects.get_or_create(
                name=j['name'],
                defaults={
                    'slug': j['name'].lower().replace(' ', '-'),
                    'twitter_handle': j['twitter'],
                    'publications': j['pubs'],
                    'truthfulness_score': j['truth'],
                    'speed_score': j['speed'],
                },
            )
            journalist_objs[j['name']] = obj
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {j["name"]}')

        # Create claims
        claims_created = 0
        first_claim_obj = None
        for i, c in enumerate(CLAIMS):
            dt = timezone.make_aware(datetime.strptime(c['date'], '%Y-%m-%d %H:%M'))
            journalist = journalist_objs[c['journalist']]

            claim, created = Claim.objects.get_or_create(
                journalist=journalist,
                claim_text=c['text'],
                defaults={
                    'claim_date': dt,
                    'publication': journalist.publications[0] if journalist.publications else '',
                    'player_name': 'Declan Rice',
                    'from_club': 'West Ham United',
                    'to_club': 'Arsenal',
                    'transfer_fee': '£105m' if c['certainty'] == 'confirmed' else '',
                    'certainty_level': classify_claim_confidence(c['text']),
                    'source_type': c['source_type'],
                    'is_first_claim': c.get('first', False),
                    'validation_status': 'confirmed_true',
                    'validation_date': timezone.make_aware(datetime(2023, 7, 15, 12, 0)),
                    'validation_notes': 'Transfer officially completed on 15 July 2023.',
                },
            )
            if created:
                claims_created += 1
            if i == 0:
                first_claim_obj = claim

        self.stdout.write(self.style.SUCCESS(f'\n  Created {claims_created} claims'))

        # Create Transfer record
        transfer, created = Transfer.objects.get_or_create(
            player_name='Declan Rice',
            to_club='Arsenal',
            transfer_window='Summer 2023',
            defaults={
                'from_club': 'West Ham United',
                'completed': True,
                'completion_date': '2023-07-15',
                'actual_fee': '£105m',
                'first_claim': first_claim_obj,
            },
        )

        status = 'Created' if created else 'Already exists'
        self.stdout.write(self.style.SUCCESS(f'  {status} Transfer: Declan Rice → Arsenal (ID: {transfer.pk})'))
        self.stdout.write(self.style.SUCCESS(f'\n  View at: http://localhost:5173/transfer/{transfer.pk}'))
