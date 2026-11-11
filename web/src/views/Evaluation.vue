<template>
  <div class="evaluation-page" v-loading="loading">
    <el-row :gutter="20" class="mb-20">
      <el-col :md="10" :xs="24">
        <RadarChart :reports="reports" :loading="loading" />
      </el-col>
      <el-col :md="14" :xs="24">
        <div class="card">
          <h3>{{ $t('evaluation.ablationTitle') }}</h3>
          <p class="desc">{{ $t('evaluation.ablationDesc') }}</p>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item :label="$t('evaluation.engine')">
              {{ engine.backend || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('evaluation.dataset')">
              {{ engine.dataset || 'UK-DALE' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('evaluation.samples')">
              {{ reports.samples || 0 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('dashboard.model')">
              {{ reports.model_version || engine.model_version || '-' }}
            </el-descriptions-item>
          </el-descriptions>
          <el-alert
            v-if="!reports.samples"
            type="warning"
            :title="$t('evaluation.noData')"
            show-icon
            class="mt-16"
            :closable="false"
          />
        </div>
      </el-col>
    </el-row>

    <div class="card">
      <h3>{{ $t('evaluation.tableTitle') }}</h3>
      <el-table :data="reports.per_appliance || []" style="width: 100%" stripe>
        <el-table-column :label="$t('evaluation.appliance')">
          <template #default="scope">
            {{ te(`appliances.${keyOf(scope.row.appliance)}`) ? t(`appliances.${keyOf(scope.row.appliance)}`) : scope.row.appliance }}
          </template>
        </el-table-column>
        <el-table-column prop="model" :label="$t('evaluation.model')" width="120" />
        <el-table-column :label="$t('evaluation.mae')" width="110">
          <template #default="scope">{{ Number(scope.row.mae).toFixed(1) }}</template>
        </el-table-column>
        <el-table-column :label="$t('evaluation.sae')" width="100">
          <template #default="scope">{{ Number(scope.row.sae).toFixed(3) }}</template>
        </el-table-column>
        <el-table-column :label="$t('evaluation.stateF1')" width="110">
          <template #default="scope">{{ pct(scope.row.state_f1) }}</template>
        </el-table-column>
        <el-table-column :label="$t('evaluation.eventF1')" width="110">
          <template #default="scope">{{ pct(scope.row.event_f1) }}</template>
        </el-table-column>
        <el-table-column prop="samples" :label="$t('evaluation.samples')" width="120" />
        <el-table-column prop="on_threshold" :label="$t('appliances.threshold')" width="120" />
      </el-table>
      <el-empty
        v-if="!reports.samples && !loading"
        :description="$t('evaluation.noData')"
        :image-size="80"
      />
    </div>

    <div v-if="whited.available" class="card block mt-20">
      <h3>{{ $t('evaluation.whitedTitle') }}</h3>
      <p class="desc">{{ $t('evaluation.whitedDesc') }}</p>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item :label="$t('evaluation.whitedSamples')">
          {{ whited.index?.used ?? whited.metrics?.samples ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.classes')">
          {{ whited.index?.classes ?? whited.metrics?.classes ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.devices')">
          {{ whited.index?.devices ?? whited.metrics?.devices ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.evaluatedClasses')">
          {{ whited.metrics?.split?.classes_in_test ?? '-' }} /
          {{ whited.index?.classes ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.accuracy')">
          {{ pct(whitedBest.accuracy) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.macroF1')">
          {{ pct(whitedBest.macro_f1) }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('evaluation.top3')">
          {{ pct(whitedBest.top3_accuracy) }}
        </el-descriptions-item>
      </el-descriptions>
      <h4 class="sub-title">{{ $t('evaluation.confusion') }}</h4>
      <el-table :data="(whited.metrics?.confusion_top || []).slice(0, 6)" size="small">
        <el-table-column prop="true" :label="$t('evaluation.trueLabel')" />
        <el-table-column prop="predicted" :label="$t('evaluation.predicted')" />
        <el-table-column prop="count" :label="$t('evaluation.count')" width="90" />
      </el-table>
    </div>
    <el-empty
      v-else-if="!loading"
      class="mt-20"
      :description="$t('evaluation.whitedMissing')"
      :image-size="60"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { getModelEvaluationMetrics, getModelStatus } from '../api/disaggregation'
import { getWhitedDataset } from '../api/datasets'
import RadarChart from '../charts/RadarChart.vue'

const { t, te } = useI18n()
const reports = ref({ indicators: [], series: [], per_appliance: [] })
const engine = ref({})
const whited = ref({ available: false })
const loading = ref(false)

const whitedBest = computed(() => {
  const metrics = whited.value.metrics
  if (!metrics?.best_model) return {}
  return metrics.models?.[metrics.best_model] || {}
})

const keyOf = (type) => (type === 'washing_machine' ? 'washingMachine' : type)
const pct = (value) => `${(Number(value || 0) * 100).toFixed(1)}%`

onMounted(async () => {
  loading.value = true
  try {
    const [reportData, status, whitedData] = await Promise.all([
      getModelEvaluationMetrics(),
      getModelStatus(),
      getWhitedDataset()
    ])
    reports.value = reportData || {}
    engine.value = status || {}
    whited.value = whitedData || { available: false }
  } catch (err) {
    reports.value = { indicators: [], series: [], per_appliance: [] }
    whited.value = { available: false }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 24px;
  height: 100%;
  box-sizing: border-box;
}
.desc {
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
}
.block {
  height: auto;
}
.mt-20 {
  margin-top: 20px;
}
.sub-title {
  margin: 18px 0 10px;
  color: #0f172a;
  font-size: 14px;
}
.mb-20 {
  margin-bottom: 20px;
}
.mt-16 {
  margin-top: 16px;
}
</style>
