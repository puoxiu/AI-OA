import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'

const app = createApp(App)
app.use(router) // 使用路由
app.mount('#app') // 挂载到 index.html 中的 #app
