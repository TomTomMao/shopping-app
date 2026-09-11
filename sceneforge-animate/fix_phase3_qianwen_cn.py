from pathlib import Path
p=Path('sceneforge-animate/phase3.html')
s=p.read_text(encoding='utf-8')
s=s.replace('''    <div class="settings">\n      <div class="field"><label>Workspace ID</label><input id="workspaceId" placeholder="ws-... / workspace id"/></div>\n      <div class="field"><label>Model Studio 区域</label><select id="qwenRegion"><option value="ap-northeast-1" selected>东京</option><option value="ap-southeast-1">新加坡</option><option value="cn-beijing">北京</option><option value="cn-hongkong">香港</option><option value="eu-central-1">法兰克福</option></select></div>\n    </div>\n    <div class="hint">测试版 Key 只保存在当前浏览器 session。Qwen 默认使用 qwen-image-3.0-pro；Meshy 默认使用 latest。</div>''','''    <div class="hint">千问AI平台（qianwenai.com）按量付费 Key 直接填写完整的 <b>sk-ws-...</b>。无需 Workspace ID，也无需选择区域。测试版 Key 只保存在当前浏览器 session。Qwen 默认使用 qwen-image-3.0-pro；Meshy 默认使用 latest。</div>''')
s=s.replace("workspaceId:$('workspaceId'),qwenRegion:$('qwenRegion'),","")
s=s.replace("ui.workspaceId.value=session.get('sf3_workspace');ui.qwenRegion.value=session.get('sf3_region')||'ap-northeast-1';","")
s=s.replace("[ui.qwenKey,'sf3_qwen'],[ui.workspaceId,'sf3_workspace'],[ui.qwenRegion,'sf3_region']","[ui.qwenKey,'sf3_qwen']")
start=s.index('function qwenEndpoint(){')
end=s.index('\nasync function meshyCreate',start)
new=r'''function qwenEndpoint(){return 'https://dashscope.aliyuncs.com/compatible-mode/v1/images/generations'}
async function qwenImage(prompt,job,base=0,span=100){
  const key=ui.qwenKey.value.trim();if(!key)throw new Error('请填写千问AI平台 API Key（sk-ws-...）');
  session.set('sf3_qwen',key);setJob(job,base+span*.12,'Qwen Image 请求已发送','generating');
  let fake=base+span*.12;const timer=setInterval(()=>{fake=Math.min(base+span*.82,fake+span*.035);setJob(job,fake,'Qwen Image 正在生成','generating')},900);
  try{
    const r=await fetch(qwenEndpoint(),{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${key}`},body:JSON.stringify({model:'qwen-image-3.0-pro',prompt,size:'1024x1024',n:1,prompt_extend:true,prompt_extend_mode:'direct',enable_thinking:true,watermark:false})});
    if(!r.ok)throw new Error(`Qwen ${r.status}: ${(await r.text()).slice(0,500)}`);
    const j=await r.json();const url=j.data?.[0]?.url;if(!url)throw new Error('Qwen 返回中没有图片 URL');
    clearInterval(timer);setJob(job,base+span,'Qwen Image 完成','generating');return{url,filename:`${job.assetId}.png`,provider:'qwen-image-3.0-pro',raw:j};
  }finally{clearInterval(timer)}
}'''
s=s[:start]+new+s[end:]
s=s.replace('Alibaba Model Studio API Key','千问AI平台 API Key（qianwenai.com）')
s=s.replace('placeholder="sk-..."','placeholder="sk-ws-..."',1 if False else 0)
# only replace qwen placeholder safely
s=s.replace('<input id="qwenKey" type="password" placeholder="sk-..."/>','<input id="qwenKey" type="password" placeholder="sk-ws-..."/>')
p.write_text(s,encoding='utf-8')
