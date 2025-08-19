<script setup name="subabsent">
import absentHttp from "@/api/absentHttp";
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import OAMain from "@/components/OAMain.vue"
import OAPagination from "@/components/OAPagination.vue"
import OADialog from "@/components/OADialog.vue";

let absents = ref([])
let pagination = reactive({
  total: 0,
  page: 1
})
let dialogVisible = ref(false)
let absentForm = reactive({
  status: 2,  // 2：通过，3：拒绝
  response_content: ""  // 处理理由
})
let rules = reactive({
  status: [{ required: true, message: '请选择处理结果！', trigger: 'change' }],
  response_content: [{ required: true, message: '请输入处理理由！', trigger: "blur" }]
})
let absentFormRef = ref()
let handleIndex = null

// 封装一个获取数据的方法
const fetchAbsents = async () => {
  try {
    const res = await absentHttp.getSubAbsents(pagination.page)
    pagination.total = res.data.data.total
    absents.value = res.data.data.items
    console.log("下属请假记录：", res)
  } catch (err) {
    ElMessage.error(err.msg || '获取下属请假记录失败')
  }
}

onMounted(fetchAbsents)

const onShowDialog = (index) => {
  absentForm.status = 2
  absentForm.response_content = ""
  dialogVisible.value = true
  handleIndex = index
}

const onSubmitAbsent = () => {
  absentFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const absent = absents.value[handleIndex]
        await absentHttp.handleSubAbsent(
          absent.id,
          absentForm.status,
          absentForm.response_content
        )
        ElMessage.success('下属考勤处理成功！')
        dialogVisible.value = false
        // ✅ 处理成功后刷新列表，防止数据不同步
        await fetchAbsents()
      } catch (err) {
        ElMessage.error(err.msg || '处理失败')
      }
    }
  })
}
</script>

<template>
  <OADialog title="处理考勤" v-model="dialogVisible" @submit="onSubmitAbsent">
    <el-form :model="absentForm" :rules="rules" ref="absentFormRef" label-width="100px">
      <el-form-item label="结果" prop="status">
        <el-radio-group v-model="absentForm.status" class="ml-4">
          <el-radio :value="2">通过</el-radio>
          <el-radio :value="3">拒绝</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="理由" prop="response_content">
        <el-input type="textarea" v-model="absentForm.response_content" autocomplete="off" />
      </el-form-item>
    </el-form>
  </OADialog>
  <OAMain title="下属考勤">
    <el-card>
      <el-table :data="absents">
        <el-table-column prop="title" label="标题" />
        <el-table-column label="发起者">
          <template #default="scope">
            {{ scope.row.initiator_name }}
          </template>
        </el-table-column>
        <el-table-column prop="absent_type_id" label="请假类型" />
        <el-table-column prop="start_date" label="开始日期" />
        <el-table-column prop="end_date" label="结束日期" />
        <el-table-column prop="request_content" label="请假理由" />
        <el-table-column prop="create_time" label="发起时间" />
        <el-table-column label="审核领导" />
        <el-table-column prop="response_content" label="反馈意见" />
        <el-table-column label="审核状态">
          <template #default="scope">
            <el-tag type="info" v-if="scope.row.status == 1">审核中</el-tag>
            <el-tag type="success" v-else-if="scope.row.status == 2">已通过</el-tag>
            <el-tag type="danger" v-else>已拒绝</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理">
          <template #default="scope">
            <el-button v-if="scope.row.status == 1" @click="onShowDialog(scope.$index)" type="primary" icon="EditPen" />
            <el-button v-else disabled type="default">已处理</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <OAPagination v-model="pagination.page" :total="pagination.total" @current-change="fetchAbsents"></OAPagination>
      </template>
    </el-card>
  </OAMain>
</template>

<style scoped>
.el-pagination {
  justify-content: center;
}
</style>
