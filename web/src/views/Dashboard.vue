<template>
  <div class="dashboard-page">
    <div class="toolbar mb-20">
      <el-select v-model="store.buildingId" placeholder="建筑" style="width: 180px" @change="onBuildingChange">
        <el-option
          v-for="b in store.buildings"
          :key="b.id"
          :label="b.name"
          :value="b.id"
        />
      </el-select>
      <el-select v-model="store.meterId" placeholder="电表" style="width: 280px" @change="onMeterChange">
        <el-option
          v-for="m in store.meters"
          :key="m.id"
          :label="m.name"
          :value="m.id"
        />
      </el-select>
      <el-button type="primary" :loading="refreshing" @click="refresh">刷新分解</el-button>
    </div>

    <el-alert
      v-if="computedKpiData.mainsPower > store.powerLimit"
      :title="$t('analytics.logs.overload.msg', { power: computedKpiData.mainsPower, limit: store.powerLimit })"
      type="error"
      show-icon
      class="mb-20"
      closable
    />

    <KpiCards :data="computedKpiData" class="mb-20" />
    <DisaggregationChart class="mb-20" />

    <h3>{{ $t('section.fleet') }}</h3>
    <ApplianceGrid :list="store.appliances" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  getNilmOverview,
  getAppliancesList,
  listBuildings,
  listMeters,
  runDisaggregation,
  getSafetyAlerts
} from '../api/disaggregation'
import { useNilmStore } from '../store/useNilmStore'
import KpiCards from '../components/KpiCards.vue'
import DisaggregationChart from '../charts/DisaggregationChart.vue'
import ApplianceGrid from '../components/ApplianceGrid.vue'

const store = useNilmStore()
const rawOverview = ref({})
const refreshing = ref(false)
let timer = null

const computedKpiData = computed(() => {
  const hasApplianceData = store.totalDevicesCount > 0
  return {
    ...rawOverview.value,
    mainsPower: hasApplianceData ? store.calculatedMainsPower : (rawOverview.value.mainsPower || 0),
    activeDevices: hasApplianceData ? store.activeDevicesCount : (rawOverview.value.activeDevices || 0),
    totalDevices: hasApplianceData ? store.totalDevicesCount : (rawOverview.value.totalDevices || 0)
  }
})

const loadMeta = async () => {
  const b = await listBuildings()
  store.buildings = b?.items || []
  const m = await listMeters(store.buildingId)
  store.meters = m?.items || []
}

const refresh = async () => {
  refreshing.value = true
  try {
    await runDisaggregation()
    rawOverview.value = await getNilmOverview()
    const listData = await getAppliancesList()
    store.appliances = Array.isArray(listData) ? listData : []
    const alerts = await getSafetyAlerts()
    store.alertCount = alerts.filter((a) => a.status === '未处理').length
  } catch (error) {
    console.error('获取家电数据失败:', error)
  } finally {
    refreshing.value = false
  }
}

const onBuildingChange = async (id) => {
  store.setBuildingId(id)
  const m = await listMeters(id)
  store.meters = m?.items || []
  if (store.meters.length) {
    store.setMeterId(store.meters[0].id)
    await refresh()
  }
}

const onMeterChange = async (id) => {
  store.setMeterId(id)
  await refresh()
}

onMounted(async () => {
  await loadMeta()
  await refresh()
  timer = setInterval(refresh, 15000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.mb-20 { margin-bottom: 20px; }
.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
</style>
