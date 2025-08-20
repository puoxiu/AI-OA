<script setup name="InformDetail">
import informHttp from "@/api/informHttp";
import { ref, reactive, onMounted } from "vue"
import { ElMessage } from "element-plus"
import OAMain from "@/components/OAMain.vue"
import OAPagination from "@/components/OAPagination.vue"
import OADialog from "@/components/OADialog.vue";
import { useRoute } from "vue-router";

const route = useRoute()

let inform = reactive({
    title: "",
    content: "",
    create_time: "",
    author: {
        realname: "",
        department: {
            name: ""
        }
    }
})

onMounted(async () => {
    console.log(route.params)
    const inform_id = route.params.inform_id
    console.log("第：", inform_id)
    try{
        let data = await informHttp.getInformDetail(inform_id)
        // console.log("通知详情：", data)
        Object.assign(inform, data.data.data)
    }catch(err){
        ElMessage.error(err.msg)
    }

    // 发送阅读请求
    // await informHttp.readInform(inform_id)
})

</script>
<template>
  <OAMain title="通知详情">
    <el-card>
      <template #header>
        <div style="text-align: center;">
          <h2 class="title">{{ inform.title }}</h2>
          <div class="meta">
            <span class="label">作者：</span>
            <span class="value author">{{ inform.author.username }}</span>
            <span class="label" style="margin-left: 20px;">发布时间：</span>
            <span class="value time">{{ inform.create_time }}</span>
          </div>
        </div>
      </template>
      <template #default>
        <div v-html="inform.content" class="content"></div>
      </template>
    </el-card>
  </OAMain>
</template>

<style scoped>
.title {
  padding-bottom: 20px;
  font-size: 22px;
  font-weight: bold;
  color: #333;
}

.meta {
  font-size: 14px;
}

.label {
  color: #888; /* 字段名灰色 */
}

.value {
  font-weight: 500;
}

.value.author {
  color: #2a4e9e; /* 作者蓝色 */
}

.value.time {
  color: #67c23a; /* 时间绿色 */
}

.content {
  margin-top: 20px;
  line-height: 1.8;
  font-size: 15px;
  color: #444;
}
</style>