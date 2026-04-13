# WikiAgent

[中文版](README_zh.md)

An agent framework that uses LLMs to incrementally build and maintain a personal knowledge base.

Unlike RAG, which retrieves raw documents from scratch on every query, WikiAgent lets an LLM **continuously maintain a structured Markdown Wiki** — automatically extracting entities, concepts, and cross-references when ingesting new material; answering queries from compiled knowledge rather than reassembling from scratch. Knowledge accumulates with each ingestion, not re-derived on every query.

## Core Operations

| Operation | You do | WikiAgent does |
|---|---|---|
| **Ingest** | Drop in a new source (PDF/URL/article) | Read source → write summary page → create/update entity & concept pages → refresh index & log |
| **Query** | Ask a question | Search wiki → synthesize cited answer → flag knowledge gaps |
| **Lint** | Say "health check" | Scan dead links/orphans/contradictions/missing pages → auto-fix minor issues → generate report |

## Quick Start

### 1. Install Dependencies

```bash
pip install openai pyyaml
# Optional, better HTML-to-Markdown conversion:
pip install html2text
# Optional, PDF text extraction:
brew install poppler  # provides pdftotext
```

### 2. Configure API

```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your LLM API credentials
```

Supports any OpenAI-compatible API (OpenAI / Volcano Engine ARK / Moonshot / DeepSeek, etc.).

### 3. Ingest Your First Source

```bash
./start.sh
# Interactive mode, type:
# > Ingest https://example.com/some-article
```

Or place files under `raw/articles/`:
```bash
./start.sh
# > Ingest raw/articles/my-paper.pdf
```

### 4. Query

```bash
./start.sh
# > Based on the wiki, answer: What are the key features of XXX?
```

### 5. Batch Ingest

```bash
# Place multiple files under raw/, then:
./start.sh
# > Ingest all files under raw/
```

## Project Structure

```
wikiagent/
├── start.sh                 # Entry point
├── config.yaml.example      # API config template
├── wiki_schema.md           # Wiki structure conventions (for the agent)
├── wiki_main_prompt.md      # Main agent role definition
├── prompts/                 # Prompt templates
│   ├── ingest.txt
│   ├── batch_ingest.txt
│   ├── query.txt
│   └── lint.txt
├── raw/                     # Your source materials (read-only, not in git)
├── wiki/                    # LLM-maintained knowledge base
│   ├── index.md             # Global index
│   ├── log.md               # Operation log
│   ├── sources/             # Source summary pages
│   ├── entities/            # Entity pages (people/products/companies/books)
│   ├── concepts/            # Concept pages (ideas/methods/frameworks)
│   └── topics/              # Topic overview pages
└── wikiagent/               # Agent engine
    ├── agent.py             # Agent loop
    ├── llm.py               # LLM client
    ├── main.py              # CLI entry point
    ├── tools/               # Built-in tools (bash/read/write/edit/grep/web_fetch/...)
    └── subagents/           # Subagent definitions
        ├── wiki_ingest.py   # Ingest agent
        ├── wiki_query.py    # Query agent (read-only)
        └── wiki_lint.py     # Lint agent
```

## Obsidian Integration

`wiki/` is a standard Markdown directory that can be opened directly with [Obsidian](https://obsidian.md):
- Internal links use `[[entities/foo]]` format, natively supported by Obsidian
- Graph View for visualizing the full knowledge graph
- Backlinks panel for exploring reverse references

## Supported Source Formats

| Format | Processing |
|---|---|
| `.md` / `.txt` / `.html` | Direct read |
| `.pdf` | Text extraction via `pdftotext` (requires poppler) |
| URL | Fetch & convert to Markdown via `web_fetch` |
| Image-only PDF | Not yet supported (requires OCR) |

## Inspiration

This project implements [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): the LLM handles all the tedious knowledge base maintenance (summarization, cross-referencing, consistency), while humans focus on curation, questioning, and thinking.
