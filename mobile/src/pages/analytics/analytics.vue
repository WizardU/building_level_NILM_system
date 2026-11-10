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
          <view class="summary-col">
            <text class="summary-label">Estimated Cost</text>
            <text class="summary-value">¥{{ (bill.totalCost || 0).toFixed(2) }}</text>
          </view>
          <view class="summary-divider" />
          <view class="summary-col">
            <text class="summary-label">Total Energy</text>
            <text class="summary-value">{{ (bill.totalKWh || 0).toFixed(2) }} kWh</text>
          </view>
        </view>

        <text v-if="windowText" class="window-text">Window: {{ windowText }}</text>
        <view v-if="bill.estimated" class="notice">
          <text class="notice-text">
            No disaggregation result yet. Showing total energy only.
          </text>
        </view>

        <view class="section">
          <text class="section-title">Energy Breakdown</text>
          <view v-for="(item, idx) in billRows" :key="item.key" class="bill-row">
            <view class="bill-left">
              <text class="bill-name">{{ item.name }}</text>
              <view class="progress">
                <view
                  class="progress-bar"
                  :style="{
                    width: `${Math.min(item.ratio, 100)}%`,
                    background: colors[idx % colors.length]
                  }"
                />
              </view>
            </view>
            <view class="bill-right">
              <text class="bill-kwh">{{ (item.kWh || 0).toFixed(2) }} kWh</text>
              <text class="bill-cost">¥{{ (item.cost || 0).toFixed(2) }}</text>
            </view>
          </view>
          <view v-if="!billRows.length" class="empty">
            <text class="empty-text">No data yet</text>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <text class="section-title">Alert Log</text>
            <view v-if="store.alertCount > 0" class="badge">
              <text>{{ store.alertCount }} open</text>
            </view>
          </view>

          <view v-if="!store.alerts.length" class="empty">
            <text class="empty-text">No alerts</text>
          </view>

          <view
            v-for="alert in store.alerts"
            :key="alert.id"
            class="alert-row"
            :class="alert.type"
          >
            <view class="alert-dot" :class="alert.type" />
            <view class="alert-body">
              <text class="alert-title">{{ titleOf(alert) }}</text>
              <text class="alert-msg">{{ messageOf(alert) }}</text>
              <text class="alert-time">{{ alert.time }}</text>
            </view>
            <text v-if="!alert.resolved" class="resolve" @click="resolve(alert)">
              Resolve
            </text>
            <text v-else class="alert-status">Resolved</text>
          </view>
        </view>

        <text v-if="lastUpdate" class="last-update">Updated {{ lastUpdate }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getEnergyBill, getAlerts, getOverview, resolveAlert } from '../../utils/api.js'
import { alertTitle, alertMessage, applianceLabel } from '../../utils/labels.js'
import store from '../../utils/store.js'

const refreshing = ref(false)
const bill = ref({ totalCost: 0, totalKWh: 0, breakdown: [] })
const lastUpdate = ref('')

const colors = ['#0D9488', '#0284C7', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']

const titleOf = (alert) => alertTitle(alert)
const messageOf = (alert) => alertMessage(alert)

const billRows = computed(() => {
  // The backend returns appliance names in Chinese; the mobile UI is English.
  const rows = (bill.value.breakdown || []).map((row) => ({
    ...row,
    name: applianceLabel(row.key, row.name)
  }))
  const unmetered = Number(bill.value.unmeteredKWh || 0)
  if (unmetered > 0) {
    rows.push({
      key: 'unmetered',
      name: 'Unmetered',
      kWh: unmetered,
      cost: unmetered * Number(bill.value.tariff || 0),
      ratio: bill.value.totalKWh
        ? Math.round((unmetered / bill.value.totalKWh) * 100)
        : 0
    })
  }
  return rows
})

const windowText = computed(() => {
  const window = bill.value.window
  if (!window?.start || !window?.end) return ''
  const start = new Date(window.start)
  const end = new Date(window.end)
  const fmt = (d) =>
    `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(
      2,
      '0'
    )} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  return `${fmt(start)} ~ ${fmt(end)}`
})

async function load() {
  try {
    const [energy, alerts, overview] = await Promise.all([
      getEnergyBill(store.buildingId, store.meterId),
      getAlerts(store.buildingId),
      getOverview(store.meterId)
    ])
    bill.value = energy || { totalCost: 0, totalKWh: 0, breakdown: [] }
    store.alerts = alerts?.items || []
    store.alertCount = store.alerts.filter((a) => !a.resolved).length
    store.overview = { ...(store.overview || {}), ...overview }
    const now = new Date()
    lastUpdate.value = `${String(now.getHours()).padStart(2, '0')}:${String(
      now.getMinutes()
    ).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  } catch (e) {
    console.error('analytics load error', e)
  }
}

async function resolve(alert) {
  try {
    await resolveAlert(alert.id)
    await load()
  } catch (e) {
    uni.showToast({ title: 'Failed to resolve', icon: 'none' })
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
  timer = setInterval(load, 30000)
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
  display: flex;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border-radius: 24rpx;
  padding: 40rpx;
  color: #fff;
  margin-bottom: 24rpx;
}
.summary-col {
  flex: 1;
  text-align: center;
}
.summary-divider {
  width: 1px;
  background: rgba(255, 255, 255, 0.2);
}
.summary-label {
  opacity: 0.7;
  font-size: 24rpx;
  display: block;
}
.summary-value {
  font-size: 42rpx;
  font-weight: 700;
  margin-top: 12rpx;
  display: block;
}
.section {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  border: 1px solid #e2e8f0;
  margin-bottom: 24rpx;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #0f172a;
}
.badge {
  background: #fee2e2;
  color: #b91c1c;
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}
.bill-row {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1px solid #f1f5f9;
}
.bill-left {
  flex: 1;
  min-width: 0;
}
.bill-name {
  font-size: 28rpx;
  color: #0f172a;
  display: block;
  margin-bottom: 8rpx;
}
.progress {
  height: 8rpx;
  background: #f1f5f9;
  border-radius: 4rpx;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  border-radius: 4rpx;
}
.bill-right {
  text-align: right;
  margin-left: 20rpx;
}
.bill-kwh {
  font-size: 22rpx;
  color: #64748b;
  display: block;
}
.bill-cost {
  font-size: 28rpx;
  font-weight: 600;
  color: #0d9488;
  display: block;
  margin-top: 4rpx;
}
.empty {
  padding: 40rpx 0;
  text-align: center;
}
.empty-text {
  color: #94a3b8;
  font-size: 28rpx;
}
.alert-row {
  display: flex;
  align-items: flex-start;
  padding: 20rpx 0;
  border-bottom: 1px solid #f1f5f9;
}
.alert-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  margin-top: 8rpx;
  margin-right: 16rpx;
}
.alert-dot.danger {
  background: #ef4444;
}
.alert-dot.warning {
  background: #f59e0b;
}
.alert-dot.info {
  background: #0284c7;
}
.alert-body {
  flex: 1;
  min-width: 0;
}
.alert-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #0f172a;
  display: block;
}
.alert-msg {
  font-size: 24rpx;
  color: #64748b;
  display: block;
  margin-top: 4rpx;
  line-height: 1.4;
}
.alert-time {
  font-size: 20rpx;
  color: #94a3b8;
  display: block;
  margin-top: 4rpx;
}
.alert-status {
  font-size: 22rpx;
  color: #10b981;
  margin-left: 16rpx;
  white-space: nowrap;
}
.resolve {
  font-size: 22rpx;
  color: #0d9488;
  margin-left: 16rpx;
  white-space: nowrap;
}
.last-update {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #94a3b8;
  padding-bottom: 40rpx;
}
.window-text {
  display: block;
  font-size: 22rpx;
  color: #94a3b8;
  margin: -8rpx 0 16rpx 8rpx;
}
.notice {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 12rpx;
  padding: 16rpx 20rpx;
  margin-bottom: 20rpx;
}
.notice-text {
  font-size: 22rpx;
  color: #92400e;
}
</style>
