from pathlib import Path
p=Path('sceneforge-animate/phase141.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Phase 1.4.1','Phase 1.5')
s=s.replace('Director → orientation QA → resilient Repair JSON','Director → visual QA / user video feedback → Repair JSON')

# CSS
s=s.replace('.validation{font-size:10px;line-height:1.45;padding:7px;border-radius:8px;background:#0b1018;border:1px solid #31415b;margin-bottom:7px}', '.validation{font-size:10px;line-height:1.45;padding:7px;border-radius:8px;background:#0b1018;border:1px solid #31415b;margin-bottom:7px}.tabBar{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px}.tabBtn{background:#0d1420;color:#9dadc5;border:1px solid #30415d}.tabBtn.active{background:#25385e;color:#fff;border-color:#6680ba}.tabPanel{display:none}.tabPanel.active{display:block}.videoPreview{width:100%;max-height:180px;background:#05080d;border:1px solid #30415d;border-radius:9px;margin:6px 0}.miniText{height:82px!important}.modePill{font-size:9px;color:#b7c5dc;border:1px solid #405274;padding:2px 6px;border-radius:999px}')

old_card='''  <div class="card"><h3>视觉自检设置</h3>
    <div class="row">
      <div class="field"><label>每秒采样帧数</label>
        <select id="sampleFps"><option value="0.25">0.25 fps</option><option value="0.5">0.5 fps</option><option value="1" selected>1 fps</option><option value="2">2 fps</option></select>
      </div>
      <div class="field"><label>最多图片数</label><input id="maxImages" type="number" min="9" max="90" step="3" value="45"/></div>
    </div>
    <div class="hint">每个采样时刻截 3 张：导演视角、左侧视角、右侧视角。还会计算角色 forward、移动方向和互动目标的朝向点积。若超过图片上限，会均匀抽样时间点，但始终成组三视角。</div>
    <div class="row" style="margin-top:8px"><button id="review">👁 多视角自检</button><button id="applyRepair" class="apply" disabled>✓ 应用修复</button></div>
    <label class="check"><input id="autoReview" type="checkbox"/> Agent 生成后自动视觉自检</label>
  </div>'''
new_card='''  <div class="card"><h3>视觉反馈</h3>
    <div class="tabBar"><button id="qaTab" class="tabBtn active">多视角自检</button><button id="videoTab" class="tabBtn">用户视频反馈</button></div>
    <div id="qaPanel" class="tabPanel active">
      <div class="row">
        <div class="field"><label>每秒采样帧数</label><select id="sampleFps"><option value="0.25">0.25 fps</option><option value="0.5">0.5 fps</option><option value="1" selected>1 fps</option><option value="2">2 fps</option></select></div>
        <div class="field"><label>最多图片数</label><input id="maxImages" type="number" min="9" max="90" step="3" value="45"/></div>
      </div>
      <div class="hint">每个采样时刻截 director / left / right 三视图，并计算朝向点积。</div>
      <button id="review" style="width:100%;margin-top:8px">👁 多视角自检</button>
      <label class="check"><input id="autoReview" type="checkbox"/> Agent 生成后自动视觉自检</label>
    </div>
    <div id="videoPanel" class="tabPanel">
      <div class="field"><label>上传反馈视频</label><input id="feedbackVideo" type="file" accept="video/*"/></div>
      <video id="feedbackPreview" class="videoPreview" controls muted playsinline></video>
      <div class="field"><label>你看到的问题</label><textarea id="feedbackText" class="miniText" placeholder="例如：0–4 秒蓝色机器人一直背对前进方向；希望它面朝运动方向。"></textarea></div>
      <div class="row">
        <div class="field"><label>视频抽帧 fps</label><select id="videoFps"><option value="0.25">0.25 fps</option><option value="0.5">0.5 fps</option><option value="1" selected>1 fps</option><option value="2">2 fps</option></select></div>
        <div class="field"><label>最多视频帧</label><input id="maxVideoFrames" type="number" min="4" max="48" value="24"/></div>
      </div>
      <button id="videoReview" style="width:100%">🎬 分析视频并生成修复</button>
      <div class="hint" style="margin-top:7px">视频只在浏览器本地抽帧；送给 Agent 的是抽取后的图片帧、时间戳和你的文字反馈。</div>
    </div>
    <div class="row" style="margin-top:9px"><button id="applyRepair" class="apply" disabled>✓ 应用修复</button></div>
  </div>'''
if old_card not in s: raise SystemExit('visual feedback card not found')
s=s.replace(old_card,new_card,1)

# Result card title
s=s.replace('<div class="card"><h3>视觉自检采样</h3><div id="sampleInfo"', '<div class="card"><h3>视觉反馈帧 <span id="feedbackMode" class="modePill">多视角</span></h3><div id="sampleInfo"')
s=s.replace('点击“多视角自检”后显示。','运行多视角自检或视频反馈后显示。')

# UI refs
old="""  clearContext:$('clearContext'),clearKey:$('clearKey'),sampleFps:$('sampleFps'),maxImages:$('maxImages'),review:$('review'),
  applyRepair:$('applyRepair'),autoReview:$('autoReview'),thinking:$('thinking'),logs:$('logs'),stage:$('stage'),"""
new="""  clearContext:$('clearContext'),clearKey:$('clearKey'),qaTab:$('qaTab'),videoTab:$('videoTab'),qaPanel:$('qaPanel'),videoPanel:$('videoPanel'),sampleFps:$('sampleFps'),maxImages:$('maxImages'),review:$('review'),
  feedbackVideo:$('feedbackVideo'),feedbackPreview:$('feedbackPreview'),feedbackText:$('feedbackText'),videoFps:$('videoFps'),maxVideoFrames:$('maxVideoFrames'),videoReview:$('videoReview'),applyRepair:$('applyRepair'),autoReview:$('autoReview'),thinking:$('thinking'),logs:$('logs'),stage:$('stage'),"""
if old not in s: raise SystemExit('ui refs anchor not found')
s=s.replace(old,new,1)
s=s.replace("  assets:$('assets'),sampleInfo:$('sampleInfo'),keyframes:$('keyframes'),validation:$('validation'),", "  assets:$('assets'),feedbackMode:$('feedbackMode'),sampleInfo:$('sampleInfo'),keyframes:$('keyframes'),validation:$('validation'),")
s=s.replace("let templates={},actors=new Map(),plan=null,timeline={actions:[]},pendingRepair=null,history=[],playing=false,current=0,last=performance.now(),cameraDriven=true,lastFrames=[];", "let templates={},actors=new Map(),plan=null,timeline={actions:[]},pendingRepair=null,history=[],playing=false,current=0,last=performance.now(),cameraDriven=true,lastFrames=[],feedbackVideoUrl=null;")

# Add tab and video helpers before candidateTimes
anchor='function candidateTimes(){'
insert=r'''function setFeedbackTab(mode){
  const video=mode==='video';ui.qaTab.classList.toggle('active',!video);ui.videoTab.classList.toggle('active',video);ui.qaPanel.classList.toggle('active',!video);ui.videoPanel.classList.toggle('active',video);ui.feedbackMode.textContent=video?'用户视频':'多视角';
}
function waitEvent(el,name,timeout=8000){return new Promise((resolve,reject)=>{let timer;const done=()=>{cleanup();resolve()};const fail=()=>{cleanup();reject(new Error(`video ${name} failed`))};const cleanup=()=>{clearTimeout(timer);el.removeEventListener(name,done);el.removeEventListener('error',fail)};el.addEventListener(name,done,{once:true});el.addEventListener('error',fail,{once:true});timer=setTimeout(()=>{cleanup();reject(new Error(`video ${name} timeout`))},timeout)})}
async function seekVideo(video,time){if(Math.abs(video.currentTime-time)<.025)return;video.currentTime=Math.max(0,Math.min(time,Math.max(0,video.duration-.02)));await waitEvent(video,'seeked')}
function videoSampleTimes(duration){const fps=clamp(ui.videoFps.value,.25,2,1),step=1/fps,maxFrames=Math.floor(clamp(ui.maxVideoFrames.value,4,48,24)),all=[];for(let t=0;t<duration;t+=step)all.push(Math.min(duration-.03,Math.max(.02,t)));if(all.length<=maxFrames)return all;const out=[];for(let i=0;i<maxFrames;i++)out.push(all[Math.round(i*(all.length-1)/(maxFrames-1))]);return [...new Set(out)]}
async function extractFeedbackVideoFrames(){
  const file=ui.feedbackVideo.files?.[0];if(!file)throw new Error('请先上传反馈视频');
  const video=ui.feedbackPreview;if(!Number.isFinite(video.duration)||video.duration<=0){await waitEvent(video,'loadedmetadata')}
  const times=videoSampleTimes(video.duration),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),frames=[];
  const targetW=Math.min(640,video.videoWidth||640),targetH=Math.max(1,Math.round(targetW*(video.videoHeight||360)/(video.videoWidth||640)));canvas.width=targetW;canvas.height=targetH;
  ui.keyframes.innerHTML='';ui.sampleInfo.className='validation';ui.sampleInfo.textContent=`视频 ${video.duration.toFixed(2)}s，准备抽取 ${times.length} 帧…`;
  const oldTime=video.currentTime;video.pause();
  for(const t of times){await seekVideo(video,t);ctx.drawImage(video,0,0,targetW,targetH);const dataUrl=canvas.toDataURL('image/jpeg',.68);frames.push({time:t,view:'user-video',title:'用户反馈视频',caption:ui.feedbackText.value.trim(),dataUrl});const d=document.createElement('div');d.className='kf';d.innerHTML=`<img src="${dataUrl}" alt="user video"><div>${t.toFixed(2)}s · user-video</div>`;ui.keyframes.appendChild(d)}
  try{await seekVideo(video,oldTime)}catch{}
  lastFrames=frames;ui.feedbackMode.textContent='用户视频';ui.sampleInfo.className='validation good';ui.sampleInfo.textContent=`已从用户视频抽取 ${frames.length} 帧；反馈：${ui.feedbackText.value.trim()||'（无文字反馈）'}`;return frames;
}
const USER_VIDEO_REVIEW_SYSTEM=`You are SceneForge Animate repair agent. The user supplies a video showing an animation problem or desired correction, plus explicit text feedback and the current Director Plan. Treat the user's written feedback as authoritative. Inspect the sampled video frames to understand the issue. Return one COMPLETE corrected Director Plan JSON, not a patch. For facing/orientation complaints, use faceTarget for interactions and rely on runtime auto-facing for walk/run; do not invent arbitrary numeric rotationY unless unavoidable. Preserve unrelated parts of the current plan. Include assistant_message, review_summary, issues, title, summary, duration, assets, shots. Output JSON only.`;
async function reviewUserVideo(){
  if(!plan)return;ui.videoReview.disabled=true;ui.applyRepair.disabled=true;pendingRepair=null;
  try{
    status('正在从用户视频抽帧…','warn');const frames=await extractFeedbackVideoFrames();const feedback=ui.feedbackText.value.trim();
    const parts=[{type:'text',text:`USER FEEDBACK (authoritative): ${feedback||'User supplied a video demonstrating the problem.'}\n\nCURRENT DIRECTOR PLAN:\n${JSON.stringify(plan)}\n\nInspect the sampled video frames below and return a complete repaired plan. Preserve unrelated content.`}];
    for(const f of frames){parts.push({type:'text',text:`User video frame at t=${f.time.toFixed(2)}s`});parts.push({type:'image_url',image_url:{url:f.dataUrl,detail:'low'}})}
    status(`Repair Agent 正在分析 ${frames.length} 个用户视频帧…`,'warn');
    const content=await stream({model:'deepseek-flash',messages:[{role:'system',content:USER_VIDEO_REVIEW_SYSTEM},{role:'user',content:parts}],response_format:{type:'json_object'},thinking:{type:'enabled'},reasoning_effort:'high',max_tokens:10000});
    const raw=await parseValidateOrRepair(content,'用户视频反馈 Repair 输出',plan);pendingRepair=sanitize(raw);ui.reviewSummary.textContent=(raw.review_summary||'用户视频反馈分析完成')+(Array.isArray(raw.issues)&&raw.issues.length?'\n问题：'+raw.issues.join('；'):'');ui.repairJson.textContent=JSON.stringify(pendingRepair,null,2);ui.applyRepair.disabled=false;status('用户视频 Repair JSON 已通过校验，可应用','good');
  }catch(e){console.error(e);status(e.message,'bad');log(e.message);ui.validation.className='validation bad';ui.validation.textContent=`视频反馈修复失败：${e.message}`}
  finally{ui.videoReview.disabled=false}
}
'''
if anchor not in s: raise SystemExit('candidateTimes anchor missing')
s=s.replace(anchor,insert+anchor,1)

# Ensure multi-view identifies mode
s=s.replace("async function selfReview(){\n  if(!plan)return;", "async function selfReview(){\n  if(!plan)return;ui.feedbackMode.textContent='多视角';")

# Handlers
handler_anchor='ui.generate.onclick=generate;'
handlers="""ui.qaTab.onclick=()=>setFeedbackTab('qa');
ui.videoTab.onclick=()=>setFeedbackTab('video');
ui.feedbackVideo.onchange=()=>{if(feedbackVideoUrl)URL.revokeObjectURL(feedbackVideoUrl);const f=ui.feedbackVideo.files?.[0];feedbackVideoUrl=f?URL.createObjectURL(f):null;ui.feedbackPreview.src=feedbackVideoUrl||'';if(f){ui.feedbackMode.textContent='用户视频';ui.sampleInfo.className='validation';ui.sampleInfo.textContent=`已选择视频：${f.name}`}};
ui.videoReview.onclick=reviewUserVideo;
"""+handler_anchor
if handler_anchor not in s: raise SystemExit('handler anchor missing')
s=s.replace(handler_anchor,handlers,1)

# clear context preserves current animation but clears feedback/video context
old_clear="""ui.clearContext.onclick=()=>{
  history=[];pendingRepair=null;lastFrames=[];ui.applyRepair.disabled=true;ui.thinking.textContent='上下文已清除，当前动画保留。';ui.reviewSummary.textContent='尚未复审。';ui.repairJson.textContent='{}';ui.validation.className='validation';ui.validation.textContent='上下文已清除。当前动画仍保留。';ui.keyframes.innerHTML='<div class="hint">上下文已清除；当前动画未删除。</div>';log('已清除 Agent 对话上下文和复审缓存；当前动画保留。');
};"""
new_clear="""ui.clearContext.onclick=()=>{
  history=[];pendingRepair=null;lastFrames=[];ui.applyRepair.disabled=true;ui.thinking.textContent='上下文已清除，当前动画保留。';ui.reviewSummary.textContent='尚未复审。';ui.repairJson.textContent='{}';ui.validation.className='validation';ui.validation.textContent='上下文已清除。当前动画仍保留。';ui.keyframes.innerHTML='<div class="hint">上下文已清除；当前动画未删除。</div>';ui.feedbackText.value='';ui.feedbackVideo.value='';ui.feedbackPreview.removeAttribute('src');if(feedbackVideoUrl){URL.revokeObjectURL(feedbackVideoUrl);feedbackVideoUrl=null}ui.sampleInfo.className='validation';ui.sampleInfo.textContent='尚未采样。';log('已清除 Agent 对话上下文、视频反馈和复审缓存；当前动画保留。');
};"""
if old_clear not in s: raise SystemExit('clear context handler missing')
s=s.replace(old_clear,new_clear,1)

Path('sceneforge-animate/phase15.html').write_text(s,encoding='utf-8')
