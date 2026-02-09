import { useState } from 'react'
import { useClaimsStats } from '../hooks/useClaims'
import { Link } from 'react-router-dom'

const AnimatedNumber = ({ value, suffix = '' }) => {
  return (
    <span className="tabular-nums">{value?.toLocaleString() ?? '—'}{suffix}</span>
  )
}

const AboutPage = () => {
  const { data: stats } = useClaimsStats()
  const [hoveredStep, setHoveredStep] = useState(null)

  return (
    <div className="space-y-16 animate-fade-in">
      {/* Hero */}
      <div className="relative text-center py-16">
        <h1 className="text-5xl md:text-6xl font-display text-zinc-100 mb-4">
          Who can you <span className="text-accent">actually</span> trust?
        </h1>
        <p className="text-xl text-zinc-500 font-sans max-w-2xl mx-auto leading-relaxed">
          Veracity tracks what football journalists claim, then checks if they were right.
        </p>
      </div>

      {/* The Problem — visual, not wordy */}
      <div className="animate-slide-up">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              ),
              color: '#ef4444',
              bgColor: 'bg-refuted/15',
              textColor: 'text-refuted',
              title: 'No accountability',
              desc: 'A journalist can link your club to 50 players, get 48 wrong, and face zero consequences.',
            },
            {
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              ),
              color: '#f59e0b',
              bgColor: 'bg-amber-500/15',
              textColor: 'text-amber-400',
              title: 'Copycats rewarded',
              desc: 'Aggregators repackage others\' scoops as their own. Original reporting gets diluted.',
            },
            {
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              ),
              color: '#6366f1',
              bgColor: 'bg-accent/15',
              textColor: 'text-accent',
              title: 'Fans left guessing',
              desc: 'When a rumour drops, there\'s no way to know if the source is reliable or just clickbait.',
            },
          ].map((item, i) => (
            <div
              key={i}
              className="bg-surface-1 border border-edge rounded-xl p-6 hover:border-zinc-600 transition-all duration-300 animate-slide-up"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className={`w-12 h-12 ${item.bgColor} rounded-xl flex items-center justify-center mb-4`}>
                <svg className={`w-6 h-6 ${item.textColor}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {item.icon}
                </svg>
              </div>
              <h3 className="text-lg font-display text-zinc-100 mb-2">{item.title}</h3>
              <p className="text-sm text-zinc-500 font-sans leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Live Stats Bar */}
      {stats && (
        <div className="animate-slide-up">
          <div className="bg-surface-1 border border-edge rounded-xl p-1">
            <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-edge">
              {[
                { label: 'Claims Tracked', value: stats.total_claims, color: 'text-zinc-100' },
                { label: 'Journalists', value: stats.total_journalists, color: 'text-accent' },
                { label: 'Confirmed True', value: stats.true_claims, color: 'text-verified' },
                { label: 'Proven False', value: stats.false_claims, color: 'text-refuted' },
              ].map((stat, i) => (
                <div key={i} className="text-center py-6 px-4">
                  <div className={`text-3xl md:text-4xl font-mono font-bold ${stat.color} tabular-nums mb-1`}>
                    <AnimatedNumber value={stat.value} />
                  </div>
                  <div className="text-xs text-zinc-500 font-sans font-semibold uppercase tracking-wider">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Two Scores — visual cards */}
      <div className="animate-slide-up">
        <h2 className="text-3xl font-display text-zinc-100 mb-6 text-center">
          Two scores. No hiding.
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          {/* Truthfulness */}
          <div className="bg-surface-1 border border-edge rounded-xl p-8 relative overflow-hidden group hover:border-verified/30 transition-all duration-300">
            <div className="absolute top-0 right-0 w-32 h-32 bg-verified/5 rounded-full -translate-y-12 translate-x-12 group-hover:scale-150 transition-transform duration-500" />
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-verified/15 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-verified" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-xl font-display text-zinc-100">Truthfulness</h3>
              </div>
              <p className="text-zinc-400 font-sans leading-relaxed mb-5">
                How many claims ended up being confirmed true. The numbers speak for themselves.
              </p>
              {/* Visual example */}
              <div className="bg-surface-2 rounded-lg p-4 border border-edge">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-zinc-500 font-sans font-semibold uppercase">Example</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-mono font-bold text-verified">13</span>
                  <span className="text-sm text-zinc-500 font-sans">confirmed true out of 82 claims</span>
                </div>
              </div>
            </div>
          </div>

          {/* Speed */}
          <div className="bg-surface-1 border border-edge rounded-xl p-8 relative overflow-hidden group hover:border-score-good/30 transition-all duration-300">
            <div className="absolute top-0 right-0 w-32 h-32 bg-score-good/5 rounded-full -translate-y-12 translate-x-12 group-hover:scale-150 transition-transform duration-500" />
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-score-good/15 rounded-lg flex items-center justify-center">
                  <svg className="w-5 h-5 text-score-good" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-xl font-display text-zinc-100">Speed</h3>
              </div>
              <p className="text-zinc-400 font-sans leading-relaxed mb-5">
                For confirmed stories, how early were they compared to everyone else? Rewards breaking news, not following it.
              </p>
              {/* Visual example */}
              <div className="bg-surface-2 rounded-lg p-4 border border-edge">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-zinc-500 font-sans font-semibold uppercase">Example</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-mono font-bold text-score-good">1.8</span>
                    <span className="text-sm text-zinc-500 font-sans">avg position</span>
                  </div>
                  <div className="text-xs text-zinc-600 font-sans">|</div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-lg font-mono font-semibold text-zinc-300">4</span>
                    <span className="text-sm text-zinc-500 font-sans">stories</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works — interactive steps */}
      <div className="animate-slide-up">
        <h2 className="text-3xl font-display text-zinc-100 mb-8 text-center">
          How it works
        </h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            {
              num: 1,
              title: 'Collect',
              desc: 'Claims gathered from journalists across the football media landscape',
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              ),
              color: '#6366f1',
            },
            {
              num: 2,
              title: 'Classify',
              desc: 'Player, clubs, and certainty level extracted and categorised automatically',
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              ),
              color: '#3b82f6',
            },
            {
              num: 3,
              title: 'Validate',
              desc: 'When transfers confirm or collapse, claims are checked against reality',
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              ),
              color: '#22c55e',
            },
            {
              num: 4,
              title: 'Score',
              desc: 'Truthfulness and speed update automatically into a permanent public record',
              icon: (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              ),
              color: '#f59e0b',
            },
          ].map((step, i) => (
            <div
              key={step.num}
              className={`bg-surface-1 border rounded-xl p-6 cursor-default transition-all duration-300 animate-slide-up ${
                hoveredStep === i ? 'border-zinc-500 scale-[1.02] shadow-lg shadow-black/20' : 'border-edge'
              }`}
              style={{ animationDelay: `${i * 80}ms` }}
              onMouseEnter={() => setHoveredStep(i)}
              onMouseLeave={() => setHoveredStep(null)}
            >
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center transition-colors duration-300"
                  style={{ backgroundColor: `${step.color}20` }}
                >
                  <svg
                    className="w-5 h-5 transition-colors duration-300"
                    style={{ color: step.color }}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    {step.icon}
                  </svg>
                </div>
                <span className="text-xs font-mono text-zinc-600 font-bold">0{step.num}</span>
              </div>
              <h3 className="font-display text-zinc-100 mb-1.5">{step.title}</h3>
              <p className="text-xs text-zinc-500 font-sans leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Why It Matters — compact impact cards */}
      <div className="animate-slide-up">
        <h2 className="text-3xl font-display text-zinc-100 mb-6 text-center">
          Why it matters
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-surface-1 border border-edge rounded-xl p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-amber-500/15 rounded-lg flex items-center justify-center mt-0.5">
                <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div>
                <h3 className="font-display text-zinc-100 mb-1">For fans</h3>
                <p className="text-sm text-zinc-500 font-sans leading-relaxed">
                  Check a source's track record before getting your hopes up. Filter signal from noise.
                </p>
              </div>
            </div>
          </div>
          <div className="bg-surface-1 border border-edge rounded-xl p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-verified/15 rounded-lg flex items-center justify-center mt-0.5">
                <svg className="w-5 h-5 text-verified" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <div>
                <h3 className="font-display text-zinc-100 mb-1">For good journalists</h3>
                <p className="text-sm text-zinc-500 font-sans leading-relaxed">
                  A public record of accuracy they can point to. Good work gets recognised.
                </p>
              </div>
            </div>
          </div>
          <div className="bg-surface-1 border border-edge rounded-xl p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-refuted/15 rounded-lg flex items-center justify-center mt-0.5">
                <svg className="w-5 h-5 text-refuted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <div>
                <h3 className="font-display text-zinc-100 mb-1">For the industry</h3>
                <p className="text-sm text-zinc-500 font-sans leading-relaxed">
                  When accuracy is measured publicly, the incentives change. There's a cost to fabrication.
                </p>
              </div>
            </div>
          </div>
          <div className="bg-surface-1 border border-edge rounded-xl p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-accent/15 rounded-lg flex items-center justify-center mt-0.5">
                <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                </svg>
              </div>
              <div>
                <h3 className="font-display text-zinc-100 mb-1">Transparent by default</h3>
                <p className="text-sm text-zinc-500 font-sans leading-relaxed">
                  Every claim, score, and validation is public. No opaque algorithms. Trace any result to source data.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Claim Your Profile — CTA card */}
      <div className="animate-slide-up">
        <div className="bg-gradient-to-br from-accent/10 via-surface-1 to-surface-1 border border-accent/20 rounded-xl p-8 md:p-10 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full -translate-y-32 translate-x-32" />
          <div className="relative flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="flex-shrink-0 w-16 h-16 bg-accent/20 border border-accent/30 rounded-2xl flex items-center justify-center">
              <svg className="w-8 h-8 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-display text-zinc-100">
                  Are you a journalist?
                </h2>
                <span className="px-2.5 py-0.5 bg-accent/15 border border-accent/30 rounded-full text-xs font-sans font-semibold text-accent uppercase tracking-wider">
                  Coming Soon
                </span>
              </div>
              <p className="text-zinc-400 font-sans leading-relaxed max-w-2xl">
                Soon you'll be able to claim your profile to flag misattributed claims and provide context on your reporting.
                Claimed profiles will be marked as verified. Our goal is accuracy, not gotchas.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="animate-slide-up text-center pb-8">
        <Link
          to="/leaderboard"
          className="inline-flex items-center gap-2 px-8 py-3.5 bg-accent hover:bg-accent/90 text-white font-sans font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-accent/20 hover:shadow-accent/30"
        >
          View the Rankings
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </div>
    </div>
  )
}

export default AboutPage
