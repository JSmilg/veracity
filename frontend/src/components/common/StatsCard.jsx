const StatsCard = ({ title, value, subtitle, color = 'accent', trend }) => {
  const colorMap = {
    accent: '#6366f1',
    verified: '#22c55e',
    refuted: '#ef4444',
    partial: '#f59e0b',
    pending: '#a1a1aa',
  }

  const borderColor = colorMap[color] || colorMap.accent

  return (
    <div
      className="bg-surface-1 border border-edge rounded-xl p-6 transition-all duration-300 hover:shadow-elevation-2"
      style={{ borderLeftWidth: '3px', borderLeftColor: borderColor }}
    >
      <div className="text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider mb-3">
        {title}
      </div>

      <div className="text-4xl font-mono font-bold text-zinc-100 tabular-nums mb-1">
        {value?.toLocaleString() || value}
      </div>

      {subtitle && (
        <div className="text-sm text-zinc-500 font-sans">
          {subtitle}
        </div>
      )}

      {trend && (
        <div className={`mt-3 inline-flex items-center gap-1 text-sm font-sans font-semibold px-2 py-1 rounded ${
          trend > 0
            ? 'text-verified bg-verified/10 border border-verified/25'
            : 'text-refuted bg-refuted/10 border border-refuted/25'
        }`}>
          <span>{trend > 0 ? '\u2191' : '\u2193'}</span>
          {Math.abs(trend)}%
        </div>
      )}
    </div>
  )
}

export default StatsCard
