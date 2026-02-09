import { useParams } from 'react-router-dom'
import { useJournalist, useJournalistClaims } from '../hooks/useJournalists'
import ScoreDisplay from '../components/journalists/ScoreDisplay'
import StatsCard from '../components/common/StatsCard'
import ClaimFeed from '../components/claims/ClaimFeed'
import Loading from '../components/common/Loading'
import ErrorMessage from '../components/common/ErrorMessage'
import { getScoreBarColor } from '../utils/formatters'

const JournalistDetailPage = () => {
  const { slug } = useParams()
  const { data: journalist, isLoading, error } = useJournalist(slug)
  const { data: claimsData, isLoading: claimsLoading, error: claimsError } = useJournalistClaims(slug)

  if (isLoading) {
    return <Loading text="Loading journalist profile..." />
  }

  if (error) {
    return <ErrorMessage message="Failed to load journalist profile. Please try again." />
  }

  if (!journalist) {
    return <ErrorMessage message="Journalist not found." />
  }

  const claims = claimsData?.results || claimsData || []
  const truthColor = getScoreBarColor(journalist.truthfulness_score)
  const speedColor = getScoreBarColor(journalist.speed_score)

  return (
    <div className="space-y-0 animate-fade-in">
      {/* Clean Hero Header */}
      <div className="bg-surface-0 border-b border-edge">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row items-start gap-8">
            {/* Avatar */}
            <div className="flex-shrink-0">
              <div className="w-24 h-24 bg-accent-muted rounded-full flex items-center justify-center">
                <span className="text-accent font-sans font-bold text-2xl">
                  {journalist.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                </span>
              </div>
            </div>

            {/* Info */}
            <div className="flex-grow">
              <h1 className="text-5xl md:text-6xl font-display text-zinc-100 mb-4 tracking-tight">
                {journalist.name}
              </h1>

              {journalist.publications && journalist.publications.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {journalist.publications.map((pub, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1.5 bg-surface-1 text-zinc-400 text-sm font-sans font-medium rounded-md border border-edge"
                    >
                      {pub}
                    </span>
                  ))}
                </div>
              )}

              {journalist.twitter_handle && (
                <a
                  href={`https://twitter.com/${journalist.twitter_handle.replace('@', '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 text-accent hover:text-accent-hover font-sans transition-colors mb-4"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                  </svg>
                  <span className="text-sm">{journalist.twitter_handle}</span>
                </a>
              )}

              {journalist.bio && (
                <p className="text-zinc-500 font-sans leading-relaxed max-w-3xl text-sm">
                  {journalist.bio}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Split-Screen Score Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-0 min-h-[600px] border-b border-edge">
        {/* Truthfulness Side */}
        <div
          className="relative bg-surface-0 border-r border-edge flex flex-col items-center justify-center py-16"
          style={{ background: `linear-gradient(135deg, ${truthColor}08 0%, transparent 60%)` }}
        >
          <ScoreDisplay
            score={journalist.truthfulness_score}
            size="massive"
            label="Truthfulness"
            showProgressRing={true}
          />

          <div className="mt-8 space-y-3 px-8 w-full max-w-xs">
            <div className="flex items-center justify-between text-sm font-sans">
              <span className="text-zinc-500">Validated</span>
              <span className="text-zinc-100 font-mono font-bold tabular-nums">{journalist.validated_claims}</span>
            </div>
            <div className="flex items-center justify-between text-sm font-sans">
              <span className="text-zinc-500">True</span>
              <span className="text-verified font-mono font-bold tabular-nums">{journalist.true_claims}</span>
            </div>
            <div className="flex items-center justify-between text-sm font-sans">
              <span className="text-zinc-500">False</span>
              <span className="text-refuted font-mono font-bold tabular-nums">{journalist.false_claims}</span>
            </div>
          </div>
        </div>

        {/* Speed Side */}
        <div
          className="relative bg-surface-0 flex flex-col items-center justify-center py-16"
          style={{ background: `linear-gradient(225deg, ${speedColor}08 0%, transparent 60%)` }}
        >
          <ScoreDisplay
            score={journalist.speed_score}
            size="massive"
            label="Speed"
            showProgressRing={true}
          />

          <div className="mt-8 space-y-3 px-8 w-full max-w-xs">
            <div className="flex items-center justify-between text-sm font-sans">
              <span className="text-zinc-500">Original Scoops</span>
              <span className="text-zinc-100 font-mono font-bold tabular-nums">{journalist.original_scoops || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm font-sans">
              <span className="text-zinc-500">First to Report</span>
              <span className="text-accent font-mono font-bold tabular-nums">{journalist.first_to_report_count || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 animate-slide-up">
          <StatsCard
            title="Total Claims"
            value={journalist.total_claims}
            color="accent"
          />
          <StatsCard
            title="Validated"
            value={journalist.validated_claims}
            color="accent"
          />
          <StatsCard
            title="Correct"
            value={journalist.true_claims}
            color="verified"
          />
          <StatsCard
            title="Incorrect"
            value={journalist.false_claims}
            color="refuted"
          />
        </div>
      </div>

      {/* Claims Section */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-slide-up">
        <div className="mb-8">
          <h2 className="text-3xl font-display text-zinc-100 mb-2">
            Claim History
          </h2>
          <p className="text-zinc-500 font-sans text-sm">
            All claims made by {journalist.name}
          </p>
        </div>

        <ClaimFeed
          claims={claims}
          isLoading={claimsLoading}
          error={claimsError}
          title=""
        />
      </div>
    </div>
  )
}

export default JournalistDetailPage
