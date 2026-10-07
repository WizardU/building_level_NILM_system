<template>
  <div class="analytics-page">
    <el-row :gutter="20" class="mb-20">
      <!-- 分项账单占比卡片 -->
      <el-col :span="14">
        <div class="card">
          <h3> {{ $t('analytics.billingTitle') }}</h3>
          <div class="cost-summary">
            {{ $t('analytics.estTotalCost') }}：<span class="price">￥{{ billing.totalCost }}</span> 
            ({{ $t('analytics.totalUsage') }}: {{ billing.totalKWh }} kWh)
          </div>
          
          <el-table :data="billing.breakdown" style="width: 100%; margin-top: 15px;">
            <el-table-column :label="$t('analytics.colAppliance')">
              <template #default="scope">
                <!-- 优先通过 scope.row.key 或 scope.row.name 查找 i18n 翻译 -->
                {{ te(`appliances.${scope.row.key}`) ? t(`appliances.${scope.row.key}`) : scope.row.name }}
              </template>
            </el-table-column>
            <el-table-column prop="kWh" :label="$t('analytics.colUsage') + ' (kWh)'" />
            <el-table-column prop="cost" :label="$t('analytics.colCost')" />
            <el-table-column :label="$t('analytics.colRatio')">
              <template #default="scope">
                <el-progress :percentage="scope.row.ratio" color="#0D9488" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>

      <!-- 用电安全与阈值设置 -->
      <el-col :span="10">
        <div class="card">
          <h3>{{ $t('analytics.safetyConfig') }}</h3>
          <el-form label-position="top">
            <el-form-item :label="$t('analytics.powerLimitLabel') + ' (W)'">
              <el-input-number v-model="store.powerLimit" :step="500" :min="1000" :max="10000" />
            </el-form-item>
          </el-form>

          <h3 style="margin-top: 24px;">{{ $t('analytics.alertLogTitle') }}</h3>
          <el-timeline>
            <el-timeline-item
              v-for="alert in alerts"
              :key="alert.id"
              :type="alert.type"
              :timestamp="alert.time"
            >
              <!-- 日志标题与内容的国际化匹配 -->
              <strong>{{ te(`analytics.logs.${alert.key}.title`) ? t(`analytics.logs.${alert.key}.title`) : alert.title }}</strong>
              <p style="margin: 4px 0; font-size: 12px; color: #64748B;">
                {{ te(`analytics.logs.${alert.key}.msg`) ? t(`analytics.logs.${alert.key}.msg`, alert.params || {}) : alert.message }}
              </p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getBillingData, getSafetyAlerts } from '../api/disaggregation'
import { useNilmStore } from '../store/useNilmStore'

const { t, te } = useI18n()
const store = useNilmStore()
const billing = ref({ breakdown: [] })
const alerts = ref([])

onMounted(async () => {
  billing.value = await getBillingData()
  alerts.value = await getSafetyAlerts()
})
</script>

<style scoped>
.card { background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; padding: 20px; }
.cost-summary { font-size: 14px; color: #64748B; margin-top: 6px; }
.price { font-size: 24px; font-weight: 700; color: #0F172A; }
.mb-20 { margin-bottom: 20px; }
</style>