import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 定义一个常量，用于存储 token 的 key
const TOKEN_KEY = 'OA_TOKEN'

export const useAuthStore = defineStore('auth', () => {
    // 存储到对象中（内存中）
  let _token = ref('')

  // 存储到 localStorage 中(硬盘)
  function setToken(token) {
    _token.value = token
    localStorage.setItem(TOKEN_KEY, token)
  }

  let token = computed(() => {
    if(!_token.value) {
      _token.value = localStorage.getItem(TOKEN_KEY)
    }
    return _token.value
  })
  // 暴露方法
  return { setToken, token }
})
