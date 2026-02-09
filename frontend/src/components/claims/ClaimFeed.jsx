import ClaimCard from './ClaimCard'
import Loading from '../common/Loading'
import ErrorMessage from '../common/ErrorMessage'

const PAGE_SIZE = 20

const ClaimFeed = ({
  claims,
  isLoading,
  error,
  title = 'Claims',
  page,
  totalCount,
  hasNext,
  hasPrevious,
  onPageChange,
  onEdit,
  onDelete,
}) => {
  if (isLoading) {
    return <Loading text="Loading claims..." />
  }

  if (error) {
    return <ErrorMessage message="Failed to load claims. Please try again." />
  }

  if (!claims || claims.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="bg-surface-1 border border-edge rounded-xl p-8 inline-block">
          <svg
            className="w-16 h-16 mx-auto text-zinc-600 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <p className="text-zinc-300 font-sans font-medium">No claims found</p>
          <p className="text-zinc-500 text-sm font-sans mt-2">
            Check back later for more transfer rumours!
          </p>
        </div>
      </div>
    )
  }

  const totalPages = totalCount ? Math.ceil(totalCount / PAGE_SIZE) : 1
  const showPagination = onPageChange && totalCount > PAGE_SIZE

  const handlePageChange = (newPage) => {
    onPageChange(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div>
      {title && (
        <h2 className="text-2xl font-display font-bold mb-6 text-zinc-100">{title}</h2>
      )}
      <div className="space-y-4">
        {claims.map((claim) => (
          <ClaimCard key={claim.id} claim={claim} onEdit={onEdit} onDelete={onDelete} />
        ))}
      </div>

      {showPagination && (
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-edge">
          <p className="text-sm text-zinc-500 font-sans">
            Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, totalCount)} of {totalCount} claims
          </p>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={!hasPrevious}
              className="flex items-center gap-1 px-4 py-2 text-sm font-sans font-medium rounded-lg border border-edge bg-surface-1 text-zinc-300 hover:bg-surface-2 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>

            <span className="px-3 py-2 text-sm font-sans text-zinc-400">
              Page {page} of {totalPages}
            </span>

            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={!hasNext}
              className="flex items-center gap-1 px-4 py-2 text-sm font-sans font-medium rounded-lg border border-edge bg-surface-1 text-zinc-300 hover:bg-surface-2 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Next
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ClaimFeed
