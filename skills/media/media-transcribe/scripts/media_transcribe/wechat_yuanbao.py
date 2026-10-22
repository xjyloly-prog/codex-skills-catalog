from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .dependencies import DependencySpec, ensure_dependencies
from .status import StatusReporter

YUANBAO_ORIGIN = "https://yuanbao.tencent.com"
CHANNELS_HOST = "channels.weixin.qq.com"


class YuanbaoFallbackError(RuntimeError):
    pass


@dataclass(frozen=True)
class YuanbaoResult:
    title: str
    media_url: str
    metadata: dict[str, str]


class _CdpClient:
    def __init__(self, websocket_url: str, timeout: float = 15.0) -> None:
        parsed = urlsplit(websocket_url)
        if parsed.scheme != "ws" or parsed.hostname not in ("127.0.0.1", "localhost"):
            raise YuanbaoFallbackError("The isolated Chrome debugger returned an unsafe endpoint.")
        try:
            from websocket import create_connection
        except ImportError as exc:
            raise YuanbaoFallbackError(
                "The isolated Yuanbao fallback dependency is missing. Install it with: "
                "bash install.sh --component wechat-yuanbao"
            ) from exc
        self._socket = create_connection(
            websocket_url,
            timeout=timeout,
            suppress_origin=True,
            http_no_proxy=["127.0.0.1", "localhost"],
        )
        self._next_id = 0

    def close(self) -> None:
        self._socket.close()

    def call(self, method: str, **params):
        self._next_id += 1
        request_id = self._next_id
        payload = {"id": request_id, "method": method}
        if params:
            payload["params"] = params
        self._socket.send(json.dumps(payload))
        while True:
            raw = self._socket.recv()
            response = json.loads(raw)
            if response.get("id") != request_id:
                continue
            if "error" in response:
                message = _safe_text((response.get("error") or {}).get("message") or "CDP error")
                raise YuanbaoFallbackError(f"Isolated Chrome command failed: {message}")
            return response.get("result") or {}

    def evaluate(self, expression: str, *, await_promise: bool = False):
        result = self.call(
            "Runtime.evaluate",
            expression=expression,
            awaitPromise=await_promise,
            returnByValue=True,
        )
        if result.get("exceptionDetails"):
            details = result["exceptionDetails"]
            message = _safe_text(details.get("text") or "page script failed")
            raise YuanbaoFallbackError(f"Yuanbao page request failed: {message}")
        return (result.get("result") or {}).get("value")


class _IsolatedChrome:
    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self.process: subprocess.Popen | None = None
        self.port: int | None = None

    def __enter__(self) -> _IsolatedChrome:
        executable = _find_chrome()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.profile_dir.chmod(0o700)
        except OSError:
            pass
        command = [
            executable,
            f"--user-data-dir={self.profile_dir}",
            "--remote-debugging-address=127.0.0.1",
            "--remote-debugging-port=0",
            "--no-first-run",
            "--no-default-browser-check",
            YUANBAO_ORIGIN,
        ]
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        port_file = self.profile_dir / "DevToolsActivePort"
        deadline = time.monotonic() + 30
        try:
            while time.monotonic() < deadline:
                if self.process.poll() is not None:
                    raise YuanbaoFallbackError(
                        "The isolated Chrome process exited before it was ready."
                    )
                try:
                    first_line = port_file.read_text(encoding="utf-8").splitlines()[0]
                    self.port = int(first_line)
                    return self
                except (FileNotFoundError, IndexError, UnicodeDecodeError, ValueError):
                    time.sleep(0.2)
            raise YuanbaoFallbackError("Timed out while starting the isolated Chrome session.")
        except BaseException:
            self._stop()
            raise

    def __exit__(self, _type, _value, _traceback) -> None:
        self._stop()

    def _stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)


def _find_chrome() -> str:
    configured = os.environ.get("MEDIA_TRANSCRIBE_CHROME")
    candidates = [
        configured,
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    if os.name == "nt":
        for root_name in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            root = os.environ.get(root_name)
            if root:
                candidates.append(str(Path(root) / "Google/Chrome/Application/chrome.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate))
    raise YuanbaoFallbackError(
        "Google Chrome or Chromium is required for the isolated Yuanbao fallback."
    )


def _safe_text(value: object) -> str:
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(value or "")).strip()


def _local_json(url: str, timeout: float = 5.0):
    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost"):
        raise YuanbaoFallbackError("Refused a non-loopback Chrome debugger endpoint.")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _page_target(port: int, host: str) -> dict | None:
    targets = _local_json(f"http://127.0.0.1:{port}/json/list")
    if not isinstance(targets, list):
        return None
    for target in targets:
        if not isinstance(target, dict) or target.get("type") != "page":
            continue
        parsed = urlsplit(str(target.get("url") or ""))
        if parsed.scheme == "https" and (parsed.hostname or "").lower() == host:
            websocket_url = target.get("webSocketDebuggerUrl")
            if isinstance(websocket_url, str) and websocket_url:
                return target
    return None


def _parse_with_yuanbao(client: _CdpClient, source: str) -> dict:
    source_json = json.dumps(source, ensure_ascii=False)
    origin_json = json.dumps(YUANBAO_ORIGIN)
    expression = f"""
(async () => {{
  const page = {{href: location.href, origin: location.origin, readyState: document.readyState}};
  if (page.origin !== {origin_json} || page.readyState === 'loading') {{
    return {{waiting: true, page}};
  }}
  try {{
    const response = await fetch('https://yuanbao.tencent.com/api/weixin/get_parse_result', {{
      method: 'POST',
      credentials: 'same-origin',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{
        type: 'video_channel_url',
        url: {source_json},
        scene: 1
      }})
    }});
    let data = null;
    try {{ data = await response.json(); }} catch (_) {{}}
    return {{status: response.status, ok: response.ok, data, page}};
  }} catch (error) {{
    return {{waiting: true, networkError: String(error), page}};
  }}
}})()
"""
    result = client.evaluate(expression, await_promise=True)
    return result if isinstance(result, dict) else {}


def _wait_for_parse(port: int, source: str, reporter: StatusReporter | None, timeout: float) -> str:
    deadline = time.monotonic() + timeout
    last_notice = 0.0
    while time.monotonic() < deadline:
        target = _page_target(port, "yuanbao.tencent.com")
        if target:
            client = _CdpClient(target["webSocketDebuggerUrl"])
            try:
                parsed = _parse_with_yuanbao(client, source)
            finally:
                client.close()
            status = parsed.get("status")
            payload = parsed.get("data") if isinstance(parsed.get("data"), dict) else {}
            data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
            playable = data.get("playable_url")
            if status == 200 and payload.get("code") == 0 and isinstance(playable, str):
                return _trusted_playable_url(playable)
            if status not in (None, 401, 403) and payload:
                detail = _safe_text(payload.get("msg") or payload.get("message") or payload.get("code"))
                raise YuanbaoFallbackError(f"Yuanbao could not parse this share link: {detail or status}")
        now = time.monotonic()
        if reporter and now - last_notice >= 10:
            reporter.detail("Log in to Tencent Yuanbao in the isolated Chrome window; waiting for login")
            last_notice = now
        time.sleep(3)
    raise YuanbaoFallbackError(
        "Timed out waiting for Tencent Yuanbao login. The isolated browser profile was removed."
    )


def _trusted_playable_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() != CHANNELS_HOST
        or parsed.username
        or parsed.password
        or parsed.port
    ):
        raise YuanbaoFallbackError("Yuanbao returned an unexpected playback URL.")
    return value


def _wait_for_media(port: int, playable_url: str, timeout: float) -> tuple[str, str]:
    target = _page_target(port, "yuanbao.tencent.com")
    if not target:
        raise YuanbaoFallbackError("The authenticated Yuanbao page closed before playback started.")
    client = _CdpClient(target["webSocketDebuggerUrl"])
    try:
        client.call("Page.enable")
        client.call("Page.navigate", url=playable_url)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = client.evaluate("""
(() => {
  const video = document.querySelector('video');
  if (video) { video.play().catch(() => {}); }
  const title =
    document.querySelector('meta[property="og:title"]')?.content ||
    document.title ||
    '视频号视频';
  return {url: video?.currentSrc || video?.src || '', title};
})()
""")
            if isinstance(value, dict) and isinstance(value.get("url"), str) and value["url"]:
                return _safe_text(value.get("title")) or "视频号视频", value["url"]
            time.sleep(2)
    finally:
        client.close()
    raise YuanbaoFallbackError("The official WeChat Channels page did not expose a playable video.")


def resolve_via_yuanbao(
    source: str,
    temp_dir: Path,
    reporter: StatusReporter | None = None,
    *,
    login_timeout: float = 600,
    playback_timeout: float = 120,
) -> YuanbaoResult:
    ensure_dependencies(DependencySpec("wechat-yuanbao", ("websocket",)))
    if reporter:
        reporter.stage("Opening isolated Tencent Yuanbao browser")
        reporter.warning(
            "Use the isolated Chrome window to log in to Tencent Yuanbao. "
            "Cookies stay inside this temporary browser profile and are not exported."
        )
    profile_dir = temp_dir / "yuanbao-profile"
    with _IsolatedChrome(profile_dir) as chrome:
        assert chrome.port is not None
        if reporter:
            reporter.stage("Waiting for Yuanbao same-origin parsing")
        playable_url = _wait_for_parse(chrome.port, source, reporter, login_timeout)
        if reporter:
            reporter.stage("Reading the official WeChat Channels media URL")
        title, media_url = _wait_for_media(chrome.port, playable_url, playback_timeout)
    return YuanbaoResult(title, media_url, {"acquisition": "yuanbao-same-origin"})
