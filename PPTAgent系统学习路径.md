# PPTAgent 系统学习路径（大模型开发聚焦版）

> **目标**：掌握 PPTAgent 中大模型相关的核心技术，能拆解复用 Agent 框架、LLM 封装、Prompt 工程到自己的项目
> **基础**：有 Python 基础，不熟悉异步/高级特性
> **总时长**：约 5-6 周（每天 3-4 小时）

---

## 目录

- [第 0 阶段：环境准备](#第-0-阶段环境准备)
- [第 1 阶段：Python 高级特性](#第-1-阶段python-高级特性)
- [第 2 阶段：LLM API 编程基础](#第-2-阶段llm-api-编程基础)
- [第 3 阶段：RAG 与文档处理](#第-3-阶段rag-与文档处理)
- [第 4 阶段：Agent 框架深入（核心）](#第-4-阶段agent-框架深入核心)
- [第 5 阶段：Code-as-Action 模式（核心）](#第-5-阶段code-as-action-模式核心)
- [第 6 阶段：多 Agent 协作流水线（核心）](#第-6-阶段多-agent-协作流水线核心)
- [第 7 阶段：架构整合与拆解复用](#第-7-阶段架构整合与拆解复用)

---

## 第 0 阶段：环境准备

**时长**：1 天 | **目标**：能跑通测试，IDE 能跳转代码

### 0.1 安装 PPTAgent

```bash
# clone 源码
git clone https://github.com/zihanfu-code/PPTAgent.git
cd PPTAgent
pip install -e .
```

### 0.2 配置 IDE

- 用 VS Code 打开项目根目录
- 验证：点击 [agent.py](pptagent/agent.py) 中的 `class Agent`，能跳转到定义

### 0.3 跑通测试（验证安装成功）

```bash
pytest -v -n 8 test/
```

> **注意**：跑测试需要 LLM API Key。如果暂时没有，跳过也可，不影响代码阅读。

---

## 第 1 阶段：Python 高级特性

**时长**：1 周 | **目标**：能顺畅阅读 PPTAgent 中所有 Python 语法

> PPTAgent 大量使用了 Python 高级特性，不掌握它们 = 读代码如读天书。

### 1.1 asyncio 异步编程（2 天）

**为什么重要**：整个项目异步化。`AsyncAgent`、`AsyncLLM`、`asyncio.TaskGroup` 无处不在。异步是构建高吞吐 LLM 应用的必备技能。

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `async/await` 基本语法 | [llms.py:229-300](pptagent/llms.py#L229-L300) `AsyncLLM.__call__()` |
| `asyncio.TaskGroup` 并行执行 | [document.py:344-363](pptagent/document/document.py#L344-L363) 同时解析多个文档块 |
| `asyncio.gather` 并行等待 | [document.py:538-540](pptagent/document/document.py#L538-L540) 并行获取多个 image embedding |
| `asyncio.create_task` 创建任务 | [induct.py](pptagent/induct.py) `SlideInducterAsync` 多处使用 |

**实践练习**：写一个简化版 `AsyncLLM`：
1. `async def __call__(self, prompt)` 异步调用
2. 用 `asyncio.TaskGroup` 同时发 5 个请求
3. 用 `asyncio.gather` 收集所有结果

---

### 1.2 dataclasses 数据类（1 天）

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `@dataclass` 基本用法 | [agent.py](pptagent/agent.py) `Turn` 类 — 自动生成 `__init__`、`__repr__` |
| `field(default=...)` 默认值 | [document.py:114-118](pptagent/document/document.py#L114-L118) `Document` |
| `__post_init__` 初始化后处理 | [document.py:120-121](pptagent/document/document.py#L120-L121) 自动设置日期 |
| `asdict()` 转字典 | [document.py:395-396](pptagent/document/document.py#L395-L396) `Document.to_dict()` |
| 嵌套 dataclass | [document.py:440-457](pptagent/document/document.py#L440-L457) `OutlineItem` |

**实践练习**：把 [agent.py](pptagent/agent.py) 的 `Turn` 类和 [document.py](pptagent/document/document.py) 的 `Document`、`OutlineItem` 的定义抄写一遍并加注释。

---

### 1.3 装饰器 + Type Hints（2 天）

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `@tenacity` 重试装饰器 | [utils.py:26](pptagent/utils.py#L26) — 失败等 3s 重试最多 5 次 |
| `@staticmethod` / `@classmethod` | [document.py:153-206](pptagent/document/document.py#L153-L206) `Document._parse_chunk` |
| `@property` 属性 | [document.py:431-436](pptagent/document/document.py#L431-L436) |
| `Optional[X]`、`dict[str, list[str]]` | 几乎所有函数参数 |
| `Callable` 可调用对象 | [apis.py](pptagent/apis.py) `API_TYPES.all_funcs() -> dict[str, callable]` |

**实践练习**：自己写一个 `@retry(max_attempts=3, wait_seconds=2)` 装饰器，能装饰任意函数并自动重试。

---

### 阶段检验

- [ ] 能解释 `await` 为什么释放 GIL 但不等于多线程
- [ ] 能用 `@dataclass` 定义包含嵌套类型的类
- [ ] 能手写一个重试装饰器

---

## 第 2 阶段：LLM API 编程基础

**时长**：1.5 周 | **目标**：能独立封装一个 LLM 调用类（chat + embedding + 多模态 + 重试）

### 2.1 OpenAI Compatible API（3 天）

**对应代码**：[pptagent/llms.py](pptagent/llms.py)（约 310 行，逐行精读 3 遍）

这是整个项目的"发动机"。所有 Agent 最终都通过这个文件调用 LLM。

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `OpenAI()` 客户端初始化 | [llms.py:30-40](pptagent/llms.py#L30-L40) | `api_key`、`base_url`、SOCKS 代理 — 支持任何 OpenAI 兼容端点 |
| `chat.completions.create()` | [llms.py:50-80](pptagent/llms.py#L50-L80) | `model`、`messages`、`response_format`、`stream` |
| 多模态调用（图片 base64） | [llms.py:100-150](pptagent/llms.py#L100-L150) | PIL Image → base64 → `image_url` 格式，文本+图片混合输入 |
| Embeddings API | [llms.py:160-190](pptagent/llms.py#L160-L190) | `embeddings.create()` → `torch.Tensor`，用于语义检索 |
| JSON Mode（结构化输出） | [llms.py:65-70](pptagent/llms.py#L65-L70) | `response_format={"type": "json_object"}`，让 LLM 返回合法 JSON |
| 连接测试 | [llms.py:250-260](pptagent/llms.py#L250-L260) | 发送简短请求验证 API 可用 |

**实践练习**：基于 `openai` 库封装自己的 `MyLLM` 类：
- `__call__(prompt, system=None)` → 文本回复
- `__call__(image, prompt)` → 多模态输入
- `get_embedding(text)` → embedding 向量
- 自动重试 3 次

---

### 2.2 AsyncLLM 异步封装 + Batch（2 天）

**对应代码**：[pptagent/llms.py:229-310](pptagent/llms.py#L229-L310)

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `AsyncOpenAI()` vs `OpenAI()` | [llms.py:229-240](pptagent/llms.py#L229-L240) | 异步客户端初始化 |
| **Batch 批量请求 (`oaib.Auto`)** | [llms.py:234-240](pptagent/llms.py#L234-L240) | `oaib.Auto` 将多个请求自动合并批量提交，大幅提升吞吐量 |
| 异步多模态 | [llms.py:270-290](pptagent/llms.py#L270-L290) | async 版本的多模态调用 |
| 异步 Embedding | [llms.py:295-310](pptagent/llms.py#L295-L310) | async 版本的 embedding |

**关键理解**：为什么需要 `AsyncLLM` + `oaib.Auto`？
- 同步 LLM 调用是 IO 密集型，一次请求等 2-5 秒
- 异步版本在等待时释放事件循环，让其他请求并发执行
- `oaib.Auto` 进一步把多个独立请求合并成一个 batch，减少 API 调用次数

**实践练习**：对比 `LLM.__call__`（同步）和 `AsyncLLM.__call__`（异步）的代码差异，用 diff 工具标注所有不同之处。

---

### 2.3 Prompt Engineering 实战（2 天）

PPTAgent 有 16 个 prompt 模板 + 9 个 YAML 角色配置，是最佳的 Prompt Engineering 学习材料。

| 知识点 | PPTAgent 代码位置 |
|--------|------------------|
| Jinja2 模板渲染 | [agent.py:55-62](pptagent/agent.py#L55-L62) `Environment(undefined=StrictUndefined)` |
| YAML 角色三段式配置 | [agent.yaml](pptagent/roles/agent.yaml) `system_prompt` + `template` + `jinja_args` |
| 结构化输出 Prompt | [prompts/ppteval_content.txt](pptagent/prompts/ppteval_content.txt) |
| 多模态 Prompt | [prompts/caption.txt](pptagent/prompts/caption.txt) |

**9 个 Agent 角色一览**：

| 角色文件 | 模型类型 | 作用 | 大模型开发启示 |
|---------|---------|------|--------------|
| [planner.yaml](pptagent/roles/planner.yaml) | language | 规划任务结构 | 任务分解 Agent |
| [doc_extractor.yaml](pptagent/roles/doc_extractor.yaml) | language/vision | 提取结构化内容 | 信息抽取 Agent |
| [schema_extractor.yaml](pptagent/roles/schema_extractor.yaml) | language | 从样例提取 schema | 模式学习 Agent |
| [layout_selector.yaml](pptagent/roles/layout_selector.yaml) | vision | 图文匹配选择 | 多模态匹配 Agent |
| [content_organizer.yaml](pptagent/roles/content_organizer.yaml) | language | 组织内容结构 | 内容编排 Agent |
| [coder.yaml](pptagent/roles/coder.yaml) | language | 生成可执行代码 | **代码生成 Agent**（重点） |
| [editor.yaml](pptagent/roles/editor.yaml) | vision | 审查并修正结果 | 质量审查 Agent |
| [agent.yaml](pptagent/roles/agent.yaml) | language | 通用内容处理 | 通用 Agent 模板 |
| [copilot.yaml](pptagent/roles/copilot.yaml) | language | 辅助决策验证 | 验证 Agent |

**实践练习**：选 [coder.yaml](pptagent/roles/coder.yaml)、[planner.yaml](pptagent/roles/planner.yaml)、[editor.yaml](pptagent/roles/editor.yaml) 3 个角色，分析其 prompt 结构，回答：
- system_prompt 定义了什么角色身份？
- template 要求输出什么格式？
- 哪些输入变量来自上游 Agent 的输出？

---

### 2.4 LLM 输出后处理（1 天）

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| `json_repair` 修复坏 JSON | [utils.py:14](pptagent/utils.py#L14) | LLM 经常输出缺括号的 JSON，自动修复 |
| 多策略 JSON 提取 | [utils.py](pptagent/utils.py) `get_json_from_response()` | `json.loads` → 正则 → `json_repair` 三级兜底 |
| `tiktoken` Token 计数 | [agent.py:6](pptagent/agent.py#L6) | 精确计算 prompt 长度，超限截断历史 |
| `edit_distance` 编辑距离 | [utils.py:15](pptagent/utils.py#L15) | 模糊匹配标题/图片 caption，LLM 输出不精确时的容错手段 |

---

### 阶段检验

- [ ] 能独立封装一个 `MyLLM` 类，支持 chat + embedding + 多模态 + 重试
- [ ] 能逐行读懂 [llms.py](pptagent/llms.py)
- [ ] 能解释 `oaib.Auto` 的批量调度原理
- [ ] 能分析一个 Agent 角色的 prompt 设计

---

## 第 3 阶段：RAG 与文档处理

**时长**：1.5 周 | **目标**：理解文档解析→切分→嵌入→检索的完整 RAG 管道

> RAG 是大模型应用中最常见的模式之一。PPTAgent 的文档处理层本质上就是一个完整的 RAG 管道。

### 3.1 预热：用练习项目建立 RAG 直觉（3 天）

#### 步骤 1：LangChain RAG（1 天）

**练习项目**：`12. Langchain实现RAG/`

| 文件 | 知识点 |
|------|--------|
| [rag.py](D:/UST/vibe/练习/居丽叶玩具项目/12.%20Langchain实现RAG/rag.py) | 完整 RAG 流程代码 |

| 步骤 | 知识点 | 对应 PPTAgent 代码 |
|------|--------|-------------------|
| ① `TextLoader` 加载文档 | 文档加载 | [model_utils.py:58-63](pptagent/model_utils.py#L58-L63) marker-pdf 解析 |
| ② `RecursiveCharacterTextSplitter` 切分 | 语义分块 | [document.py:35-78](pptagent/document/document.py#L35-L78) `split_markdown_by_headings` |
| ③ `HuggingFaceBgeEmbeddings` 嵌入 | 文本向量化 | [llms.py:160-190](pptagent/llms.py#L160-L190) `get_embedding()` |
| ④ `Chroma.from_documents()` 存储 | 向量存储 | PPTAgent 直接用 `torch.cosine_similarity` 内存计算（无外部 DB） |
| ⑤ `similarity_search()` 检索 | 相似度检索 | [document.py:412-416](pptagent/document/document.py#L412-L416) |
| ⑥ `LLMChain` + `PromptTemplate` 生成 | 检索增强生成 | [agent.py](pptagent/agent.py) Agent prompt + LLM 调用 |

**关键对比**：

```
LangChain RAG:  文档 → Splitter → Embedding → ChromaDB → 相似度搜索 → LLM
PPTAgent RAG:   PDF → marker-pdf → Markdown → 标题分块 → Embedding → cosine_sim → 内容填充
```

---

#### 步骤 2：LlamaIndex RAG（1 天）

**练习项目**：`9. LLamaIndex 实现RAG/`

| 文件 | 知识点 |
|------|--------|
| `LLamIndex 实现 RAG.ipynb` | LlamaParse PDF 解析 + Markdown 输出 |

| LlamaIndex 做法 | PPTAgent 做法 |
|----------------|--------------|
| `LlamaParse` 云服务解析 | `marker-pdf` 本地模型解析 |
| `VectorStoreIndex` 向量索引 | `torch.cosine_similarity` 内存计算 |
| `SimpleDirectoryReader` 批量加载 | `parse_pdf()` 单文件 |

---

#### 步骤 3：Agent + RAG 融合（1 天）

**练习项目**：`11. Agent +RAG实现检索/`

| 文件 | 知识点 |
|------|--------|
| `11 Agent +RAG实现检索.ipynb` | Agent 架构 + RAG 检索 |

**Agent 四模块 vs PPTAgent 对应**：

```
Agent 模块         → PPTAgent 中的对应
├── Planning      → Planner Agent (pptgen.py)
├── Memory        → Turn 历史管理 (agent.py:88-140)
├── Tools         → CodeExecutor API 函数 (apis.py:533)
└── Executor      → CodeExecutor.execute_actions() (apis.py:127)
```

---

### 3.2 PPTAgent 文档处理管线（4 天）

#### 3.2.1 PDF → Markdown → Document（2 天）

**核心文件**：[pptagent/document/document.py](pptagent/document/document.py)（550 行）

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| 标题提取 + LLM 对齐 | [document.py:292-295](pptagent/document/document.py#L292-L295) | 正则提取 → LLM 调整标题结构 |
| 按标题分块 | [document.py:35-78](pptagent/document/document.py#L35-L78) | `split_markdown_by_headings` — 合并小段防止碎片化 |
| 段落分类 | [document.py:81-111](pptagent/document/document.py#L81-L111) | 文本/表格/图片自动分类 |
| 并行解析（TaskGroup） | [document.py:344-364](pptagent/document/document.py#L344-L364) | 多块并行解析 + 生成摘要 |
| 媒体关联 | [document.py:227](pptagent/document/document.py#L227) | 表格/图片关联到最近段落 |
| LLM 生成 caption | [document.py:174-179](pptagent/document/document.py#L174-L179) | Language Model 写表格标题，Vision Model 写图片标题 |
| **Retry + Feedback** | [document.py:181-206](pptagent/document/document.py#L181-L206) | 解析失败→错误+traceback 注入 prompt→重试最多 3 次 |
| 两级检索 | [document.py:398-415](pptagent/document/document.py#L398-L415) | `retrieve()` Section → SubSection 精确查找 |

**Retry + Feedback 模式（重点）**：

```python
# 不是简单的 while retry < 3:
# 而是把异常信息注入 prompt，让 LLM 知道上次哪里错了
new_section = extractor.retry(
    str(e),                      # 错误信息
    traceback.format_exc(),      # 完整堆栈
    turn_id,                     # 哪一轮对话
    retry + 1                    # 第几次重试
)
```

这是 PPTAgent 的核心技巧——**让 LLM 看到自己上轮的输出和报错，自我纠正。**

---

#### 3.2.2 模型管理（1 天）

**核心文件**：[pptagent/model_utils.py](pptagent/model_utils.py)

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| `ModelManager` | [model_utils.py:23-78](pptagent/model_utils.py#L23-L78) | 统一管理 3 个 LLM + ViT + marker 模型 |
| 懒加载模式 | [model_utils.py:52-63](pptagent/model_utils.py#L52-L63) | `@property` 实现首次访问才加载，节省内存 |
| `test_connections()` | [model_utils.py:66-78](pptagent/model_utils.py#L66-L78) | 启动时验证所有模型连接可用 |
| 多模型类型切换 | [model_utils.py:48-50](pptagent/model_utils.py#L48-L50) | language / vision / text / image / marker 五种模型 |

---

#### 3.2.3 多模态处理（1 天）

**核心文件**：[pptagent/multimodal.py](pptagent/multimodal.py)

| 知识点 | 说明 |
|--------|------|
| Vision Model 图片理解 | 用 Vision Model 为图片生成自然语言 caption |
| 图片统计 | 收集大小/位置/频率，辅助后续选择 |

---

### 阶段检验

- [ ] 能画出 PDF → Markdown → Document → Section → SubSection 的数据流
- [ ] 能解释 Retry + Feedback 模式为什么比简单重试更有效
- [ ] 能说出编辑距离 (`edit_distance`) 在什么场景下优于字符串相等

---

## 第 4 阶段：Agent 框架深入（核心）

**时长**：1 周 | **目标**：能复刻一个简化的 Agent 框架

> 这是 PPTAgent 最重要的可复用模块。Agent 框架 = YAML 配置 + Jinja2 模板 + LLM 调用 + 历史管理 + Retry。

### 4.1 Agent 核心类（3 天）

**核心文件**：[pptagent/agent.py](pptagent/agent.py)（401 行，**全文精读**）

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `Turn` 数据结构 | [agent.py:19-30](pptagent/agent.py#L19-L30) | 一轮对话：`prompt` + `response` + `info` |
| YAML 角色加载 | [agent.py:40-55](pptagent/agent.py#L40-L55) | `roles/{name}.yaml` → system_prompt + template + jinja_args |
| Jinja2 StrictUndefined | [agent.py:55-65](pptagent/agent.py#L55-L65) | 变量缺失时抛异常，防止静默错误 |
| Token 计数 + 截断 | [agent.py:70-85](pptagent/agent.py#L70-L85) | `tiktoken` 精确计算，超 context 限制时截断历史 |
| **历史管理**（亮点） | [agent.py:88-140](pptagent/agent.py#L88-L140) | 保留最近 N 轮 + **语义相似历史检索**（Embedding + Cosine Similarity） |
| `Agent.__call__` 主流程 | [agent.py:145-200](pptagent/agent.py#L145-L200) | 8 步执行流程 |
| `Agent.retry` | [agent.py:200-230](pptagent/agent.py#L200-L230) | 错误 + traceback → 重新渲染 → 重新调用 |
| LLM 映射 | [agent.py:40-50](pptagent/agent.py#L40-L50) | 一个 Agent 可调用多个不同模型 |

**Agent 执行流程图**：

```
输入：用户变量（如 schema=..., text=..., api_docs=...）

① 加载 roles/{name}.yaml
   ├── system_prompt: "You are a..."
   ├── template: "Task: ... {{schema}} ... {{api_docs}}"
   └── jinja_args: [schema, outline, text, api_docs]

② 过滤输入变量（只保留 jinja_args 中声明的）

③ Jinja2 渲染 template → 最终 prompt
   └── StrictUndefined 确保所有 {{变量}} 都有值

④ 构造 messages:
   [{"role": "system", "content": system_prompt}]
   + [历史 Turn（按相似度 + 最近 N 轮筛选）]
   + [{"role": "user", "content": prompt}]

⑤ tiktoken 计数 → 超 context 限制则截断历史

⑥ LLM 调用（language model 或 vision model）

⑦ 解析返回值 → 存入 Turn(history.append(Turn(...)))

⑧ 如果 return_json=True → json_repair 修复 → json.loads
   如果出错 → retry（错误信息注入 prompt → 回到⑥）
```

### 4.2 AsyncAgent 对比（1 天）

**代码位置**：[pptagent/agent.py:240-401](pptagent/agent.py#L240-L401)

| 同步 `Agent` | 异步 `AsyncAgent` | 差异 |
|-------------|-------------------|------|
| `LLM` 客户端 | `AsyncLLM` 客户端 | 底层 SDK 不同 |
| `for` 循环顺序获取 embedding | `asyncio.TaskGroup` 并行获取 | 并行提升性能 |
| `def __call__` | `async def __call__` | 调用方加 `await` |
| `def retry` | `async def retry` | 全链路异步 |

**实践练习**：将 `Agent.__call__` 和 `AsyncAgent.__call__` 并排对照，标注所有 `async/await` 差异点。

---

### 4.3 Prompt 模板体系（2 天）

**目录**：[pptagent/prompts/](pptagent/prompts/)（16 个模板）+ [pptagent/roles/](pptagent/roles/)（9 个角色）

**按用途分类**：

| 类别 | 模板文件 | 调用的 Agent/代码 |
|------|---------|------------------|
| **文档理解** | `heading_extract.txt`、`section_summary.txt`、`merge_metadata.txt` | [document.py](pptagent/document/document.py) |
| **内容生成** | `caption.txt`、`markdown_table_caption.txt`、`markdown_image_caption.txt`、`table_parsing.txt` | multimodal.py, document/element.py |
| **PPT 分析** | `category_split.txt`、`ask_category.txt` | [induct.py](pptagent/induct.py) |
| **PPT 生成** | `lengthy_rewrite.txt` | [pptgen.py](pptagent/pptgen.py) |
| **质量评估** | `ppteval_content.txt`、`ppteval_style.txt`、`ppteval_coherence.txt`、`ppteval_describe_*.txt`、`ppteval_extract.txt` | [ppteval.py](pptagent/ppteval.py) |

**角色协作关系**：

```
Phase I（分析参考 PPT）:
  doc_extractor ──→ schema_extractor ──→ layout_selector
       │                    │
       └── 提取文档结构      └── 学习 PPT 内容模式

Phase II（生成新 PPT）:
  planner ──→ content_organizer ──→ layout_selector ──→ coder ──→ editor
    │              │                      │               │          │
   规划每页      组织具体内容          选择最佳布局    生成操作代码  审查修正
                                                         │
                                                    copilot（辅助）
```

**实践练习**：在 [pptgen.py](pptagent/pptgen.py) 中搜索每个 Agent 的调用点，画出 Agent 之间的数据传递图——上一个 Agent 的哪个输出字段传给了下一个 Agent 的哪个输入字段。

---

### 阶段检验

- [ ] 能手写一个简化版 Agent 框架（YAML 加载 + Jinja2 渲染 + LLM 调用 + Turn 历史）
- [ ] 能画出一轮 Agent 调用的完整 8 步流程
- [ ] 能说出 9 个 Agent 的职责和协作关系

---

## 第 5 阶段：Code-as-Action 模式（核心）

**时长**：1 周 | **目标**：理解并复刻"让 LLM 输出可执行代码"的设计模式

> 这是 PPTAgent 最创新的设计。普通 LLM 应用：LLM 输出描述文本 → 程序解析文本 → 执行操作。Code-as-Action：LLM 直接输出函数调用代码 → `eval()` 执行。

### 5.1 CodeExecutor 核心（3 天）

**核心文件**：[pptagent/apis.py](pptagent/apis.py)（549 行，**全文精读**）

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| API 函数枚举 | [apis.py:533-541](pptagent/apis.py#L533-L541) | `API_TYPES` 定义 5 个可用函数 |
| **函数文档自动生成** | [apis.py:84-125](pptagent/apis.py#L84-L125) | 用 `inspect` 读取函数的 `__doc__` + `__signature__` → 自动生成给 LLM 的 API 文档 |
| `execute_actions()` | [apis.py:127-203](pptagent/apis.py#L127-L203) | 解析 LLM 输出的代码行 → `eval()` 执行 → 收集结果 |
| `HistoryMark` | [apis.py:51-62](pptagent/apis.py#L51-L62) | 记录每次操作的历史，用于后续 slide 参考 |

**5 个 API 函数**：

| 函数 | 作用 |
|------|------|
| `replace_span(slide_idx, para_idx, span_idx, text)` | 替换指定位置的文本 |
| `clone_paragraph(slide_idx, para_idx)` | 克隆段落（保留样式） |
| `del_span(slide_idx, para_idx, span_idx)` | 删除文本 |
| `replace_image(slide_idx, image_path)` | 替换图片 |
| `del_image(slide_idx)` | 删除图片 |

**Code-as-Action 完整流程**：

```
① Coder Agent (LLM) 收到:
   ├── api_docs（自动生成的 5 个函数文档）
   ├── schema（当前页布局结构）
   ├── content（要填充的内容）
   └── current_slide_html（当前 slide 的 HTML 表示）

② Coder Agent (LLM) 输出:
   replace_span(0, 0, 0, "New Title")
   clone_paragraph(0, 1)
   replace_span(0, 2, 0, "New content...")
   replace_image(0, "images/chart.png")

③ CodeExecutor.execute_actions():
   逐行 eval() 执行 → 修改真实 PPTX 对象 → 返回 HistoryMark

④ Editor Agent 审查 → 不对则 retry
```

**为什么这种模式高效？**
- LLM 不需要输出"请把第一页的标题改成 XXX"然后程序解析
- LLM 直接输出 `replace_span(0, 0, 0, "XXX")`，程序直接 `eval()` 执行
- 减少了一层"文本解析"，降低了出错概率

**实践练习**：写一个简化版 CodeExecutor：
1. 定义 3 个自己的 API 函数（如 `send_email(to, subject, body)`）
2. 用 `inspect` 自动生成 API 文档
3. 把文档注入 prompt，让 LLM 输出调用代码
4. `eval()` 执行并收集结果

---

### 5.2 文本块处理（2 天）

**代码位置**：[apis.py:236-280](pptagent/apis.py#L236-L280) `TextBlock.build_run()`

| 知识点 | 说明 |
|--------|------|
| Markdown → HTML | `mistune` 渲染，自定义 `SlideRenderer` |
| HTML → 文本块 | `beautifulsoup4` 解析，提取样式标签 |
| 样式继承 | bold、italic、color、strikethrough、href → 应用到 PPTX Run 对象 |

---

### 5.3 Closure 延迟执行（2 天）

**核心文件**：[pptagent/presentation/shapes.py](pptagent/presentation/shapes.py)（1267 行，**速读即可**）

```python
# 核心思想：操作先记录为闭包，推迟到真实对象准备好时执行

class ClosureType(Enum):
    REPLACE_TEXT = auto()
    CLONE_PARAGRAPH = auto()
    # ...

class Closure:
    type: ClosureType
    func: Callable  # 实际操作函数，绑定了目标 slide
    args: tuple
```

**为什么用 Closure？**
- Agent 在"逻辑 slides"上操作（可能存在也可能不存在真实 PPTX 对象）
- Closure 把操作推迟到真实对象就绪
- 执行前可以验证所有 Closure 的合法性（事务性）

> **大模型开发启示**：这种"先规划操作序列 → 延迟批量执行"的模式适用于任何 LLM 操控外部工具的场景（如操作数据库、调用 API、操作文件）。

---

### 阶段检验

- [ ] 能手写一个简化版 CodeExecutor（注册函数 → 生成文档 → LLM 输出代码 → eval 执行）
- [ ] 能解释为什么 Code-as-Action 比"LLM 输出描述 → 程序解析"更可靠
- [ ] 能说出 Closure 模式和直接执行的各自适用场景

---

## 第 6 阶段：多 Agent 协作流水线（核心）

**时长**：1 周 | **目标**：理解多个 Agent 如何按流水线协作完成复杂任务

> 这是 PPTAgent 最复杂的部分。单个 Agent 能力有限，多 Agent 按阶段分工协作才能完成端到端任务。

### 6.1 架构总览（1 天）

**核心文件**：[pptagent/pptgen.py](pptagent/pptgen.py)（924 行）

**类继承体系**：

```
PPTGen (ABC)              ← 抽象基类，定义完整生成流程
├── PPTAgent              ← 同步实现
└── PPTGenAsync           ← 异步基类
    └── PPTAgentAsync     ← 异步实现（生产环境使用）

PPTGenAsync 在 PPTGen 基础上：
- 所有 Agent 换成 AsyncAgent
- 所有 LLM 换成 AsyncLLM
- 并行化所有可并行的步骤
```

**设计启示**：ABC 抽象基类定义了流程骨架，子类只需实现具体步骤。这种模式让同一套流程可以适配不同的 Agent 实现。

---

### 6.2 生成主流程（2 天）

**代码位置**：[pptgen.py:375-433](pptagent/pptgen.py#L375-L433)

```python
# PPTGenAsync.generate_pres() 主流程

async def generate_pres(self, document, ...):
    # ① 规划大纲
    outline = await self.generate_outline(document)
    #    Planner Agent: 输入 document 大纲 → 输出每页 purpose + section + images
    
    # ② 插入功能页（封面/目录/结束页）
    self._add_functional_layouts(outline)
    
    # ③ 修正大纲
    outline = await self._fix_outline(outline)
    #    Editor Agent: 检查大纲合理性 → 修正不合理的安排
    
    # ④ 逐页生成
    for slide_idx, item in enumerate(outline):
        await self.generate_slide(slide_idx, item, ...)
    
    # ⑤ 保存
    presentation.save("output.pptx")
```

---

### 6.3 单页生成（3 天）

**代码位置**：[pptgen.py:719-760](pptagent/pptgen.py#L719-L760)

这是最复杂的部分——**一页幻灯片调用 4 个 Agent**：

```
① _select_layout()         → layout_selector Agent
   输入: purpose + 内容摘要
   输出: 最佳 layout_schema
   
② _generate_content()      → content_organizer Agent  
   输入: schema + outline + document 检索结果
   输出: 结构化的页面内容
   
③ _generate_commands()     → coder Agent ⭐ 最关键
   输入: schema + 内容 + slide HTML + api_docs
   输出: API 调用序列（replace_span(...), clone_paragraph(...) 等）
   
④ _edit_slide()            → CodeExecutor 执行
   逐行 eval(LLM 生成的代码) → 修改 PPTX
   
⑤ _collect_history()       → 保存这次生成的经验
   为后续 slide 提供参考
```

**Agent 链数据流**：

```
Document ──→ Planner ──→ Content Organizer ──→ Coder ──→ CodeExecutor ──→ PPTX
              │                 │                   │            │
           purpose          structured          API calls     real edits
           + section        content             (代码)        (执行)
           + images
```

**实践练习**：


---

### 6.4 Phase I 分析流程（1 天）

**核心文件**：[pptagent/induct.py](pptagent/induct.py)（430 行）

> Phase I 是 PPT 特有的分析流程，但其中的**图像嵌入 + 聚类**模式在大模型开发中有通用价值。

```python
# layout_induct() 流程
PPT 每页 → ViT image embedding → cosine similarity 矩阵 → 聚类 → 布局模板

# content_induct() 流程
每类布局的代表 slide → LLM 分析结构 → 提取 content schema
```

**对大模型开发的启示**：
- ViT Embedding 用于无监督聚类，自动发现模板类型
- LLM 用于语义分析，提取结构化 schema
- 这种"视觉识别 + 语言理解"的双通道模式可复用到其他多模态任务

---

### 阶段检验

- [ ] 能画出完整 Phase II 的 5 步流程
- [ ] 能说清 Planner → Content Organizer → Coder → Editor 的数据传递链
- [ ] 能解释为什么用 PPTGen(ABC) → PPTGenAsync → PPTAgentAsync 三层抽象

---

## 第 7 阶段：架构整合与拆解复用

**时长**：3 天 | **目标**：能画出完整架构图，能拆出独立可复用的模块

### 7.1 全局架构图（0.5 天）

```
┌─────────────────────────────────────────────────────────┐
│                      输入层                              │
│  PDF ──→ marker-pdf ──→ Markdown ──→ Document           │
│  PPTX ──→ ViT Embedding ──→ 聚类 ──→ 布局模板           │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    LLM 抽象层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │   LLM    │  │ AsyncLLM │  │ oaib.Auto    │          │
│  │ (同步)   │  │ (异步)   │  │ (批量调度)   │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    Agent 框架层                          │
│  ┌────────────────────────────────────────────┐         │
│  │  Agent / AsyncAgent                        │         │
│  │  YAML配置 → Jinja2渲染 → LLM调用 → 历史管理 │         │
│  └────────────────────────────────────────────┘         │
│  9 个角色: planner │ organizer │ coder │ editor │ ...    │
│  16 个 Prompt 模板                                     │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    执行层                                │
│  ┌──────────────────────────────────────┐               │
│  │  CodeExecutor + Code-as-Action       │               │
│  │  LLM 生成代码 → eval() 执行 → Closure │               │
│  └──────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### 7.2 关键技术点可复用性评估（1 天）

| 技术点 | 复用度 | 复用场景 |
|--------|--------|---------|
| **Agent 框架**（[agent.py](pptagent/agent.py)） | ⭐⭐⭐⭐⭐ | 任何需要 LLM Agent 的项目，直接抽出 YAML + Jinja2 + LLM + 历史管理 |
| **AsyncLLM + Batch**（[llms.py](pptagent/llms.py)） | ⭐⭐⭐⭐⭐ | 任何高吞吐 LLM 调用场景 |
| **Code-as-Action**（[apis.py](pptagent/apis.py)） | ⭐⭐⭐⭐⭐ | LLM 操控工具/API 的场景 |
| **Retry + Feedback** | ⭐⭐⭐⭐⭐ | 任何 LLM 输出不可靠的场景 |
| **Prompt 模板管理** | ⭐⭐⭐⭐ | 任何 Prompt 密集型项目 |
| **Closure 延迟执行** | ⭐⭐⭐⭐ | 先规划再执行的事务性场景 |
| **多 Agent 流水线** | ⭐⭐⭐⭐ | 复杂任务的多阶段 LLM 协作 |
| **PPTEval 评估框架** | ⭐⭐⭐ | 生成任务的自动质量评估 |

### 7.3 终极练习：拆出 3 个独立模块（1.5 天）

从 PPTAgent 中拆出 3 个可独立使用的模块：

**模块 1：Agent 框架（~200 行）**

```python
# 目标：不依赖 PPTAgent 任何其他代码，可独立运行
# 来源：agent.py + roles/*.yaml + llms.py（精简版）

class Agent:
    def __init__(self, role_path: str, llm):
        # 加载 YAML → 设置 Jinja2 → 初始化 LLM
        ...
    def __call__(self, **kwargs) -> Any:
        # 渲染模板 → 构造消息 → LLM 调用 → 解析结果
        ...
    def retry(self, error, traceback, ...):
        # 错误信息注入 prompt → 重新调用
        ...
```

**模块 2：Code-as-Action 执行器（~150 行）**

```python
# 目标：注册任意函数 → 自动生成 API 文档 → LLM 生成调用代码 → eval 执行
# 来源：apis.py CodeExecutor + API_TYPES

class ToolExecutor:
    def register(self, func: Callable):
        """注册一个工具函数"""
        ...
    def get_tool_docs(self) -> str:
        """用 inspect 自动生成工具文档，喂给 LLM"""
        ...
    def execute(self, code: str):
        """执行 LLM 生成的工具调用代码"""
        ...
```

**模块 3：Prompt 模板管理器（~100 行）**

```python
# 目标：YAML 配置 + Jinja2 渲染 + 变量校验
# 来源：agent.py 的配置加载部分 + roles/*.yaml

class PromptManager:
    def __init__(self, templates_dir: str):
        # 加载所有 YAML 模板
        ...
    def render(self, name: str, **variables) -> str:
        # 渲染指定模板，StrictUndefined 检查缺失变量
        ...
```

---

## 附录 A：核心文件优先级

### 必读（大模型开发核心）

| 文件 | 大小 | 内容 | 阅读顺序 |
|------|------|------|---------|
| [llms.py](pptagent/llms.py) | 310 行 | LLM 封装：同步/异步/多模态/Embedding/Batch | ① 先读 |
| [agent.py](pptagent/agent.py) | 401 行 | Agent 框架：YAML+Jinja2+历史+Retry | ② 必读 |
| [apis.py](pptagent/apis.py) | 549 行 | CodeExecutor + Code-as-Action | ③ 必读 |
| [pptgen.py](pptagent/pptgen.py) | 924 行 | 多 Agent 协作流水线 | ④ 核心 |
| [roles/](pptagent/roles/) | 9 个 | Agent 角色配置（Prompt Engineering 实例） | ⑤ 参考 |
| [prompts/](pptagent/prompts/) | 16 个 | Prompt 模板库 | ⑥ 参考 |

### 选读（理解全貌）

| 文件 | 内容 | 备注 |
|------|------|------|
| [document.py](pptagent/document/document.py) | 文档结构化 | RAG 管道实现 |
| [induct.py](pptagent/induct.py) | Phase I 分析 | 图像聚类 + 内容归纳 |
| [model_utils.py](pptagent/model_utils.py) | 模型管理 | 懒加载 + 多模型切换 |
| [ppteval.py](pptagent/ppteval.py) | 评估框架 | LLM 驱动的多维评估 |

### 跳过（与大模型开发无关）

| 文件 | 原因 |
|------|------|
| [backend.py](pptagent_ui/backend.py) | FastAPI 胶水代码 |
| [Upload.vue](pptagent_ui/src/components/Upload.vue) / [Generate.vue](pptagent_ui/src/components/Generate.vue) | Vue 前端 |
| [serve_sd3.py](pptagent_ui/serve_sd3.py) | SD3 图片生成独立服务 |
| [presentation/presentation.py](pptagent/presentation/presentation.py) + [shapes.py](pptagent/presentation/shapes.py) | 纯 PPT 文件操作 |
| [docker/Dockerfile](docker/Dockerfile) | 容器配置 |

---

## 附录 B：练习项目使用指南

你的 `D:\UST\vibe\练习\居丽叶玩具项目\` 下有 13 个项目，按此顺序使用：

| 优先级 | 练习项目 | 用于阶段 | 学习价值 |
|--------|---------|---------|---------|
| 🔴 必做 | 11. Agent+RAG实现检索 | 第 3 阶段 | Agent 四模块 + RAG 检索 |
| 🔴 必做 | 12. Langchain实现RAG | 第 3 阶段 | 完整 RAG 链代码 |
| 🔴 必做 | 9. LLamaIndex 实现RAG | 第 3 阶段 | 对比不同 RAG 实现 |
| 🟡 选做 | 6. Agent 微调智能客服 | 第 4 阶段 | Agent 概念理解 |
| 🟡 选做 | 13. 多模态lora微调 | 第 3 阶段 | 多模态模型理解 |
| ⚪ 跳过 | 1-5, 7, 8, 10 | — | 纯微调项目，PPTAgent 不涉及训练 |

---

## 附录 C：按周计划

```
第 1 周           第 2 周             第 3 周             第 4 周
Python 高级       LLM API 编程        RAG 与文档处理       Agent 框架
├ asyncio        ├ OpenAI API       ├ 练习: 12→9→11    ├ agent.py 精读
├ dataclass      ├ AsyncLLM+Batch   ├ document.py      ├ AsyncAgent 对比
├ 装饰器         ├ Prompt Engineering├ 模型管理         ├ 9 个角色配置
└ TypeHints      └ 输出后处理        └ 多模态处理        └ 16 个 Prompt 模板

第 5 周           第 6 周
Code-as-Action    多 Agent 流水线 + 整合
├ apis.py 精读    ├ pptgen.py 精读
├ CodeExecutor    ├ Phase I 分析（速读）
├ Closure 模式    ├ Phase II 生成（精读）
└ 拆模块 1+2      └ 拆模块 3 + 全局架构
```

---

## 附录 D：推荐学习资源

| 主题 | 资源 |
|------|------|
| Python asyncio | [Real Python: Async IO in Python](https://realpython.com/async-io-python/) |
| OpenAI API | [OpenAI Cookbook](https://cookbook.openai.com/) |
| Jinja2 | [Jinja2 官方文档](https://jinja.palletsprojects.com/) |
| Prompt Engineering | [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/) |
| LangChain RAG | [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) |
| PPTAgent 论文 | [arXiv 2501.03936](https://arxiv.org/abs/2501.03936) |

---

## 附录 E：PPT/前端部分速览（可选）

如果你仍然想了解 PPT 操作和前端大概做什么，这是 10 分钟速览：

**PPT 操作层**（[presentation/](pptagent/presentation/)）：
- `Presentation` 封装了 `python-pptx` 的加载/保存/遍历
- `shapes.py` 定义形状体系和 Closure 延迟执行
- PPTX 层级：Presentation → Slide → Shape → Paragraph → Run
- 与 LLM 开发关系：0%，纯工具层

**Web 层**（[pptagent_ui/](pptagent_ui/)）：
- FastAPI 后端：文件上传 + WebSocket 推送进度 + 文件下载
- Vue 3 前端：2 个页面（Upload + Generate），表单 + 进度条
- 与 LLM 开发关系：0%，纯展示层
