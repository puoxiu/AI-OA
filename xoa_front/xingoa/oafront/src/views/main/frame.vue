<script setup name="Frame">
import { ref, computed, reactive } from 'vue'
import { Expand, Fold } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import authHttp from '@/api/authHttp'


const auth = useAuthStore()
const router = useRouter()
// console.log("嘿嘿", auth.user )

let isCollapse = ref(false)

let asideWidth = computed(() => {
  if (isCollapse.value) {
    return '64px'
  } else {
    return '230px'
  }
})

// 退出登录
const logOut = () => {
  auth.logout()
  router.push({ name: "login" })
  ElMessage.success("退出登录成功")
}

// 修改密码
let dialogVisible = ref(false)
let resetPwdForm = reactive({
  verifyCode: '',
  pwd1: '',
  pwd2: '',
})
let resetPwdFormLabelWidth = "80px"
const onControlResetPwdDialog = () => {
  resetPwdForm.verifyCode = ''
  resetPwdForm.pwd1 = ''
  resetPwdForm.pwd2 = ''
  dialogVisible.value = true
}

let resetPwdFormRef = ref()
const onSubmit =  () => {
  resetPwdFormRef.value.validate(async (valid) => {
    if (valid) {
      // 校验通过，执行提交操作
      console.log('校验通过，提交表单数据');
      try {
        await authHttp.resetPwd(resetPwdForm.verifyCode, resetPwdForm.pwd1, resetPwdForm.pwd2)
        ElMessage.success("修改密码成功")
        dialogVisible.value = false
      } catch (err) {
        console.log(err)
        ElMessage.error(err.msg)
      }
    } else {
      // 校验不通过，提示用户输入正确信息
      console.log('校验不通过，提示用户输入正确信息');
    }
  });
}

// 用户输入校验（不合格在前端提示)
const rules = reactive({
  verifyCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 6, message: '验证码长度至少6位', trigger: 'blur' },
  ],
  pwd1: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  pwd2: [
    { required: true, message: '请输入确认密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
})
</script>

<template>
  <!-- 主容器 -->
  <el-container class="container">
    <!-- 侧边栏 -->
    <el-aside class="sidebar" :width="asideWidth">
      <router-link to="/" class="sidebar-link">
        <el-icon>
          <HomeFilled />
        </el-icon>
        <span v-show="!isCollapse"><strong> 智能OA</strong></span>
      </router-link>
      <el-menu default-active="1" class="el-menu-vertical-demo" @open="handleOpen" @close="handleClose"
        background-color="#545c64" text-color="#fff" active-text-color="#ffd04b" :collapse="isCollapse"
        :collapse-transition="false" :router="true">
        <el-menu-item index="1" :route="{ name: 'home' }">
          <el-icon>
            <Position />
          </el-icon>
          <span>首页</span>
        </el-menu-item>
        <!-- <el-menu-item index="2" > -->
        <el-sub-menu index="2">
          <template v-slot:title>
            <el-icon>
              <EditPen />
            </el-icon>
            <span>考勤管理</span>
          </template>
          <el-menu-item index="2-1" :route="{ name: 'myabsent' }">
            <el-icon>
              <User />
            </el-icon>
            <span>个人考勤</span>
          </el-menu-item>
          <el-menu-item index="2-2" :route="{ name: 'subabsent' }">
            <el-icon>
              <User />
            </el-icon>
            <span>下属考勤</span>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="3">
          <template v-slot:title>
            <el-icon>
              <Notification />
            </el-icon>
            <span>通知管理</span>
          </template>
          <el-menu-item index="3-1" :route="{ name: 'informpublish' }">
            <el-icon>
              <Edit />
            </el-icon>
            <span>发布通知</span>
          </el-menu-item>
          <el-menu-item index="3-2" :route="{ name: 'informlist' }">
            <el-icon>
              <List />
            </el-icon>
            <span>通知列表</span>
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="4">
          <template v-slot:title>
            <el-icon>
              <User />
            </el-icon>
            <span>员工管理</span>
          </template>
          <el-menu-item index="4-1">
            <el-icon>
              <Plus />
            </el-icon>
            <span>添加员工</span>
          </el-menu-item>
          <el-menu-item index="4-2">
            <el-icon>
              <List />
            </el-icon>
            <span>员工列表</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="5">
          <el-icon>
            <Cpu />
          </el-icon>
          <span>AI助手</span>
        </el-menu-item>
      </el-menu>

    </el-aside>
    <!-- 内容区域 -->
    <el-container>
      <!-- 顶部 -->
      <el-header class="header">
        <div class="left-header">
          <el-button :icon="Expand" v-show="!isCollapse" @click="isCollapse = !isCollapse" />
          <el-button :icon="Fold" v-show="isCollapse" @click="isCollapse = !isCollapse" />
        </div>
        <div class="right-header">
          <el-dropdown>
            <span class="el-dropdown-link">
              <el-avatar :size="20" icon="UserFilled" />
              <span style="margin-left: 5px;">[{{ auth.user.email }} {{ auth.user.username }}]</span>
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item @click="onControlResetPwdDialog">修改密码</el-dropdown-item>
                <el-dropdown-item @click="logOut">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <!-- 主体 -->
      <el-main class="main">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>

  <!-- 弹窗 -->
  <el-dialog v-model="dialogVisible" title="修改密码" width="400px">
    <el-form :model="resetPwdForm" :rules="rules" ref="resetPwdFormRef">
      <el-form-item label="验证码" :label-width="formLabelWidth" prop="verifyCode">
        <el-input v-model="resetPwdForm.verifyCode" autocomplete="off" />
      </el-form-item>
      <el-form-item label="新密码" :label-width="resetPwdFormLabelWidth" prop="pwd1">
        <el-input v-model="resetPwdForm.pwd1" autocomplete="off" type="password" />
      </el-form-item>
      <el-form-item label="确认密码" :label-width="resetPwdFormLabelWidth" prop="pwd2">
        <el-input v-model="resetPwdForm.pwd2" autocomplete="off" type="password" />
      </el-form-item>

    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onSubmit">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.container {
  /* 高度占满全屏 */
  height: 100vh;
  color: #e2dbdb;
}

.sidebar {
  background-color: #433f3f;
}

.sidebar .sidebar-link {
  color: #fff;
  text-decoration: none;
  border-bottom: 1px solid #163958;
  background-color: #232631;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
}

.header {
  background-color: #dcd4d4;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
}

.header .left-header {
  display: flex;
  align-items: center;
}

.header .right-header {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  color: #000;
  display: flex;
  align-items: center;
}

.main {
  background-color: #fff;
  height: 100%;
}
</style>
