from pathlib import Path

src = Path('sceneforge-animate/phase3.html')
out = Path('sceneforge-animate/phase32.html')
s = src.read_text(encoding='utf-8')

s = s.replace('<title>SceneForge Animate · Phase 3.0.2</title>', '<title>SceneForge Animate · Phase 3.2</title>')
s = s.replace('<div class="brand">SceneForge Animate · Phase 3.0.2</div>', '<div class="brand">SceneForge Animate · Phase 3.2</div>', 1)
s = s.replace('Phase 3.0 + 3.1：故事规划 → 资产规划 → 用户审批 → 多供应商生成 → 资产检查与复用', 'Phase 3.2：故事规划 → 资产生成/上传 → 用户审批 → 自动装配 Three.js 场景 → 时间线动画预览', 1)

css = r'''
.animLayout{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:10px;height:calc(100vh - 90px);min-height:540px}.animStageWrap{position:relative;background:#05080d;border:1px solid #29384f;border-radius:12px;overflow:hidden;min-height:460px}.animStage{position:absolute;inset:0}.animStage canvas{display:block;width:100%;height:100%}.animOverlay{position:absolute;z-index:4;left:10px;right:10px;top:10px;display:flex;align-items:center;gap:6px;pointer-events:none}.animOverlay>*{pointer-events:auto}.animCaption{position:absolute;z-index:4;left:50%;bottom:54px;transform:translateX(-50%);max-width:78%;padding:7px 11px;border:1px solid #42536f;border-radius:9px;background:#090f19d9;text-align:center;font-size:13px;font-weight:700;text-shadow:0 2px 8px #000}.animTimeline{position:absolute;z-index:4;left:12px;right:12px;bottom:12px;background:#0a101ad9;border:1px solid #34445e;border-radius:9px;padding:8px}.animTimeline input{width:100%}.animSide{overflow:auto}.animShot{border:1px solid #30415d;background:#0d1420;border-radius:8px;padding:7px;margin-bottom:6px;font-size:9px}.animShot.active{border-color:#7794d2;background:#182641}.runtimeAsset{display:flex;justify-content:space-between;gap:8px;border-bottom:1px solid #253147;padding:5px 0;font-size:9px}.runtimeAsset:last-child{border-bottom:0}.animStatus{font-size:9px;color:#a9b7cc;margin-left:auto}.animBadge{font-size:9px;padding:4px 7px;border-radius:999px;border:1px solid #405270;background:#101824}.animJson{max-height:230px}.animHint{font-size:9px;color:#8191a9;line-height:1.45}.animStageEmpty{height:100%;display:flex;align-items:center;justify-content:center;color:#71829d;font-size:12px;padding:30px;text-align:center}.pulseGood{box-shadow:0 0 0 1px #3d7654 inset}
'''
s = s.replace('</style>', css + '\n</style>', 1)

old_tabs = '<div class="tabs"><button class="tab active" data-view="planView">规划</button><button class="tab" data-view="jobsView">生成任务</button><button class="tab" data-view="inventoryView">资产库</button></div>'
new_tabs = '<div class="tabs"><button class="tab active" data-view="planView">规划</button><button class="tab" data-view="jobsView">生成任务</button><button class="tab" data-view="inventoryView">资产库</button><button class="tab" data-view="animateView">动画预览</button></div><button id="buildAnimationBtn" class="goodBtn" disabled>🎬 生成动画</button>'
if old_tabs not in s:
    raise SystemExit('tabs anchor missing')
s = s.replace(old_tabs, new_tabs, 1)

inventory_close = '''  <div id="inventoryView" class="view">
    <div class="card"><h3>上传资产</h3><div class="uploadBox"><input id="uploadInput" type="file" multiple accept="image/png,image/jpeg,image/webp,.glb"/><div class="hint" style="margin-top:6px">支持 PNG/JPG/WebP/GLB。上传后 Agent 会结合当前 Prompt 与资产规划判断是否可复用。</div></div></div>
    <div class="card"><h3>当前资产</h3><div id="inventory" class="inventoryGrid"><div class="empty">还没有资产。</div></div></div>
  </div>
</section>'''
animate_html = '''  <div id="inventoryView" class="view">
    <div class="card"><h3>上传资产</h3><div class="uploadBox"><input id="uploadInput" type="file" multiple accept="image/png,image/jpeg,image/webp,.glb"/><div class="hint" style="margin-top:6px">支持 PNG/JPG/WebP/GLB。上传后 Agent 会结合当前 Prompt 与资产规划判断是否可复用。</div></div></div>
    <div class="card"><h3>当前资产</h3><div id="inventory" class="inventoryGrid"><div class="empty">还没有资产。</div></div></div>
  </div>

  <div id="animateView" class="view">
    <div class="animLayout">
      <div class="animStageWrap" id="animStageWrap">
        <div id="animStage" class="animStage"><div class="animStageEmpty">资产生成完成后点击“生成动画”。Director 会把 Phase 3 的真实资产装入 Phase 1 风格的 Three.js 时间线。</div></div>
        <div class="animOverlay"><button id="animPlay">▶ 播放</button><button id="animRestart">↺ 重播</button><button id="animRebuild">重新编排</button><span id="animShotBadge" class="animBadge">未编排</span><span id="animStatus" class="animStatus">等待资产</span></div>
        <div id="animCaption" class="animCaption" style="display:none"></div>
        <div class="animTimeline"><input id="animSeek" type="range" min="0" max="20" step="0.01" value="0"/></div>
      </div>
      <div class="animSide">
        <div class="card"><h3>Runtime 资产</h3><div id="animAssets"><div class="empty">尚未装配。</div></div></div>
        <div class="card"><h3>动画镜头</h3><div id="animShots"><div class="empty">尚未编排。</div></div></div>
        <div class="card"><h3>Director Runtime Plan</h3><div id="animJson" class="json animJson">{}</div></div>
        <div class="card"><h3>Phase 3.2 说明</h3><div class="animHint">当前版本先不生成音频。GLB 若自带动作 clip 会优先使用；没有骨骼动画时，会用 Phase 1 风格的程序化移动、转身、跳跃、摇摆和旋转完成表演。</div></div>
      </div>
    </div>
  </div>
</section>'''
if inventory_close not in s:
    raise SystemExit('inventory anchor missing')
s = s.replace(inventory_close, animate_html, 1)

# Keep the intermediate Qwen concept image as a fallback runtime asset even if Meshy later fails.
s = s.replace("job.intermediate=concept;job.output=await meshyImage3D(asset,concept.url,job,30,70);", "job.intermediate=concept;if(!inventory.some(x=>x.planAssetId===asset.id&&x.provider==='qwen-image-3.0-pro'))addGeneratedToInventory(asset,concept);job.output=await meshyImage3D(asset,concept.url,job,30,70);", 1)

js = r'''

// ========================= Phase 3.2: Phase 3 assets + Phase 1 runtime =========================
const animUI={
  build:$('buildAnimationBtn'),play:$('animPlay'),restart:$('animRestart'),rebuild:$('animRebuild'),seek:$('animSeek'),
  stage:$('animStage'),stageWrap:$('animStageWrap'),status:$('animStatus'),caption:$('animCaption'),badge:$('animShotBadge'),
  assets:$('animAssets'),shots:$('animShots'),json:$('animJson')
};
let animPlan32=null,animActors32=new Map(),animPlaying32=false,animTime32=0,animLast32=performance.now(),animReady32=false,animBuilding32=false;
let animScene32=null,animCamera32=null,animRenderer32=null,animRAF32=null;
const animLoader32=new GLTFLoader();
const ANIM_CAM32={wide:[0,5.2,12.5],medium:[0,3.5,8.3],close:[0,2.5,5.1],reaction:[2.8,2.7,5.5],follow:[4.2,3.4,7.4]};
const ANIM_ACTIONS32=['idle','walk','run','wave','dance','jump','spin','react','face','pause'];

function isLocal32(){return ['127.0.0.1','localhost'].includes(location.hostname)}
function runtimeUrl32(url){if(!url||/^(blob:|data:)/i.test(url))return url;return isLocal32()?`/asset-proxy?url=${encodeURIComponent(url)}`:url}
function invForAsset32(id){
  const spec=projectPlan?.assets?.find(a=>a.id===id);
  const matches=inventory.filter(x=>x.planAssetId===id||x.suitability?.matchedAssetId===id||x.id===spec?.matched_inventory_id);
  return matches.sort((a,b)=>(b.type==='glb')-(a.type==='glb'))[0]||null;
}
function availableRuntimeAssets32(){return (projectPlan?.assets||[]).map(a=>({spec:a,inv:invForAsset32(a.id)})).filter(x=>x.inv?.url)}
function updateAnimButton32(){if(animUI.build)animUI.build.disabled=availableRuntimeAssets32().length===0||animBuilding32}

function initAnimScene32(){
  if(animRenderer32)return;
  animScene32=new THREE.Scene();animScene32.background=new THREE.Color(0x080d18);
  animCamera32=new THREE.PerspectiveCamera(48,1,.1,300);animCamera32.position.set(0,4.5,11);
  animRenderer32=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
  animRenderer32.setPixelRatio(Math.min(devicePixelRatio,1.5));animRenderer32.outputColorSpace=THREE.SRGBColorSpace;
  animUI.stage.innerHTML='';animUI.stage.appendChild(animRenderer32.domElement);
  animScene32.add(new THREE.HemisphereLight(0xcfe1ff,0x30261f,2.2));
  const key=new THREE.DirectionalLight(0xffffff,3.1);key.position.set(5,9,6);animScene32.add(key);
  const rim=new THREE.DirectionalLight(0x7b91ff,1.5);rim.position.set(-5,5,-6);animScene32.add(rim);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,40),new THREE.MeshStandardMaterial({color:0x151b25,roughness:.88,metalness:.05}));floor.rotation.x=-Math.PI/2;floor.position.y=-.02;floor.receiveShadow=true;animScene32.add(floor);
  const grid=new THREE.GridHelper(40,40,0x34435a,0x1e2938);grid.position.y=0;animScene32.add(grid);
  resizeAnim32();
  if(!animRAF32)animLoop32(performance.now());
}
function resizeAnim32(){if(!animRenderer32||!animCamera32)return;const w=Math.max(2,animUI.stage.clientWidth),h=Math.max(2,animUI.stage.clientHeight);animRenderer32.setSize(w,h,false);animCamera32.aspect=w/h;animCamera32.updateProjectionMatrix()}
new ResizeObserver(()=>resizeAnim32()).observe(animUI.stageWrap);

function clearAnimActors32(){
  for(const a of animActors32.values()){
    a.mixer?.stopAllAction();
    animScene32?.remove(a.wrap);
  }
  animActors32.clear();animReady32=false;
}
function assetRole32(spec){return String(spec?.role||'').toLowerCase()}
function targetSize32(spec){const r=assetRole32(spec);if(r.includes('environment')||r.includes('scene')||r.includes('background'))return 8;if(r.includes('character'))return 1.8;if(r.includes('vehicle'))return 2.5;return 1.0}
async function texture32(url){return await new THREE.TextureLoader().loadAsync(runtimeUrl32(url))}
async function loadRuntimeAsset32(spec,inv,index,total){
  const wrap=new THREE.Group();wrap.name=spec.id;animScene32.add(wrap);
  const role=assetRole32(spec);let model=null,mixer=null,clips=[];
  if(inv.type==='glb'){
    const gltf=await animLoader32.loadAsync(runtimeUrl32(inv.url));model=gltf.scene;clips=gltf.animations||[];wrap.add(model);
    model.traverse(n=>{if(n.isMesh){n.castShadow=true;n.receiveShadow=true}});
    let box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3());const max=Math.max(size.x,size.y,size.z)||1;
    const desired=targetSize32(spec),scale=desired/max;model.scale.setScalar(scale);
    box=new THREE.Box3().setFromObject(model);const c=box.getCenter(new THREE.Vector3());model.position.x-=c.x;model.position.z-=c.z;model.position.y-=box.min.y;
    if(clips.length)mixer=new THREE.AnimationMixer(model);
  }else{
    const tex=await texture32(inv.url);tex.colorSpace=THREE.SRGBColorSpace;
    if(role.includes('environment')||role.includes('background')||role.includes('scene')){
      const geo=new THREE.PlaneGeometry(16,9);const mat=new THREE.MeshBasicMaterial({map:tex,side:THREE.DoubleSide});model=new THREE.Mesh(geo,mat);model.position.set(0,4.5,-7);wrap.add(model);
    }else{
      const geo=new THREE.PlaneGeometry(1.8,1.8);const mat=new THREE.MeshBasicMaterial({map:tex,transparent:true,side:THREE.DoubleSide});model=new THREE.Mesh(geo,mat);model.position.y=.9;wrap.add(model);
    }
  }
  const actor={id:spec.id,spec,inv,wrap,model,mixer,clips,currentClip:null,baseScale:wrap.scale.clone(),baseY:0,index,total};animActors32.set(spec.id,actor);return actor;
}
function clipForAction32(actor,action){if(!actor?.clips?.length)return null;const synonyms={idle:['idle','standing','survey'],walk:['walk','walking'],run:['run','running'],wave:['wave','hello'],dance:['dance'],jump:['jump'],react:['yes','no','react','thumb'],spin:['dance']};const names=synonyms[action]||[action];return actor.clips.find(c=>names.some(n=>c.name.toLowerCase().includes(n)))||null}
function setActorClip32(actor,action,timeInAction=0){if(!actor.mixer)return;const clip=clipForAction32(actor,action);if(!clip){actor.mixer.stopAllAction();actor.currentClip=null;return}if(actor.currentClip!==clip.name){actor.mixer.stopAllAction();const ac=actor.mixer.clipAction(clip);ac.reset().play();actor.currentClip=clip.name}actor.mixer.setTime(Math.max(0,timeInAction))}
function yawTo32(a,b){return Math.atan2(b[0]-a[0],b[2]-a[2])}
function lerp32(a,b,t){return a+(b-a)*t}
function lerp3_32(a,b,t){return[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t]}
function ease32(t){t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)}
function normCamera32(v){v=String(v||'medium').toLowerCase();return ANIM_CAM32[v]?v:(v.includes('wide')?'wide':v.includes('close')?'close':v.includes('follow')?'follow':v.includes('reaction')?'reaction':'medium')}
function currentShot32(t){return animPlan32?.shots?.find(s=>t>=s.start&&t<s.end)||animPlan32?.shots?.at(-1)||null}
function activeBeat32(id,t){return animPlan32?.beats?.filter(b=>b.target===id&&t>=b.start&&t<=b.end).sort((a,b)=>b.start-a.start)[0]||null}
function actorState32(id,t){
  const actor=animPlan32.actors.find(a=>a.assetId===id);let pos=[...actor.position],yaw=actor.rotationY||0,action='idle',actionStart=0;
  const beats=animPlan32.beats.filter(b=>b.target===id).sort((a,b)=>a.start-b.start);
  for(const b of beats){if(t<b.start)continue;action=b.action;actionStart=b.start;
    if(['walk','run'].includes(b.action)&&b.to){const from=b.from||pos,to=b.to;if(t>=b.end)pos=[...to];else pos=lerp3_32(from,to,ease32((t-b.start)/Math.max(.01,b.end-b.start)));yaw=yawTo32(from,to);if(t>=b.end)pos=[...to]}
    if(b.action==='face'&&b.faceTarget){const other=animPlan32.actors.find(a=>a.assetId===b.faceTarget);if(other)yaw=yawTo32(pos,actorState32Simple32(other.assetId,t).pos)}
  }
  return{pos,yaw,action,actionTime:Math.max(0,t-actionStart)}
}
function actorState32Simple32(id,t){const actor=animPlan32.actors.find(a=>a.assetId===id);let pos=[...(actor?.position||[0,0,0])];for(const b of animPlan32.beats.filter(x=>x.target===id&&['walk','run'].includes(x.action)).sort((a,b)=>a.start-b.start)){if(t<b.start)continue;const from=b.from||pos,to=b.to||pos;pos=t>=b.end?[...to]:lerp3_32(from,to,ease32((t-b.start)/Math.max(.01,b.end-b.start)))}return{pos}}
function applyAnim32(t){
  if(!animPlan32)return;
  for(const def of animPlan32.actors){const a=animActors32.get(def.assetId);if(!a)continue;const st=actorState32(def.assetId,t),beat=activeBeat32(def.assetId,t);a.wrap.position.set(...st.pos);a.wrap.rotation.set(0,st.yaw,0);a.wrap.scale.set(1,1,1);
    if(beat){const p=Math.max(0,Math.min(1,(t-beat.start)/Math.max(.01,beat.end-beat.start)));if(beat.action==='jump')a.wrap.position.y+=Math.sin(Math.PI*p)*.85;if(beat.action==='wave')a.wrap.rotation.z+=Math.sin(p*Math.PI*6)*.12;if(beat.action==='dance'){a.wrap.position.y+=Math.abs(Math.sin(p*Math.PI*6))*.18;a.wrap.rotation.y+=Math.sin(p*Math.PI*4)*.65}if(beat.action==='spin')a.wrap.rotation.y+=p*Math.PI*2;if(beat.action==='react'){const q=1+Math.sin(p*Math.PI)*.15;a.wrap.scale.set(q,q,q)}}
    setActorClip32(a,st.action,st.actionTime);
  }
  const sh=currentShot32(t);if(sh){const ids=(sh.focus?.length?sh.focus:animPlan32.actors.map(a=>a.assetId)).filter(id=>animActors32.has(id));const pts=ids.map(id=>actorState32Simple32(id,t).pos);const target=pts.length?[pts.reduce((n,p)=>n+p[0],0)/pts.length,1.25,pts.reduce((n,p)=>n+p[2],0)/pts.length]:[0,1.2,0];const off=ANIM_CAM32[sh.camera]||ANIM_CAM32.medium;animCamera32.position.set(target[0]+off[0],off[1],target[2]+off[2]);animCamera32.lookAt(...target);animUI.badge.textContent=`${sh.title} · ${sh.camera}`;animUI.caption.textContent=sh.caption||'';animUI.caption.style.display=sh.caption?'block':'none';}
  animUI.seek.value=String(t);animUI.status.textContent=`${t.toFixed(1)} / ${animPlan32.duration.toFixed(1)}s`;
  for(const el of animUI.shots.querySelectorAll('.animShot'))el.classList.toggle('active',el.dataset.id===currentShot32(t)?.id);
}
function animLoop32(now){animRAF32=requestAnimationFrame(animLoop32);const dt=Math.min(.05,(now-animLast32)/1000);animLast32=now;if(animPlaying32&&animPlan32){animTime32+=dt;if(animTime32>=animPlan32.duration){animTime32=animPlan32.duration;animPlaying32=false;animUI.play.textContent='▶ 播放'}applyAnim32(animTime32)}if(animRenderer32&&animScene32&&animCamera32)animRenderer32.render(animScene32,animCamera32)}

const ANIM_DIRECTOR32=`You are SceneForge Animation Director. Convert the provided story, storyboard, planned assets and AVAILABLE runtime assets into a constrained Three.js animation timeline. No audio. Use ONLY available asset ids. Return JSON only: {title,duration,actors:[{assetId,position:[x,0,z],rotationY}],shots:[{id,title,start,end,camera,focus:[assetIds],caption}],beats:[{target,action,start,end,to?,faceTarget?}]}. Allowed actions: idle, walk, run, wave, dance, jump, spin, react, face, pause. Cameras: wide, medium, close, reaction, follow. Make 3-6 readable shots, preserve story continuity, avoid teleporting, keep all beat times inside duration. Locomotion automatically faces the movement direction. If an asset is a static image, avoid locomotion unless it represents a character/object. Environment/background assets should normally stay static. Keep the animation visually understandable without audio.`;
function sanitizeAnimPlan32(raw,avail){
  const ids=new Set(avail.map(x=>x.spec.id)),duration=Math.max(4,Math.min(60,Number(raw?.duration||storyAnalysis?.duration_seconds||20)||20));
  const actors=avail.map((x,i)=>{const r=(raw?.actors||[]).find(a=>a.assetId===x.spec.id)||{};const p=Array.isArray(r.position)&&r.position.length>=3?r.position:[(i-(avail.length-1)/2)*2,0,0];return{assetId:x.spec.id,position:[Number(p[0])||0,0,Number(p[2])||0],rotationY:Number(r.rotationY)||0}});
  let shots=(Array.isArray(raw?.shots)?raw.shots:[]).map((sh,i)=>({id:String(sh.id||`shot${i+1}`),title:String(sh.title||`Shot ${i+1}`),start:Math.max(0,Number(sh.start)||0),end:Math.min(duration,Number(sh.end)||duration),camera:normCamera32(sh.camera),focus:(Array.isArray(sh.focus)?sh.focus:[]).filter(id=>ids.has(id)),caption:String(sh.caption||'').slice(0,180)})).filter(sh=>sh.end>sh.start).sort((a,b)=>a.start-b.start);
  if(!shots.length){const source=shotPlan?.shots||[];shots=source.length?source.map((sh,i)=>({id:String(sh.id||`shot${i+1}`),title:String(sh.title||`Shot ${i+1}`),start:Math.max(0,Number(sh.start)||0),end:Math.min(duration,Number(sh.end)||duration),camera:normCamera32(sh.camera),focus:actors.slice(0,2).map(a=>a.assetId),caption:String(sh.goal||sh.action||'')})):[{id:'shot1',title:'Main',start:0,end:duration,camera:'wide',focus:actors.map(a=>a.assetId),caption:storyAnalysis?.summary||''}]}
  const starts=new Map(actors.map(a=>[a.assetId,[...a.position]]));const beats=[];
  for(const b of (Array.isArray(raw?.beats)?raw.beats:[])){if(!ids.has(b.target)||!ANIM_ACTIONS32.includes(b.action))continue;const start=Math.max(0,Math.min(duration,Number(b.start)||0)),end=Math.max(start+.05,Math.min(duration,Number(b.end)||start+1));const x={target:b.target,action:b.action,start,end};if(Array.isArray(b.to)&&b.to.length>=3)x.to=[Number(b.to[0])||0,0,Number(b.to[2])||0];if(ids.has(b.faceTarget))x.faceTarget=b.faceTarget;if(['walk','run'].includes(x.action)&&x.to){x.from=[...starts.get(x.target)];starts.set(x.target,[...x.to])}beats.push(x)}
  if(!beats.length&&actors.length){const a=actors[0],b=actors[1];beats.push({target:a.assetId,action:'walk',start:0.5,end:Math.min(3,duration*.25),from:[...a.position],to:[-.7,0,0]});if(b)beats.push({target:b.assetId,action:'wave',start:Math.min(3.1,duration*.3),end:Math.min(5.5,duration*.5)});beats.push({target:a.assetId,action:'dance',start:Math.min(5.5,duration*.5),end:Math.min(8,duration*.7)})}
  return{title:String(raw?.title||storyAnalysis?.title||'SceneForge Animation'),duration,actors,shots,beats};
}
async function buildAnimation32(auto=false){
  if(animBuilding32)return;const avail=availableRuntimeAssets32();if(!avail.length){toast('还没有可用于动画的资产');return}animBuilding32=true;updateAnimButton32();initAnimScene32();animUI.status.textContent='Director 正在编排动画…';traceAdd('7. 动画编排',`将 ${avail.length} 个已生成/上传资产接入 Phase 1 runtime。`,'running');
  try{
    const context={prompt:ui.prompt.value,story:storyAnalysis,storyboard:shotPlan,assetPlan:projectPlan?.assets?.map(a=>({id:a.id,name:a.name,role:a.role,description:a.description}))||[],availableAssets:avail.map(x=>({assetId:x.spec.id,name:x.spec.name,role:x.spec.role,type:x.inv.type,provider:x.inv.provider,hasRuntimeUrl:!!x.inv.url}))};
    let raw;try{raw=await deepseekJSON(ANIM_DIRECTOR32,`PROJECT CONTEXT:\n${JSON.stringify(context)}`)}catch(e){console.warn('Runtime director fallback',e);raw={title:storyAnalysis?.title,duration:storyAnalysis?.duration_seconds,shots:[],beats:[]}}
    animPlan32=sanitizeAnimPlan32(raw,avail);clearAnimActors32();animUI.status.textContent='正在装配 Three.js 场景…';
    for(let i=0;i<avail.length;i++){const {spec,inv}=avail[i];try{await loadRuntimeAsset32(spec,inv,i,avail.length)}catch(e){console.error('runtime asset load',spec.id,e);traceAdd('资产装配警告',`${spec.name}: ${e.message}`,'error')}}
    animReady32=animActors32.size>0;animUI.assets.innerHTML=avail.map(({spec,inv})=>`<div class="runtimeAsset"><span><b>${esc(spec.name)}</b><br>${esc(spec.role||'asset')}</span><span>${esc(inv.type)} · ${esc(inv.provider||inv.source||'asset')}</span></div>`).join('');
    animUI.shots.innerHTML=animPlan32.shots.map(sh=>`<div class="animShot" data-id="${esc(sh.id)}"><b>${esc(sh.title)}</b><br>${sh.start.toFixed(1)}–${sh.end.toFixed(1)}s · ${esc(sh.camera)}<br>${esc(sh.caption||'')}</div>`).join('');animUI.json.textContent=JSON.stringify(animPlan32,null,2);animUI.seek.max=String(animPlan32.duration);animTime32=0;applyAnim32(0);animUI.status.textContent=animReady32?'动画已装配，可以播放':'没有资产成功加载';traceAdd('8. Three.js 动画就绪',`${animActors32.size}/${avail.length} 个资产已进入 runtime；音频暂未启用。`,animReady32?'done':'error');
    document.querySelector('[data-view="animateView"]')?.click();
  }catch(e){console.error(e);animUI.status.textContent=e.message;toast(`动画装配失败：${e.message}`);traceAdd('动画装配失败',e.message,'error')}
  finally{animBuilding32=false;updateAnimButton32()}
}

animUI.build.onclick=()=>buildAnimation32(false);animUI.rebuild.onclick=()=>buildAnimation32(false);
animUI.play.onclick=()=>{if(!animPlan32)return;animPlaying32=!animPlaying32;if(animTime32>=animPlan32.duration&&animPlaying32)animTime32=0;animUI.play.textContent=animPlaying32?'⏸ 暂停':'▶ 播放'};
animUI.restart.onclick=()=>{animTime32=0;animPlaying32=false;animUI.play.textContent='▶ 播放';if(animPlan32)applyAnim32(0)};
animUI.seek.oninput=()=>{animTime32=Number(animUI.seek.value);animPlaying32=false;animUI.play.textContent='▶ 播放';if(animPlan32)applyAnim32(animTime32)};

// Preserve Phase 3 behavior, then automatically compile whatever assets actually succeeded.
const originalStartGeneration32=ui.startBtn.onclick;
ui.startBtn.onclick=async()=>{await originalStartGeneration32?.();updateAnimButton32();if(availableRuntimeAssets32().length)await buildAnimation32(true)};
const originalUpload32=ui.uploadInput.onchange;
ui.uploadInput.onchange=async(...args)=>{await originalUpload32?.(...args);setTimeout(updateAnimButton32,50)};
const originalClear32=ui.clearBtn.onclick;
ui.clearBtn.onclick=(...args)=>{clearAnimActors32();animPlan32=null;animUI.json.textContent='{}';animUI.assets.innerHTML='<div class="empty">尚未装配。</div>';animUI.shots.innerHTML='<div class="empty">尚未编排。</div>';updateAnimButton32();return originalClear32?.(...args)};
updateAnimButton32();
// ======================= End Phase 3.2 integration =======================
'''

pos = s.rfind('</script>')
if pos < 0:
    raise SystemExit('script close missing')
s = s[:pos] + js + '\n' + s[pos:]
out.write_text(s, encoding='utf-8')
print(f'wrote {out} ({out.stat().st_size} bytes)')
