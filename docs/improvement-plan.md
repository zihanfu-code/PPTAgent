# PPTAgent 优化改进计划

## 一、仓库卫生清理（高优先级，低成本）

当前仓库中提交了大量不应纳入版本控制的文件：

| 问题 | 路径 | 估计体积 |
|------|------|----------|
| node_modules 被提交 | `pptagent_ui/node_modules/` | ~430MB |
| 编译产物冗余 | `build/` | 与源码重复 |
| Jupyter 临时文件 | `pptagent/.ipynb_checkpoints/`, `pptagent_ui/.ipynb_checkpoints/` | 少量 |
| macOS 系统文件 | 根目录 `build/` `.github/` 下的 `.DS_Store` | 几KB |
| 构建产物 | `pptagent.egg-info/` | 少量 |
| Python 缓存 | `pptagent_ui/__pycache__/` | 少量 |
| 孤立文件 | 根目录 `package-lock.json`（无对应 `package.json`） | ~500KB |
| 包管理器冲突 | `pptagent_ui/.pnp.cjs` + `pptagent_ui/.pnp.loader.mjs`（Yarn PnP）与 `package-lock.json`（npm）并存 | ~1MB |

**修复方案：**

```gitignore
# 补充 .gitignore
build/
*.egg-info/
.ipynb_checkpoints/
__pycache__/
.DS_Store
node_modules/
.pnp.*
```

然后 `git rm --cached` 已追踪的这些文件。

---

## 二、同步/异步代码重复（高优先级，中工作量）

### 现状

项目中几乎每个类都有两套几乎完全一致的实现，估计 **60-70% 重复代码**：

| 同步 | 异步 |
|------|------|
| `LLM` | `AsyncLLM` |
| `Agent` | `AsyncAgent` |
| `PPTGen` | `PPTGenAsync` |
| `PPTAgent` | `PPTAgentAsync` |
| `SlideInducter` | `SlideInducterAsync` |
| `Document.from_markdown` | `Document.from_markdown_async` |
| `Media.parse` | `Media.parse_async` |
| `Table.parse` | `Table.parse_async` |
| `Media.get_caption` | `Media.get_caption_async` |
| `OutlineItem.check_images` | `OutlineItem.check_images_async` |

### 修复方案

**方案一：asyncio.to_thread 适配（轻量）**

```python
# 不改现有同步类，在需要异步的地方包装
import asyncio

async def some_async_flow():
    result = await asyncio.to_thread(sync_llm, prompt)
```

- 优点：零代码改动
- 缺点：阻塞线程池，不能利用 asyncio 并发优势

**方案二：统一到 async，同步版本用 asyncio.run 包装（推荐）**

```python
class LLM:
    def __init__(self, ...):
        self._async_client = None
    
    def __call__(self, prompt, **kwargs):
        return asyncio.run(self.__call_async__(prompt, **kwargs))
    
    async def __call_async__(self, prompt, **kwargs):
        # 真正的实现只写一次
        ...
```

- 优点：只维护一套代码
- 缺点：需要一次性的迁移工作

---

## 三、引入 LangGraph 替代手写多 Agent 编排（中优先级，中工作量）

### 现状

[pptgen.py](../pptagent/pptgen.py) 中 5 个 Agent（editor / coder / copilot / content_organizer / layout_selector）的协作流程完全由手写代码串联，包含大量重复的重试/异常处理逻辑。

### 目标架构

用 LangGraph 的 `StateGraph` 对生成流程建模：

```
                    ┌──────────────────┐
                    │   document/doc   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  content_organizer│
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌───────▼──────┐  ┌───▼──────────┐
     │  slide_1    │  │  slide_2    │  │  slide_n     │
     │  planner    │  │  planner    │  │  planner     │
     └─────┬───────┘  └──────┬──────┘  └──────┬───────┘
           │                 │                │
     ┌─────▼───────┐  ┌──────▼──────┐  ┌──────▼───────┐
     │  editor      │  │  editor     │  │  editor      │
     │  coder       │  │  coder      │  │  coder       │
     │  copilot     │  │  copilot    │  │  copilot     │
     └─────┬───────┘  └──────┬──────┘  └──────┬───────┘
           │                 │                │
           └─────────────────┼────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  finalize/export │
                    └──────────────────┘
```

### 核心代码示例

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class GenerationState(TypedDict):
    document: Document
    reference_presentations: list[Presentation]
    outline: list[OutlineItem]
    slides: Annotated[list[SlidePage], operator.add]  # reducer
    errors: list[str]

def content_organizer_node(state: GenerationState) -> GenerationState:
    """生成大纲"""
    agent = Agent("content_organizer", llm_mapping={...})
    outline = agent(state["document"])
    return {"outline": outline}

def slide_planner_node(state: GenerationState, slide_idx: int) -> GenerationState:
    """单页规划"""
    ...

def editor_coder_node(state: GenerationState) -> GenerationState:
    """编辑 + 代码执行 + copilot 自检"""
    ...

# 构建图
builder = StateGraph(GenerationState)

builder.add_node("content_organizer", content_organizer_node)
builder.add_node("slide_planner", slide_planner_node)
builder.add_node("editor_coder", editor_coder_node)

builder.set_entry_point("content_organizer")
builder.add_edge("content_organizer", "slide_planner")
builder.add_conditional_edges(
    "editor_coder",
    should_retry,          # 需要重试 → 回到 editor_coder
    {
        "retry": "editor_coder",
        "next": "slide_planner",  # 下一张
        "done": END,
    }
)

graph = builder.compile()
```

### 收益

1. **消除手写重试/异常逻辑** — LangGraph 内置 `Command(resume=...)` 和 checkpoint
2. **可观测性** — LangGraph 自带 tracing/debug
3. **天然解决同步/异步双写** — LangGraph 原生 async
4. **Human-in-the-loop** — 内置支持，方便后续做交互式 PPT 生成
5. **简历价值** — "自研 Agent 基础设施 + LangGraph 有状态编排" 比纯手写或纯调包都有说服力

---

## 四、安全修复（高优先级，低工作量）

### 4.1 `eval()` 执行 LLM 生成代码

[apis.py:186](../pptagent/apis.py#L186)

```python
# 当前代码
eval(line, {}, {func: partial_func})
```

**风险**：LLM 输出不可控时可能执行任意表达式。

**修复方案**：手写一个简单的 DSL 解析器，仅支持已知的 5 个 API 函数调用：

```python
import ast

def safe_execute(line: str, func_map: dict) -> Any:
    tree = ast.parse(line, mode='eval')
    if not isinstance(tree.body, ast.Call):
        raise ValueError(f"Expected function call, got {type(tree.body)}")
    func_name = tree.body.func.id
    if func_name not in func_map:
        raise ValueError(f"Unknown API: {func_name}, allowed: {list(func_map.keys())}")
    args = [ast.literal_eval(arg) for arg in tree.body.args]
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in tree.body.keywords}
    return func_map[func_name](*args, **kwargs)
```

### 4.2 脆弱的路径操作

[llms.py:12](../pptagent/llms.py#L12) 中 `sys.path.append('..')` — 删除即可，项目已有正确的包结构。

---

## 五、依赖与配置修复（中优先级，低工作量）

| 问题 | 修复 |
|------|------|
| `requirements.txt` 与 `pyproject.toml` 重复维护 | 删除 `requirements.txt`，只保留 `pyproject.toml` |
| `pyupgrade --py39-plus` 与 Python 3.11+ 不匹配 | 改为 `--py311-plus` |
| `peft` 依赖未在源码中使用 | 从 `pyproject.toml` 移除 |
| `socksio` 依赖未在源码中使用 | 从 `pyproject.toml` 移除 |
| 版本约束过老（2025 年初） | 逐步升级 `transformers`、`marker-pdf` 等，跑一次完整测试 |

---

## 六、`utils.py` 拆分（低优先级，中工作量）

当前 [utils.py](../pptagent/utils.py) 约 620 行，混入了多个不相关的职责。建议拆分为：

```
pptagent/utils/
├── __init__.py        # 统一导出
├── logging.py         # get_logger
├── config.py          # Config 类
├── text.py            # edit_distance, get_json_from_response
├── image.py           # ppt_to_images, markdown_table_to_image, WMF 转换
├── path.py            # package_join, pjoin, pexists 等别名
└── retry.py           # tenacity_decorator
```

---

## 七、其他小修复

1. **[agent.py:46](../pptagent/agent.py#L46)** — `Turn.__eq__` 使用 `self is other` 与默认行为相同，无实际意义
2. **[agent.py:128-133](../pptagent/agent.py#L128-L133)** — `get_history` 中语义相似度筛选逻辑死代码
3. **[agent.py:106](../pptagent/agent.py#L106)** — monkey-patching `self.llm.__call__` 影响同一 LLM 实例在其他 Agent 中的行为
4. **[llms.py:148](../pptagent/llms.py#L148)** — `content.startswith("You are")` 启发式检测 system message，改用显式的 role 标记
5. **注释语言不一致** — `pptgen.py` 和 `induct.py` 的异步版本是中文注释，同步版本是英文注释

---

## 建议执行顺序

```
第1天: 仓库清理 + .gitignore + 修复 eval/sys.path → 提一个 PR
第2-3天: 同步/异步统一 + utils 拆分 + 小 bug 修复 → 提一个 PR
第4-5天: LangGraph 迁移多 Agent 编排 → 提一个 PR
第6天: 依赖清理 + pyupgrade 修复 → 提一个 PR
```

第 1 步和第 5 步的改动最小但收益最大，建议优先做。
