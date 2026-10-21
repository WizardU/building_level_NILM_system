<template>
  <view class="picker-bar">
    <picker mode="selector" :range="buildingNames" :value="buildingIndex" @change="onBuildingChange">
      <view class="picker-item">
        <text class="picker-label">建筑</text>
        <text class="picker-value">{{ selectedBuilding?.name || '请选择' }}</text>
        <text class="arrow">▾</text>
      </view>
    </picker>
    <picker mode="selector" :range="meterNames" :value="meterIndex" @change="onMeterChange">
      <view class="picker-item">
        <text class="picker-label">电表</text>
        <text class="picker-value">{{ selectedMeter?.name || '请选择' }}</text>
        <text class="arrow">▾</text>
      </view>
    </picker>
  </view>
</template>

<script setup>
import { computed, watch } from 'vue'
import store, { setBuildingId, setMeterId } from '../utils/store.js'

const emit = defineEmits(['change'])

const buildingNames = computed(() => store.buildings.map((b) => b.name))
const meterNames = computed(() => store.meters.map((m) => m.name))

const selectedBuilding = computed(() =>
  store.buildings.find((b) => b.id === store.buildingId)
)
const selectedMeter = computed(() =>
  store.meters.find((m) => m.id === store.meterId)
)

const buildingIndex = computed(() =>
  store.buildings.findIndex((b) => b.id === store.buildingId)
)
const meterIndex = computed(() =>
  store.meters.findIndex((m) => m.id === store.meterId)
)

function onBuildingChange(e) {
  const idx = e.detail.value
  const b = store.buildings[idx]
  if (!b) return
  setBuildingId(b.id)
  emit('change', { buildingId: b.id })
}

function onMeterChange(e) {
  const idx = e.detail.value
  const m = store.meters[idx]
  if (!m) return
  setMeterId(m.id)
  emit('change', { meterId: m.id })
}

watch(
  () => store.meters,
  (meters) => {
    if (meters.length && !meters.find((m) => m.id === store.meterId)) {
      setMeterId(meters[0].id)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.picker-bar {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.picker-item {
  flex: 1;
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
}
.picker-label {
  font-size: 22rpx;
  color: #64748b;
  margin-right: 12rpx;
}
.picker-value {
  flex: 1;
  font-size: 28rpx;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.arrow {
  color: #94a3b8;
  font-size: 24rpx;
  margin-left: 8rpx;
}
</style>
