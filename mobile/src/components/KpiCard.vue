<template>
  <view class="kpi-card" :style="{ borderColor: borderColor }">
    <text class="label">{{ label }}</text>
    <text class="value" :style="{ color: valueColor }">{{ value }}</text>
    <text v-if="unit" class="unit">{{ unit }}</text>
  </view>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  valueColor: { type: String, default: '#0F172A' },
  borderColor: { type: String, default: '#E2E8F0' }
})
</script>

<style scoped>
.kpi-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 24rpx;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  min-width: 0;
  flex: 1;
}
.label {
  font-size: 22rpx;
  color: #64748b;
  font-weight: 500;
  display: block;
}
.value {
  font-size: 40rpx;
  font-weight: 700;
  margin-top: 8rpx;
  display: block;
}
.unit {
  font-size: 20rpx;
  color: #94a3b8;
}
</style>
