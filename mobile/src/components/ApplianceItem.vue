<template>
  <view class="appliance-row" :class="{ active: item.state }">
    <view class="icon-wrap" :style="{ background: item.state ? '#CCFBF1' : '#F1F5F9' }">
      <text class="icon">{{ icon }}</text>
    </view>
    <view class="info">
      <text class="name">{{ item.name }}</text>
      <text class="meta">
        {{ item.energyToday }} · 置信度 {{ item.confidence }}%
      </text>
    </view>
    <view class="state">
      <text class="power" :class="item.state ? 'on' : 'off'">
        {{ item.state ? `${item.power} W` : 'OFF' }}
      </text>
      <view class="badge" :class="item.state ? 'on' : 'off'">
        <text class="dot" />{{ item.state ? '运行中' : '待机' }}
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true }
})

const icon = computed(() => {
  const map = {
    fridge: '❄️',
    washing_machine: '🧺',
    washingMachine: '🧺',
    washer: '🧺',
    kettle: '☕',
    dishwasher: '🍽️',
    microwave: '♨️'
  }
  return map[props.item.key] || '⚡'
})
</script>

<style scoped>
.appliance-row {
  display: flex;
  align-items: center;
  background: #ffffff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  border: 1px solid #e2e8f0;
}
.appliance-row.active {
  border-color: #99f6e4;
  background: #f0fdfa;
}
.icon-wrap {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}
.icon {
  font-size: 40rpx;
}
.info {
  flex: 1;
  min-width: 0;
}
.name {
  font-size: 30rpx;
  font-weight: 600;
  color: #0f172a;
  display: block;
}
.meta {
  font-size: 22rpx;
  color: #64748b;
  display: block;
  margin-top: 4rpx;
}
.state {
  text-align: right;
  min-width: 120rpx;
}
.power {
  font-size: 32rpx;
  font-weight: 700;
  display: block;
}
.power.on {
  color: #0d9488;
}
.power.off {
  color: #94a3b8;
}
.badge {
  display: inline-flex;
  align-items: center;
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  margin-top: 8rpx;
}
.badge.on {
  color: #0d9488;
  background: #ccfbf1;
}
.badge.off {
  color: #64748b;
  background: #f1f5f9;
}
.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  margin-right: 8rpx;
}
.badge.on .dot {
  background: #0d9488;
}
.badge.off .dot {
  background: #94a3b8;
}
</style>
