<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>{{ $t('login.title') }}</h2>
      <p class="sub">{{ $t('login.subtitle') }}</p>
      <el-form @submit.prevent="onSubmit">
        <el-form-item :label="$t('login.username')">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item :label="$t('login.password')">
          <el-input
            v-model="password"
            type="password"
            autocomplete="current-password"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-alert v-if="error" :title="error" type="error" show-icon :closable="false" />
        <el-button
          type="primary"
          style="width: 100%; margin-top: 12px"
          :loading="loading"
          @click="onSubmit"
        >
          {{ $t('login.submit') }}
        </el-button>
      </el-form>
      <p class="hint">{{ $t('login.hint') }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'

const router = useRouter()
const { t } = useI18n()
const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)
const error = ref('')

const onSubmit = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await login(username.value, password.value)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    ElMessage.success(t('login.success'))
    router.push('/')
  } catch (err) {
    error.value = err?.response?.data?.message || t('login.failed')
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
h2 {
  margin: 0 0 4px;
  color: #0f172a;
}
.sub {
  color: #64748b;
  margin: 0 0 20px;
  font-size: 13px;
}
.hint {
  margin-top: 16px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}
</style>
