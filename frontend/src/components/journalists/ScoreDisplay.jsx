import { formatScore, getScoreBarColor } from '../../utils/formatters'
import { useEffect, useState } from 'react'

const ScoreDisplay = ({
  score,
  label,
  size = 'md',
  showProgressRing = true,
}) => {
  const [displayScore, setDisplayScore] = useState(0)
  const [hasAnimated, setHasAnimated] = useState(false)

  // Count-up animation on mount
  useEffect(() => {
    if (!hasAnimated) {
      let start = 0
      const duration = 1000
      const increment = score / (duration / 16)

      const timer = setInterval(() => {
        start += increment
        if (start >= score) {
          setDisplayScore(score)
          clearInterval(timer)
          setHasAnimated(true)
        } else {
          setDisplayScore(Math.floor(start))
        }
      }, 16)

      return () => clearInterval(timer)
    } else {
      setDisplayScore(score)
    }
  }, [score, hasAnimated])

  const sizeClasses = {
    sm: {
      container: 'w-24 h-24',
      text: 'text-3xl',
      percentText: 'text-lg',
      strokeWidth: 4,
      radius: 40,
    },
    md: {
      container: 'w-36 h-36',
      text: 'text-5xl',
      percentText: 'text-2xl',
      strokeWidth: 6,
      radius: 60,
    },
    lg: {
      container: 'w-48 h-48',
      text: 'text-7xl',
      percentText: 'text-3xl',
      strokeWidth: 8,
      radius: 84,
    },
    massive: {
      container: 'w-80 h-80 md:w-96 md:h-96',
      text: 'text-8xl md:text-9xl',
      percentText: 'text-4xl md:text-5xl',
      strokeWidth: 10,
      radius: 140,
    },
  }

  const { container, text, percentText, strokeWidth, radius } = sizeClasses[size]

  const circumference = 2 * Math.PI * radius
  const progress = (score / 100) * circumference
  const remainingProgress = circumference - progress

  const tierColor = getScoreBarColor(score)

  return (
    <div className="text-center">
      <div className="relative inline-flex items-center justify-center">
        {showProgressRing && (
          <svg
            className={`${container} transform -rotate-90`}
            viewBox={`0 0 ${(radius + strokeWidth) * 2} ${(radius + strokeWidth) * 2}`}
          >
            {/* Background track */}
            <circle
              cx={radius + strokeWidth}
              cy={radius + strokeWidth}
              r={radius}
              stroke="#27272b"
              strokeWidth={strokeWidth}
              fill="none"
            />
            {/* Progress arc */}
            <circle
              cx={radius + strokeWidth}
              cy={radius + strokeWidth}
              r={radius}
              stroke={tierColor}
              strokeWidth={strokeWidth}
              fill="none"
              strokeDasharray={`${progress} ${remainingProgress}`}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
        )}

        {/* Score number */}
        <div className={`${showProgressRing ? 'absolute' : ''} flex flex-col items-center justify-center`}>
          <span className={`${text} font-mono font-bold text-zinc-100 tabular-nums`}>
            {formatScore(displayScore, 0)}
            <span className={percentText}>%</span>
          </span>
        </div>
      </div>

      {/* Label */}
      {label && (
        <p className="text-sm md:text-base text-zinc-500 font-sans font-semibold mt-4 uppercase tracking-wider">
          {label}
        </p>
      )}
    </div>
  )
}

export default ScoreDisplay
