import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)
const vuetify = createVuetify() // Replaces new Vuetify()

app.use(vuetify).use(router)

app.mount('#app')

//createApp(App).mount('#app')


