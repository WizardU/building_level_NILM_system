<template>
  <el-row :gutter="16">
    <el-col :span="4.8" v-for="item in list" :key="item.id" style="width: 20%;">
      <div class="appliance-card" :class="{ active: item.state }">
        <div class="card-top">
          <div class="app-icon" :style="{ background: item.state ? '#CCFBF1' : '#F1F5F9', color: item.state ? '#0D9488' : '#94A3B8' }">⚡</div>
          <el-switch v-model="item.state" active-color="#0D9488" />
        </div>
        
        <!-- 💡 1. 家电名称：动态匹配 i18n 字典，找不到时回退显示原来的 item.name -->
        <div class="app-name">
          {{ te(`appliances.${item.key}`) ? t(`appliances.${item.key}`) : item.name }}
        </div>
        
        <div class="power-val">
          <span class="num">{{ item.state ? item.power : 0 }}</span>
          <span class="unit"> W</span>
        </div>
        
        <!-- 💡 2. 底部栏：替换置信度和今日文本 -->
        <div class="card-footer">
          <div>{{ $t('appliances.confidence') }}: <strong>{{ item.confidence }}%</strong></div>
          <div>{{ $t('appliances.today') }}: {{ item.energyToday }}</div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

// 引入 vue-i18n 的 t (翻译) 和 te (检查 key 是否存在)
const { t, te } = useI18n()

defineProps({
  list: { type: Array, default: () => [] }
})
</script>

<style scoped>
.appliance-card { background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0; padding: 18px; transition: all 0.2s ease; }
.appliance-card.active { border-color: #0D9488; box-shadow: 0 4px 12px rgba(13, 148, 136, 0.08); }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.app-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.app-name { font-weight: 600; color: #1E293B; font-size: 14px; }
.power-val { margin: 8px 0; }
.power-val .num { font-size: 24px; font-weight: 700; color: #0F172A; }
.power-val .unit { font-size: 12px; color: #64748B; }
.card-footer { display: flex; justify-content: space-between; font-size: 11px; color: #64748B; border-top: 1px dashed #F1F5F9; padding-top: 10px; margin-top: 10px; }
</style>