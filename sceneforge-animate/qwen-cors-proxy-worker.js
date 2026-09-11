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

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin') || '*';
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: corsHeaders(origin) });
    if (url.pathname === '/health') return Response.json({ ok: true, service: 'sceneforge-qwen-proxy' }, { headers: corsHeaders(origin) });
    if (url.pathname !== '/qwen-image' || request.method !== 'POST') return Response.json({ error: 'Not found' }, { status: 404, headers: corsHeaders(origin) });

    const key = request.headers.get('X-Qwen-Key') || request.headers.get('Authorization')?.replace(/^Bearer\s+/i, '');
    if (!key) return Response.json({ error: 'Missing Qwen API key' }, { status: 401, headers: corsHeaders(origin) });

    let body;
    try { body = await request.json(); } catch { return Response.json({ error: 'Invalid JSON' }, { status: 400, headers: corsHeaders(origin) }); }

    const upstream = await fetch(QWEN_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${key}` },
      body: JSON.stringify(body)
    });
    const text = await upstream.text();
    const headers = { ...corsHeaders(origin), 'Content-Type': upstream.headers.get('Content-Type') || 'application/json' };
    return new Response(text, { status: upstream.status, headers });
  }
};
