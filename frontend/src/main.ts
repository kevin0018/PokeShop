import './assets/main.css'
import './assets/pokemon-palette.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { i18n, syncLocale } from './i18n'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
syncLocale()

app.mount('#app')
