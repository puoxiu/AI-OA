<script setup name="MyAbsent">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import ai1Http from '@/api/ai1Http'
import { ElMessage } from 'element-plus'
// 自定义组件
import OAMain from '@/components/OAMain.vue'
import OADialog from '@/components/OADialog.vue'

const dialogFormVisible = ref(false)
const dialogDeleteVisible = ref(false)


const onShowDialog = () => {
  sessionForm.title = ''
  sessionForm.last_message = '你现在是一名可靠的AI助手'
  dialogFormVisible.value = true
}


let formLabelWidth = '120px'
let sessionForm = reactive({
  title: '',
  last_message: '你现在是一名可靠的AI助手'
})
let rules = reactive({
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  last_message: [],
})
let sessionFormRef = ref(null)


const onSubmitSession = () => {
  sessionFormRef.value.validate(async (valid, fields) => {
    if (valid) {
      let data = {
        title: sessionForm.title,
        last_message: sessionForm.last_message,
      }
      console.log("提交数据：", data)
      try {
        let session = await ai1Http.addSession(data)
        ElMessage.success(session.data.msg)
        dialogFormVisible.value = false
        // 刷新列表
        sessions.value.unshift(session.data.data)
      } catch (error) {
        ElMessage.error(error.msg)
      }

    } else {
      ElMessage.error('请完善必填项')
    }
  })
}


let sessions = ref([])


onMounted(async () => {
  try {
    let session_data = await ai1Http.getSessionList()
    console.log("获取会话列表：", session_data.data.data.sessions)
    sessions.value = session_data.data.data.sessions
  } catch (error) {
    ElMessage.error(error.msg || '获取会话列表失败')
  }
})


// 删除会话
const deleteSessionId = ref('');

const onShowDeleteDialog = (row) => {
  console.log("删除的会话索引：", row)
  deleteSessionId.value = row.session_id
  dialogDeleteVisible.value = true;
}
const onDeleteSession = async () => {
  try {
    const deleteIndex = sessions.value.findIndex(
      (session) => session.session_id === deleteSessionId.value
    );
    if (deleteIndex === -1) {
      ElMessage.warning("未找到该会话，可能已被删除");
      dialogDeleteVisible.value = false;
      return;
    }
    await ai1Http.deleteSession(deleteSessionId.value); // 参数为 session_id
    sessions.value.splice(deleteIndex, 1);
    dialogDeleteVisible.value = false;
    ElMessage.success("会话删除成功！")
  } catch (err) {
    ElMessage.error(err.msg || '会话删除失败')
  }
}


</script>

<template>
  <OAMain title="所有会话">
    <el-card style="text-align: right;">
      <el-button type="primary" @click="onShowDialog">
        <el-icon>
          <Plus />
        </el-icon>
        新增
      </el-button>
    </el-card>

    <el-card>
      <el-table :data="sessions" style="width: 100%">
        <el-table-column label="标题">
          <template #default="scope">
            <RouterLink :to="{ name: 'chatting_room', params: { session_id: scope.row.session_id } }">{{ scope.row.title
            }}</RouterLink>
          </template>
        </el-table-column>

        <el-table-column prop="session_id" label="会话ID" />
        <el-table-column prop="last_message" label="最后消息" />
        <el-table-column prop="last_timestamp" label="最后消息时间" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button @click="onShowDeleteDialog(scope.row)" type="danger" icon="Delete" />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </OAMain>

  <OADialog title="新的会话" v-model="dialogFormVisible" @submit="onSubmitSession">
    <el-form :model="sessionForm" :rules="rules" ref="sessionFormRef">
      <el-form-item label="标题" :label-width="formLabelWidth" prop="title">
        <el-input v-model="sessionForm.title" placeholder="请输入会话标题（如：工作助手、学习问答）" autocomplete="off"
          maxLength="50"></el-input>
      </el-form-item>

      <el-form-item label="角色提示" :label-width="formLabelWidth" prop="last_message">
        <el-input v-model="sessionForm.last_message" disabled style="background: #f5f7fa;"
          placeholder="AI助手的角色描述"></el-input>
        <div style="margin-top: 8px; color: #999; font-size: 12px;">
          提示：该角色描述为系统默认设置，无需手动修改
        </div>
      </el-form-item>
    </el-form>
  </OADialog>
  <OADialog v-model="dialogDeleteVisible" title="提示" @submit="onDeleteSession">
    <span>您确定要删除这会话吗？</span>
  </OADialog>
</template>

<style scoped>
.el-card+.el-card {
  margin-top: 16px;
}
</style>
