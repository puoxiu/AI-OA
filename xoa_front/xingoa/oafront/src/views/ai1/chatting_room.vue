<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, watch } from "vue"
import { useRoute } from "vue-router"
import ai1Http from "@/api/ai1Http"
import { ElMessage } from "element-plus"
import { useAuthStore } from "@/stores/auth"

const route = useRoute()
const authStore = useAuthStore()

// 当前会话 ID
const sessionId = ref(route.params.session_id)

// 聊天消息列表
const messages = ref([])

// 输入框
const inputText = ref("")

// 发送状态
const sending = ref(false)

// 滚动容器
const chatListRef = ref(null)

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatListRef.value) {
    // 使用 requestAnimationFrame 确保在浏览器下次重绘前执行，效果更佳
    requestAnimationFrame(() => {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    })
  }
}

// 格式化时间
const fmtTime = (ts) => {
  const d = new Date(ts * 1000)
  const pad = (n) => (n < 10 ? `0${n}` : n)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// 加载历史消息
const loadHistory = async () => {
  try {
    const res = await ai1Http.getSessionChatHistory(sessionId.value)
    messages.value = res.data.data.history || []
    // 数据更新后，等待DOM渲染完毕再滚动
    await scrollToBottom()
  } catch (e) {
    ElMessage.error(e.msg || "获取聊天历史失败")
  }
}

// 发送消息
let abortController = null
const send = async () => {
  if (!inputText.value.trim() || sending.value) return

  const content = inputText.value
  inputText.value = ""
  sending.value = true

  // 1. 添加用户消息并立即滚动
  const userMsg = { role: "user", content, timestamp: Math.floor(Date.now() / 1000) }
  messages.value.push(userMsg)
  await scrollToBottom()

  // 2. 添加AI消息占位并记录索引，也立即滚动
  const aiMessageIndex = messages.value.length
  messages.value.push({
    role: "assistant",
    content: "",
    timestamp: Math.floor(Date.now() / 1000)
  })
  await scrollToBottom()

  // 3. 准备发送的数据
  const requestData = {
    session_id: sessionId.value,
    message: content,
  }

  // 4. 使用aiHttp中的流式方法发送消息
  abortController = new AbortController()

  try {
    let receivedContent = ''
    await ai1Http.sendMessageStream(
      requestData,
      (data) => {
        // 实时更新AI消息内容，并累加
        receivedContent += data
        messages.value[aiMessageIndex].content = receivedContent
        // 每次收到新数据都滚动
        scrollToBottom()
      },
      (err) => {
        if (err.name !== "AbortError") {
          messages.value[aiMessageIndex].content = `发生错误: ${err.message || '未知错误'}`
          ElMessage.error(`发送失败: ${err.message || '未知错误'}`)
        }
      },
      () => {
        // 完成后更新时间戳
        sending.value = false
        messages.value[aiMessageIndex].timestamp = Math.floor(Date.now() / 1000)
        // 确保在完成时最终滚动一次
        scrollToBottom()
        abortController = null
      },
      abortController.signal
    )
  } catch (err) {
    if (err.name !== "AbortError") {
      ElMessage.error(`发送失败: ${err.message || '未知错误'}`)
    }
    sending.value = false
    abortController = null
  }
}

const stop = () => {
  if (abortController) {
    abortController.abort()
    abortController = null
    sending.value = false
    ElMessage.info("已中断发送")
  }
}

// 生命周期
onMounted(() => {
  loadHistory()
})

onBeforeUnmount(() => {
  stop()
})

// 监听路由变化
watch(
  () => route.params.session_id,
  async (v) => {
    sessionId.value = v
    stop()
    messages.value = []
    await loadHistory()
  }
)
</script>

---

### Template 和 Style

Template 和 Style 部分没有改动，因为它们已经写得很好了。我将它们保留在这里，以便您有一个完整的可运行文件。

```vue
<template>
  <div class="chat-wrapper">
    <el-card class="chat-header">
      <div>会话ID: {{ sessionId }}</div>
      <el-button v-if="sending" @click="stop">中断</el-button>
    </el-card>

    <el-card class="chat-body" ref="chatListRef">
      <div v-for="(m, idx) in messages" :key="idx" class="msg" :class="m.role">
        <div class="bubble">
          <div class="content" v-html="m.content.replace(/\n/g,'<br/>')"></div>
          <div class="meta">{{ m.role === 'user' ? '我' : 'AI' }} · {{ fmtTime(m.timestamp) }}</div>
        </div>
      </div>

      <div v-if="sending" class="msg assistant">
        <div class="bubble">
          <div class="content">
            <div class="flex space-x-1">
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="chat-input">
      <el-input
        v-model="inputText"
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 6 }"
        placeholder="输入消息…（回车发送，Shift+回车换行）"
        @keyup.enter.exact.prevent="send"
        @keyup.enter.shift.exact.stop
      />
      <div class="actions">
        <el-button type="primary" :loading="sending" @click="send">发送</el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.chat-wrapper {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: calc(100vh - 120px);
  gap: 12px;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-body {
  overflow-y: auto;
}
.msg {
  display: flex;
  margin: 10px 0;
}
.msg.user {
  justify-content: flex-end;
}
.msg.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 10px 12px;
  border-radius: 12px;
  background: #f6f7f9;
}
.user .bubble {
  background: #e8f3ff;
}
.meta {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
  text-align: right;
}
.chat-input .actions {
  margin-top: 8px;
  text-align: right;
}

/* 加载动画 */
.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out both;
}
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>