<template>
  <div class="evaluation-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <RadarChart />
      </el-col>
      <el-col :span="12">
        <div class="eval-card">
          <!-- 💡 使用 $t() 动态替换标题与描述 -->
          <h3>{{ $t('evaluation.ablationTitle') }}</h3>
          <p class="desc">{{ $t('evaluation.ablationDesc') }}</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import RadarChart from '../charts/RadarChart.vue'

// 确保组件挂载了 i18n
const { t } = useI18n()
</script>

<style scoped>
.eval-card { background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; padding: 24px; height: 100%; box-sizing: border-box; }
.desc { color: #64748B; font-size: 14px; line-height: 1.6; }
</style>