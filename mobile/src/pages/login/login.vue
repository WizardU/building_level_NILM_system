<template>
  <view class="page">
    <view class="card">
      <view class="brand">
        <text class="logo">⚡</text>
        <text class="title">Building NILM</text>
        <text class="subtitle">智能负荷监测系统</text>
      </view>

      <view class="form">
        <view class="input-wrap">
          <text class="input-icon">👤</text>
          <input v-model="username" class="input" placeholder="用户名" />
        </view>

        <view class="input-wrap">
          <text class="input-icon">🔒</text>
          <input v-model="password" class="input" password placeholder="密码" />
        </view>

        <button
          class="btn"
          :loading="loading"
          :disabled="loading"
          @click="onLogin"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </view>

      <text class="hint">默认账号 admin / admin123</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { login } from '../../utils/api.js'
import { setToken } from '../../utils/store.js'

const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)

const onLogin = async () => {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请输入账号和密码', icon: 'none' })
    return
  }
  loading.value = true
  try {
    const data = await login(username.value, password.value)
    setToken(data.access_token)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/home' })
    }, 500)
  } catch (e) {
    uni.showToast({ title: '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style>
.page {
  min-height: 100vh;
  padding: 80rpx 40rpx;
  background: linear-gradient(180deg, #e0f2fe 0%, #f8fafc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.card {
  width: 100%;
  background: #fff;
  border-radius: 32rpx;
  padding: 56rpx 40rpx;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}
.brand {
  text-align: center;
  margin-bottom: 48rpx;
}
.logo {
  font-size: 80rpx;
  display: block;
  margin-bottom: 16rpx;
}
.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #0f172a;
  display: block;
}
.subtitle {
  font-size: 26rpx;
  color: #64748b;
  display: block;
  margin-top: 8rpx;
}
.form {
  margin-bottom: 32rpx;
}
.input-wrap {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16rpx;
  padding: 0 20rpx;
  margin-bottom: 24rpx;
}
.input-icon {
  font-size: 28rpx;
  margin-right: 16rpx;
}
.input {
  flex: 1;
  height: 90rpx;
  font-size: 30rpx;
  color: #0f172a;
}
.btn {
  background: #0d9488;
  color: #fff;
  height: 96rpx;
  line-height: 96rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
}
.btn::after {
  border: none;
}
.hint {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #94a3b8;
}
</style>
