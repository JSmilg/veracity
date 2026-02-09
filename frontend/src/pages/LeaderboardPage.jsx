import { useState } from 'react'
import { useLeaderboard } from '../hooks/useJournalists'
import { usePublicationLeaderboard } from '../hooks/useClaims'
import LeaderboardTable from '../components/journalists/LeaderboardTable'
import { SCORE_TYPE } from '../utils/constants'
import { formatScore, getScoreColor, getScoreBarColor } from '../utils/formatters'
import Loading from '../components/common/Loading'
import ErrorMessage from '../components/common/ErrorMessage'

const PublicationTable = ({ publications, scoreType, isLoading, error }) => {
  if (isLoading) return <Loading text="Loading leaderboard..." />
  if (error) return <ErrorMessage message="Failed to load publication leaderboard." />
  if (!publications || publications.length === 0) {
    return (
      <div className="bg-surface-1 border border-edge rounded-xl text-center py-16">
        <p className="text-zinc-300 font-sans font-medium">No publications found</p>
      </div>
    )
  }

  const isSpeed = scoreType === 'speed'

  const getRankBadge = (rank) => {
    const styles = {
      1: 'bg-amber-500/20 border-amber-500/30 text-amber-400',
      2: 'bg-zinc-500/20 border-zinc-500/30 text-zinc-300',
      3: 'bg-orange-500/20 border-orange-500/30 text-orange-400',
    }
    const cls = styles[rank] || 'bg-surface-2 border-edge text-zinc-500'
    return (
      <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${cls}`}>
        <span className="text-base font-mono font-bold">{rank}</span>
      </div>
    )
  }

  return (
    <div className="bg-surface-1 border border-edge rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-edge">
          <thead>
            <tr className="bg-surface-2">
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">Rank</th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">Publication</th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">Score</th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">Claims</th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                {isSpeed ? 'Avg Position' : 'True'}
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                {isSpeed ? 'Stories' : 'False'}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-edge">
            {publications.map((pub, index) => (
              <tr
                key={pub.publication}
                className="hover:bg-surface-2 transition-colors duration-200 animate-slide-up"
                style={{ animationDelay: `${index * 60}ms` }}
              >
                <td className="px-6 py-5 whitespace-nowrap">
                  {getRankBadge(pub.rank)}
                </td>
                <td className="px-6 py-5">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-10 h-10 bg-accent-muted rounded-lg flex items-center justify-center">
                      <span className="text-accent font-sans font-bold text-sm">
                        {pub.publication.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    <span className="text-base font-semibold text-zinc-100 font-sans">
                      {pub.publication}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div>
                    {isSpeed ? (
                      <>
                        <div className={`text-2xl font-mono font-bold tabular-nums ${getScoreColor(pub.score)}`}>
                          {formatScore(pub.score, 1)}
                        </div>
                        <div className="h-1 bg-surface-3 rounded-full mt-1.5 w-20 overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${pub.score}%`, backgroundColor: getScoreBarColor(pub.score) }}
                          />
                        </div>
                      </>
                    ) : (
                      <div className="text-2xl font-mono font-bold tabular-nums text-verified">
                        {Math.round(parseFloat(pub.score) || 0)}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-5">
                  <div className="text-base font-semibold text-zinc-100 tabular-nums font-mono">{pub.total_claims}</div>
                  <div className="text-xs text-zinc-500 font-sans">total</div>
                </td>
                {isSpeed ? (
                  <>
                    <td className="px-6 py-5">
                      <div className="text-base font-semibold text-zinc-100 tabular-nums font-mono">
                        {pub.avg_position != null ? pub.avg_position : '—'}
                      </div>
                      <div className="text-xs text-zinc-500 font-sans">avg rank</div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="text-base font-semibold text-zinc-300 tabular-nums font-mono">{pub.story_count || 0}</div>
                      <div className="text-xs text-zinc-500 font-sans">stories</div>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="px-6 py-5">
                      <div className="text-base font-semibold text-verified tabular-nums font-mono">{pub.true_claims}</div>
                      <div className="text-xs text-zinc-500 font-sans">confirmed</div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="text-base font-semibold text-refuted tabular-nums font-mono">{pub.false_claims}</div>
                      <div className="text-xs text-zinc-500 font-sans">false</div>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const LeaderboardPage = () => {
  const [view, setView] = useState('journalists') // 'journalists' | 'publications'
  const [scoreType, setScoreType] = useState(SCORE_TYPE.TRUTHFULNESS)

  const { data: leaderboard, isLoading, error } = useLeaderboard({
    score_type: scoreType,
    limit: 20,
  })

  const { data: pubLeaderboard, isLoading: pubLoading, error: pubError } = usePublicationLeaderboard({
    score_type: scoreType,
    limit: 20,
  })

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="relative">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <h1 className="text-4xl font-display text-zinc-100 mb-2">
              Rankings
            </h1>
            <p className="text-lg text-zinc-500 font-sans">
              {view === 'journalists'
                ? `Top-performing journalists ranked by ${scoreType === SCORE_TYPE.TRUTHFULNESS ? 'accuracy' : 'speed'}`
                : `Publications ranked by ${scoreType === SCORE_TYPE.TRUTHFULNESS ? 'accuracy' : 'speed'} of their transfer reporting`
              }
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* View Toggle: Journalists / Publications */}
            <div className="flex items-center gap-2 bg-surface-2 border border-edge rounded-xl p-1.5">
              <button
                onClick={() => setView('journalists')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-sans font-semibold transition-all ${
                  view === 'journalists'
                    ? 'bg-accent text-white shadow-elevation-1'
                    : 'text-zinc-400 hover:text-zinc-100'
                }`}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Journalists
              </button>
              <button
                onClick={() => setView('publications')}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-sans font-semibold transition-all ${
                  view === 'publications'
                    ? 'bg-accent text-white shadow-elevation-1'
                    : 'text-zinc-400 hover:text-zinc-100'
                }`}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
                Publications
              </button>
            </div>

            {/* Score Type Toggle */}
            <div className="flex items-center gap-2 bg-surface-2 border border-edge rounded-xl p-1.5">
              <button
                onClick={() => setScoreType(SCORE_TYPE.TRUTHFULNESS)}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-sans font-semibold transition-all ${
                  scoreType === SCORE_TYPE.TRUTHFULNESS
                    ? 'bg-accent text-white shadow-elevation-1'
                    : 'text-zinc-400 hover:text-zinc-100'
                }`}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Truthfulness
              </button>
              <button
                onClick={() => setScoreType(SCORE_TYPE.SPEED)}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-sans font-semibold transition-all ${
                  scoreType === SCORE_TYPE.SPEED
                    ? 'bg-accent text-white shadow-elevation-1'
                    : 'text-zinc-400 hover:text-zinc-100'
                }`}
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Speed
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Description Card */}
      <div
        className="bg-surface-1 border border-edge rounded-xl p-6"
        style={{ borderLeftWidth: '4px', borderLeftColor: '#6366f1' }}
      >
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 bg-accent rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="font-display text-zinc-100 mb-1">
              {scoreType === SCORE_TYPE.TRUTHFULNESS ? 'Truthfulness Score' : 'Speed Score'}
            </h3>
            <p className="text-zinc-400 font-sans leading-relaxed">
              {scoreType === SCORE_TYPE.TRUTHFULNESS ? (
                <>
                  Total number of claims that have been confirmed true.
                  {view === 'publications'
                    ? ' Counted across all claims attributed to each publication.'
                    : ' A higher count indicates more verified accurate reporting.'
                  }
                </>
              ) : (
                <>
                  Measures how often {view === 'publications' ? 'a publication' : 'a journalist'} was first to break a story among original scoops.
                  Rewards {view === 'publications' ? 'publications' : 'journalists'} who break news before others.
                </>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Leaderboard */}
      <div className="animate-slide-up">
        {view === 'journalists' ? (
          <LeaderboardTable
            journalists={leaderboard}
            scoreType={scoreType}
            isLoading={isLoading}
            error={error}
          />
        ) : (
          <PublicationTable
            publications={pubLeaderboard}
            scoreType={scoreType}
            isLoading={pubLoading}
            error={pubError}
          />
        )}
      </div>
    </div>
  )
}

export default LeaderboardPage
