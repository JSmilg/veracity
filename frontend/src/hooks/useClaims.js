import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getClaims,
  getClaimById,
  getLatestClaims,
  getPendingClaims,
  getValidatedClaims,
  getClaimsStats,
  getFilterOptions,
  getPublicationLeaderboard,
  createClaim,
  updateClaim,
  deleteClaim,
} from '../api/claims'

/**
 * Hook to fetch list of claims
 * @param {Object} params - Query parameters
 * @returns {Object} React Query result
 */
export const useClaims = (params = {}) => {
  return useQuery({
    queryKey: ['claims', params],
    queryFn: () => getClaims(params),
    placeholderData: (prev) => prev,
    staleTime: 1000 * 60 * 2, // 2 minutes
  })
}

/**
 * Hook to fetch claim by ID
 * @param {number} id - Claim ID
 * @returns {Object} React Query result
 */
export const useClaim = (id) => {
  return useQuery({
    queryKey: ['claim', id],
    queryFn: () => getClaimById(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook to fetch latest claims
 * @returns {Object} React Query result
 */
export const useLatestClaims = () => {
  return useQuery({
    queryKey: ['claims', 'latest'],
    queryFn: getLatestClaims,
    staleTime: 1000 * 60, // 1 minute
  })
}

/**
 * Hook to fetch pending claims
 * @param {Object} params - Query parameters
 * @returns {Object} React Query result
 */
export const usePendingClaims = (params = {}) => {
  return useQuery({
    queryKey: ['claims', 'pending', params],
    queryFn: () => getPendingClaims(params),
    staleTime: 1000 * 60, // 1 minute
  })
}

/**
 * Hook to fetch validated claims
 * @param {Object} params - Query parameters
 * @returns {Object} React Query result
 */
export const useValidatedClaims = (params = {}) => {
  return useQuery({
    queryKey: ['claims', 'validated', params],
    queryFn: () => getValidatedClaims(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook to fetch claims statistics
 * @returns {Object} React Query result
 */
export const useClaimsStats = () => {
  return useQuery({
    queryKey: ['claims', 'stats'],
    queryFn: getClaimsStats,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook to fetch filter options for dropdowns
 * @returns {Object} React Query result
 */
export const useFilterOptions = () => {
  return useQuery({
    queryKey: ['claims', 'filter-options'],
    queryFn: getFilterOptions,
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

export const usePublicationLeaderboard = (params = {}) => {
  return useQuery({
    queryKey: ['claims', 'publication-leaderboard', params],
    queryFn: () => getPublicationLeaderboard(params),
    staleTime: 1000 * 60 * 5,
  })
}

export const useCreateClaim = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createClaim,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['claims'] }),
  })
}

export const useUpdateClaim = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }) => updateClaim(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['claims'] }),
  })
}

export const useDeleteClaim = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteClaim,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['claims'] }),
  })
}
