// 引入 vue-router 创建路由对象
import { createRouter, createWebHashHistory } from 'vue-router'

// 引入你要配置的页面组件（我们下面会创建这些）
import LoginPage from '../views/LoginPage.vue'
import HomePage from '../views/HomePage.vue'

// 定义路由表，每个对象是一个页面路由
const routes = [
  {
    path: '/',             // 默认访问路径
    name: 'Login',
    component: LoginPage,  // 登录页面组件
  },
  {
    path: '/home',         // 登录成功后跳转到这里
    name: 'Home',
    component: HomePage,   // 主页组件
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(), // 使用 hash 模式，防止刷新页面 404
  routes,
})

export default router
