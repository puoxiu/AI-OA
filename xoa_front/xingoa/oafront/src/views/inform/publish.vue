<script setup name="InformPublish">
import OAMain from '@/components/OAMain.vue';
import { ref, reactive, onBeforeUnmount, shallowRef, onMounted } from "vue"
import { ElMessage } from "element-plus"
import '@wangeditor/editor/dist/css/style.css' // 引入 css
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import staffHttp from '@/api/staffHttp'
import informHttp from '@/api/informHttp'

let informForm = reactive({
    title: '',
    content: '',
    department_ids: []
})
const rules = reactive({
    title: [{ required: true, message: "请输入标题！", trigger: 'blur' }],
    content: [{ required: true, message: "请输入内容！", trigger: 'blur' }],
    department_ids: [{ required: true, message: "请选择部门！", trigger: 'change' }]
})
let formRef = ref()
let formLabelWidth = "100px"
let departments = ref([])


////////////// 这是跟wangEditor相关的配置 //////////////
// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

const toolbarConfig = {}
const editorConfig = {
    placeholder: '请输入内容...',
    MENU_CONF: {

    }
}
// editorConfig.MENU_CONF['uploadImage']
let mode = "default"

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
    const editor = editorRef.value
    if (editor == null) return
    editor.destroy()
})

const handleCreated = (editor) => {
    editorRef.value = editor // 记录 editor 实例，重要！
}
////////////// 这是跟wangEditor相关的配置 //////////////

onMounted(async () => {
    try {
        let data = await staffHttp.getAllDepartment()
        // console.log(data);
        departments.value = data.data.data
    } catch (err) {
        console.log(err)
        ElMessage.error(err.msg)
    }
})

const onSubmit = () => {
    formRef.value.validate(async (valid, fields) => {
        if (valid) {
            console.log(informForm);
            try{
                let data = await informHttp.publishInform(informForm)
                console.log(data);
                ElMessage.success(data.data.msg)
            }catch(err){
                ElMessage.error(err.msg)
            }
        }
    })
}
</script>

<template>
    <OAMain title="发布通知">
        <el-card>
            <el-form :model="informForm" :rules="rules" ref="formRef">
                <el-form-item label="标题" :label-width="formLabelWidth" prop="title">
                    <el-input v-model="informForm.title" autocomplete="off" />
                </el-form-item>
                <el-form-item label="部门可见" :label-width="formLabelWidth" prop="department_ids">
                    <el-select multiple v-model="informForm.department_ids">
                        <el-option :value="0" label="所有部门"></el-option>
                        <el-option v-for="department in departments" :label="department.name" :value="department.id"
                            :key="department.name" />
                    </el-select>
                </el-form-item>
                <el-form-item label="内容" :label-width="formLabelWidth" prop="content">
                    <div style="border: 1px solid #ccc; width: 100%;">
                        <Toolbar style="border-bottom: 1px solid #ccc" :editor="editorRef"
                            :defaultConfig="toolbarConfig" :mode="mode" />
                        <Editor style="height: 500px; overflow-y: hidden;" v-model="informForm.content"
                            :defaultConfig="editorConfig" :mode="mode" @onCreated="handleCreated" />
                    </div>
                </el-form-item>
                <el-form-item>
                    <div style="text-align: right; flex: 1;">
                        <el-button type="primary" @click="onSubmit">提交</el-button>
                    </div>
                </el-form-item>
            </el-form>
        </el-card>
    </OAMain>
</template>

<style scoped>

</style>
