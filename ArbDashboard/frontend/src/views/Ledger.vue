<template>
  <div class="page">
    <n-space vertical :size="12">
      <n-page-header title="实盘对账" subtitle="查看当前交易台账与历史闭环记录">
        <template #extra>
          <n-space>
            <n-select v-model:value="status" size="small" style="width: 130px" :options="statusOptions" @update:value="fetchTrades" />
            <n-button size="small" :loading="loading" @click="fetchTrades">刷新</n-button>
          </n-space>
        </template>
      </n-page-header>

      <n-card size="small">
        <n-data-table
          size="small"
          :columns="columns"
          :data="trades"
          :loading="loading"
          :pagination="{ pageSize: 12 }"
          :scroll-x="1100"
        />
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import axios from 'axios'
import { NButton, NCard, NDataTable, NPageHeader, NSelect, NSpace, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const loading = ref(false)
const status = ref('ACTIVE')
const trades = ref<any[]>([])

const statusOptions = [
  { label: '进行中', value: 'ACTIVE' },
  { label: '已关闭', value: 'CLOSED' },
  { label: '全部', value: 'ALL' }
]

const columns: DataTableColumns<any> = [
  { title: 'ID', key: 'id', width: 80, fixed: 'left' },
  { title: '代码', key: 'fund_code', width: 110, render: row => row.fund_code || row.code || '-' },
  { title: '名称', key: 'fund_name', width: 150, render: row => row.fund_name || row.name || '-' },
  { title: '方向', key: 'direction', width: 100, render: row => h(NTag, { size: 'small', type: row.direction === 'SELL' ? 'error' : 'success' }, { default: () => row.direction || row.side || '-' }) },
  { title: '数量', key: 'volume', width: 110, render: row => row.volume ?? row.qty ?? '-' },
  { title: '价格', key: 'price', width: 110, render: row => row.price ?? '-' },
  { title: '状态', key: 'status', width: 110, render: row => h(NTag, { size: 'small', type: row.status === 'CLOSED' ? 'default' : 'info' }, { default: () => row.status || '-' }) },
  { title: '开仓时间', key: 'open_time', width: 180, render: row => row.open_time || row.created_at || '-' },
  { title: '平仓时间', key: 'close_time', width: 180, render: row => row.close_time || '-' },
  { title: '备注', key: 'remark', minWidth: 180, ellipsis: { tooltip: true }, render: row => row.remark || '-' }
]

const fetchTrades = async () => {
  loading.value = true
  try {
    const params = status.value === 'ALL' ? {} : { status: status.value }
    const res = await axios.get('/api/ledger/trades', { params })
    trades.value = res.data?.data || []
  } catch (error: any) {
    message.error(`台账加载失败：${error.message}`)
  } finally {
    loading.value = false
  }
}

onMounted(fetchTrades)
</script>

<style scoped>
.page { min-height: 100%; }
</style>
