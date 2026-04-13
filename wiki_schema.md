# Wiki Schema — 约定文件

This file is the source of truth for how the wiki is structured. Both the main agent and the `wiki_ingest` / `wiki_query` / `wiki_lint` subagents should read this before making decisions.

## Directory layout

```
raw/                         # IMMUTABLE — original source material
  articles/                  # Web articles, blog posts (.md / .html / .txt)
  papers/                    # Academic papers, reports (.pdf)
  books/                     # Book content, one subdir per book, one file per chapter
    <book-name>/
      ch01.md
      ch02.md
  notes/                     # Meeting notes, chat exports, journal entries, podcast transcripts
  assets/                    # Images, data files, attachments (NOT standalone sources)

wiki/                        # LLM-maintained knowledge base
  index.md                   # Catalog of all wiki pages (one-line summary each)
  log.md                     # Append-only chronological log
  sources/<slug>.md          # One page per ingested source
  entities/<slug>.md         # People, products, companies, books, places, organizations
  concepts/<slug>.md         # Ideas, methods, frameworks, theories, techniques
  topics/<slug>.md           # Broader topic syntheses that span multiple entities/concepts
  _lint_report.md            # Most recent lint report (overwritten each run)
```

All page filenames are lowercase-kebab-case: `memex.md`, `vannevar-bush.md`, `personal-knowledge-management.md`.

## Page types and required structure

### `sources/<slug>.md`
```markdown
---
title: <source title>
url_or_path: <original location>
ingested: YYYY-MM-DD
type: article | paper | book-chapter | video-transcript | chat-log | image | other
---

## Summary
- 3-10 bullet points capturing the key claims or takeaways.

## Entities / concepts mentioned
- [[entities/foo]] — brief note on how this source relates
- [[concepts/bar]]

## Notable quotes / data
> Direct quotes with attribution if useful.

## Open questions
- Anything this source raised but didn't answer.
```

### `entities/<slug>.md`
```markdown
---
type: person | product | company | book | place | organization
---

## What it is
One paragraph.

## Key facts
- Bullet list of stable facts drawn from the wiki's sources.

## Relationships
- Related to [[entities/...]] via ...
- Associated with [[concepts/...]]

## Mentioned in
- [[sources/...]] — one line on the angle
- [[sources/...]]

## Contradictions
(Only if different sources say different things. Cite each side.)
```

### `concepts/<slug>.md`
```markdown
## Definition
One paragraph.

## Origin / history
Where it came from.

## How it works / key ideas
Bulleted or prose.

## Relationships
- Generalizes / specializes [[concepts/...]]
- Applied in [[topics/...]]

## Mentioned in
- [[sources/...]]

## Contradictions
```

### `topics/<slug>.md`
```markdown
## Overview
One paragraph framing the topic.

## Current thesis
What we currently believe about this topic, synthesized from sources.
Update this as new sources come in — don't delete the old thesis, record the change.

## Key entities
- [[entities/...]]

## Key concepts
- [[concepts/...]]

## Sources informing this
- [[sources/...]]

## Open questions
```

### `index.md`
```markdown
# Wiki Index

_Last updated: YYYY-MM-DD_

## Sources (N)
- [[sources/foo]] — one-line summary
- [[sources/bar]] — one-line summary

## Entities (N)
- [[entities/alice]] — one-line summary

## Concepts (N)
- [[concepts/memex]] — one-line summary

## Topics (N)
- [[topics/personal-knowledge-management]] — one-line summary
```

### `log.md`
Append-only. Each entry starts with `## [YYYY-MM-DD] <op> | <title>` so it's grep-able.
```markdown
## [2026-04-11] ingest | Vannevar Bush: As We May Think
- Source: sources/as-we-may-think.md
- Created: entities/vannevar-bush.md, concepts/memex.md
- Updated: topics/personal-knowledge-management.md
- Notes: Coined the Memex concept. Seminal reference for LLM Wiki idea.

## [2026-04-12] query | What is the relationship between Memex and modern RAG?
- Pages read: concepts/memex.md, concepts/rag.md, topics/personal-knowledge-management.md
- Answer saved to: (none — just discussed)

## [2026-04-15] lint | 3 issues found, 2 auto-fixed
- Report: wiki/_lint_report.md
```

## Linking conventions

- Internal links use `[[path/slug]]` (Obsidian-compatible), NOT `[title](path.md)`.
- When referring to a page the first time on a new page, use its slug so backlinks work.
- If you mention an entity/concept that doesn't have a page yet, and it feels important, CREATE a stub page for it during ingest. A stub is better than a dangling name.

## Workflow invariants (all agents must respect)

1. **`raw/` is immutable.** Never write to or modify anything under `raw/`.
2. **Never silently overwrite.** If new information contradicts existing content, add to a `## Contradictions` section. Don't delete the old claim.
3. **Always update `index.md`** when creating or renaming a page.
4. **Always append to `log.md`** for any operation that touches the wiki.
5. **Prefer `edit` over `write`** for existing pages — search/replace preserves context better than full rewrites.
6. **Slugs are stable.** Once a page has a slug, don't rename it casually — it breaks links. If a rename is necessary, update all backlinks and note the rename in the log.

## Growth hints

- If you find yourself making many pages of the same new kind (e.g. `experiments/`, `decisions/`, `people/` split from `entities/`), propose a new category and update this schema file.
- If a page grows past ~500 lines, consider splitting it into a topic page + multiple concept pages.
- If `index.md` grows past ~300 lines, consider adding a secondary `index-<category>.md` per category.

## Source format handling

The `wiki_ingest` subagent decides how to read a source based on file extension:

| Extension | Method |
|---|---|
| `.md`, `.txt` | `read` tool directly |
| `.html` | `read` tool directly (LLM can parse HTML) |
| `.pdf` | `bash` → try `pdftotext <path> -`, then `python3 -c "import fitz; ..."`, then `marker_single` |
| URL (`http://...`) | `web_fetch` tool |
| Image (`.png`, `.jpg`, etc.) | Record path in source page; no OCR (yet) |
| Other | Skip with a warning |

For PDFs, the user should have at least one of these installed:
- `poppler` (`brew install poppler` → provides `pdftotext`)
- `pymupdf` (`pip install pymupdf` → provides `fitz`)

For books or very long PDFs, split into chapters first (one file per chapter under `raw/books/<name>/`), then ingest each chapter as a separate source.

## `raw/` organization conventions

Users drop files into subdirectories under `raw/` by category:
- `raw/articles/` — web articles, blog posts, newsletters (use Obsidian Web Clipper or save-as-markdown)
- `raw/papers/` — academic papers, reports, whitepapers (PDF)
- `raw/books/<book-name>/` — one directory per book, one file per chapter
- `raw/notes/` — personal notes, meeting transcripts, journal entries, chat exports
- `raw/assets/` — images, data files, diagrams (NOT standalone sources; these support other sources)

The `raw/assets/` directory is special: files there won't be ingested as sources, but can be referenced from source pages or wiki pages. During batch ingest, `raw/assets/` is skipped.

This is a recommendation, not a hard rule. Any file under `raw/` (except `raw/assets/`) is fair game for ingestion regardless of which subdirectory it's in.

## Agent-specific behaviors

- **`wiki_ingest`** — reads ONE source, writes/updates 5-15 pages, always touches `index.md` + `log.md`. Has `bash` for PDF text extraction.
- **`wiki_query`** — READ-ONLY. Reads index, reads pages, synthesizes a cited answer. Never writes.
- **`wiki_lint`** — reads everything, writes `_lint_report.md`, may auto-fix index drift and add missing cross-references, never deletes pages.
