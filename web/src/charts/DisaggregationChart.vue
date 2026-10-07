<template>
  <div class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">{{ $t('chart.title') }}</div>
        <div class="chart-sub">{{ $t('chart.sub') }}</div>
      </div>
      <el-tag type="success" effect="light" round>{{ $t('chart.liveTag') }}</el-tag>
    </div>
    <div ref="chartRef" style="width: 100%; height: 340px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import { getDisaggregationTimeSeries } from '../api/disaggregation'

const { t, te, locale } = useI18n()
const chartRef = ref(null)
let chartInstance = null

const updateChartOption = async () => {
  if (!chartInstance) return

  try {
    // 💡 从 Mock API 获取数据
    const res = await getDisaggregationTimeSeries()

    const seriesList = [
      {
        name: t('chart.mains'),
        type: 'line',
        smooth: true,
        data: res.mains,
        lineStyle: { width: 3, color: '#0284C7' },
        areaStyle: { color: 'rgba(2, 132, 199, 0.08)' }
      }
    ]

    const colorPalette = ['#10B981', '#F59E0B', '#0D9488', '#8B5CF6']
    res.appliances.forEach((app, idx) => {
      seriesList.push({
        name: te(`appliances.${app.key}`) ? t(`appliances.${app.key}`) : app.name,
        type: 'line',
        smooth: true,
        data: app.data,
        lineStyle: { color: colorPalette[idx % colorPalette.length] }
      })
    })

    chartInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { top: 0 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: res.times },
      yAxis: { type: 'value', name: t('chart.yAxis') },
      series: seriesList
    }, true)
  } catch (error) {
    console.error('加载分解图表数据失败:', error)
  }
}

watch(locale, () => {
  updateChartOption()
})

const handleResize = () => chartInstance?.resize()

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  updateChartOption()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card { background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.chart-title { font-weight: 700; color: #0F172A; font-size: 15px; }
.chart-sub { font-size: 12px; color: #64748B; }
</style>