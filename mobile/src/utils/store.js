import { reactive, computed, watch } from 'vue'
import {
  DEFAULT_BUILDING_ID,
  DEFAULT_METER_ID,
  DEFAULT_POWER_LIMIT
} from './config.js'

function getStored(key, defaultValue) {
  const raw = uni.getStorageSync(key)
  return raw !== undefined && raw !== '' && raw !== null ? raw : defaultValue
}

function setStored(key, value) {
  uni.setStorageSync(key, value)
}

const store = reactive({
  accessToken: getStored('access_token', ''),
  buildingId: Number(getStored('building_id', DEFAULT_BUILDING_ID)),
  meterId: Number(getStored('meter_id', DEFAULT_METER_ID)),
  buildings: [],
  meters: [],
  language: getStored('lang', 'zh'),
  powerLimit: Number(getStored('power_limit', DEFAULT_POWER_LIMIT)),
  appliances: [],
  alertCount: 0,
  overview: {},
  realtime: null,
  alerts: []
})

export const activeDevicesCount = computed(
  () => store.appliances.filter((a) => a.state).length
)
export const totalDevicesCount = computed(() => store.appliances.length)
export const calculatedMainsPower = computed(() =>
  store.appliances.reduce((sum, a) => sum + (a.state ? a.power : 0), 0)
)

watch(
  () => store.buildingId,
  (v) => setStored('building_id', v)
)
watch(
  () => store.meterId,
  (v) => setStored('meter_id', v)
)
watch(
  () => store.language,
  (v) => setStored('lang', v)
)
watch(
  () => store.powerLimit,
  (v) => setStored('power_limit', v)
)
watch(
  () => store.accessToken,
  (v) => setStored('access_token', v)
)

export function setToken(token) {
  store.accessToken = token
}

export function clearToken() {
  store.accessToken = ''
  uni.removeStorageSync('access_token')
}

export function setBuildingId(id) {
  store.buildingId = Number(id)
}

export function setMeterId(id) {
  store.meterId = Number(id)
}

export function setLanguage(lang) {
  store.language = lang
}

export default store
