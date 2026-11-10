<template>
  <div class="analytics-page" v-loading="loading">
    <el-row :gutter="20" class="mb-20">
      <el-col :md="14" :xs="24">
        <div class="card">
          <h3>{{ $t('analytics.billingTitle') }}</h3>
          <div class="cost-summary">
            {{ $t('analytics.estTotalCost') }}：
            <span class="price">￥{{ billing.totalCost ?? 0 }}</span>
            <span class="muted">
              ({{ $t('analytics.totalUsage') }}: {{ billing.totalKWh ?? 0 }} kWh)
            </span>
          </div>
          <div v-if="billing.window" class="window">
            {{ $t('analytics.window') }}: {{ formatWindow(billing.window) }}
            · {{ $t('analytics.tariff') }} ￥{{ billing.tariff }}/kWh
          </div>

          <el-alert
            v-if="billing.estimated"
            type="warning"
            :title="$t('analytics.estimated')"
            show-icon
            :closable="false"
            class="mb-12"
          />

          <el-table :data="tableRows" style="width: 100%; margin-top: 15px">
            <el-table-column :label="$t('analytics.colAppliance')">
              <template #default="scope">
                {{ nameOf(scope.row) }}
              </template>
            </el-table-column>
            <el-table-column prop="kWh" :label="$t('analytics.colUsage') + ' (kWh)'" />
            <el-table-column prop="cost" :label="$t('analytics.colCost')" />
            <el-table-column :label="$t('analytics.colRatio')">
              <template #default="scope">
                <el-progress :percentage="Number(scope.row.ratio || 0)" color="#0D9488" />
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!tableRows.length && !loading"
            :description="$t('evaluation.noData')"
            :image-size="60"
          />
        </div>
      </el-col>

      <el-col :md="10" :xs="24">
        <div class="card">
          <h3>{{ $t('analytics.safetyConfig') }}</h3>
          <el-form label-position="top">
            <el-form-item :label="$t('analytics.powerLimitLabel') + ' (W)'">
              <el-input-number v-model="form.power_limit_w" :step="500" :min="500" :max="30000" />
            </el-form-item>
            <el-form-item :label="$t('analytics.tariff') + ' (￥/kWh)'">
              <el-input-number v-model="form.tariff_cny_per_kwh" :step="0.1" :min="0" :max="10" />
            </el-form-item>
            <el-button type="primary" :loading="saving" @click="saveSettings">
              {{ $t('analytics.saved') }}
            </el-button>
          </el-form>

          <h3 style="margin-top: 24px">{{ $t('analytics.alertLogTitle') }}</h3>
          <el-timeline v-if="alerts.length">
            <el-timeline-item
              v-for="alert in alerts"
              :key="alert.id"
              :type="alert.type"
              :timestamp="alert.time"
            >
              <strong>
                {{ te(`analytics.logs.${alert.key}.title`) ? t(`analytics.logs.${alert.key}.title`) : alert.title }}
              </strong>
              <p class="alert-msg">
                {{ te(`analytics.logs.${alert.key}.msg`) ? t(`analytics.logs.${alert.key}.msg`, alert.params || {}) : alert.message }}
              </p>
              <el-button
                v-if="!alert.resolved"
                size="small"
                text
                type="primary"
                @click="resolve(alert)"
              >
                {{ $t('analytics.resolve') }}
              </el-button>
              <el-tag v-else size="small" type="success" effect="plain">
                {{ $t('analytics.resolved') }}
              </el-tag>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else :description="$t('analytics.emptyAlerts')" :image-size="60" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  getBillingData,
  getSafetyAlerts,
  getSettings,
  resolveAlert,
  updateSettings
} from '../api/disaggregation'
import { useNilmStore } from '../store/useNilmStore'

const { t, te } = useI18n()
const store = useNilmStore()

const billing = ref({ breakdown: [] })
const alerts = ref([])
const loading = ref(false)
const saving = ref(false)
const form = reactive({ power_limit_w: 3000, tariff_cny_per_kwh: 0.6 })

const tableRows = computed(() => {
  const rows = [...(billing.value.breakdown || [])]
  if (Number(billing.value.unmeteredKWh || 0) > 0) {
    rows.push({
      key: 'unmetered',
      name: t('analytics.unmetered'),
      kWh: billing.value.unmeteredKWh,
      cost: (billing.value.unmeteredKWh * (billing.value.tariff || 0)).toFixed(2),
      ratio: billing.value.totalKWh
        ? Math.round((billing.value.unmeteredKWh / billing.value.totalKWh) * 100)
        : 0,
      unmetered: true
    })
  }
  return rows
})

const keyOf = (type) => (type === 'washing_machine' ? 'washingMachine' : type)

const nameOf = (row) => {
  if (row.unmetered) return row.name
  return te(`appliances.${keyOf(row.key)}`) ? t(`appliances.${keyOf(row.key)}`) : row.name
}

const formatWindow = (window) => {
  const start = new Date(window.start)
  const end = new Date(window.end)
  return `${start.toLocaleString()} → ${end.toLocaleString()}`
}

async function load() {
  loading.value = true
  try {
    const [billingData, alertData, settings] = await Promise.all([
      getBillingData(),
      getSafetyAlerts(),
      getSettings()
    ])
    billing.value = billingData || {}
    alerts.value = alertData
    form.power_limit_w = Number(settings.power_limit_w)
    form.tariff_cny_per_kwh = Number(settings.tariff_cny_per_kwh)
    store.setPowerLimit(form.power_limit_w)
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    await updateSettings({
      power_limit_w: form.power_limit_w,
      tariff_cny_per_kwh: form.tariff_cny_per_kwh
    })
    store.setPowerLimit(form.power_limit_w)
    ElMessage.success(t('analytics.saved'))
    billing.value = await getBillingData()
  } finally {
    saving.value = false
  }
}

async function resolve(alert) {
  await resolveAlert(alert.id)
  alerts.value = await getSafetyAlerts()
  store.alertCount = alerts.value.filter((item) => item.status === '未处理').length
}

onMounted(load)
</script>

<style scoped>
.card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 20px;
}
.cost-summary {
  font-size: 14px;
  color: #64748b;
  margin-top: 6px;
}
.price {
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}
.muted {
  font-size: 12px;
}
.window {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
}
.mb-20 {
  margin-bottom: 20px;
}
.mb-12 {
  margin-bottom: 12px;
}
.alert-msg {
  margin: 4px 0;
  font-size: 12px;
  color: #64748b;
}
</style>
