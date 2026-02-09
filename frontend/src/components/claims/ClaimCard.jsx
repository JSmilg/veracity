import { Link } from 'react-router-dom'
import { formatDate, formatTimeAgo } from '../../utils/formatters'
import StatusBadge from './StatusBadge'

const ClaimCard = ({ claim, onEdit, onDelete }) => {
  return (
    <div className="bg-surface-1 border border-edge rounded-xl shadow-elevation-1 hover:shadow-elevation-2 transition-all duration-300 animate-scale-in">
      <div className="p-6">
        {/* Header: Journalist and Status */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-grow">
            <div className="flex items-center space-x-2 mb-1">
              <Link
                to={`/journalist/${claim.journalist_slug}`}
                className="font-semibold text-zinc-100 hover:text-accent transition-colors font-sans"
              >
                {claim.journalist_name}
              </Link>
              {claim.is_first_claim && (
                <span className="inline-flex items-center px-2 py-0.5 bg-warm/10 text-warm text-xs font-sans font-semibold rounded-md border border-warm/25">
                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  FIRST
                </span>
              )}
            </div>
            <div className="flex items-center text-xs text-zinc-500 space-x-2 font-sans">
              <span className="font-medium">{claim.publication}</span>
              <span className="text-zinc-700">&middot;</span>
              <span>{formatDate(claim.claim_date, 'd MMM yyyy')}</span>
              <span className="text-zinc-700">&middot;</span>
              <span>{formatTimeAgo(claim.claim_date)}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge status={claim.validation_status} />
            {onEdit && (
              <button
                onClick={() => onEdit(claim)}
                className="p-1.5 text-zinc-500 hover:text-accent rounded-lg hover:bg-surface-2 transition-colors"
                title="Edit claim"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(claim)}
                className="p-1.5 text-zinc-500 hover:text-refuted rounded-lg hover:bg-surface-2 transition-colors"
                title="Delete claim"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Claim Text - editorial pull-quote */}
        <blockquote className="font-display text-lg text-zinc-200 mb-4 leading-relaxed border-l-2 border-accent/40 pl-4">
          {claim.claim_text}
        </blockquote>

        {/* Transfer Details */}
        {(claim.player_name || claim.to_club || claim.from_club) && (
          <div className="bg-surface-2/50 rounded-lg p-4 mb-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              {claim.player_name && (
                <div>
                  <div className="text-zinc-500 text-xs font-sans uppercase tracking-wide mb-0.5">Player</div>
                  <div className="text-zinc-100 font-sans font-semibold">{claim.player_name}</div>
                </div>
              )}
              {claim.from_club && (
                <div>
                  <div className="text-zinc-500 text-xs font-sans uppercase tracking-wide mb-0.5">From</div>
                  <div className="text-zinc-100 font-sans font-semibold">{claim.from_club}</div>
                </div>
              )}
              {claim.to_club && (
                <div>
                  <div className="text-zinc-500 text-xs font-sans uppercase tracking-wide mb-0.5">To</div>
                  <div className="text-zinc-100 font-sans font-semibold">{claim.to_club}</div>
                </div>
              )}
              {claim.transfer_fee && (
                <div>
                  <div className="text-zinc-500 text-xs font-sans uppercase tracking-wide mb-0.5">Fee</div>
                  <div className="text-verified font-sans font-semibold">{claim.transfer_fee}</div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer: Metadata */}
        <div className="flex justify-between items-center pt-4 border-t border-edge">
          <div className="flex items-center space-x-3 text-xs">
            {claim.certainty_level_display && (
              <span className="px-2 py-1 bg-surface-2 text-zinc-400 border border-edge rounded font-sans uppercase tracking-wide">
                {claim.certainty_level_display}
              </span>
            )}
            {claim.source_type_display === 'Citing Another Source' && (
              <span className="px-2 py-1 bg-surface-2 text-zinc-500 border border-edge rounded font-sans uppercase tracking-wide">
                Citing
              </span>
            )}
          </div>
          <a
            href={claim.article_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 text-sm text-accent hover:text-accent-hover font-sans transition-colors group"
          >
            <span>Read Source</span>
            <svg className="w-4 h-4 transform transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        {/* Validation Info (if validated) */}
        {claim.validation_status !== 'pending' && claim.validation_date && (
          <div className="mt-4 pt-4 border-t border-edge">
            <div className="flex items-start space-x-2 text-sm">
              <svg
                className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                  claim.validation_status === 'confirmed_true'
                    ? 'text-verified'
                    : 'text-refuted'
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={claim.validation_status === 'confirmed_true'
                    ? "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    : "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"}
                />
              </svg>
              <div className="flex-grow">
                <div className="text-zinc-300 font-sans font-medium">
                  Validated {formatTimeAgo(claim.validation_date)}
                </div>
                {claim.validation_notes && (
                  <p className="mt-1 text-zinc-500 text-sm font-sans">
                    {claim.validation_notes}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ClaimCard
