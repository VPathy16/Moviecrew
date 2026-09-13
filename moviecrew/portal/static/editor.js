/* Editing owns the cut; processing creates candidates and never replaces it silently. */
(() => {
 const host=$('final-edit');
 const icons={play:'<path d="m9 5 11 7-11 7Z"/>',pause:'<path d="M8 5v14M16 5v14"/>',close:'<path d="m6 6 12 12M6 18 18 6"/>',undo:'<path d="M9 5 4 10l5 5M4 10h9a6 6 0 0 1 6 6"/>',fit:'<path d="M8 4H4v4m12-4h4v4M4 16v4h4m12-4v4h-4"/>'};
 function iconButton(b,name,label){b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icons[name]+'</svg>';b.classList.add('editor-icon');b.setAttribute('aria-label',label);b.title=label;}
 function playState(){iconButton(play,playing?'pause':'play',playing?'Pause film':'Play film')}

 host.querySelector('h1').textContent='Edit your film';
 host.querySelector('p').textContent='Shape the story. Drag to edit. Right-click a clip for more.';
 const style=document.createElement('style');style.textContent=`
 #final-edit{max-width:1320px;padding:24px 32px}#final-edit h1{font-size:24px;margin:8px 0}
 .edit-toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0}.edit-toolbar label{font-size:11px;color:#a5abb5;margin:0}.edit-toolbar select{padding:7px 10px;width:auto;font-size:12px}.edit-toolbar button{font-size:12px;padding:8px 12px}
 #edit-stage{background:#000;max-height:420px;max-width:100%;margin:0 auto;overflow:hidden;border:1px solid #34383f;border-radius:10px;display:flex;justify-content:center}#edit-player{width:100%;height:100%;max-height:420px;background:#000}
 #edit-time{font-variant-numeric:tabular-nums;font-size:12px;color:#a5abb5}.edit-transport{display:flex;align-items:center;gap:16px;margin:10px 0}#edit-seek{flex:1;padding:0;accent-color:#f27656}
 #cut-clips{display:flex;align-items:center;gap:6px;overflow-x:auto;padding:12px 0 18px;min-height:100px}.edit-tile{flex-shrink:0;height:90px;min-width:110px;border:1px solid #34383f;border-radius:9px;padding:0;overflow:hidden;background:#24272d;text-align:left}.edit-tile[aria-pressed=true]{border:2px solid #f27656}.edit-tile video{width:100%;height:55px;object-fit:cover;pointer-events:none}.edit-tile small{display:block;padding:3px 8px;font-size:10px;white-space:nowrap}.edit-add{padding:4px 8px;border:0;background:transparent;color:#f4f1eb;font-size:20px;flex-shrink:0}
 #edit-inspector{padding:12px 16px;border:1px solid #34383f;border-radius:12px}.trim-control{display:flex;align-items:center;gap:8px;font-size:12px}.trim-control input[type=range]{width:130px;padding:0;accent-color:#f27656}.trim-control input[type=number]{width:70px;padding:6px;font-size:12px}#edit-inspector .edit-toolbar{margin:6px 0}
 #editor-dialog{width:min(620px,90vw);max-height:85vh;overflow:auto;padding:24px}#editor-dialog h2{font-size:20px}#editor-dialog p{font-size:13px;color:#a5abb5}#editor-dialog button{font-size:12px}#editor-dialog video{width:100%;max-height:250px}.edit-library{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.edit-library button{padding:6px}.edit-library img,.edit-library video{height:90px;width:100%;object-fit:cover}.edit-library small{display:block;font-size:11px}.edit-job{border-top:1px solid #34383f;padding:12px 0}.edit-job video{max-height:200px;width:100%}
 @media(max-width:700px){#final-edit{padding:18px 12px}.edit-toolbar{gap:7px}.edit-library{grid-template-columns:repeat(2,1fr)}#edit-stage,#edit-player{max-height:320px}}

 #final-edit .crew-eyebrow{display:none}#final-edit>h1{font-size:20px;font-weight:600;letter-spacing:-.5px}#final-edit>p{font-size:12px;margin:4px 0 12px;color:#858b96}
 #final-edit .edit-toolbar{gap:8px;margin:10px 0}#final-edit .edit-toolbar select{min-height:32px;background:#ffffff06;border:1px solid #ffffff0d;border-radius:8px;padding:6px 10px;color:#c4c8cf}
 #final-edit .edit-transport{gap:12px;padding:6px 0;margin:10px 0 4px;border-top:1px solid #ffffff09}#final-edit .timeline-tools{margin-left:auto;flex-wrap:nowrap;gap:10px}#final-edit .timeline-tools label{display:flex;align-items:center;gap:10px;font-size:11px;color:#828996}
 #final-edit button.editor-icon,dialog button.editor-icon{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-height:32px;padding:7px;border:0;border-radius:8px;background:transparent;color:#b3b9c3;box-shadow:none;flex-shrink:0}
 button.editor-icon svg{width:18px;height:18px}#final-edit button.editor-icon:hover,dialog button.editor-icon:hover{background:#ffffff0b;color:#fff}#final-edit button.editor-icon:disabled{opacity:.25}#final-edit .edit-transport>button.editor-icon{width:36px;height:36px;background:#f0f0ed;color:#15171b;border-radius:50%}
 #final-edit button:focus-visible,dialog button:focus-visible{outline:2px solid #f27656;outline-offset:3px}
 #final-edit input[type=range]{appearance:none;-webkit-appearance:none;height:3px!important;min-height:0;background:#3b3f47;border:0;border-radius:3px;box-shadow:none}#final-edit input[type=range]::-webkit-slider-thumb{appearance:none;-webkit-appearance:none;width:10px;height:10px;background:#c7cbd1;border:0;border-radius:50%}#final-edit input[type=range]::-moz-range-thumb{width:10px;height:10px;background:#c7cbd1;border:0;border-radius:50%}
 #editor-dialog,#export-dialog{border:1px solid #ffffff16;border-radius:16px;background:#1b1d22;color:#ebecef;box-shadow:0 24px 100px #0008;padding:24px!important}#editor-dialog::backdrop,#export-dialog::backdrop{background:#090b10a6;backdrop-filter:blur(6px)}#editor-dialog h2,#export-dialog h2{font-size:18px;letter-spacing:-.3px;margin:0 40px 18px 0}#editor-dialog .editor-close,#export-dialog .editor-close{position:absolute;right:14px;top:14px}#editor-dialog p,#export-dialog p{font-size:12px;line-height:1.6;color:#979eaa}
 #editor-dialog button:not(.editor-icon),#export-dialog button:not(.editor-icon){min-height:32px;padding:8px 12px;border-radius:8px;border:1px solid #ffffff12;background:#ffffff06;font-size:12px;font-weight:500}#editor-dialog select,#export-dialog select{min-height:34px;padding:7px 12px;border-radius:8px;font-size:12px}
 #export-dialog button.export-confirm{background:#f27656;color:#191614;border:0}#export-dialog a{font-size:12px;text-decoration:none;margin-right:12px}
 #final-edit #save-cut,#final-edit #export-film{min-height:32px;padding:7px 13px;font-size:12px;border-radius:8px}#final-edit #save-cut{margin-left:auto;background:transparent;border:1px solid #ffffff12;color:#a5abb5}#final-edit #export-film{background:#f27656;border:0;color:#191614}#final-edit .board-actions{margin-top:8px;padding:0}#cut-status{font-size:11px!important;color:#818894!important}
 @media(pointer:coarse){#final-edit button.editor-icon,dialog button.editor-icon{width:44px;height:44px;min-height:44px}}
 `;document.head.append(style);
 const toolbar=crewEl('div',undefined,'edit-toolbar');
 const format=host.querySelector(':scope > label');format.firstChild.textContent='Canvas ';toolbar.append(format);
 function select(label,id,choices){const l=crewEl('label',label+' '),s=crewEl('select');s.id=id;for(const [v,t] of choices){const o=crewEl('option',t);o.value=v;s.append(o)}l.append(s);toolbar.append(l);return s}
 const fit=select('Framing','edit-fit',[['contain','Fit · black bars'],['cover','Crop to fill']]);
 toolbar.append($('save-cut'),$('export-film'));
 const resolution=select('Export size','edit-resolution',[['720p','720p'],['1080p','1080p'],['4K','4K']]);
 const stage=crewEl('div');stage.id='edit-stage';let player=crewEl('video');player.id='edit-player';player.controls=false;player.playsInline=true;stage.append(player);let standby=crewEl('video');standby.playsInline=true;standby.muted=true;standby.preload='auto';standby.style.display='none';stage.append(standby);let preloadKey='',preloadReady=false,transportFrame=null;
 const hold=crewEl('canvas');hold.setAttribute('aria-hidden','true');hold.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;display:none;background:#000';stage.style.position='relative';stage.append(hold);let loadVersion=0;
 const transport=crewEl('div',undefined,'edit-transport'),play=crewEl('button','▶ Play film'),seek=crewEl('input'),time=crewEl('span','0:00 / 0:00');seek.type='range';seek.id='edit-seek';seek.min=0;seek.step=1/24;seek.setAttribute('aria-label','Film playhead');time.id='edit-time';transport.append(play,seek,time);
 const inspector=crewEl('div');inspector.id='edit-inspector';inspector.hidden=true;const jobs=crewEl('div');jobs.id='edit-jobs';
 host.insertBefore(toolbar,$('cut-clips'));host.insertBefore(stage,$('cut-clips'));host.insertBefore(transport,$('cut-clips'));$('cut-clips').after(inspector,jobs);
 const dialog=crewEl('dialog');dialog.id='editor-dialog';document.body.append(dialog);
 let selected=0,playing=false,dragIndex=null,insertAt=0,pendingInsert=null,enhanceId=null,undo=[],dialogVersion=0;
 const FPS=24,FRAME=1/FPS;
 const snap=t=>Math.round(t*FPS)/FPS;
 const sourceEnd=t=>Math.floor(t*FPS+1e-6)/FPS;
 const clock=t=>`${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`;
 const total=()=>cut.clips.reduce((n,c)=>n+c.end-c.start,0);
 const offset=i=>cut.clips.slice(0,i).reduce((n,c)=>n+c.end-c.start,0);
 const media=c=>filmMedia.find(v=>v.id===c?.video_id);
 function remember(){undo.push(JSON.stringify(cut));if(undo.length>30)undo.shift()}
 function changed(){cutDirty=true;$('cut-status').textContent='Unsaved edit';renderInspector();}
 function applyCanvas(){const [w,h]=cut.aspect_ratio.split(':').map(Number);stage.style.aspectRatio=w+'/'+h;stage.style.width='min(100%, '+(420*w/h)+'px)';player.style.objectFit=cut.fit||'contain';}
 function stop(){playing=false;player.pause();cancelAnimationFrame(transportFrame);playState()}
 function prepareNext(){
  const c=cut.clips[selected+1],m=media(c),key=c&&m?.video_url?m.video_url+'|'+c.start:'';
  if(key===preloadKey)return;preloadKey=key;preloadReady=false;standby.pause();
  standby.onloadedmetadata=standby.onseeked=standby.onloadeddata=null;
  if(!key){standby.removeAttribute('src');standby.load();return}
  const p=standby;const ready=()=>{if(p===standby&&preloadKey===key&&!p.seeking&&p.readyState>=2&&Math.abs(p.currentTime-c.start)<FRAME)preloadReady=true};
  p.onloadedmetadata=()=>{if(p===standby&&preloadKey===key)p.currentTime=c.start};p.onseeked=ready;p.onloadeddata=ready;p.src=m.video_url;
 }
 function runClock(){
  cancelAnimationFrame(transportFrame);
  const tick=()=>{if(!playing)return;refreshClock();const c=cut.clips[selected];
   if(c&&!player.seeking&&player.currentTime>=c.end){advance();return}
   transportFrame=requestAnimationFrame(tick);
  };transportFrame=requestAnimationFrame(tick);
 }
 function advance(){if(!playing)return;if(selected+1<cut.clips.length){loadClip(selected+1,true);renderTiles();renderInspector()}else{stop();seek.value=total();time.textContent=clock(total())+' / '+clock(total())}}
 function wirePlayer(){const p=player;p.ontimeupdate=()=>{if(p===player)refreshClock()};p.onended=()=>{if(p===player)advance()};p.onerror=()=>{if(p===player){stop();$('cut-status').textContent='This clip could not load. Try playing again.'}};}
 wirePlayer();
 function loadClip(index,autoplay=false,position=null){
  const token=++loadVersion;cancelAnimationFrame(transportFrame);
  const incoming=cut.clips[index],incomingMedia=media(incoming);
  if(autoplay&&position===null&&incoming&&preloadReady&&preloadKey===incomingMedia?.video_url+'|'+incoming.start){
   player.pause();const outgoing=player;player=standby;standby=outgoing;
   standby.id='';standby.style.display='none';standby.ontimeupdate=standby.onended=standby.onloadedmetadata=standby.onseeked=standby.onloadeddata=standby.onerror=null;
   player.onloadedmetadata=player.onseeked=player.onloadeddata=null;player.id='edit-player';player.style.display='';player.style.objectFit=cut.fit||'contain';player.muted=incoming.mute;selected=index;hold.style.display='none';wirePlayer();
   preloadKey='';preloadReady=false;player.play().then(()=>{if(token===loadVersion&&playing){runClock();prepareNext()}}).catch(()=>stop());return;
  }
  // Keep the outgoing decoded frame visible while the replacement buffers/seeks.
  if(player.readyState>=2&&player.videoWidth){try{hold.width=player.videoWidth;hold.height=player.videoHeight;hold.getContext('2d').drawImage(player,0,0);hold.style.objectFit=cut.fit||'contain';hold.style.display='block'}catch(e){hold.style.display='none'}}
  player.pause();selected=Math.max(0,Math.min(index,cut.clips.length-1));
  const c=cut.clips[selected],m=media(c);
  if(!c||!m?.video_url){hold.style.display='none';player.removeAttribute('src');player.load();return}
  const reveal=()=>{if(token===loadVersion)hold.style.display='none'};
  player.onloadedmetadata=()=>{if(token!==loadVersion)return;player.currentTime=position??c.start};
  player.onseeked=()=>{if(token!==loadVersion)return;
   requestAnimationFrame(()=>requestAnimationFrame(reveal));
   if(autoplay&&playing)player.play().then(()=>{if(token===loadVersion&&playing)runClock()}).catch(()=>{reveal();stop()});
   prepareNext();
  };
  player.onloadeddata=()=>{if(token===loadVersion&&!player.seeking)player.onseeked()};
  player.onerror=()=>{if(token!==loadVersion)return;reveal();stop();$('cut-status').textContent='This clip could not load. Try playing again.'};
  player.src=m.video_url;player.muted=c.mute;player.preload='auto';
 }

 function refreshClock(){const c=cut.clips[selected];const now=c?offset(selected)+Math.max(0,Math.min(c.end,player.currentTime)-c.start):0;seek.max=total();seek.value=now;time.textContent=clock(now)+' / '+clock(total());const head=$('timeline-playhead');if(head){head.style.left=(24+now*pixelsPerSecond)+'px';head.setAttribute('aria-valuenow',now.toFixed(2))}}
 play.onclick=()=>{if(playing)return stop();if(!cut.clips.length)return;const c=cut.clips[selected];if(!c)return;playing=true;playState();if(player.currentTime>=c.end&&selected===cut.clips.length-1)loadClip(0,true);else if(player.readyState>=2&&!player.seeking)player.play().then(()=>{if(playing){runClock();prepareNext()}}).catch(()=>stop());else loadClip(selected,true,Math.max(c.start,Math.min(player.currentTime,c.end-FRAME)));};
 seek.oninput=()=>{stop();let t=Number(seek.value),i=0;while(i<cut.clips.length-1&&t>=cut.clips[i].end-cut.clips[i].start){t-=cut.clips[i].end-cut.clips[i].start;i++}loadClip(i,false,cut.clips[i]?.start+t);renderTiles();renderInspector()};
 for(const control of [$('cut-ratio'),fit,resolution])control.onchange=()=>{remember();cut.aspect_ratio=$('cut-ratio').value;cut.fit=fit.value;cut.resolution=resolution.value;changed();applyCanvas()};
 function button(text,fn,parent){const b=crewEl('button',text);b.onclick=fn;if(text==='Close'){iconButton(b,'close','Close dialog');b.classList.add('editor-close')}parent.append(b);return b}
 function modal(title){closeClipMenu();dialog.classList.remove('trim-dialog');dialogVersion++;dialog.replaceChildren();dialog.append(crewEl('h2',title));button('Close',()=>dialog.close(),dialog);if(!dialog.open)dialog.showModal();return dialog}
 let pixelsPerSecond=40,trimActive=false;
 const zoomRow=crewEl('div',undefined,'edit-toolbar timeline-tools');
 const zoomLabel=crewEl('label','Zoom '),zoom=crewEl('input');zoom.type='range';zoom.min=16;zoom.max=100;zoom.value=pixelsPerSecond;zoom.setAttribute('aria-label','Timeline zoom');zoom.style.cssText='width:100px;padding:0;accent-color:#f27656';zoomLabel.append(zoom);zoomRow.append(zoomLabel);transport.append(zoomRow);seek.hidden=true;playState();
 zoom.oninput=()=>{pixelsPerSecond=Number(zoom.value);renderTiles();refreshClock()};
 const timelineStyle=crewEl('style');timelineStyle.textContent=`
 #edit-inspector{display:none}
 #cut-clips .clip-options{position:absolute;right:13px;top:5px;width:26px;height:24px;min-height:0;padding:0;border:1px solid #ffffff25;border-radius:6px;background:#111c;line-height:18px;font-size:20px;color:#fff;z-index:4;cursor:pointer}
 #clip-menu{position:fixed;z-index:1000;width:208px;max-height:calc(100dvh - 16px);overflow-y:auto;padding:5px;border:1px solid #ffffff20;border-radius:12px;background:#24272df5;box-shadow:0 12px 40px #0009;backdrop-filter:blur(20px)}#clip-menu[hidden]{display:none}
 #clip-menu .clip-menu-title{padding:7px 9px;font-size:10px;color:#a5abb5}#clip-menu button{display:block;width:100%;min-height:0;text-align:left;font-size:12px;font-weight:400;line-height:18px;padding:6px 9px;margin:0;border:0;border-radius:6px;background:transparent;color:#f4f1eb}#clip-menu button:hover,#clip-menu button:focus-visible{background:#ffffff10;outline:none}#clip-menu button:disabled{opacity:.3}#clip-menu button.clip-menu-remove{color:#f0a69d}#clip-menu hr{margin:4px 5px;border:0;border-top:1px solid #ffffff10}
 #editor-dialog.trim-dialog{width:min(360px,90vw);padding:20px;border-radius:14px}#editor-dialog.trim-dialog h2{font-size:17px;margin:0 0 12px}#editor-dialog.trim-dialog .trim-control{margin:16px 0;justify-content:space-between}#editor-dialog.trim-dialog .trim-control input[type=range]{flex:1;min-width:40px}#editor-dialog.trim-dialog .trim-control input[type=number]{width:76px}#editor-dialog.trim-dialog>button{padding:6px 12px}
 #cut-clips{display:block;position:relative;border:1px solid #34383f;background:#17191d;border-radius:12px;padding:0;min-height:164px;overflow-x:auto;touch-action:pan-x}
 .timeline-surface{position:relative;height:158px;min-width:100%}.timeline-ruler{position:absolute;top:0;left:24px;right:24px;height:30px;border-bottom:1px solid #34383f;cursor:crosshair;touch-action:none}.timeline-tick{position:absolute;top:0;height:29px;border-left:1px solid #34383f;color:#a5abb5;font-size:10px;padding:5px;pointer-events:none}.timeline-track{position:absolute;left:24px;right:24px;top:40px;height:80px;background:#24272d;border-radius:6px}
 #cut-clips .edit-tile{position:absolute;top:40px;height:80px;min-width:0;padding:0;box-sizing:border-box;cursor:grab;border-radius:5px;touch-action:none;user-select:none}
 #cut-clips .edit-tile video{height:52px;object-fit:cover;opacity:.8}#cut-clips .edit-tile small{padding:4px 10px;overflow:hidden;text-overflow:ellipsis;font-size:10px;pointer-events:none}#cut-clips .edit-tile[aria-pressed=true]{box-shadow:inset 0 0 0 1px #f27656}
 .timeline-handle{position:absolute;top:0;bottom:0;width:10px;min-height:0;padding:0!important;border:0!important;border-radius:0!important;background:#f2765699!important;cursor:ew-resize;touch-action:none;z-index:3}.timeline-handle::after{content:'';position:absolute;left:4px;top:28px;width:2px;height:20px;background:#17191d}.timeline-handle.start{left:0}.timeline-handle.end{right:0}.timeline-handle:focus{outline:2px solid #fff}
 #cut-clips .edit-add{position:absolute;top:126px;transform:translateX(-50%);font-size:17px;padding:0 7px;line-height:22px;border-radius:5px;background:#24272d;z-index:4}
 #timeline-playhead{position:absolute;top:19px;height:105px;width:12px;margin-left:-6px;border:0;padding:0;background:transparent;z-index:5;cursor:ew-resize;touch-action:none}#timeline-playhead::before{content:'';position:absolute;top:0;left:1px;border-top:9px solid var(--accent);border-left:5px solid transparent;border-right:5px solid transparent}#timeline-playhead::after{content:'';position:absolute;top:8px;bottom:0;left:5px;width:2px;background:var(--accent);pointer-events:none}.timeline-drop{box-shadow:inset 5px 0 #fff!important}
 `;document.head.append(timelineStyle);
 function timelineSeek(value){if(!cut.clips.length)return;stop();value=Math.max(0,Math.min(total()-FRAME,snap(value)));let t=value,i=0;while(i<cut.clips.length-1&&t>=cut.clips[i].end-cut.clips[i].start){t-=cut.clips[i].end-cut.clips[i].start;i++}if(i===selected){player.currentTime=cut.clips[i].start+t}else loadClip(i,false,cut.clips[i].start+t);renderInspector();document.querySelectorAll('.edit-tile').forEach((el,n)=>el.setAttribute('aria-pressed',String(n===i)));const head=$('timeline-playhead');if(head)head.style.left=(24+value*pixelsPerSecond)+'px';seek.value=value;time.textContent=clock(value)+' / '+clock(total())}
 function drawRuler(ruler){ruler.replaceChildren();const step=pixelsPerSecond<25?5:pixelsPerSecond<60?2:1;for(let t=0;t<=total()+step;t+=step){const tick=crewEl('span',clock(t),'timeline-tick');tick.style.left=t*pixelsPerSecond+'px';ruler.append(tick)}}
 function timelineGeometry(){const surface=$('cut-clips').querySelector('.timeline-surface');if(!surface)return;surface.style.width=(Math.max(total()*pixelsPerSecond+48,$('cut-clips').clientWidth))+'px';surface.querySelectorAll('.edit-tile').forEach((el,i)=>{const c=cut.clips[i];el.style.left=(24+offset(i)*pixelsPerSecond)+'px';el.style.width=Math.max(2,(c.end-c.start)*pixelsPerSecond)+'px';el.querySelector('small').textContent=`${i+1} · ${friendlyShot(media(c)?.shot_id||'Clip')} · ${(c.end-c.start).toFixed(2)}s`});surface.querySelectorAll('.edit-add').forEach((el,i)=>el.style.left=(24+offset(i)*pixelsPerSecond)+'px');drawRuler(surface.querySelector('.timeline-ruler'));refreshClock()}
 function renderTiles(){
  if(trimActive)return;closeClipMenu();const list=$('cut-clips');list.replaceChildren();
  const surface=crewEl('div',undefined,'timeline-surface'),ruler=crewEl('div',undefined,'timeline-ruler'),track=crewEl('div',undefined,'timeline-track');list.append(surface);surface.append(ruler,track);
  function pointerTime(e){return (e.clientX-list.getBoundingClientRect().left+list.scrollLeft-24)/pixelsPerSecond}
  function scrub(e){if(e.button!==0)return;e.preventDefault();const target=e.currentTarget;target.setPointerCapture(e.pointerId);timelineSeek(pointerTime(e));target.onpointermove=move=>timelineSeek(pointerTime(move));target.onpointerup=target.onpointercancel=()=>{target.onpointermove=null};}
  ruler.onpointerdown=scrub;
  for(let i=0;i<=cut.clips.length;i++){
   const add=button('+',()=>showAdd(i),surface);add.className='edit-add';add.setAttribute('aria-label','Add clip at position '+(i+1));if(i===cut.clips.length)break;
   const c=cut.clips[i],m=media(c),tile=crewEl('div',undefined,'edit-tile');tile.setAttribute('role','button');tile.tabIndex=0;tile.setAttribute('aria-label','Select clip '+(i+1));tile.setAttribute('aria-pressed',String(i===selected));surface.append(tile);
   const selectClip=()=>{stop();loadClip(i);renderTiles();renderInspector()};tile.onclick=e=>{if(!e.target.closest('button'))selectClip()};tile.oncontextmenu=e=>{e.preventDefault();openClipMenu(i,e.clientX,e.clientY,tile)};tile.onkeydown=e=>{if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();const r=tile.getBoundingClientRect();openClipMenu(i,r.left+20,r.top,tile);return}if(e.target===tile&&['Enter',' '].includes(e.key)){e.preventDefault();selectClip()}};
   tile.draggable=true;tile.ondragstart=e=>{if(trimActive){e.preventDefault();return}dragIndex=i;e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',String(i))};tile.ondragend=()=>{dragIndex=null;surface.querySelectorAll('.timeline-drop').forEach(el=>el.classList.remove('timeline-drop'))};
   tile.ondragover=e=>{e.preventDefault();tile.classList.add('timeline-drop')};tile.ondragleave=()=>tile.classList.remove('timeline-drop');tile.ondrop=e=>{e.preventDefault();if(dragIndex===null)return;const from=dragIndex;let at=i+(e.clientX>tile.getBoundingClientRect().left+tile.clientWidth/2?1:0);if(from<at)at--;dragIndex=null;if(at!==from){remember();const [v]=cut.clips.splice(from,1);cut.clips.splice(at,0,v);selected=at;changed()}renderCut()};
   if(m?.video_url){const thumb=crewEl('video');thumb.src=m.video_url+'#t='+c.start;thumb.preload='metadata';thumb.muted=true;tile.append(thumb)}tile.append(crewEl('small'));const more=button('⋯',e=>{e.stopPropagation();const r=more.getBoundingClientRect();openClipMenu(i,r.left,r.bottom+5,more)},tile);more.className='clip-options';more.setAttribute('aria-label',`Clip ${i+1} options`);more.setAttribute('aria-haspopup','menu');more.setAttribute('aria-expanded','false');more.ondragstart=e=>e.preventDefault();
   for(const edge of ['start','end']){
    const handle=crewEl('button',undefined,'timeline-handle '+edge);handle.setAttribute('aria-label',`Clip ${i+1} trim ${edge}`);handle.title=`Drag to trim ${edge}. Arrow keys adjust one frame (24 fps).`;tile.append(handle);handle.onclick=e=>e.stopPropagation();handle.ondragstart=e=>e.preventDefault();
    function adjust(value){c[edge]=edge==='start'?Math.max(0,Math.min(snap(value),c.end-FRAME)):Math.min(sourceEnd(m?.duration_s||c.end),Math.max(snap(value),c.start+FRAME));changed();timelineGeometry();player.currentTime=edge==='start'?c.start:Math.max(c.start,c.end-FRAME)}
    handle.onpointerdown=e=>{if(e.button!==0)return;e.preventDefault();e.stopPropagation();stop();selected=i;loadClip(i);remember();trimActive=true;tile.draggable=false;handle.setPointerCapture(e.pointerId);const x=e.clientX,initial=c[edge],scroll=list.scrollLeft;handle.onpointermove=move=>adjust(initial+(move.clientX-x+list.scrollLeft-scroll)/pixelsPerSecond);const finish=()=>{handle.onpointermove=null;trimActive=false;tile.draggable=true;renderTiles();renderInspector()};handle.onpointerup=finish;handle.onpointercancel=finish};
    handle.onkeydown=e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();e.stopPropagation();stop();selected=i;remember();adjust(c[edge]+(e.key==='ArrowRight'?FRAME:-FRAME));renderInspector()};
   }
  }
  const head=crewEl('button');head.id='timeline-playhead';head.setAttribute('aria-label','Drag timeline playhead');head.onpointerdown=scrub;head.onkeydown=e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();timelineSeek(Number(seek.value)+(e.key==='ArrowRight'?FRAME:-FRAME))}};surface.append(head);timelineGeometry();
 }
 const clipMenu=crewEl('div');clipMenu.id='clip-menu';clipMenu.hidden=true;clipMenu.setAttribute('role','menu');document.body.append(clipMenu);
 let menuTrigger=null;
 function closeClipMenu(restore=false){if(clipMenu.hidden)return;clipMenu.hidden=true;menuTrigger?.setAttribute('aria-expanded','false');if(restore&&menuTrigger?.isConnected)menuTrigger.focus();}
 document.addEventListener('pointerdown',e=>{if(!clipMenu.contains(e.target))closeClipMenu()});
 document.addEventListener('scroll',e=>{if(!clipMenu.contains(e.target))closeClipMenu()},true);window.addEventListener('resize',()=>closeClipMenu());
 clipMenu.onkeydown=e=>{const items=[...clipMenu.querySelectorAll('button:not(:disabled)')],i=items.indexOf(document.activeElement);if(e.key==='Escape'){e.preventDefault();closeClipMenu(true)}else if(e.key==='Tab'){closeClipMenu(true)}else if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)){e.preventDefault();items[e.key==='Home'?0:e.key==='End'?items.length-1:(i+(e.key==='ArrowDown'?1:-1)+items.length)%items.length]?.focus()}};
 function openClipMenu(index,x,y,trigger){
  closeClipMenu();stop();if(selected!==index)loadClip(index);selected=index;
  document.querySelectorAll('.edit-tile').forEach((el,n)=>el.setAttribute('aria-pressed',String(n===index)));
  const c=cut.clips[index],m=media(c);if(!c)return;
  menuTrigger=trigger;trigger.setAttribute('aria-expanded','true');clipMenu.replaceChildren();clipMenu.setAttribute('aria-label',`Clip ${index+1} actions`);
  clipMenu.append(crewEl('div',`Clip ${index+1} · ${friendlyShot(m?.shot_id||'Clip')}`,'clip-menu-title'));
  const action=(label,fn,disabled=false)=>{const b=button(label,()=>{closeClipMenu(true);if(cut.clips[index]!==c)return;fn()},clipMenu);b.setAttribute('role','menuitem');b.disabled=disabled;return b};
  const divider=()=>{const hr=crewEl('hr');hr.setAttribute('role','separator');clipMenu.append(hr)};
  action('Trim…',()=>showTrim(index));
  action('Split at playhead',()=>{const t=snap(player.currentTime);if(t<c.start+FRAME-1e-8||t>c.end-FRAME+1e-8)return notify('Move the playhead inside this clip to split it');remember();cut.clips.splice(index,1,{...c,end:t},{...c,id:crypto.randomUUID(),start:t});changed();renderCut()});
  action(c.mute?'Unmute':'Mute',()=>{remember();c.mute=!c.mute;player.muted=c.mute;changed()});divider();
  action('Extend before…',()=>extendClip(index,'before'));action('Extend after…',()=>extendClip(index,'after'));
  action('Expand canvas…',()=>showEnhance(m,c,'expand'));action('Upscale · FLUX…',()=>showEnhance(m,c,'upscale'));divider();
  for(const [label,delta] of [['Move earlier',-1],['Move later',1]])action(label,()=>{remember();[cut.clips[index],cut.clips[index+delta]]=[cut.clips[index+delta],c];selected=index+delta;changed();renderCut()},index+delta<0||index+delta>=cut.clips.length);
  action('Remove from edit',()=>{remember();cut.clips.splice(index,1);changed();renderCut()}).className='clip-menu-remove';
  clipMenu.hidden=false;clipMenu.style.left=Math.max(8,Math.min(x,innerWidth-clipMenu.offsetWidth-8))+'px';clipMenu.style.top=Math.max(8,Math.min(y,innerHeight-clipMenu.offsetHeight-8))+'px';clipMenu.querySelector('button').focus({preventScroll:true});
 }
 function showTrim(index){
  const c=cut.clips[index],m=media(c),d=modal('Trim clip');d.classList.add('trim-dialog');
  d.append(crewEl('p',`Clip ${index+1} · ${friendlyShot(m?.shot_id||'Clip')} · seconds`));
  let remembered=false;const fields={};
  for(const [key,label] of [['start','In'],['end','Out']]){const wrap=crewEl('label',label,'trim-control'),range=crewEl('input'),number=crewEl('input');range.type='range';number.type='number';fields[key]=[range,number];for(const input of [range,number]){input.min=0;input.max=m?.duration_s||c.end;input.step=input===number?'any':FRAME;input.value=c[key].toFixed(6);input.setAttribute('aria-label',`Trim ${label.toLowerCase()}`)}
   const update=input=>{if(cut.clips[index]!==c||input.value==='')return;const v=Number(input.value);if(!Number.isFinite(v))return;if(!remembered){remember();remembered=true}c[key]=key==='start'?Math.max(0,Math.min(snap(v),c.end-FRAME)):Math.min(sourceEnd(m?.duration_s||c.end),Math.max(snap(v),c.start+FRAME));for(const el of fields[key])el.value=c[key].toFixed(6);stop();player.currentTime=key==='start'?c.start:Math.max(c.start,c.end-FRAME);changed();renderTiles();refreshClock()};range.oninput=()=>update(range);number.oninput=()=>{if(number.value!==''&&number.validity.valid)update(number)};number.onchange=()=>update(number);wrap.append(range,number);d.append(wrap)
  }
  button('Done',()=>dialog.close(),d);
 }
 function renderInspector(){undoButton.disabled=!undo.length;}
 const undoButton=button('↶ Undo',()=>{if(!undo.length)return;stop();cut={...JSON.parse(undo.pop()),revision:cut.revision};changed();renderCut()},zoomRow);undoButton.disabled=true;iconButton(undoButton,'undo','Undo edit');zoomRow.prepend(undoButton);const fitTimeline=button('',()=>{pixelsPerSecond=Math.max(16,Math.min(100,($('cut-clips').clientWidth-48)/Math.max(total(),1)));zoom.value=pixelsPerSecond;renderTiles();refreshClock()},zoomRow);iconButton(fitTimeline,'fit','Fit timeline');
 renderCut=function(){stop();selected=Math.min(selected,Math.max(0,cut.clips.length-1));$('cut-ratio').value=cut.aspect_ratio;fit.value=cut.fit||'contain';resolution.value=cut.resolution||'720p';applyCanvas();renderTiles();renderInspector();loadClip(selected);refreshClock()};
 const oldLoad=loadFinalEdit;loadFinalEdit=async function(){undo=[];selected=0;await oldLoad()};
 async function insert(item,index=insertAt){remember();cut.clips.splice(Math.min(index,cut.clips.length),0,{id:crypto.randomUUID(),video_id:item.id,start:0,end:sourceEnd(item.duration_s),mute:false});changed();dialog.close();renderCut();await saveCut()}
 function showAdd(index){insertAt=index;const d=modal('Add a clip');const row=crewEl('div',undefined,'edit-toolbar');d.append(row);button('Video library',()=>libraryPicker('video'),row);button('Generate from image',()=>libraryPicker('image'),row);button('Upload',()=>uploadPicker(),row);if(index>0){button('Extend previous clip',()=>extendClip(index-1,'after'),row)}if(index<cut.clips.length){button('Extend before next clip',()=>extendClip(index,'before'),row)}}
 function libraryPicker(kind){const d=modal(kind==='video'?'Video library':'Choose a starting image');const grid=crewEl('div',undefined,'edit-library');d.append(grid);const entries=kind==='video'?filmMedia.filter(i=>i.kind==='video'&&i.status==='complete'):project.versions.filter(i=>i.status==='ok'&&i.image_url);for(const entry of entries){const b=button('',()=>kind==='video'?insert(entry):prepareGeneration({version_id:entry.version_id},entry.shot_id),grid);const visual=crewEl(kind==='video'?'video':'img');visual.src=kind==='video'?entry.video_url:entry.image_url;if(kind==='video'){visual.preload='metadata';visual.muted=true}b.append(visual,crewEl('small',friendlyShot(entry.shot_id||'Clip')))}if(!entries.length)d.append(crewEl('p','No saved '+(kind==='video'?'videos':'images')+' yet. Upload one to get started.'));if(kind==='image')for(const ref of project.image_references||[]){const b=button('',()=>prepareGeneration({reference_id:ref.id}),grid);const img=crewEl('img');img.src='/api/projects/'+project.id+'/references/'+ref.id;b.append(img,crewEl('small',ref.name||'Reference'))}}
 async function continueClip(index,edge){const c=cut.clips[index];await prepareGeneration({video_id:c.video_id,time_s:edge==='end'?Math.max(c.start,c.end-1/24):c.start},media(c)?.shot_id)}
 function uploadPicker(){const d=modal('Upload a video or starting image');const input=crewEl('input');input.type='file';input.accept='video/mp4,video/quicktime,image/png,image/jpeg,image/webp';d.append(input);input.onchange=async()=>{const file=input.files[0];if(!file)return;input.disabled=true;const id=project.id,shot=shots()[0]?.id;try{const isImage=file.type.startsWith('image/');const res=await fetch('/api/projects/'+id+(isImage?'/references':'/shots/'+shot+'/upload-video'),{method:'POST',headers:{'Content-Type':file.type},body:file});const result=await res.json();if(!res.ok)throw Error(result.detail||'Upload failed');if(isImage){await prepareGeneration({reference_id:result.id})}else{filmMedia.unshift(result);pendingInsert={id:result.id,index:insertAt,project:id};dialog.close();renderExports();startMediaPoll();notify('Preparing your uploaded clip…')}}catch(e){report(e)}finally{input.disabled=false}}}
 async function prepareGeneration(source,preferredShot){try{const id=project.id,shot=preferredShot||shots()[0]?.id;const frame=await api('/api/projects/'+id+'/editor-frame','POST',{shot_id:shot,...source});project=await api('/api/projects/'+id);dialog.close();await jumpToShot(shot,'video');$('video-frame').value=frame.frame_id;$('prompt').value='';$('prompt').placeholder='Describe what happens next. Keep one clear action.';videoDirty=true;showStartingFrame();estimateVideo();notify('Starting image ready. Describe the action and generate; then add the result to your edit.');pendingInsert={shot,index:insertAt,project:id}}catch(e){report(e)}}
 const oldAdd=addToCut;addToCut=async function(item){if(pendingInsert?.project===project.id&&pendingInsert.shot===item.shot_id){const at=pendingInsert.index;pendingInsert=null;await insert(item,at);await switchFilmSection('edit')}else await oldAdd(item)};
 async function showEnhance(item,clip,operation){enhanceId=crypto.randomUUID();const d=modal(operation==='expand'?'Expand the canvas':'Upscale with FLUX');d.append(crewEl('p',operation==='expand'?`Expand this ${(clip.end-clip.start).toFixed(1)}s selection to ${cut.aspect_ratio}. A new version will be saved for review.`:'FLUX Video Upscale enhances detail and increases width and height. Your original and its audio are retained.'));const settings=crewEl('div');d.append(settings);let prompt,factor,preserve,creativity;
 if(operation==='expand'){prompt=crewEl('textarea');prompt.rows=3;prompt.value='Extend the surrounding scene with matching lighting, perspective and motion.';prompt.setAttribute('aria-label','Expansion prompt');settings.append(prompt);const l=crewEl('label','Keep original picture in the centre ');preserve=crewEl('input');preserve.type='checkbox';preserve.checked=true;preserve.style.width='auto';l.prepend(preserve);settings.append(l,crewEl('p','New edges may need another pass. Review the joins before replacing your clip.'))}else{factor=crewEl('select');factor.setAttribute('aria-label','Upscale factor');for(const n of [1.5,2,2.5,3]){const o=crewEl('option',n+'× dimensions');o.value=n;factor.append(o)}factor.value='2';creativity=crewEl('select');creativity.setAttribute('aria-label','Upscale mode');for(const [value,label] of [[0,'Precise · preserve detail'],[1,'Creative · enhance detail']]){const o=crewEl('option',label);o.value=value;creativity.append(o)}settings.append(factor,creativity)}
 const status=crewEl('p','Checking connection…');d.append(status);const submit=button('Create new version',async()=>{submit.disabled=true;try{const result=await api('/api/projects/'+project.id+'/enhancements','POST',{request_id:enhanceId,video_id:item.id,clip_id:clip.id,operation,start:clip.start,end:clip.end,aspect_ratio:cut.aspect_ratio,factor:Number(factor?.value||2),creativity:Number(creativity?.value||0),prompt:prompt?.value||'',preserve_center:preserve?.checked??true});filmMedia.unshift(result);dialog.close();renderExports();startMediaPoll();notify('Processing started. Your current edit is unchanged.')}catch(e){status.textContent=e.message;submit.disabled=false}},d);submit.disabled=true;
 try{const c=await api('/api/projects/'+project.id+'/enhancement-options');const limit=operation==='expand'?c.expand_max_seconds:c.upscale_max_seconds;c.configured=operation==='upscale'?c.upscale_configured:c.configured;status.textContent=!c.configured?(operation==='upscale'?'Connect OpenRouter in Settings to enable this.':'Connect your fal API key in Settings to enable this.'):!c.storage_ready?'Connect media storage in Settings first.':clip.end-clip.start>limit?`Trim this selection to ${limit} seconds or less.`:'Paid processing through '+(operation==='upscale'?'OpenRouter':'fal')+'. Cost varies by output size and duration; estimate unavailable.';submit.disabled=!c.configured||!c.storage_ready||clip.end-clip.start>limit;if(!c.configured||!c.storage_ready)button('Open Settings',()=>{dialog.close();$('account').click()},d)}catch(e){status.textContent=e.message}}
 async function extendClip(index,direction){
  stop();const source={...cut.clips[index]},owner=project.id;
  const d=modal(direction==='before'?'Extend before · Prequel':'Extend after · Sequel'),ticket=dialogVersion;
  d.append(crewEl('p',direction==='before'?'Describe the action leading into this clip. The new clip must end at the selected clip’s first visible frame.':'Describe what happens next. The new clip starts at the selected clip’s last visible frame.'));
  const status=crewEl('p','Preparing the trimmed boundary…');d.append(status);
  try{
   const [boundary,available]=await Promise.all([api('/api/projects/'+owner+'/extension-boundary','POST',{clip_id:source.id,video_id:source.video_id,start:source.start,end:source.end,direction}),api('/api/projects/'+owner+'/video-models')]);
   if(project.id!==owner||!d.open||ticket!==dialogVersion)return;
   const picture=crewEl('img');picture.src=boundary.image_url;picture.alt=direction==='before'?'Required ending frame':'Starting frame';picture.style.cssText='width:100%;max-height:180px;object-fit:contain;background:#000;border-radius:8px';d.append(picture);
   const prompt=crewEl('textarea');prompt.rows=3;prompt.placeholder=direction==='before'?'What happens before this moment?':'What happens after this moment?';prompt.setAttribute('aria-label','Extension prompt');d.append(prompt);
   const referenceBox=crewEl('details'),referenceTitle=crewEl('summary','Character sheets · optional');referenceBox.open=true;referenceBox.append(referenceTitle);d.append(referenceBox);
   referenceBox.append(crewEl('p','Selecting sheets uses character-guided generation instead of a locked boundary frame. The join may need editing. Clear selections to restore the exact boundary mode.'));
   let selectedSheets=[];const picker=crewEl('div',undefined,'edit-toolbar');referenceBox.append(picker);
   function drawSheets(){picker.replaceChildren();for(const ref of project.image_references||[]){const label=crewEl('label'),check=crewEl('input');check.type='checkbox';check.checked=selectedSheets.includes(ref.id);check.style.width='auto';check.onchange=()=>{selectedSheets=check.checked?[...selectedSheets,ref.id]:selectedSheets.filter(id=>id!==ref.id);requestId=crypto.randomUUID();estimate()};const img=crewEl('img');img.src='/api/projects/'+owner+'/references/'+ref.id;img.alt=ref.name;img.style.cssText='width:70px;height:70px;object-fit:contain';label.append(check,img,crewEl('span',ref.name));picker.append(label)}}
   const upload=crewEl('input');upload.type='file';upload.accept='image/png,image/jpeg,image/webp';upload.setAttribute('aria-label','Upload character sheet');const uploadLabel=crewEl('label','Upload character sheet from your computer');uploadLabel.append(upload);referenceBox.append(uploadLabel);
   upload.onchange=async()=>{const file=upload.files[0];if(!file)return;upload.disabled=true;try{if(file.size>5*1024*1024)throw Error('Choose an image smaller than 5 MB');const result=await fetch('/api/projects/'+owner+'/references',{method:'POST',headers:{'Content-Type':file.type,'X-Image-Name':encodeURIComponent(file.name)},body:file});const data=await result.json();if(!result.ok)throw Error(data.error||data.detail||'Upload failed');const fresh=await api('/api/projects/'+owner);if(project.id!==owner||!d.open)return;const old=new Set((project.image_references||[]).map(r=>r.id));project.image_references=fresh.image_references;selectedSheets.push(...fresh.image_references.filter(r=>!old.has(r.id)).map(r=>r.id));drawSheets();requestId=crypto.randomUUID();estimate()}catch(e){status.textContent=e.message}finally{upload.disabled=false;upload.value=''}};
   drawSheets();
   const row=crewEl('div',undefined,'edit-toolbar');d.append(row);
   function field(label){const l=crewEl('label',label+' '),select=crewEl('select');select.setAttribute('aria-label',label);l.append(select);row.append(l);return select}
   const model=field('Extension model'),duration=field('Extension seconds'),quality=field('Extension resolution'),ratio=field('Extension ratio');
   const audioLabel=crewEl('label','Generate audio '),audio=crewEl('input');audio.type='checkbox';audio.style.width='auto';audioLabel.prepend(audio);d.append(audioLabel);
   const choices=available.models.filter(m=>(m.frame_positions||[]).includes(boundary.anchor_position));
   function fill(select,values){select.replaceChildren();for(const value of values){const o=crewEl('option',String(value));o.value=value;select.append(o)}}
   for(const m of choices){const o=crewEl('option',m.name||m.id);o.value=m.id;model.append(o)}
   let requestId=crypto.randomUUID(),version=0;
   const price=crewEl('p');d.append(price);
   const submit=button('Generate '+(direction==='before'?'prequel':'sequel'),async()=>{
    submit.disabled=true;try{const job=await api('/api/projects/'+owner+'/videos','POST',body());if(project.id!==owner)return;filmMedia.unshift(job);dialog.close();renderExports();startMediaPoll();notify('Extension generating. Preview it below before inserting.')}catch(e){price.textContent=e.message;submit.disabled=false}
   },d);submit.disabled=true;
   function body(){return {request_id:requestId,shot_id:boundary.shot_id,frame_id:boundary.frame_id,anchor_position:boundary.anchor_position,reference_mode:selectedSheets.length?'character':'shot',reference_ids:selectedSheets,prompt:prompt.value.trim(),model:model.value,duration_s:Number(duration.value),aspect_ratio:ratio.value,resolution:quality.value,audio:audio.checked}}
   async function estimate(){const token=++version;submit.disabled=true;if(!choices.length||!prompt.value.trim()){price.textContent='Describe the action to see the estimate.';return}try{const result=await api('/api/projects/'+owner+'/video-estimate','POST',body());if(token!==version||project.id!==owner||ticket!==dialogVersion||!d.open)return;price.textContent=result.offline?'Offline preview · no charge':result.cost==null?'Paid generation · estimate unavailable':'Estimated cost: $'+Number(result.cost).toFixed(4);submit.disabled=false}catch(e){if(token===version&&ticket===dialogVersion)price.textContent=e.message}}
   function sync(){const m=choices.find(m=>m.id===model.value);if(!m)return;fill(duration,m.durations?.length?m.durations:Array.from({length:m.duration_max},(_,i)=>i+1));if([...duration.options].some(o=>o.value==='5'))duration.value='5';fill(quality,m.resolutions);fill(ratio,m.ratios);if(m.ratios.includes(cut.aspect_ratio))ratio.value=cut.aspect_ratio;audio.disabled=!m.audio;audio.checked=false;estimate()}
   model.onchange=sync;for(const el of [duration,quality,ratio,audio])el.onchange=estimate;let timer;prompt.oninput=()=>{++version;submit.disabled=true;clearTimeout(timer);timer=setTimeout(estimate,350)};
   status.textContent=choices.length?'Default: locked boundary frame. Open Character sheets to select library images or upload a sheet for character-guided generation.':'No connected model advertises '+(direction==='before'?'ending':'starting')+'-frame support. Choose another provider in Settings.';
   sync();
  }catch(e){status.textContent=e.message}
 }
 async function insertExtension(item){
  const e=item.extension,matches=cut.clips.map((c,index)=>({c,index})).filter(({c})=>(!e.clip_id||c.id===e.clip_id)&&c.video_id===e.video_id&&Math.abs(c.start-e.start)<.001&&Math.abs(c.end-e.end)<.001);
  if(matches.length!==1)return notify('The source clip has moved or changed, or appears more than once. Use + and select this extension from the library.');
  await insert(item,matches[0].index+(e.direction==='after'?1:0));
 }

 const exportDialog=crewEl('dialog');exportDialog.id='export-dialog';exportDialog.style.cssText='width:min(580px,90vw);max-height:85vh;overflow:auto;padding:24px';document.body.append(exportDialog);
 exportDialog.append(crewEl('h2','Export your film'));button('Close',()=>exportDialog.close(),exportDialog);
 exportDialog.append(crewEl('p','Choose the export size. For AI detail enhancement, export first, then choose Upscale with FLUX on the saved film.'));
 exportDialog.append(resolution.parentElement);
 const exportAction=$('export-film').onclick;
 const createExport=button('Create export',async()=>{createExport.disabled=true;try{await exportAction();exportNotice.textContent=$('cut-status').textContent}catch(e){exportNotice.textContent=e.message}finally{createExport.disabled=false}},exportDialog);
 createExport.classList.add('export-confirm');
 const exportNotice=crewEl('p');exportNotice.setAttribute('role','status');exportDialog.append(exportNotice,$('film-exports'));
 $('export-film').onclick=()=>{exportNotice.textContent='';renderExports();exportDialog.showModal()};
 const oldExports=renderExports;renderExports=function(){oldExports();if(exportDialog.open)exportNotice.textContent=$('cut-status').textContent;if(cutDirty)$('cut-status').textContent='Unsaved edit';jobs.replaceChildren();for(const item of filmMedia.filter(i=>i.backend==='fal-enhance'||i.backend==='openrouter-enhance'||i.id===pendingInsert?.id)){const card=crewEl('div',undefined,'edit-job');card.append(crewEl('strong',item.model+' · '+item.status));if(item.error)card.append(crewEl('p',item.error));if(item.video_url){const v=crewEl('video');v.src=item.video_url;v.controls=true;card.append(v);if(item.extension)button('Insert '+item.extension.direction+' source clip',()=>insertExtension(item),card);else button('Add to edit',()=>insert(item,cut.clips.length),card);if(item.enhancement)button('Replace matching selection',async()=>{const spec=item.enhancement;const index=cut.clips.findIndex(c=>(!spec.clip_id||c.id===spec.clip_id)&&c.video_id===item.source_id&&Math.abs(c.start-spec.start)<.01&&Math.abs(c.end-spec.end)<.01);if(index<0)return notify('The original selection has changed. Add this version from the library instead.');remember();cut.clips[index]={id:cut.clips[index].id,video_id:item.id,start:0,end:item.duration_s,mute:cut.clips[index].mute};changed();renderCut();await saveCut()},card)}else if(item.status==='waiting')button('Resume',async()=>{await api('/api/projects/'+project.id+'/videos/'+item.id+'/resume','POST',{});startMediaPoll()},card);jobs.append(card)}
 if(pendingInsert?.id){const item=filmMedia.find(i=>i.id===pendingInsert.id);if(item?.status==='complete'){const at=pendingInsert.index;pendingInsert=null;insert(item,at).catch(report)}}
 for(const card of $('film-exports').children){const video=card.querySelector('video');if(!video)continue;const item=filmMedia.find(i=>i.video_url===video.getAttribute('src'));if(item)button('Upscale film · FLUX',()=>{exportDialog.close();showEnhance(item,{start:0,end:item.duration_s},'upscale')},card)}};
 const priorSection=showFilmSection;showFilmSection=function(){if(filmSection!=='edit'){stop();closeClipMenu()}priorSection()};
})();
