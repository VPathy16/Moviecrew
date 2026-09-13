/* Director review owns its draft; the shot composer keeps its own save lifecycle. */
const directionDrafts = new Map();
let directionSaving = null;
function directionLocal() {
  const state = project.director_review;
  let local = directionDrafts.get(project.id);
  if (!local || (!local.dirty && local.revision !== state.revision)) {
    local = {revision: state.revision, draft: structuredClone(state.draft), dirty: false};
    directionDrafts.set(project.id, local);
  }
  return local;
}
async function saveDirection() {
  if (directionSaving) await directionSaving;
  if (!project?.director_review?.draft) return;
  const id = project.id, local = directionLocal();
  if (!local.dirty) return;
  const snapshot = JSON.stringify(local.draft);
  directionSaving = api('/api/projects/'+id+'/director','PUT',{
    revision: local.revision, draft: JSON.parse(snapshot)
  }).then(state => {
    local.revision = state.revision;
    local.dirty = JSON.stringify(local.draft) !== snapshot;
    if(project?.id===id)$('autosave').textContent=local.dirty?'Unsaved story changes':'All changes saved';
    if (project?.id === id) {
      project.director_review = state;
      if (!project.project.scenes.length) Object.assign(project.project, {title:state.draft.title, logline:state.draft.logline, outline:state.draft.outline});
    }
  });
  try { await directionSaving; } finally { directionSaving = null; }
}
const saveBeforeDirection = saveDraft;
saveDraft = async function() {
  try { await saveDirection(); } catch(error) { report(error); return false; }
  return saveBeforeDirection();
};
window.addEventListener('beforeunload', event => {
  if ([...directionDrafts.values()].some(d=>d.dirty)) {event.preventDefault();event.returnValue='';}
});
const priorDirectionStatus = crewStatus;
crewStatus = function(key) {
  if (project?.director_review?.request && !project.director_review.approved) {
    if (key !== 'director') return 'After story approval';
    return ['running','queued'].includes(project.status) ? 'Shaping your story…' : 'Review your story';
  }
  return priorDirectionStatus(key);
};
const priorDirectionRender = renderCrew;
renderCrew = function() {
  priorDirectionRender();
  const state = project?.director_review;
  if (!state || !Object.keys(state).length) return;
  const hasScenes = !!project.project.scenes.length;
  if (!state.approved) {
    for (const button of $('crew-roster').querySelectorAll('button')) {
      if (button.getAttribute('aria-pressed')!=='true') button.disabled = true;
    }
  }
  if (crewRole !== 'director') return;
  const content = $('crew-output').querySelector('.crew-artifacts');
  content.replaceChildren();
  const active = ['running','queued'].includes(project.status);
  if (!state.draft) {
    content.append(crewEl('p',project.error || 'Your Director is shaping the first proposal. The Writer will wait for your approval.','muted'));
    if (!active) {const retry=crewEl('button','Try Director again','primary');retry.onclick=()=>directionAction('regenerate',{feedback:''});content.append(retry);}
    return;
  }
  const local = directionLocal();
  const form=crewEl('fieldset',undefined,'direction-form');form.disabled=active;content.append(form);
  if(project.backend==='mock')form.append(crewEl('p','Demo example: fixed sample output, not a generated interpretation of your concept.','status'));
  form.append(crewEl('p',hasScenes?'Your accepted scenes are preserved. Story changes are saved as a proposal for review.':'Refine the story and cast. Your Writer starts when you approve.','muted'));
  function field(parent,label,key,object,rows=0) {
    const wrap=crewEl('label',label), input=crewEl(rows?'textarea':'input');
    input.value=Array.isArray(object[key])?object[key].join('\n'):object[key]||'';
    input.setAttribute('aria-label',label);if(rows)input.rows=rows;
    input.oninput=()=>{object[key]=key==='outline'?input.value.split('\n').filter(s=>s.trim()):input.value;local.dirty=true;$('autosave').textContent='Unsaved story changes';};
    wrap.append(input);parent.append(wrap);return input;
  }
  field(form,'Film title','title',local.draft);
  field(form,'The story in one sentence','logline',local.draft,2);
  field(form,'Story beats · one per line','outline',local.draft,4);
  const cast=crewEl('details');cast.open=local.castOpen ?? local.draft.characters.length===0;cast.ontoggle=()=>{local.castOpen=cast.open};
  cast.append(crewEl('summary','Characters · '+local.draft.characters.length));form.append(cast);
  for (const character of local.draft.characters) {
    const row=crewEl('div',undefined,'direction-character');cast.append(row);
    field(row,'Name','name',character);field(row,'Role in the story','role',character);
    const more=crewEl('details');more.append(crewEl('summary','Motivation & identity'));row.append(more);
    field(more,'What they want','motivation',character,2);field(more,'Identity notes','description',character,2);
    const remove=crewEl('button','Remove character');remove.type='button';remove.onclick=()=>{local.draft.characters=local.draft.characters.filter(c=>c.id!==character.id);local.dirty=true;renderCrew();};row.append(remove);
  }
  const add=crewEl('button','＋ Add character');add.type='button';add.setAttribute('aria-label','Add character');add.onclick=()=>{local.draft.characters.push({id:'char_'+crypto.randomUUID(),name:'New character',role:'',motivation:'',description:''});local.dirty=true;local.castOpen=true;renderCrew();};cast.append(add);
  const feedback=crewEl('textarea');feedback.rows=2;feedback.placeholder='What should the Director change?';feedback.setAttribute('aria-label','Feedback for Director');feedback.value=local.feedback||'';feedback.oninput=()=>{local.feedback=feedback.value};form.append(feedback);
  const actions=crewEl('div',undefined,'direction-actions');form.append(actions);
  const save=crewEl('button','Save changes');save.onclick=async()=>{try{await saveDirection();notify('Story saved');renderCrew()}catch(e){report(e)}};actions.append(save);
  const regen=crewEl('button','Regenerate direction');regen.disabled=hasScenes;regen.onclick=()=>directionAction('regenerate',{feedback:feedback.value});actions.append(regen);
  const approve=crewEl('button',hasScenes?'Story approved':'Approve & continue to Writer →','primary');approve.disabled=hasScenes;approve.onclick=()=>directionAction('approve',{});actions.append(approve);
  if (state.history.length>1) {
    const versions=crewEl('details');versions.append(crewEl('summary','Previous versions'));form.append(versions);
    for (const version of [...state.history].reverse()) {
      if(version.revision===state.revision)continue;
      const button=crewEl('button','Restore version '+version.revision+' · '+version.draft.title);
      button.onclick=()=>directionAction('restore',{restore_revision:version.revision});versions.append(button);
    }
  }
  if (active)content.append(crewEl('p','Working… Your saved direction is preserved.','muted'));
  if (project.error)content.append(crewEl('p',project.error,'status'));
  if (state.needs_review)content.append(crewEl('p','The proposed direction differs from the approved script. Existing scenes need review; they have not been rewritten.','status'));
  if(project.backend!=='mock')content.append(crewEl('p','Regenerating or starting the Writer uses your connected provider. Charges may apply.','muted'));
};
async function directionAction(action, extra) {
  const id=project.id;
  if(busy)return;
  busy=true;
  $('crew-output').querySelectorAll('button').forEach(b=>b.disabled=true);
  try {
    await saveDirection();
    await api('/api/projects/'+id+'/director/'+action,'POST',{revision:project.director_review.revision,...extra});
    if(project?.id!==id)return;
    project=await api('/api/projects/'+id);
    if(action==='restore')directionDrafts.delete(id);
    if(action==='approve')crewRole='writer';
    render();
    if(['queued','running'].includes(project.status)) {clearTimeout(pollTimer);pollTimer=setTimeout(()=>poll(id,epoch),700);}
  } catch(error) {report(error);} finally {busy=false;if(project?.id===id)renderCrew();}
}
const beforeDirectionSwitch=switchFilmSection;
switchFilmSection=async function(section) {
  if(project?.director_review?.request && !project.director_review.approved && section!=='crew') {
    notify('Approve your story with the Director first.');section='crew';crewRole='director';
  }
  return beforeDirectionSwitch(section);
};
if(project)renderCrew();
