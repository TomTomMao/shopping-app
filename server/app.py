from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Any
from urllib.request import getproxies

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
SCENEFORGE_DIR = ROOT / "sceneforge-animate"
load_dotenv(ROOT / "server" / ".env")

DEEPSEEK_BASE = "https://api.deepseek.com"
MESHY_BASE = "https://api.meshy.ai"
QWEN_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

app = FastAPI(title="SceneForge Local Server", version="3.0.4")
app.mount("/sceneforge-animate", StaticFiles(directory=SCENEFORGE_DIR), name="sceneforge-animate")


def env_key(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise HTTPException(status_code=503, detail=f"Missing {name} in server/.env")
    return value


def filtered_headers(headers: dict[str, str]) -> dict[str, str]:
    blocked = {"host", "content-length", "authorization", "x-qwen-key", "connection", "origin", "referer"}
    return {k: v for k, v in headers.items() if k.lower() not in blocked}


def detected_proxy() -> str | None:
    explicit = (
        os.getenv("SCENEFORGE_PROXY", "").strip()
        or os.getenv("HTTPS_PROXY", "").strip()
        or os.getenv("https_proxy", "").strip()
        or os.getenv("HTTP_PROXY", "").strip()
        or os.getenv("http_proxy", "").strip()
    )
    if explicit:
        return explicit
    proxies = getproxies()
    return proxies.get("https") or proxies.get("http")


def exc_detail(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc!r}"


async def request_upstream(method: str, url: str, *, headers: dict[str, str] | None = None, content: bytes | None = None, params: Any = None, json: Any = None, timeout: float = 180.0) -> httpx.Response:
    proxy = detected_proxy()
    attempts: list[tuple[str, str | None]] = []
    if proxy:
        attempts.append(("system-proxy", proxy))
    attempts.append(("direct", None))

    errors: list[str] = []
    for label, proxy_url in attempts:
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(timeout, connect=30.0),
                follow_redirects=True,
                proxy=proxy_url,
                trust_env=False,
            ) as client:
                return await client.request(method, url, headers=headers, content=content, params=params, json=json)
        except httpx.HTTPError as exc:
            errors.append(f"{label}={exc_detail(exc)}")

    raise HTTPException(
        status_code=502,
        detail={
            "message": "All outbound connection attempts failed",
            "target": url,
            "proxy_detected": proxy or None,
            "attempts": errors,
        },
    )


async def forward(request: Request, upstream_url: str, auth_key: str) -> Response:
    body = await request.body()
    headers = filtered_headers(dict(request.headers))
    headers["Authorization"] = f"Bearer {auth_key}"
    result = await request_upstream(
        request.method,
        upstream_url,
        params=request.query_params,
        headers=headers,
        content=body or None,
    )
    media_type = result.headers.get("content-type", "application/json").split(";", 1)[0]
    return Response(content=result.content, status_code=result.status_code, media_type=media_type)


LOCAL_SHIM = r'''
<script>
(() => {
  sessionStorage.setItem('sf3_deepseek', 'local-backend-managed');
  sessionStorage.setItem('sf3_meshy', 'local-backend-managed');
  sessionStorage.setItem('sf3_qwen', 'sk-ws-local-backend-managed');
  sessionStorage.setItem('sf3_qwen_proxy', location.origin);

  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const raw = typeof input === 'string' ? input : input.url;
    let url;
    try { url = new URL(raw, location.href); } catch { return nativeFetch(input, init); }
    let target = null;
    if (url.hostname === 'api.deepseek.com') target = '/api/deepseek' + url.pathname + url.search;
    if (url.hostname === 'api.meshy.ai') target = '/api/meshy' + url.pathname + url.search;
    if (!target) return nativeFetch(input, init);

    const headers = new Headers(init.headers || (typeof input !== 'string' ? input.headers : undefined) || {});
    headers.delete('Authorization');
    headers.delete('X-Qwen-Key');
    return nativeFetch(target, {...init, headers});
  };

  addEventListener('DOMContentLoaded', () => {
    const ids = ['deepseekKey','meshyKey','qwenKey','qwenProxy'];
    for (const id of ids) {
      const el = document.getElementById(id);
      if (!el) continue;
      el.disabled = true;
      el.title = 'Local mode: configured in server/.env';
    }
    const brand = document.querySelector('.brand');
    if (brand) brand.textContent = 'SceneForge Animate · Phase 3.0.4 Local';
    const apiCard = [...document.querySelectorAll('.card')].find(x => x.querySelector('h3')?.textContent === 'API 设置');
    const hint = apiCard?.querySelector('.hint');
    if (hint) hint.textContent = '本地模式：API Key 由 server/.env 管理；服务端会自动尝试 Windows 系统代理并在失败时回退直连。';
  });
})();
</script>
'''


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_path = SCENEFORGE_DIR / "phase3.html"
    html = html_path.read_text(encoding="utf-8")
    marker = '<script type="importmap">'
    if marker not in html:
        raise HTTPException(status_code=500, detail="Phase 3 page is missing importmap marker")
    html = html.replace(marker, LOCAL_SHIM + "\n" + marker, 1)
    return HTMLResponse(html)


@app.get("/health")
async def health() -> dict[str, Any]:
    proxy = detected_proxy()
    return {
        "ok": True,
        "service": "sceneforge-local",
        "providers": {
            "deepseek": bool(os.getenv("DEEPSEEK_API_KEY", "").strip()),
            "qwen": bool(os.getenv("QWEN_API_KEY", "").strip()),
            "meshy": bool(os.getenv("MESHY_API_KEY", "").strip()),
        },
        "network": {
            "proxy_detected": proxy,
        },
    }


@app.get("/network-check")
async def network_check() -> dict[str, Any]:
    targets = {
        "deepseek": "https://api.deepseek.com/models",
        "qwen": "https://dashscope.aliyuncs.com/",
        "meshy": "https://api.meshy.ai/",
    }
    out: dict[str, Any] = {"proxy_detected": detected_proxy(), "dns": {}, "https": {}}
    for name, url in targets.items():
        host = url.split("//", 1)[1].split("/", 1)[0]
        try:
            out["dns"][name] = socket.gethostbyname(host)
        except Exception as exc:
            out["dns"][name] = exc_detail(exc)
        try:
            r = await request_upstream("GET", url, timeout=20.0)
            out["https"][name] = {"status": r.status_code}
        except HTTPException as exc:
            out["https"][name] = exc.detail
    return out


@app.api_route("/api/deepseek/{path:path}", methods=["GET", "POST"])
async def deepseek_proxy(path: str, request: Request) -> Response:
    return await forward(request, f"{DEEPSEEK_BASE}/{path}", env_key("DEEPSEEK_API_KEY"))


@app.api_route("/api/meshy/{path:path}", methods=["GET", "POST"])
async def meshy_proxy(path: str, request: Request) -> Response:
    return await forward(request, f"{MESHY_BASE}/{path}", env_key("MESHY_API_KEY"))


@app.post("/qwen-image")
async def qwen_image(request: Request) -> Response:
    return await forward(request, QWEN_ENDPOINT, env_key("QWEN_API_KEY"))


@app.post("/verify-qwen")
async def verify_qwen() -> JSONResponse:
    key = env_key("QWEN_API_KEY")
    payload = {
        "model": "qwen-image-3.0-pro",
        "input": {"messages": [{"role": "user", "content": []}]},
        "parameters": {"prompt_extend": False},
    }
    result = await request_upstream(
        "POST",
        QWEN_ENDPOINT,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        json=payload,
        timeout=60.0,
    )
    return JSONResponse({"upstream_status": result.status_code, "upstream_body": result.text[:1000]})
