import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'

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
          component: Analysis
        },
        {
          path: 'data',
          name: 'Data',
          component: Dashboard
        },
        {
          path: 'ledger',
          name: 'Ledger',
          component: Analysis
        },
        {
          path: 'settings',
          name: 'Settings',
          component: Dashboard
        }
      ]
    }
  ]
})

export default router
