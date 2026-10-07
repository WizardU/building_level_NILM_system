<template>
  <el-row :gutter="16">
    <el-col :span="6">
      <div class="kpi-card">
        <!-- 1. 总入户功率 -->
        <div class="kpi-title">{{ $t('kpi.mainsPower') }}</div>
        <div class="kpi-value">{{ data.mainsPower || 0 }} <span class="unit">W</span></div>
      </div>
    </el-col>
    <el-col :span="6">
      <div class="kpi-card">
        <!-- 2. 当前激活家电 -->
        <div class="kpi-title">{{ $t('kpi.activeAppliances') }}</div>
        <div class="kpi-value" style="color: #0D9488">
          {{ data.activeDevices || 0 }} / {{ data.totalDevices || 0 }} <span class="unit">{{ $t('kpi.units') }}</span>
        </div>
      </div>
    </el-col>
    <el-col :span="6">
      <div class="kpi-card">
        <!-- 3. 平均 F1-Score -->
        <div class="kpi-title">{{ $t('kpi.f1Score') }}</div>
        <div class="kpi-value" style="color: #10B981">{{ ((data.f1Score || 0) * 100).toFixed(1) }}%</div>
      </div>
    </el-col>
    <el-col :span="6">
      <div class="kpi-card">
        <!-- 4. MAE (平均绝对误差) -->
        <div class="kpi-title">{{ $t('kpi.mae') }}</div>
        <div class="kpi-value">{{ data.maeScore || 0 }} <span class="unit">W</span></div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup>
defineProps({
  data: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.kpi-card { background: #FFFFFF; border-radius: 14px; padding: 18px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.kpi-title { font-size: 12px; color: #64748B; font-weight: 500; }
.kpi-value { font-size: 26px; font-weight: 700; color: #0F172A; margin-top: 6px; }
.kpi-value .unit { font-size: 13px; font-weight: normal; color: #64748B; }
</style>