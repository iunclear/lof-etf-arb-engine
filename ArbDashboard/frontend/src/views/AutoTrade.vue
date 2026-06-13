<template>
  <div class="page">
    <n-space vertical :size="12">
      <n-page-header title="信号监控" subtitle="查看自动交易引擎状态、规则与最近日志">
        <template #extra>
          <n-space>
            <n-tag :type="running ? 'success' : 'warning'">{{ running ? '运行中' : '已暂停' }}</n-tag>
            <n-button size="small" :loading="loading" @click="fetchData">刷新</n-button>
            <n-button size="small" :type="running ? 'warning' : 'primary'" :loading="toggling" @click="toggleEngine">
              {{ running ? '停止引擎' : '启动引擎' }}
            </n-button>
          </n-space>
        </template>
      </n-page-header>

      <n-grid :cols="24" :x-gap="12" :y-gap="12">
        <n-gi :span="8">
          <n-card size="small" title="引擎状态">
            <n-statistic :value="running ? '运行中' : '已暂停'" />
          </n-card>
        </n-gi>
        <n-gi :span="8">
          <n-card size="small" title="规则数量">
            <n-statistic :value="rules.length" />
          </n-card>
        </n-gi>
        <n-gi :span="8">
          <n-card size="small" title="日志条数">
            <n-statistic :value="logs.length" />
          </n-card>
        </n-gi>
      </n-grid>

      <n-card size="small" title="自动交易规则">
        <n-data-table
          size="small"
          :columns="ruleColumns"
          :data="rules"
          :loading="loading"
          :pagination="{ pageSize: 8 }"
          :scroll-x="900"
        />
      </n-card>

      <n-card size="small" title="最近日志">
        <n-list v-if="logs.length" size="small" bordered>
          <n-list-item v-for="(log, index) in logs" :key="index">
            <pre class="log-line">{{ formatLog(log) }}</pre>
          </n-list-item>
        </n-list>
        <n-empty v-else description="暂无日志" />
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import axios from 'axios'
import {
  NButton, NCard, NDataTable, NEmpty, NGi, NGrid, NList, NListItem,
  NPageHeader, NSpace, NStatistic, NTag, useMessage
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

const message = useMessage()
const loading = ref(false)
const toggling = ref(false)
const running = ref(false)
const rules = ref<any[]>([])
const logs = ref<any[]>([])

const ruleColumns: DataTableColumns<any> = [
  { title: 'ID', key: 'id', width: 120, fixed: 'left', render: row => row.id || row.rule_id || '-' },
  { title: '名称', key: 'name', width: 180, render: row => row.name || row.title || '-' },
  { title: '标的', key: 'symbol', width: 120, render: row => row.symbol || row.code || row.fund_code || '-' },
  { title: '启用', key: 'enabled', width: 100, render: row => h(NTag, { size: 'small', type: row.enabled === false ? 'default' : 'success' }, { default: () => row.enabled === false ? '否' : '是' }) },
  { title: '条件', key: 'condition', minWidth: 260, ellipsis: { tooltip: true }, render: row => row.condition || row.trigger || JSON.stringify(row) }
]

const formatLog = (log: any) => typeof log === 'string' ? log : JSON.stringify(log, null, 2)

const fetchData = async () => {
  loading.value = true
  try {
    const [statusRes, rulesRes, logsRes] = await Promise.all([
      axios.get('/api/auto_trade/status'),
      axios.get('/api/auto_trade/rules'),
      axios.get('/api/auto_trade/logs')
    ])
    running.value = Boolean(statusRes.data?.running)
    rules.value = rulesRes.data?.rules || []
    logs.value = logsRes.data?.logs || []
  } catch (error: any) {
    message.error(`信号监控加载失败：${error.message}`)
  } finally {
    loading.value = false
  }
}

const toggleEngine = async () => {
  toggling.value = true
  try {
    const action = running.value ? 'stop' : 'start'
    const res = await axios.post('/api/auto_trade/toggle', { action })
    if (res.data?.status === 'ok') {
      running.value = Boolean(res.data.running)
      message.success(running.value ? '自动交易引擎已启动' : '自动交易引擎已停止')
      fetchData()
    } else {
      message.error(res.data?.message || '引擎状态切换失败')
    }
  } catch (error: any) {
    message.error(`引擎状态切换失败：${error.message}`)
  } finally {
    toggling.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.page { min-height: 100%; }
.log-line { margin: 0; white-space: pre-wrap; font-family: Consolas, monospace; font-size: 12px; }
</style>
