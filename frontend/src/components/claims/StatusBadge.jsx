import { STATUS_LABELS, VALIDATION_STATUS } from '../../utils/constants'

const StatusBadge = ({ status, size = 'md' }) => {
  const label = STATUS_LABELS[status] || 'Unknown'

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-xs',
    lg: 'px-4 py-2 text-sm',
  }

  const getStatusStyle = () => {
    switch (status) {
      case VALIDATION_STATUS.CONFIRMED_TRUE:
        return {
          classes: 'bg-verified/15 text-verified border-verified/25',
          icon: (
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          )
        }
      case VALIDATION_STATUS.PROVEN_FALSE:
        return {
          classes: 'bg-refuted/15 text-refuted border-refuted/25',
          icon: (
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          )
        }
      case VALIDATION_STATUS.PARTIALLY_TRUE:
        return {
          classes: 'bg-partial/15 text-partial border-partial/25',
          icon: (
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          )
        }
      default:
        return {
          classes: 'bg-pending/15 text-pending border-pending/25',
          icon: (
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
          )
        }
    }
  }

  const style = getStatusStyle()

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${sizeClasses[size]} ${style.classes} border rounded-md font-sans font-semibold uppercase tracking-wide transition-colors`}
    >
      {style.icon}
      {label}
    </span>
  )
}

export default StatusBadge
