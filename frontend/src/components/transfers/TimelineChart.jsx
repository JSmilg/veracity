import { useState, useCallback } from 'react'
import {
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { formatDate } from '../../utils/formatters'

const COLORS = {
  accent: '#6366f1',
  verified: '#22c55e',
  warm: '#f97316',
  edge: '#2e2e33',
  zinc400: '#a1a1aa',
  zinc500: '#71717a',
  surface1: '#18181b',
  surface2: '#1f1f23',
}

// Certainty levels ordered from lowest to highest (6-tier taxonomy)
const CERTAINTY_ORDER = [
  'tier_6_speculation',
  'tier_5_early_intent',
  'tier_4_concrete_interest',
  'tier_3_active',
  'tier_2_advanced',
  'tier_1_done_deal',
]
const CERTAINTY_NUMERIC = {
  tier_6_speculation: 1,
  tier_5_early_intent: 2,
  tier_4_concrete_interest: 3,
  tier_3_active: 4,
  tier_2_advanced: 5,
  tier_1_done_deal: 6,
}
const CERTAINTY_LABELS = {
  1: 'Speculation',
  2: 'Early Intent',
  3: 'Concrete Interest',
  4: 'Active Talks',
  5: 'Advanced',
  6: 'Done Deal',
}
const CERTAINTY_COLORS = {
  1: '#8b5cf6',  // purple
  2: '#3b82f6',  // blue
  3: '#22c55e',  // green
  4: '#eab308',  // yellow
  5: '#f97316',  // orange
  6: '#ef4444',  // red
}

// Compute the running max certainty level for each date
function computeCertaintyTrack(dailyCounts, claims) {
  if (!claims?.length) return dailyCounts.map(() => 0)

  // Build a map: date → highest certainty numeric value on that date
  const dateCertainty = {}
  for (const c of claims) {
    const date = c.claim_date.split('T')[0]
    const val = CERTAINTY_NUMERIC[c.certainty_level] || 0
    dateCertainty[date] = Math.max(dateCertainty[date] || 0, val)
  }

  // Running maximum across the timeline
  let runningMax = 0
  return dailyCounts.map(d => {
    const dayCertainty = dateCertainty[d.date] || 0
    runningMax = Math.max(runningMax, dayCertainty)
    return runningMax
  })
}

function computeRollingSum(dailyCounts, window = 7) {
  return dailyCounts.map((d, i) => {
    const start = Math.max(0, i - window + 1)
    const slice = dailyCounts.slice(start, i + 1)
    const sum = slice.reduce((acc, x) => acc + x.count, 0)
    return { ...d, rolling: sum }
  })
}

function mergeChartData(smoothed, milestones, certaintyTrack) {
  const milestoneMap = {}
  for (const m of milestones) {
    milestoneMap[m.date] = m
  }
  return smoothed.map((d, i) => ({
    ...d,
    milestone: milestoneMap[d.date] || null,
    certainty: certaintyTrack[i] || 0,
  }))
}

// Custom dot: larger + colored for milestones, invisible otherwise
const ChartDot = (props) => {
  const { cx, cy, payload } = props
  if (!payload?.milestone) return null

  const m = payload.milestone
  return (
    <g>
      <circle cx={cx} cy={cy} r={10} fill={m.color} fillOpacity={0.15} />
      <circle cx={cx} cy={cy} r={6} fill={m.color} stroke="#fff" strokeWidth={2} />
    </g>
  )
}

// Active dot on hover: bigger glow
const ActiveDot = (props) => {
  const { cx, cy, payload } = props
  const color = payload?.milestone ? payload.milestone.color : COLORS.accent
  return (
    <g>
      <circle cx={cx} cy={cy} r={14} fill={color} fillOpacity={0.15} />
      <circle cx={cx} cy={cy} r={7} fill={color} stroke="#fff" strokeWidth={2} />
    </g>
  )
}

const MilestoneTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null

  const data = payload[0]?.payload
  const milestone = data?.milestone

  return (
    <div
      className="border rounded-xl shadow-elevation-2 pointer-events-none"
      style={{
        background: COLORS.surface1,
        borderColor: milestone ? milestone.color + '40' : COLORS.edge,
        padding: milestone ? '16px' : '12px',
        maxWidth: 320,
      }}
    >
      <div className="text-xs font-sans mb-1" style={{ color: COLORS.zinc500 }}>
        {formatDate(label, 'EEEE, d MMMM yyyy')}
      </div>

      {milestone ? (
        <>
          <div className="flex items-center gap-2 mb-2">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ background: milestone.color }}
            />
            <span className="text-sm font-sans font-bold text-zinc-100">
              {milestone.label}
            </span>
          </div>
          <p className="text-xs font-sans text-zinc-400 leading-relaxed mb-2">
            {milestone.detail}
          </p>
          {milestone.journalist && (
            <div className="text-xs font-sans text-zinc-500">
              {milestone.journalist}
              {milestone.publication ? ` — ${milestone.publication}` : ''}
            </div>
          )}
          <div className="mt-2 pt-2 border-t border-edge text-xs font-mono text-zinc-500">
            {data.count} {data.count === 1 ? 'claim' : 'claims'} this day · {data.rolling} in past 14 days
          </div>
        </>
      ) : (
        <div className="text-sm font-mono font-bold text-zinc-100">
          {data.count} {data.count === 1 ? 'claim' : 'claims'} this day
          <span className="text-xs font-normal text-zinc-500 ml-2">
            ({data.rolling} in past 14 days)
          </span>
        </div>
      )}

      {data.certainty > 0 && (
        <div className="flex items-center gap-2 mt-2 pt-2 border-t border-edge">
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ background: CERTAINTY_COLORS[data.certainty] }}
          />
          <span className="text-xs font-sans" style={{ color: CERTAINTY_COLORS[data.certainty] }}>
            Peak certainty: {CERTAINTY_LABELS[data.certainty]}
          </span>
        </div>
      )}
    </div>
  )
}

// Custom tick for certainty Y-axis: show level labels
const CertaintyTick = ({ x, y, payload }) => {
  const label = CERTAINTY_LABELS[payload.value]
  if (!label) return null
  const color = CERTAINTY_COLORS[payload.value] || COLORS.zinc500
  return (
    <text x={x} y={y} dy={4} textAnchor="start" fill={color} fontSize={9} fontFamily="DM Sans">
      {label}
    </text>
  )
}

// Build a horizontal gradient that changes color at each certainty transition
function buildCertaintyGradientStops(certaintyTrack) {
  if (!certaintyTrack.length) return []
  const stops = []
  const len = certaintyTrack.length
  for (let i = 0; i < len; i++) {
    const val = certaintyTrack[i]
    const prev = i > 0 ? certaintyTrack[i - 1] : val
    const pct = len === 1 ? 0 : i / (len - 1)
    // Add a stop at the transition point with the new color
    if (val !== prev) {
      stops.push({ offset: pct, color: CERTAINTY_COLORS[val] || CERTAINTY_COLORS[1] })
    } else if (i === 0) {
      stops.push({ offset: 0, color: CERTAINTY_COLORS[val] || CERTAINTY_COLORS[1] })
    }
  }
  // Ensure we have an end stop
  const lastVal = certaintyTrack[certaintyTrack.length - 1]
  const lastStop = stops[stops.length - 1]
  if (!lastStop || lastStop.offset < 1) {
    stops.push({ offset: 1, color: CERTAINTY_COLORS[lastVal] || CERTAINTY_COLORS[1] })
  }
  return stops
}

const TimelineChart = ({ dailyCounts, milestones = [], claims = [] }) => {
  if (!dailyCounts?.length) {
    return (
      <div className="flex items-center justify-center h-[400px] text-zinc-500 font-sans text-sm">
        No timeline data available
      </div>
    )
  }

  const smoothed = computeRollingSum(dailyCounts, 14)
  const certaintyTrack = computeCertaintyTrack(dailyCounts, claims)
  const chartData = mergeChartData(smoothed, milestones, certaintyTrack)
  const certaintyStops = buildCertaintyGradientStops(certaintyTrack)

  const formatTick = (dateStr) => formatDate(dateStr, 'MMM yy')

  // Show ~6-8 ticks max
  const tickInterval = Math.max(1, Math.floor(chartData.length / 7))

  const hasCertainty = Math.max(...certaintyTrack, 0) > 0

  return (
    <div>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData} margin={{ top: 20, right: hasCertainty ? 10 : 20, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="accentGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={COLORS.accent} stopOpacity={0.25} />
              <stop offset="100%" stopColor={COLORS.accent} stopOpacity={0} />
            </linearGradient>
            {/* Horizontal gradient for certainty stroke — color changes with tier */}
            <linearGradient id="certaintyStrokeGradient" x1="0" y1="0" x2="1" y2="0">
              {certaintyStops.map((s, i) => (
                <stop key={i} offset={`${(s.offset * 100).toFixed(2)}%`} stopColor={s.color} stopOpacity={0.9} />
              ))}
            </linearGradient>
            {/* Vertical fill gradient that uses the stroke gradient color at top, fading to transparent */}
            <linearGradient id="certaintyFillGradient" x1="0" y1="0" x2="1" y2="0">
              {certaintyStops.map((s, i) => (
                <stop key={i} offset={`${(s.offset * 100).toFixed(2)}%`} stopColor={s.color} stopOpacity={0.1} />
              ))}
            </linearGradient>
          </defs>

          <XAxis
            dataKey="date"
            tickFormatter={formatTick}
            tick={{ fill: COLORS.zinc400, fontSize: 11, fontFamily: 'DM Sans' }}
            axisLine={{ stroke: COLORS.edge }}
            tickLine={false}
            interval={tickInterval}
          />

          {/* Left Y-axis: claim volume */}
          <YAxis
            yAxisId="volume"
            dataKey="rolling"
            allowDecimals={false}
            tick={{ fill: COLORS.zinc400, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            axisLine={false}
            tickLine={false}
            label={{
              value: 'Claims (14-day rolling)',
              angle: -90,
              position: 'insideLeft',
              offset: 30,
              style: { fill: COLORS.zinc500, fontSize: 10, fontFamily: 'DM Sans' },
            }}
          />

          {/* Right Y-axis: certainty level */}
          {hasCertainty && (
            <YAxis
              yAxisId="certainty"
              orientation="right"
              domain={[0, 6.5]}
              ticks={[1, 2, 3, 4, 5, 6]}
              tick={<CertaintyTick />}
              axisLine={false}
              tickLine={false}
              width={80}
            />
          )}

          <Tooltip
            content={<MilestoneTooltip />}
            cursor={{ stroke: COLORS.edge, strokeDasharray: '4 4' }}
          />

          {/* Certainty step area (rendered first so it sits behind) */}
          {hasCertainty && (
            <Area
              yAxisId="certainty"
              type="stepAfter"
              dataKey="certainty"
              stroke="url(#certaintyStrokeGradient)"
              strokeWidth={1.5}
              fill="url(#certaintyFillGradient)"
              dot={false}
              activeDot={false}
              isAnimationActive={true}
            />
          )}

          {/* Claim volume area (rendered on top) */}
          <Area
            yAxisId="volume"
            type="monotone"
            dataKey="rolling"
            stroke={COLORS.accent}
            strokeWidth={2}
            fill="url(#accentGradient)"
            dot={<ChartDot />}
            activeDot={<ActiveDot />}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Dual legend */}
      {hasCertainty && (
        <div className="flex items-center gap-6 mt-3">
          <div className="flex items-center gap-1.5 text-xs font-sans text-zinc-500">
            <span className="w-4 h-0.5 rounded-full flex-shrink-0" style={{ background: COLORS.accent }} />
            Claim volume
          </div>
          <div className="flex-1 h-px bg-edge" />
          {CERTAINTY_ORDER.map((level, i) => (
            <div key={level} className="flex items-center gap-1.5 text-xs font-sans" style={{ color: CERTAINTY_COLORS[i + 1] }}>
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: CERTAINTY_COLORS[i + 1] }} />
              {CERTAINTY_LABELS[i + 1]}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default TimelineChart
