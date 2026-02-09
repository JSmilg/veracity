import { Link } from 'react-router-dom'
import { formatDate } from '../../utils/formatters'

const ICONS = {
  first_rumour: (
    <svg className="w-5 h-5 text-warm" fill="currentColor" viewBox="0 0 20 20">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
    </svg>
  ),
  first_confirmed: (
    <svg className="w-5 h-5 text-verified" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  major_journalist: (
    <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
    </svg>
  ),
}

const LABELS = {
  first_rumour: 'First Rumour',
  first_confirmed: 'Deal Confirmed',
  major_journalist: 'Joined Story',
}

const KeyMomentCard = ({ moment, type }) => {
  if (!moment) return null

  return (
    <div className="bg-surface-2/50 rounded-lg p-4 border border-edge">
      <div className="flex items-center gap-2 mb-2">
        {ICONS[type]}
        <span className="text-xs font-sans uppercase tracking-wide text-zinc-500">
          {LABELS[type]}
        </span>
      </div>
      <Link
        to={`/journalist/${moment.journalist_slug}`}
        className="text-sm font-sans font-semibold text-zinc-100 hover:text-accent transition-colors"
      >
        {moment.journalist_name}
      </Link>
      {moment.publication && (
        <div className="text-xs text-zinc-500 font-sans mt-0.5">{moment.publication}</div>
      )}
      <div className="text-xs text-zinc-500 font-mono mt-1">
        {formatDate(moment.date, 'd MMM yyyy')}
      </div>
    </div>
  )
}

export default KeyMomentCard
