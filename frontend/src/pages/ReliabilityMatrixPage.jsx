import { useState, useMemo } from 'react'
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

// ── Fake data ──────────────────────────────────────────────────

const CLUBS = [
  { id: 'all', name: 'All Clubs' },
  { id: 'arsenal', name: 'Arsenal' },
  { id: 'chelsea', name: 'Chelsea' },
  { id: 'liverpool', name: 'Liverpool' },
  { id: 'man-city', name: 'Manchester City' },
  { id: 'man-utd', name: 'Manchester United' },
  { id: 'tottenham', name: 'Tottenham Hotspur' },
  { id: 'newcastle', name: 'Newcastle United' },
  { id: 'barcelona', name: 'Barcelona' },
  { id: 'real-madrid', name: 'Real Madrid' },
  { id: 'bayern', name: 'Bayern Munich' },
  { id: 'psg', name: 'PSG' },
  { id: 'juventus', name: 'Juventus' },
]

// Per-journalist per-club overrides (scores shift depending on club expertise)
// Only journalists with club-specific data are listed; others are excluded when filtering
const CLUB_DATA = {
  arsenal: {
    'David Ornstein':     { truthfulness: 94, speed: 90, claims: 48 },
    'Fabrizio Romano':    { truthfulness: 86, speed: 88, claims: 42 },
    'Charles Watts':      { truthfulness: 85, speed: 82, claims: 52 },
    'Chris Wheatley':     { truthfulness: 78, speed: 75, claims: 38 },
    'Ben Jacobs':         { truthfulness: 70, speed: 62, claims: 22 },
    'Dharmesh Sheth':     { truthfulness: 72, speed: 55, claims: 28 },
    'John Cross':         { truthfulness: 68, speed: 52, claims: 35 },
    'Sami Mokbel':        { truthfulness: 62, speed: 48, claims: 20 },
    'Ekrem Konur':        { truthfulness: 35, speed: 72, claims: 45 },
    'Dean Jones':         { truthfulness: 55, speed: 48, claims: 15 },
    'Graeme Bailey':      { truthfulness: 50, speed: 55, claims: 18 },
    'Kaveh Solhekol':     { truthfulness: 65, speed: 50, claims: 22 },
    'Nicolo Schira':      { truthfulness: 40, speed: 75, claims: 30 },
    'Rudy Galetti':       { truthfulness: 32, speed: 68, claims: 25 },
    'Pete O\'Rourke':     { truthfulness: 45, speed: 65, claims: 28 },
  },
  chelsea: {
    'David Ornstein':     { truthfulness: 90, speed: 82, claims: 35 },
    'Fabrizio Romano':    { truthfulness: 90, speed: 95, claims: 55 },
    'Ben Jacobs':         { truthfulness: 78, speed: 75, claims: 40 },
    'Simon Stone':        { truthfulness: 80, speed: 38, claims: 18 },
    'Dharmesh Sheth':     { truthfulness: 74, speed: 58, claims: 30 },
    'Nizaar Kinsella':    { truthfulness: 82, speed: 78, claims: 45 },
    'John Cross':         { truthfulness: 58, speed: 40, claims: 22 },
    'Sami Mokbel':        { truthfulness: 60, speed: 45, claims: 18 },
    'Ekrem Konur':        { truthfulness: 38, speed: 80, claims: 38 },
    'Nicolo Schira':      { truthfulness: 42, speed: 82, claims: 35 },
    'Kaveh Solhekol':     { truthfulness: 72, speed: 58, claims: 25 },
  },
  liverpool: {
    'David Ornstein':     { truthfulness: 92, speed: 80, claims: 30 },
    'Fabrizio Romano':    { truthfulness: 85, speed: 90, claims: 38 },
    'James Pearce':       { truthfulness: 90, speed: 85, claims: 55 },
    'Paul Joyce':         { truthfulness: 88, speed: 78, claims: 42 },
    'Dharmesh Sheth':     { truthfulness: 70, speed: 55, claims: 20 },
    'Simon Stone':        { truthfulness: 84, speed: 42, claims: 15 },
    'Ekrem Konur':        { truthfulness: 40, speed: 75, claims: 32 },
    'Nicolo Schira':      { truthfulness: 44, speed: 78, claims: 28 },
    'Graeme Bailey':      { truthfulness: 52, speed: 55, claims: 20 },
  },
  'man-utd': {
    'David Ornstein':     { truthfulness: 92, speed: 85, claims: 40 },
    'Fabrizio Romano':    { truthfulness: 89, speed: 90, claims: 50 },
    'Simon Stone':        { truthfulness: 88, speed: 48, claims: 42 },
    'Laurie Whitwell':    { truthfulness: 85, speed: 72, claims: 38 },
    'Dharmesh Sheth':     { truthfulness: 76, speed: 62, claims: 32 },
    'James Ducker':       { truthfulness: 80, speed: 50, claims: 28 },
    'John Cross':         { truthfulness: 60, speed: 42, claims: 25 },
    'Ekrem Konur':        { truthfulness: 44, speed: 76, claims: 40 },
    'Nicolo Schira':      { truthfulness: 48, speed: 82, claims: 35 },
    'Craig Hope':         { truthfulness: 58, speed: 45, claims: 18 },
  },
  'man-city': {
    'David Ornstein':     { truthfulness: 90, speed: 82, claims: 25 },
    'Fabrizio Romano':    { truthfulness: 86, speed: 88, claims: 35 },
    'Sam Lee':            { truthfulness: 92, speed: 88, claims: 48 },
    'Jack Gaughan':       { truthfulness: 85, speed: 75, claims: 35 },
    'Simon Stone':        { truthfulness: 84, speed: 45, claims: 20 },
    'Dharmesh Sheth':     { truthfulness: 72, speed: 55, claims: 18 },
    'Ekrem Konur':        { truthfulness: 38, speed: 72, claims: 28 },
    'Nicolo Schira':      { truthfulness: 42, speed: 78, claims: 22 },
  },
  tottenham: {
    'David Ornstein':     { truthfulness: 90, speed: 80, claims: 22 },
    'Fabrizio Romano':    { truthfulness: 85, speed: 88, claims: 30 },
    'Alasdair Gold':      { truthfulness: 84, speed: 80, claims: 55 },
    'Dan KP':             { truthfulness: 78, speed: 72, claims: 40 },
    'Dharmesh Sheth':     { truthfulness: 74, speed: 58, claims: 22 },
    'John Cross':         { truthfulness: 60, speed: 45, claims: 18 },
    'Ekrem Konur':        { truthfulness: 42, speed: 75, claims: 25 },
    'Nicolo Schira':      { truthfulness: 45, speed: 80, claims: 20 },
  },
  newcastle: {
    'David Ornstein':     { truthfulness: 88, speed: 78, claims: 18 },
    'Fabrizio Romano':    { truthfulness: 84, speed: 85, claims: 25 },
    'Craig Hope':         { truthfulness: 75, speed: 70, claims: 42 },
    'Luke Edwards':       { truthfulness: 80, speed: 75, claims: 38 },
    'Keith Downie':       { truthfulness: 78, speed: 72, claims: 45 },
    'Dharmesh Sheth':     { truthfulness: 72, speed: 55, claims: 20 },
    'Ekrem Konur':        { truthfulness: 40, speed: 72, claims: 22 },
  },
  barcelona: {
    'Fabrizio Romano':    { truthfulness: 90, speed: 92, claims: 45 },
    'Matteo Moretto':     { truthfulness: 88, speed: 82, claims: 35 },
    'Gerard Romero':      { truthfulness: 72, speed: 90, claims: 60 },
    'Helena Condis':      { truthfulness: 82, speed: 78, claims: 30 },
    'David Ornstein':     { truthfulness: 85, speed: 65, claims: 12 },
    'Ekrem Konur':        { truthfulness: 45, speed: 80, claims: 35 },
    'Nicolo Schira':      { truthfulness: 48, speed: 82, claims: 28 },
    'Rudy Galetti':       { truthfulness: 42, speed: 75, claims: 22 },
  },
  'real-madrid': {
    'Fabrizio Romano':    { truthfulness: 88, speed: 90, claims: 40 },
    'David Ornstein':     { truthfulness: 82, speed: 60, claims: 10 },
    'Matteo Moretto':     { truthfulness: 85, speed: 80, claims: 28 },
    'Mario Cortegana':    { truthfulness: 90, speed: 85, claims: 45 },
    'Jose Felix Diaz':    { truthfulness: 86, speed: 78, claims: 38 },
    'Ekrem Konur':        { truthfulness: 42, speed: 78, claims: 30 },
    'Nicolo Schira':      { truthfulness: 44, speed: 80, claims: 25 },
  },
  bayern: {
    'Florian Plettenberg': { truthfulness: 92, speed: 90, claims: 55 },
    'Christian Falk':      { truthfulness: 82, speed: 85, claims: 48 },
    'Fabrizio Romano':     { truthfulness: 85, speed: 82, claims: 30 },
    'Kerry Hau':           { truthfulness: 88, speed: 80, claims: 35 },
    'David Ornstein':      { truthfulness: 80, speed: 55, claims: 8 },
    'Ekrem Konur':         { truthfulness: 40, speed: 72, claims: 20 },
    'Nicolo Schira':       { truthfulness: 42, speed: 75, claims: 18 },
  },
  psg: {
    'Fabrizio Romano':    { truthfulness: 86, speed: 88, claims: 35 },
    'Loic Tanzi':         { truthfulness: 88, speed: 85, claims: 42 },
    'Mohamed Bouhafsi':   { truthfulness: 84, speed: 82, claims: 30 },
    'David Ornstein':     { truthfulness: 78, speed: 55, claims: 8 },
    'Matteo Moretto':     { truthfulness: 80, speed: 75, claims: 18 },
    'Ekrem Konur':        { truthfulness: 42, speed: 78, claims: 25 },
    'Nicolo Schira':      { truthfulness: 46, speed: 80, claims: 22 },
    'Rudy Galetti':       { truthfulness: 40, speed: 72, claims: 18 },
  },
  juventus: {
    'Fabrizio Romano':     { truthfulness: 90, speed: 92, claims: 45 },
    'Gianluca Di Marzio':  { truthfulness: 82, speed: 88, claims: 50 },
    'Matteo Moretto':      { truthfulness: 86, speed: 80, claims: 32 },
    'Romeo Agresti':       { truthfulness: 92, speed: 88, claims: 55 },
    'David Ornstein':      { truthfulness: 78, speed: 50, claims: 6 },
    'Ekrem Konur':         { truthfulness: 44, speed: 78, claims: 22 },
    'Nicolo Schira':       { truthfulness: 50, speed: 82, claims: 30 },
    'Rudy Galetti':        { truthfulness: 45, speed: 75, claims: 25 },
  },
}

// Global journalist data (used for "All Clubs")
const ALL_JOURNALISTS = [
  { name: 'David Ornstein', publication: 'The Athletic', truthfulness: 91, speed: 85, claims: 142 },
  { name: 'Fabrizio Romano', publication: 'The Guardian', truthfulness: 88, speed: 92, claims: 310 },
  { name: 'Florian Plettenberg', publication: 'Sky Germany', truthfulness: 80, speed: 75, claims: 95 },
  { name: 'Matteo Moretto', publication: 'Relevo', truthfulness: 84, speed: 78, claims: 68 },
  { name: 'Ben Jacobs', publication: 'CBS Sports', truthfulness: 72, speed: 68, claims: 87 },
  { name: 'Charles Watts', publication: 'Goal', truthfulness: 78, speed: 70, claims: 54 },
  { name: 'Dharmesh Sheth', publication: 'Sky Sports', truthfulness: 75, speed: 60, claims: 120 },
  { name: 'Gianluca Di Marzio', publication: 'Sky Sport Italia', truthfulness: 70, speed: 82, claims: 180 },
  { name: 'John Cross', publication: 'Daily Mirror', truthfulness: 62, speed: 45, claims: 95 },
  { name: 'Sami Mokbel', publication: 'Daily Mail', truthfulness: 65, speed: 50, claims: 78 },
  { name: 'Simon Stone', publication: 'BBC Sport', truthfulness: 82, speed: 40, claims: 45 },
  { name: 'Julien Laurens', publication: 'ESPN', truthfulness: 58, speed: 55, claims: 62 },
  { name: 'Dean Jones', publication: 'GiveMeSport', truthfulness: 60, speed: 52, claims: 48 },
  { name: 'Graeme Bailey', publication: '90min', truthfulness: 55, speed: 58, claims: 72 },
  { name: 'Ekrem Konur', publication: 'CaughtOffside', truthfulness: 42, speed: 78, claims: 220 },
  { name: 'Rudy Galetti', publication: 'Sportitalia', truthfulness: 38, speed: 72, claims: 185 },
  { name: 'Christian Falk', publication: 'BILD', truthfulness: 68, speed: 70, claims: 88 },
  { name: 'Nicolo Schira', publication: 'Various', truthfulness: 45, speed: 80, claims: 250 },
  { name: 'Pipe Sierra', publication: 'Win Sports', truthfulness: 50, speed: 65, claims: 35 },
  { name: 'James Ducker', publication: 'The Telegraph', truthfulness: 76, speed: 42, claims: 52 },
  { name: 'Sam Dean', publication: 'The Telegraph', truthfulness: 73, speed: 38, claims: 40 },
  { name: 'Mark Ogden', publication: 'ESPN', truthfulness: 64, speed: 35, claims: 55 },
  { name: 'David Lynch', publication: 'The Athletic', truthfulness: 79, speed: 48, claims: 32 },
  { name: 'Chris Wheatley', publication: 'Football.london', truthfulness: 71, speed: 62, claims: 44 },
  { name: 'Kaveh Solhekol', publication: 'Sky Sports', truthfulness: 69, speed: 55, claims: 85 },
  { name: 'Craig Hope', publication: 'Daily Mail', truthfulness: 61, speed: 48, claims: 60 },
  { name: 'Pete O\'Rourke', publication: 'Football Insider', truthfulness: 48, speed: 70, claims: 155 },
  { name: 'Jason Burt', publication: 'The Telegraph', truthfulness: 74, speed: 36, claims: 38 },
]

// Extra per-club journalists not in the global list (club-specific reporters)
const CLUB_ONLY_JOURNALISTS = {
  chelsea: { 'Nizaar Kinsella': 'Standard Sport' },
  liverpool: { 'James Pearce': 'The Athletic', 'Paul Joyce': 'The Times' },
  'man-utd': { 'Laurie Whitwell': 'The Athletic' },
  'man-city': { 'Sam Lee': 'The Athletic', 'Jack Gaughan': 'Daily Mail' },
  tottenham: { 'Alasdair Gold': 'Football.london', 'Dan KP': 'Standard Sport' },
  newcastle: { 'Luke Edwards': 'The Telegraph', 'Keith Downie': 'Sky Sports' },
  barcelona: { 'Gerard Romero': 'Jijantes FC', 'Helena Condis': 'COPE' },
  'real-madrid': { 'Mario Cortegana': 'The Athletic', 'Jose Felix Diaz': 'Marca' },
  bayern: { 'Kerry Hau': 'Sky Germany' },
  psg: { 'Loic Tanzi': 'RMC Sport', 'Mohamed Bouhafsi': 'RMC Sport' },
  juventus: { 'Romeo Agresti': 'Goal Italia' },
}

function getJournalistsForClub(clubId) {
  if (clubId === 'all') return ALL_JOURNALISTS

  const clubData = CLUB_DATA[clubId]
  if (!clubData) return ALL_JOURNALISTS

  const clubPubs = CLUB_ONLY_JOURNALISTS[clubId] || {}

  return Object.entries(clubData).map(([name, stats]) => {
    // Find the global journalist for their publication
    const global = ALL_JOURNALISTS.find(j => j.name === name)
    return {
      name,
      publication: global?.publication || clubPubs[name] || '',
      ...stats,
    }
  })
}

function aggregatePublications(journalists) {
  const pubMap = {}
  for (const j of journalists) {
    const pub = j.publication || 'Other'
    if (!pubMap[pub]) {
      pubMap[pub] = { name: pub, truthScores: [], speedScores: [], totalClaims: 0, count: 0 }
    }
    pubMap[pub].truthScores.push(j.truthfulness)
    pubMap[pub].speedScores.push(j.speed)
    pubMap[pub].totalClaims += j.claims
    pubMap[pub].count++
  }
  return Object.values(pubMap).map(p => ({
    name: p.name,
    truthfulness: Math.round(p.truthScores.reduce((a, b) => a + b, 0) / p.count),
    speed: Math.round(p.speedScores.reduce((a, b) => a + b, 0) / p.count),
    claims: p.totalClaims,
    journalists: p.count,
  }))
}

// ── Colors ──────────────────────────────────────────────────

const QUADRANT_LABELS = {
  topRight: { label: 'The Gold Standard', sub: 'Fast & Accurate', color: '#22c55e' },
  topLeft: { label: 'Speed Over Substance', sub: 'Fast but Unreliable', color: '#f59e0b' },
  bottomRight: { label: 'Slow but Steady', sub: 'Accurate but Late', color: '#3b82f6' },
  bottomLeft: { label: 'Why Bother?', sub: 'Slow & Unreliable', color: '#ef4444' },
}

function getDotColor(truthfulness, speed) {
  if (truthfulness >= 65 && speed >= 55) return '#22c55e'
  if (truthfulness < 65 && speed >= 55) return '#f59e0b'
  if (truthfulness >= 65 && speed < 55) return '#3b82f6'
  return '#ef4444'
}

// ── Tooltip ──────────────────────────────────────────────────

const MatrixTooltip = ({ active, payload, viewMode, clubName }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null

  const color = getDotColor(d.truthfulness, d.speed)

  return (
    <div
      className="border rounded-xl shadow-elevation-2 pointer-events-none"
      style={{ background: '#18181b', borderColor: color + '40', padding: 16, maxWidth: 280 }}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="w-3 h-3 rounded-full" style={{ background: color }} />
        <span className="text-sm font-sans font-bold text-zinc-100">{d.name}</span>
      </div>

      {viewMode === 'journalists' && d.publication && (
        <div className="text-xs font-sans text-zinc-500 mb-3">{d.publication}</div>
      )}
      {viewMode === 'publications' && d.journalists && (
        <div className="text-xs font-sans text-zinc-500 mb-3">{d.journalists} journalist{d.journalists > 1 ? 's' : ''}</div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <div className="text-xs font-sans text-zinc-500 uppercase tracking-wide mb-0.5">Accuracy</div>
          <div className="text-lg font-mono font-bold" style={{ color }}>{d.truthfulness}%</div>
        </div>
        <div>
          <div className="text-xs font-sans text-zinc-500 uppercase tracking-wide mb-0.5">Speed</div>
          <div className="text-lg font-mono font-bold" style={{ color }}>{d.speed}%</div>
        </div>
      </div>

      <div className="mt-3 pt-2 border-t border-zinc-800 text-xs font-mono text-zinc-500">
        {d.claims} {clubName !== 'All Clubs' ? clubName + ' ' : ''}claims tracked
      </div>
    </div>
  )
}

// ── Main component ──────────────────────────────────────────

const ReliabilityMatrixPage = () => {
  const [viewMode, setViewMode] = useState('journalists')
  const [selectedClub, setSelectedClub] = useState('all')
  const [hoveredDot, setHoveredDot] = useState(null)

  const clubName = CLUBS.find(c => c.id === selectedClub)?.name || 'All Clubs'

  const journalists = useMemo(() => getJournalistsForClub(selectedClub), [selectedClub])
  const publications = useMemo(() => aggregatePublications(journalists), [journalists])

  const data = viewMode === 'journalists' ? journalists : publications

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-5xl md:text-6xl font-display text-zinc-100 mb-3 tracking-tight">
          Reliability Matrix
        </h1>
        <p className="text-zinc-500 font-sans text-base max-w-2xl leading-relaxed">
          Every football journalist and publication plotted on two axes:
          how accurate are they, and how fast do they break stories?
          {selectedClub !== 'all' && (
            <span className="text-zinc-300"> Filtered to <strong>{clubName}</strong> rumours only.</span>
          )}
        </p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4 mb-8">
        {/* View toggle */}
        <div className="inline-flex bg-surface-1 border border-edge rounded-lg p-1">
          <button
            onClick={() => setViewMode('journalists')}
            className={`px-4 py-2 text-sm font-sans font-medium rounded-md transition-all ${
              viewMode === 'journalists'
                ? 'bg-accent text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Journalists
          </button>
          <button
            onClick={() => setViewMode('publications')}
            className={`px-4 py-2 text-sm font-sans font-medium rounded-md transition-all ${
              viewMode === 'publications'
                ? 'bg-accent text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Publications
          </button>
        </div>

        {/* Club filter */}
        <div className="relative">
          <select
            value={selectedClub}
            onChange={(e) => { setSelectedClub(e.target.value); setHoveredDot(null) }}
            className="appearance-none bg-surface-1 border border-edge rounded-lg px-4 py-2.5 pr-10 text-sm font-sans text-zinc-200 cursor-pointer hover:border-edge-hover transition-colors focus:outline-none focus:border-accent"
          >
            {CLUBS.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <svg
            className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none"
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>

        <span className="text-xs font-sans text-zinc-600">
          {data.length} {viewMode} · bubble size = claim volume
        </span>
      </div>

      {/* Chart */}
      <div className="bg-surface-1 border border-edge rounded-xl shadow-elevation-1 p-6">
        {/* Quadrant legend */}
        <div className="flex flex-wrap gap-6 mb-6">
          {Object.values(QUADRANT_LABELS).map((q) => (
            <div key={q.label} className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ background: q.color }} />
              <div>
                <span className="text-xs font-sans font-semibold text-zinc-300">{q.label}</span>
                <span className="text-xs font-sans text-zinc-600 ml-1.5">{q.sub}</span>
              </div>
            </div>
          ))}
        </div>

        <ResponsiveContainer width="100%" height={560}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
            <XAxis
              type="number"
              dataKey="truthfulness"
              name="Accuracy"
              domain={[25, 100]}
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
              dataKey="speed"
              name="Speed"
              domain={[25, 100]}
              tick={{ fill: '#a1a1aa', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              axisLine={{ stroke: '#2e2e33' }}
              tickLine={false}
              label={{
                value: 'Speed (% stories broken first)',
                angle: -90,
                position: 'insideLeft',
                offset: 0,
                style: { fill: '#71717a', fontSize: 12, fontFamily: 'DM Sans' },
              }}
            />
            <ZAxis
              type="number"
              dataKey="claims"
              range={[viewMode === 'journalists' ? 80 : 150, viewMode === 'journalists' ? 600 : 1200]}
              name="Claims"
            />

            {/* Quadrant divider lines */}
            <ReferenceLine x={65} stroke="#2e2e33" strokeDasharray="6 4" />
            <ReferenceLine y={55} stroke="#2e2e33" strokeDasharray="6 4" />

            <Tooltip
              content={<MatrixTooltip viewMode={viewMode} clubName={clubName} />}
              cursor={false}
            />

            <Scatter data={data} fillOpacity={0.85}>
              {data.map((entry, i) => (
                <Cell
                  key={`${selectedClub}-${viewMode}-${i}`}
                  fill={getDotColor(entry.truthfulness, entry.speed)}
                  stroke={getDotColor(entry.truthfulness, entry.speed)}
                  strokeOpacity={0.3}
                  strokeWidth={hoveredDot === i ? 8 : 0}
                  style={{ cursor: 'pointer', transition: 'stroke-width 0.2s' }}
                  onMouseEnter={() => setHoveredDot(i)}
                  onMouseLeave={() => setHoveredDot(null)}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>

        {/* Name labels below chart */}
        <div className="mt-6 pt-4 border-t border-edge">
          <div className="flex flex-wrap gap-x-5 gap-y-2">
            {[...data]
              .sort((a, b) => (b.truthfulness + b.speed) - (a.truthfulness + a.speed))
              .map((d) => {
                const idx = data.indexOf(d)
                return (
                  <div
                    key={`${selectedClub}-${d.name}`}
                    className="flex items-center gap-1.5 text-xs font-sans text-zinc-500 hover:text-zinc-200 transition-colors cursor-default"
                    onMouseEnter={() => setHoveredDot(idx)}
                    onMouseLeave={() => setHoveredDot(null)}
                  >
                    <span
                      className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{ background: getDotColor(d.truthfulness, d.speed) }}
                    />
                    <span className={hoveredDot === idx ? 'text-zinc-100 font-medium' : ''}>
                      {d.name}
                    </span>
                    <span className="font-mono text-zinc-700 text-[10px]">
                      {d.truthfulness}/{d.speed}
                    </span>
                  </div>
                )
              })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReliabilityMatrixPage
