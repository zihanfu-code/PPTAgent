# PPTAgent 系统学习路径

> 目标：完全掌握 PPTAgent 项目架构，并能拆解复用核心技术到自己的项目
> 基础：有 Python 基础，不熟悉异步/高级特性
> 总时长：约 7-8 周（每天 3-4 小时）

---

## 目录

- [第 0 阶段：环境准备](#第-0-阶段环境准备)
- [第 1 阶段：Python 高级特性](#第-1-阶段python-高级特性)
- [第 2 阶段：LLM API 编程基础](#第-2-阶段llm-api-编程基础)
- [第 3 阶段：RAG 与文档处理](#第-3-阶段rag-与文档处理)
- [第 4 阶段：Agent 架构深入](#第-4-阶段agent-架构深入)
- [第 5 阶段：PPT 文件操作](#第-5-阶段ppt-文件操作)
- [第 6 阶段：核心流水线：Phase I 分析](#第-6-阶段核心流水线phase-i-分析)
- [第 7 阶段：核心流水线：Phase II 生成](#第-7-阶段核心流水线phase-ii-生成)
- [第 8 阶段：Web 框架与前端](#第-8-阶段web-框架与前端)
- [第 9 阶段：架构整合与复用](#第-9-阶段架构整合与复用)

---

## 第 0 阶段：环境准备

**时长**：1 天 | **目标**：能跑通测试，IDE 能跳转代码

### 0.1 安装 PPTAgent

```bash
# 方式一：pip 安装（只读代码，不需要 GPU）
pip install git+https://github.com/icip-cas/PPTAgent.git

# 方式二：clone 源码（可以修改代码）
git clone https://github.com/icip-cas/PPTAgent.git
cd PPTAgent
pip install -e .
```

### 0.2 配置 IDE

- 用 VS Code 打开项目根目录
- 安装 Python、Vue 插件
- 验证：点击 [agent.py](pptagent/agent.py) 中的 `class Agent`，能跳转到定义

### 0.3 跑通测试（验证安装成功）

```bash
pytest -v -n 8 test/
```

---

## 第 1 阶段：Python 高级特性

**时长**：1 周 | **目标**：能顺畅阅读 PPTAgent 中所有 Python 语法

> PPTAgent 大量使用了 Python 高级特性，不掌握它们 = 读代码如读天书。

### 1.1 asyncio 异步编程（2 天）

**为什么重要**：整个项目异步化。`AsyncAgent`、`AsyncLLM`、`asyncio.TaskGroup` 无处不在。

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `async/await` 基本语法 | [llms.py:229-300](pptagent/llms.py#L229-L300) `AsyncLLM.__call__()` |
| `asyncio.TaskGroup` 并行执行 | [document.py:344-363](pptagent/document/document.py#L344-L363) 同时解析多个文档块 |
| `asyncio.gather` 并行等待 | [document.py:538-540](pptagent/document/document.py#L538-L540) 并行获取多个 image embedding |
| `@asynccontextmanager` 上下文管理器 | [backend.py:62-65](pptagent_ui/backend.py#L62-L65) FastAPI 生命周期管理 |
| `asyncio.create_task` 创建任务 | [induct.py](pptagent/induct.py) `SlideInducterAsync` 多处使用 |

**实践练习**：写一个简化版 `AsyncLLM`，支持：
1. `async def __call__(self, prompt)` 异步调用
2. 用 `asyncio.TaskGroup` 同时发 5 个请求
3. 用 `asyncio.gather` 收集所有结果

---

### 1.2 dataclasses 数据类（1 天）

**为什么重要**：项目中几乎所有核心数据结构都用 `@dataclass` 定义，避免大量样板代码。

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `@dataclass` 基本用法 | [agent.py](pptagent/agent.py) `Turn` 类 — 自动生成 `__init__`、`__repr__` |
| `field(default=...)` 默认值 | [document.py:114-118](pptagent/document/document.py#L114-L118) `Document` — `sections`、`metadata` 字段 |
| `__post_init__` 初始化后处理 | [document.py:120-121](pptagent/document/document.py#L120-L121) `Document.__post_init__` 自动设置日期 |
| `asdict()` 转字典 | [document.py:395-396](pptagent/document/document.py#L395-L396) `Document.to_dict()` |
| 嵌套 dataclass | [document.py:440-457](pptagent/document/document.py#L440-L457) `OutlineItem` |

**实践练习**：把 [document.py](pptagent/document/document.py) 的 `Document`、`Section`、`OutlineItem` 三个类的定义抄写一遍并加注释。

---

### 1.3 装饰器（1 天）

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `@tenacity` 重试装饰器 | [utils.py:26](pptagent/utils.py#L26) `tenacity_decorator` — 失败等 3s 重试最多 5 次 |
| `@staticmethod` / `@classmethod` | [document.py:153-206](pptagent/document/document.py#L153-L206) `Document._parse_chunk` 类方法 |
| `@property` 属性 | [document.py:431-436](pptagent/document/document.py#L431-L436) `Document.metainfo`、`Document.subsections` |

**实践练习**：自己写一个 `@retry(max_attempts=3, wait_seconds=2)` 装饰器，能装饰任意函数并自动重试。

---

### 1.4 Type Hints 类型标注（1 天）

| 知识点 | PPTAgent 代码示例 |
|--------|------------------|
| `Optional[X]` | 几乎所有函数参数 `Optional[str] = None` |
| `dict[str, list[str]]` 嵌套泛型 | [document.py:400-401](pptagent/document/document.py#L400-L401) `retrieve(indexs: dict[str, list[str]])` |
| `Callable` 可调用对象 | [apis.py](pptagent/apis.py) `API_TYPES.all_funcs() -> dict[str, callable]` |
| Union 类型 | [pptgen.py:463](pptagent/pptgen.py#L463) 多处 |

**练习**：给 [agent.py](pptagent/agent.py) 的一个方法补全 type hints，验证 mypy 不报错。

---

### 阶段检验

- [ ] 能解释 `await` 为什么释放 GIL 但不等于多线程
- [ ] 能用 `@dataclass` 定义包含 3 个字段的类并正确使用
- [ ] 能手写一个重试装饰器

---

## 第 2 阶段：LLM API 编程基础

**时长**：1.5 周 | **目标**：能独立写一个调 LLM API + 自动重试 + JSON 解析的 Python 类

### 2.1 OpenAI Compatible API（3 天）

**对应代码**：[pptagent/llms.py](pptagent/llms.py)（约 310 行，建议逐行读 3 遍）

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `OpenAI()` 客户端初始化 | [llms.py:30-40](pptagent/llms.py#L30-L40) | `api_key`、`base_url`、SOCKS 代理 |
| `chat.completions.create()` | [llms.py:50-80](pptagent/llms.py#L50-L80) | `model`、`messages`、`response_format`、`stream` |
| 多模态调用（图片 base64） | [llms.py:100-150](pptagent/llms.py#L100-L150) | PIL Image → base64 → `image_url` 格式 |
| Embeddings API | [llms.py:160-190](pptagent/llms.py#L160-L190) | `embeddings.create()` → `torch.Tensor` |
| Images API（文生图） | [llms.py:200-240](pptagent/llms.py#L200-L240) | `images.generate()` → `b64_json` |
| JSON Mode（结构化输出） | [llms.py:65-70](pptagent/llms.py#L65-L70) | `response_format={"type": "json_object"}` |
| 连接测试 | [llms.py:250-260](pptagent/llms.py#L250-L260) | `test_connection()` 发送一个简短请求验证 API 可用 |

**实践练习**：基于 `openai` 库，自己封装一个 `MyLLM` 类，要求：
- `__call__(prompt, system=None)` 方法返回文本
- `__call__(image, prompt)` 支持图片输入（多模态）
- `get_embedding(text)` 返回 embedding 向量
- 连接失败自动重试 3 次

---

### 2.2 AsyncLLM 异步封装（2 天）

**对应代码**：[pptagent/llms.py:229-310](pptagent/llms.py#L229-L310)

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `AsyncOpenAI()` vs `OpenAI()` | [llms.py:229-240](pptagent/llms.py#L229-L240) | 异步客户端初始化 |
| Batch 批量请求 (`oaib.Auto`) | [llms.py:234-240](pptagent/llms.py#L234-L240) | `oaib.Auto` 自动将多个请求合并批量提交 |
| 异步多模态 | [llms.py:270-290](pptagent/llms.py#L270-L290) | async 版本的多模态调用 |
| 异步 Embedding | [llms.py:295-310](pptagent/llms.py#L295-L310) | async 版本的 embedding |

**核心理解**：为什么用 `AsyncLLM`？
- FastAPI 是异步框架，同步 LLM 调用会阻塞事件循环
- `oaib.Auto` 可以在同一个 event loop 中批量调度多个请求

**实践练习**：对比 [llms.py](pptagent/llms.py) 中 `LLM.__call__`（同步）和 `AsyncLLM.__call__`（异步）的代码差异，标注出所有不同的地方。

---

### 2.3 Prompt Engineering（2 天）

**练习项目**：不需要（直接用 PPTAgent 的 prompt 文件学习）

| 知识点 | PPTAgent 代码位置 | 详细说明 |
|--------|------------------|---------|
| Jinja2 模板渲染 | [agent.py:55-62](pptagent/agent.py#L55-L62) | `Environment(undefined=StrictUndefined)` 确保所有变量都有值 |
| YAML 角色配置 | [agent.yaml](pptagent/roles/agent.yaml) | `system_prompt` + `template` + `jinja_args` 三段式配置 |
| 结构化 Prompt 设计 | [prompts/ppteval_content.txt](pptagent/prompts/ppteval_content.txt) | 看真实 prompt 如何定义输入输出 schema |
| Markdown→HTML Prompt | [prompts/caption.txt](pptagent/prompts/caption.txt) | 看如何要求 LLM 处理特定格式 |

**9 个 Agent 角色一览**：

| 角色文件 | 使用的模型 | 作用 |
|---------|-----------|------|
| [planner.yaml](pptagent/roles/planner.yaml) | language | 规划每页 PPT 要表达的内容 |
| [doc_extractor.yaml](pptagent/roles/doc_extractor.yaml) | language/vision | 从文档提取结构化内容 |
| [schema_extractor.yaml](pptagent/roles/schema_extractor.yaml) | language | 从参考 PPT 提取内容 schema |
| [layout_selector.yaml](pptagent/roles/layout_selector.yaml) | vision | 根据内容选择合适的布局模板 |
| [content_organizer.yaml](pptagent/roles/content_organizer.yaml) | language | 组织每页 PPT 的具体内容 |
| [coder.yaml](pptagent/roles/coder.yaml) | language | 生成 API 调用序列（代码） |
| [editor.yaml](pptagent/roles/editor.yaml) | vision | 检查生成结果并修正 |
| [agent.yaml](pptagent/roles/agent.yaml) | language | 通用内容处理助手 |
| [copilot.yaml](pptagent/roles/copilot.yaml) | language | 辅助决策和验证 |

**实践练习**：选 3 个 prompt 模板（如 `ppteval_content.txt`、`caption.txt`、`agent.yaml`），逐行分析：
- 哪些是指令？
- 哪些是约束？
- 输入变量在代码中怎么传入的？（搜索 `render(` 调用点）

---

### 2.4 LLM 输出后处理（1 天）

| 知识点 | PPTAgent 代码位置 | 详细说明 |
|--------|------------------|---------|
| `json_repair` 修复坏 JSON | [utils.py:14](pptagent/utils.py#L14) | LLM 经常输出缺括号的 JSON，`json_repair` 自动修复 |
| 多策略 JSON 提取 | [utils.py](pptagent/utils.py) `get_json_from_response()` | 先直接 `json.loads` → 失败则正则提取 → 失败则 `json_repair` |
| `tiktoken` Token 计数 | [agent.py:6](pptagent/agent.py#L6) | 精确计算 prompt 长度，超出限制时截断历史消息 |

---

### 阶段检验

- [ ] 能独立写一个 `MyLLM` 类，封装 chat + embedding + image generation
- [ ] 能读懂 [llms.py](pptagent/llms.py) 每一行代码
- [ ] 能说清楚为什么 PPTAgent 需要 AsyncLLM 而不是直接用同步 LLM

---

## 第 3 阶段：RAG 与文档处理

**时长**：1.5 周 | **目标**：理解文档解析→切分→嵌入→检索的完整 RAG 管道

> 这是 PPTAgent 的"数据输入层"。PDF 文档经过解析→结构化→检索→填充到 PPT 中。

### 3.1 预热：用练习项目建立 RAG 直觉（3 天）

#### 步骤 1：LangChain RAG（1 天）

**练习项目**：`12. Langchain实现RAG/`

| 文件 | 对应知识点 |
|------|-----------|
| [rag.py](D:/UST/vibe/练习/居丽叶玩具项目/12.%20Langchain实现RAG/rag.py) | 完整的 RAG 流程代码 |

**学习路径**：

| 步骤 | 知识点 | 对应 PPTAgent 代码 |
|------|--------|-------------------|
| ① `TextLoader` 加载文档 | 文档加载器模式 | [marker-pdf 转换](pptagent/model_utils.py#L58-63) PDF→Markdown |
| ② `RecursiveCharacterTextSplitter` 切分 | 语义分块策略 | [document.py:35-78](pptagent/document/document.py#L35-L78) `split_markdown_by_headings` |
| ③ `HuggingFaceBgeEmbeddings` 嵌入 | 文本向量化 | [llms.py:160-190](pptagent/llms.py#L160-L190) `get_embedding()` |
| ④ `Chroma.from_documents()` 向量存储 | 向量数据库 | PPTAgent 直接用 `torch.cosine_similarity` 在内存中计算，不用外部 DB |
| ⑤ `similarity_search()` 检索 | 相似度检索 | [document.py:412-416](pptagent/document/document.py#L412-L416) `Document.find_caption()` |
| ⑥ `LLMChain` + `PromptTemplate` 生成 | 检索增强生成 | [agent.py](pptagent/agent.py) Agent 的 prompt + LLM 调用 |

**关键对比**：

```
LangChain RAG:  文档 → TextSplitter → Embedding → ChromaDB → 相似度搜索 → LLM 回答
PPTAgent RAG:   PDF → marker-pdf → Markdown → 标题分块 → Embedding → cosine_similarity → 内容填充
```

---

#### 步骤 2：LlamaIndex RAG（1 天）

**练习项目**：`9. LLamaIndex 实现RAG/`

| 文件 | 对应知识点 |
|------|-----------|
| `LLamIndex 实现 RAG.ipynb` | LlamaParse PDF 解析 + Markdown 输出 |

**核心对比**：

| LlamaIndex 做法 | PPTAgent 做法 |
|----------------|--------------|
| `LlamaParse` 云服务解析 PDF → Markdown | `marker-pdf` 本地模型解析 PDF → Markdown |
| `SimpleDirectoryReader` 批量加载 | `parse_pdf()` 单文件解析 |
| `VectorStoreIndex` 向量索引 | 直接用 `torch.cosine_similarity` 计算 |

---

#### 步骤 3：Agent + RAG 融合（1 天）

**练习项目**：`11. Agent +RAG实现检索/`

| 文件 | 对应知识点 |
|------|-----------|
| `11 Agent +RAG实现检索.ipynb` | Agent 架构 + RAG 检索 |

**核心概念**：

```
Agent 模块         → PPTAgent 中的对应
├── Planning      → Planner Agent (pptgen.py:179)
├── Memory        → Turn 历史管理 (agent.py:90-140)
├── Tools         → CodeExecutor API 函数 (apis.py:533)
└── Executor      → CodeExecutor.execute_actions() (apis.py:127)
```

---

### 3.2 PPTAgent 文档处理管线（4 天）

#### 3.2.1 PDF → Markdown 解析（1 天）

**核心文件**：[pptagent/model_utils.py](pptagent/model_utils.py)

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| `ModelManager` 模型管理器 | [model_utils.py:23-78](pptagent/model_utils.py#L23-L78) | 管理 3 个 LLM + image_model + marker_model |
| `marker_model` 懒加载 | [model_utils.py:58-63](pptagent/model_utils.py#L58-L63) | `create_model_dict()` 创建 PDF 解析模型（只在首次调用时加载） |
| `parse_pdf()` PDF 解析 | [model_utils.py](pptagent/model_utils.py) `parse_pdf` 函数 | 调用 marker-pdf 将 PDF 转为 Markdown |
| `PdfConverter` 转换器 | [model_utils.py:10-12](pptagent/model_utils.py#L10-L12) | marker-pdf 的核心转换类 |

#### 3.2.2 Markdown → Document 结构化（2 天）

**核心文件**：[pptagent/document/document.py](pptagent/document/document.py)（约 550 行，最重要）

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| Markdown 标题提取 | [document.py:292-294](pptagent/document/document.py#L292-L294) | `re.findall(r"^#+\s+.*", markdown_content)` 正则提取所有标题 |
| 标题对齐（LLM） | [document.py:293-295](pptagent/document/document.py#L293-L295) | 用 LLM 调整标题结构，合并冗余标题 |
| 按标题分块 | [document.py:35-78](pptagent/document/document.py#L35-L78) | `split_markdown_by_headings` — 将 Markdown 按标题切块，合并小段 |
| 段落分类 | [document.py:81-111](pptagent/document/document.py#L81-L111) | `to_paragraphs` — 文本/表格/图片分类 |
| 并行解析块 | [document.py:344-364](pptagent/document/document.py#L344-L364) | `asyncio.TaskGroup` 并行解析 + 生成摘要 |
| 关联媒体 | [document.py:227](pptagent/document/document.py#L227) | `link_medias` — 将表格/图片关联到最近的段落 |
| 表格/图片 caption | [document.py:174-179](pptagent/document/document.py#L174-L179) | 用 LLM/Vision Model 为媒体生成标题 |
| 重试机制 | [document.py:181-206](pptagent/document/document.py#L181-L206) | 解析失败→错误注入 prompt→重试最多 3 次 |
| Document 检索 | [document.py:398-415](pptagent/document/document.py#L398-L415) | `retrieve()` 按 Section/SubSection 两级索引查找内容 |
| OutlineItem 规划 | [document.py:459-469](pptagent/document/document.py#L459-L469) | `retrieve()` 检索 + header/content/images 组装 |

**实践练习**：找一段 PDF 文档（或直接用项目自带的 `runs/` 下的测试 PDF），用手动代码跑一遍：
```python
# 1. marker-pdf 解析 PDF → Markdown
# 2. Document.from_markdown() 结构化
# 3. Document.retrieve() 检索特定章节
```

#### 3.2.3 多模态处理（1 天）

**核心文件**：[pptagent/multimodal.py](pptagent/multimodal.py)

| 知识点 | 说明 |
|--------|------|
| `ImageLabler` | 提取参考 PPT 中的图片，用 Vision Model 生成 caption |
| 图片统计 | 收集图片的大小、位置、出现频率，辅助布局选择 |

---

### 阶段检验

- [ ] 能画出 PDF → Markdown → Document → Section → SubSection 的完整数据流
- [ ] 能解释 `split_markdown_by_headings` 的分块逻辑
- [ ] 能解释为什么用编辑距离 (`edit_distance`) 而不是字符串相等来匹配标题

---

## 第 4 阶段：Agent 架构深入

**时长**：1 周 | **目标**：能复刻一个简化的 Agent 框架（YAML 配置 + Jinja2 模板 + LLM 调用 + 历史管理）

> 练习项目 `11. Agent+RAG` 让你懂了 Agent 概念，现在深入 PPTAgent 的实现。

### 4.1 Agent 核心类（2 天）

**核心文件**：[pptagent/agent.py](pptagent/agent.py)（401 行）

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `Turn` 数据类 | [agent.py:19-30](pptagent/agent.py#L19-L30) | 一轮对话的数据结构：`prompt`、`response`、`info` |
| YAML 角色加载 | [agent.py:40-55](pptagent/agent.py#L40-L55) | 从 `roles/{name}.yaml` 加载 `system_prompt`、`template`、`jinja_args` |
| Jinja2 `StrictUndefined` | [agent.py:55-65](pptagent/agent.py#L55-L65) | 变量未定义时抛异常而非静默失败 |
| Token 计数 | [agent.py:70-85](pptagent/agent.py#L70-L85) | `tiktoken` 计算所有消息的 token 数 |
| 历史管理 | [agent.py:88-140](pptagent/agent.py#L88-L140) | 保留最近 N 轮 + 语义相似历史（Embedding + Cosine Similarity） |
| `Agent.__call__` | [agent.py:145-200](pptagent/agent.py#L145-L200) | 同步 Agent 的核心执行流程 |
| `Agent.retry` | [agent.py:200-230](pptagent/agent.py#L200-L230) | 错误 + traceback 注入 prompt 重试 |
| LLM 映射 | [agent.py:40-50](pptagent/agent.py#L40-L50) | `llm_mapping` 字典：同一 Agent 可调用多个不同模型 |

**Agent 执行流程（逐行对照）**：

```
1. 加载 YAML 配置（system_prompt + template + jinja_args）
2. 过滤用户输入中 template 不需要的变量
3. 用 Jinja2 渲染 template → 最终 prompt
4. 构造 messages: [system_prompt] + [历史消息] + [当前 prompt]
5. Token 计数 → 超限则截断历史
6. 调用 LLM（同步 or 异步）
7. 解析返回值 → 存入 Turn 历史
8. 如需重试：错误信息 + traceback → 重新渲染 prompt → 回到第 6 步
```

### 4.2 AsyncAgent 对比（1 天）

**核心文件**：[pptagent/agent.py:240-401](pptagent/agent.py#L240-L401)

**同步 vs 异步对比表**：

| 同步 `Agent` | 异步 `AsyncAgent` | 差异说明 |
|-------------|-------------------|---------|
| `LLM` | `AsyncLLM` | 底层 LLM 客户端不同 |
| `for` 循环顺序执行 | `asyncio.TaskGroup` 并行 | 并行获取多个相似历史的 embedding |
| `def __call__` | `async def __call__` | 调用时用 `await` |
| `def retry` | `async def retry` | 重试也要异步 |

**实践练习**：将 `Agent` 和 `AsyncAgent` 的 `__call__` 方法并排对照，标注出所有 `async/await` 带来的差异点。

### 4.3 9 个 Agent 角色配置（2 天）

**目录**：[pptagent/roles/](pptagent/roles/)

逐个角色分析，关注每个角色的：
- `system_prompt`：定义了什么角色身份？
- `template`：输入什么变量？要求输出什么？
- `jinja_args`：哪些变量是必须的？
- `use_model`：用的是 language model 还是 vision model？

**角色协作关系图**：

```
Phase I（分析）:
  doc_extractor ──→ schema_extractor ──→ layout_selector
       │                    │
       └── 提取文档内容      └── 提取 PPT 结构

Phase II（生成）:
  planner ──→ content_organizer ──→ layout_selector ──→ coder ──→ editor
    │              │                      │               │          │
   规划结构      组织内容             选择布局         生成代码    审查修正
                                                         │
                                                    copilot（辅助）
```

### 4.4 Prompt 模板分析（2 天）

**目录**：[pptagent/prompts/](pptagent/prompts/)（16 个模板文件）

| 模板文件 | 被谁调用 | 作用 |
|---------|---------|------|
| `heading_extract.txt` | [document.py:25](pptagent/document/document.py#L25) | 用 LLM 调整 Markdown 标题结构 |
| `section_summary.txt` | [document.py:27](pptagent/document/document.py#L27) | 生成文档块摘要 |
| `merge_metadata.txt` | [document.py:22](pptagent/document/document.py#L22) | 合并各块的元数据 |
| `caption.txt` | multimodal.py | 为图片生成标题 |
| `markdown_table_caption.txt` | document/element.py | 为表格生成标题 |
| `category_split.txt` | [induct.py](pptagent/induct.py) | 分类幻灯片（封面/目录/内容/结束） |
| `ask_category.txt` | [induct.py](pptagent/induct.py) | 询问幻灯片的类别含义 |
| `lengthy_rewrite.txt` | pptgen.py | 压缩过长内容 |
| `ppteval_content.txt` | [ppteval.py](pptagent/ppteval.py) | 评估内容准确性 |
| `ppteval_style.txt` | [ppteval.py](pptagent/ppteval.py) | 评估视觉风格 |
| `ppteval_coherence.txt` | [ppteval.py](pptagent/ppteval.py) | 评估逻辑连贯性 |
| `ppteval_describe_content.txt` | [ppteval.py](pptagent/ppteval.py) | 描述幻灯片内容 |
| `ppteval_describe_style.txt` | [ppteval.py](pptagent/ppteval.py) | 描述视觉风格 |
| `ppteval_extract.txt` | [ppteval.py](pptagent/ppteval.py) | 提取结构信息 |
| `markdown_image_caption.txt` | document/element.py | 为 Markdown 图片生成 caption |
| `table_parsing.txt` | document/element.py | 解析表格结构 |

### 阶段检验

- [ ] 能手写一个 `Agent` 类的简化版（YAML 加载 + Jinja2 渲染 + LLM 调用）
- [ ] 能画出 9 个 Agent 角色之间的调用关系图
- [ ] 能解释 `StrictUndefined` 在 Jinja2 中的作用

---

## 第 5 阶段：PPT 文件操作

**时长**：1 周 | **目标**：能用 python-pptx 创建/修改/保存 PPTX 文件

### 5.1 python-pptx 基础（2 天）

**练习项目**：不需要，直接对着 PPTAgent 代码学。

**核心文件**：[pptagent/presentation/](pptagent/presentation/)

| 知识点 | 代码位置 |
|--------|---------|
| `Presentation` 加载/保存 | [presentation.py:1-80](pptagent/presentation/presentation.py#L1-L80) |
| `SlidePage` 幻灯片 | [presentation.py:80-200](pptagent/presentation/presentation.py#L80-L200) |
| `ShapeElement` 形状元素 | [shapes.py:1-200](pptagent/presentation/shapes.py#L1-L200) |
| `Picture` 图片 | [shapes.py:200-300](pptagent/presentation/shapes.py#L200-L300) |
| 形状遍历 | [presentation.py](pptagent/presentation/presentation.py) `iter_shapes()` |
| 坐标计算 | [utils.py](pptagent/utils.py) `parse_groupshape()` |

**PPTX 内部层级**（必须背下来）：

```
Presentation (pptx.Presentation)
  └── Slide (pptx.slide.Slide)
        └── Shape (pptx.shapes.base.BaseShape)
              ├── GroupShape（组合形状）
              │     └── Shape（子形状）
              ├── Picture（图片）
              ├── Placeholder（占位符）
              │     └── TextFrame
              │           └── Paragraph（段落）
              │                 └── Run（文本运行，最小文本单元）
              └── GraphicFrame（图表/表格框架）
```

### 5.2 PPTX XML 底层操作（1 天）

| 知识点 | 代码位置 |
|--------|---------|
| `lxml.etree` 解析 | [shapes.py:7](pptagent/presentation/shapes.py#L7) |
| `pptx.oxml.parse_xml` | [shapes.py](pptagent/presentation/shapes.py) 多处 |
| 幻灯片 XML 结构 | `SlideLayout`、`SlideMaster` 的 XML 表示 |
| 图片关系管理 | `SlidePart.relate_to()` 添加图片关系 |

**实践练习**：用 python-pptx 打开一个 PPTX，打印所有 Slide 的所有 Shape 的类型和文本内容。

### 5.3 Closure 延迟执行模式（2 天）

**核心文件**：[pptagent/presentation/shapes.py](pptagent/presentation/shapes.py)（1267 行）

这是 PPTAgent 最精妙的设计之一：

```python
# 操作先记录为闭包（Closure），不立即执行
# 最后统一在真实 PPTX 对象上执行

class ClosureType(Enum):
    REPLACE_TEXT = auto()
    CLONE_PARAGRAPH = auto()
    DELETE_SPAN = auto()
    # ...

class Closure:
    type: ClosureType
    func: Callable  # 闭包函数
    args: tuple     # 参数
```

**为什么这样设计？**
- Agent 生成的代码操作的是"逻辑幻灯片"（可能不存在真实 PPTX 对象）
- Closure 把操作推迟到真实对象准备好时执行
- 可以在执行前验证所有操作的合法性

### 5.4 API 函数与 CodeExecutor（2 天）

**核心文件**：[pptagent/apis.py](pptagent/apis.py)（549 行）

| 知识点 | 代码位置 | 详细说明 |
|--------|---------|---------|
| `API_TYPES` 枚举 | [apis.py:533-541](pptagent/apis.py#L533-L541) | 5 个可用 API 函数 |
| 函数文档自动生成 | [apis.py:84-125](pptagent/apis.py#L84-L125) | `get_apis_docs()` — 用 `inspect` 读取 `__doc__` 和 `__signature__` |
| `CodeExecutor.execute_actions` | [apis.py:127-203](pptagent/apis.py#L127-L203) | `eval()` 执行 LLM 生成的代码 |
| Markdown→HTML 渲染 | [apis.py:29-41](pptagent/apis.py#L29-L41) | `SlideRenderer` — 自定义 `mistune` 渲染器 |
| 文本样式继承 | [apis.py:236-280](pptagent/apis.py#L236-L280) | `TextBlock.build_run()` — bold/italic/color/strikethrough |
| 段落克隆 | [apis.py](pptagent/apis.py) `clone_paragraph` | 复制段落（保留样式）并赋予新 ID |
| 图片替换 | [apis.py](pptagent/apis.py) `replace_image` | 替换幻灯片中的图片 |

**5 个 API 函数**：

| 函数 | 作用 | 参数 |
|------|------|------|
| `replace_span(slide_idx, para_idx, span_idx, text)` | 替换文本内容 | 幻灯片/段落/文本索引 + 新文本 |
| `clone_paragraph(slide_idx, para_idx)` | 克隆段落 | 幻灯片/段落索引 |
| `del_span(slide_idx, para_idx, span_idx)` | 删除文本 | 幻灯片/段落/文本索引 |
| `replace_image(slide_idx, image_path)` | 替换图片 | 幻灯片索引 + 图片路径 |
| `del_image(slide_idx)` | 删除图片 | 幻灯片索引 |

---

### 阶段检验

- [ ] 能用 python-pptx 遍历一个 PPTX 的所有形状并打印文本
- [ ] 能解释 Closure 模式解决了什么问题
- [ ] 能解释 `eval()` 执行 LLM 生成代码的安全风险

---

## 第 6 阶段：核心流水线 Phase I — 分析

**时长**：1 周 | **目标**：理解 PPTAgent 如何从参考 PPT 中学习布局和内容模式

### 6.1 PPT → 图片管道（1 天）

**对应代码**：

| 步骤 | 代码位置 | 工具 |
|------|---------|------|
| PPTX → PDF | [utils.py](pptagent/utils.py) `ppt_to_images_async()` | `subprocess` 调用 `soffice --headless` |
| PDF → 图片 | [utils.py:18](pptagent/utils.py#L18) | `pdf2image.convert_from_path()` |
| WMF → JPG | [utils.py](pptagent/utils.py) `wmf_to_images()` | WMF 矢量图转换 |

### 6.2 布局归纳 layout_induct()（2 天）

**核心文件**：[pptagent/induct.py:154-180](pptagent/induct.py#L154-L180) `layout_induct()`

```python
布局归纳流程：
1. PPT 每一页 → 图片
2. ViT 模型提取每页图像嵌入 (image_model from model_utils.py)
3. 计算幻灯片之间的图像余弦相似度矩阵
4. 基于相似度进行聚类（agglomerative clustering）
5. 识别布局模板类型：封面/目录/内容/结束
```

| 知识点 | 代码位置 |
|--------|---------|
| `image_model` ViT 加载 | [model_utils.py:52-56](pptagent/model_utils.py#L52-L56) |
| 图像嵌入提取 | [model_utils.py](pptagent/model_utils.py) `get_image_embedding()` |
| 相似度矩阵 | [model_utils.py](pptagent/model_utils.py) `images_cosine_similarity()` |
| 聚类 | [model_utils.py](pptagent/model_utils.py) `get_cluster()` |
| 分类（封面/内容/结束） | [induct.py:181-196](pptagent/induct.py#L181-L196) `category_split()` |

### 6.3 内容归纳 content_induct()（2 天）

**核心文件**：[pptagent/induct.py:233-268](pptagent/induct.py#L233-L268) `content_induct()`

```python
内容归纳流程：
1. 对每种布局类型 → 选中代表幻灯片
2. LLM 分析幻灯片的文本结构
3. 提取内容 schema：slide_title、main_content、logo、decoration 等
4. 验证和修正 schema（_fix_schema）
```

| 知识点 | 代码位置 |
|--------|---------|
| `content_induct` | [induct.py:233-268](pptagent/induct.py#L233-L268) |
| `_fix_schema` | [induct.py:247-270](pptagent/induct.py#L247-L270) |
| Async 版本 | [induct.py:272-428](pptagent/induct.py#L272-L428) `SlideInducterAsync` |

### 6.4 SlideInducter vs SlideInducterAsync 对比（2 天）

**核心文件**：[pptagent/induct.py:96-428](pptagent/induct.py#L96-L428)

| 同步版本 `SlideInducter` | 异步版本 `SlideInducterAsync` |
|--------------------------|------------------------------|
| `def __init__(self, llm, image_model)` | `def __init__(self, async_llm, image_model)` |
| `def layout_induct(self)` 顺序执行 | `async def layout_induct(self)` 并行聚类 |
| `def content_induct(self)` 顺序处理每个布局 | `async def content_induct(self)` 并行分析多个布局 |
| `def category_split(self)` LLM 调用 | `async def category_split(self)` async LLM |

**实践练习**：找 5-10 页 PPT，手动运行 `layout_induct()` 的简化版——用 ViT 提取嵌入 → 计算相似度 → 看聚类结果。

---

## 第 7 阶段：核心流水线 Phase II — 生成

**时长**：1.5 周 | **目标**：理解从文档大纲到最终 PPTX 的完整生成流程

### 7.1 架构总览（1 天）

**核心文件**：[pptagent/pptgen.py](pptagent/pptgen.py)（924 行，最重要的文件）

类继承体系：

```
PPTGen (ABC)              ← 抽象基类，定义完整生成流程
├── PPTAgent              ← 同步实现
└── PPTGenAsync           ← 异步基类
    └── PPTAgentAsync     ← 异步实现（实际使用的）
```

### 7.2 生成主流程 generate_pres()（2 天）

**代码位置**：[pptgen.py:375-433](pptagent/pptgen.py#L375-L433) `PPTGenAsync.generate_pres()`

```python
主流程（逐方法对照）：
1. generate_outline()        → Planner Agent 规划每页内容
2. _add_functional_layouts() → 插入封面/目录/结束页
3. _fix_outline()            → Editor Agent 修正大纲
4. generate_slide() × N      → 逐页生成幻灯片内容
5. 保存 PPTX
```

| 子步骤 | 代码位置 | 调用的 Agent |
|--------|---------|-------------|
| `generate_outline()` | [pptgen.py:434-454](pptagent/pptgen.py#L434-L454) | planner |
| `_add_functional_layouts()` | [pptgen.py:262-282](pptagent/pptgen.py#L262-L282) | 预定义模板 |
| `_fix_outline()` | [pptgen.py:464-498](pptagent/pptgen.py#L464-L498) | editor |
| `generate_slide()` | [pptgen.py:719-760](pptagent/pptgen.py#L719-L760) | 多个 Agent |

### 7.3 单页 slide 生成（3 天）

**代码位置**：[pptgen.py:719-760](pptagent/pptgen.py#L719-L760) `PPTAgentAsync.generate_slide()`

```
每页幻灯片生成流程：

① _select_layout()      → layout_selector Agent 选择布局模板
    输入：当前页 purpose + 内容
    输出：最合适的 layout schema

② _generate_content()   → content_organizer Agent 组织内容
    输入：schema + outline + document 内容 + 图片信息
    输出：结构化的内容安排

③ _generate_commands()  → coder Agent 生成 API 调用序列
    输入：schema + 内容 + 当前 slide HTML 结构 + api_docs
    输出：replace_span(0, 0, 0, "标题") / clone_paragraph(1, 0) 等

④ _edit_slide()         → CodeExecutor 执行 API 调用
    eval(replace_span(0, 0, 0, "标题"))
    修改真实 PPTX 对象

⑤ _collect_history()    → 收集生成历史，辅助后续 slide
```

**逐方法详解**：

| 方法 | 代码位置 | 调用的 Agent |
|------|---------|-------------|
| `_select_layout()` | [pptgen.py:762-803](pptagent/pptgen.py#L762-L803) | layout_selector |
| `_generate_content()` | [pptgen.py:804-823](pptagent/pptgen.py#L804-L823) | content_organizer |
| `_generate_commands()` | [pptgen.py:861-924](pptagent/pptgen.py#L861-L924) | coder |
| `_edit_slide()` | [pptgen.py:825-859](pptagent/pptgen.py#L825-L859) | CodeExecutor |

### 7.4 FunctionalLayouts 预设模板（1 天）

**代码位置**：[pptgen.py:23-37](pptagent/pptgen.py#L23-L37)

```python
class FunctionalLayouts(Enum):
    OPENING = auto()         # 封面："{title}\n{author}\n{date}"
    TOC = auto()             # 目录："Table of Contents\n{contents}"
    SECTION_OUTLINE = auto() # 章节过渡
    ENDING = auto()          # 结束页："Thank you"
```

### 7.5 PPTGen → PPTAgent 差异（2 天）

| 抽象方法 `PPTGen` | 具体实现 `PPTAgent` | 说明 |
|-------------------|-------------------|------|
| `generate_slide()` | [pptgen.py:514-548](pptagent/pptgen.py#L514-L548) | PPTAgent 实现了 4 步 slide 生成 |
| `_select_layout()` | [pptgen.py:550-590](pptagent/pptgen.py#L550-L590) | 根据 content 选择合适的 layout |
| `_generate_content()` | [pptgen.py:592-620](pptagent/pptgen.py#L592-L620) | 组织页面内容 |
| `_edit_slide()` | [pptgen.py:621-652](pptagent/pptgen.py#L621-L652) | 生成和编辑 slide |
| `_generate_commands()` | [pptgen.py:654-704](pptagent/pptgen.py#L654-L704) | 生成 API 调用序列 |

---

### 阶段检验

- [ ] 能画出 Phase II 的完整 5 步流程（outline → layout → content → commands → edit）
- [ ] 能说出 `PPTGen(ABC)` → `PPTGenAsync` → `PPTAgentAsync` 的三层继承作用

---

## 第 8 阶段：Web 框架与前端

**时长**：3 天 | **目标**：理解 FastAPI + Vue 3 如何驱动整个系统

### 8.1 FastAPI 后端（2 天）

| 知识点 | 代码位置 | 说明 |
|--------|---------|------|
| Lifespan 管理 | [backend.py:62-65](pptagent_ui/backend.py#L62-L65) | 启动时测试模型连接 |
| CORS 配置 | [backend.py:71-77](pptagent_ui/backend.py#L71-L77) | 允许任意来源跨域 |
| 文件上传 API | [backend.py](pptagent_ui/backend.py) `POST /api/upload` | multipart/form-data 接收 PPTX + PDF |
| WebSocket 推送 | [backend.py:153-210](pptagent_ui/backend.py#L153-L210) | `/wsapi/{task_id}` 实时推送进度 |
| 下载 API | [backend.py](pptagent_ui/backend.py) `GET /api/download` | 返回生成的 PPTX 文件 |
| 反馈 API | [backend.py](pptagent_ui/backend.py) `POST /api/feedback` | 收集用户反馈 |
| `ProgressManager` | [backend.py:82-152](pptagent_ui/backend.py#L82-L152) | 5 阶段进度追踪 + 状态消息 |
| SD3 服务 | [serve_sd3.py](pptagent_ui/serve_sd3.py) | 独立的 SD3 文生图服务 |

### 8.2 Vue 3 前端（1 天）

| 文件 | 功能 |
|------|------|
| [Upload.vue](pptagent_ui/src/components/Upload.vue) | 上传 PPTX/PDF、选择页数、跳转生成页 |
| [Generate.vue](pptagent_ui/src/components/Generate.vue) | WebSocket 进度条、下载链接、反馈提交 |
| [router/index.js](pptagent_ui/src/router/index.js) | Vue Router 页面路由 |

前端代码量很小（2 个组件），主要是表单 + WebSocket 进度显示，快速过一遍即可。

---

## 第 9 阶段：架构整合与复用

**时长**：1 周 | **目标**：能画出完整架构图，能拆解复用核心技术

### 9.1 全局数据流图（1 天）

画出完整数据流，标注每个数据结构的来源和去向：

```
输入：
  PDF 文件 ──→ marker-pdf ──→ Markdown
  PPTX 文件 ──→ LibreOffice ──→ 幻灯片图片

Phase I（分析）：
  幻灯片图片 ──→ ViT Embedding ──→ 聚类 ──→ 布局模板
  布局模板 + 文本 ──→ LLM ──→ Content Schema

Phase II（生成）：
  Markdown ──→ Document ──→ OutlineItem[]
  OutlineItem[] + Schema ──→ Planner Agent ──→ 每页规划
  每页规划 ──→ Content Organizer ──→ 结构化内容
  结构化内容 ──→ Layout Selector ──→ 布局选择
  布局 + 内容 ──→ Coder Agent ──→ API 调用序列
  API 调用序列 ──→ CodeExecutor ──→ 修改 PPTX

输出：
  PPTX 文件
```

### 9.2 关键技术点可复用性评估（2 天）

| 技术点 | 可复用程度 | 复用方式 |
|--------|-----------|---------|
| **Agent 框架**（[agent.py](pptagent/agent.py)） | ⭐⭐⭐⭐⭐ | 直接抽出 YAML 配置 + Jinja2 模板 + LLM 调用的 Agent 框架，可用于任何需要 LLM Agent 的项目 |
| **Code-as-Action**（[apis.py](pptagent/apis.py)） | ⭐⭐⭐⭐⭐ | LLM 生成可执行代码而非描述的模式，适用于任何"LLM 操控工具"的场景 |
| **异步 LLM 封装**（[llms.py](pptagent/llms.py)） | ⭐⭐⭐⭐⭐ | `AsyncLLM` + `oaib.Auto` 批量调度，适用于任何需要高吞吐 LLM 调用的项目 |
| **Closure 延迟执行**（[shapes.py](pptagent/presentation/shapes.py)） | ⭐⭐⭐⭐ | 先记录操作后执行，适用于任何"先规划再执行"的场景 |
| **Retry + Feedback**（[agent.py](pptagent/agent.py)） | ⭐⭐⭐⭐ | 错误信息注入 prompt 让 LLM 自我纠正，适用于任何 LLM 输出不可靠的场景 |
| **两阶段流水线**（[induct.py](pptagent/induct.py) + [pptgen.py](pptagent/pptgen.py)） | ⭐⭐⭐ | 分析 → 生成的模式可应用于其他格式转换任务（Word→PPT、Excel→图表等） |
| **PPTEval 评估**（[ppteval.py](pptagent/ppteval.py)） | ⭐⭐⭐ | 多维评估框架可应用于其他生成任务的质量评估 |
| **Prompt 模板管理**（[prompts/](pptagent/prompts/) + [roles/](pptagent/roles/)） | ⭐⭐⭐ | YAML + Jinja2 的 prompt 管理方式可应用于任何 prompt 密集型项目 |

### 9.3 可调参数清单（1 天）

| 参数 | 位置 | 默认值 | 说明 |
|------|------|--------|------|
| 重试次数 | [document.py:182](pptagent/document/document.py#L182) | 3 | 文档解析失败重试 |
| 重试等待 | [utils.py:26](pptagent/utils.py#L26) | 3s | Tenacity 重试间隔 |
| 最小分块大小 | [document.py:39](pptagent/document/document.py#L39) | 64 字符 | Markdown 分块最小阈值 |
| 最大上下文大小 | [document.py:81](pptagent/document/document.py#L81) | 256 字符 | 表格/图片的上下文窗口 |
| 相似度阈值 | [document.py:477](pptagent/document/document.py#L477) | `sim_bound` | 标题匹配的编辑距离阈值 |
| 历史保留数 | [agent.py](pptagent/agent.py) | `max_history` | Agent 保留最近 N 轮对话 |
| Token 限制 | [agent.py:70-85](pptagent/agent.py#L70-L85) | 模型 context 长度 | 超出截断历史消息 |

### 9.4 自己动手：拆解一个简化版（3 天）

**终极练习**：从 PPTAgent 中拆出 3 个独立可复用的模块：

1. **Agent 框架**（200 行以内）
   - 从 [agent.py](pptagent/agent.py) 抽出核心逻辑
   - YAML 加载 → Jinja2 渲染 → LLM 调用 → 结果解析
   - 支持 retry

2. **Code-as-Action 执行器**（150 行以内）
   - 从 [apis.py](pptagent/apis.py) 抽出 CodeExecutor
   - 注册自定义 API 函数
   - `eval()` 执行 + 安全检查

3. **Prompt 模板管理器**（100 行以内）
   - 从 [roles/](pptagent/roles/) 和 [prompts/](pptagent/prompts/) 抽出
   - YAML 配置加载
   - Jinja2 模板渲染
   - 变量校验（StrictUndefined）

---

## 附录 A：核心文件按难度分级

### 入门级（先读这些）
| 文件 | 大小 | 原因 |
|------|------|------|
| [agent.yaml](pptagent/roles/agent.yaml) | 73 行 | YAML 配置，直观 |
| [Upload.vue](pptagent_ui/src/components/Upload.vue) | 241 行 | Vue 表单，简单 |
| [Generate.vue](pptagent_ui/src/components/Generate.vue) | 158 行 | Vue 进度条，简单 |
| [serve_sd3.py](pptagent_ui/serve_sd3.py) | ~80 行 | 独立服务，结构清晰 |

### 进阶级
| 文件 | 大小 | 原因 |
|------|------|------|
| [llms.py](pptagent/llms.py) | 310 行 | LLM 封装，逐行清晰 |
| [model_utils.py](pptagent/model_utils.py) | ~200 行 | 模型管理，结构清晰 |
| [document.py](pptagent/document/document.py) | 550 行 | 文档处理核心，逻辑密集 |
| [agent.py](pptagent/agent.py) | 401 行 | Agent 框架核心 |

### 资深级
| 文件 | 大小 | 原因 |
|------|------|------|
| [apis.py](pptagent/apis.py) | 549 行 | CodeExecutor + API 函数 + Markdown 渲染 |
| [induct.py](pptagent/induct.py) | 430 行 | Phase I 布局+内容归纳 |
| [shapes.py](pptagent/presentation/shapes.py) | 1267 行 | 形状体系 + Closure，最大文件 |
| [pptgen.py](pptagent/pptgen.py) | 924 行 | Phase II 生成流程，最复杂 |
| [backend.py](pptagent_ui/backend.py) | ~360 行 | Web 框架 + 任务管理 |

---

## 附录 B：按周计划日历

```
第 1 周       第 2 周         第 3 周         第 4 周
Python高级     LLM API编程     RAG与文档处理    Agent架构深入
├ asyncio     ├ OpenAI API   ├ LangChain RAG ├ Agent核心类
├ dataclass   ├ AsyncLLM     ├ LlamaIndex    ├ AsyncAgent对比
├ 装饰器      ├ Prompt工程   ├ Agent+RAG     ├ 9个角色配置
└ TypeHints   └ 后处理       └ 文档管线      └ Prompt模板

第 5 周       第 6 周         第 7 周         第 8 周
PPT文件操作    Phase I 分析   Phase II 生成    Web + 整合
├ python-pptx ├ PPT→图片     ├ 架构总览      ├ FastAPI
├ XML底层     ├ 布局归纳     ├ 生成主流程    ├ Vue3前端
├ Closure     ├ 内容归纳     ├ slide生成     ├ 架构图
└ CodeExecutor└ 同步vs异步   └ Functional    └ 拆解复用
```

---

## 附录 C：推荐外部学习资源

| 主题 | 资源 |
|------|------|
| Python asyncio | [Real Python: Async IO in Python](https://realpython.com/async-io-python/) |
| OpenAI API | [OpenAI Cookbook](https://cookbook.openai.com/) |
| python-pptx | [python-pptx 官方文档](https://python-pptx.readthedocs.io/) |
| FastAPI | [FastAPI 官方教程](https://fastapi.tiangolo.com/tutorial/) |
| Jinja2 | [Jinja2 官方文档](https://jinja.palletsprojects.com/) |
| Prompt Engineering | [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/) |
| LangChain RAG | [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) |
| PPTAgent 论文 | [arXiv 2501.03936](https://arxiv.org/abs/2501.03936) |
