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
        const body = res.data
        resolve(body && body.data !== undefined ? body.data : body)
      },
      fail: reject
    })
  })
}

export const login = (username, password) =>
  request('/auth/login', 'POST', { username, password })

export const getOverview = (meterId) =>
  request(`/disaggregation/overview?meter_id=${meterId}`)

export const getResult = (meterId) => {
  const end = new Date()
  const start = new Date(end.getTime() - 2 * 3600 * 1000)
  return request(
    `/disaggregation/result?meter_id=${meterId}&start=${encodeURIComponent(start.toISOString())}&end=${encodeURIComponent(end.toISOString())}`
  )
}
