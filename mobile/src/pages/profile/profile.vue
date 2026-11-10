<template>
  <view class="page">
    <view class="header">
      <text class="avatar">👤</text>
      <text class="username">{{ username }}</text>
      <text class="role">{{ roleText }}</text>
    </view>

    <view class="section">
      <view class="cell" @click="editThreshold">
        <text class="cell-label">Power Alert Threshold</text>
        <text class="cell-value">{{ store.powerLimit }} W</text>
        <text class="arrow">▸</text>
      </view>
    </view>

    <view class="section">
      <view class="cell" @click="showAbout">
        <text class="cell-label">About NILM Mobile</text>
        <text class="arrow">▸</text>
      </view>
    </view>

    <button class="logout" @click="onLogout">Sign Out</button>
  </view>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import store, { clearToken } from '../../utils/store.js'
import { getSettings, updateSettings } from '../../utils/api.js'

const username = computed(() => {
  try {
    const token = uni.getStorageSync('access_token')
    if (!token) return 'admin'
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub || 'admin'
  } catch (e) {
    return 'admin'
  }
})

const roleText = 'System Administrator'

async function loadSettings() {
  try {
    const settings = await getSettings()
    if (settings?.power_limit_w) {
      store.powerLimit = Number(settings.power_limit_w)
    }
  } catch (e) {
    // keep the local value when offline
  }
}

function editThreshold() {
  uni.showModal({
    title: 'Power Alert Threshold',
    editable: true,
    placeholderText: 'Enter watts',
    success: async (res) => {
      if (!res.confirm) return
      const val = parseInt(res.content, 10)
      if (isNaN(val) || val <= 0) return
      try {
        await updateSettings({ power_limit_w: val })
        store.powerLimit = val
        uni.showToast({ title: 'Saved', icon: 'success' })
      } catch (e) {
        uni.showToast({ title: 'Save failed', icon: 'none' })
      }
    }
  })
}

function showAbout() {
  uni.showModal({
    title: 'About',
    content: 'NILM Mobile v1.0.0\nBuilding-level non-intrusive load monitoring',
    showCancel: false
  })
}

function onLogout() {
  uni.showModal({
    title: 'Sign out?',
    content: 'You will need to sign in again.',
    success: (res) => {
      if (res.confirm) {
        clearToken()
        uni.reLaunch({ url: '/pages/login/login' })
      }
    }
  })
}

onMounted(loadSettings)
</script>

<style>
.page {
  min-height: 100vh;
  background: #f8fafc;
  padding-bottom: 40rpx;
}
.header {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 80rpx 40rpx 60rpx;
  color: #fff;
  text-align: center;
}
.avatar {
  font-size: 100rpx;
  display: block;
}
.username {
  font-size: 40rpx;
  font-weight: 600;
  margin-top: 16rpx;
  display: block;
}
.role {
  font-size: 24rpx;
  opacity: 0.7;
  margin-top: 8rpx;
  display: block;
}
.section {
  background: #fff;
  border-radius: 16rpx;
  margin: 24rpx;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
.cell {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1px solid #f1f5f9;
}
.cell:last-child {
  border-bottom: none;
}
.cell-label {
  flex: 1;
  font-size: 30rpx;
  color: #0f172a;
}
.cell-value {
  font-size: 28rpx;
  color: #64748b;
  margin-right: 12rpx;
}
.arrow {
  color: #94a3b8;
  font-size: 28rpx;
}
.logout {
  margin: 48rpx 24rpx 0;
  background: #fee2e2;
  color: #b91c1c;
  border: none;
  border-radius: 16rpx;
  height: 96rpx;
  line-height: 96rpx;
  font-size: 32rpx;
  font-weight: 600;
}
.logout::after {
  border: none;
}
</style>
