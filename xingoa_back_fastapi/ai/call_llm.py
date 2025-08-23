from openai import AsyncOpenAI, OpenAI
import asyncio

from ai.ai_config import ai_settings
from ai.ai_logger import ai_logger



async def stream_llm(prompt: str):
    """流式获取LLM响应"""
    try:
        # 在函数内部初始化OpenAI客户端，而不是全局初始化
        client = OpenAI(
            base_url=ai_settings.AI_BASE_URL,
            api_key=ai_settings.AI_API_KEY
        )
        
        # 调用LLM的流式接口
        stream = client.chat.completions.create(
            model=ai_settings.AI_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=True,  # 启用流式响应
        )
        
        # 逐个返回流式数据
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                # 以SSE格式返回数据
                yield chunk.choices[0].delta.content
                # 短暂休眠，避免数据推送过快
                await asyncio.sleep(0.01)
        
        # 发送结束标记
        yield "data: [DONE]\n\n"
    except Exception as e:
        ai_logger.error(f"调用LLM失败: {str(e)}")
        raise e