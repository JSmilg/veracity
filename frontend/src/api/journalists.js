import apiClient from './client'

/**
 * Get list of all journalists
 * @param {Object} params - Query parameters (search, ordering, page, page_size)
 * @returns {Promise} Paginated list of journalists
 */
export const getJournalists = async (params = {}) => {
  const { data } = await apiClient.get('/journalists/', { params })
  return data
}

/**
 * Get journalist by slug
 * @param {string} slug - Journalist slug
 * @returns {Promise} Journalist details with full statistics
 */
export const getJournalistBySlug = async (slug) => {
  const { data } = await apiClient.get(`/journalists/${slug}/`)
  return data
}

/**
 * Get score history for a journalist
 * @param {string} slug - Journalist slug
 * @returns {Promise} Historical score data
 */
export const getJournalistScoreHistory = async (slug) => {
  const { data } = await apiClient.get(`/journalists/${slug}/score_history/`)
  return data
}

/**
 * Get all claims for a journalist
 * @param {string} slug - Journalist slug
 * @param {Object} params - Query parameters (status)
 * @returns {Promise} List of claims
 */
export const getJournalistClaims = async (slug, params = {}) => {
  const { data } = await apiClient.get(`/journalists/${slug}/claims/`, { params })
  return data
}

/**
 * Get leaderboard rankings
 * @param {Object} params - Query parameters (score_type, limit)
 * @returns {Promise} Ranked list of journalists
 */
export const getLeaderboard = async (params = {}) => {
  const { data } = await apiClient.get('/journalists/leaderboard/', { params })
  return data
}

/**
 * Get club-specific journalist tier list
 * @param {string} club - Club name (e.g. 'Arsenal')
 * @returns {Promise} Tiered list of journalists for the club
 */
export const getClubTiers = async (club) => {
  const { data } = await apiClient.get('/journalists/club-tiers/', { params: { club } })
  return data
}
