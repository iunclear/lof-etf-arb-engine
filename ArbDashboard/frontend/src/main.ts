import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import axios from 'axios'
import 'vfonts/Inter.css'
import 'vfonts/FiraCode.css'

axios.defaults.timeout = 8000

const app = createApp(App)
app.use(router)
app.use(createPinia())
app.mount('#app')
