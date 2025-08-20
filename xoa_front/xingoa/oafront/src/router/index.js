import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/login/login.vue'
import Frame from '../views/main/frame.vue'
import { useAuthStore } from '@/stores/auth'
import MyAbsent from '../views/absent/my.vue'
import SubAbsent from '../views/absent/sub.vue'
import InformList from '../views/inform/list.vue'
import InformPublish from '../views/inform/publish.vue'
import InformDetail from '../views/inform/detail.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'frame',
      component: Frame,
      children: [
        {path: '/absent/my', name: 'myabsent', component: MyAbsent},
        {path: '/absent/sub',name: 'subabsent',component: SubAbsent},
        {path: '/inform/list',name: 'informlist',component: InformList},
        {path: '/inform/publish',name: 'informpublish',component: InformPublish},
        {path: '/inform/:inform_id',name: 'informdetail',component: InformDetail},
      ]
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
