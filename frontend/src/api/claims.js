import apiClient from './client'

/**
 * Get list of all claims
 * @param {Object} params - Query parameters (validation_status, journalist, search, ordering, etc.)
 * @returns {Promise} Paginated list of claims
 */
export const getClaims = async (params = {}) => {
  const { data } = await apiClient.get('/claims/', { params })
  return data
}

/**
 * Get claim by ID
 * @param {number} id - Claim ID
 * @returns {Promise} Claim details
 */
export const getClaimById = async (id) => {
  const { data } = await apiClient.get(`/claims/${id}/`)
  return data
}

/**
 * Get latest claims (for homepage feed)
 * @returns {Promise} List of 20 most recent claims
 */
export const getLatestClaims = async () => {
  const { data } = await apiClient.get('/claims/latest/')
  return data
}

/**
 * Get pending claims awaiting validation
 * @param {Object} params - Query parameters
 * @returns {Promise} Paginated list of pending claims
 */
export const getPendingClaims = async (params = {}) => {
  const { data } = await apiClient.get('/claims/pending/', { params })
  return data
}

/**
 * Get validated claims (true or false)
 * @param {Object} params - Query parameters
 * @returns {Promise} Paginated list of validated claims
 */
export const getValidatedClaims = async (params = {}) => {
  const { data } = await apiClient.get('/claims/validated/', { params })
  return data
}

/**
 * Get overall platform statistics
 * @returns {Promise} Aggregate stats
 */
export const getClaimsStats = async () => {
  const { data } = await apiClient.get('/claims/stats/')
  return data
}

/**
 * Get distinct filter options for dropdowns
 * @returns {Promise} { clubs, publications, certainty_levels, validation_statuses }
 */
export const getFilterOptions = async () => {
  const { data } = await apiClient.get('/claims/filter-options/')
  return data
}

export const getPublicationLeaderboard = async (params = {}) => {
  const { data } = await apiClient.get('/claims/publication-leaderboard/', { params })
  return data
}

export const createClaim = async (claimData) => {
  const { data } = await apiClient.post('/claims/', claimData)
  return data
}

export const updateClaim = async (id, claimData) => {
  const { data } = await apiClient.patch(`/claims/${id}/`, claimData)
  return data
}

export const deleteClaim = async (id) => {
  await apiClient.delete(`/claims/${id}/`)
}
