<template>
  <div class="page">
    <n-space vertical :size="12">
      <n-page-header title="数据管理" subtitle="查看当前数据源、基金配置与系统最近状态">
        <template #extra>
          <n-button size="small" :loading="loading" @click="fetchData">刷新</n-button>
        </template>
      </n-page-header>

      <n-grid :cols="24" :x-gap="12" :y-gap="12">
        <n-gi :span="6">
          <n-card size="small" title="基金数量">
            <n-statistic :value="overview.stats?.fund_count || funds.length" />
          </n-card>
        </n-gi>
        <n-gi :span="6">
          <n-card size="small" title="系统健康度">
            <n-statistic :value="overview.stats?.system_health || 0" suffix="%" />
          </n-card>
        </n-gi>
        <n-gi :span="6">
          <n-card size="small" title="美元/人民币">
            <n-statistic :value="overview.rates?.usd_cny_mid || '-'" />
          </n-card>
        </n-gi>
        <n-gi :span="6">
          <n-card size="small" title="港币/人民币">
            <n-statistic :value="overview.rates?.hkd_cny_mid || '-'" />
          </n-card>
        </n-gi>
      </n-grid>

      <n-card size="small" title="活跃数据源">
        <n-space v-if="activeSources.length" :size="8">
          <n-tag v-for="source in activeSources" :key="source" type="success" round>{{ source }}</n-tag>
        </n-space>
        <n-empty v-else description="暂无活跃数据源" />
      </n-card>

      <n-card size="small" title="基金配置">
        <n-data-table
          size="small"
          :columns="fundColumns"
          :data="funds"
          :loading="loading"
          :pagination="pagination"
          :scroll-x="900"
        />
      </n-card>

      <n-card size="small" title="最近系统状态">
        <n-list v-if="milestones.length" size="small" bordered>
          <n-list-item v-for="(item, index) in milestones" :key="index">
            <n-space align="center">
              <n-tag :type="tagType(item.level)" size="small">{{ item.level }}</n-tag>
              <n-text depth="3">{{ item.time }}</n-text>
              <span>{{ item.message }}</span>
            </n-space>
          </n-list-item>
        </n-list>
        <n-empty v-else description="暂无状态记录" />
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { computed, h, onMounted, ref } from 'vue'
import axios from 'axios'
import {
  NButton, NCard, NDataTable, NEmpty, NGi, NGrid, NList, NListItem,
  NPageHeader, NSpace, NStatistic, NTag, NText, useMessage
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const loading = ref(false)
const overview = ref<any>({ rates: {}, stats: {}, active_sources: [] })
const funds = ref<any[]>([])
const milestones = ref<any[]>([])

const activeSources = computed(() => overview.value.active_sources || [])
const pagination = { pageSize: 10 }

const fundColumns: DataTableColumns<any> = [
  { title: '代码', key: 'fund_code', width: 110, fixed: 'left' },
  { title: '名称', key: 'fund_name', width: 160 },
  { title: '分组', key: 'category', width: 120, render: row => h(NTag, { size: 'small' }, { default: () => row.category || '-' }) },
  { title: '指数', key: 'idx_name', width: 160, render: row => row.idx_name || '-' },
  { title: '指数代码', key: 'idx_code', width: 120, render: row => row.idx_code || '-' },
  { title: '申购费率', key: 'purchase_fee', width: 110, render: row => row.purchase_fee || '-' },
  { title: '赎回费率', key: 'redemption_fee', width: 110, render: row => row.redemption_fee || '-' }
]

const tagType = (level: string) => {
  if (level === 'ERROR') return 'error'
  if (level === 'WARNING') return 'warning'
  if (level === 'SUCCESS') return 'success'
  return 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    const [overviewRes, fundsRes, milestoneRes] = await Promise.all([
      axios.get('/api/market/overview'),
      axios.get('/api/config/funds'),
      axios.get('/api/system/milestones')
    ])
    overview.value = overviewRes.data?.data || { rates: {}, stats: {}, active_sources: [] }
    funds.value = fundsRes.data?.data || []
    milestones.value = milestoneRes.data?.data || []
  } catch (error: any) {
    message.error(`数据管理加载失败：${error.message}`)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page { min-height: 100%; }
</style>
