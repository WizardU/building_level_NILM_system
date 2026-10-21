<template>
  <view class="chart-card">
    <view class="header">
      <text class="title">实时功率曲线</text>
      <text class="sub">W</text>
    </view>
    <view v-if="!chartData" class="empty">
      <text class="empty-text">暂无数据</text>
    </view>
    <qiun-data-charts
      v-else
      type="mix"
      :opts="opts"
      :chartData="chartData"
      :canvas2d="true"
      canvasId="powerChart"
      class="chart"
    />
  </view>
</template>

<script setup>
import { computed } from 'vue'
import QiunDataCharts from '@qiun/uni-ucharts'

const props = defineProps({
  data: { type: Object, default: null }
})

const chartData = computed(() => props.data)

const opts = {
  padding: [15, 10, 0, 10],
  enableScroll: false,
  legend: { show: true, position: 'top', float: 'right' },
  xAxis: {
    disableGrid: true,
    fontSize: 10,
    color: '#64748B',
    rotateLabel: true
  },
  yAxis: {
    disabled: false,
    disableGrid: false,
    gridColor: '#E2E8F0',
    fontSize: 10,
    color: '#64748B',
    min: 0
  },
  extra: {
    mix: {
      line: { type: 'curve', width: 2 }
    }
  },
  dataLabel: false,
  dataPointShape: false
}
</script>

<style scoped>
.chart-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 24rpx;
  border: 1px solid #e2e8f0;
  margin-bottom: 24rpx;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}
.title {
  font-size: 30rpx;
  font-weight: 600;
  color: #0f172a;
}
.sub {
  font-size: 22rpx;
  color: #94a3b8;
}
.chart {
  width: 100%;
  height: 400rpx;
}
.empty {
  height: 400rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.empty-text {
  color: #94a3b8;
  font-size: 28rpx;
}
</style>
