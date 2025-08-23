import http from "./http";
import { useAuthStore } from "@/stores/auth";

// 获取历史会话列表
const getSessionList = () => {
    return http.get(`/ai/chat/sessions`)
}

// 新建会话
const addSession = (data) => {
    return http.post(`/ai/chat/start`, data)
}

// 删除会话
const deleteSession = (session_id) => {
  return http.delete(`/ai/chat/sessions/${session_id}`);
};

// 获取会话聊天历史
const getSessionChatHistory = (session_id) => {
  return http.get(`/ai/chat/history`, {
    params: { session_id }
  })
}

// 发送消息
const sendMessage = (data) => {
    return http.post(`/ai/chat/message`, data)
}

// 流式对话（SSE解析）
const sendMessageStream = async (data, onMessage, onError, onComplete, signal) => {
  try {
    const authStore = useAuthStore()
    // 确保URL正确，没有重复的/api/v1
    const baseUrl = import.meta.env.VITE_BASE_URL || '';
    const url = baseUrl.endsWith('/api/v1')  ? `${baseUrl}/ai/chat/stream`  : `${baseUrl}/api/v1/ai/chat/stream`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(data),
      signal,
    })

    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status} ${response.statusText}`)
    }

    if (!response.body) {
      throw new Error("响应没有内容")
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder("utf-8")
    let buffer = ""

    while (true) {
    const { done, value } = await reader.read()
    if (done) break

    // 1. 解码当前数据块（保留原逻辑）
    buffer += decoder.decode(value, { stream: true })
    
    // 2. 按 SSE 格式分割（每个事件以 \n\n 分隔，保留原逻辑）
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || '' // 保留不完整的最后一段，下次继续处理
    
    // 3. 处理每个完整的事件（关键修改：增加去重 data: 前缀）
    for (const line of lines) {
        if (line.startsWith('data: ')) {
        // 核心修改：移除所有多余的 "data: " 前缀（兼容重复情况）
        // 例如将 "data:data: 您" → "您"，"data: 提到" → "提到"
        let dataContent = line.trim()
        // 循环移除所有开头的 "data: "（处理1次或多次重复）
        while (dataContent.startsWith('data: ')) {
            dataContent = dataContent.slice(6).trim() // 每次移除 "data: "（长度6）
        }
        
        // 后续逻辑不变（处理结束标记、传递数据）
        if (dataContent === '[DONE]') {
            onComplete?.()
            return
        }
        if (dataContent) {
            onMessage?.(dataContent) // 将去重后的数据传递给组件
        }
        } else if (line.startsWith('event: error')) {
        // 错误事件处理（保留原逻辑）
        const errorLine = line.split('\n').find(l => l.startsWith('data: '))
        if (errorLine) {
            let errorMsg = errorLine.trim()
            // 错误信息也需要去重 data: 前缀
            while (errorMsg.startsWith('data: ')) {
            errorMsg = errorMsg.slice(6).trim()
            }
            throw new Error(errorMsg)
        } else {
            throw new Error('发生未知错误')
        }
        }
    }
    }

    // 处理剩余的缓冲数据
    if (buffer) {
      if (buffer.startsWith('data: ')) {
        const dataContent = buffer.slice(6).trim()
        if (dataContent && dataContent !== '[DONE]') {
          onMessage?.(dataContent)
        }
      }
    }

    onComplete?.()
  } catch (err) {
    onError?.(err)
  }
}

export default {
    getSessionList,
    addSession,
    deleteSession,
    getSessionChatHistory,
    sendMessage,
    sendMessageStream,
}
