import request from './request'

export const meterId = () => Number(localStorage.getItem('meter_id') || 101)
export const buildingId = () => Number(localStorage.getItem('building_id') || 1)

/**
 * Align the window to the current minute so repeated page loads hit the
 * backend cache instead of recomputing the whole inference every 15 s.
 */
export function currentWindow(hours = 2) {
  const end = new Date()
  end.setSeconds(0, 0)
  const start = new Date(end.getTime() - hours * 3600 * 1000)
  return { start: start.toISOString(), end: end.toISOString() }
}

export const getNilmOverview = () =>
  request.get('/disaggregation/overview', { params: { meter_id: meterId() } })

export const getDisaggregationResult = (options = {}) =>
  request.get('/disaggregation/result', {
    params: {
      meter_id: meterId(),
      ...currentWindow(options.hours || 2),
      refresh: options.refresh || undefined
    }
  })

export const runDisaggregation = () => {
  const { start, end } = currentWindow()
  return request.post('/disaggregation/run', {
    meter_id: meterId(),
    start,
    end
  })
}

export const getDisaggregationStatus = (taskId) =>
  request.get(`/disaggregation/status/${taskId}`)

export const getModelStatus = () => request.get('/disaggregation/models')

export const getModelEvaluationMetrics = () => request.get('/analytics/reports')

export const getMetrics = () => request.get('/analytics/metrics')

export const getBillingData = () =>
  request.get('/analytics/energy', { params: { meter_id: meterId() } })

export const getSafetyAlerts = async () => {
  const data = await request.get('/analytics/alerts', { params: { building_id: buildingId() } })
  return data?.items || []
}

export const resolveAlert = (alertId) => request.post(`/analytics/alerts/${alertId}/resolve`)

export const getSettings = () => request.get('/analytics/settings')

export const updateSettings = (payload) => request.put('/analytics/settings', payload)

export const listBuildings = () => request.get('/buildings')

export const listMeters = (id) => request.get('/meters', { params: { building_id: id } })

const keyFor = (type) => (type === 'washing_machine' ? 'washingMachine' : type)

export function toAppliances(result) {
  return (result?.appliances || []).map((appliance) => ({
    id: appliance.appliance_id || appliance.type,
    key: keyFor(appliance.type),
    type: appliance.type,
    name: appliance.name,
    power: Math.round(appliance.power_w || 0),
    state: !!appliance.state,
    confidence: Math.round((appliance.confidence || 0) * 1000) / 10,
    energyToday: `${(appliance.energy_kwh || 0).toFixed(3)} kWh`,
    percentage: appliance.percentage || 0,
    threshold: appliance.threshold_w
  }))
}

export function toSeries(result) {
  const mains = result?.mains_series || []
  const times = mains.map((point) => {
    const date = new Date(point.timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  return {
    times,
    mains: mains.map((point) => Math.round((point.power_kw || 0) * 1000)),
    appliances: (result?.appliances || []).map((appliance) => ({
      key: keyFor(appliance.type),
      name: appliance.name,
      data: (appliance.series || []).map((point) => Math.round((point.power_kw || 0) * 1000))
    }))
  }
}
