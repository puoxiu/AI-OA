<!-- 封装页面头部组件 -->
<script setup name="OAPageHeader">

import { useRouter } from 'vue-router'
import { defineProps } from 'vue'

const router = useRouter()

const goBack = () => {
    router.go(-1)
}

let props = defineProps({
    content: {
        type: String,
        default: ""
    }
})
</script>

<template>
    <el-page-header @back="goBack" title="返回">
        <template #content>
            <span>{{ content }}</span>
        </template>
    </el-page-header>
</template>

<style scoped>
</style>
