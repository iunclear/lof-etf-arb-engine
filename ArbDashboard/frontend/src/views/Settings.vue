<template>
  <div class="page">
    <n-space vertical :size="12">
      <n-page-header title="系统配置" subtitle="管理行情源状态、基金配置概览与连接维护">
        <template #extra>
          <n-space>
            <n-button size="small" :loading="loading" @click="fetchData">刷新</n-button>
            <n-button size="small" :loading="reconnectingEngine" @click="reconnectEngine">重启行情引擎</n-button>
            <n-button size="small" :loading="reconnectingIb" @click="reconnectIb">重连 IB</n-button>
          </n-space>
        </template>
      </n-page-header>

      <n-card size="small" title="数据源配置">
        <n-data-table
          size="small"
          :columns="sourceColumns"
          :data="sources"
          :loading="loading"
          :pagination="false"
          :scroll-x="760"
        />
      </n-card>

      <n-card size="small" title="基金配置概览">
        <n-data-table
          size="small"
          :columns="fundColumns"
          :data="funds"
          :loading="loading"
          :pagination="{ pageSize: 8 }"
          :scroll-x="760"
        />
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import axios from 'axios'
import {
  NButton, NCard, NDataTable, NPageHeader, NSpace, NSwitch, NTag, useMessage
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const loading = ref(false)
const reconnectingEngine = ref(false)
const reconnectingIb = ref(false)
const sources = ref<any[]>([])
const funds = ref<any[]>([])

const updateSource = async (row: any, isActive: boolean) => {
  const previous = row.is_active
  row.is_active = isActive
  try {
    const res = await axios.post('/api/config/data_sources/update', {
      module: row.module || 'realtime_market',
      source_name: row.source_name,
      priority: row.priority,
      is_active: isActive,
      config: row.config || {}
    })
    if (res.data?.status !== 'ok') throw new Error(res.data?.message || '保存失败')
    message.success('数据源配置已保存')
  } catch (error: any) {
    row.is_active = previous
    message.error(`保存失败：${error.message}`)
  }
}

const sourceColumns: DataTableColumns<any> = [
  { title: '名称', key: 'source_name', width: 160, fixed: 'left' },
  { title: '模块', key: 'module', width: 160, render: row => row.module || 'realtime_market' },
  { title: '优先级', key: 'priority', width: 100 },
  {
    title: '启用',
    key: 'is_active',
    width: 100,
    render: row => h(NSwitch, {
      value: Boolean(row.is_active),
      'onUpdate:value': (value: boolean) => updateSource(row, value)
    })
  },
  {
    title: '配置',
    key: 'config',
    minWidth: 260,
    ellipsis: { tooltip: true },
    render: row => JSON.stringify(row.config || {})
  }
]

const fundColumns: DataTableColumns<any> = [
  { title: '代码', key: 'fund_code', width: 110, fixed: 'left' },
  { title: '名称', key: 'fund_name', width: 160 },
  { title: '分组', key: 'category', width: 130, render: row => h(NTag, { size: 'small' }, { default: () => row.category || '-' }) },
  { title: '指数', key: 'idx_name', width: 180, render: row => row.idx_name || '-' },
  { title: '申购费率', key: 'purchase_fee', width: 120, render: row => row.purchase_fee || '-' }
]

const fetchData = async () => {
  loading.value = true
  try {
    const [sourceRes, fundRes] = await Promise.all([
      axios.get('/api/config/data_sources'),
      axios.get('/api/config/funds')
    ])
    sources.value = sourceRes.data?.data || []
    funds.value = fundRes.data?.data || []
  } catch (error: any) {
    message.error(`系统配置加载失败：${error.message}`)
  } finally {
    loading.value = false
  }
}

const reconnectEngine = async () => {
  reconnectingEngine.value = true
  try {
    const res = await axios.post('/api/system/reconnect_engine')
    if (res.data?.status === 'ok') {
      message.success('行情引擎已重启')
      fetchData()
    } else {
      message.error(res.data?.message || '行情引擎重启失败')
    }
  } catch (error: any) {
    message.error(`行情引擎重启失败：${error.message}`)
  } finally {
    reconnectingEngine.value = false
  }
}

const reconnectIb = async () => {
  reconnectingIb.value = true
  try {
    const res = await axios.post('/api/system/reconnect_ib')
    if (res.data?.status === 'ok') {
      message.success('IB 已重连')
    } else {
      message.warning(res.data?.message || 'IB 重连失败')
    }
  } catch (error: any) {
    message.error(`IB 重连失败：${error.message}`)
  } finally {
    reconnectingIb.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page { min-height: 100%; }
</style>
