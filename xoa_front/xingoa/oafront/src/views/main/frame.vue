<script setup name="Frame">
import { ref, computed } from 'vue'
import { Expand, Fold } from '@element-plus/icons-vue'
import {useAuthStore} from '@/stores/auth'

const auth = useAuthStore()
console.log("嘿嘿", auth.token)

let isCollapse = ref(false)

let asideWidth = computed(() => {
  if (isCollapse.value) {
    return '64px'
  } else {
    return '230px'
  }
})

</script>

<template>
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
        :collapse-transition="false">
        <el-menu-item index="1">
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
          <el-menu-item index="2-1">
            <el-icon>
              <User />
            </el-icon>
            <span>个人考勤</span>
          </el-menu-item>
          <el-menu-item index="2-2">
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
          <el-menu-item index="3-1">
            <el-icon>
              <Edit />
            </el-icon>
            <span>发布通知</span>
          </el-menu-item>
          <el-menu-item index="3-2">
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
              <span style="margin-left: 5px;">用户</span>
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item>设置</el-dropdown-item>
                <el-dropdown-item>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <!-- 主体 -->
      <el-main class="main">Main</el-main>
    </el-container>
  </el-container>
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
