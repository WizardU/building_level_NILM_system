<template>
  <header class="header">
    <div class="brand">
      <div class="brand-logo">⚡</div>
      <div class="brand-text">
        <div class="brand-title">{{ $t('system.title') }}</div>
        <div class="brand-sub">UK-DALE · Seq2Point · ONNX Runtime</div>
      </div>
    </div>

    <div class="header-controls">
      <el-tag v-if="store.backend" :type="store.backend === 'onnx' ? 'success' : 'warning'" round>
        {{ $t(`status.backend.${store.backend}`) }}
      </el-tag>

      <el-button-group>
        <el-button
          v-for="item in navItems"
          :key="item.path"
          :type="$route.path === item.path ? 'primary' : 'default'"
          @click="$router.push(item.path)"
        >
          {{ $t(item.label) }}
        </el-button>
      </el-button-group>

      <el-button plain @click="store.toggleDrawer">{{ $t('nav.team') }}</el-button>

      <el-dropdown @command="handleLanguageChange">
        <el-button circle>🌐</el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="zh" :disabled="locale === 'zh'">简体中文</el-dropdown-item>
            <el-dropdown-item command="en" :disabled="locale === 'en'">English</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-badge :value="store.alertCount" :hidden="store.alertCount === 0" type="danger">
        <el-button circle icon="Bell" @click="$router.push('/analytics')" />
      </el-badge>

      <el-button text @click="logout">{{ $t('nav.logout') }}</el-button>
    </div>
  </header>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getModelStatus } from '../api/disaggregation'
import { useNilmStore } from '../store/useNilmStore'

const store = useNilmStore()
const router = useRouter()
const { t, locale } = useI18n()

const navItems = [
  { path: '/', label: 'nav.dashboard' },
  { path: '/evaluation', label: 'nav.evaluation' },
  { path: '/analytics', label: 'nav.analytics' }
]

const handleLanguageChange = (lang) => {
  locale.value = lang
  store.setLanguage(lang)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}

onMounted(async () => {
  try {
    const status = await getModelStatus()
    store.setEngine(status)
  } catch (err) {
    // Header status is optional; the dashboard surfaces errors.
  }
})
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  padding: 12px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-logo {
  width: 38px;
  height: 38px;
  background: #ccfbf1;
  color: #0d9488;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.brand-title {
  font-weight: 700;
  font-size: 16px;
  color: #0f172a;
}
.brand-sub {
  font-size: 11px;
  color: #64748b;
}
.header-controls {
  display: flex;
  align-items: center;
  gap: 14px;
}
</style>
