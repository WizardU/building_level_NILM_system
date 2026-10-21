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
        <view class="summary">
          <text class="summary-title">当前电表</text>
          <text class="summary-value">{{ meterName }}</text>
          <text class="summary-sub">共 {{ store.appliances.length }} 台设备 · {{ activeCount }} 台运行中</text>
        </view>

        <view class="filter-bar">
          <text
            v-for="tab in tabs"
            :key="tab.key"
            class="filter-item"
            :class="{ active: currentTab === tab.key }"
            @click="currentTab = tab.key"
          >
            {{ tab.label }}
          </text>
        </view>

        <view class="appliance-list">
          <ApplianceItem
            v-for="item in filteredAppliances"
            :key="item.id"
            :item="item"
          />
        </view>

        <text v-if="lastUpdate" class="last-update">更新于 {{ lastUpdate }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ApplianceItem from '../../components/ApplianceItem.vue'
import { getResult } from '../../utils/api.js'
import store, { activeDevicesCount } from '../../utils/store.js'

const refreshing = ref(false)
const currentTab = ref('all')
const lastUpdate = ref('')

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'on', label: '运行中' },
  { key: 'off', label: '待机' }
]

const meterName = computed(() => {
  const m = store.meters.find((x) => x.id === store.meterId)
  return m?.name || `Meter ${store.meterId}`
})
const activeCount = computed(() => activeDevicesCount.value)

const filteredAppliances = computed(() => {
  if (currentTab.value === 'on') return store.appliances.filter((a) => a.state)
  if (currentTab.value === 'off') return store.appliances.filter((a) => !a.state)
  return store.appliances
})

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

async function load() {
  try {
    const result = await getResult(store.meterId)
    store.appliances = normalizeAppliances(result?.appliances || [])
    const now = new Date()
    lastUpdate.value = `${String(now.getHours()).padStart(2, '0')}:${String(
      now.getMinutes()
    ).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  } catch (e) {
    console.error('appliances load error', e)
  }
}

async function onPullRefresh() {
  refreshing.value = true
  await load()
  refreshing.value = false
}

let timer = null

onMounted(async () => {
  await load()
  timer = setInterval(load, 15000)
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
.summary {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border-radius: 24rpx;
  padding: 40rpx;
  color: #fff;
  margin-bottom: 24rpx;
}
.summary-title {
  opacity: 0.7;
  font-size: 24rpx;
  display: block;
}
.summary-value {
  font-size: 34rpx;
  font-weight: 600;
  margin: 12rpx 0;
  display: block;
}
.summary-sub {
  opacity: 0.8;
  font-size: 24rpx;
  display: block;
}
.filter-bar {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.filter-item {
  flex: 1;
  text-align: center;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12rpx;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: #64748b;
}
.filter-item.active {
  background: #0d9488;
  color: #fff;
  border-color: #0d9488;
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
