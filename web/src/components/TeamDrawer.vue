<template>
  <el-drawer v-model="store.drawerVisible" :title="$t('team.drawerTitle')" size="450px">
    <div class="drawer-content">
      <h4 class="section-title">{{ $t('team.rolesTitle') }}</h4>
      
      <div class="role-box">
        <div class="role-name">{{ $t('team.roles.jin.title') }}</div>
        <div class="role-desc">{{ $t('team.roles.jin.desc') }}</div>
      </div>

      <div class="role-box">
        <div class="role-name">{{ $t('team.roles.yang.title') }}</div>
        <div class="role-desc">{{ $t('team.roles.yang.desc') }}</div>
      </div>

      <div class="role-box">
        <div class="role-name">{{ $t('team.roles.yu.title') }}</div>
        <div class="role-desc">{{ $t('team.roles.yu.desc') }}</div>
      </div>

      <h4 class="section-title" style="margin-top: 24px;">{{ $t('team.sysTitle') }}</h4>
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item :label="$t('team.slidingWindow')">599 Points</el-descriptions-item>
        <el-descriptions-item :label="$t('team.inferenceEngine')">ONNX Runtime (PyTorch)</el-descriptions-item>
        <el-descriptions-item :label="$t('team.techStack')">Vue 3 + Element Plus + ECharts</el-descriptions-item>
      </el-descriptions>
    </div>
  </el-drawer>
</template>

<script setup>
import { useNilmStore } from '../store/useNilmStore'

const store = useNilmStore()
</script>

<style scoped>
.role-box { background: #F8FAFC; border-radius: 10px; padding: 12px; margin-bottom: 12px; border: 1px solid #E2E8F0; }
.role-name { font-weight: 700; color: #0F172A; font-size: 13px; margin-bottom: 4px; }
.role-desc { font-size: 12px; color: #64748B; line-height: 1.5; }
.section-title { font-weight: 700; color: #1E293B; margin-bottom: 12px; }
</style>