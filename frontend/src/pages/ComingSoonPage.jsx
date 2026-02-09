import { useParams, Link } from 'react-router-dom'

const domainData = {
  hollywood: {
    label: 'Hollywood',
    color: '#f59e0b',
    tagline: 'Tracking who really knows what\'s happening in entertainment.',
    tracks: [
      { title: 'Cast Announcements', desc: 'When insiders claim an actor is attached to a role, we track whether it pans out.' },
      { title: 'Relationship News', desc: 'Celebrity relationship scoops — who broke it first, and were they right?' },
      { title: 'Project Deals', desc: 'Studio acquisitions, greenlights, and production deals reported before confirmation.' },
      { title: 'Award Predictions', desc: 'Nomination leaks, campaign buzz, and winner predictions scored against results.' },
    ],
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
    ),
  },
  politics: {
    label: 'Politics',
    color: '#ef4444',
    tagline: 'Scoring political predictions against what actually happens.',
    tracks: [
      { title: 'Election Forecasts', desc: 'Pundit predictions about races, margins, and turnout — validated against results.' },
      { title: 'Policy Leaks', desc: 'Insider claims about upcoming legislation, executive orders, and regulatory moves.' },
      { title: 'Foreign Policy Moves', desc: 'Diplomatic scoops, treaty negotiations, and geopolitical predictions tracked to outcome.' },
      { title: 'Legislative Negotiations', desc: 'Claims about deal-making, vote counts, and bill prospects checked against reality.' },
    ],
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
    ),
  },
  tech: {
    label: 'Tech',
    color: '#06b6d4',
    tagline: 'Tech rumours are everywhere and often wrong. We\'ll keep score.',
    tracks: [
      { title: 'Product Launch Rumours', desc: 'Leaked specs, release dates, and feature lists — scored when the product ships.' },
      { title: 'Funding Rounds', desc: 'Reported valuations, lead investors, and round sizes checked against announcements.' },
      { title: 'Leadership Hires', desc: 'Executive moves and board appointments reported before the press release.' },
      { title: 'Acquisition Leaks', desc: 'M&A rumours tracked from first whisper to close — or collapse.' },
    ],
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    ),
  },
  'wall-st': {
    label: 'Wall St',
    color: '#22c55e',
    tagline: 'Analyst predictions scored against market reality.',
    tracks: [
      { title: 'Stock Forecasts', desc: 'Price targets and buy/sell calls from analysts, scored against actual performance.' },
      { title: 'Earnings Predictions', desc: 'Revenue and EPS estimates tracked against reported numbers each quarter.' },
      { title: 'Macro Calls', desc: 'Recession warnings, rate predictions, and inflation forecasts validated over time.' },
      { title: 'IPO & Deal Predictions', desc: 'Rumoured listings, valuations, and deal terms checked against outcomes.' },
    ],
    icon: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    ),
  },
}

const steps = [
  { num: 1, title: 'Collect', desc: 'Claims gathered from journalists, analysts, and insiders across the domain.' },
  { num: 2, title: 'Classify', desc: 'Subjects, entities, and certainty levels extracted and categorised automatically.' },
  { num: 3, title: 'Validate', desc: 'When outcomes confirm or disprove claims, they\'re checked against reality.' },
  { num: 4, title: 'Score', desc: 'Accuracy and speed update automatically into a permanent public record.' },
]

const ComingSoonPage = () => {
  const { domain } = useParams()
  const data = domainData[domain]

  if (!data) {
    return (
      <div className="text-center py-32 animate-fade-in">
        <h1 className="text-4xl font-display text-zinc-100 mb-4">Domain not found</h1>
        <p className="text-zinc-500 font-sans mb-8">We don't have a page for that yet.</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 bg-accent hover:bg-accent/90 text-white font-sans font-semibold rounded-xl transition-all duration-200"
        >
          Back to Veracity
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-16 animate-fade-in">
      {/* Hero */}
      <div className="relative text-center py-16">
        <div className="flex justify-center mb-6">
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center"
            style={{ backgroundColor: `${data.color}20` }}
          >
            <svg
              className="w-8 h-8"
              style={{ color: data.color }}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {data.icon}
            </svg>
          </div>
        </div>
        <h1 className="text-5xl md:text-6xl font-display text-zinc-100 mb-4">
          Veracity{' '}
          <span style={{ color: data.color }}>{data.label}</span>
        </h1>
        <p className="text-xl text-zinc-500 font-sans max-w-2xl mx-auto leading-relaxed">
          {data.tagline}
        </p>
        <span
          className="inline-block mt-6 px-4 py-1.5 rounded-full text-sm font-sans font-semibold uppercase tracking-wider"
          style={{
            backgroundColor: `${data.color}15`,
            color: data.color,
          }}
        >
          Coming Soon
        </span>
      </div>

      {/* What we'll track */}
      <div className="animate-slide-up">
        <h2 className="text-3xl font-display text-zinc-100 mb-6 text-center">
          What we'll track
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          {data.tracks.map((item, i) => (
            <div
              key={i}
              className="bg-surface-1 border border-edge rounded-xl p-6 hover:border-zinc-600 transition-all duration-300 animate-slide-up"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div
                className="w-1 h-8 rounded-full mb-4"
                style={{ backgroundColor: data.color }}
              />
              <h3 className="text-lg font-display text-zinc-100 mb-2">{item.title}</h3>
              <p className="text-sm text-zinc-500 font-sans leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Same engine, new domain */}
      <div className="animate-slide-up">
        <h2 className="text-3xl font-display text-zinc-100 mb-6 text-center">
          Same engine, new domain
        </h2>
        <p className="text-zinc-400 font-sans text-center max-w-2xl mx-auto leading-relaxed mb-8">
          The Veracity model — Collect, Classify, Validate, Score — works wherever people make public predictions.
          We're bringing the same accountability engine to {data.label.toLowerCase()}.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {steps.map((step, i) => (
            <div
              key={step.num}
              className="bg-surface-1 border border-edge rounded-xl p-5 text-center animate-slide-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3"
                style={{ backgroundColor: `${data.color}15` }}
              >
                <span
                  className="text-sm font-mono font-bold"
                  style={{ color: data.color }}
                >
                  0{step.num}
                </span>
              </div>
              <h3 className="font-display text-zinc-100 mb-1">{step.title}</h3>
              <p className="text-xs text-zinc-500 font-sans leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="animate-slide-up text-center pb-8">
        <p className="text-zinc-500 font-sans mb-6">
          In the meantime, see how we're tracking football transfers.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-8 py-3.5 bg-accent hover:bg-accent/90 text-white font-sans font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-accent/20 hover:shadow-accent/30"
        >
          Explore Veracity Transfers
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </div>
    </div>
  )
}

export default ComingSoonPage
