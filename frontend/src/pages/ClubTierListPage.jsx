import { useState, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts'
import { useClubTiers } from '../hooks/useJournalists'
import Loading from '../components/common/Loading'
import ErrorMessage from '../components/common/ErrorMessage'

// ── Club config ──────────────────────────────────────────────

const CLUBS = [
  { slug: 'arsenal', name: 'Arsenal', color: '#EF0107' },
  { slug: 'chelsea', name: 'Chelsea', color: '#034694' },
  { slug: 'liverpool', name: 'Liverpool', color: '#C8102E' },
  { slug: 'man-city', name: 'Manchester City', color: '#6CABDD' },
  { slug: 'man-utd', name: 'Manchester United', color: '#DA291C' },
  { slug: 'tottenham', name: 'Tottenham Hotspur', color: '#132257' },
]

const TIERS = [
  { tier: 1, label: 'Gold Standard', color: '#22c55e', bg: 'rgba(34,197,94,0.08)', border: 'rgba(34,197,94,0.2)' },
  { tier: 2, label: 'Reliable', color: '#3b82f6', bg: 'rgba(59,130,246,0.08)', border: 'rgba(59,130,246,0.2)' },
  { tier: 3, label: 'Inconsistent', color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)' },
  { tier: 4, label: 'Avoid', color: '#ef4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)' },
]

function getTierColor(tier) {
  if (tier === 1) return '#22c55e'
  if (tier === 2) return '#3b82f6'
  if (tier === 3) return '#f59e0b'
  if (tier === 4) return '#ef4444'
  return '#71717a'
}

// ── Scatter tooltip ──────────────────────────────────────────

const TierTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null

  const color = getTierColor(d.tier)
  const tierLabel = TIERS.find(t => t.tier === d.tier)?.label || 'Low Volume'

  return (
    <div
      className="border rounded-xl shadow-elevation-2 pointer-events-none"
      style={{ background: '#18181b', borderColor: color + '40', padding: 16, maxWidth: 260 }}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="w-3 h-3 rounded-full" style={{ background: color }} />
        <span className="text-sm font-sans font-bold text-zinc-100">{d.name}</span>
      </div>
      <div className="text-xs font-sans text-zinc-500 mb-3">
        {tierLabel} &middot; {d.publications}
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-xs font-sans text-zinc-500 uppercase tracking-wide mb-0.5">Accuracy</div>
          <div className="text-lg font-mono font-bold" style={{ color }}>{d.club_accuracy}%</div>
        </div>
        <div>
          <div className="text-xs font-sans text-zinc-500 uppercase tracking-wide mb-0.5">Speed</div>
          <div className="text-lg font-mono font-bold" style={{ color }}>{d.club_speed}%</div>
        </div>
      </div>
      <div className="mt-3 pt-2 border-t border-zinc-800 text-xs font-mono text-zinc-500">
        {d.club_claims} claims &middot; {d.club_true} true &middot; {d.club_false} false
      </div>
    </div>
  )
}

// ── Journalist card ──────────────────────────────────────────

const JournalistCard = ({ entry, tierColor, index }) => {
  const { journalist: j, club_accuracy, club_speed, club_claims, club_true, club_false, club_validated } = entry
  const trueWidth = club_validated > 0 ? (club_true / club_validated) * 100 : 0
  const falseWidth = club_validated > 0 ? (club_false / club_validated) * 100 : 0
  const publications = Array.isArray(j.publications) ? j.publications.join(', ') : j.publications || ''

  return (
    <div
      className="bg-surface-1 border border-edge rounded-xl p-5 hover:border-edge-hover transition-all duration-200 animate-slide-up"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="min-w-0">
          <Link
            to={`/journalist/${j.slug}`}
            className="text-base font-sans font-semibold text-zinc-100 hover:text-accent transition-colors"
          >
            {j.name}
          </Link>
          {publications && (
            <div className="text-xs font-sans text-zinc-500 mt-0.5 truncate">{publications}</div>
          )}
        </div>
        <div
          className="flex-shrink-0 ml-3 px-2 py-0.5 rounded-md text-xs font-mono font-bold"
          style={{ background: tierColor + '18', color: tierColor }}
        >
          {club_accuracy}%
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mb-3">
        <div>
          <div className="text-xs font-sans text-zinc-600 uppercase tracking-wide">Accuracy</div>
          <div className="text-sm font-mono font-bold tabular-nums" style={{ color: tierColor }}>{club_accuracy}%</div>
        </div>
        <div>
          <div className="text-xs font-sans text-zinc-600 uppercase tracking-wide">Speed</div>
          <div className="text-sm font-mono font-bold tabular-nums text-zinc-300">{club_speed}%</div>
        </div>
        <div>
          <div className="text-xs font-sans text-zinc-600 uppercase tracking-wide">Claims</div>
          <div className="text-sm font-mono font-bold tabular-nums text-zinc-300">{club_claims}</div>
        </div>
      </div>

      {/* True/false mini bar */}
      <div className="flex items-center gap-2">
        <div className="flex-1 h-2 bg-surface-2 rounded-full overflow-hidden flex">
          {trueWidth > 0 && (
            <div
              className="h-full bg-emerald-500 rounded-l-full"
              style={{ width: `${trueWidth}%` }}
            />
          )}
          {falseWidth > 0 && (
            <div
              className="h-full bg-red-500"
              style={{ width: `${falseWidth}%`, borderRadius: trueWidth === 0 ? '9999px 0 0 9999px' : '0' }}
            />
          )}
        </div>
        <span className="text-[10px] font-mono text-zinc-600 flex-shrink-0">
          {club_true}T / {club_false}F
        </span>
      </div>
    </div>
  )
}

// ── Main component ──────────────────────────────────────────

const ClubTierListPage = () => {
  const { slug } = useParams()
  const [showLowVolume, setShowLowVolume] = useState(false)
  const [hoveredDot, setHoveredDot] = useState(null)

  const club = CLUBS.find(c => c.slug === slug) || CLUBS[0]
  const { data, isLoading, error } = useClubTiers(club.name)

  // Group data by tier
  const { tiered, untiered, scatterData } = useMemo(() => {
    if (!data) return { tiered: {}, untiered: [], scatterData: [] }

    const tierGroups = { 1: [], 2: [], 3: [], 4: [] }
    const lowVol = []
    const scatter = []

    for (const entry of data) {
      const publications = Array.isArray(entry.journalist.publications)
        ? entry.journalist.publications.join(', ')
        : entry.journalist.publications || ''

      const point = {
        name: entry.journalist.name,
        slug: entry.journalist.slug,
        publications,
        club_accuracy: entry.club_accuracy,
        club_speed: entry.club_speed,
        club_claims: entry.club_claims,
        club_true: entry.club_true,
        club_false: entry.club_false,
        tier: entry.tier,
      }
      scatter.push(point)

      if (entry.tier != null && tierGroups[entry.tier]) {
        tierGroups[entry.tier].push(entry)
      } else {
        lowVol.push(entry)
      }
    }

    return { tiered: tierGroups, untiered: lowVol, scatterData: scatter }
  }, [data])

  if (isLoading) return <Loading text={`Loading ${club.name} tier list...`} />
  if (error) return <ErrorMessage message={`Failed to load tier list for ${club.name}.`} />

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div
            className="w-2 h-10 rounded-full"
            style={{ background: club.color }}
          />
          <h1 className="text-4xl md:text-5xl font-display text-zinc-100 tracking-tight">
            {club.name}
          </h1>
        </div>
        <p className="text-lg font-sans text-zinc-500 max-w-2xl leading-relaxed">
          <span style={{ color: club.color }} className="font-semibold">Journalist Tier List</span> — who to trust
          when they link a player to {club.name}. Ranked by accuracy on validated claims.
        </p>
      </div>

      {/* Club nav pills */}
      <div className="flex flex-wrap gap-2 mb-8">
        {CLUBS.map(c => {
          const active = c.slug === slug
          return (
            <Link
              key={c.slug}
              to={`/club/${c.slug}`}
              className="px-4 py-2 rounded-lg text-sm font-sans font-medium transition-all duration-200"
              style={active ? {
                background: c.color + '20',
                color: c.color,
                borderWidth: 1,
                borderColor: c.color + '40',
              } : {
                background: 'transparent',
                color: '#a1a1aa',
                borderWidth: 1,
                borderColor: '#27272a',
              }}
            >
              {c.name}
            </Link>
          )
        })}
      </div>

      {/* Scatter plot */}
      {scatterData.length > 0 && (
        <div className="bg-surface-1 border border-edge rounded-xl shadow-elevation-1 p-6 mb-8">
          <div className="flex flex-wrap gap-5 mb-5">
            {TIERS.map(t => (
              <div key={t.tier} className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full" style={{ background: t.color }} />
                <span className="text-xs font-sans font-semibold text-zinc-300">T{t.tier}</span>
                <span className="text-xs font-sans text-zinc-600">{t.label}</span>
              </div>
            ))}
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-zinc-600" />
              <span className="text-xs font-sans text-zinc-600">Low Volume</span>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={480}>
            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
              <XAxis
                type="number"
                dataKey="club_accuracy"
                name="Accuracy"
                domain={[0, 100]}
                tick={{ fill: '#a1a1aa', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                axisLine={{ stroke: '#2e2e33' }}
                tickLine={false}
                label={{
                  value: 'Accuracy (% claims proven true)',
                  position: 'bottom',
                  offset: 0,
                  style: { fill: '#71717a', fontSize: 12, fontFamily: 'DM Sans' },
                }}
              />
              <YAxis
                type="number"
                dataKey="club_claims"
                name="Volume"
                tick={{ fill: '#a1a1aa', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                axisLine={{ stroke: '#2e2e33' }}
                tickLine={false}
                label={{
                  value: 'Volume (total claims)',
                  angle: -90,
                  position: 'insideLeft',
                  offset: 0,
                  style: { fill: '#71717a', fontSize: 12, fontFamily: 'DM Sans' },
                }}
              />
              <ZAxis
                type="number"
                dataKey="club_speed"
                range={[60, 500]}
                name="Speed"
              />

              {/* Tier boundary lines */}
              <ReferenceLine x={70} stroke="#22c55e" strokeOpacity={0.25} strokeDasharray="6 4" />
              <ReferenceLine x={50} stroke="#3b82f6" strokeOpacity={0.25} strokeDasharray="6 4" />
              <ReferenceLine x={30} stroke="#f59e0b" strokeOpacity={0.25} strokeDasharray="6 4" />

              <Tooltip content={<TierTooltip />} cursor={false} />

              <Scatter data={scatterData} fillOpacity={0.85}>
                {scatterData.map((entry, i) => {
                  const color = getTierColor(entry.tier)
                  return (
                    <Cell
                      key={`${slug}-${i}`}
                      fill={color}
                      stroke={color}
                      strokeOpacity={0.3}
                      strokeWidth={hoveredDot === i ? 8 : 0}
                      style={{ cursor: 'pointer', transition: 'stroke-width 0.2s' }}
                      onMouseEnter={() => setHoveredDot(i)}
                      onMouseLeave={() => setHoveredDot(null)}
                    />
                  )
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>

          {/* Name labels */}
          <div className="mt-4 pt-3 border-t border-edge">
            <div className="flex flex-wrap gap-x-4 gap-y-1.5">
              {[...scatterData]
                .sort((a, b) => (b.club_accuracy + b.club_claims) - (a.club_accuracy + a.club_claims))
                .map(d => {
                  const idx = scatterData.indexOf(d)
                  return (
                    <div
                      key={d.name}
                      className="flex items-center gap-1.5 text-xs font-sans text-zinc-500 hover:text-zinc-200 transition-colors cursor-default"
                      onMouseEnter={() => setHoveredDot(idx)}
                      onMouseLeave={() => setHoveredDot(null)}
                    >
                      <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: getTierColor(d.tier) }} />
                      <span className={hoveredDot === idx ? 'text-zinc-100 font-medium' : ''}>
                        {d.name}
                      </span>
                      <span className="font-mono text-zinc-700 text-[10px]">
                        {d.club_accuracy}%
                      </span>
                    </div>
                  )
                })}
            </div>
          </div>
        </div>
      )}

      {/* Tier sections */}
      {TIERS.map(t => {
        const entries = tiered[t.tier] || []
        if (entries.length === 0) return null

        return (
          <div key={t.tier} className="mb-8">
            <div
              className="flex items-center gap-3 mb-4 px-4 py-3 rounded-lg"
              style={{ background: t.bg, borderLeft: `3px solid ${t.color}` }}
            >
              <span
                className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-mono font-bold"
                style={{ background: t.color + '20', color: t.color }}
              >
                T{t.tier}
              </span>
              <div>
                <h2 className="text-lg font-display text-zinc-100">{t.label}</h2>
                <p className="text-xs font-sans text-zinc-500">
                  {t.tier === 1 && 'Highly reliable sources for this club'}
                  {t.tier === 2 && 'Generally trustworthy, worth paying attention to'}
                  {t.tier === 3 && 'Hit or miss — verify with better sources'}
                  {t.tier === 4 && 'Frequently wrong — take with a large grain of salt'}
                </p>
              </div>
              <span className="ml-auto text-xs font-mono text-zinc-600">{entries.length} journalist{entries.length !== 1 ? 's' : ''}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {entries.map((entry, i) => (
                <JournalistCard key={entry.journalist.id} entry={entry} tierColor={t.color} index={i} />
              ))}
            </div>
          </div>
        )
      })}

      {/* Low volume section */}
      {untiered.length > 0 && (
        <div className="mb-8">
          <button
            onClick={() => setShowLowVolume(!showLowVolume)}
            className="flex items-center gap-3 mb-4 px-4 py-3 rounded-lg w-full text-left bg-surface-1 border border-edge hover:border-edge-hover transition-colors"
          >
            <span className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center text-sm font-mono font-bold text-zinc-500">
              ?
            </span>
            <div>
              <h2 className="text-lg font-display text-zinc-400">Low Volume</h2>
              <p className="text-xs font-sans text-zinc-600">
                Fewer than 3 validated claims — not enough data to tier
              </p>
            </div>
            <span className="ml-auto text-xs font-mono text-zinc-600">{untiered.length}</span>
            <svg
              className={`w-4 h-4 text-zinc-500 transition-transform duration-200 ${showLowVolume ? 'rotate-180' : ''}`}
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showLowVolume && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 opacity-60">
              {untiered.map((entry, i) => (
                <JournalistCard key={entry.journalist.id} entry={entry} tierColor="#71717a" index={i} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {data && data.length === 0 && (
        <div className="bg-surface-1 border border-edge rounded-xl text-center py-16">
          <p className="text-zinc-300 font-sans font-medium">
            No journalist data found for {club.name}.
          </p>
          <p className="text-zinc-500 font-sans text-sm mt-1">
            Claims need to be added and validated before tiers can be generated.
          </p>
        </div>
      )}
    </div>
  )
}

export default ClubTierListPage
