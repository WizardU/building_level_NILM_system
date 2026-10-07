<template>
  <view class="page">
    <view class="kpi">
      <text class="label">总功率</text>
      <text class="value">{{ overview.mainsPower || 0 }} W</text>
      <text class="sub">活跃设备 {{ overview.activeDevices || 0 }} / {{ overview.totalDevices || 0 }}</text>
    </view>
    <view class="kpi small">
      <text>F1 {{ overview.f1Score }} · MAE {{ overview.maeScore }} · SAE {{ overview.saeScore }}</text>
    </view>
  </view>
</template>

<script>
import { getOverview } from '../../utils/api.js'
import { DEFAULT_METER_ID } from '../../utils/config.js'

export default {
  data() {
    return { overview: {} }
  },
  onShow() {
    getOverview(DEFAULT_METER_ID)
      .then((data) => { this.overview = data || {} })
      .catch((e) => console.error(e))
  }
}
</script>

<style>
.page { padding: 40rpx; }
.kpi { background: #0f172a; color: #fff; border-radius: 24rpx; padding: 40rpx; margin-bottom: 24rpx; }
.label { opacity: 0.7; font-size: 26rpx; }
.value { display: block; font-size: 64rpx; font-weight: 700; margin: 12rpx 0; }
.sub { opacity: 0.8; }
.small { background: #fff; color: #334155; border: 1px solid #e2e8f0; }
</style>
