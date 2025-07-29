<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo 图片 -->
      <div class="logo-container">
        <img src="../assets/images/OA1.png" alt="系统Logo" class="logo"/>
      </div>
      
      <h2 class="login-title">员工登录</h2>
      <p class="login-subtitle">请登录您的账号继续使用系统</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label" for="username">邮箱</label>
          <div class="input-wrapper">
            <i class="icon-user"></i>
            <input 
              v-model="loginForm.username" 
              id="username" 
              type="text" 
              required 
              placeholder="请输入邮箱"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label" for="password">密码</label>
          <div class="input-wrapper">
            <i class="icon-lock"></i>
            <input 
              v-model="loginForm.password" 
              id="password" 
              type="password" 
              required 
              placeholder="请输入密码"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="form-actions">
          <a href="/forgot-password" class="forgot-link">忘记密码?</a>
        </div>
        
        <button type="submit" class="login-button">
          <span>登录</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { reactive } from 'vue'
import axios from 'axios'

// 处理登录表单提交
let loginForm = reactive({
  username: '',
  password: ''
})

const router = useRouter()

// 处理登录逻辑
const handleLogin = () => {
  // 进行数据格式校验：email格式、密码长度
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(loginForm.username)) {
    alert('请输入正确的邮箱格式')
    return
  }
  if (loginForm.password.length < 6 || loginForm.password.length > 20) {
    alert('密码长度必须在6位到20位之间')
    return
  }

  // 发送后端请求--axios
  axios.post('http://localhost:8003/api/v1/auth/login', loginForm)
    .then(response => {
      // 登录成功处理
      console.log('登录成功', response.data)
      router.push('/home') // 跳转到首页
    })
    .catch(error => {
      // 登录失败处理
      console.error('登录失败', error)
      alert('登录失败，请检查邮箱和密码')
    })
}

</script>

<style scoped>
/* 基础样式 */
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f0ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 40px 30px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

/* Logo样式 */
.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.logo {
  height: 60px;
  width: auto;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

/* 标题样式 */
.login-title {
  text-align: center;
  color: #1d2129;
  font-size: 26px;
  font-weight: 600;
  margin: 0 0 10px 0;
}

.login-subtitle {
  text-align: center;
  color: #86909c;
  font-size: 14px;
  margin: 0 0 30px 0;
}

/* 表单样式 */
.login-form {
  width: 100%;
}

.form-group {
  margin-bottom: 22px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: #4e5969;
  font-size: 14px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
}

.icon-user, .icon-lock {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #86909c;
  font-size: 16px;
}

/* 使用伪元素模拟图标，实际项目中可替换为iconfont */
.icon-user::before {
  content: "👤";
}

.icon-lock::before {
  content: "🔒";
}

.form-input {
  width: 100%;
  padding: 14px 14px 14px 44px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  font-size: 15px;
  color: #1d2129;
  background-color: #f7f8fa;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #86909c;
}

.form-input:focus {
  outline: none;
  border-color: #4096ff;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(64, 150, 255, 0.1);
}

/* 表单操作区 */
.form-actions {
  text-align: right;
  margin-bottom: 25px;
}

.forgot-link {
  color: #4096ff;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.2s ease;
}

.forgot-link:hover {
  color: #1677ff;
  text-decoration: underline;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  padding: 14px;
  background-color: #4096ff;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover {
  background-color: #1677ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.3);
}

.login-button:active {
  transform: translateY(0);
}


.register-link {
  color: #4096ff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.register-link:hover {
  color: #1677ff;
  text-decoration: underline;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-container {
  animation: fadeIn 0.5s ease forwards;
}

.form-group {
  animation: fadeIn 0.5s ease forwards;
  opacity: 0;
}

.form-group:nth-child(1) { animation-delay: 0.1s; }
.form-group:nth-child(2) { animation-delay: 0.2s; }
</style>