<template>
  <div v-loading="loading" class="appliance-grid">
    <div
      v-for="item in list"
      :key="item.id"
      class="appliance-card"
      :class="{ active: item.state }"
    >
      <div class="card-top">
        <div
          class="app-icon"
          :style="{
            background: item.state ? '#CCFBF1' : '#F1F5F9',
            color: item.state ? '#0D9488' : '#94A3B8'
          }"
        >
          ⚡
        </div>
        <span class="state-badge" :class="item.state ? 'on' : 'off'">
          {{ item.state ? $t('appliances.on') : $t('appliances.off') }}
        </span>
      </div>

      <div class="app-name">
        {{ te(`appliances.${item.key}`) ? t(`appliances.${item.key}`) : item.name }}
      </div>

      <div class="power-val">
        <span class="num">{{ item.power }}</span>
        <span class="unit"> W</span>
      </div>

      <div class="card-footer">
        <div>
          {{ $t('appliances.confidence') }}: <strong>{{ item.confidence }}%</strong>
        </div>
        <div>{{ $t('appliances.today') }}: {{ item.energyToday }}</div>
      </div>
      <div v-if="item.threshold" class="threshold">
        {{ $t('appliances.threshold') }}: {{ item.threshold }} W ·
        {{ item.percentage }}%
      </div>
    </div>

    <el-empty v-if="!loading && list.length === 0" :description="$t('appliances.empty')" />
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t, te } = useI18n()

defineProps({
  list: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})
</script>

<style scoped>
.appliance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.appliance-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 18px;
  transition: all 0.2s ease;
}
.appliance-card.active {
  border-color: #0d9488;
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.08);
}
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.app-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.state-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
}
.state-badge.on {
  background: #ccfbf1;
  color: #0f766e;
}
.state-badge.off {
  background: #f1f5f9;
  color: #64748b;
}
.app-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}
.power-val {
  margin: 8px 0;
}
.power-val .num {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}
.power-val .unit {
  font-size: 12px;
  color: #64748b;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
  border-top: 1px dashed #f1f5f9;
  padding-top: 10px;
  margin-top: 10px;
}
.threshold {
  margin-top: 6px;
  font-size: 11px;
  color: #94a3b8;
}
</style>
