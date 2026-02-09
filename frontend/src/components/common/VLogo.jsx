import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'

const domains = [
  {
    key: 'hollywood',
    label: 'Hollywood',
    color: '#f59e0b',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
    ),
  },
  {
    key: 'politics',
    label: 'Politics',
    color: '#ef4444',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
    ),
  },
  {
    key: 'tech',
    label: 'Tech',
    color: '#06b6d4',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    ),
  },
  {
    key: 'wall-st',
    label: 'Wall St',
    color: '#22c55e',
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    ),
  },
]

const VLogo = () => {
  const [open, setOpen] = useState(false)
  const timeoutRef = useRef(null)
  const containerRef = useRef(null)

  const handleEnter = () => {
    clearTimeout(timeoutRef.current)
    setOpen(true)
  }

  const handleLeave = () => {
    timeoutRef.current = setTimeout(() => setOpen(false), 150)
  }

  useEffect(() => {
    return () => clearTimeout(timeoutRef.current)
  }, [])

  return (
    <div
      ref={containerRef}
      className="relative"
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
    >
      <Link to="/" className="inline-flex items-center gap-1.5 group">
        <span className="text-2xl font-display text-zinc-100 tracking-tight cursor-pointer select-none">
          Veracity
        </span>
        <svg
          className={`w-3 h-3 text-zinc-500 group-hover:text-zinc-300 transition-all duration-200 ${open ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={3}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </Link>

      {/* Dropdown */}
      <div
        className={`absolute top-full left-0 mt-2 w-64 bg-surface-1 border border-edge rounded-xl shadow-2xl shadow-black/40 p-3 z-50 transition-all duration-200 origin-top-left ${
          open
            ? 'opacity-100 scale-100 pointer-events-auto'
            : 'opacity-0 scale-95 pointer-events-none'
        }`}
      >
          <div className="grid grid-cols-2 gap-2">
            {domains.map((d) => (
              <Link
                key={d.key}
                to={`/coming-soon/${d.key}`}
                className="group flex flex-col items-center gap-2 p-3 rounded-lg border border-edge hover:border-opacity-60 transition-all duration-200 bg-surface-2 hover:bg-surface-2/80"
                style={{ '--domain-color': d.color }}
                onClick={() => setOpen(false)}
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors duration-200"
                  style={{ backgroundColor: `${d.color}20` }}
                >
                  <svg
                    className="w-4 h-4 transition-colors duration-200"
                    style={{ color: d.color }}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    {d.icon}
                  </svg>
                </div>
                <div className="text-center">
                  <div className="text-base font-display text-zinc-100 group-hover:text-white tracking-wide transition-colors leading-tight">
                    Veracity<br />{d.label}
                  </div>
                  <span
                    className="inline-block mt-1 px-1.5 py-0.5 rounded-full text-[10px] font-sans font-semibold uppercase tracking-wider"
                    style={{
                      backgroundColor: `${d.color}15`,
                      color: d.color,
                    }}
                  >
                    Coming Soon
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
    </div>
  )
}

export default VLogo
