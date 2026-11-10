<template>
  <div v-loading="loading" class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-title">{{ $t('kpi.mainsPower') }}</div>
      <div class="kpi-value">
        {{ Math.round(data.mainsPower || 0) }} <span class="unit">W</span>
      </div>
      <div class="kpi-hint">{{ $t('kpi.liveMainsHint') }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-title">{{ $t('kpi.activeAppliances') }}</div>
      <div class="kpi-value accent">
        {{ data.activeDevices || 0 }} / {{ data.totalDevices || 0 }}
        <span class="unit">{{ $t('kpi.units') }}</span>
      </div>
      <div class="kpi-hint">{{ $t('kpi.activeHint') }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-title">{{ $t('kpi.f1Score') }}</div>
      <div class="kpi-value green">{{ ((data.f1Score || 0) * 100).toFixed(1) }}%</div>
      <div class="kpi-hint">{{ $t('kpi.f1Hint') }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-title">{{ $t('kpi.eventF1') }}</div>
      <div class="kpi-value blue">{{ ((data.eventF1 || 0) * 100).toFixed(1) }}%</div>
      <div class="kpi-hint">{{ $t('kpi.eventF1Hint') }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-title">{{ $t('kpi.mae') }}</div>
      <div class="kpi-value">{{ (data.maeScore || 0).toFixed(1) }} <span class="unit">W</span></div>
      <div class="kpi-hint">
        {{ $t('kpi.latency') }}: {{ data.latency != null ? `${data.latency} ms` : '-' }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false }
})
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}
.kpi-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.kpi-title {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}
.kpi-value {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  margin-top: 6px;
}
.kpi-value.accent {
  color: #0d9488;
}
.kpi-value.green {
  color: #10b981;
}
.kpi-value.blue {
  color: #0284c7;
}
.kpi-value .unit {
  font-size: 13px;
  font-weight: normal;
  color: #64748b;
}
.kpi-hint {
  margin-top: 6px;
  font-size: 11px;
  color: #94a3b8;
}
</style>
