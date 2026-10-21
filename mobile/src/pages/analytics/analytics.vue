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
            <text class="summary-label">预估总电费</text>
            <text class="summary-value">¥{{ bill.totalCost?.toFixed(2) || '0.00' }}</text>
          </view>
          <view class="summary-divider" />
          <view class="summary-col">
            <text class="summary-label">总用电量</text>
            <text class="summary-value">{{ bill.totalKWh?.toFixed(2) || '0.00' }} kWh</text>
          </view>
        </view>

        <view class="section">
          <text class="section-title">分项用电账单</text>
          <view v-for="(item, idx) in bill.breakdown" :key="item.key" class="bill-row">
            <view class="bill-left">
              <text class="bill-name">{{ item.name }}</text>
              <view class="progress">
                <view class="progress-bar" :style="{ width: `${Math.min(item.ratio, 100)}%`, background: colors[idx % colors.length] }" />
              </view>
            </view>
            <view class="bill-right">
              <text class="bill-kwh">{{ item.kWh?.toFixed(2) }} kWh</text>
              <text class="bill-cost">¥{{ item.cost?.toFixed(2) }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <text class="section-title">告警日志</text>
            <view v-if="store.alertCount > 0" class="badge"
              ><text>{{ store.alertCount }} 条未处理</text></view
            >
          </view>

          <view v-if="!store.alerts.length" class="empty"
            ><text class="empty-text">暂无告警</text></view
          >

          <view
            v-for="alert in store.alerts"
            :key="alert.id"
            class="alert-row"
            :class="alert.type"
          >
            <view class="alert-dot" :class="alert.type" />
            <view class="alert-body">
              <text class="alert-title">{{ alert.title }}</text>
              <text class="alert-msg">{{ alert.message }}</text>
              <text class="alert-time">{{ alert.time }}</text>
            </view>
            <text class="alert-status">{{ alert.status }}</text>
          </view>
        </view>

        <text v-if="lastUpdate" class="last-update">更新于 {{ lastUpdate }}</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getEnergyBill, getAlerts, getOverview } from '../../utils/api.js'
import store from '../../utils/store.js'

const refreshing = ref(false)
const bill = ref({ totalCost: 0, totalKWh: 0, breakdown: [] })
const lastUpdate = ref('')

const colors = ['#0D9488', '#0284C7', '#F59E0B', '#8B5CF6', '#EC4899', '#10B981']

async function load() {
  try {
    const [energy, alerts, overview] = await Promise.all([
      getEnergyBill(store.buildingId, store.meterId),
      getAlerts(store.buildingId),
      getOverview(store.meterId)
    ])
    bill.value = energy || { totalCost: 0, totalKWh: 0, breakdown: [] }
    store.alerts = alerts?.items || []
    store.alertCount = store.alerts.filter((a) => a.status === '未处理').length
    store.overview = { ...(store.overview || {}), ...overview }
    const now = new Date()
    lastUpdate.value = `${String(now.getHours()).padStart(2, '0')}:${String(
      now.getMinutes()
    ).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
  } catch (e) {
    console.error('analytics load error', e)
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
  color: #ef4444;
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
</style>
