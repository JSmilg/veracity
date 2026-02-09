import apiClient from './client'

export const getTransferTimeline = async (id) => {
  const { data } = await apiClient.get(`/transfers/${id}/timeline/`)
  return data
}
