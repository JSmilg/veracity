const ErrorMessage = ({ message = 'Something went wrong', retry }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="bg-refuted/10 border border-refuted/30 rounded-lg p-6 max-w-md">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-6 w-6 text-refuted"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-semibold text-refuted font-sans">Error</h3>
            <div className="mt-2 text-sm text-zinc-400 font-sans">
              <p>{message}</p>
            </div>
            {retry && (
              <div className="mt-4">
                <button
                  onClick={retry}
                  className="text-sm font-medium text-accent hover:text-accent-hover transition-colors"
                >
                  Try again
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ErrorMessage
