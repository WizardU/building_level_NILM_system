<template>
  <view class="page">
    <scroll-view
      scroll-y
      class="scroll"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onPullRefresh"
    >
      <view class="container">
        <BuildingPicker @change="onPickerChange" />

        <AlertBanner :power="mainsPower" />

        <view class="kpi-row">
          <KpiCard
            label="总入户功率"
            :value="mainsPower"
            unit="W"
            value-color="#0284C7"
            border-color="#BFDBFE"
          />
          <KpiCard
            label="激活设备"
            :value="`${activeCount} / ${totalCount}`"
            unit="台"
            value-color="#0D9488"
            border-color="#99F6E4"
          />
        </view>

        <view class="kpi-row">
          <KpiCard
            label="F1-Score"
            :value="f1Score"
            unit="%"
            value-color="#10B981"
            border-color="#A7F3D0"
          />
          <KpiCard
            label="MAE"
            :value="maeScore"
            unit="W"
            value-color="#F59E0B"
            border-color="#FDE68A"
          />
        </view>

        <PowerChart :data="chartData" />

        <view class="section-header">
          <text class="section-title">家电运行状态</text>
          <button class="refresh-btn" size="mini" :loading="running" @click="runNilm">
            {{ running ? '分解中' : '刷新分解' }}
          </button>
        </view>

        <view class="appliance-list">
          <ApplianceItem
            v-for="item in appliances"
            :key="item.id"
            :item="item"
          />
        </view>

        <text v-if="lastUpdate" class="last-update"
          >更新于 {{ lastUpdate }}</text
        >
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import KpiCard from '../../components/KpiCard.vue'
import ApplianceItem from '../../components/ApplianceItem.vue'
import PowerChart from '../../components/PowerChart.vue'
import AlertBanner from '../../components/AlertBanner.vue'
import BuildingPicker from '../../components/BuildingPicker.vue'
import {
  listBuildings,
  listMeters,
  getOverview,
  getResult,
  runDisaggregation,
  getDisaggregationStatus,
  getAlerts
} from '../../utils/api.js'
import store, {
  setBuildingId,
  setMeterId,
  activeDevicesCount,
  totalDevicesCount,
  calculatedMainsPower
} from '../../utils/store.js'
import { buildPowerChartData } from '../../utils/chart.js'

const refreshing = ref(false)
const running = ref(false)
const lastUpdate = ref('')

const mainsPower = computed(() => {
  const fromApps = calculatedMainsPower.value
  if (fromApps > 0) return Math.round(fromApps)
  return Math.round(store.overview?.mainsPower || 0)
})
const activeCount = computed(
  () => activeDevicesCount.value || store.overview?.activeDevices || 0
)
const totalCount = computed(
  () => totalDevicesCount.value || store.overview?.totalDevices || 0
)
const f1Score = computed(() =>
  ((store.overview?.f1Score || 0) * 100).toFixed(1)
)
const maeScore = computed(() => (store.overview?.maeScore || 0).toFixed(1))
const appliances = computed(() => store.appliances)
const chartData = computed(() => buildPowerChartData(store.overview?.result))

async function loadMeta() {
  const b = await listBuildings()
  store.buildings = b?.items || []
  if (!store.buildings.find((x) => x.id === store.buildingId)) {
    const first = store.buildings[0]
    if (first) setBuildingId(first.id)
  }
  await loadMeters()
}

async function loadMeters() {
  const m = await listMeters(store.buildingId)
  store.meters = m?.items || []
  if (!store.meters.find((x) => x.id === store.meterId)) {
    const first = store.meters[0]
    if (first) setMeterId(first.id)
  }
}

async function loadDashboard() {
  try {
    const [overview, result, alerts] = await Promise.all([
      getOverview(store.meterId),
      getResult(store.meterId),
      getAlerts(store.buildingId)
    ])
    store.overview = {
      ...overview,
      result
    }
    store.appliances = normalizeAppliances(result?.appliances || [])
    store.alerts = alerts?.items || []
    store.alertCount = store.alerts.filter((a) => a.status === '未处理').length
    const now = new Date()
    lastUpdate.value = `${String(now.getHours()).padStart(2, '0')}:${String(
      now.getMinutes()
    ).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  } catch (e) {
    console.error('loadDashboard error', e)
  }
}

function normalizeAppliances(apps) {
  return apps.map((a) => ({
    id: a.appliance_id || a.type,
    key: a.type === 'washing_machine' ? 'washingMachine' : a.type,
    name: a.name,
    power: Math.round(a.power_w || 0),
    state: !!a.state,
    confidence: Math.round((a.confidence || 0.9) * 1000) / 10,
    energyToday: `${(a.energy_kwh || 0).toFixed(2)} kWh`,
    percentage: a.percentage || 0
  }))
}

async function onPullRefresh() {
  refreshing.value = true
  await refreshAll()
  refreshing.value = false
}

async function refreshAll() {
  await loadMeta()
  await loadDashboard()
}

async function onPickerChange({ buildingId, meterId }) {
  if (buildingId) {
    setBuildingId(buildingId)
    await loadMeters()
  }
  if (meterId) {
    setMeterId(meterId)
  }
  await loadDashboard()
}

async function runNilm() {
  running.value = true
  try {
    const { task_id: taskId } = await runDisaggregation(store.meterId)
    await pollTask(taskId)
    await loadDashboard()
    uni.showToast({ title: '分解完成', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '分解失败', icon: 'none' })
  } finally {
    running.value = false
  }
}

function pollTask(taskId) {
  return new Promise((resolve, reject) => {
    let attempts = 0
    const maxAttempts = 30
    const timer = setInterval(async () => {
      attempts++
      try {
        const status = await getDisaggregationStatus(taskId)
        if (status.status === 'completed') {
          clearInterval(timer)
          resolve(status)
        } else if (status.status === 'failed' || attempts >= maxAttempts) {
          clearInterval(timer)
          reject(new Error('task failed or timeout'))
        }
      } catch (e) {
        clearInterval(timer)
        reject(e)
      }
    }, 1000)
  })
}

let timer = null

onMounted(async () => {
  await refreshAll()
  timer = setInterval(loadDashboard, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style>
.page {
  height: 100vh;
  background: #f8fafc;
}
.scroll {
  height: 100%;
}
.container {
  padding: 24rpx;
}
.kpi-row {
  display: flex;
  gap: 16rpx;
  margin-bottom: 16rpx;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 32rpx 0 16rpx;
}
.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #0f172a;
}
.refresh-btn {
  margin: 0;
  background: #0d9488;
  color: #fff;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
  line-height: 52rpx;
}
.refresh-btn::after {
  border: none;
}
.appliance-list {
  margin-bottom: 24rpx;
}
.last-update {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #94a3b8;
  padding-bottom: 40rpx;
}
</style>
