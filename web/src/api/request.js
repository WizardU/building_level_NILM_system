import axios from 'axios'

const service = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

service.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

service.interceptors.response.use(
  (response) => {
    const body = response.data
    if (body && typeof body === 'object' && 'data' in body) {
      return body.data
    }
    return body
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default service
