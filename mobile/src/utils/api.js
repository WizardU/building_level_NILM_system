import { API_BASE } from './config.js'

function headers() {
  const token = uni.getStorageSync('access_token')
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' }
}

export function request(path, method = 'GET', data) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE}${path}`,
      method,
      data,
      header: headers(),
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('access_token')
          uni.reLaunch({ url: '/pages/login/login' })
          reject(new Error('unauthorized'))
          return
        }
        if (res.statusCode >= 400) {
          reject(new Error(res.data?.message || `HTTP ${res.statusCode}`))
          return
        }
        const body = res.data
        resolve(body && body.data !== undefined ? body.data : body)
      },
      fail: reject
    })
  })
}

// Auth
export const login = (username, password) =>
  request('/auth/login', 'POST', { username, password })

export const me = () => request('/auth/me')

// Buildings & meters
export const listBuildings = () => request('/buildings')
export const listMeters = (buildingId) =>
  request(`/meters?building_id=${buildingId}`)
export const getMeterCurrent = (meterId) =>
  request(`/meters/${meterId}/current`)

// Measurements
export const getRealtime = (meterId) =>
  request(`/measurements/realtime?meter_id=${meterId}`)

export const getHistory = (meterId, start, end, page = 1, size = 1000) =>
  request(
    `/measurements/history?meter_id=${meterId}&start=${encodeURIComponent(
      start
    )}&end=${encodeURIComponent(end)}&page=${page}&size=${size}`
  )

// Appliances
export const listAppliances = (meterId) =>
  request(`/appliances?meter_id=${meterId}`)

// Disaggregation
export const getOverview = (meterId) =>
  request(`/disaggregation/overview?meter_id=${meterId}`)

export const getResult = (meterId) => {
  const end = new Date()
  const start = new Date(end.getTime() - 2 * 3600 * 1000)
  return request(
    `/disaggregation/result?meter_id=${meterId}&start=${encodeURIComponent(
      start.toISOString()
    )}&end=${encodeURIComponent(end.toISOString())}`
  )
}

export const runDisaggregation = (meterId) => {
  const end = new Date()
  const start = new Date(end.getTime() - 2 * 3600 * 1000)
  return request('/disaggregation/run', 'POST', {
    meter_id: meterId,
    start: start.toISOString(),
    end: end.toISOString()
  })
}

export const getDisaggregationStatus = (taskId) =>
  request(`/disaggregation/status/${taskId}`)

// Analytics
export const getAnalyticsOverview = (buildingId) =>
  request(`/analytics/overview?building_id=${buildingId}`)

export const getEnergyBill = (buildingId, meterId) =>
  request(
    `/analytics/energy?building_id=${buildingId}&meter_id=${meterId}`
  )

export const getAlerts = (buildingId) =>
  request(`/analytics/alerts?building_id=${buildingId}`)

export const getReports = () => request('/analytics/reports')
