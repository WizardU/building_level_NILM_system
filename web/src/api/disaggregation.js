import request from './request'

const meterId = () => Number(localStorage.getItem('meter_id') || 101)

export const getNilmOverview = () =>
  request.get('/disaggregation/overview', { params: { meter_id: meterId() } })

export const getAppliancesList = async () => {
  const end = new Date()
  const start = new Date(end.getTime() - 2 * 3600 * 1000)
  const result = await request.get('/disaggregation/result', {
    params: {
      meter_id: meterId(),
      start: start.toISOString(),
      end: end.toISOString()
    }
  })
  const apps = result?.appliances || []
  return apps.map((a) => ({
    id: a.type,
    key: a.type === 'washing_machine' ? 'washingMachine' : a.type,
    name: a.name,
    power: Math.round(a.power_w || 0),
    state: !!a.state,
    confidence: Math.round((a.confidence || 0.9) * 1000) / 10,
    energyToday: `${(a.energy_kwh || 0).toFixed(2)} kWh`
  }))
}

export const getDisaggregationTimeSeries = async () => {
  const end = new Date()
  const start = new Date(end.getTime() - 2 * 3600 * 1000)
  const result = await request.get('/disaggregation/result', {
    params: {
      meter_id: meterId(),
      start: start.toISOString(),
      end: end.toISOString()
    }
  })
  const mains = result?.mains_series || []
  const times = mains.map((p) => {
    const d = new Date(p.timestamp)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  })
  return {
    times,
    mains: mains.map((p) => Math.round(p.power_kw * 1000)),
    appliances: (result?.appliances || []).map((a) => ({
      key: a.type === 'washing_machine' ? 'washingMachine' : a.type,
      name: a.name,
      data: (a.series || []).map((p) => Math.round(p.power_kw * 1000))
    }))
  }
}

export const getModelEvaluationMetrics = () => request.get('/analytics/reports')

export const getBillingData = () =>
  request.get('/analytics/energy', { params: { meter_id: meterId() } })

export const getSafetyAlerts = async () => {
  const data = await request.get('/analytics/alerts', { params: { building_id: 1 } })
  return data?.items || []
}

export const listBuildings = () => request.get('/buildings')
export const listMeters = (buildingId) =>
  request.get('/meters', { params: { building_id: buildingId } })

export const runDisaggregation = () => {
  const end = new Date()
  const start = new Date(end.getTime() - 2 * 3600 * 1000)
  return request.post('/disaggregation/run', {
    meter_id: meterId(),
    start: start.toISOString(),
    end: end.toISOString()
  })
}
