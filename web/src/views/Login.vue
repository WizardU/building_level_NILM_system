<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>Building NILM</h2>
      <p class="sub">建筑级非侵入式负荷监测</p>
      <el-form @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" autocomplete="current-password" show-password />
        </el-form-item>
        <el-button type="primary" style="width: 100%" :loading="loading" @click="onSubmit">
          登录
        </el-button>
      </el-form>
      <p class="hint">默认账号 admin / admin123</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'

const router = useRouter()
const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)

const onSubmit = async () => {
  loading.value = true
  try {
    const data = await login(username.value, password.value)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('meter_id', '101')
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #e0f2fe 0%, #f8fafc 45%, #ccfbf1 100%);
}
.login-card {
  width: 380px;
  border-radius: 16px;
}
h2 { margin: 0 0 4px; color: #0f172a; }
.sub { color: #64748b; margin: 0 0 20px; font-size: 13px; }
.hint { margin-top: 16px; font-size: 12px; color: #94a3b8; text-align: center; }
</style>
