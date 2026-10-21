export function buildPowerChartData(result) {
  const mains = result?.mains_series || []
  if (!mains.length) return null

  const categories = mains.map((p) => {
    const d = new Date(p.timestamp)
    return `${String(d.getHours()).padStart(2, '0')}:${String(
      d.getMinutes()
    ).padStart(2, '0')}`
  })

  const series = [
    {
      name: '总功率',
      data: mains.map((p) => Math.round((p.power_kw || 0) * 1000)),
      color: '#0284C7',
      type: 'line',
      style: 'curve',
      area: {
        gradient: 'linear',
        color: ['rgba(2, 132, 199, 0.3)', 'rgba(2, 132, 199, 0.05)']
      }
    }
  ]

  const palette = ['#10B981', '#F59E0B', '#0D9488', '#8B5CF6', '#EC4899']
  ;(result?.appliances || []).forEach((a, idx) => {
    const data = (a.series || []).map((p) =>
      Math.round((p.power_kw || 0) * 1000)
    )
    if (data.some((v) => v > 0)) {
      series.push({
        name: a.name,
        data,
        color: palette[idx % palette.length],
        type: 'line',
        style: 'curve',
        width: 2
      })
    }
  })

  return { categories, series }
}
