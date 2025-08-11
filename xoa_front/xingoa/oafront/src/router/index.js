import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/login/login.vue'
import Frame from '../views/main/frame.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'frame',
      component: Frame
    },
    {
      path: '/login',
      name: 'login',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: Login
    }
  ]
})


// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 1 登录页面不拦截
  const auth = useAuthStore()
  if(to.name === "login") {
    next()
    return
  }

  // 2 其他页面拦截
  if(auth.isLogin) {
    next()
  }else {
    next({ name: "login" })
  }
})

export default router
