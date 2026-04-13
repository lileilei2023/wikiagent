from __future__ import annotations

import json
import time
from typing import Optional
from openai import OpenAI, APITimeoutError


class LLMClient:
    """Handles LLM API communication with streaming and tool-use parsing."""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def stream_chat(self, messages: list[dict], tools: Optional[list[dict]] = None,
                    first_token_timeout: int = 60, max_first_token_retries: int = 3,
                    first_token_retry_delay: int = 10) -> dict:
        """
        Send a streaming chat request and return parsed result.

        Returns:
            {
                "assistant_message": dict,     # The full assistant message for appending to messages
                "content": str | None,         # Text content
                "tool_calls": list[dict],      # [{id, name, arguments(str)}]
                "finish_reason": str | None,
                "usage": dict | None,
                "timing": dict,                # Timing information
            }
        """
        request_start_time = time.time()
        first_token_time = None
        stream = None
        first_chunk = None

        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # First token retry loop
        for ft_attempt in range(max_first_token_retries):
            try:
                stream = self.client.chat.completions.create(**kwargs, timeout=first_token_timeout)
                first_chunk = next(stream, None)
                first_token_time = time.time()
                print(f"First token received in {first_token_time - request_start_time:.2f} seconds.")
                break

            except APITimeoutError as e:
                print(f"First token timeout ({first_token_timeout}s). Retrying (Attempt {ft_attempt + 1}/{max_first_token_retries})...")
                if ft_attempt == max_first_token_retries - 1:
                    raise Exception(f"First token timeout after {max_first_token_retries} attempts.")
                time.sleep(first_token_retry_delay)
                continue

        # If we are here, we have stream and first_chunk
        content_parts: list[str] = []
        tc_map: dict[int, dict] = {}
        finish_reason = None
        usage_info = None

        chunks = [first_chunk]
        for chunk in stream:
            chunks.append(chunk)

        for chunk in chunks:
            if not chunk:
                continue

            if not chunk.choices:
                if hasattr(chunk, "usage") and chunk.usage:
                    usage_info = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
                continue

            delta = chunk.choices[0].delta

            if delta.content:
                print(delta.content, end="", flush=True)
                content_parts.append(delta.content)

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tc_map:
                        tc_map[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc_delta.id:
                        tc_map[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tc_map[idx]["name"] = tc_delta.function.name
                            print(f"\n🔧 Tool call: {tc_delta.function.name}", flush=True)
                        if tc_delta.function.arguments:
                            tc_map[idx]["arguments"] += tc_delta.function.arguments

            fr = chunk.choices[0].finish_reason
            if fr:
                finish_reason = fr

        request_end_time = time.time()

        if content_parts:
            print()

        content = "".join(content_parts) or None
        tool_calls_list = []
        if tc_map:
            for idx in sorted(tc_map.keys()):
                tc = tc_map[idx]
                tool_calls_list.append(
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["arguments"],
                        },
                    }
                )
                print(f"   Args: {tc['arguments']}", flush=True)

        assistant_msg = {"role": "assistant", "content": content}
        if tool_calls_list:
            assistant_msg["tool_calls"] = tool_calls_list

        function_calls = [
            {"id": tc["id"], "name": tc["function"]["name"], "arguments": tc["function"]["arguments"]}
            for tc in tool_calls_list
        ]

        if usage_info:
            print(f"  [tokens] prompt={usage_info['prompt_tokens']} completion={usage_info['completion_tokens']}")

        timing = {
            "request_start": request_start_time,
            "first_token": first_token_time,
            "request_end": request_end_time,
            "duration_first_token": first_token_time - request_start_time if first_token_time else None,
            "duration_total": request_end_time - request_start_time,
        }

        return {
            "assistant_message": assistant_msg,
            "content": content,
            "tool_calls": function_calls,
            "finish_reason": finish_reason,
            "usage": usage_info,
            "timing": timing,
        }
