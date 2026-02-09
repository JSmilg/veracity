const TransferHero = ({ transfer }) => {
  return (
    <div className="bg-surface-0 border-b border-edge">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-5xl md:text-6xl font-display text-zinc-100 mb-4 tracking-tight">
          {transfer.player_name}
        </h1>

        <div className="flex items-center gap-3 text-xl font-sans text-zinc-400 mb-6">
          <span>{transfer.from_club}</span>
          <svg className="w-6 h-6 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
          <span>{transfer.to_club}</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {transfer.transfer_window && (
            <span className="inline-flex items-center px-3 py-1.5 bg-surface-1 text-zinc-400 text-sm font-sans font-medium rounded-md border border-edge">
              {transfer.transfer_window}
            </span>
          )}
          {transfer.completed ? (
            <span className="inline-flex items-center px-3 py-1.5 bg-verified/10 text-verified text-sm font-sans font-medium rounded-md border border-verified/25">
              Completed
            </span>
          ) : (
            <span className="inline-flex items-center px-3 py-1.5 bg-pending/10 text-pending text-sm font-sans font-medium rounded-md border border-pending/25">
              In Progress
            </span>
          )}
          {transfer.actual_fee && (
            <span className="inline-flex items-center px-3 py-1.5 bg-surface-1 text-zinc-400 text-sm font-sans font-medium rounded-md border border-edge">
              {transfer.actual_fee}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

export default TransferHero
