import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'
import AutoTrade from '../views/AutoTrade.vue'
import Data from '../views/Data.vue'
import Ledger from '../views/Ledger.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'analysis',
          name: 'Analysis',
          component: Analysis
        },
        {
          path: 'auto-trade',
          name: 'AutoTrade',
          component: AutoTrade
        },
        {
          path: 'data',
          name: 'Data',
          component: Data
        },
        {
          path: 'ledger',
          name: 'Ledger',
          component: Ledger
        },
        {
          path: 'settings',
          name: 'Settings',
          component: Settings
        }
      ]
    }
  ]
})

export default router
