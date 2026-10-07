<template>
  <view class="page">
    <view class="card">
      <text class="title">Building NILM</text>
      <input v-model="username" class="input" placeholder="用户名" />
      <input v-model="password" class="input" password placeholder="密码" />
      <button type="primary" @click="onLogin">登录</button>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '../../utils/api.js'

const username = ref('admin')
const password = ref('admin123')

const onLogin = async () => {
  try {
    const data = await login(username.value, password.value)
    uni.setStorageSync('access_token', data.access_token)
    uni.switchTab({ url: '/pages/home/home' })
  } catch (e) {
    uni.showToast({ title: '登录失败', icon: 'none' })
  }
}
</script>

<style>
.page { min-height: 100vh; padding: 80rpx 40rpx; background: #e0f2fe; }
.card { background: #fff; border-radius: 24rpx; padding: 48rpx; }
.title { font-size: 44rpx; font-weight: 700; display: block; margin-bottom: 40rpx; }
.input { border: 1px solid #e2e8f0; border-radius: 12rpx; padding: 20rpx; margin-bottom: 24rpx; }
</style>
