import html as html_module
import re
import urllib.error
import urllib.request

from wikiagent.tool import Tool


_USER_AGENT = "Mozilla/5.0 (compatible; PyAgent-WebFetch/1.0)"


def _strip_html(html: str) -> str:
    """Stdlib-only fallback: strip tags and collapse whitespace."""
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"</(p|div|h[1-6]|li|tr|section|article)[^>]*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", "", html)
    html = html_module.unescape(html)
    html = re.sub(r"\n\s*\n+", "\n\n", html)
    html = re.sub(r"[ \t]+", " ", html)
    return html.strip()


def _html_to_markdown(html: str) -> str:
    """Try html2text, then markdownify, then fall back to plain text stripping."""
    try:
        import html2text  # type: ignore

        h = html2text.HTML2Text()
        h.body_width = 0
        h.ignore_images = False
        h.ignore_links = False
        return h.handle(html)
    except ImportError:
        pass
    try:
        from markdownify import markdownify as md  # type: ignore

        return md(html, heading_style="ATX")
    except ImportError:
        pass
    return _strip_html(html)


def _detect_charset(content_type: str, raw_bytes: bytes) -> str:
    m = re.search(r"charset=([\w-]+)", content_type, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(rb'<meta[^>]+charset=["\']?([\w-]+)', raw_bytes[:2048], flags=re.IGNORECASE)
    if m:
        try:
            return m.group(1).decode("ascii")
        except UnicodeDecodeError:
            pass
    return "utf-8"


def _execute_web_fetch(url: str, max_chars: int = 50000, raw: bool = False) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        return "[Error] URL must start with http:// or https://"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            final_url = resp.geturl()
            content_type = resp.headers.get("Content-Type", "")
            raw_bytes = resp.read()
    except urllib.error.HTTPError as e:
        return "[Error] HTTP {}: {}".format(e.code, e.reason)
    except urllib.error.URLError as e:
        return "[Error] URLError: {}".format(e.reason)
    except Exception as e:
        return "[Error] {}".format(e)

    charset = _detect_charset(content_type, raw_bytes)
    try:
        text = raw_bytes.decode(charset, errors="replace")
    except LookupError:
        text = raw_bytes.decode("utf-8", errors="replace")

    looks_like_html = (
        "text/html" in content_type.lower()
        or text.lstrip()[:15].lower().startswith(("<!doctype", "<html"))
    )

    if raw or not looks_like_html:
        output = text
    else:
        output = _html_to_markdown(text)

    header = "[{}] ({} bytes, content-type: {})".format(
        final_url, len(raw_bytes), content_type or "unknown"
    )
    if len(output) > max_chars:
        truncated = output[:max_chars]
        omitted = len(output) - max_chars
        return "{}\n\n{}\n\n[...TRUNCATED, {} more chars omitted. Call again with a larger max_chars if needed.]".format(
            header, truncated, omitted
        )
    return "{}\n\n{}".format(header, output)


def make_web_fetch_tool() -> Tool:
    return Tool(
        name="web_fetch",
        description=(
            "Fetch a URL and return its content. HTML pages are auto-converted to Markdown "
            "for easier downstream processing. Use this to ingest articles, blog posts, "
            "documentation, or any web page into your knowledge base. "
            "Output is truncated at `max_chars` (default 50000) to avoid context bloat. "
            "Set `raw=true` to skip HTML-to-Markdown conversion (useful for JSON APIs or when "
            "you need the original markup)."
        ),
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL starting with http:// or https://.",
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return (default: 50000).",
                },
                "raw": {
                    "type": "boolean",
                    "description": "If true, skip HTML-to-Markdown conversion (default: false).",
                },
            },
            "required": ["url"],
        },
        execute=lambda url, max_chars=50000, raw=False: _execute_web_fetch(url, max_chars, raw),
    )
