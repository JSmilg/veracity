import { Link } from 'react-router-dom'
import { formatScore, getScoreColor, getScoreBarColor } from '../../utils/formatters'
import Loading from '../common/Loading'
import ErrorMessage from '../common/ErrorMessage'

const LeaderboardTable = ({ journalists, scoreType = 'truthfulness', isLoading, error }) => {
  if (isLoading) {
    return <Loading text="Loading leaderboard..." />
  }

  if (error) {
    return <ErrorMessage message="Failed to load leaderboard. Please try again." />
  }

  if (!journalists || journalists.length === 0) {
    return (
      <div className="bg-surface-1 border border-edge rounded-xl text-center py-16">
        <svg className="w-16 h-16 text-zinc-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <p className="text-zinc-300 font-sans font-medium">No journalists found</p>
        <p className="text-sm text-zinc-500 font-sans mt-1">Check back later for updated rankings</p>
      </div>
    )
  }

  const scoreField = scoreType === 'speed' ? 'speed_score' : 'truthfulness_score'

  const getRankBadge = (rank) => {
    if (rank === 1) {
      return (
        <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
          <span className="text-base font-mono font-bold text-amber-400">{rank}</span>
        </div>
      )
    }
    if (rank === 2) {
      return (
        <div className="w-10 h-10 rounded-xl bg-zinc-500/20 border border-zinc-500/30 flex items-center justify-center">
          <span className="text-base font-mono font-bold text-zinc-300">{rank}</span>
        </div>
      )
    }
    if (rank === 3) {
      return (
        <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-500/30 flex items-center justify-center">
          <span className="text-base font-mono font-bold text-orange-400">{rank}</span>
        </div>
      )
    }
    return (
      <div className="w-10 h-10 rounded-xl bg-surface-2 border border-edge flex items-center justify-center">
        <span className="text-base font-mono font-semibold text-zinc-500">{rank}</span>
      </div>
    )
  }

  return (
    <div className="bg-surface-1 border border-edge rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-edge">
          <thead>
            <tr className="bg-surface-2">
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                Journalist
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                Publication
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                Claims
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                {scoreType === 'speed' ? 'Avg Position' : 'True'}
              </th>
              <th className="px-6 py-4 text-left text-xs font-sans font-semibold text-zinc-500 uppercase tracking-wider">
                {scoreType === 'speed' ? 'Stories' : 'False'}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-edge">
            {journalists.map((entry, index) => {
              const journalist = entry.journalist || entry
              const rank = entry.rank || index + 1
              const score = entry.score !== undefined ? entry.score : journalist[scoreField]
              const trueClaims = journalist.true_claims || 0
              const falseClaims = journalist.false_claims || 0
              const totalClaims = journalist.total_claims || 0
              const avgPosition = entry.avg_position
              const storyCount = entry.story_count || 0

              return (
                <tr
                  key={journalist.id}
                  className="hover:bg-surface-2 transition-colors duration-200 animate-slide-up"
                  style={{ animationDelay: `${index * 60}ms` }}
                >
                  <td className="px-6 py-5 whitespace-nowrap">
                    {getRankBadge(rank)}
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-accent-muted rounded-lg flex items-center justify-center">
                        <span className="text-accent font-sans font-bold text-sm">
                          {journalist.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                        </span>
                      </div>
                      <div>
                        <Link
                          to={`/journalist/${journalist.slug}`}
                          className="text-base font-semibold text-zinc-100 hover:text-accent transition-colors font-sans"
                        >
                          {journalist.name}
                        </Link>
                        {journalist.twitter_handle && (
                          <div className="flex items-center space-x-1 text-xs text-zinc-500 font-mono mt-0.5">
                            <span>{journalist.twitter_handle}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className="inline-flex items-center px-3 py-1 bg-surface-2 text-zinc-400 text-sm font-sans font-medium rounded-md border border-edge">
                      {journalist.publications?.[0] || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-5">
                    <div>
                      {scoreType === 'speed' ? (
                        <>
                          <div className={`text-2xl font-mono font-bold tabular-nums ${getScoreColor(score)}`}>
                            {formatScore(score, 1)}
                          </div>
                          <div className="h-1 bg-surface-3 rounded-full mt-1.5 w-20 overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{ width: `${score}%`, backgroundColor: getScoreBarColor(score) }}
                            ></div>
                          </div>
                        </>
                      ) : (
                        <div className="text-2xl font-mono font-bold tabular-nums text-verified">
                          {Math.round(parseFloat(score) || 0)}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="text-base font-semibold text-zinc-100 tabular-nums font-mono">
                      {totalClaims}
                    </div>
                    <div className="text-xs text-zinc-500 font-sans">
                      total
                    </div>
                  </td>
                  {scoreType === 'speed' ? (
                    <>
                      <td className="px-6 py-5">
                        <div className="text-base font-semibold text-zinc-100 tabular-nums font-mono">
                          {avgPosition != null ? `${avgPosition}` : '—'}
                        </div>
                        <div className="text-xs text-zinc-500 font-sans">avg rank</div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="text-base font-semibold text-zinc-300 tabular-nums font-mono">
                          {storyCount}
                        </div>
                        <div className="text-xs text-zinc-500 font-sans">stories</div>
                      </td>
                    </>
                  ) : (
                    <>
                      <td className="px-6 py-5">
                        <div className="text-base font-semibold text-verified tabular-nums font-mono">
                          {trueClaims}
                        </div>
                        <div className="text-xs text-zinc-500 font-sans">confirmed</div>
                      </td>
                      <td className="px-6 py-5">
                        <div className="text-base font-semibold text-refuted tabular-nums font-mono">
                          {falseClaims}
                        </div>
                        <div className="text-xs text-zinc-500 font-sans">false</div>
                      </td>
                    </>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default LeaderboardTable
