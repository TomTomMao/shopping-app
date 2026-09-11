from pathlib import Path
p=Path('sceneforge-animate/phase3.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Phase 3.0.1','Phase 3.0.2')
old='''    <div class="field"><label>千问AI平台 API Key（qianwenai.com）</label><input id="qwenKey" type="password" placeholder="sk-ws-..."/></div>
    <div class="hint">千问AI平台（qianwenai.com）按量付费 Key 直接填写完整的 <b>sk-ws-...</b>。无需 Workspace ID，也无需选择区域。测试版 Key 只保存在当前浏览器 session。Qwen 默认使用 qwen-image-3.0-pro；Meshy 默认使用 latest。</div>'''
new='''    <div class="field"><label>千问AI平台 API Key（qianwenai.com）</label><input id="qwenKey" type="password" placeholder="sk-ws-..."/></div>
    <div class="field"><label>Qwen Proxy URL</label><input id="qwenProxy" type="url" placeholder="https://your-worker.workers.dev"/></div>
    <div class="hint">DashScope 不允许 raw.githack 浏览器跨域直连，所以 Qwen 必须经过一个很薄的代理。填 Worker 根地址即可，不要加 /qwen-image。Key 与 Proxy URL 都只保存在当前浏览器 session。</div>'''
if old not in s: raise SystemExit('qwen settings anchor missing')
s=s.replace(old,new,1)
s=s.replace("qwenKey:$('qwenKey'),verifyDeepseek", "qwenKey:$('qwenKey'),qwenProxy:$('qwenProxy'),verifyDeepseek")
s=s.replace("ui.deepseekKey.value=session.get('sf3_deepseek');ui.meshyKey.value=session.get('sf3_meshy');ui.qwenKey.value=session.get('sf3_qwen');", "ui.deepseekKey.value=session.get('sf3_deepseek');ui.meshyKey.value=session.get('sf3_meshy');ui.qwenKey.value=session.get('sf3_qwen');ui.qwenProxy.value=session.get('sf3_qwen_proxy');")
s=s.replace("[ui.qwenKey,'sf3_qwen','qwen']])", "[ui.qwenKey,'sf3_qwen','qwen'],[ui.qwenProxy,'sf3_qwen_proxy','qwen']])")
s=s.replace('<div class="apiCheck"><b>Qwen Endpoint</b><span class="endpoint">dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation</span></div>', '<div class="apiCheck"><b>Qwen Route</b><span class="endpoint">Browser → Qwen Proxy → DashScope</span></div>')
s=s.replace("function qwenEndpoint(){return 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'}", "function qwenProxyBase(){const v=ui.qwenProxy.value.trim().replace(/\\/$/,'');if(!v)throw new Error('请填写 Qwen Proxy URL');return v}\nfunction qwenEndpoint(){return qwenProxyBase()+'/qwen-image'}")
s=s.replace("headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`}", "headers:{'Content-Type':'application/json','X-Qwen-Key':key}")
s=s.replace("providerError('Qwen',e,'dashscope.aliyuncs.com')", "providerError('Qwen Proxy',e,qwenProxyBase())")
start=s.index('async function verifyQwen(){')
end=s.index('async function verifyMeshy(){',start)
new_verify=r'''async function verifyQwen(){
  const key=ui.qwenKey.value.trim();if(!key){setApiState('qwen','fail','未填写 API Key');return false}
  if(!key.startsWith('sk-ws-')){setApiState('qwen','fail','Key 应以 sk-ws- 开头');return false}
  let base;try{base=qwenProxyBase()}catch(e){setApiState('qwen','fail','DashScope 被浏览器 CORS 阻止，请先填写 Qwen Proxy URL');return false}
  setApiState('qwen','testing','正在验证 Proxy 和 DashScope 鉴权…');
  try{
    const health=await fetch(base+'/health');if(!health.ok){setApiState('qwen','fail',`Proxy /health HTTP ${health.status}`);return false}
    const r=await fetch(base+'/verify-qwen',{method:'POST',headers:{'Content-Type':'application/json','X-Qwen-Key':key},body:'{}'});
    if(!r.ok){const t=await r.text();setApiState('qwen','fail',`Proxy 验证失败 HTTP ${r.status}: ${t.slice(0,180)}`);return false}
    const j=await r.json(),st=Number(j.upstream_status);
    if([200,400,422].includes(st)){setApiState('qwen','ok',`Proxy 可达，DashScope 鉴权通过（上游 HTTP ${st}；测试未生成图片）`);return true}
    setApiState('qwen','fail',httpMeaning('Qwen/DashScope',st,j.upstream_body||''));return false
  }catch(e){setApiState('qwen','fail',providerError('Qwen Proxy',e,base));return false}
}
'''
s=s[:start]+new_verify+s[end:]
s=s.replace("const key=ui.qwenKey.value.trim();if(!key)throw new Error('请填写千问AI平台 API Key（sk-ws-...）');", "const key=ui.qwenKey.value.trim();if(!key)throw new Error('请填写千问AI平台 API Key（sk-ws-...）');qwenProxyBase();")
p.write_text(s,encoding='utf-8')
