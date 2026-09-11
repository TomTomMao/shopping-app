from pathlib import Path
p=Path('sceneforge-animate/phase14.html')
s=p.read_text(encoding='utf-8')
s=s.replace('Phase 1.4','Phase 1.4.1')
s=s.replace('Director → auto-facing runtime → orientation QA → validated Repair JSON','Director → orientation QA → resilient Repair JSON')
anchor="""function sanitize(raw){"""
helpers=r'''function isObject(x){return !!x&&typeof x==='object'&&!Array.isArray(x)}
function planScore(x){if(!isObject(x))return -1;let s=0;if(Array.isArray(x.assets))s+=x.assets.length?7:2;if(Array.isArray(x.shots))s+=x.shots.length?7:2;if(Number.isFinite(Number(x.duration)))s+=2;if(typeof x.title==='string')s+=1;if(typeof x.summary==='string')s+=1;return s}
function unwrapPlanCandidate(root){
  if(!isObject(root))return root;
  const keys=['plan','directorPlan','director_plan','repairedPlan','repaired_plan','repair','result','data','output','json','animation','project'];
  let best=root,bestScore=planScore(root),queue=[{value:root,depth:0}],seen=new Set();
  while(queue.length){const {value,depth}=queue.shift();if(!isObject(value)||seen.has(value)||depth>5)continue;seen.add(value);const sc=planScore(value);if(sc>bestScore){best=value;bestScore=sc}for(const k of keys){if(isObject(value[k]))queue.unshift({value:value[k],depth:depth+1})}for(const v of Object.values(value)){if(isObject(v))queue.push({value:v,depth:depth+1})}}
  if(best!==root){const merged={...best};for(const k of ['assistant_message','review_summary','issues'])if(merged[k]==null&&root[k]!=null)merged[k]=root[k];return merged}
  return root;
}
function completeFromBase(raw,base){
  if(!isObject(raw))raw={};if(!base)return {value:raw,filled:[]};
  const out={...raw},filled=[];
  if(!Array.isArray(out.assets)||out.assets.length===0){out.assets=structuredClone(base.assets);filled.push('assets')}
  if(!Array.isArray(out.shots)||out.shots.length===0){out.shots=structuredClone(base.shots);filled.push('shots')}
  if(!Number.isFinite(Number(out.duration))){out.duration=base.duration;filled.push('duration')}
  if(typeof out.title!=='string'||!out.title.trim()){out.title=base.title;filled.push('title')}
  if(typeof out.summary!=='string'){out.summary=base.summary||'';filled.push('summary')}
  return {value:out,filled};
}
'''
if anchor not in s: raise SystemExit('sanitize anchor missing')
s=s.replace(anchor,helpers+anchor,1)
old=r'''async function repairMalformedJson(text,why){
  log(`JSON 校验失败，启动自动 JSON 修复：${why}`);
  const content=await stream({
    model:'deepseek-flash',
    messages:[{role:'system',content:JSON_REPAIR_SYSTEM},{role:'user',content:`Validation problem: ${why}\nMalformed output:\n${text}`}],
    response_format:{type:'json_object'},thinking:{type:'enabled'},reasoning_effort:'low',max_tokens:7000
  });
  return parseJsonLoose(content).value;
}
async function parseValidateOrRepair(content,label){
  let raw,errors=[];
  try{raw=parseJsonLoose(content).value;errors=validatePlanShape(raw)}
  catch(e){errors=[e.message]}
  if(errors.length){
    ui.validation.className='validation warn';ui.validation.textContent=`${label} 首次 JSON 无效：${errors.join('；')}。正在自动修复…`;
    raw=await repairMalformedJson(content,errors.join('; '));
    const errors2=validatePlanShape(raw);
    if(errors2.length)throw new Error(`自动 JSON 修复后仍不合法：${errors2.join('；')}`);
    ui.validation.className='validation good';ui.validation.textContent=`${label}：JSON 自动修复成功并通过结构校验。`;
  }else{
    ui.validation.className='validation good';ui.validation.textContent=`${label}：JSON.parse + 结构校验通过。`;
  }
  return raw;
}'''
new=r'''async function repairMalformedJson(text,why,basePlan=null){
  log(`JSON 校验失败，启动自动 JSON 修复：${why}`);
  const reference=basePlan?`\nREFERENCE CURRENT PLAN (copy unchanged sections such as assets/shots if the attempted repair omitted them):\n${JSON.stringify(basePlan)}`:'';
  const content=await stream({
    model:'deepseek-flash',
    messages:[{role:'system',content:JSON_REPAIR_SYSTEM+` The output MUST contain non-empty assets and shots arrays at the ROOT. Never wrap the plan inside repair/result/data/plan. If a reference current plan is provided, preserve every unchanged section from it.`},{role:'user',content:`Validation problem: ${why}\nMalformed output:\n${text}${reference}`}],
    response_format:{type:'json_object'},thinking:{type:'disabled'},max_tokens:9000
  });
  return parseJsonLoose(content).value;
}
async function parseValidateOrRepair(content,label,basePlan=null){
  let raw=null,errors=[],filled=[];
  try{
    raw=unwrapPlanCandidate(parseJsonLoose(content).value);
    const completed=completeFromBase(raw,basePlan);raw=completed.value;filled=completed.filled;
    errors=validatePlanShape(raw);
  }catch(e){errors=[e.message]}
  if(errors.length){
    ui.validation.className='validation warn';ui.validation.textContent=`${label} 首次 JSON 无效：${errors.join('；')}。正在自动修复…`;
    let repaired=await repairMalformedJson(content,errors.join('; '),basePlan);
    repaired=unwrapPlanCandidate(repaired);
    const completed=completeFromBase(repaired,basePlan);raw=completed.value;filled=[...new Set([...filled,...completed.filled])];
    const errors2=validatePlanShape(raw);
    if(errors2.length){
      if(basePlan){
        const deterministic=completeFromBase(raw,basePlan);raw=deterministic.value;filled=[...new Set([...filled,...deterministic.filled])];
        const errors3=validatePlanShape(raw);
        if(errors3.length)throw new Error(`自动 JSON 修复后仍不合法：${errors3.join('；')}`);
      }else throw new Error(`自动 JSON 修复后仍不合法：${errors2.join('；')}`);
    }
    ui.validation.className='validation good';ui.validation.textContent=`${label}：JSON 修复并通过结构校验${filled.length?`；从当前动画补齐：${filled.join(', ')}`:''}。`;
  }else{
    ui.validation.className='validation good';ui.validation.textContent=`${label}：JSON.parse + 结构校验通过${filled.length?`；从当前动画补齐：${filled.join(', ')}`:''}。`;
  }
  return raw;
}'''
if old not in s: raise SystemExit('repair block not found')
s=s.replace(old,new,1)
s=s.replace("const raw=await parseValidateOrRepair(content,'Vision Repair 输出');","const raw=await parseValidateOrRepair(content,'Vision Repair 输出',plan);")
s=s.replace("const JSON_REPAIR_SYSTEM=`You repair malformed JSON for SceneForge Animate. Return exactly one valid JSON object and no markdown. Preserve the intended animation content. Required root fields: title, summary, duration, assets, shots. assets and shots must be arrays. Do not explain.`;","const JSON_REPAIR_SYSTEM=`You repair malformed or structurally incomplete JSON for SceneForge Animate. Return exactly one valid ROOT JSON object and no markdown. Preserve the intended animation content. Required root fields: title, summary, duration, assets, shots. assets and shots MUST be non-empty arrays. The animation plan itself must be the root object; never wrap it inside plan, repair, result, data, output, project or animation. Do not explain.`;")
Path('sceneforge-animate/phase141.html').write_text(s,encoding='utf-8')
