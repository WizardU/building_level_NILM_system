// Backend base URL. For phone testing on the same LAN, replace 127.0.0.1
// with the LAN IP of the computer running the backend, e.g.
// export const API_BASE = 'http://192.168.1.100:8000/api/v1'
export const API_BASE = 'http://127.0.0.1:8000/api/v1'

// Defaults kept in sync with backend/app/seed.py
export const DEFAULT_BUILDING_ID = 1
export const DEFAULT_METER_ID = 101
export const DEFAULT_POWER_LIMIT = 3000
