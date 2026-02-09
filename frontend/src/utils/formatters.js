import { format, formatDistanceToNow, parseISO } from 'date-fns'

/**
 * Format date to readable string
 */
export const formatDate = (date, formatStr = 'MMM d, yyyy') => {
  if (!date) return ''
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return format(dateObj, formatStr)
}

/**
 * Format date as time ago (e.g., "2 hours ago")
 */
export const formatTimeAgo = (date) => {
  if (!date) return ''
  const dateObj = typeof date === 'string' ? parseISO(date) : date
  return formatDistanceToNow(dateObj, { addSuffix: true })
}

/**
 * Format score as percentage
 */
export const formatScore = (score, decimals = 2) => {
  if (score === null || score === undefined) return '0.00%'
  const numScore = typeof score === 'string' ? parseFloat(score) : score
  return `${numScore.toFixed(decimals)}%`
}

/**
 * Get text color class for score tier
 */
export const getScoreColor = (score) => {
  const numScore = typeof score === 'string' ? parseFloat(score) : score
  if (numScore >= 80) return 'text-score-excellent'
  if (numScore >= 60) return 'text-score-good'
  if (numScore >= 40) return 'text-score-fair'
  return 'text-score-poor'
}

/**
 * Get background color class for score tier
 */
export const getScoreBgColor = (score) => {
  const numScore = typeof score === 'string' ? parseFloat(score) : score
  if (numScore >= 80) return 'bg-score-excellent/15'
  if (numScore >= 60) return 'bg-score-good/15'
  if (numScore >= 40) return 'bg-score-fair/15'
  return 'bg-score-poor/15'
}

/**
 * Get hex color string for score tier (for inline styles)
 */
export const getScoreBarColor = (score) => {
  const numScore = typeof score === 'string' ? parseFloat(score) : score
  if (numScore >= 80) return '#22c55e'
  if (numScore >= 60) return '#3b82f6'
  if (numScore >= 40) return '#f59e0b'
  return '#ef4444'
}

/**
 * Truncate text to specified length
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
