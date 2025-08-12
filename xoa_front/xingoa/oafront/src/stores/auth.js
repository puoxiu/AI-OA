import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 定义一个常量，用于存储 token 的 key
const TOKEN_KEY = 'OA_TOKEN'
const USER_KEY = 'OA_USER'

export const useAuthStore = defineStore('auth', () => {
    // 存储到对象中（内存中）
  let _token = ref('')
  let _user = ref({})

  // 存储到 localStorage 中(硬盘)
  function setUserToken(user, token) {
    _user.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    _token.value = token
    localStorage.setItem(TOKEN_KEY, token)
  }

  // 退出登录
  function logout() {
    _user.value = {}
    localStorage.removeItem(USER_KEY)
    _token.value = ''
    localStorage.removeItem(TOKEN_KEY)
  }

  let user = computed(() => {
    if(Object.keys(_user.value).length === 0) {
      let user = localStorage.getItem(USER_KEY)
      if(user) {
        _user.value = JSON.parse(user)
      }
    }
    return _user.value
  })

  let token = computed(() => {
    if(!_token.value) {
      let token = localStorage.getItem(TOKEN_KEY)
      if(token) {
        _token.value = token
      }
    }
    return _token.value
  })

  // 判断是否登录
  let isLogin = computed(() => {
    return token.value !== ''
  })

  // 暴露方法
  return { setUserToken, logout, token, user, isLogin }
})
