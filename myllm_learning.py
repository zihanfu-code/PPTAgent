"""
MyLLM —— 学习用 LLM 封装类
============================
对照 PPTAgent 原始 llms.py 中的 LLM 类编写。
目标：掌握 chat / embedding / image generation 三大 API + 自动重试机制。

使用方法：
    llm = MyLLM(model="gpt-4o", base_url="https://api.openai.com/v1", api_key="sk-xxx")

    # 1. 纯文本对话
    response = llm("你好，介绍一下Python")

    # 2. 带 system prompt 的对话
    response = llm("介绍一下Python", system="你是一个编程教师")

    # 3. 多模态：图片 + 文本（传入图片路径）
    response = llm("描述这张图片", images="photo.jpg")

    # 4. 文本 Embedding
    embedding = llm.get_embedding("Hello world")  # → torch.Tensor

    # 5. 图像生成
    image_b64 = llm.gen_image("a cat sitting on a table")  # → base64 字符串
"""

import base64
from typing import Optional, Union

import torch
from openai import OpenAI


# ============================================================================
# 第 1 层：自动重试装饰器
# ============================================================================

def auto_retry(max_attempts: int = 3, wait_seconds: float = 2.0):
    """
    自动重试装饰器 —— 学习版。

    当被装饰的函数抛异常时，等待 wait_seconds 秒后重试，最多重试 max_attempts 次。
    如果全部失败，抛出最后一次的异常。

    这是 PPTAgent 中 @tenacity_decorator 的简化手写版。
    学习 tenacity 库之前，先理解重试逻辑本身。
    """
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        print(f"[Retry {attempt}/{max_attempts}] 等待 {wait_seconds}s 后重试... 错误: {e}")
                        time.sleep(wait_seconds)
                    else:
                        print(f"[重试耗尽] {max_attempts} 次全部失败。")
            raise last_exception
        return wrapper
    return decorator


# ============================================================================
# 第 2 层：MyLLM 类 —— 封装三大 API
# ============================================================================

class MyLLM:
    """
    教学版 LLM 封装类。

    对照 PPTAgent llms.py:18-210 的 LLM 类，提取最核心的三个能力：
      1. chat        → __call__()
      2. embedding   → get_embedding()
      3. image_gen   → gen_image()

    简化点：
      - 去掉了异步（AsyncLLM 单独学习）
      - 去掉了 batch 批处理
      - 去掉了 history 管理（那是 Agent 层的职责）
      - 去掉了 connection test、SOCKS 代理 等运维细节
    """

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        初始化 LLM 客户端。

        Args:
            model:   模型名称，如 "gpt-4o", "qwen-plus"
            base_url: API 地址，None 则用 OpenAI 默认地址
            api_key:  API 密钥，None 则读环境变量 OPENAI_API_KEY
        """
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

        # 核心：创建 OpenAI 客户端对象
        # 这是所有 API 调用的入口，对标 llms.py:30-32
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    # =========================================================================
    # 2.1 Chat —— 对话（纯文本 + 多模态图片）
    # =========================================================================

    @auto_retry(max_attempts=3, wait_seconds=2.0)
    def __call__(
        self,
        content: str,
        system: Optional[str] = None,
        images: Optional[Union[str, list[str]]] = None,
    ) -> str:
        """
        调用 LLM 对话，支持纯文本和多模态（图片+文本）。

        Args:
            content: 用户输入的文本（必填）
            system:  系统提示词，设定模型角色（可选）
            images:  图片文件路径或路径列表（可选）

        Returns:
            模型返回的文本字符串

        ——————————————————
        对照 PPTAgent 原始实现：

        llms.py:34-72 的 LLM.__call__():
          - 多了 history（对话历史）参数 → Agent 层管理，这里省略
          - 多了 return_json / return_message 后处理 → 这里省略
          - 多了 **client_kwargs（透传 temperature 等）→ 这里省略

        核心逻辑完全一致：
          format_message() → client.chat.completions.create() → 取 response
        """
        # 第 1 步：构建 messages
        # 对标 llms.py:62: system, message = self.format_message(...)
        messages = self._build_messages(content, system, images)

        # 第 2 步：调用 OpenAI API
        # 对标 llms.py:64-66: self.client.chat.completions.create(...)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        # 第 3 步：提取响应文本
        # 对标 llms.py:70: completion.choices[0].message.content
        return completion.choices[0].message.content

    def _build_messages(
        self,
        content: str,
        system: Optional[str] = None,
        images: Optional[Union[str, list[str]]] = None,
    ) -> list[dict]:
        """
        构建发送给 API 的 messages 列表。

        消息结构（OpenAI 标准格式）：
        [
            {"role": "system", "content": "你是一个..."},           ← 角色设定
            {"role": "user",   "content": [                        ← 用户消息
                {"type": "text", "text": "描述这张图片"},           ← 文本部分
                {"type": "image_url", "image_url": {"url":          ← 图片部分
                    "data:image/jpeg;base64,/9j/4AAQ..."}}          ← base64 编码
            ]}
        ]

        对标 llms.py:126-171 的 format_message()，但做了简化：
          - 去掉了"从 content 首行自动提取 system message"的智能逻辑
          - 去掉了 SOCKS 代理相关的图片处理
        """
        # 处理 images 参数：统一转成列表
        if isinstance(images, str):
            images = [images]

        # ─── 构建 system message ───
        messages = []
        if system is not None:
            messages.append({
                "role": "system",
                "content": system,
            })

        # ─── 构建 user message ───
        user_content = [{"type": "text", "text": content}]

        # 如果有图片，把每张图片编码为 base64 追加到 user_content
        if images is not None:
            for image_path in images:
                image_block = self._encode_image(image_path)
                user_content.append(image_block)

        messages.append({"role": "user", "content": user_content})
        return messages

    def _encode_image(self, image_path: str) -> dict:
        """
        将图片文件编码为 OpenAI Vision API 要求的格式。

        输入：图片文件路径，如 "cat.jpg"
        输出：
        {
            "type": "image_url",
            "image_url": {
                "url": "data:image/jpeg;base64,/9j/4AAQ..."
            }
        }

        对标 llms.py:159-168 的图片编码逻辑。
        """
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_data}"
            },
        }

    # =========================================================================
    # 2.2 Embedding —— 文本向量化
    # =========================================================================

    @auto_retry(max_attempts=3, wait_seconds=2.0)
    def get_embedding(self, text: str) -> torch.Tensor:
        """
        获取文本的 embedding 向量。

        Args:
            text: 输入文本

        Returns:
            torch.Tensor: embedding 向量（形状取决于模型）

        ——————————————————
        对标 llms.py:183-199 的 get_embedding():
          - 去掉了 encoding_format 参数（默认 "float"）
          - 去掉了 to_tensor 参数（始终返回 Tensor，因为 PPTAgent 用 cosine_similarity）
          - 保留核心调用：client.embeddings.create(model=..., input=...)

        Embedding 在 PPTAgent 中的作用：
          - Agent 的"语义相似历史检索"（agent.py:128）
          - Document 的"图片标题模糊匹配"（document.py:505-515）
        """
        # 调用 OpenAI Embeddings API
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        # 提取 embedding 向量并转换为 PyTorch Tensor
        # PPTAgent 使用 torch.cosine_similarity 计算相似度，所以必须转 Tensor
        embedding = response.data[0].embedding
        return torch.tensor(embedding)

    # =========================================================================
    # 2.3 Image Generation —— AI 绘图
    # =========================================================================

    @auto_retry(max_attempts=3, wait_seconds=2.0)
    def gen_image(self, prompt: str) -> str:
        """
        根据文本描述生成图片。

        Args:
            prompt: 图片描述文本，如 "a sunset over mountains"

        Returns:
            str: 生成图片的 base64 编码字符串

        ——————————————————
        对标 llms.py:173-181 的 gen_image():
          - 原始版本返回 b64_json（base64 字符串），方便嵌入到 PPTX 中
          - 去掉了 n 参数（这里每次只生成 1 张）
        """
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            n=1,
            response_format="b64_json",  # 直接返回 base64，不经过磁盘
        )
        return response.data[0].b64_json

    # =========================================================================
    # 2.4 辅助方法
    # =========================================================================

    def __repr__(self) -> str:
        """对标 llms.py:100-104"""
        return f"MyLLM(model={self.model}, base_url={self.base_url})"


# ============================================================================
# 第 3 层：对比学习 —— 原始 LLM 与 MyLLM 的差异速查
# ============================================================================

"""
┌────────────────────┬──────────────────────────┬─────────────────────────┐
│ 功能               │ PPTAgent 原始 LLM        │ MyLLM（学习版）          │
├────────────────────┼──────────────────────────┼─────────────────────────┤
│ 聊天               │ __call__() 14 个参数      │ __call__() 3 个参数      │
│ 图片输入           │ ✅ 多张，base64 编码      │ ✅ 相同逻辑              │
│ System prompt      │ ✅ + 自动从首行提取       │ ✅ 简化版                │
│ Embedding          │ ✅ → torch.Tensor         │ ✅ 相同                  │
│ 图像生成           │ ✅ → b64_json             │ ✅ 相同                  │
│ 历史消息           │ ✅ history 参数            │ ❌ Agent 层负责          │
│ JSON 模式          │ ✅ return_json 参数        │ ❌ 省略                  │
│ 重试机制           │ tenacity（3s 等/5 次）     │ auto_retry（手写，教学用）│
│ 异步版本           │ AsyncLLM（独立类）         │ ❌ 省略                  │
│ 批处理             │ oaib.Auto                 │ ❌ 省略                  │
│ 连接测试           │ test_connection()         │ ❌ 省略                  │
│ 同步↔异步转换      │ to_sync() / to_async()    │ ❌ 省略                  │
│ SOCKS 代理         │ ✅                        │ ❌ 省略                  │
└────────────────────┴──────────────────────────┴─────────────────────────┘
"""


# ============================================================================
# 第 4 层：自测代码
# ============================================================================

if __name__ == "__main__":
    import os

    # 配置 —— 根据你的 API 修改
    llm = MyLLM(
        model=os.environ.get("LANGUAGE_MODEL", "gpt-4o"),
        base_url=os.environ.get("API_BASE", None),
        api_key=os.environ.get("API_KEY", None),
    )

    print("=" * 60)
    print("测试 1: 纯文本对话")
    print("=" * 60)
    response = llm("用一句话介绍Python语言")
    print(f"回复: {response}\n")

    print("=" * 60)
    print("测试 2: 带 System Prompt 的对话")
    print("=" * 60)
    response = llm(
        "用一句话介绍Python语言",
        system="你是一个幼儿园老师，要用小朋友能听懂的话回答",
    )
    print(f"回复: {response}\n")

    print("=" * 60)
    print("测试 3: Embedding")
    print("=" * 60)
    emb = llm.get_embedding("Hello world")
    print(f"Embedding 形状: {emb.shape}")
    print(f"Embedding 前 5 个值: {emb[:5]}\n")

    print("=" * 60)
    print("测试 4: 重试机制演示")
    print("=" * 60)
    print("（用一个不存在的 API 地址触发重试）")
    bad_llm = MyLLM(
        model="gpt-4o",
        base_url="https://this-does-not-exist.example.com/v1",
        api_key="fake-key",
    )
    try:
        bad_llm("hello")
    except Exception as e:
        print(f"最终异常: {type(e).__name__}: {e}")
