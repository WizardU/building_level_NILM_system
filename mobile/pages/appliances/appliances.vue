<template>
  <view class="page">
    <view v-for="a in appliances" :key="a.appliance_id" class="row">
      <view>
        <text class="name">{{ a.name }}</text>
        <text class="meta">{{ a.energy_kwh }} kWh · {{ a.percentage }}%</text>
      </view>
      <text :class="a.state ? 'on' : 'off'">{{ a.state ? Math.round(a.power_w) + ' W' : 'OFF' }}</text>
    </view>
  </view>
</template>

<script>
import { getResult } from '../../utils/api.js'
import { DEFAULT_METER_ID } from '../../utils/config.js'

export default {
  data() {
    return { appliances: [] }
  },
  onShow() {
    getResult(DEFAULT_METER_ID)
      .then((data) => { this.appliances = (data && data.appliances) || [] })
      .catch((e) => console.error(e))
  }
}
</script>

<style>
.page { padding: 24rpx; }
.row {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; border-radius: 16rpx; padding: 28rpx; margin-bottom: 16rpx;
  border: 1px solid #e2e8f0;
}
.name { font-weight: 600; display: block; }
.meta { font-size: 22rpx; color: #64748b; }
.on { color: #0d9488; font-weight: 700; }
.off { color: #94a3b8; }
</style>
