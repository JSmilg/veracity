import { useQuery } from '@tanstack/react-query'
import {
  getJournalists,
  getJournalistBySlug,
  getJournalistScoreHistory,
  getJournalistClaims,
  getLeaderboard,
} from '../api/journalists'

/**
 * Hook to fetch list of journalists
 * @param {Object} params - Query parameters
 * @returns {Object} React Query result
 */
export const useJournalists = (params = {}) => {
  return useQuery({
    queryKey: ['journalists', params],
    queryFn: () => getJournalists(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook to fetch journalist by slug
 * @param {string} slug - Journalist slug
 * @returns {Object} React Query result
 */
export const useJournalist = (slug) => {
  return useQuery({
    queryKey: ['journalist', slug],
    queryFn: () => getJournalistBySlug(slug),
    enabled: !!slug, // Only run if slug is provided
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook to fetch journalist score history
 * @param {string} slug - Journalist slug
 * @returns {Object} React Query result
 */
export const useJournalistScoreHistory = (slug) => {
  return useQuery({
    queryKey: ['journalist', slug, 'scoreHistory'],
    queryFn: () => getJournalistScoreHistory(slug),
    enabled: !!slug,
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}

/**
 * Hook to fetch journalist claims
 * @param {string} slug - Journalist slug
 * @param {Object} params - Query parameters
 * @returns {Object} React Query result
 */
export const useJournalistClaims = (slug, params = {}) => {
  return useQuery({
    queryKey: ['journalist', slug, 'claims', params],
    queryFn: () => getJournalistClaims(slug, params),
    enabled: !!slug,
    staleTime: 1000 * 60 * 2, // 2 minutes
  })
}

/**
 * Hook to fetch leaderboard
 * @param {Object} params - Query parameters (score_type, limit)
 * @returns {Object} React Query result
 */
export const useLeaderboard = (params = {}) => {
  return useQuery({
    queryKey: ['leaderboard', params],
    queryFn: () => getLeaderboard(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}
