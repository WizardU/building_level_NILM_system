<template>
  <div class="chart-card" v-loading="loading">
    <div class="chart-title">{{ $t('evaluation.radarTitle') }}</div>
    <div v-show="!empty" ref="chartRef" style="width: 100%; height: 320px"></div>
    <el-empty v-if="empty && !loading" :description="$t('evaluation.noData')" :image-size="80" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'

const props = defineProps({
  reports: { type: Object, default: () => ({ indicators: [], series: [] }) },
  loading: { type: Boolean, default: false }
})

const { t, locale } = useI18n()
const chartRef = ref(null)
let chartInstance = null

const empty = computed(() => {
  const values = (props.reports?.series || []).flatMap((item) => item.value || [])
  return values.length === 0 || values.every((value) => value === 0)
})

function updateChart() {
  if (!chartInstance) return
  if (empty.value) {
    chartInstance.clear()
    return
  }
  const series = props.reports.series || []
  chartInstance.setOption(
    {
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      radar: { indicator: props.reports.indicators, radius: '65%' },
      series: [
        {
          type: 'radar',
          data: series.map((item) => ({
            value: item.value,
            name: item.key === 'baseline' ? t('model.baseline') : t('model.proposed'),
            itemStyle: {
              color: item.key === 'baseline' ? '#94A3B8' : '#0D9488'
            },
            areaStyle: { opacity: 0.12 }
          }))
        }
      ]
    },
    true
  )
}

watch(() => props.reports, updateChart, { deep: true })
watch(locale, updateChart)

const handleResize = () => chartInstance?.resize()

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  updateChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 20px;
}
.chart-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 15px;
  margin-bottom: 12px;
}
</style>
