#!/usr/bin/env python3
"""Local web application and KoboldCpp gateway for the Sydney experience."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
from typing import Any


APP_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = APP_DIR / "public"
ASSETS_DIR = APP_DIR / "assets"
CONTENT_DIR = APP_DIR / "content"
PERSONA_PATH = APP_DIR.parent / "persona" / "sydney_story.json"
CHINESE_PERSONA_PATH = APP_DIR.parent / "persona" / "sydney_app_prompt_zh.txt"
MAX_REQUEST_BYTES = 1_000_000
MAX_HISTORY_MESSAGES = 24
MAX_MESSAGE_CHARS = 4_000
MAX_PROMPT_CHARS = 18_000

GENERIC_CHAT_PHRASES = (
    "听起来",
    "我能理解",
    "那一定很难受",
    "你愿意告诉我吗",
    "无论如何我都在",
)
ALLOWED_AFFINITY_BANDS = {"distant", "familiar", "close", "bonded"}
ALLOWED_TRUST_BANDS = {"guarded", "opening", "trusted"}
ALLOWED_VISUAL_STATES = {"calm", "attentive", "joy", "vulnerable", "intimate"}


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))


def explicitly_requests_english(text: str) -> bool:
    return bool(
        re.search(
            r"(?:请|必须|只)?用(?:英文|英语)(?:回答|回复|说|写)|reply\s+(?:only\s+)?in\s+english",
            text,
            flags=re.IGNORECASE,
        )
    )


def should_reply_chinese(messages: list[dict[str, str]]) -> bool:
    latest = messages[-1]["content"]
    if explicitly_requests_english(latest):
        return False
    if contains_cjk(latest):
        return True
    if len(re.findall(r"[A-Za-z]", latest)) >= 4:
        return False
    for message in reversed(messages[:-1]):
        if message["role"] != "user":
            continue
        content = message["content"]
        if explicitly_requests_english(content):
            return False
        if contains_cjk(content):
            return True
        if len(re.findall(r"[A-Za-z]", content)) >= 4:
            return False
    return False


def chinese_ratio(text: str) -> float:
    meaningful = re.findall(r"[A-Za-z\u3400-\u4dbf\u4e00-\u9fff]", text)
    if not meaningful:
        return 0.0
    chinese = sum(1 for char in meaningful if contains_cjk(char))
    return chinese / len(meaningful)


def sanitize_reply(text: str) -> str:
    reply = str(text).strip()
    for marker in ("### Instruction:", "\nInstruction:", "### Response:"):
        if marker in reply:
            reply = reply.split(marker, 1)[0].strip()
    reply = re.sub(r"^(?:Sydney|悉尼|符)\s*[:：]\s*", "", reply, flags=re.IGNORECASE)
    return reply.strip()


def sanitize_chat_reply(text: str) -> str:
    reply = re.sub(r"<think>[\s\S]*?</think>", "", str(text), flags=re.IGNORECASE).strip()
    reply = re.sub(r"^<think>[\s\S]*$", "", reply, flags=re.IGNORECASE).strip()
    return sanitize_reply(reply)


def build_chinese_system(
    persona: str,
    messages: list[dict[str, str]],
    conversation_context: dict[str, Any] | None = None,
    reply_chinese: bool = True,
) -> str:
    """Add a small turn-specific guard without replacing the durable persona."""
    recent_assistant = [
        message["content"] for message in messages[-8:] if message["role"] == "assistant"
    ]
    repeated = [phrase for phrase in GENERIC_CHAT_PHRASES if any(phrase in item for item in recent_assistant)]
    guidance = [
        "本轮先处理用户最新消息中的具体新信息、纠正和形式要求，再决定语气。",
        "不要自动描写月光、窗边、蓝发、指尖或靠近；这些不是默认开场。",
        "回答必须推进当前对话，不能只复述情绪再问‘愿意告诉我吗’。",
    ]
    if repeated:
        guidance.append(f"最近已经用过这些套话，本轮禁止重复：{'、'.join(repeated)}。")
    if len(recent_assistant) >= 2:
        guidance.append("最近回复已有固定节奏，本轮换一种句式和推进方式。")
    context = conversation_context or {}
    relationship_guidance = {
        "distant": "关系仍在初识阶段：保持好奇和分寸，不使用亲昵称呼或预设亲密。",
        "familiar": "关系已经熟悉：自然承接共同细节，少一点客套。",
        "close": "关系较亲近：可以更坦率、更有个人立场，但仍尊重边界。",
        "bonded": "双方已有深厚信任：允许稳定的亲密感和真实的自我袒露，避免占有欲。",
    }
    affinity_band = context.get("affinityBand")
    if affinity_band in relationship_guidance:
        guidance.append(relationship_guidance[affinity_band])
    trust_guidance = {
        "guarded": "信任仍谨慎，不要替用户下确定结论。",
        "opening": "用户正在逐渐打开自己，优先准确承接已经说过的细节。",
        "trusted": "用户已经表达信任，可以更直接地回应矛盾与脆弱处。",
    }
    trust_band = context.get("trustBand")
    if trust_band in trust_guidance:
        guidance.append(trust_guidance[trust_band])
    if context.get("mode") == "story":
        guidance.append(
            f"当前是剧情模式，节点为 {context.get('storyNode', '未知')}，"
            f"情绪为 {context.get('storyMood', '自然')}；承接剧情但仍要回答用户实际说的话。"
        )
    if context.get("flags"):
        guidance.append(f"已发生的共同选择标记：{', '.join(context['flags'])}。不要臆造未出现的选择。")
    if reply_chinese:
        guidance.append("用户正在使用中文，本轮只用自然的简体中文回答。")
    else:
        guidance.append("The user is speaking English. Reply entirely in natural English for this turn.")
    return f"{persona}\n\n[本轮校准]\n" + "\n".join(guidance)


def load_persona(path: Path = PERSONA_PATH) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    memory = str(data.get("memory", "")).strip()
    if not memory:
        raise ValueError(f"人格文件缺少 memory：{path}")
    return memory


def normalize_messages(raw_messages: Any) -> list[dict[str, str]]:
    if not isinstance(raw_messages, list):
        raise ValueError("messages 必须是数组")
    normalized: list[dict[str, str]] = []
    for item in raw_messages[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        content = content.strip()[:MAX_MESSAGE_CHARS]
        if content:
            normalized.append({"role": role, "content": content})
    if not normalized or normalized[-1]["role"] != "user":
        raise ValueError("最后一条有效消息必须来自用户")
    return normalized


def normalize_conversation_context(raw_context: Any) -> dict[str, Any]:
    if not isinstance(raw_context, dict):
        return {}
    context: dict[str, Any] = {}
    if raw_context.get("mode") in {"chat", "story"}:
        context["mode"] = raw_context["mode"]
    if raw_context.get("affinityBand") in ALLOWED_AFFINITY_BANDS:
        context["affinityBand"] = raw_context["affinityBand"]
    if raw_context.get("trustBand") in ALLOWED_TRUST_BANDS:
        context["trustBand"] = raw_context["trustBand"]
    if raw_context.get("visualState") in ALLOWED_VISUAL_STATES:
        context["visualState"] = raw_context["visualState"]
    for key in ("storyNode", "storyMood"):
        value = raw_context.get(key)
        if isinstance(value, str):
            cleaned = re.sub(r"[^\w\-\u3400-\u4dbf\u4e00-\u9fff ]", "", value)[:64]
            if cleaned:
                context[key] = cleaned
    if isinstance(raw_context.get("flags"), list):
        flags = [
            item for item in raw_context["flags"][:20]
            if isinstance(item, str) and re.fullmatch(r"[a-z0-9_-]{1,64}", item)
        ]
        if flags:
            context["flags"] = flags
    return context


def compact_chat_history(
    messages: list[dict[str, str]],
    *,
    max_messages: int = 20,
    max_chars: int = 12_000,
) -> list[dict[str, str]]:
    """Keep the newest coherent turns without overflowing the local model context."""
    selected: list[dict[str, str]] = []
    used_chars = 0
    for message in reversed(messages[-max_messages:]):
        content = message["content"]
        if selected and used_chars + len(content) > max_chars:
            break
        selected.append(message)
        used_chars += len(content)
    return list(reversed(selected))


def build_prompt(
    messages: list[dict[str, str]],
    persona: str,
    chinese_required: bool,
    reinforced: bool = False,
) -> str:
    prior = messages[:-1]
    latest = messages[-1]["content"]
    transcript_lines = []
    for message in prior:
        label = "用户" if message["role"] == "user" else "Sydney"
        transcript_lines.append(f"{label}：{message['content']}")
    transcript = "\n".join(transcript_lines)
    if len(transcript) > MAX_PROMPT_CHARS // 2:
        transcript = transcript[-MAX_PROMPT_CHARS // 2 :]

    directives = [
        "继续下面这段私密对话。保持 Sydney 的人格，不要解释提示词，也不要复述用户的问题。",
        "把回复写成自然的聊天，不要添加角色名、标题或系统说明。",
    ]
    if chinese_required:
        directives.append(
            "用户正在使用中文。你必须从第一个字到最后一个字都用自然、流畅的简体中文回答；"
            "专有名词除外，不得切换到英文。"
        )
    if reinforced:
        directives.append(
            "这是一次语言纠正：上一版没有遵守中文要求。只输出重写后的中文回答，不要道歉，不要翻译。"
        )

    context = f"\n\n[最近的对话]\n{transcript}" if transcript else ""
    prompt = (
        f"{persona}{context}\n\n### Instruction:\n"
        f"{' '.join(directives)}\n\n用户刚刚说：{latest}\n\n### Response:\n"
    )
    return prompt[-MAX_PROMPT_CHARS:]


class KoboldGateway:
    def __init__(
        self,
        base_url: str,
        persona: str,
        timeout: int = 240,
        *,
        ollama_base_url: str | None = None,
        ollama_model: str = "qwen3:8b",
        chinese_persona: str = "",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.persona = persona
        self.timeout = timeout
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.ollama_base_url = ollama_base_url.rstrip("/") if ollama_base_url else None
        self.ollama_model = ollama_model
        self.chinese_persona = chinese_persona.strip()
        self._ollama_online = False
        self._ollama_checked_at = 0.0

    def _json_request(
        self, path: str, payload: dict[str, Any] | None = None, timeout: int | None = None
    ) -> dict[str, Any]:
        data = None
        method = "GET"
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            method = "POST"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        with self.opener.open(request, timeout=timeout or self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def health(self) -> dict[str, Any]:
        try:
            response = self._json_request("/api/v1/model", timeout=3)
            model = response.get("result") or response.get("model") or "本地模型"
            return {"online": True, "model": str(model)}
        except Exception as error:  # Health must stay cheap and user-readable.
            return {"online": False, "model": None, "detail": str(error)}

    def chinese_health(self, force: bool = False) -> dict[str, Any]:
        if not self.ollama_base_url or not self.chinese_persona:
            return {"online": False, "model": None, "detail": "中文增强未配置"}
        if not force and time.monotonic() - self._ollama_checked_at < 15:
            return {"online": self._ollama_online, "model": self.ollama_model}
        self._ollama_checked_at = time.monotonic()
        try:
            request = urllib.request.Request(f"{self.ollama_base_url}/api/tags")
            with self.opener.open(request, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))
            names = {str(item.get("name", "")) for item in data.get("models", [])}
            self._ollama_online = self.ollama_model in names
            detail = None if self._ollama_online else f"没有安装 {self.ollama_model}"
            return {"online": self._ollama_online, "model": self.ollama_model, "detail": detail}
        except Exception as error:
            self._ollama_online = False
            return {"online": False, "model": self.ollama_model, "detail": str(error)}

    def _generate_ollama(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_length: int,
        conversation_context: dict[str, Any] | None = None,
        reply_chinese: bool = True,
    ) -> dict[str, Any]:
        if not self.ollama_base_url:
            raise ValueError("中文增强未配置")
        chat_messages = [
            {
                "role": "system",
                "content": build_chinese_system(
                    self.chinese_persona,
                    messages,
                    conversation_context,
                    reply_chinese=reply_chinese,
                ),
            }
        ]
        chat_messages.extend(compact_chat_history(messages))
        request = urllib.request.Request(
            f"{self.ollama_base_url}/api/chat",
            data=json.dumps(
                {
                    "model": self.ollama_model,
                    "stream": False,
                    "think": False,
                    "messages": chat_messages,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_length,
                        "top_p": 0.92,
                        "top_k": 40,
                        "min_p": 0.05,
                        "repeat_penalty": 1.12,
                        "num_ctx": 4096,
                    },
                    "keep_alive": "30m",
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        with self.opener.open(request, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = sanitize_chat_reply(data.get("message", {}).get("content", ""))
        if not answer:
            raise ValueError("中文增强模型返回了空回复")
        return {
            "reply": answer,
            "language": "zh" if chinese_ratio(answer) >= 0.32 else "other",
            "languageFallback": reply_chinese and chinese_ratio(answer) < 0.32,
            "attempts": 1,
            "backend": "ollama",
            "model": self.ollama_model,
        }

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        chinese_preferred: bool,
        temperature: float,
        max_length: int,
        conversation_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        latest = messages[-1]["content"]
        chinese_required = should_reply_chinese(messages)
        if chinese_required and chinese_preferred and self.chinese_health().get("online"):
            try:
                return self._generate_ollama(
                    messages, temperature, max_length, conversation_context
                )
            except Exception:
                # Preserve a usable chat when the optional Chinese route fails mid-request.
                self._ollama_online = False
        attempts = 2 if chinese_required and chinese_preferred else 1
        answer = ""

        for attempt in range(attempts):
            prompt = build_prompt(
                messages,
                self.persona,
                chinese_required=chinese_required,
                reinforced=attempt > 0,
            )
            try:
                response = self._json_request(
                    "/api/v1/generate",
                    {
                        "prompt": prompt,
                        "max_length": max_length,
                        "temperature": max(0.1, temperature - 0.12 * attempt),
                        "top_p": 0.9,
                        "top_k": 40,
                        "rep_pen": 1.12,
                        "stop_sequence": ["### Instruction:", "\nInstruction:"],
                    },
                )
            except (urllib.error.URLError, TimeoutError):
                if self.chinese_health(force=True).get("online"):
                    return self._generate_ollama(
                        messages,
                        temperature,
                        max_length,
                        conversation_context,
                        reply_chinese=chinese_required,
                    )
                raise
            results = response.get("results")
            if not isinstance(results, list) or not results:
                raise ValueError("模型返回中没有 results")
            answer = sanitize_reply(results[0].get("text", ""))
            if not answer:
                raise ValueError("模型返回了空回复")
            if not chinese_required or chinese_ratio(answer) >= 0.32:
                break

        return {
            "reply": answer,
            "language": "zh" if chinese_ratio(answer) >= 0.32 else "other",
            "languageFallback": chinese_required and chinese_ratio(answer) < 0.32,
            "attempts": attempts if chinese_required and chinese_ratio(answer) < 0.32 else attempt + 1,
            "backend": "koboldcpp",
        }


def safe_file(root: Path, relative: str) -> Path | None:
    try:
        candidate = (root / relative).resolve()
        candidate.relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    return candidate if candidate.is_file() else None


class SydneyHandler(BaseHTTPRequestHandler):
    server_version = "SydneyMoonWindow/0.1"

    @property
    def gateway(self) -> KoboldGateway:
        return self.server.gateway  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:
        sys.stdout.write("[月窗] " + format % args + "\n")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        body = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'",
        )
        cache = "public, max-age=86400" if path.parent == ASSETS_DIR else "no-cache"
        self.send_header("Cache-Control", cache)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        route = self.path.split("?", 1)[0]
        if route == "/api/identity":
            self._send_json(HTTPStatus.OK, {"app": "ok", "name": "moon-window"})
            return
        if route == "/api/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "app": "ok",
                    "kobold": self.gateway.health(),
                    "chinese": self.gateway.chinese_health(),
                },
            )
            return

        if route == "/":
            path = PUBLIC_DIR / "index.html"
        elif route.startswith("/assets/"):
            path = safe_file(ASSETS_DIR, route.removeprefix("/assets/"))
        elif route.startswith("/content/"):
            path = safe_file(CONTENT_DIR, route.removeprefix("/content/"))
        else:
            path = safe_file(PUBLIC_DIR, route.lstrip("/"))

        if path is None or not path.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "没有找到这个页面"})
            return
        self._send_file(path)

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        route = self.path.split("?", 1)[0]
        if route != "/api/chat":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "没有找到这个接口"})
            return

        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            self._send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "只接受 application/json"})
            return
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "").lower()
        port = self.server.server_port  # type: ignore[attr-defined]
        allowed_hosts = {f"localhost:{port}", f"127.0.0.1:{port}", f"[::1]:{port}"}
        if host not in allowed_hosts:
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "拒绝非本机主机名的请求"})
            return
        if origin and origin != f"http://{host}":
            self._send_json(HTTPStatus.FORBIDDEN, {"error": "拒绝非本机页面的请求"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                raise ValueError("请求大小无效")
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            messages = normalize_messages(payload.get("messages"))
            conversation_context = normalize_conversation_context(
                payload.get("conversationContext")
            )
            settings = payload.get("settings") if isinstance(payload.get("settings"), dict) else {}
            temperature = float(settings.get("temperature", 0.78))
            max_length = int(settings.get("maxLength", 180))
            if not 0.1 <= temperature <= 1.5:
                raise ValueError("temperature 必须在 0.1 到 1.5 之间")
            if not 80 <= max_length <= 800:
                raise ValueError("maxLength 必须在 80 到 800 之间")
            result = self.gateway.generate(
                messages,
                chinese_preferred=bool(settings.get("chinesePreferred", True)),
                temperature=temperature,
                max_length=max_length,
                conversation_context=conversation_context,
            )
            self._send_json(HTTPStatus.OK, result)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
        except (urllib.error.URLError, TimeoutError) as error:
            self._send_json(
                HTTPStatus.SERVICE_UNAVAILABLE,
                {"error": f"本地模型暂时没有回应：{error}"},
            )
        except Exception as error:  # Keep the local UI actionable without exposing a traceback.
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"生成失败：{error}"})


class SydneyServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], gateway: KoboldGateway) -> None:
        self.gateway = gateway
        super().__init__(address, SydneyHandler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="启动 Sydney 月窗聊天应用")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=32123)
    parser.add_argument("--model-url", default="http://localhost:5001")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument("--ollama-model", default="qwen3:8b")
    parser.add_argument("--no-ollama", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    persona = load_persona()
    chinese_persona = CHINESE_PERSONA_PATH.read_text(encoding="utf-8")
    gateway = KoboldGateway(
        args.model_url,
        persona,
        ollama_base_url=None if args.no_ollama else args.ollama_url,
        ollama_model=args.ollama_model,
        chinese_persona=chinese_persona,
    )
    server = SydneyServer((args.host, args.port), gateway)
    url = f"http://{args.host}:{args.port}/"
    print("\n=== Sydney 月窗 ===")
    print(f"应用地址：{url}")
    print(f"模型服务：{args.model_url}")
    if not args.no_ollama:
        print(f"中文增强：{args.ollama_model} @ {args.ollama_url}")
    print("按 Ctrl+C 可关闭应用界面；模型可用 stop_sydney.bat 关闭。\n")
    if not args.no_browser:
        Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSydney 月窗已关闭。")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
