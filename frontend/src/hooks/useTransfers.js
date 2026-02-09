import { useQuery } from '@tanstack/react-query'
import { getTransferTimeline } from '../api/transfers'

export const useTransferTimeline = (id) => {
  return useQuery({
    queryKey: ['transfer', id, 'timeline'],
    queryFn: () => getTransferTimeline(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
    placeholderData: (prev) => prev,
  })
}
