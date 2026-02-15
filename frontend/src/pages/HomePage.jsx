import { useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useClaims, useClaimsStats, useFilterOptions, useDeleteClaim } from '../hooks/useClaims'
import ClaimFeed from '../components/claims/ClaimFeed'
import ClaimForm from '../components/claims/ClaimForm'
import StatsCard from '../components/common/StatsCard'
import Loading from '../components/common/Loading'

const FilterSelect = ({ label, value, onChange, options, placeholder = 'All' }) => (
  <div className="flex flex-col gap-1.5">
    <label className="text-xs font-sans font-medium text-zinc-500 uppercase tracking-wider">
      {label}
    </label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-surface-2 border border-edge rounded-lg px-3 py-2 text-sm font-sans text-zinc-200 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-colors appearance-none cursor-pointer"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2371717a' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 10px center',
        paddingRight: '32px',
      }}
    >
      <option value="">{placeholder}</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  </div>
)

const HomePage = () => {
  const [page, setPage] = useState(1)
  const [formOpen, setFormOpen] = useState(false)
  const [editingClaim, setEditingClaim] = useState(null)
  const deleteMutation = useDeleteClaim()

  const handleEdit = useCallback((claim) => {
    setEditingClaim(claim)
    setFormOpen(true)
  }, [])

  const handleDelete = useCallback((claim) => {
    if (window.confirm('Delete this claim?')) {
      deleteMutation.mutate(claim.id)
    }
  }, [deleteMutation])

  const handleFormClose = useCallback(() => {
    setFormOpen(false)
    setEditingClaim(null)
  }, [])

  const handleAdd = useCallback(() => {
    setEditingClaim(null)
    setFormOpen(true)
  }, [])

  const [filters, setFilters] = useState({
    club: '',
    publication: '',
    certainty_level: '',
    validation_status: '',
  })

  const { data: filterOptions } = useFilterOptions()

  // Build query params from filters
  const queryParams = { page }
  if (filters.club) queryParams.club = filters.club
  if (filters.publication) queryParams.publication = filters.publication
  if (filters.certainty_level) queryParams.certainty_level = filters.certainty_level
  if (filters.validation_status) queryParams.validation_status = filters.validation_status

  const { data: claimsData, isLoading: claimsLoading, error: claimsError } = useClaims(queryParams)
  const { data: stats, isLoading: statsLoading } = useClaimsStats()

  const updateFilter = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1) // Reset to first page when filter changes
  }, [])

  const activeFilterCount = Object.values(filters).filter(Boolean).length

  const clearFilters = useCallback(() => {
    setFilters({ club: '', publication: '', certainty_level: '', validation_status: '' })
    setPage(1)
  }, [])

  return (
    <div className="space-y-12 animate-fade-in">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-accent/5 to-transparent pointer-events-none"></div>

        <div className="relative text-center py-24 px-4">
          <div className="inline-block mb-6 px-4 py-2 bg-surface-1 border border-edge rounded-full">
            <span className="text-xs font-sans font-semibold text-zinc-400 uppercase tracking-wider">
              Truth in Transfer Reporting
            </span>
          </div>

          <h1 className="text-6xl md:text-7xl font-display text-zinc-100 mb-8 leading-tight">
            Veracity
          </h1>

          <p className="text-xl md:text-2xl text-zinc-400 max-w-3xl mx-auto mb-10 leading-relaxed font-sans">
            Data-driven journalism accountability. Track which football reporters
            get it right, and which ones are just jumping on the bandwagon.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/leaderboard" className="btn-primary group">
              View Leaderboard
              <svg className="inline-block w-4 h-4 ml-2 transform transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            <Link to="/about" className="btn-secondary">
              How It Works
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Dashboard */}
      {statsLoading ? (
        <div className="flex justify-center py-12">
          <Loading size="sm" text="" />
        </div>
      ) : stats ? (
        <div className="animate-slide-up">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-display text-zinc-100">
              Platform Overview
            </h2>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-verified rounded-full animate-pulse"></div>
              <span className="text-sm text-zinc-500 font-sans uppercase tracking-wider">Live</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard
              title="Total Claims"
              value={stats.total_claims}
              subtitle="Tracked rumours"
              color="accent"
            />
            <StatsCard
              title="Active Journalists"
              value={stats.total_journalists}
              subtitle="Being monitored"
              color="accent"
            />
            <StatsCard
              title="Verified True"
              value={stats.true_claims}
              subtitle={`${stats.accuracy_rate?.toFixed(1)}% accuracy rate`}
              color="verified"
            />
            <StatsCard
              title="Under Review"
              value={stats.pending_claims}
              subtitle="Awaiting validation"
              color="pending"
            />
          </div>
        </div>
      ) : null}

      {/* Accuracy Breakdown */}
      {stats && stats.validated_claims > 0 && (
        <div className="bg-surface-1 border border-edge rounded-xl p-8 shadow-elevation-1 animate-slide-up">
          <h3 className="text-xl font-display text-zinc-100 mb-6">
            Validation Breakdown
          </h3>
          <div className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-sans font-medium text-zinc-400">Confirmed True</span>
                <span className="text-lg font-mono font-bold text-verified tabular-nums">{stats.true_claims}</span>
              </div>
              <div className="h-2 bg-surface-3 rounded-full overflow-hidden">
                <div
                  className="h-full bg-verified rounded-full transition-all duration-1000"
                  style={{ width: `${(stats.true_claims / stats.validated_claims) * 100}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-sans font-medium text-zinc-400">Proven False</span>
                <span className="text-lg font-mono font-bold text-refuted tabular-nums">{stats.false_claims}</span>
              </div>
              <div className="h-2 bg-surface-3 rounded-full overflow-hidden">
                <div
                  className="h-full bg-refuted rounded-full transition-all duration-1000"
                  style={{ width: `${(stats.false_claims / stats.validated_claims) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Latest Claims Section */}
      <div className="animate-slide-up">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-display text-zinc-100 mb-2">
              Latest Transfer Rumours
            </h2>
            <p className="text-zinc-500 font-sans text-sm">
              Real-time tracking of journalist claims
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleAdd}
              className="btn-primary flex items-center gap-2 text-sm"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Rumour
            </button>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-verified rounded-full animate-pulse"></div>
              <span className="text-sm text-zinc-500 font-sans uppercase tracking-wider">Live</span>
            </div>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="bg-surface-1 border border-edge rounded-xl p-4 mb-6">
          <div className="flex items-end gap-4 flex-wrap">
            <FilterSelect
              label="Club"
              value={filters.club}
              onChange={(v) => updateFilter('club', v)}
              options={(filterOptions?.clubs || []).map(c => ({ value: c, label: c }))}
              placeholder="All clubs"
            />
            <FilterSelect
              label="Publication"
              value={filters.publication}
              onChange={(v) => updateFilter('publication', v)}
              options={(filterOptions?.publications || []).map(p => ({ value: p, label: p }))}
              placeholder="All publications"
            />
            <FilterSelect
              label="Confidence"
              value={filters.certainty_level}
              onChange={(v) => updateFilter('certainty_level', v)}
              options={filterOptions?.certainty_levels || []}
              placeholder="All levels"
            />
            <FilterSelect
              label="Status"
              value={filters.validation_status}
              onChange={(v) => updateFilter('validation_status', v)}
              options={filterOptions?.validation_statuses || []}
              placeholder="All statuses"
            />
            {activeFilterCount > 0 && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1.5 px-3 py-2 text-xs font-sans font-medium text-zinc-400 hover:text-zinc-100 bg-surface-2 border border-edge rounded-lg hover:border-zinc-600 transition-colors mb-px"
              >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Clear {activeFilterCount} {activeFilterCount === 1 ? 'filter' : 'filters'}
              </button>
            )}
          </div>
        </div>

        <ClaimFeed
          claims={claimsData?.results}
          isLoading={claimsLoading}
          error={claimsError}
          title=""
          page={page}
          totalCount={claimsData?.count}
          hasNext={!!claimsData?.next}
          hasPrevious={!!claimsData?.previous}
          onPageChange={setPage}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </div>

      <ClaimForm
        claim={editingClaim}
        isOpen={formOpen}
        onClose={handleFormClose}
      />
    </div>
  )
}

export default HomePage
