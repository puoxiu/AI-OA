<script setup name="InformList">
import { ref, reactive, onMounted } from "vue"
import OAMain from "@/components/OAMain.vue";
import OADialog from "@/components/OADialog.vue";
import OAPagination from "@/components/OAPagination.vue";
// import timeFormatter from "@/utils/timeFormatter"
import { useAuthStore } from "@/stores/auth";
import informHttp from "@/api/informHttp";
import { ElMessage } from "element-plus";

const authStore = useAuthStore()

let informs = ref([])
let pagination = reactive({
    page: 1,
    total: 0
})
let dialogVisible = ref(false)
let handleIndex = 0

onMounted(async () => {
    try {
        let data = await informHttp.getInformList()
        console.log(data); 
        informs.value = data.data.data
        console.log("通知列表：", data.data.data)
    } catch (detail) {
        ElMessage.error(detail)
    }
})


const onShowDialog = (index) => {
    handleIndex = index
    dialogVisible.value = true;
}

const onDeleteInform = async () => {
    try {
        let inform = informs.value[handleIndex]
        // console.log("删除的通知：", inform)
        await informHttp.deleteInform(inform.id)
        informs.value.splice(handleIndex, 1)
        dialogVisible.value = false;
        ElMessage.success("通知删除成功！")
    } catch (err) {
      console.log("删除通知失败：", err)
        ElMessage.error(err.msg)
    }
}

</script>

<template>
    <OADialog v-model="dialogVisible" title="提示" @submit="onDeleteInform">
        <span>您确定要删除这篇通知吗？</span>
    </OADialog>
    <OAMain title="通知列表">
        <el-card>
            <el-table :data="informs">
                <el-table-column label="标题">
                    <template #default="scope">
                        <el-badge v-if="!scope.row.is_read" is-dot class="item">
                        </el-badge>
                        <RouterLink :to="{ name: 'informdetail', params: { inform_id: scope.row.id } }">{{ scope.row.title }}</RouterLink>
                    </template>
                </el-table-column>
                <el-table-column label="发布者">
                    <template #default="scope">
                        {{ '[' + scope.row.author_department_name + ']' + scope.row.author_name }}
                    </template>
                </el-table-column>
                <el-table-column label="发布时间">
                    <template #default="scope">
                        {{scope.row.create_time}}
                    </template>
                </el-table-column>
                <el-table-column label="部门可见">
                    <template #default="scope">
                        <el-tag v-if="scope.row.is_public" type="success">公开</el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作">
                    <template #default="scope">
                        <el-button v-if="scope.row.author_id == authStore.user.id" @click="onShowDialog(scope.$index)"
                            type="danger" icon="Delete" />
                        <el-button v-else disabled type="default">无</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <template #footer>
                <!-- <OAPagination v-model="pagination.page" :total="pagination.total"></OAPagination> -->
            </template>
        </el-card>
    </OAMain>
</template>

<style scoped>
.el-badge{
    margin-right: 4px;
    margin-top: 4px;
}
</style>
