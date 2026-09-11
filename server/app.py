from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import getproxies

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
SCENEFORGE_DIR = ROOT / "sceneforge-animate"
load_dotenv(ROOT / "server" / ".env")

DEEPSEEK_BASE = "https://api.deepseek.com"
MESHY_BASE = "https://api.meshy.ai"
QWEN_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

app = FastAPI(title="SceneForge Local Server", version="3.2.0")
app.mount("/sceneforge-animate", StaticFiles(directory=SCENEFORGE_DIR), name="sceneforge-animate")


def env_key(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise HTTPException(status_code=503, detail=f"Missing {name} in server/.env")
    return value


def filtered_headers(headers: dict[str, str]) -> dict[str, str]:
    blocked = {"host", "content-length", "authorization", "x-qwen-key", "connection", "origin", "referer"}
    return {k: v for k, v in headers.items() if k.lower() not in blocked}


def normalize_proxy(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if "://" not in value:
        return "http://" + value
    lowered = value.lower()
    for prefix in ("https://127.0.0.1:", "https://localhost:", "https://[::1]:"):
        if lowered.startswith(prefix):
            return "http://" + value[len("https://"):]
    return value


def raw_detected_proxy() -> str | None:
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


def detected_proxy() -> str | None:
    return normalize_proxy(raw_detected_proxy())


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
            "proxy_raw": raw_detected_proxy(),
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
    for (const id of ['deepseekKey','meshyKey','qwenKey','qwenProxy']) {
      const el = document.getElementById(id);
      if (!el) continue;
      el.disabled = true;
      el.title = 'Local mode: configured in server/.env';
    }
    const brand = document.querySelector('.brand');
    if (brand && brand.textContent.includes('Phase 3')) brand.textContent = brand.textContent.includes('3.2') ? 'SceneForge Animate · Phase 3.2 Local' : 'SceneForge Animate · Phase 3 Local';
    const apiCard = [...document.querySelectorAll('.card')].find(x => x.querySelector('h3')?.textContent === 'API 设置');
    const hint = apiCard?.querySelector('.hint');
    if (hint) hint.textContent = '本地模式：API Key 由 server/.env 管理；供应商 API 与生成资产下载均由 localhost 后端转发。';
  });
})();
</script>
'''


def render_page(filename: str) -> HTMLResponse:
    html_path = SCENEFORGE_DIR / filename
    if not html_path.exists():
        raise HTTPException(status_code=404, detail=f"Missing {filename}. Run the Phase 3.2 builder/workflow first.")
    html = html_path.read_text(encoding="utf-8")
    marker = '<script type="importmap">'
    if marker not in html:
        raise HTTPException(status_code=500, detail=f"{filename} is missing importmap marker")
    html = html.replace(marker, LOCAL_SHIM + "\n" + marker, 1)
    return HTMLResponse(html)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    phase32 = SCENEFORGE_DIR / "phase32.html"
    return render_page("phase32.html" if phase32.exists() else "phase3.html")


@app.get("/phase3", response_class=HTMLResponse)
async def phase3() -> HTMLResponse:
    return render_page("phase3.html")


@app.get("/phase32", response_class=HTMLResponse)
async def phase32() -> HTMLResponse:
    return render_page("phase32.html")


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "sceneforge-local",
        "version": "3.2.0",
        "phase32_built": (SCENEFORGE_DIR / "phase32.html").exists(),
        "providers": {
            "deepseek": bool(os.getenv("DEEPSEEK_API_KEY", "").strip()),
            "qwen": bool(os.getenv("QWEN_API_KEY", "").strip()),
            "meshy": bool(os.getenv("MESHY_API_KEY", "").strip()),
        },
        "network": {"proxy_raw": raw_detected_proxy(), "proxy_detected": detected_proxy()},
    }


@app.get("/network-check")
async def network_check() -> dict[str, Any]:
    targets = {
        "deepseek": "https://api.deepseek.com/models",
        "qwen": "https://dashscope.aliyuncs.com/",
        "meshy": "https://api.meshy.ai/",
    }
    out: dict[str, Any] = {
        "proxy_raw": raw_detected_proxy(),
        "proxy_detected": detected_proxy(),
        "note": "DeepSeek 401 and Qwen/Meshy 404 at these unauthenticated probe URLs can still mean network connectivity is healthy.",
        "dns": {}, "https": {},
    }
    for name, url in targets.items():
        host = url.split("//", 1)[1].split("/", 1)[0]
        try:
            out["dns"][name] = socket.gethostbyname(host)
        except Exception as exc:
            out["dns"][name] = exc_detail(exc)
        try:
            r = await request_upstream("GET", url, timeout=20.0)
            out["https"][name] = {"reachable": True, "status": r.status_code}
        except HTTPException as exc:
            out["https"][name] = {"reachable": False, **(exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail})}
    return out


@app.get("/asset-proxy")
async def asset_proxy(url: str = Query(..., min_length=8)) -> Response:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Only http/https asset URLs are allowed")
    if parsed.hostname in {"127.0.0.1", "localhost", "::1"}:
        raise HTTPException(status_code=400, detail="Loopback asset URLs are not allowed")
    result = await request_upstream("GET", url, timeout=180.0)
    media_type = result.headers.get("content-type", "application/octet-stream").split(";", 1)[0]
    headers = {"Cache-Control": "private, max-age=300"}
    return Response(content=result.content, status_code=result.status_code, media_type=media_type, headers=headers)


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
        "POST", QWEN_ENDPOINT,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        json=payload, timeout=60.0,
    )
    return JSONResponse({"upstream_status": result.status_code, "upstream_body": result.text[:1000]})
