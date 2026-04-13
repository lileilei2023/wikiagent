# WikiAgent

用 LLM 增量构建和维护个人知识库的 Agent 框架。

不同于 RAG 每次查询都从零检索原始文档，WikiAgent 让 LLM **持续维护一个结构化的 Markdown Wiki** —— 摄入新资料时自动提取实体、概念、交叉引用；查询时从已编译的知识出发，而不是从头拼凑。知识在每次摄入中累积，而非每次查询时重新推导。

## 核心操作

| 操作 | 你做什么 | WikiAgent 做什么 |
|---|---|---|
| **Ingest** | 放一份新资料（PDF/URL/文章） | 读源 → 写摘要页 → 创建/更新实体和概念页 → 刷新索引和日志 |
| **Query** | 问一个问题 | 搜索 wiki → 合成带引用的答案 → 指出知识缺口 |
| **Lint** | 说"健康检查一下" | 扫描死链/孤立页/矛盾/缺页 → 自动修小问题 → 生成报告 |

## 快速开始

### 1. 安装依赖

```bash
pip install openai pyyaml
# 可选，提升 HTML 转 Markdown 质量：
pip install html2text
# 可选，PDF 文本提取：
brew install poppler  # 提供 pdftotext
```

### 2. 配置 API

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml，填入你的 LLM API 配置
```

支持任何 OpenAI 兼容 API（OpenAI / 火山引擎 ARK / Moonshot / DeepSeek 等）。

### 3. 摄入第一个源

```bash
./start.sh
# 交互模式，输入：
# > 帮我摄入 https://example.com/some-article
```

或者把文件放到 `raw/articles/` 下：
```bash
./start.sh
# > 帮我摄入 raw/articles/my-paper.pdf
```

### 4. 查询

```bash
./start.sh
# > 基于 wiki 回答：XXX 的核心特征是什么？
```

### 5. 批量摄入

```bash
# 把多个文件放到 raw/ 下，然后：
./start.sh
# > 帮我摄入 raw/ 下所有文件
```

## 项目结构

```
wikiagent/
├── start.sh                 # 启动入口
├── config.yaml.example      # API 配置模板
├── wiki_schema.md           # Wiki 结构约定（给 agent 看）
├── wiki_main_prompt.md      # 主 agent 角色定义
├── prompts/                 # Prompt 模板
│   ├── ingest.txt
│   ├── batch_ingest.txt
│   ├── query.txt
│   └── lint.txt
├── raw/                     # 你的原始资料（只读，不进 git）
├── wiki/                    # LLM 维护的知识库
│   ├── index.md             # 全局索引
│   ├── log.md               # 操作日志
│   ├── sources/             # 源摘要页
│   ├── entities/            # 实体页（人/产品/公司/书）
│   ├── concepts/            # 概念页（想法/方法/框架）
│   └── topics/              # 主题综述页
└── wikiagent/               # Agent 引擎
    ├── agent.py             # Agent 循环
    ├── llm.py               # LLM 客户端
    ├── main.py              # CLI 入口
    ├── tools/               # 内置工具（bash/read/write/edit/grep/web_fetch/...）
    └── subagents/           # 子代理定义
        ├── wiki_ingest.py   # 摄入 agent
        ├── wiki_query.py    # 查询 agent（只读）
        └── wiki_lint.py     # 体检 agent
```

## 配合 Obsidian

`wiki/` 是标准 Markdown 目录，可以用 [Obsidian](https://obsidian.md) 直接打开：
- 内部链接用 `[[entities/foo]]` 格式，Obsidian 原生支持点击跳转
- Graph View 查看知识图谱全貌
- Backlinks 面板查看反向引用

## 源格式支持

| 格式 | 处理方式 |
|---|---|
| `.md` / `.txt` / `.html` | 直接读取 |
| `.pdf` | `pdftotext` 提取文字（需装 poppler） |
| URL | `web_fetch` 抓取并转 Markdown |
| 纯图片 PDF | 暂不支持（需 OCR） |

## 灵感来源

本项目实现了 [LLM Wiki](https://github.com/tobi/llm-wiki) 模式：LLM 做所有繁琐的知识库维护工作（摘要、交叉引用、一致性维护），人类专注于策展、提问和思考。
