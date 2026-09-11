from pathlib import Path
p=Path('sceneforge-animate/phase151.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Phase 1.5.1','Phase 1.5.2')
s=s.replace('Director → multi-view QA / full-context text feedback → Repair JSON','Director → full-context feedback → plan + runtime calibration')

s=s.replace("const MODEL_FORWARD_OFFSET={robot:Math.PI,fox:0};", "const MODEL_FORWARD_OFFSET={robot:Math.PI,fox:0};\n// Empirical visual calibration: user observed Running faces correctly while the other RobotExpressive clips read 180° reversed.\nconst DEFAULT_RUNTIME_CONFIG={clipYawCorrection:{robot:{Idle:Math.PI,Walking:Math.PI,Running:0,Dance:Math.PI,Wave:Math.PI,Jump:Math.PI,Yes:Math.PI,No:Math.PI,Punch:Math.PI,ThumbsUp:Math.PI,Standing:Math.PI,Sitting:Math.PI},fox:{Survey:0,Walk:0,Run:0}}};\nlet runtimeConfig=structuredClone(DEFAULT_RUNTIME_CONFIG),pendingRuntimePatch=null;")
s=s.replace("let templates={},actors=new Map(),plan=null,timeline={actions:[]},pendingRepair=null,history=[],playing=false,current=0,last=performance.now(),cameraDriven=true,lastFrames=[];", "let templates={},actors=new Map(),plan=null,timeline={actions:[]},pendingRepair=null,history=[],playing=false,current=0,last=performance.now(),cameraDriven=true,lastFrames=[];")

old_create="""function createActor(spec){
  const tpl=templates[spec.type]||fallback();
  let model;try{model=SkeletonUtils.clone(tpl.scene)}catch{model=fallback().scene}
  model.traverse(n=>{if(n.isMesh){n.visible=true;n.frustumCulled=false}});
  model.scale.setScalar(spec.type==='fox'?.04:1);
  const wrap=new THREE.Group();wrap.add(model);world.add(wrap);
  const mixer=new THREE.AnimationMixer(model),actions={};
  for(const cl of tpl.animations||[])actions[cl.name]=mixer.clipAction(cl);
  actors.set(spec.id,{spec,wrap,mixer,actions,currentClip:null});
}
function setClip(a,name,t){
  const n=(CATALOG[a.spec.type]?.clips||[]).find(x=>x.toLowerCase()===String(name).toLowerCase());
  if(!n||!a.actions[n])return;
  if(a.currentClip!==n){a.mixer.stopAllAction();a.actions[n].reset().play();a.currentClip=n}
  a.mixer.setTime(Math.max(0,t));
}"""
new_create="""function createActor(spec){
  const tpl=templates[spec.type]||fallback();
  let model;try{model=SkeletonUtils.clone(tpl.scene)}catch{model=fallback().scene}
  model.traverse(n=>{if(n.isMesh){n.visible=true;n.frustumCulled=false}});
  model.scale.setScalar(spec.type==='fox'?.04:1);
  const wrap=new THREE.Group(),visualPivot=new THREE.Group();visualPivot.add(model);wrap.add(visualPivot);world.add(wrap);
  const mixer=new THREE.AnimationMixer(model),actions={};
  for(const cl of tpl.animations||[])actions[cl.name]=mixer.clipAction(cl);
  actors.set(spec.id,{spec,wrap,visualPivot,model,mixer,actions,currentClip:null});
}
function clipYawCorrection(type,clip){return Number(runtimeConfig?.clipYawCorrection?.[type]?.[clip]||0)}
function setClip(a,name,t){
  const n=(CATALOG[a.spec.type]?.clips||[]).find(x=>x.toLowerCase()===String(name).toLowerCase());
  if(!n||!a.actions[n])return;
  a.visualPivot.rotation.y=clipYawCorrection(a.spec.type,n);
  if(a.currentClip!==n){a.mixer.stopAllAction();a.actions[n].reset().play();a.currentClip=n}
  a.mixer.setTime(Math.max(0,t));
}"""
if old_create not in s: raise SystemExit('create actor block missing')
s=s.replace(old_create,new_create,1)

# Preserve null rotationY; Number(null) must not become zero.
s=s.replace("rotationY:Number.isFinite(Number(b.rotationY))?clamp(b.rotationY,-6.3,6.3,0):null", "rotationY:b.rotationY!==null&&b.rotationY!==undefined&&Number.isFinite(Number(b.rotationY))?clamp(b.rotationY,-6.3,6.3,0):null")

# Runtime patch validation/apply helpers before fullContextSnapshot.
anchor='function fullContextSnapshot(){'
helpers=r'''function normalizeRuntimePatch(raw){
  if(!raw||typeof raw!=='object')return null;const src=raw.runtime_patch||raw.runtimePatch||raw.runtime||null;if(!src||typeof src!=='object')return null;
  const patch={clipYawCorrection:{}};let changed=false;
  const table=src.clipYawCorrection||src.clip_yaw_correction||{};
  for(const type of ['robot','fox']){if(!table[type]||typeof table[type]!=='object')continue;for(const [clip,val] of Object.entries(table[type])){if(!(CATALOG[type]?.clips||[]).includes(clip))continue;const n=Number(val);if(!Number.isFinite(n))continue;if(!patch.clipYawCorrection[type])patch.clipYawCorrection[type]={};patch.clipYawCorrection[type][clip]=normAngle(n);changed=true}}
  return changed?patch:null;
}
function applyRuntimePatch(patch){if(!patch)return;for(const [type,clips] of Object.entries(patch.clipYawCorrection||{})){if(!runtimeConfig.clipYawCorrection[type])runtimeConfig.clipYawCorrection[type]={};for(const [clip,yaw] of Object.entries(clips))runtimeConfig.clipYawCorrection[type][clip]=yaw}log('已应用 runtime facing calibration：'+JSON.stringify(patch.clipYawCorrection));}
function formatIssues(xs){if(!Array.isArray(xs)||!xs.length)return'';return xs.map(x=>typeof x==='string'?x:(x?.detail||x?.message||x?.note||JSON.stringify(x))).join('；')}
'''
if anchor not in s: raise SystemExit('context anchor missing')
s=s.replace(anchor,helpers+anchor,1)

s=s.replace("runtime:{catalog:CATALOG,cameraPresets:CAM,actions:ACTIONS,modelForwardOffset:MODEL_FORWARD_OFFSET,autoFacingRules:{walkRun:'runtime faces movement direction',interaction:'prefer faceTarget',numericRotationY:'avoid unless necessary'}},", "runtime:{catalog:CATALOG,cameraPresets:CAM,actions:ACTIONS,modelForwardOffset:MODEL_FORWARD_OFFSET,runtimeConfig:structuredClone(runtimeConfig),autoFacingRules:{walkRun:'runtime faces movement direction',interaction:'prefer faceTarget',numericRotationY:'avoid unless necessary'},visualCalibrationRule:'clipYawCorrection is applied on a child visualPivot after logical world yaw. Use runtime_patch for clip/model facing bugs.'},")

old_sys="""const USER_TEXT_REVIEW_SYSTEM=`You are the SceneForge Animate revision agent. The user provides TEXT feedback about the current generated animation. You are given the COMPLETE project context: full agent history, current Director Plan, compiled runtime timeline, current playback state, supported assets/actions/cameras, pending repair if any, and all metadata from the latest multi-view visual QA. If visual QA keyframes are attached, inspect all of them too. Treat the newest user feedback as authoritative while preserving all unrelated intent and continuity from prior context. Return one COMPLETE corrected Director Plan JSON, not a patch. For locomotion facing issues, walk/run orientation is enforced by runtime movement vectors; correct movement destinations or facing intent rather than inventing arbitrary rotationY. For interactions, prefer face beats with faceTarget. Include assistant_message, review_summary, issues, title, summary, duration, assets, shots. Output JSON only.`;"""
new_sys="""const USER_TEXT_REVIEW_SYSTEM=`You are the SceneForge Animate revision agent. The user provides TEXT feedback about the current generated animation. You are given the COMPLETE project context: full agent history, current Director Plan, compiled runtime timeline, current playback state, supported assets/actions/cameras, runtimeConfig, pending repair if any, and all metadata from the latest multi-view visual QA. If visual QA keyframes are attached, inspect all of them too. Treat the newest user feedback as authoritative while preserving unrelated intent and continuity. Return one COMPLETE corrected Director Plan JSON. IMPORTANT: distinguish PLAN bugs from RUNTIME VISUAL CALIBRATION bugs. walk/run logical yaw is enforced by runtime movement vectors, so if the user says a character is visually walking/running backward while moveFacingDot is already near +1, do NOT keep changing plan rotationY: that indicates the rendered GLB/clip visual forward disagrees with the mathematical forward. In that case also return runtime_patch.clipYawCorrection with per-model/per-clip yaw correction in radians. A 180-degree flip is 3.141592653589793. If Running is reported correct but Walking/Idle/interaction clips are reversed, preserve Running=0 and flip only the clips that are visually reversed. For interactions, prefer face beats with faceTarget. Include assistant_message, review_summary, issues, optional runtime_patch, title, summary, duration, assets, shots. Output JSON only.`;"""
if old_sys not in s: raise SystemExit('text system missing')
s=s.replace(old_sys,new_sys,1)

# Capture runtime patch from text feedback and use readable issue formatting.
old="""    const raw=await parseValidateOrRepair(content,'用户文本反馈 Repair 输出',plan);pendingRepair=sanitize(raw);
    history.push({event:'user_text_feedback',feedback,contextSnapshot:context,proposedPlan:structuredClone(pendingRepair),reviewSummary:raw.review_summary||'',issues:Array.isArray(raw.issues)?raw.issues:[]});
    ui.reviewSummary.textContent=(raw.review_summary||'文本反馈修订完成')+(Array.isArray(raw.issues)&&raw.issues.length?'\\n问题：'+raw.issues.join('；'):'');ui.repairJson.textContent=JSON.stringify(pendingRepair,null,2);ui.applyRepair.disabled=false;ui.feedbackMode.textContent='文本反馈';status('文本反馈 Repair JSON 已通过校验，可应用','good');"""
new="""    const raw=await parseValidateOrRepair(content,'用户文本反馈 Repair 输出',plan);pendingRepair=sanitize(raw);pendingRuntimePatch=normalizeRuntimePatch(raw);
    history.push({event:'user_text_feedback',feedback,contextSnapshot:context,proposedPlan:structuredClone(pendingRepair),runtimePatch:pendingRuntimePatch?structuredClone(pendingRuntimePatch):null,reviewSummary:raw.review_summary||'',issues:Array.isArray(raw.issues)?raw.issues:[]});
    ui.reviewSummary.textContent=(raw.review_summary||'文本反馈修订完成')+(Array.isArray(raw.issues)&&raw.issues.length?'\\n问题：'+formatIssues(raw.issues):'')+(pendingRuntimePatch?'\\n包含 runtime facing calibration。':'');ui.repairJson.textContent=JSON.stringify({...pendingRepair,...(pendingRuntimePatch?{runtime_patch:pendingRuntimePatch}:{})},null,2);ui.applyRepair.disabled=false;ui.feedbackMode.textContent='文本反馈';status('文本反馈 Repair 已校验，可应用 Plan + Runtime 修复','good');"""
if old not in s: raise SystemExit('text review result block missing')
s=s.replace(old,new,1)

# Apply runtime patch with repair.
old_apply="""  plan=pendingRepair;pendingRepair=null;ui.applyRepair.disabled=true;history.push({event:'vision_repair_applied',plan});renderPlan();log('已应用通过校验的 Vision Repair JSON');"""
new_apply="""  plan=pendingRepair;if(pendingRuntimePatch)applyRuntimePatch(pendingRuntimePatch);const appliedRuntime=pendingRuntimePatch?structuredClone(pendingRuntimePatch):null;pendingRepair=null;pendingRuntimePatch=null;ui.applyRepair.disabled=true;history.push({event:'repair_applied',plan:structuredClone(plan),runtimePatch:appliedRuntime});renderPlan();log('已应用通过校验的 Plan'+(appliedRuntime?' + Runtime facing calibration':''));"""
if old_apply not in s: raise SystemExit('apply block missing')
s=s.replace(old_apply,new_apply,1)

# Clear runtime pending but keep calibrated runtime config; clear context should not silently revert engine calibration.
s=s.replace("history=[];pendingRepair=null;lastFrames=[];ui.applyRepair.disabled=true;", "history=[];pendingRepair=null;pendingRuntimePatch=null;lastFrames=[];ui.applyRepair.disabled=true;",1)

# Explicitly use empirical calibration now, not waiting for another AI turn.
s=s.replace("status('动画已编译','good');", "status('动画已编译 · RobotExpressive clip-facing calibration active','good');")

# Fix object issues in multiview review too.
s=s.replace("'\\n问题：'+raw.issues.join('；')", "'\\n问题：'+formatIssues(raw.issues)")

Path('sceneforge-animate/phase152.html').write_text(s,encoding='utf-8')
