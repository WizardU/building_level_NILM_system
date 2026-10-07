import request from './request'

export const login = (username, password) =>
  request.post('/auth/login', { username, password })

export const me = () => request.get('/auth/me')
