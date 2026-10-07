<template>
  <el-config-provider :locale="currentElementLocale">
    <div id="app">
      <HeaderBar v-if="!isLogin" />
      <main :class="isLogin ? 'login-wrap' : 'main-content'">
        <router-view />
      </main>
      <TeamDrawer v-if="!isLogin" />
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import HeaderBar from './components/HeaderBar.vue'
import TeamDrawer from './components/TeamDrawer.vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

const { locale } = useI18n()
const route = useRoute()
const isLogin = computed(() => route.path === '/login')
const currentElementLocale = computed(() => (locale.value === 'en' ? en : zhCn))
</script>

<style>
body {
  margin: 0;
  background-color: #F8FAFC;
  color: #1E293B;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}
.main-content {
  padding: 24px 28px;
  max-width: 1600px;
  margin: 0 auto;
}
.login-wrap { padding: 0; max-width: none; }
</style>
