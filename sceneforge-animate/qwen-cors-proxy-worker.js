const QWEN_ENDPOINT = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation';

function corsHeaders(origin='*') {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Qwen-Key',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin'
  };
}

async function forwardQwen(key, body) {
  return fetch(QWEN_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${key}` },
    body: JSON.stringify(body)
  });
}

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin') || '*';
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: corsHeaders(origin) });
    if (url.pathname === '/health') return Response.json({ ok: true, service: 'sceneforge-qwen-proxy' }, { headers: corsHeaders(origin) });

    const key = request.headers.get('X-Qwen-Key') || request.headers.get('Authorization')?.replace(/^Bearer\s+/i, '');
    if (!key) return Response.json({ error: 'Missing Qwen API key' }, { status: 401, headers: corsHeaders(origin) });

    if (url.pathname === '/verify-qwen' && request.method === 'POST') {
      const upstream = await forwardQwen(key, {
        model: 'qwen-image-3.0-pro',
        input: { messages: [{ role: 'user', content: [] }] },
        parameters: { prompt_extend: false }
      });
      const text = await upstream.text();
      return Response.json({ upstream_status: upstream.status, upstream_body: text.slice(0, 600) }, { status: 200, headers: corsHeaders(origin) });
    }

    if (url.pathname !== '/qwen-image' || request.method !== 'POST') return Response.json({ error: 'Not found' }, { status: 404, headers: corsHeaders(origin) });

    let body;
    try { body = await request.json(); } catch { return Response.json({ error: 'Invalid JSON' }, { status: 400, headers: corsHeaders(origin) }); }

    const upstream = await forwardQwen(key, body);
    const text = await upstream.text();
    const headers = { ...corsHeaders(origin), 'Content-Type': upstream.headers.get('Content-Type') || 'application/json' };
    return new Response(text, { status: upstream.status, headers });
  }
};
