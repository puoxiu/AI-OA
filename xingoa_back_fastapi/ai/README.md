

## Redis存储会话结构示例

### 用户会话列表
> 存储每个用户的所有的会话

> eg： 用户ID=12345 的会话列表

```json
Key: user_sessions:12345
Type: Hash
Value:
{
   "session_001": '{"session_id":"session_001","last_message":"你好...","last_timestamp":"2025-08-21T14:05"}',
   "session_002": '{"session_id":"session_002","last_message":"帮我写个Python代码","last_timestamp":"2025-08-21T14:07"}'
}


```

### 会话详情
> 存储每个会话的详细信息，👉 用来展示某个会话里的完整聊天记录
> eg： 会话ID=session_001 的会话详情

```json
Key: conversation:12345:session_001
Type: List
Value:
[
   '{"role":"user","content":"你好"}',
   '{"role":"assistant","content":"你好，我能帮你什么？"}',
   '{"role":"user","content":"今天天气怎么样？"}',
   '{"role":"assistant","content":"今天晴天，气温25度"}'
]

```


### 关系图

> 会话列表 👉 会话详情
> 会话详情 👉 会话消息

```less
[ user_sessions:12345 ]   --->   [ conversation:12345:session_001 ]
      (会话索引)                   (具体聊天记录)
           |
           +--------------------> [ conversation:12345:session_002 ]
```

* user_sessions:{user_id} 是目录/索引表，存放用户有哪些会话，以及每个会话的最近一句话和时间。
* conversation:{user_id}:{session_id} 才是实际聊天内容，存放消息的顺序列表。

