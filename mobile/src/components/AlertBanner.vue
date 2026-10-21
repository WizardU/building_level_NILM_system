<template>
  <view v-if="visible" class="alert-banner">
    <text class="icon">⚠️</text>
    <text class="msg">{{ message }}</text>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import store from '../utils/store.js'

const props = defineProps({
  power: { type: Number, default: 0 }
})

const visible = computed(() => props.power > store.powerLimit)
const message = computed(() =>
  `实时总功率 ${Math.round(props.power)} W，超过安全阈值 ${store.powerLimit} W`
)
</script>

<style scoped>
.alert-banner {
  display: flex;
  align-items: center;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 24rpx;
}
.icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}
.msg {
  flex: 1;
  font-size: 26rpx;
  color: #b91c1c;
  line-height: 1.4;
}
</style>
