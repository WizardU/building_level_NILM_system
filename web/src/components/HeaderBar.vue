<template>
  <header class="header">
    <div class="brand">
    
      <div class="brand-text">
        <!-- 💡 使用 $t() 或 t() 获取响应式语言文案 -->
        <div class="brand-title">{{ $t('system.title') }}</div>
        <div class="brand-sub">Non-Intrusive Load Monitoring</div>
      </div>
    </div>

    <div class="header-controls">
      <el-select v-model="store.selectedDataset" size="default" style="width: 130px">
        <el-option label="UK-DALE" value="ukdale" />
        <el-option label="REDD" value="redd" />
        <el-option label="PLAID" value="plaid" />
      </el-select>

      <!-- 动态替换模型名称 -->
      <el-radio-group v-model="store.selectedModel" size="default">
        <el-radio-button value="baseline">{{ t('model.baseline') }}</el-radio-button>
        <el-radio-button value="proposed">{{ t('model.proposed') }}</el-radio-button>
      </el-radio-group>

      <!-- 动态替换路由按钮文案 -->
      <el-button-group>
        <el-button :type="$route.path === '/' ? 'primary' : 'default'" @click="$router.push('/')">
          {{ t('nav.dashboard') }}
        </el-button>
        <el-button :type="$route.path === '/evaluation' ? 'primary' : 'default'" @click="$router.push('/evaluation')">
          {{ t('nav.evaluation') }}
        </el-button>
        <el-button :type="$route.path === '/analytics' ? 'primary' : 'default'" @click="$router.push('/analytics')">
          {{ t('nav.analytics') }}
        </el-button>
      </el-button-group>

      <el-button type="primary" plain @click="store.toggleDrawer">
        <el-icon><InfoFilled /></el-icon> {{ t('nav.team') }}
      </el-button>

      <!-- ➕ 新增：中英文语言切换下拉菜单 -->
      <el-dropdown @command="handleLanguageChange">
        <el-button circle>
          🌐
        </el-button>
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
    </div>
  </header>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useNilmStore } from '../store/useNilmStore'

const store = useNilmStore()

// ➕ 1. 引入 vue-i18n
const { t, locale } = useI18n()

// ➕ 2. 语言切换回调函数
const handleLanguageChange = (lang) => {
  locale.value = lang       // 更新 vue-i18n 当前语言
  store.setLanguage(lang)   // 更新 Pinia 状态并同步写入 localStorage
}
</script>

<style scoped>
.header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #E2E8F0;
  padding: 12px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-logo { width: 38px; height: 38px; background: #CCFBF1; color: #0D9488; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; }
.brand-title { font-weight: 700; font-size: 16px; color: #0F172A; }
.brand-sub { font-size: 11px; color: #64748B; }
.header-controls { display: flex; align-items: center; gap: 14px; }
</style>