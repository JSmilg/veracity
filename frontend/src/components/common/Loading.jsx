const Loading = ({ size = 'md', text = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'h-8 w-8 border-2',
    md: 'h-12 w-12 border-3',
    lg: 'h-16 w-16 border-4',
  }

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-accent border-t-transparent`}
      ></div>
      {text && (
        <p className="mt-4 text-zinc-500 font-sans text-sm">{text}</p>
      )}
    </div>
  )
}

export default Loading
