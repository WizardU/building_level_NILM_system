<template>
  <div v-loading="loading" class="chart-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">{{ $t('chart.title') }}</div>
        <div class="chart-sub">{{ $t('chart.sub') }}</div>
      </div>
      <el-tag type="success" effect="light" round>{{ $t('chart.liveTag') }}</el-tag>
    </div>
    <div ref="chartRef" style="width: 100%; height: 340px"></div>
    <el-empty v-if="empty" :description="$t('chart.empty')" :image-size="80" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'

const props = defineProps({
  series: { type: Object, default: () => ({ times: [], mains: [], appliances: [] }) },
  loading: { type: Boolean, default: false }
})

const { t, te, locale } = useI18n()
const chartRef = ref(null)
let chartInstance = null

const empty = computed(() => !props.series || (props.series.times || []).length === 0)

const palette = ['#10B981', '#F59E0B', '#0D9488', '#8B5CF6', '#EF4444']

function updateChart() {
  if (!chartInstance) return
  if (empty.value) {
    chartInstance.clear()
    return
  }
  const seriesList = [
    {
      name: t('chart.mains'),
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: props.series.mains,
      lineStyle: { width: 3, color: '#0284C7' },
      areaStyle: { color: 'rgba(2, 132, 199, 0.08)' }
    }
  ]
  ;(props.series.appliances || []).forEach((appliance, index) => {
    seriesList.push({
      name: te(`appliances.${appliance.key}`)
        ? t(`appliances.${appliance.key}`)
        : appliance.name,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: appliance.data,
      lineStyle: { color: palette[index % palette.length] }
    })
  })

  chartInstance.setOption(
    {
      tooltip: { trigger: 'axis' },
      legend: { top: 0, type: 'scroll' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: props.series.times },
      yAxis: { type: 'value', name: t('chart.yAxis') },
      series: seriesList
    },
    true
  )
}

watch(() => props.series, updateChart, { deep: true })
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.chart-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 15px;
}
.chart-sub {
  font-size: 12px;
  color: #64748b;
}
</style>
