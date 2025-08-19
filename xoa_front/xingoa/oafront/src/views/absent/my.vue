<script setup name="MyAbsent">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import absentHttp from '@/api/absentHttp'
import OAPagination from '@/components/OAPagination.vue'
import { ElMessage } from 'element-plus'
// 自定义组件
import OAMain from '@/components/OAMain.vue'
import OADialog from '@/components/OADialog.vue'

const dialogFormVisible = ref(false)

const onShowDialog = () => {
    absentForm.date_range = []
    absentForm.absent_type_id = null
    absentForm.reason = ''
    absentForm.title = ''
    dialogFormVisible.value = true
}

let formLabelWidth = '100px'
let absentForm = reactive({
    title: '',
    absent_type_id: null,
    date_range: [],
    reason: ''
})
let rules = reactive({
    title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
    absent_type_id: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
    date_range: [{ required: true, message: '请选择请假日期', trigger: 'blur' }],
    reason: [{ required: true, message: '请输入请假理由', trigger: 'blur' }],
})
let absentFormRef = ref(null)

let absent_types = ref([])
let absent_responder = reactive({
    email: '',
    username: '',
})


const onSubmitAbsent = () => {
    absentFormRef.value.validate(async (valid, fields) => {
        if (valid) {
            let data = {
                title: absentForm.title,
                absent_type_id: absentForm.absent_type_id,
                start_date: absentForm.date_range[0],
                end_date: absentForm.date_range[1],
                request_content: absentForm.reason,
            }
            console.log("提交数据：", data)
            try {
                let absent = await absentHttp.addAbsent(data)
                ElMessage.success(absent.data.msg)
                dialogFormVisible.value = false
                // 刷新列表
                absents.value.unshift(absent.data.data)
            } catch (error) {
                ElMessage.error(error.msg)
            }
            // 
        } else {
            ElMessage.error('提交失败')
        }
    })
}

let absent_responder_str = computed(() => {
    if (absent_responder.email && absent_responder.username) {
        return absent_responder.username + ' [' + absent_responder.email + ']'
    }
    return '无'
})

let absents = ref([])
// 分页
let pagination = reactive({
    currentPage: 1,
    total: 0,
})

// 监听
watch(() => pagination.currentPage, async (newVal, oldVal) => {
    try {
        let absent_data = await absentHttp.getMyAbsents(newVal)
        absents.value = absent_data.data.data.items
        pagination.total = absent_data.data.data.total
    } catch (err) {
        ElMessage.error(err.msg)
    }
})

onMounted(async () => {
    try {
        // 1、获取请假类型列表
        let absent_typed_data = await absentHttp.getAbsentTypes()
        absent_types.value = absent_typed_data.data.data
        console.log("获取类型：", absent_typed_data.data.data)
        // 2、获取审批者
        let responder_data = await absentHttp.getResponder()
        Object.assign(absent_responder, responder_data.data.data)
        console.log("获取审批者：", absent_responder)

        // 3、获取历史请假列表
        let absent_data = await absentHttp.getMyAbsents(pagination.currentPage)
        absents.value = absent_data.data.data.items
        pagination.total = absent_data.data.data.total
        console.log("分页：", pagination)
        console.log("获取请假返回：", absent_data.data.data)
    } catch (error) {
        ElMessage.error(error.msg)
    }
})

</script>

<template>
    <OAMain title="个人考勤">
        <el-card style="text-align: right;">
            <el-button type="primary" @click="onShowDialog">
                <el-icon>
                    <Plus />
                </el-icon>
                新增
            </el-button>
        </el-card>
        <el-card>
            <el-table :data="absents" style="width: 100%">
                <el-table-column prop="title" label="标题" />
                <el-table-column prop="absent_type_id" label="请假类型" />
                <el-table-column prop="start_date" label="开始日期" />
                <el-table-column prop="end_date" label="结束日期" />
                <el-table-column prop="request_content" label="请假理由" />
                <el-table-column prop="create_time" label="创建时间" />
                <el-table-column label="审核领导">{{ absent_responder_str }}</el-table-column>
                <el-table-column prop="status" label="当前状态">
                    <template #default="scope">
                        <!-- 1-待审批，2-通过，3-拒绝 -->
                        <el-tag :type="scope.row.status === 1 ? 'warning' :
                            scope.row.status === 2 ? 'success' : 'danger'">{{scope.row.status === 1 ? '待审批' : scope.row.status === 2 ? '已通过' :'已拒绝'}}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column prop="response_content" label="审核意见">
                    <template #default="scope">
                        {{ scope.row.response_content}}
                    </template>
                </el-table-column>

            </el-table>
            <template #footer>
                <!-- <el-pagination background layout="prev, pager, next" :total="pagination.total" :page-size="10"
                    v-model:current-page="pagination.currentPage" /> -->
                <OAPagination :total="pagination.total" :page-size="10" v-model="pagination.currentPage" />
            </template>
        </el-card>
    </OAMain>

    <OADialog title="发起请假" v-model="dialogFormVisible" @submit="onSubmitAbsent">
        <el-form :model="absentForm" :rules="rules" ref="absentFormRef">
            <el-form-item label="标题" :label-width="formLabelWidth" prop="title">
                <el-input v-model="absentForm.title" autocomplete="off"></el-input>
            </el-form-item>
            <el-form-item label="请假类型" :label-width="formLabelWidth" prop="absent_type_id">
                <el-select v-model="absentForm.absent_type_id" placeholder="请选择请假类型">
                    <el-option v-for="item in absent_types" :key="item.name" :label="item.name"
                        :value="item.id"></el-option>
                </el-select>
            </el-form-item>
            <el-form-item label="请假日期" :label-width="formLabelWidth" prop="date_range">
                <el-date-picker v-model="absentForm.date_range" type="daterange" range-separator="至"
                    start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="请假理由" :label-width="formLabelWidth" prop="reason">
                <el-input v-model="absentForm.reason" autocomplete="off" type="textarea"></el-input>
            </el-form-item>
            <el-form-item label="审批人" :label-width="formLabelWidth">
                <el-input :value="absent_responder_str" readonly disabled autocomplete="off"></el-input>
            </el-form-item>
        </el-form>
    </OADialog>
</template>

<style scoped>
.el-pagination {
    justify-content: center;
}
</style>
