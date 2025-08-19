<script setup>
import OAPageHeader from '@/components/OAPageHeader.vue'
import {defineProps} from 'vue'

const props = defineProps({
    title: {
        type: String,
        default: ""
    }
})

</script>

<template>
    <el-space direction="vertical" fill style="width: 100%;">
        <OAPageHeader :content="props.title" />
        <slot></slot>
    </el-space>
</template>



<style scoped>
/* 解决tab之后表格显示问题 */
.el-space :deep(.el-space__item) {
    width: 100%;
}
</style>
