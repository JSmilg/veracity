import { useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { useTransferTimeline } from '../hooks/useTransfers'
import TransferHero from '../components/transfers/TransferHero'
import TimelineChart from '../components/transfers/TimelineChart'
import KeyMomentCard from '../components/transfers/KeyMomentCard'
import ClaimCard from '../components/claims/ClaimCard'
import Loading from '../components/common/Loading'
import ErrorMessage from '../components/common/ErrorMessage'
import { truncateText } from '../utils/formatters'

const MILESTONE_COLORS = {
  first_rumour: '#f97316',    // warm orange
  journalist: '#6366f1',      // accent indigo
  escalation: '#3b82f6',      // blue
  bid: '#a78bfa',             // violet
  competition: '#f59e0b',     // amber
  confirmed: '#22c55e',       // verified green
  official: '#10b981',        // emerald
}

// Notable tier-1 journalists to track individually
const TIER_ONE = ['David Ornstein', 'Fabrizio Romano']

function deriveMilestones(claims, keyMoments) {
  if (!claims?.length) return []

  const milestones = []
  const usedDates = new Set()

  const add = (date, label, detail, color, journalist, publication) => {
    const dateKey = date.split('T')[0]
    // Allow multiple milestones on different dates, but avoid cluttering same day
    if (usedDates.has(dateKey)) return
    usedDates.add(dateKey)
    milestones.push({ date: dateKey, label, detail, color, journalist, publication })
  }

  // 1. First rumour
  if (keyMoments?.first_rumour) {
    const m = keyMoments.first_rumour
    add(
      m.date,
      'First Rumour',
      truncateText(claims.find(c => c.id === m.claim_id)?.claim_text || '', 140),
      MILESTONE_COLORS.first_rumour,
      m.journalist_name,
      m.publication
    )
  }

  // 2. First report from each tier-1 journalist
  for (const name of TIER_ONE) {
    const first = claims.find(c => c.journalist_name === name)
    if (first && first.id !== keyMoments?.first_rumour?.claim_id) {
      const surname = name.split(' ').pop()
      add(
        first.claim_date,
        `${surname} Reports`,
        truncateText(first.claim_text, 140),
        MILESTONE_COLORS.journalist,
        first.journalist_name,
        first.publication
      )
    }
  }

  // 3. First escalation to 'tier_2_advanced' (if different from above)
  const firstAdvanced = claims.find(c => c.certainty_level === 'tier_2_advanced')
  if (firstAdvanced) {
    add(
      firstAdvanced.claim_date,
      'Deal Advanced',
      truncateText(firstAdvanced.claim_text, 140),
      MILESTONE_COLORS.escalation,
      firstAdvanced.journalist_name,
      firstAdvanced.publication
    )
  }

  // 4. Volume spike days (3+ claims in a single day = significant event)
  const dateCounts = {}
  for (const c of claims) {
    const d = c.claim_date.split('T')[0]
    dateCounts[d] = (dateCounts[d] || 0) + 1
  }
  const spikeDays = Object.entries(dateCounts)
    .filter(([, count]) => count >= 3)
    .sort(([a], [b]) => a.localeCompare(b))

  for (const [date, count] of spikeDays) {
    // Pick the best claim for that day (highest-profile journalist or original source)
    const dayClaims = claims.filter(c => c.claim_date.startsWith(date))
    const best = dayClaims.find(c => TIER_ONE.includes(c.journalist_name))
      || dayClaims.find(c => c.source_type === 'original')
      || dayClaims[0]

    // Try to infer a label from the claim text
    const text = best.claim_text.toLowerCase()
    let label = `${count} Reports in One Day`
    if (text.includes('reject')) label = 'Bid Rejected'
    else if (text.includes('bid') || text.includes('offer')) label = 'New Bid Submitted'
    else if (text.includes('city') && text.includes('not') || text.includes('city') && text.includes('drop')) label = 'Man City Drop Out'
    else if (text.includes('city') && text.includes('bid')) label = 'Man City Enter Race'
    else if (text.includes('agreed') || text.includes('accepted')) label = 'Fee Agreed'
    else if (text.includes('here we go') || text.includes('done')) label = 'Deal Done'

    const color = label.includes('Reject') ? MILESTONE_COLORS.bid
      : label.includes('City') ? MILESTONE_COLORS.competition
      : label.includes('Agreed') ? MILESTONE_COLORS.confirmed
      : MILESTONE_COLORS.escalation

    add(
      best.claim_date,
      label,
      truncateText(best.claim_text, 140),
      color,
      best.journalist_name,
      best.publication
    )
  }

  // 5. First confirmed (deal done)
  if (keyMoments?.first_confirmed) {
    const m = keyMoments.first_confirmed
    const claim = claims.find(c => c.id === m.claim_id)
    add(
      m.date,
      'Deal Confirmed',
      truncateText(claim?.claim_text || '', 140),
      MILESTONE_COLORS.confirmed,
      m.journalist_name,
      m.publication
    )
  }

  // 6. Official announcement (last confirmed claim, if different date from first confirmed)
  const confirmedClaims = claims.filter(c => c.certainty_level === 'tier_1_done_deal')
  if (confirmedClaims.length > 1) {
    const last = confirmedClaims[confirmedClaims.length - 1]
    add(
      last.claim_date,
      'Official Announcement',
      truncateText(last.claim_text, 140),
      MILESTONE_COLORS.official,
      last.journalist_name,
      last.publication
    )
  }

  return milestones.sort((a, b) => a.date.localeCompare(b.date))
}

const TransferTimelinePage = () => {
  const { id } = useParams()
  const { data, isLoading, error } = useTransferTimeline(id)

  const milestones = useMemo(() => {
    if (!data) return []
    return deriveMilestones(data.claims, data.key_moments)
  }, [data])

  if (isLoading) {
    return <Loading text="Loading transfer story..." />
  }

  if (error) {
    return <ErrorMessage message="Failed to load transfer story. Please try again." />
  }

  if (!data) {
    return <ErrorMessage message="Transfer not found." />
  }

  const { transfer, claims, daily_counts, key_moments, total_claims } = data

  const daySpan = daily_counts.length
  const claimsLabel = total_claims === 1 ? '1 claim' : `${total_claims} claims`
  const daysLabel = daySpan === 1 ? '1 day' : `${daySpan} days`

  return (
    <div className="space-y-0 animate-fade-in">
      {/* Hero */}
      <TransferHero transfer={transfer} />

      {/* Timeline Chart Section */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-surface-1 border border-edge rounded-xl shadow-elevation-1 p-6 mb-8">
          <div className="mb-6">
            <h2 className="text-3xl font-display text-zinc-100 mb-1">
              Transfer Timeline
            </h2>
            {total_claims > 0 && (
              <p className="text-zinc-500 font-sans text-sm">
                {claimsLabel} tracked over {daysLabel} · {milestones.length} key moments · hover the dots for details
              </p>
            )}
          </div>

          <TimelineChart dailyCounts={daily_counts} milestones={milestones} claims={claims} />

          {/* Milestone Legend */}
          {milestones.length > 0 && (
            <div className="flex flex-wrap gap-3 mt-6 pt-4 border-t border-edge">
              {milestones.map((m, i) => (
                <div key={i} className="flex items-center gap-1.5 text-xs font-sans text-zinc-400">
                  <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: m.color }} />
                  {m.label}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Key Moments Cards */}
      {(key_moments.first_rumour || key_moments.first_confirmed || key_moments.major_journalists?.length > 0) && (
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 pb-12">
          <div className="mb-6">
            <h2 className="text-3xl font-display text-zinc-100 mb-2">Key Moments</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {key_moments.first_rumour && (
              <KeyMomentCard moment={key_moments.first_rumour} type="first_rumour" />
            )}
            {key_moments.first_confirmed && (
              <KeyMomentCard moment={key_moments.first_confirmed} type="first_confirmed" />
            )}
            {key_moments.major_journalists?.map((m) => (
              <KeyMomentCard key={m.claim_id} moment={m} type="major_journalist" />
            ))}
          </div>
        </div>
      )}

      {/* All Claims */}
      {claims.length > 0 && (
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 pb-12 animate-slide-up">
          <div className="mb-8">
            <h2 className="text-3xl font-display text-zinc-100 mb-2">
              All Claims
            </h2>
            <p className="text-zinc-500 font-sans text-sm">
              Every report tracked for this transfer, ordered by date
            </p>
          </div>

          <div className="space-y-4">
            {claims.map((claim) => (
              <ClaimCard key={claim.id} claim={claim} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TransferTimelinePage
