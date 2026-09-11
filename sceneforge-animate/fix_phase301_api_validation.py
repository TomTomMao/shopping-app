from pathlib import Path
p=Path('sceneforge-animate/phase3.html')
s=p.read_text(encoding='utf-8')

# Version label.
s=s.replace('SceneForge Animate · Phase 3</title>','SceneForge Animate · Phase 3.0.1</title>')
s=s.replace('SceneForge Animate · Phase 3</div>','SceneForge Animate · Phase 3.0.1</div>',1)

# Styles for provider checks.
s=s.replace('.goodText{color:var(--good)}.badText{color:var(--bad)}.warnText{color:var(--warn)}', '.goodText{color:var(--good)}.badText{color:var(--bad)}.warnText{color:var(--warn)}.apiCheckGrid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:9px}.apiCheck{border:1px solid #30415d;background:#0b111a;border-radius:8px;padding:7px;font-size:9px;line-height:1.35}.apiCheck b{display:block;margin-bottom:3px}.apiCheck.ok{border-color:#397453}.apiCheck.fail{border-color:#713846}.apiCheck.testing{border-color:#6c6195}.apiActions{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:7px}.apiActions button{font-size:9px;padding:6px}.endpoint{font-family:ui-monospace,monospace;color:#8194b2;word-break:break-all;font-size:8px}')

# API validation controls.
old='''    <div class="hint">千问AI平台（qianwenai.com）按量付费 Key 直接填写完整的 <b>sk-ws-...</b>。无需 Workspace ID，也无需选择区域。测试版 Key 只保存在当前浏览器 session。Qwen 默认使用 qwen-image-3.0-pro；Meshy 默认使用 latest。</div>\n  </div>'''
new='''    <div class="hint">千问AI平台（qianwenai.com）按量付费 Key 直接填写完整的 <b>sk-ws-...</b>。无需 Workspace ID，也无需选择区域。测试版 Key 只保存在当前浏览器 session。Qwen 默认使用 qwen-image-3.0-pro；Meshy 默认使用 latest。</div>\n    <div class="apiActions"><button id="verifyDeepseek">验证 DeepSeek</button><button id="verifyQwen">验证 Qwen</button><button id="verifyMeshy">验证 Meshy</button><button id="verifyAll" class="goodBtn">全部验证</button></div>\n    <div class="apiCheckGrid">\n      <div id="deepseekCheck" class="apiCheck"><b>DeepSeek · 未验证</b><span>等待验证</span></div>\n      <div id="qwenCheck" class="apiCheck"><b>Qwen · 未验证</b><span>等待验证</span></div>\n      <div id="meshyCheck" class="apiCheck"><b>Meshy · 未验证</b><span>等待验证</span></div>\n      <div class="apiCheck"><b>Qwen Endpoint</b><span class="endpoint">dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation</span></div>\n    </div>\n  </div>'''
if old not in s: raise SystemExit('API settings anchor not found')
s=s.replace(old,new,1)

# UI refs.
s=s.replace("qwenKey:$('qwenKey'),trace:$('trace')", "qwenKey:$('qwenKey'),verifyDeepseek:$('verifyDeepseek'),verifyQwen:$('verifyQwen'),verifyMeshy:$('verifyMeshy'),verifyAll:$('verifyAll'),deepseekCheck:$('deepseekCheck'),qwenCheck:$('qwenCheck'),meshyCheck:$('meshyCheck'),trace:$('trace')")

# Provider state.
s=s.replace("let storyAnalysis=null,shotPlan=null,projectPlan=null,planApproved=false,history=[],jobs=[],inventory=[],lastSelected=null,planningBusy=false,generationBusy=false;", "let storyAnalysis=null,shotPlan=null,projectPlan=null,planApproved=false,history=[],jobs=[],inventory=[],lastSelected=null,planningBusy=false,generationBusy=false;\nconst apiState={deepseek:{state:'idle',message:'未验证'},qwen:{state:'idle',message:'未验证'},meshy:{state:'idle',message:'未验证'}};")

# Helpers after sleep.
needle="function sleep(ms){return new Promise(r=>setTimeout(r,ms))}"
helpers=r'''function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function round1(n){return Math.round(Number(n||0)*10)/10}
function fmtProgress(n){const x=round1(n);return `${Number.isInteger(x)?x:x.toFixed(1)}%`}
function providerError(provider,e,endpoint=''){const msg=String(e?.message||e||'未知错误');if(e instanceof TypeError||/Failed to fetch|NetworkError|Load failed/i.test(msg))return `${provider} 无法连接：浏览器请求被网络或 CORS 拦截${endpoint?`（${endpoint}）`:''}`;return `${provider}: ${msg}`}
function setApiState(name,state,message){apiState[name]={state,message};const map={deepseek:ui.deepseekCheck,qwen:ui.qwenCheck,meshy:ui.meshyCheck},label={deepseek:'DeepSeek',qwen:'Qwen',meshy:'Meshy'},el=map[name];if(!el)return;el.className=`apiCheck ${state==='ok'?'ok':state==='fail'?'fail':state==='testing'?'testing':''}`;el.innerHTML=`<b>${label[name]} · ${state==='ok'?'通过':state==='fail'?'失败':state==='testing'?'验证中':'未验证'}</b><span>${esc(message)}</span>`}
function httpMeaning(provider,status,text){if(status===401||status===403)return `${provider} 鉴权失败（HTTP ${status}），请检查 API Key/权限`;if(status===402)return `${provider} 余额或计费状态异常（HTTP 402）`;if(status===429)return `${provider} 已连通，但触发限流/额度限制（HTTP 429）`;if(status>=500)return `${provider} 服务端错误（HTTP ${status}）`;return `${provider} HTTP ${status}${text?`：${String(text).slice(0,160)}`:''}`}
'''
if needle not in s: raise SystemExit('sleep helper anchor missing')
s=s.replace(needle,helpers,1)

# Job percent formatting and storage rounding.
s=s.replace("${esc(j.message)} · ${j.progress}%", "${esc(j.message)} · ${fmtProgress(j.progress)}")
s=s.replace("function setJob(job,progress,message,status=job.status){job.progress=clamp(progress,0,100);", "function setJob(job,progress,message,status=job.status){job.progress=round1(clamp(progress,0,100));")

# Replace Qwen implementation with user's official reference structure.
start=s.index("function qwenEndpoint(){")
end=s.index("\nasync function meshyCreate",start)
qwen=r'''function qwenEndpoint(){return 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'}
function extractQwenImage(j){return j?.output?.choices?.[0]?.message?.content?.find(x=>x?.image)?.image||j?.output?.results?.[0]?.url||j?.data?.[0]?.url||null}
async function qwenImage(prompt,job,base=0,span=100){
  const key=ui.qwenKey.value.trim();if(!key)throw new Error('请填写千问AI平台 API Key（sk-ws-...）');
  session.set('sf3_qwen',key);setJob(job,base+span*.12,'Qwen Image 请求已发送','generating');
  let fake=base+span*.12;const timer=setInterval(()=>{fake=Math.min(base+span*.82,fake+span*.035);setJob(job,fake,'Qwen Image 正在生成','generating')},900);
  try{
    let r;
    try{r=await fetch(qwenEndpoint(),{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`},body:JSON.stringify({model:'qwen-image-3.0-pro',input:{messages:[{role:'user',content:[{text:prompt}]}]},parameters:{prompt_extend:true}})})}
    catch(e){throw new Error(providerError('Qwen',e,'dashscope.aliyuncs.com'))}
    if(!r.ok){const text=await r.text();throw new Error(httpMeaning('Qwen',r.status,text))}
    const j=await r.json(),url=extractQwenImage(j);if(!url)throw new Error(`Qwen 已响应，但未找到图片 URL：${JSON.stringify(j).slice(0,400)}`);
    clearInterval(timer);setJob(job,base+span,'Qwen Image 完成','generating');return{url,filename:`${job.assetId}.png`,provider:'qwen-image-3.0-pro',raw:j};
  }finally{clearInterval(timer)}
}'''
s=s[:start]+qwen+s[end:]

# Add API validation before generation functions.
anchor='async function meshyCreate(path,body){'
validation=r'''async function verifyDeepseek(){
  const key=ui.deepseekKey.value.trim();if(!key){setApiState('deepseek','fail','未填写 API Key');return false}setApiState('deepseek','testing','正在连接 api.deepseek.com/models…');
  try{const r=await fetch('https://api.deepseek.com/models',{headers:{Authorization:`Bearer ${key}`}});const text=await r.text();if(r.ok){setApiState('deepseek','ok',`连接和鉴权成功（HTTP ${r.status}）`);return true}setApiState('deepseek','fail',httpMeaning('DeepSeek',r.status,text));return false}catch(e){setApiState('deepseek','fail',providerError('DeepSeek',e,'api.deepseek.com'));return false}}
async function verifyQwen(){
  const key=ui.qwenKey.value.trim();if(!key){setApiState('qwen','fail','未填写 API Key');return false}if(!key.startsWith('sk-ws-')){setApiState('qwen','fail','Key 应以 sk-ws- 开头');return false}setApiState('qwen','testing','正在探测 DashScope 图片接口（不会生成有效图片）…');
  try{const r=await fetch(qwenEndpoint(),{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`},body:JSON.stringify({model:'qwen-image-3.0-pro',input:{messages:[{role:'user',content:[]}]},parameters:{prompt_extend:false}})});const text=await r.text();if(r.ok){setApiState('qwen','ok',`接口可达且鉴权成功（HTTP ${r.status}）`);return true}if([400,422].includes(r.status)){setApiState('qwen','ok',`接口可达、鉴权已通过；测试请求被参数校验拦截（HTTP ${r.status}，未生成图片）`);return true}setApiState('qwen','fail',httpMeaning('Qwen',r.status,text));return false}catch(e){setApiState('qwen','fail',providerError('Qwen',e,'dashscope.aliyuncs.com'));return false}}
async function verifyMeshy(){
  const key=ui.meshyKey.value.trim();if(!key){setApiState('meshy','fail','未填写 API Key');return false}setApiState('meshy','testing','正在连接 api.meshy.ai…');
  try{const r=await fetch('https://api.meshy.ai/openapi/v2/text-to-3d',{headers:{Authorization:`Bearer ${key}`}});const text=await r.text();if(r.ok||[400,404,405].includes(r.status)){setApiState('meshy','ok',`接口可达且鉴权未被拒绝（HTTP ${r.status}）`);return true}setApiState('meshy','fail',httpMeaning('Meshy',r.status,text));return false}catch(e){setApiState('meshy','fail',providerError('Meshy',e,'api.meshy.ai'));return false}}
async function verifyAll(){ui.verifyAll.disabled=true;try{const results=await Promise.all([verifyDeepseek(),verifyQwen(),verifyMeshy()]);toast(results.every(Boolean)?'三个 API 均验证通过':'有 API 未通过，请查看验证状态')}finally{ui.verifyAll.disabled=false}}
async function preflightForPlan(){const approved=projectPlan?.assets?.filter(a=>a.approved)||[],needQwen=approved.some(a=>['qwen_image','qwen_to_meshy_3d'].includes(a.route)),needMeshy=approved.some(a=>['meshy_text_3d','qwen_to_meshy_3d'].includes(a.route));const checks=[];if(needQwen&&apiState.qwen.state!=='ok')checks.push(verifyQwen());if(needMeshy&&apiState.meshy.state!=='ok')checks.push(verifyMeshy());if(!checks.length)return true;const result=await Promise.all(checks);return result.every(Boolean)}

'''
if anchor not in s: raise SystemExit('meshy anchor missing')
s=s.replace(anchor,validation+anchor,1)

# Wrap Meshy create fetch error for better message.
s=s.replace("const r=await fetch(`https://api.meshy.ai${path}`,{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`},body:JSON.stringify(body)});", "let r;try{r=await fetch(`https://api.meshy.ai${path}`,{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`},body:JSON.stringify(body)})}catch(e){throw new Error(providerError('Meshy',e,'api.meshy.ai'))};")

# Preflight before creating jobs.
old_start="async function startGeneration(){if(generationBusy||!planApproved||!projectPlan)return;const approved=projectPlan.assets.filter(a=>a.approved);if(!approved.length){toast('没有已批准的资产');return}generationBusy=true;ui.startBtn.disabled=true;jobs=approved.map(newJob);"
new_start="async function startGeneration(){if(generationBusy||!planApproved||!projectPlan)return;const approved=projectPlan.assets.filter(a=>a.approved);if(!approved.length){toast('没有已批准的资产');return}ui.startBtn.disabled=true;ui.approvalStatus.innerHTML='<span class=\"warnText\">正在验证本次生成所需 API…</span>';const preflightOk=await preflightForPlan();if(!preflightOk){ui.startBtn.disabled=false;ui.approvalStatus.innerHTML='<span class=\"badText\">API 预检失败，请先修复上方 API 状态。</span>';toast('API 预检失败，尚未开始资产生成');return}generationBusy=true;ui.approvalStatus.innerHTML='<span class=\"goodText\">API 预检通过，开始生成资产。</span>';jobs=approved.map(newJob);"
if old_start not in s: raise SystemExit('startGeneration anchor missing')
s=s.replace(old_start,new_start,1)

# Wire validation buttons.
handler="ui.uploadInput.onchange=()=>handleUploads([...ui.uploadInput.files]);ui.planBtn.onclick=createPlan;ui.startBtn.onclick=startGeneration;"
replace="ui.verifyDeepseek.onclick=verifyDeepseek;ui.verifyQwen.onclick=verifyQwen;ui.verifyMeshy.onclick=verifyMeshy;ui.verifyAll.onclick=verifyAll;ui.uploadInput.onchange=()=>handleUploads([...ui.uploadInput.files]);ui.planBtn.onclick=createPlan;ui.startBtn.onclick=startGeneration;"
if handler not in s: raise SystemExit('handler anchor missing')
s=s.replace(handler,replace,1)

# Reset API validation on key edits.
old_for="for(const [el,key] of [[ui.deepseekKey,'sf3_deepseek'],[ui.meshyKey,'sf3_meshy'],[ui.qwenKey,'sf3_qwen']])el.addEventListener('change',()=>session.set(key,el.value.trim()));"
new_for="for(const [el,key,name] of [[ui.deepseekKey,'sf3_deepseek','deepseek'],[ui.meshyKey,'sf3_meshy','meshy'],[ui.qwenKey,'sf3_qwen','qwen']])el.addEventListener('change',()=>{session.set(key,el.value.trim());setApiState(name,'idle','Key 已修改，请重新验证')});"
if old_for not in s: raise SystemExit('key handler anchor missing')
s=s.replace(old_for,new_for,1)

p.write_text(s,encoding='utf-8')
