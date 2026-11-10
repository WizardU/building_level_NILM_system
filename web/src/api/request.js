import axios from 'axios'

const service = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

service.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise = null

async function refreshToken() {
  const token = localStorage.getItem('refresh_token')
  if (!token) throw new Error('no refresh token')
  const response = await axios.post('/api/v1/auth/refresh', { refresh_token: token })
  const data = response.data?.data
  if (!data?.access_token) throw new Error('refresh failed')
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
  return data.access_token
}

service.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'data' in body) {
      return body.data
    }
    return body
  },
  async (error) => {
    const original = error.config
    const status = error.response?.status
    const isAuthCall = original?.url?.includes('/auth/')

    if (status === 401 && original && !original._retried && !isAuthCall) {
      original._retried = true
      try {
        refreshPromise = refreshPromise || refreshToken().finally(() => (refreshPromise = null))
        const token = await refreshPromise
        original.headers = { ...(original.headers || {}), Authorization: `Bearer ${token}` }
        return service(original)
      } catch (refreshError) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default service
