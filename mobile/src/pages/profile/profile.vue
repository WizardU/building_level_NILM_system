<template>
  <view class="page">
    <view class="header">
      <text class="avatar">👤</text>
      <text class="username">{{ username }}</text>
      <text class="role">{{ roleText }}</text>
    </view>

    <view class="section">
      <view class="cell" @click="toggleLanguage">
        <text class="cell-label">语言</text>
        <text class="cell-value">{{ store.language === 'zh' ? '中文' : 'English' }}</text>
        <text class="arrow">▸</text>
      </view>
      <view class="cell" @click="editThreshold">
        <text class="cell-label">功率预警阈值</text>
        <text class="cell-value">{{ store.powerLimit }} W</text>
        <text class="arrow">▸</text>
      </view>
    </view>

    <view class="section">
      <view class="cell" @click="showAbout">
        <text class="cell-label">关于 NILM Mobile</text>
        <text class="arrow">▸</text>
      </view>
    </view>

    <button class="logout" @click="onLogout">退出登录</button>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import store, { clearToken, setLanguage } from '../../utils/store.js'

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

const roleText = '系统管理员'

function toggleLanguage() {
  const next = store.language === 'zh' ? 'en' : 'zh'
  setLanguage(next)
  uni.showToast({ title: next === 'zh' ? '已切换中文' : 'Switched to English', icon: 'none' })
}

function editThreshold() {
  uni.showModal({
    title: '设置功率预警阈值',
    editable: true,
    placeholderText: '请输入瓦数',
    success: (res) => {
      if (res.confirm) {
        const val = parseInt(res.content, 10)
        if (!isNaN(val) && val > 0) {
          store.powerLimit = val
          uni.showToast({ title: '设置成功', icon: 'success' })
        }
      }
    }
  })
}

function showAbout() {
  uni.showModal({
    title: '关于',
    content: 'NILM Mobile v1.0.0\n建筑级非侵入式负荷监测移动端 Demo',
    showCancel: false
  })
}

function onLogout() {
  uni.showModal({
    title: '确认退出',
    content: '退出后需要重新登录',
    success: (res) => {
      if (res.confirm) {
        clearToken()
        uni.reLaunch({ url: '/pages/login/login' })
      }
    }
  })
}
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
