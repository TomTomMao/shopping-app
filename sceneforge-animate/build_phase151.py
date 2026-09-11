from pathlib import Path
p=Path('sceneforge-animate/phase15.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Phase 1.5','Phase 1.5.1')
s=s.replace('Director → visual QA / user video feedback → Repair JSON','Director → multi-view QA / full-context text feedback → Repair JSON')
s=s.replace('.videoPreview{width:100%;max-height:180px;background:#05080d;border:1px solid #30415d;border-radius:9px;margin:6px 0}.miniText{height:82px!important}', '.miniText{height:120px!important}')
s=s.replace('运行多视角自检或视频反馈后显示。','运行多视角自检后显示；文本反馈会复用这里已有的全部视觉上下文。')

old='''    <div class="tabBar"><button id="qaTab" class="tabBtn active">多视角自检</button><button id="videoTab" class="tabBtn">用户视频反馈</button></div>
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
    </div>'''
new='''    <div class="tabBar"><button id="qaTab" class="tabBtn active">多视角自检</button><button id="feedbackTab" class="tabBtn">用户文本反馈</button></div>
    <div id="qaPanel" class="tabPanel active">
      <div class="row">
        <div class="field"><label>每秒采样帧数</label><select id="sampleFps"><option value="0.25">0.25 fps</option><option value="0.5">0.5 fps</option><option value="1" selected>1 fps</option><option value="2">2 fps</option></select></div>
        <div class="field"><label>最多图片数</label><input id="maxImages" type="number" min="9" max="90" step="3" value="45"/></div>
      </div>
      <div class="hint">每个采样时刻截 director / left / right 三视图，并计算朝向点积。</div>
      <button id="review" style="width:100%;margin-top:8px">👁 多视角自检</button>
      <label class="check"><input id="autoReview" type="checkbox"/> Agent 生成后自动视觉自检</label>
    </div>
    <div id="feedbackPanel" class="tabPanel">
      <div class="field"><label>你的修改反馈</label><textarea id="feedbackText" class="miniText" placeholder="例如：蓝色机器人走路时面朝方向反了。请保持原剧情，只修复所有走路/跑步朝向，并让互动时双方互相面对。"></textarea></div>
      <button id="textReview" style="width:100%">💬 根据完整上下文生成修复</button>
      <div class="hint" style="margin-top:7px">会发送完整 Agent 历史、当前 Director Plan、compiled timeline、当前时间/shot、运行时能力、资产信息、pending repair，以及最近一次多视角 QA 的全部诊断；若已有关键帧，也会一起附上。</div>
    </div>'''
if old not in s: raise SystemExit('feedback UI block not found')
s=s.replace(old,new,1)

oldrefs="""  clearContext:$('clearContext'),clearKey:$('clearKey'),qaTab:$('qaTab'),videoTab:$('videoTab'),qaPanel:$('qaPanel'),videoPanel:$('videoPanel'),sampleFps:$('sampleFps'),maxImages:$('maxImages'),review:$('review'),
  feedbackVideo:$('feedbackVideo'),feedbackPreview:$('feedbackPreview'),feedbackText:$('feedbackText'),videoFps:$('videoFps'),maxVideoFrames:$('maxVideoFrames'),videoReview:$('videoReview'),applyRepair:$('applyRepair'),autoReview:$('autoReview'),thinking:$('thinking'),logs:$('logs'),stage:$('stage'),"""
newrefs="""  clearContext:$('clearContext'),clearKey:$('clearKey'),qaTab:$('qaTab'),feedbackTab:$('feedbackTab'),qaPanel:$('qaPanel'),feedbackPanel:$('feedbackPanel'),sampleFps:$('sampleFps'),maxImages:$('maxImages'),review:$('review'),
  feedbackText:$('feedbackText'),textReview:$('textReview'),applyRepair:$('applyRepair'),autoReview:$('autoReview'),thinking:$('thinking'),logs:$('logs'),stage:$('stage'),"""
if oldrefs not in s: raise SystemExit('ui refs block not found')
s=s.replace(oldrefs,newrefs,1)
s=s.replace("let templates={},actors=new Map(),plan=null,timeline={actions:[]},pendingRepair=null,history=[],playing=false,current=0,last=performance.now(),cameraDriven=true,lastFrames=[],feedbackVideoUrl=null;", "let templates={},actors=new Map(),plan=null,timeline={actions:[]},pendingRepair=null,history=[],playing=false,current=0,last=performance.now(),cameraDriven=true,lastFrames=[];")

# Full history for normal director turns too.
s=s.replace("const context={maxAssets:Number(ui.limit.value),currentPlan:plan,history:history.slice(-5)};", "const context={maxAssets:Number(ui.limit.value),currentPlan:plan,history};")

start=s.index('function setFeedbackTab(mode){')
end=s.index('function candidateTimes(){',start)
replacement=r'''function setFeedbackTab(mode){
  const feedback=mode==='feedback';ui.qaTab.classList.toggle('active',!feedback);ui.feedbackTab.classList.toggle('active',feedback);ui.qaPanel.classList.toggle('active',!feedback);ui.feedbackPanel.classList.toggle('active',feedback);ui.feedbackMode.textContent=feedback?'文本反馈':'多视角';
}
function fullContextSnapshot(){
  const sh=plan?shotAt(current):null;
  return {
    contextVersion:'phase-1.5.1-full',
    userFeedbackMode:'text',
    maxAssets:Number(ui.limit.value),
    currentTime:Number(current.toFixed(3)),
    currentShot:sh?structuredClone(sh):null,
    currentPlan:plan?structuredClone(plan):null,
    pendingRepair:pendingRepair?structuredClone(pendingRepair):null,
    compiledTimeline:structuredClone(timeline),
    currentOrientationDiagnostics:plan?orientationDiagnostics(current):[],
    runtime:{catalog:CATALOG,cameraPresets:CAM,actions:ACTIONS,modelForwardOffset:MODEL_FORWARD_OFFSET,autoFacingRules:{walkRun:'runtime faces movement direction',interaction:'prefer faceTarget',numericRotationY:'avoid unless necessary'}},
    agentHistory:structuredClone(history),
    latestVisualQA:lastFrames.map(f=>({time:f.time,view:f.view,title:f.title,caption:f.caption,orientation:f.orientation||null,warnings:f.warnings||[]}))
  };
}
const USER_TEXT_REVIEW_SYSTEM=`You are the SceneForge Animate revision agent. The user provides TEXT feedback about the current generated animation. You are given the COMPLETE project context: full agent history, current Director Plan, compiled runtime timeline, current playback state, supported assets/actions/cameras, pending repair if any, and all metadata from the latest multi-view visual QA. If visual QA keyframes are attached, inspect all of them too. Treat the newest user feedback as authoritative while preserving all unrelated intent and continuity from prior context. Return one COMPLETE corrected Director Plan JSON, not a patch. For locomotion facing issues, walk/run orientation is enforced by runtime movement vectors; correct movement destinations or facing intent rather than inventing arbitrary rotationY. For interactions, prefer face beats with faceTarget. Include assistant_message, review_summary, issues, title, summary, duration, assets, shots. Output JSON only.`;
async function reviewUserText(){
  if(!plan)return;const feedback=ui.feedbackText.value.trim();if(!feedback){status('请先输入文本反馈','warn');return}
  ui.textReview.disabled=true;ui.applyRepair.disabled=true;pendingRepair=null;
  try{
    const context=fullContextSnapshot();
    const parts=[{type:'text',text:`NEW USER FEEDBACK (highest priority):\n${feedback}\n\nCOMPLETE SCENEFORGE CONTEXT:\n${JSON.stringify(context)}\n\nReturn the complete revised Director Plan. Do not drop unchanged assets, shots, timing, or story details.`}];
    for(const f of lastFrames){parts.push({type:'text',text:`Existing multi-view QA frame: t=${Number(f.time).toFixed(2)}s view=${f.view} shot=${f.title||''} warnings=${(f.warnings||[]).join('; ')}`});if(f.dataUrl)parts.push({type:'image_url',image_url:{url:f.dataUrl,detail:'low'}})}
    status(`Revision Agent 正在读取完整上下文${lastFrames.length?` + ${lastFrames.length} 张已有 QA 帧`:''}…`,'warn');
    const content=await stream({model:'deepseek-flash',messages:[{role:'system',content:USER_TEXT_REVIEW_SYSTEM},{role:'user',content:parts}],response_format:{type:'json_object'},thinking:{type:'enabled'},reasoning_effort:'high',max_tokens:12000});
    const raw=await parseValidateOrRepair(content,'用户文本反馈 Repair 输出',plan);pendingRepair=sanitize(raw);
    history.push({event:'user_text_feedback',feedback,contextSnapshot:context,proposedPlan:structuredClone(pendingRepair),reviewSummary:raw.review_summary||'',issues:Array.isArray(raw.issues)?raw.issues:[]});
    ui.reviewSummary.textContent=(raw.review_summary||'文本反馈修订完成')+(Array.isArray(raw.issues)&&raw.issues.length?'\n问题：'+raw.issues.join('；'):'');ui.repairJson.textContent=JSON.stringify(pendingRepair,null,2);ui.applyRepair.disabled=false;ui.feedbackMode.textContent='文本反馈';status('文本反馈 Repair JSON 已通过校验，可应用','good');
  }catch(e){console.error(e);status(e.message,'bad');log(e.message);ui.validation.className='validation bad';ui.validation.textContent=`文本反馈修复失败：${e.message}`}
  finally{ui.textReview.disabled=false}
}
'''
s=s[:start]+replacement+s[end:]

# Record visual review in full context history.
needle="""    pendingRepair=sanitize(raw);
    ui.reviewSummary.textContent=(raw.review_summary||'复审完成')+(Array.isArray(raw.issues)&&raw.issues.length?'\\n问题：'+raw.issues.join('；'):'');"""
rep="""    pendingRepair=sanitize(raw);
    history.push({event:'multiview_visual_review',reviewSummary:raw.review_summary||'',issues:Array.isArray(raw.issues)?raw.issues:[],proposedPlan:structuredClone(pendingRepair),frames:lastFrames.map(f=>({time:f.time,view:f.view,title:f.title,caption:f.caption,orientation:f.orientation||null,warnings:f.warnings||[]}))});
    ui.reviewSummary.textContent=(raw.review_summary||'复审完成')+(Array.isArray(raw.issues)&&raw.issues.length?'\\n问题：'+raw.issues.join('；'):'');"""
if needle not in s: raise SystemExit('self review history anchor missing')
s=s.replace(needle,rep,1)

oldhandlers="""ui.qaTab.onclick=()=>setFeedbackTab('qa');
ui.videoTab.onclick=()=>setFeedbackTab('video');
ui.feedbackVideo.onchange=()=>{if(feedbackVideoUrl)URL.revokeObjectURL(feedbackVideoUrl);const f=ui.feedbackVideo.files?.[0];feedbackVideoUrl=f?URL.createObjectURL(f):null;ui.feedbackPreview.src=feedbackVideoUrl||'';if(f){ui.feedbackMode.textContent='用户视频';ui.sampleInfo.className='validation';ui.sampleInfo.textContent=`已选择视频：${f.name}`}};
ui.videoReview.onclick=reviewUserVideo;"""
newhandlers="""ui.qaTab.onclick=()=>setFeedbackTab('qa');
ui.feedbackTab.onclick=()=>setFeedbackTab('feedback');
ui.textReview.onclick=reviewUserText;"""
if oldhandlers not in s: raise SystemExit('feedback handlers not found')
s=s.replace(oldhandlers,newhandlers,1)

oldclear="""ui.clearContext.onclick=()=>{
  history=[];pendingRepair=null;lastFrames=[];ui.applyRepair.disabled=true;ui.thinking.textContent='上下文已清除，当前动画保留。';ui.reviewSummary.textContent='尚未复审。';ui.repairJson.textContent='{}';ui.validation.className='validation';ui.validation.textContent='上下文已清除。当前动画仍保留。';ui.keyframes.innerHTML='<div class="hint">上下文已清除；当前动画未删除。</div>';ui.feedbackText.value='';ui.feedbackVideo.value='';ui.feedbackPreview.removeAttribute('src');if(feedbackVideoUrl){URL.revokeObjectURL(feedbackVideoUrl);feedbackVideoUrl=null}ui.sampleInfo.className='validation';ui.sampleInfo.textContent='尚未采样。';log('已清除 Agent 对话上下文、视频反馈和复审缓存；当前动画保留。');
};"""
newclear="""ui.clearContext.onclick=()=>{
  history=[];pendingRepair=null;lastFrames=[];ui.applyRepair.disabled=true;ui.thinking.textContent='上下文已清除，当前动画保留。';ui.reviewSummary.textContent='尚未复审。';ui.repairJson.textContent='{}';ui.validation.className='validation';ui.validation.textContent='上下文已清除。当前动画仍保留。';ui.keyframes.innerHTML='<div class="hint">上下文已清除；当前动画未删除。</div>';ui.feedbackText.value='';ui.sampleInfo.className='validation';ui.sampleInfo.textContent='尚未采样。';log('已清除 Agent 完整历史、文本反馈和复审缓存；当前动画保留。');
};"""
if oldclear not in s: raise SystemExit('clear handler not found')
s=s.replace(oldclear,newclear,1)

Path('sceneforge-animate/phase151.html').write_text(s,encoding='utf-8')
