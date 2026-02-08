import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 120000, // MetaCheck workflows can take longer; allow up to 120s
})

export async function getHealth() {
  const { data } = await apiClient.get('/api/health')
  return data
}

export async function getDomainConfig() {
  const { data } = await apiClient.get('/api/config/domain-categories')
  return data
}

export async function getToolSettings() {
  const { data } = await apiClient.get('/api/config/settings')
  return data
}

export async function putToolSettings(payload) {
  const { data } = await apiClient.put('/api/config/settings', payload)
  return data
}

export async function postReloadSettings() {
  const { data } = await apiClient.post('/api/admin/reload-settings')
  return data
}

export async function postExtract(payload) {
  const { data } = await apiClient.post('/api/extract', payload)
  return data
}

export async function postVerify(payload) {
  const { data } = await apiClient.post('/api/verify', payload)
  return data
}

export async function postCompare(payload) {
  const { data } = await apiClient.post('/api/compare', payload)
  return data
}
