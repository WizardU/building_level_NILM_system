<template>
  <div class="chart-card">
    <div class="chart-title">{{ $t('evaluation.radarTitle') }}</div>
    <div ref="chartRef" style="width: 100%; height: 300px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import { getModelEvaluationMetrics } from '../api/disaggregation'

const { t, locale } = useI18n()
const chartRef = ref(null)
let chartInstance = null

const updateChartOptions = async () => {
  if (!chartInstance) return

  try {
    const res = await getModelEvaluationMetrics()

    chartInstance.setOption({
      tooltip: { trigger: 'item' },
      legend: {
        bottom: 0,
        data: [t('model.baseline'), t('model.proposed')]
      },
      radar: {
        indicator: res.indicators,
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: [
          {
            value: res.series.find(s => s.key === 'baseline')?.value || [],
            name: t('model.baseline'),
            itemStyle: { color: '#94A3B8' }
          },
          {
            value: res.series.find(s => s.key === 'proposed')?.value || [],
            name: t('model.proposed'),
            itemStyle: { color: '#0D9488' }
          }
        ]
      }]
    }, true)
  } catch (error) {
    console.error('加载雷达图数据失败:', error)
  }
}

watch(locale, () => {
  updateChartOptions()
})

const handleResize = () => chartInstance?.resize()

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  updateChartOptions()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card { background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; padding: 20px; }
.chart-title { font-weight: 700; color: #0F172A; font-size: 15px; margin-bottom: 12px; }
</style>