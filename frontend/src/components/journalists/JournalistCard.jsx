import { Link } from 'react-router-dom'
import { formatScore, getScoreColor, getScoreBarColor } from '../../utils/formatters'

const JournalistCard = ({ journalist, rank, scoreType = 'truthfulness' }) => {
  const score = scoreType === 'speed' ? journalist.speed_score : journalist.truthfulness_score
  const scoreLabel = scoreType === 'speed' ? 'Speed Score' : 'Truthfulness Score'
  const tierColor = getScoreBarColor(score)

  return (
    <div className="bg-surface-1 border border-edge rounded-xl p-6 hover:shadow-elevation-2 transition-all duration-300">
      <div className="flex items-start justify-between">
        {/* Rank Badge */}
        <div className="flex-shrink-0 mr-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-mono font-bold text-lg ${
            rank === 1 ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
            rank === 2 ? 'bg-zinc-500/20 text-zinc-300 border border-zinc-500/30' :
            rank === 3 ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
            'bg-surface-2 text-zinc-500 border border-edge'
          }`}>
            {rank}
          </div>
        </div>

        {/* Journalist Info */}
        <div className="flex-grow">
          <Link
            to={`/journalist/${journalist.slug}`}
            className="text-xl font-display text-zinc-100 hover:text-accent transition-colors"
          >
            {journalist.name}
          </Link>

          {journalist.publications && journalist.publications.length > 0 && (
            <p className="text-sm text-zinc-500 font-sans mt-1">
              {journalist.publications.join(', ')}
            </p>
          )}

          {journalist.twitter_handle && (
            <a
              href={`https://twitter.com/${journalist.twitter_handle.replace('@', '')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-accent hover:text-accent-hover font-sans mt-1 inline-block transition-colors"
            >
              {journalist.twitter_handle}
            </a>
          )}

          <div className="flex items-center space-x-4 mt-3 text-sm text-zinc-500 font-sans">
            <span>{journalist.total_claims || 0} claims</span>
          </div>
        </div>

        {/* Score Display */}
        <div className="flex-shrink-0 ml-4 text-right">
          <div
            className="inline-flex items-center justify-center w-20 h-20 rounded-full border-2"
            style={{ borderColor: tierColor }}
          >
            <span className={`text-2xl font-mono font-bold ${getScoreColor(score)}`}>
              {formatScore(score, 0)}
            </span>
          </div>
          <p className="text-xs text-zinc-500 font-sans mt-2">{scoreLabel}</p>
        </div>
      </div>
    </div>
  )
}

export default JournalistCard
