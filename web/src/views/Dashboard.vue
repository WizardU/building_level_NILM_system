<template>
  <div class="dashboard-page">
    <div class="toolbar">
      <el-select
        v-model="store.buildingId"
        :placeholder="$t('dashboard.building')"
        style="width: 220px"
        @change="onBuildingChange"
      >
        <el-option v-for="b in store.buildings" :key="b.id" :label="b.name" :value="b.id" />
      </el-select>
      <el-select
        v-model="store.meterId"
        :placeholder="$t('dashboard.meter')"
        style="width: 260px"
        @change="onMeterChange"
      >
        <el-option v-for="m in store.meters" :key="m.id" :label="m.name" :value="m.id" />
      </el-select>
      <el-button type="primary" :loading="refreshing" @click="manualRefresh">
        {{ $t('dashboard.refresh') }}
      </el-button>
      <el-tag :type="backend === 'onnx' ? 'success' : 'warning'" effect="light" round>
        {{ backendLabel }}
      </el-tag>
      <span class="meta">{{ $t('dashboard.model') }}: {{ modelVersion || '-' }}</span>
      <span v-if="lastUpdated" class="meta">{{ $t('dashboard.updated') }}: {{ lastUpdated }}</span>
    </div>

    <el-alert v-if="error" type="error" :title="error" show-icon class="mb-16" @close="error = ''" />
    <el-alert
      v-if="backend !== 'onnx' && backend"
      type="warning"
      :title="$t('status.degraded')"
      show-icon
      class="mb-16"
    />
    <el-alert
      v-if="overLimit"
      type="error"
      :title="$t('analytics.logs.overload.msg', { power: kpi.mainsPower, limit: kpi.powerLimit })"
      show-icon
      class="mb-16"
      closable
    />

    <KpiCards :data="kpi" :loading="loading" class="mb-20" />
    <DisaggregationChart :series="series" :loading="loading" class="mb-20" />

    <h3>{{ $t('section.fleet') }}</h3>
    <ApplianceGrid :list="appliances" :loading="loading" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  getNilmOverview,
  getDisaggregationResult,
  getDisaggregationStatus,
  getSafetyAlerts,
  listBuildings,
  listMeters,
  runDisaggregation,
  toAppliances,
  toSeries
} from '../api/disaggregation'
import { useNilmStore } from '../store/useNilmStore'
import KpiCards from '../components/KpiCards.vue'
import DisaggregationChart from '../charts/DisaggregationChart.vue'
import ApplianceGrid from '../components/ApplianceGrid.vue'

const { t } = useI18n()
const store = useNilmStore()

const overview = ref({})
const result = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const error = ref('')
const lastUpdated = ref('')
let timer = null

const backend = computed(() => overview.value.backend || '')
const modelVersion = computed(() => overview.value.modelVersion || '')
const backendLabel = computed(() => t(`status.backend.${backend.value || 'unknown'}`))

const appliances = computed(() => toAppliances(result.value))
const series = computed(() => toSeries(result.value))

const kpi = computed(() => ({
  ...overview.value,
  activeDevices: appliances.value.filter((item) => item.state).length,
  totalDevices: appliances.value.length || overview.value.totalDevices || 0,
  powerLimit: overview.value.powerLimit || store.powerLimit
}))

const overLimit = computed(() => kpi.value.mainsPower > (kpi.value.powerLimit || 3000))

const stamp = () =>
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })

async function loadMeta() {
  try {
    const buildings = await listBuildings()
    store.buildings = buildings?.items || []
    if (store.buildings.length && !store.buildings.some((b) => b.id === store.buildingId)) {
      store.setBuildingId(store.buildings[0].id)
    }
    const meters = await listMeters(store.buildingId)
    store.meters = meters?.items || []
    if (store.meters.length && !store.meters.some((m) => m.id === store.meterId)) {
      store.setMeterId(store.meters[0].id)
    }
  } catch (err) {
    error.value = t('errors.loadMeta')
  }
}

async function refresh(force = false) {
  loading.value = true
  error.value = ''
  try {
    const [overviewData, resultData, alerts] = await Promise.all([
      getNilmOverview(),
      getDisaggregationResult({ refresh: force }),
      getSafetyAlerts()
    ])
    overview.value = overviewData || {}
    result.value = resultData
    store.alertCount = alerts.filter((alert) => alert.status === '未处理').length
    if (overview.value.powerLimit) store.powerLimit = overview.value.powerLimit
    lastUpdated.value = stamp()
  } catch (err) {
    error.value = err?.response?.data?.message || t('errors.refresh')
  } finally {
    loading.value = false
  }
}

function pollTask(taskId, attempts = 30) {
  return new Promise((resolve) => {
    let tries = 0
    const tick = setInterval(async () => {
      tries += 1
      try {
        const status = await getDisaggregationStatus(taskId)
        if (status.status === 'completed' || status.status === 'failed' || tries >= attempts) {
          clearInterval(tick)
          resolve(status)
        }
      } catch (err) {
        clearInterval(tick)
        resolve({ status: 'failed' })
      }
    }, 1000)
  })
}

async function manualRefresh() {
  refreshing.value = true
  try {
    const { task_id: taskId } = await runDisaggregation()
    const status = await pollTask(taskId)
    if (status.status !== 'completed') {
      error.value = status.message || t('errors.task')
    }
    await refresh(true)
  } catch (err) {
    error.value = err?.response?.data?.message || t('errors.refresh')
  } finally {
    refreshing.value = false
  }
}

async function onBuildingChange(id) {
  store.setBuildingId(id)
  const meters = await listMeters(id)
  store.meters = meters?.items || []
  if (store.meters.length) store.setMeterId(store.meters[0].id)
  await refresh()
}

async function onMeterChange(id) {
  store.setMeterId(id)
  await refresh()
}

onMounted(async () => {
  await loadMeta()
  await refresh()
  timer = setInterval(() => refresh(), 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.mb-20 {
  margin-bottom: 20px;
}
.mb-16 {
  margin-bottom: 16px;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.meta {
  font-size: 12px;
  color: #64748b;
}
</style>
