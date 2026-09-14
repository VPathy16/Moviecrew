/* Editing owns the cut; processing creates candidates and never replaces it silently. */
(() => {
 const host=$('final-edit');
 host.querySelector('h1').textContent='Edit your film';
 host.querySelector('p').textContent='Shape the story. Drag to edit. Right-click a clip for more.';
 const style=document.createElement('style');style.textContent=`
 #final-edit{max-width:1320px;padding:24px 32px}#final-edit h1{font-size:24px;margin:8px 0}
 .edit-toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0}.edit-toolbar label{font-size:11px;color:#a5abb5;margin:0}.edit-toolbar select{padding:7px 10px;width:auto;font-size:12px}.edit-toolbar button{font-size:12px;padding:8px 12px}
 #edit-stage{background:#000;max-height:420px;max-width:100%;margin:0 auto;overflow:hidden;border:1px solid #34383f;border-radius:10px;display:flex;justify-content:center}#edit-player{width:100%;height:100%;max-height:420px;background:#000}
 #edit-time{font-variant-numeric:tabular-nums;font-size:12px;color:#a5abb5}.edit-transport{display:flex;align-items:center;gap:16px;margin:10px 0}#edit-seek{flex:1;padding:0;accent-color:#f27656}
 #cut-clips{display:flex;align-items:center;gap:6px;overflow-x:auto;padding:12px 0 18px;min-height:100px}.edit-tile{flex-shrink:0;height:90px;min-width:110px;border:1px solid #34383f;border-radius:9px;padding:0;overflow:hidden;background:#24272d;text-align:left}.edit-tile[aria-pressed=true]{border:2px solid #f27656}.edit-tile video{width:100%;height:55px;object-fit:cover;pointer-events:none}.edit-tile small{display:block;padding:3px 8px;font-size:10px;white-space:nowrap}.edit-add{padding:4px 8px;border:0;background:transparent;color:#f4f1eb;font-size:20px;flex-shrink:0}
 #edit-inspector{padding:12px 16px;border:1px solid #34383f;border-radius:12px;margin-bottom:16px}.trim-control{display:flex;align-items:center;gap:8px;font-size:12px}.trim-control input[type=range]{width:130px;padding:0;accent-color:#f27656}.trim-control input[type=number]{width:70px;padding:6px;font-size:12px}#edit-inspector .edit-toolbar{margin:6px 0}
 .inspector-title{display:block;font-size:16px;margin-bottom:2px}#edit-inspector h4{font-size:11px;text-transform:uppercase;letter-spacing:.03em;color:#a5abb5;margin:14px 0 6px}
 .inspector-direction{font-size:13px;line-height:1.5;white-space:pre-wrap;margin:0}.inspector-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
 .inspector-chip{display:inline-block;padding:4px 10px;border-radius:999px;background:#24272d;border:1px solid #34383f;font-size:11px;color:#f4f1eb}.inspector-regenerate{margin-top:10px;display:flex;align-items:center;gap:6px}
 #editor-dialog{width:min(620px,90vw);max-height:85vh;overflow:auto;padding:24px;position:relative}#editor-dialog h2{font-size:20px}#editor-dialog p{font-size:13px;color:#a5abb5}#editor-dialog button{font-size:12px}#editor-dialog video{width:100%;max-height:250px}.edit-library{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.edit-library button{padding:6px}.edit-library img,.edit-library video{height:90px;width:100%;object-fit:cover}.edit-library small{display:block;font-size:11px}.edit-job{border-top:1px solid #34383f;padding:12px 0}.edit-job video{max-height:200px;width:100%}
 .icon-btn{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;min-height:0;padding:0;border-radius:8px;flex-shrink:0}.icon-btn svg{display:block}
 .dialog-close{position:absolute;top:14px;right:14px;width:30px;height:30px;padding:0;border-radius:6px;background:transparent;border:0;color:#a5abb5}.dialog-close:hover{background:#ffffff10;color:#f4f1eb}
 .fit-btn{padding:6px 12px;font-size:11px}.fit-btn[aria-pressed=true],.snap-btn[aria-pressed=true]{background:var(--accent);color:#17191d}
 @media(max-width:700px){#final-edit{padding:18px 12px}.edit-toolbar{gap:7px}.edit-library{grid-template-columns:repeat(2,1fr)}#edit-stage,#edit-player{max-height:320px}}
 `;document.head.append(style);
 const SVG_NS='http://www.w3.org/2000/svg';
 function iconSvg(inner,size=16){const svg=document.createElementNS(SVG_NS,'svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('width',size);svg.setAttribute('height',size);svg.setAttribute('fill','none');svg.setAttribute('stroke','currentColor');svg.setAttribute('stroke-width','2');svg.setAttribute('stroke-linecap','round');svg.setAttribute('stroke-linejoin','round');svg.style.display='block';svg.innerHTML=inner;return svg}
 const ICONS={
  play:'<path d="M8 5v14l11-7z" fill="currentColor" stroke="none"/>',
  pause:'<rect x="6" y="5" width="4" height="14" fill="currentColor" stroke="none"/><rect x="14" y="5" width="4" height="14" fill="currentColor" stroke="none"/>',
  undo:'<polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>',
  redo:'<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>',
  close:'<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  refresh:'<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>',
  'skip-prev':'<rect x="5" y="4" width="2" height="16" fill="currentColor" stroke="none"/><path d="M19 5 8 12l11 7V5z" fill="currentColor" stroke="none"/>',
  'skip-next':'<rect x="17" y="4" width="2" height="16" fill="currentColor" stroke="none"/><path d="M5 5l11 7-11 7V5z" fill="currentColor" stroke="none"/>',
  minus:'<line x1="5" y1="12" x2="19" y2="12"/>',
  plus:'<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  snap:'<path d="M6 4v7a6 6 0 0 0 12 0V4"/><path d="M6 4h4"/><path d="M14 4h4"/><path d="M6 10h4"/><path d="M14 10h4"/>',
 };
 function setIcon(btn,name,label){btn.replaceChildren(iconSvg(ICONS[name]));btn.setAttribute('aria-label',label);btn.title=label}
 function iconButton(name,fn,label,parent){const b=crewEl('button');b.type='button';b.className='icon-btn';setIcon(b,name,label);b.onclick=fn;if(parent)parent.append(b);return b}
 const toolbar=crewEl('div',undefined,'edit-toolbar');
 const format=host.querySelector(':scope > label');format.firstChild.textContent='Canvas ';toolbar.append(format);
 function select(label,id,choices){const l=crewEl('label',label+' '),s=crewEl('select');s.id=id;for(const [v,t] of choices){const o=crewEl('option',t);o.value=v;s.append(o)}l.append(s);toolbar.append(l);return s}
 const fit=select('Framing','edit-fit',[['contain','Fit · black bars'],['cover','Crop to fill']]);
 const resolution=select('Export size','edit-resolution',[['720p','720p']]);
 const RESOLUTION_TIERS=[['480p',480],['720p',720],['1080p',1080],['1440p',1440],['4K',2160]];
 // The short edge, not raw height: a 1080x1920 portrait clip is 1080p-grade
 // footage, not 1920p-grade, and comparing tiers against height alone would
 // wrongly qualify it for 1440p.
 function sourceMaxShortEdge(){
  let max=0,allKnown=true;
  for(const clip of cut.clips){
   const m=media(clip);
   if(m?.width&&m?.height)max=Math.max(max,Math.min(m.width,m.height));
   else allKnown=false;
  }
  return {max,allKnown};
 }
 function refreshResolutionOptions(){
  const {max:maxEdge,allKnown}=sourceMaxShortEdge();
  const desired=cut.resolution||'720p';
  // Only cap the offered tiers when every clip's dimensions are actually
  // known. Clips generated before width/height was recorded report none at
  // all; treating "unknown" as "assume 1080p" would silently downgrade (and
  // overwrite, via cut.resolution below) an already-saved 4K export choice.
  const applicable=maxEdge&&allKnown?RESOLUTION_TIERS.filter(([,h])=>h<=maxEdge):RESOLUTION_TIERS;
  const tiers=applicable.length?applicable:RESOLUTION_TIERS.slice(0,1);
  resolution.replaceChildren();
  for(const [name,h] of tiers){const o=crewEl('option',h===maxEdge?name+' · source quality':name);o.value=name;resolution.append(o)}
  resolution.value=tiers.some(([name])=>name===desired)?desired:tiers[tiers.length-1][0];
  cut.resolution=resolution.value;
 }
 const stage=crewEl('div');stage.id='edit-stage';const player=crewEl('video');player.id='edit-player';player.controls=true;player.playsInline=true;stage.append(player);
 const hold=crewEl('canvas');hold.setAttribute('aria-hidden','true');hold.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none;display:none;background:#000';stage.style.position='relative';stage.append(hold);let loadVersion=0;
 const transport=crewEl('div',undefined,'edit-transport');
 const skipPrev=iconButton('skip-prev',()=>{stop();loadClip(selected-1);renderTiles();renderInspector()},'Previous clip');
 const play=iconButton('play',null,'Play film');
 const skipNext=iconButton('skip-next',()=>{stop();loadClip(selected+1);renderTiles();renderInspector()},'Next clip');
 const seek=crewEl('input'),time=crewEl('span','0:00 / 0:00');seek.type='range';seek.id='edit-seek';seek.min=0;seek.step=.01;seek.setAttribute('aria-label','Film playhead');time.id='edit-time';transport.append(skipPrev,play,skipNext,seek,time);
 const inspector=crewEl('div');inspector.id='edit-inspector';inspector.hidden=true;const jobs=crewEl('div');jobs.id='edit-jobs';
 host.insertBefore(toolbar,$('cut-clips'));host.insertBefore(stage,$('cut-clips'));host.insertBefore(transport,$('cut-clips'));host.insertBefore(inspector,$('cut-clips'));$('cut-clips').after(jobs);
 const dialog=crewEl('dialog');dialog.id='editor-dialog';document.body.append(dialog);
 let selected=0,playing=false,insertAt=0,pendingInsert=null,enhanceId=null,undo=[],redo=[],dialogVersion=0,shotCastCache={},castToken=0;
 const clock=t=>`${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`;
 const total=()=>cut.clips.reduce((n,c)=>n+c.end-c.start,0);
 const offset=i=>cut.clips.slice(0,i).reduce((n,c)=>n+c.end-c.start,0);
 const media=c=>filmMedia.find(v=>v.id===c?.video_id);
 function remember(){undo.push(JSON.stringify(cut));if(undo.length>30)undo.shift();redo.length=0}
 function changed(){cutDirty=true;$('cut-status').textContent='Unsaved edit';renderInspector();}
 function applyCanvas(){const [w,h]=cut.aspect_ratio.split(':').map(Number);stage.style.aspectRatio=w+'/'+h;stage.style.width='min(100%, '+(420*w/h)+'px)';player.style.objectFit=cut.fit||'contain';}
 function stop(){playing=false;player.pause();setIcon(play,'play','Play film')}
 function loadClip(index,autoplay=false,position=null){
  const token=++loadVersion;
  // Keep the outgoing decoded frame visible while the replacement buffers/seeks.
  if(player.readyState>=2&&player.videoWidth){try{hold.width=player.videoWidth;hold.height=player.videoHeight;hold.getContext('2d').drawImage(player,0,0);hold.style.objectFit=cut.fit||'contain';hold.style.display='block'}catch(e){hold.style.display='none'}}
  player.pause();selected=Math.max(0,Math.min(index,cut.clips.length-1));
  const c=cut.clips[selected],m=media(c);
  if(!c||!m?.video_url){hold.style.display='none';player.removeAttribute('src');player.load();return}
  const reveal=()=>{if(token===loadVersion)hold.style.display='none'};
  player.onloadedmetadata=()=>{if(token!==loadVersion)return;player.currentTime=position??c.start};
  player.onseeked=()=>{if(token!==loadVersion)return;
   requestAnimationFrame(()=>requestAnimationFrame(reveal));
   if(autoplay&&playing)player.play().catch(()=>{reveal();stop()});
  };
  player.onloadeddata=()=>{if(token===loadVersion&&!player.seeking)player.onseeked()};
  player.onerror=()=>{if(token!==loadVersion)return;reveal();stop();$('cut-status').textContent='This clip could not load. Try playing again.'};
  player.src=m.video_url;player.muted=c.mute;player.preload='auto';
 }

 function refreshClock(){const c=cut.clips[selected];const now=c?offset(selected)+Math.max(0,Math.min(c.end,player.currentTime)-c.start):0;seek.max=total();seek.value=now;time.textContent=clock(now)+' / '+clock(total());const head=$('timeline-playhead');if(head){head.style.left=(24+now*pixelsPerSecond)+'px';head.setAttribute('aria-valuenow',now.toFixed(2))}}
 player.ontimeupdate=()=>{refreshClock();const c=cut.clips[selected];if(c&&player.currentTime>=c.end-.025){if(playing&&selected+1<cut.clips.length){loadClip(selected+1,true);renderTiles();renderInspector()}else stop()}};
 player.onended=()=>{if(playing&&selected+1<cut.clips.length){loadClip(selected+1,true);renderTiles();renderInspector()}else stop()};
 play.onclick=()=>{if(playing)return stop();if(!cut.clips.length)return;playing=true;setIcon(play,'pause','Pause film');loadClip(0,true);renderTiles();renderInspector()};
 seek.oninput=()=>{stop();let t=Number(seek.value),i=0;while(i<cut.clips.length-1&&t>cut.clips[i].end-cut.clips[i].start){t-=cut.clips[i].end-cut.clips[i].start;i++}loadClip(i,false,cut.clips[i]?.start+t);renderTiles();renderInspector()};
 for(const control of [$('cut-ratio'),fit,resolution])control.onchange=()=>{remember();cut.aspect_ratio=$('cut-ratio').value;cut.fit=fit.value;cut.resolution=resolution.value;changed();applyCanvas()};
 function button(text,fn,parent){const b=crewEl('button',text);b.onclick=fn;parent.append(b);return b}
 function modal(title){closeClipMenu();dialog.classList.remove('trim-dialog');dialogVersion++;dialog.replaceChildren();dialog.append(crewEl('h2',title));iconButton('close',()=>dialog.close(),'Close',dialog).className='dialog-close';if(!dialog.open)dialog.showModal();return dialog}
 let pixelsPerSecond=40,trimActive=false,userZoomed=false,snapEnabled=true;
 const SNAP_PX=6;
 const zoomRow=crewEl('div',undefined,'edit-toolbar');zoomRow.append(crewEl('strong','Timeline'),crewEl('span','Drag edges to trim · right-click for options','muted'));
 const zoomOut=iconButton('minus',()=>{userZoomed=true;zoom.value=Math.max(Number(zoom.min),pixelsPerSecond-8);zoom.dispatchEvent(new Event('input'))},'Zoom out',zoomRow);
 const zoom=crewEl('input');zoom.type='range';zoom.min=16;zoom.max=100;zoom.value=pixelsPerSecond;zoom.setAttribute('aria-label','Timeline zoom');zoom.style.cssText='width:100px;padding:0;accent-color:#f27656';zoomRow.append(zoom);
 const zoomIn=iconButton('plus',()=>{userZoomed=true;zoom.value=Math.min(Number(zoom.max),pixelsPerSecond+8);zoom.dispatchEvent(new Event('input'))},'Zoom in',zoomRow);
 const fitButton=crewEl('button','Fit');fitButton.type='button';fitButton.onclick=()=>{userZoomed=false;renderTiles()};zoomRow.append(fitButton);
 const snapButton=iconButton('snap',()=>{snapEnabled=!snapEnabled;snapButton.setAttribute('aria-pressed',String(snapEnabled))},'Snap to grid',zoomRow);snapButton.classList.add('snap-btn');snapButton.setAttribute('aria-pressed','true');
 zoomRow.append(crewEl('span','24 fps','muted'));
 $('cut-clips').before(zoomRow);
 // Until the viewer picks a zoom level themselves, the timeline scales to
 // fill the visible track instead of sitting at a fixed 40px/s — a short
 // edit otherwise renders as a sliver against a mostly-empty bar. Manual
 // zoom (the slider, +/-, or scrolling past what fits) always wins from
 // then on; Fit hands control back to auto-fit.
 function fitPixelsPerSecond(){
  const available=$('cut-clips').clientWidth-48,duration=Math.max(total(),.001);
  return Math.max(Number(zoom.min),Math.min(Number(zoom.max),available/duration));
 }
 zoom.oninput=()=>{userZoomed=true;pixelsPerSecond=Number(zoom.value);renderTiles();refreshClock()};
 const timelineStyle=crewEl('style');timelineStyle.textContent=`
 #cut-clips .clip-options{position:absolute;right:13px;top:5px;width:26px;height:24px;min-height:0;padding:0;border:1px solid #ffffff25;border-radius:6px;background:#111c;line-height:18px;font-size:20px;color:#fff;z-index:4;cursor:pointer}
 #clip-menu{position:fixed;z-index:1000;width:208px;max-height:calc(100dvh - 16px);overflow-y:auto;padding:5px;border:1px solid #ffffff20;border-radius:12px;background:#24272df5;box-shadow:0 12px 40px #0009;backdrop-filter:blur(20px)}#clip-menu[hidden]{display:none}
 #clip-menu .clip-menu-title{padding:7px 9px;font-size:10px;color:#a5abb5;letter-spacing:.04em}#clip-menu button{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;min-height:0;text-align:left;font-size:12px;font-weight:400;line-height:18px;padding:6px 9px;margin:0;border:0;border-radius:6px;background:transparent;color:#f4f1eb}#clip-menu button:hover,#clip-menu button:focus-visible{background:#ffffff10;outline:none}#clip-menu button:disabled{opacity:.3}#clip-menu button.clip-menu-remove{color:#f0a69d}#clip-menu hr{margin:4px 5px;border:0;border-top:1px solid #ffffff10}#clip-menu .menu-hint{font-size:10px;color:#666a72;flex-shrink:0}
 #editor-dialog.trim-dialog{width:min(360px,90vw);padding:20px;border-radius:14px}#editor-dialog.trim-dialog h2{font-size:17px;margin:0 0 12px}#editor-dialog.trim-dialog .trim-control{margin:16px 0;justify-content:space-between}#editor-dialog.trim-dialog .trim-control input[type=range]{flex:1;min-width:40px}#editor-dialog.trim-dialog .trim-control input[type=number]{width:76px}#editor-dialog.trim-dialog>button{padding:6px 12px}
 #cut-clips{display:block;position:relative;border:1px solid #34383f;background:#17191d;border-radius:12px;padding:0;min-height:164px;overflow-x:auto;touch-action:pan-x}
 .timeline-surface{position:relative;height:190px;min-width:100%}.timeline-ruler{position:absolute;top:0;left:24px;right:24px;height:30px;border-bottom:1px solid #34383f;cursor:crosshair;touch-action:none}.timeline-tick{position:absolute;top:0;height:29px;border-left:1px solid #34383f;color:#a5abb5;font-size:10px;padding:5px;pointer-events:none}.timeline-track{position:absolute;left:24px;right:24px;top:40px;height:80px;background:#24272d;border-radius:6px}
 .timeline-wave-lane{position:absolute;left:24px;right:24px;top:124px;height:34px}.timeline-wave{position:absolute;top:0;height:34px;border-radius:4px;background:#1c1e22}
 #cut-clips .edit-tile{position:absolute;top:40px;height:80px;min-width:0;padding:0;box-sizing:border-box;cursor:grab;border-radius:5px;touch-action:none;user-select:none;transition:box-shadow .12s}
 #cut-clips .edit-tile.dragging{cursor:grabbing;z-index:6;box-shadow:0 8px 20px #000a;transition:none}
 #cut-clips .edit-tile video{height:52px;object-fit:cover;opacity:.8}#cut-clips .edit-tile small{padding:4px 10px;overflow:hidden;text-overflow:ellipsis;font-size:10px;pointer-events:none}#cut-clips .edit-tile[aria-pressed=true]{box-shadow:inset 0 0 0 1px #f27656}
 /* Above the playhead (z-index 5): the playhead can land exactly on a
    clip boundary — right where its own trim handle sits — after simply
    selecting or reordering a clip, and would otherwise silently swallow
    the pointerdown meant for the handle. */
 .timeline-handle{position:absolute;top:0;bottom:0;width:10px;min-height:0;padding:0!important;border:0!important;border-radius:0!important;background:#f2765699!important;cursor:ew-resize;touch-action:none;z-index:7}.timeline-handle::after{content:'';position:absolute;left:4px;top:28px;width:2px;height:20px;background:#17191d}.timeline-handle.start{left:0}.timeline-handle.end{right:0}.timeline-handle:focus{outline:2px solid #fff}
 #cut-clips .edit-add{position:absolute;top:164px;transform:translateX(-50%);font-size:17px;padding:0 7px;line-height:22px;border-radius:5px;background:#24272d;z-index:4}
 #timeline-playhead{position:absolute;top:19px;height:139px;width:12px;margin-left:-6px;border:0;padding:0;background:transparent;z-index:5;cursor:ew-resize;touch-action:none}#timeline-playhead::before{content:'';position:absolute;top:0;left:1px;border-top:9px solid var(--accent);border-left:5px solid transparent;border-right:5px solid transparent}#timeline-playhead::after{content:'';position:absolute;top:8px;bottom:0;left:5px;width:2px;background:var(--accent);pointer-events:none}.timeline-drop{box-shadow:inset 5px 0 #fff!important}
 `;document.head.append(timelineStyle);
 function timelineSeek(value){if(!cut.clips.length)return;stop();value=Math.max(0,Math.min(total()-.001,value));
  if(snapEnabled){
   const candidates=[Math.round(value)];for(let n=1;n<cut.clips.length;n++)candidates.push(offset(n));
   let best=value,bestDist=SNAP_PX/pixelsPerSecond;
   for(const cand of candidates){const dist=Math.abs(cand-value);if(dist<bestDist){bestDist=dist;best=cand}}
   value=Math.max(0,Math.min(total()-.001,best));
  }
  let t=value,i=0;while(i<cut.clips.length-1&&t>=cut.clips[i].end-cut.clips[i].start){t-=cut.clips[i].end-cut.clips[i].start;i++}if(i===selected){player.currentTime=cut.clips[i].start+t}else loadClip(i,false,cut.clips[i].start+t);renderInspector();document.querySelectorAll('.edit-tile').forEach((el,n)=>el.setAttribute('aria-pressed',String(n===i)));const head=$('timeline-playhead');if(head)head.style.left=(24+value*pixelsPerSecond)+'px';seek.value=value;time.textContent=clock(value)+' / '+clock(total())}
 function drawRuler(ruler){ruler.replaceChildren();const step=pixelsPerSecond<25?5:pixelsPerSecond<60?2:1;for(let t=0;t<=total()+step;t+=step){const tick=crewEl('span',clock(t),'timeline-tick');tick.style.left=t*pixelsPerSecond+'px';ruler.append(tick)}}
 function timelineGeometry(){const surface=$('cut-clips').querySelector('.timeline-surface');if(!surface)return;surface.style.width=(Math.max(total()*pixelsPerSecond+48,$('cut-clips').clientWidth))+'px';surface.querySelectorAll('.edit-tile').forEach((el,i)=>{const c=cut.clips[i];el.style.left=(24+offset(i)*pixelsPerSecond)+'px';el.style.width=Math.max(2,(c.end-c.start)*pixelsPerSecond)+'px';el.querySelector('small').textContent=`${i+1} · ${friendlyShot(media(c)?.shot_id||'Clip')} · ${(c.end-c.start).toFixed(2)}s`});surface.querySelectorAll('.edit-add').forEach((el,i)=>el.style.left=(24+offset(i)*pixelsPerSecond)+'px');
  // CSS box only, never the canvas bitmap: repainting peaks on every drag
  // frame (this runs on every pointermove while trimming) would make
  // trim-drag janky. The bitmap is only (re)drawn when renderTiles()
  // rebuilds the clip list from scratch, i.e. once the drag finishes.
  surface.querySelectorAll('.timeline-wave').forEach((el,i)=>{const c=cut.clips[i];el.style.left=(24+offset(i)*pixelsPerSecond)+'px';el.style.width=Math.max(2,(c.end-c.start)*pixelsPerSecond)+'px'});
  drawRuler(surface.querySelector('.timeline-ruler'));refreshClock()}
 function drawWave(canvas,peaks){const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);if(!peaks||!peaks.length)return;ctx.fillStyle='#a5abb570';const barW=canvas.width/peaks.length,mid=canvas.height/2;for(let i=0;i<peaks.length;i++){const h=Math.max(1,peaks[i]*canvas.height);ctx.fillRect(i*barW,mid-h/2,Math.max(1,barW-1),h)}}
 function sliceWave(peaks,c,m){if(!peaks.length||!m.duration_s)return peaks;const startIdx=Math.floor(c.start/m.duration_s*peaks.length),endIdx=Math.max(startIdx+1,Math.ceil(c.end/m.duration_s*peaks.length));return peaks.slice(startIdx,endIdx)}
 let waveformCache={};
 function loadWave(canvas,c,m){
  if(!m||m.has_audio===false){drawWave(canvas,[]);return}
  if(m.id in waveformCache){drawWave(canvas,sliceWave(waveformCache[m.id],c,m));return}
  api('/api/projects/'+project.id+'/film-media/'+m.id+'/waveform').then(res=>{
   waveformCache[m.id]=res.peaks;
   if(!canvas.isConnected)return; // renderTiles() already rebuilt the clip list; this canvas is gone
   drawWave(canvas,sliceWave(res.peaks,c,m));
  }).catch(()=>{});
 }
 function renderTiles(){
  if(trimActive)return;closeClipMenu();
  if(!userZoomed&&cut.clips.length){pixelsPerSecond=fitPixelsPerSecond();zoom.value=pixelsPerSecond}
  const list=$('cut-clips');list.replaceChildren();
  const surface=crewEl('div',undefined,'timeline-surface'),ruler=crewEl('div',undefined,'timeline-ruler'),track=crewEl('div',undefined,'timeline-track'),waveLane=crewEl('div',undefined,'timeline-wave-lane');list.append(surface);surface.append(ruler,track,waveLane);
  function pointerTime(e){return (e.clientX-list.getBoundingClientRect().left+list.scrollLeft-24)/pixelsPerSecond}
  function scrub(e){if(e.button!==0)return;e.preventDefault();const target=e.currentTarget;target.setPointerCapture(e.pointerId);timelineSeek(pointerTime(e));target.onpointermove=move=>timelineSeek(pointerTime(move));target.onpointerup=target.onpointercancel=()=>{target.onpointermove=null};}
  ruler.onpointerdown=scrub;
  for(let i=0;i<=cut.clips.length;i++){
   const add=button('+',()=>showAdd(i),surface);add.className='edit-add';add.setAttribute('aria-label','Add clip at position '+(i+1));if(i===cut.clips.length)break;
   const c=cut.clips[i],m=media(c),tile=crewEl('div',undefined,'edit-tile');tile.setAttribute('role','button');tile.tabIndex=0;tile.setAttribute('aria-label','Select clip '+(i+1));tile.setAttribute('aria-pressed',String(i===selected));surface.append(tile);
   const selectClip=()=>{stop();loadClip(i);renderTiles();renderInspector()};tile.onclick=e=>{if(!e.target.closest('button'))selectClip()};tile.oncontextmenu=e=>{e.preventDefault();openClipMenu(i,e.clientX,e.clientY,tile)};tile.onkeydown=e=>{if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();const r=tile.getBoundingClientRect();openClipMenu(i,r.left+20,r.top,tile);return}if(e.target===tile&&['Enter',' '].includes(e.key)){e.preventDefault();selectClip()}};
   // Pointer-based, not native HTML5 draggable=true: unifies mouse, touch
   // and pen (native drag-and-drop never fires from a touch gesture at
   // all, on any browser) and matches the same setPointerCapture pattern
   // already used for scrubbing and trimming below.
   tile.onpointerdown=e=>{
    if(trimActive||e.button!==0||e.target.closest('button'))return;
    const startX=e.clientX,startY=e.clientY,originIndex=i;
    let moved=false,dropIndex=originIndex;
    tile.setPointerCapture(e.pointerId);
    tile.onpointermove=move=>{
     const dx=move.clientX-startX;
     if(!moved){
      if(Math.abs(dx)<4&&Math.abs(move.clientY-startY)<12)return;
      moved=true;tile.classList.add('dragging');
     }
     tile.style.transform=`translateX(${dx}px)`;
     const tiles=[...surface.querySelectorAll('.edit-tile')];
     dropIndex=tiles.length-1;
     for(let k=0;k<tiles.length;k++){
      if(k===originIndex)continue;
      const r=tiles[k].getBoundingClientRect();
      if(move.clientX<r.left+r.width/2){dropIndex=k>originIndex?k-1:k;break}
     }
     tiles.forEach((t,k)=>t.classList.toggle('timeline-drop',k===dropIndex&&k!==originIndex));
    };
    const finish=()=>{
     tile.onpointermove=null;
     if(moved&&dropIndex!==originIndex){
      remember();const [v]=cut.clips.splice(originIndex,1);cut.clips.splice(dropIndex,0,v);selected=dropIndex;changed();renderCut();
     }else if(moved){
      renderTiles(); // snap back to its slot; also clears the drag styling and suppresses the phantom click
     }
    };
    tile.onpointerup=finish;tile.onpointercancel=finish;
   };
   if(m?.video_url){const thumb=crewEl('video');thumb.src=m.video_url+'#t='+c.start;thumb.preload='metadata';thumb.muted=true;tile.append(thumb)}tile.append(crewEl('small'));const more=button('⋯',e=>{e.stopPropagation();const r=more.getBoundingClientRect();openClipMenu(i,r.left,r.bottom+5,more)},tile);more.className='clip-options';more.setAttribute('aria-label',`Clip ${i+1} options`);more.setAttribute('aria-haspopup','menu');more.setAttribute('aria-expanded','false');
   const wave=crewEl('canvas',undefined,'timeline-wave');wave.width=300;wave.height=34;wave.style.left=(24+offset(i)*pixelsPerSecond)+'px';wave.style.width=Math.max(2,(c.end-c.start)*pixelsPerSecond)+'px';waveLane.append(wave);loadWave(wave,c,m);
   for(const edge of ['start','end']){
    const handle=crewEl('button',undefined,'timeline-handle '+edge);handle.setAttribute('aria-label',`Clip ${i+1} trim ${edge}`);handle.title=`Drag to trim ${edge}. Arrow keys adjust 0.05 seconds.`;tile.append(handle);handle.onclick=e=>e.stopPropagation();
    function adjust(value){if(snapEnabled){const rounded=Math.round(value);if(Math.abs(rounded-value)*pixelsPerSecond<=SNAP_PX)value=rounded}c[edge]=edge==='start'?Math.max(0,Math.min(value,c.end-.05)):Math.min(m?.duration_s||c.end,Math.max(value,c.start+.05));changed();timelineGeometry();player.currentTime=edge==='start'?c.start:Math.max(c.start,c.end-.03)}
    handle.onpointerdown=e=>{if(e.button!==0)return;e.preventDefault();e.stopPropagation();stop();selected=i;loadClip(i);remember();trimActive=true;handle.setPointerCapture(e.pointerId);const x=e.clientX,initial=c[edge],scroll=list.scrollLeft;handle.onpointermove=move=>adjust(initial+(move.clientX-x+list.scrollLeft-scroll)/pixelsPerSecond);const finish=()=>{handle.onpointermove=null;trimActive=false;renderTiles();renderInspector()};handle.onpointerup=finish;handle.onpointercancel=finish};
    handle.onkeydown=e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();e.stopPropagation();stop();selected=i;remember();adjust(c[edge]+(e.key==='ArrowRight'?.05:-.05));renderInspector()};
   }
  }
  const head=crewEl('button');head.id='timeline-playhead';head.setAttribute('aria-label','Drag timeline playhead');head.onpointerdown=scrub;head.onkeydown=e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();timelineSeek(Number(seek.value)+(e.key==='ArrowRight'?.1:-.1))}};surface.append(head);timelineGeometry();
 }
 const clipMenu=crewEl('div');clipMenu.id='clip-menu';clipMenu.hidden=true;clipMenu.setAttribute('role','menu');document.body.append(clipMenu);
 let menuTrigger=null;
 function closeClipMenu(restore=false){if(clipMenu.hidden)return;clipMenu.hidden=true;menuTrigger?.setAttribute('aria-expanded','false');if(restore&&menuTrigger?.isConnected)menuTrigger.focus();}
 document.addEventListener('pointerdown',e=>{if(!clipMenu.contains(e.target))closeClipMenu()});
 document.addEventListener('scroll',e=>{if(!clipMenu.contains(e.target))closeClipMenu()},true);window.addEventListener('resize',()=>closeClipMenu());
 clipMenu.onkeydown=e=>{const items=[...clipMenu.querySelectorAll('button:not(:disabled)')],i=items.indexOf(document.activeElement);if(e.key==='Escape'){e.preventDefault();closeClipMenu(true)}else if(e.key==='Tab'){closeClipMenu(true)}else if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)){e.preventDefault();items[e.key==='Home'?0:e.key==='End'?items.length-1:(i+(e.key==='ArrowDown'?1:-1)+items.length)%items.length]?.focus()}};
 function splitAtPlayhead(index){
  const c=cut.clips[index];if(!c)return;
  const t=player.currentTime;
  if(t<=c.start+.05||t>=c.end-.05)return notify('Move the playhead inside this clip to split it');
  remember();cut.clips.splice(index,1,{...c,id:crypto.randomUUID(),end:t},{...c,id:crypto.randomUUID(),start:t});changed();renderCut();
 }
 function openClipMenu(index,x,y,trigger){
  closeClipMenu();stop();if(selected!==index)loadClip(index);selected=index;
  document.querySelectorAll('.edit-tile').forEach((el,n)=>el.setAttribute('aria-pressed',String(n===index)));
  const c=cut.clips[index],m=media(c);if(!c)return;
  menuTrigger=trigger;trigger.setAttribute('aria-expanded','true');clipMenu.replaceChildren();clipMenu.setAttribute('aria-label',`Clip ${index+1} actions`);
  clipMenu.append(crewEl('div',friendlyShot(m?.shot_id||'Clip').toUpperCase(),'clip-menu-title'));
  const action=(label,fn,disabled=false,hint='')=>{const b=button(label,()=>{closeClipMenu(true);if(cut.clips[index]!==c)return;fn()},clipMenu);b.setAttribute('role','menuitem');b.disabled=disabled;if(hint)b.append(crewEl('span',hint,'menu-hint'));return b};
  const divider=()=>{const hr=crewEl('hr');hr.setAttribute('role','separator');clipMenu.append(hr)};
  action('Trim…',()=>showTrim(index));
  action('Split at playhead',()=>splitAtPlayhead(index),false,'S');
  action(c.mute?'Unmute':'Mute',()=>{remember();c.mute=!c.mute;player.muted=c.mute;changed()});divider();
  action('Extend before…',()=>extendClip(index,'before'));action('Extend after…',()=>extendClip(index,'after'));
  action('Expand canvas…',()=>showEnhance(m,c,'expand'));action('Upscale · FLUX…',()=>showEnhance(m,c,'upscale'));
  action('Regenerate take…',()=>showRegenerate(index));divider();
  action('Remove from edit',()=>{remember();cut.clips.splice(index,1);changed();renderCut()}).className='clip-menu-remove';
  clipMenu.hidden=false;clipMenu.style.left=Math.max(8,Math.min(x,innerWidth-clipMenu.offsetWidth-8))+'px';clipMenu.style.top=Math.max(8,Math.min(y,innerHeight-clipMenu.offsetHeight-8))+'px';clipMenu.querySelector('button').focus({preventScroll:true});
 }
 function showTrim(index){
  const c=cut.clips[index],m=media(c),d=modal('Trim clip');d.classList.add('trim-dialog');
  d.append(crewEl('p',`Clip ${index+1} · ${friendlyShot(m?.shot_id||'Clip')} · seconds`));
  let remembered=false;const fields={};
  for(const [key,label] of [['start','In'],['end','Out']]){const wrap=crewEl('label',label,'trim-control'),range=crewEl('input'),number=crewEl('input');range.type='range';number.type='number';fields[key]=[range,number];for(const input of [range,number]){input.min=0;input.max=m?.duration_s||c.end;input.step=.05;input.value=c[key].toFixed(2);input.setAttribute('aria-label',`Trim ${label.toLowerCase()}`)}
   const update=input=>{if(cut.clips[index]!==c||input.value==='')return;const v=Number(input.value);if(!Number.isFinite(v))return;if(!remembered){remember();remembered=true}c[key]=key==='start'?Math.max(0,Math.min(v,c.end-.05)):Math.min(m?.duration_s||c.end,Math.max(v,c.start+.05));for(const el of fields[key])el.value=c[key].toFixed(2);stop();player.currentTime=key==='start'?c.start:Math.max(c.start,c.end-.04);changed();renderTiles();refreshClock()};range.oninput=()=>update(range);number.oninput=()=>{if(number.value!==''&&number.validity.valid)update(number)};number.onchange=()=>update(number);wrap.append(range,number);d.append(wrap)
  }
  button('Done',()=>dialog.close(),d);
 }
 function renderChips(container,chips){container.replaceChildren();if(!chips.length){container.append(crewEl('span','No cast or world sheets tagged','muted'));return}for(const chip of chips)container.append(crewEl('span',chip.name,'inspector-chip'))}
 function chipsFor(m,container){
  container.replaceChildren();
  if(!m)return;
  if(m.reference_mode==='character'){renderChips(container,(project.image_references||[]).filter(r=>(m.reference_ids||[]).includes(r.id)).map(r=>({name:r.name||'Reference'})));return}
  const shotId=m.shot_id;
  if(shotCastCache[shotId]){renderChips(container,shotCastCache[shotId]);return}
  container.append(crewEl('span','Loading…','muted'));
  const token=++castToken;
  api('/api/projects/'+project.id+'/shots/'+shotId+'/cast').then(res=>{
   shotCastCache[shotId]=res.chips;
   if(token!==castToken)return; // a newer selection has already moved on
   const current=cut.clips[selected],cm=current&&media(current);
   if(!cm||cm.shot_id!==shotId)return;
   renderChips(container,res.chips);
  }).catch(()=>{if(token===castToken)container.replaceChildren(crewEl('span','Could not load cast','muted'))});
 }
 function renderInspector(){
  undoButton.disabled=!undo.length;redoButton.disabled=!redo.length;
  const c=cut.clips[selected],m=c&&media(c);
  inspector.hidden=!c;
  if(!c)return;
  inspector.replaceChildren();
  inspector.append(crewEl('strong',friendlyShot(m?.shot_id||'Clip'),'inspector-title'));
  inspector.append(crewEl('small',(c.end-c.start).toFixed(2)+'s','muted'));
  inspector.append(crewEl('h4','Direction'));
  inspector.append(crewEl('p',m?.prompt||'No direction recorded for this clip.','inspector-direction'));
  const regen=crewEl('button',undefined,'inspector-regenerate');regen.type='button';regen.append(iconSvg(ICONS.refresh,14),crewEl('span','Edit direction & regenerate'));regen.onclick=()=>showRegenerate(selected);inspector.append(regen);
  inspector.append(crewEl('h4','Used in this take'));
  const chipRow=crewEl('div',undefined,'inspector-chips');inspector.append(chipRow);
  chipsFor(m,chipRow);
 }
 const undoButton=iconButton('undo',()=>{if(!undo.length)return;stop();redo.push(JSON.stringify(cut));if(redo.length>30)redo.shift();cut=JSON.parse(undo.pop());changed();renderCut()},'Undo',zoomRow);undoButton.disabled=true;
 const redoButton=iconButton('redo',()=>{if(!redo.length)return;stop();undo.push(JSON.stringify(cut));if(undo.length>30)undo.shift();cut=JSON.parse(redo.pop());changed();renderCut()},'Redo',zoomRow);redoButton.disabled=true;
 renderCut=function(){stop();selected=Math.min(selected,Math.max(0,cut.clips.length-1));$('cut-ratio').value=cut.aspect_ratio;fit.value=cut.fit||'contain';refreshResolutionOptions();applyCanvas();renderTiles();renderInspector();loadClip(selected);refreshClock();$('edit-breadcrumb-project').textContent=project.project.title||'Untitled film'};
 const oldLoad=loadFinalEdit;loadFinalEdit=async function(){undo=[];redo=[];selected=0;userZoomed=false;waveformCache={};shotCastCache={};await oldLoad()};
 async function insert(item,index=insertAt){remember();cut.clips.splice(Math.min(index,cut.clips.length),0,{id:crypto.randomUUID(),video_id:item.id,start:0,end:item.duration_s,mute:false});changed();dialog.close();renderCut();await saveCut()}
 function showAdd(index){insertAt=index;const d=modal('Add a clip');const row=crewEl('div',undefined,'edit-toolbar');d.append(row);button('Video library',()=>libraryPicker('video'),row);button('Generate from image',()=>libraryPicker('image'),row);button('Upload',()=>uploadPicker(),row);if(index>0){button('Extend previous clip',()=>extendClip(index-1,'after'),row)}if(index<cut.clips.length){button('Extend before next clip',()=>extendClip(index,'before'),row)}}
 function libraryPicker(kind){const d=modal(kind==='video'?'Video library':'Choose a starting image');const grid=crewEl('div',undefined,'edit-library');d.append(grid);const entries=kind==='video'?filmMedia.filter(i=>i.kind==='video'&&i.status==='complete'):project.versions.filter(i=>i.status==='ok'&&i.image_url);for(const entry of entries){const b=button('',()=>kind==='video'?insert(entry):prepareGeneration({version_id:entry.version_id},entry.shot_id),grid);const visual=crewEl(kind==='video'?'video':'img');visual.src=kind==='video'?entry.video_url:entry.image_url;if(kind==='video'){visual.preload='metadata';visual.muted=true}b.append(visual,crewEl('small',friendlyShot(entry.shot_id||'Clip')))}if(!entries.length)d.append(crewEl('p','No saved '+(kind==='video'?'videos':'images')+' yet. Upload one to get started.'));if(kind==='image')for(const ref of project.image_references||[]){const b=button('',()=>prepareGeneration({reference_id:ref.id}),grid);const img=crewEl('img');img.src='/api/projects/'+project.id+'/references/'+ref.id;b.append(img,crewEl('small',ref.name||'Reference'))}}
 async function continueClip(index,edge){const c=cut.clips[index];await prepareGeneration({video_id:c.video_id,time_s:edge==='end'?Math.max(c.start,c.end-1/24):c.start},media(c)?.shot_id)}
 function uploadPicker(){const d=modal('Upload a video or starting image');const input=crewEl('input');input.type='file';input.accept='video/mp4,video/quicktime,image/png,image/jpeg,image/webp';d.append(input);input.onchange=async()=>{const file=input.files[0];if(!file)return;input.disabled=true;const id=project.id,shot=shots()[0]?.id;try{const isImage=file.type.startsWith('image/');const res=await fetch('/api/projects/'+id+(isImage?'/references':'/shots/'+shot+'/upload-video'),{method:'POST',headers:{'Content-Type':file.type},body:file});const result=await res.json();if(!res.ok)throw Error(result.detail||'Upload failed');if(isImage){await prepareGeneration({reference_id:result.id})}else{filmMedia.unshift(result);pendingInsert={id:result.id,index:insertAt,project:id};dialog.close();renderExports();startMediaPoll();notify('Preparing your uploaded clip…')}}catch(e){report(e)}finally{input.disabled=false}}}
 async function prepareGeneration(source,preferredShot){try{const id=project.id,shot=preferredShot||shots()[0]?.id;const frame=await api('/api/projects/'+id+'/editor-frame','POST',{shot_id:shot,...source});project=await api('/api/projects/'+id);dialog.close();await jumpToShot(shot,'video');$('video-frame').value=frame.frame_id;$('prompt').value='';$('prompt').placeholder='Describe what happens next. Keep one clear action.';videoDirty=true;showStartingFrame();estimateVideo();notify('Starting image ready. Describe the action and generate; then add the result to your edit.');pendingInsert={shot,index:insertAt,project:id}}catch(e){report(e)}}
 const oldAdd=addToCut;addToCut=async function(item){if(pendingInsert?.project===project.id&&pendingInsert.shot===item.shot_id){const at=pendingInsert.index;pendingInsert=null;await insert(item,at);await switchFilmSection('edit')}else await oldAdd(item)};
 async function showEnhance(item,clip,operation){enhanceId=crypto.randomUUID();const d=modal(operation==='expand'?'Expand the canvas':'Upscale with FLUX');d.append(crewEl('p',operation==='expand'?`Expand this ${(clip.end-clip.start).toFixed(1)}s selection to ${cut.aspect_ratio}. A new version will be saved for review.`:'FLUX Video Upscale enhances detail and increases width and height. Your original and its audio are retained.'));const settings=crewEl('div');d.append(settings);let prompt,factor,preserve,creativity;
 if(operation==='expand'){prompt=crewEl('textarea');prompt.rows=3;prompt.value='Extend the surrounding scene with matching lighting, perspective and motion.';prompt.setAttribute('aria-label','Expansion prompt');settings.append(prompt);const l=crewEl('label','Keep original picture in the centre ');preserve=crewEl('input');preserve.type='checkbox';preserve.checked=true;preserve.style.width='auto';l.prepend(preserve);settings.append(l,crewEl('p','New edges may need another pass. Review the joins before replacing your clip.'))}else{factor=crewEl('select');factor.setAttribute('aria-label','Upscale factor');for(const n of [1.5,2,2.5,3]){const o=crewEl('option',n+'× dimensions');o.value=n;factor.append(o)}factor.value='2';creativity=crewEl('select');creativity.setAttribute('aria-label','Upscale mode');for(const [value,label] of [[0,'Precise · preserve detail'],[1,'Creative · enhance detail']]){const o=crewEl('option',label);o.value=value;creativity.append(o)}settings.append(factor,creativity)}
 const status=crewEl('p','Checking connection…');d.append(status);const submit=button('Create new version',async()=>{submit.disabled=true;try{const result=await api('/api/projects/'+project.id+'/enhancements','POST',{request_id:enhanceId,video_id:item.id,operation,start:clip.start,end:clip.end,aspect_ratio:cut.aspect_ratio,factor:Number(factor?.value||2),creativity:Number(creativity?.value||0),prompt:prompt?.value||'',preserve_center:preserve?.checked??true});filmMedia.unshift(result);dialog.close();renderExports();startMediaPoll();notify('Processing started. Your current edit is unchanged.')}catch(e){status.textContent=e.message;submit.disabled=false}},d);submit.disabled=true;
 try{const c=await api('/api/projects/'+project.id+'/enhancement-options');const limit=operation==='expand'?c.expand_max_seconds:c.upscale_max_seconds;c.configured=operation==='upscale'?c.upscale_configured:c.configured;status.textContent=!c.configured?(operation==='upscale'?'Connect OpenRouter in Settings to enable this.':'Connect your fal API key in Settings to enable this.'):!c.storage_ready?'Connect media storage in Settings first.':clip.end-clip.start>limit?`Trim this selection to ${limit} seconds or less.`:'Paid processing through '+(operation==='upscale'?'OpenRouter':'fal')+'. Cost varies by output size and duration; estimate unavailable.';submit.disabled=!c.configured||!c.storage_ready||clip.end-clip.start>limit;if(!c.configured||!c.storage_ready)button('Open Settings',()=>{dialog.close();$('account').click()},d)}catch(e){status.textContent=e.message}}
 async function extendClip(index,direction){
  stop();const source={...cut.clips[index]},owner=project.id;
  const d=modal(direction==='before'?'Extend before · Prequel':'Extend after · Sequel'),ticket=dialogVersion;
  d.append(crewEl('p',direction==='before'?'Describe the action leading into this clip. The new clip must end at the selected clip’s first visible frame.':'Describe what happens next. The new clip starts at the selected clip’s last visible frame.'));
  const status=crewEl('p','Preparing the trimmed boundary…');d.append(status);
  try{
   const [boundary,available]=await Promise.all([api('/api/projects/'+owner+'/extension-boundary','POST',{video_id:source.video_id,start:source.start,end:source.end,direction}),api('/api/projects/'+owner+'/video-models')]);
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
 async function showRegenerate(index){
  stop();const c=cut.clips[index],m=media(c);if(!c||!m)return;
  const owner=project.id;
  // Fixed for the life of this dialog, not regenerated per body() call:
  // reusing the same id means retrying a submit that failed or timed out
  // (the server may have already accepted and started it) recovers the
  // original job via create_video's own idempotency check instead of
  // starting — and potentially billing — a second one.
  const requestId=crypto.randomUUID();
  const d=modal('Regenerate this take'),ticket=dialogVersion;
  d.append(crewEl('p','Creates a new take for review. Your current clip stays in the edit until you choose to replace it.'));
  const prompt=crewEl('textarea');prompt.rows=4;prompt.value=m.prompt||'';prompt.setAttribute('aria-label','Direction');d.append(prompt);
  const status=crewEl('p','Loading models…');d.append(status);
  const row=crewEl('div',undefined,'edit-toolbar');d.append(row);
  function field(label){const l=crewEl('label',label+' '),select=crewEl('select');select.setAttribute('aria-label',label);l.append(select);row.append(l);return select}
  const model=field('Model'),duration=field('Seconds'),quality=field('Resolution'),ratio=field('Ratio');
  const audioLabel=crewEl('label','Generate audio '),audio=crewEl('input');audio.type='checkbox';audio.style.width='auto';audioLabel.prepend(audio);d.append(audioLabel);
  const price=crewEl('p');d.append(price);
  function fill(select,values){select.replaceChildren();for(const value of values){const o=crewEl('option',String(value));o.value=value;select.append(o)}}
  const submit=button('Regenerate',async()=>{
   submit.disabled=true;
   try{const job=await api('/api/projects/'+owner+'/videos','POST',body());if(project.id!==owner)return;filmMedia.unshift(job);dialog.close();renderExports();startMediaPoll();notify('Regenerating. Review the new take below before replacing this clip.')}
   catch(e){price.textContent=e.message;submit.disabled=false}
  },d);submit.disabled=true;
  function body(){return {request_id:requestId,shot_id:m.shot_id,frame_id:m.frame_id||'',anchor_position:m.anchor_position||'first_frame',
   reference_mode:m.reference_mode||'shot',reference_ids:m.reference_ids||[],prompt:prompt.value.trim(),model:model.value,
   duration_s:Number(duration.value),aspect_ratio:ratio.value,resolution:quality.value,audio:audio.checked,
   // clip_id pins this to the exact timeline instance that was selected,
   // not just its content: two clips can share the same video_id/start/end
   // (the same trim added twice, or an exact split), and matching only on
   // those would let "Replace this clip" replace the wrong one.
   regenerate_of:{video_id:c.video_id,start:c.start,end:c.end,clip_id:c.id}}}
  let version=0;
  async function estimate(){const token=++version;submit.disabled=true;if(!model.value||!prompt.value.trim()){price.textContent='Describe the direction to see the estimate.';return}try{const result=await api('/api/projects/'+owner+'/video-estimate','POST',body());if(token!==version||project.id!==owner||ticket!==dialogVersion||!d.open)return;price.textContent=result.offline?'Offline preview · no charge':result.cost==null?'Paid generation · estimate unavailable':'Estimated cost: $'+Number(result.cost).toFixed(4);submit.disabled=false}catch(e){if(token===version&&ticket===dialogVersion)price.textContent=e.message}}
  try{
   const available=await api('/api/projects/'+owner+'/video-models');
   if(project.id!==owner||!d.open||ticket!==dialogVersion)return;
   const choices=available.models.filter(mod=>m.reference_mode!=='character'||mod.character_references);
   for(const mod of choices){const o=crewEl('option',mod.name||mod.id);o.value=mod.id;model.append(o)}
   function sync(){const mod=choices.find(x=>x.id===model.value);if(!mod)return;fill(duration,mod.durations?.length?mod.durations:Array.from({length:mod.duration_max},(_,i)=>i+1));fill(quality,mod.resolutions);fill(ratio,mod.ratios);if(mod.ratios.includes(cut.aspect_ratio))ratio.value=cut.aspect_ratio;audio.disabled=!mod.audio;audio.checked=false;estimate()}
   model.onchange=sync;for(const el of [duration,quality,ratio,audio])el.onchange=estimate;let timer;prompt.oninput=()=>{++version;submit.disabled=true;clearTimeout(timer);timer=setTimeout(estimate,350)};
   status.textContent=choices.length?'':'No connected model supports this clip\'s generation mode. Choose another provider in Settings.';
   if(choices.length)sync();
  }catch(e){status.textContent=e.message}
 }
 async function insertExtension(item){
  const e=item.extension,matches=cut.clips.map((c,index)=>({c,index})).filter(({c})=>c.video_id===e.video_id&&Math.abs(c.start-e.start)<.001&&Math.abs(c.end-e.end)<.001);
  if(matches.length!==1)return notify('The source clip has moved or changed, or appears more than once. Use + and select this extension from the library.');
  await insert(item,matches[0].index+(e.direction==='after'?1:0));
 }

 const exportDialog=crewEl('dialog');exportDialog.id='export-dialog';exportDialog.style.cssText='width:min(580px,90vw);max-height:85vh;overflow:auto;padding:24px;position:relative';document.body.append(exportDialog);
 exportDialog.append(crewEl('h2','Export your film'));iconButton('close',()=>exportDialog.close(),'Close',exportDialog).className='dialog-close';
 exportDialog.append(crewEl('p','Choose the export size. For AI detail enhancement, export first, then choose Upscale with FLUX on the saved film.'));
 exportDialog.append(resolution.parentElement);
 const exportAction=$('export-film').onclick;
 const createExport=button('Create export',async()=>{createExport.disabled=true;try{await exportAction();exportNotice.textContent=$('cut-status').textContent}catch(e){exportNotice.textContent=e.message}finally{createExport.disabled=false}},exportDialog);
 const exportNotice=crewEl('p');exportNotice.setAttribute('role','status');exportDialog.append(exportNotice,$('film-exports'));
 $('export-film').onclick=()=>{exportNotice.textContent='';renderExports();exportDialog.showModal()};
 const oldExports=renderExports;renderExports=function(){oldExports();if(exportDialog.open)exportNotice.textContent=$('cut-status').textContent;if(cutDirty)$('cut-status').textContent='Unsaved edit';jobs.replaceChildren();for(const item of filmMedia.filter(i=>i.backend==='fal-enhance'||i.backend==='openrouter-enhance'||i.id===pendingInsert?.id||i.regenerate_of)){const card=crewEl('div',undefined,'edit-job');card.append(crewEl('strong',item.model+' · '+item.status));if(item.error)card.append(crewEl('p',item.error));if(item.video_url){const v=crewEl('video');v.src=item.video_url;v.controls=true;card.append(v);if(item.extension)button('Insert '+item.extension.direction+' source clip',()=>insertExtension(item),card);else button('Add to edit',()=>insert(item,cut.clips.length),card);if(item.enhancement)button('Replace matching selection',async()=>{const spec=item.enhancement;const index=cut.clips.findIndex(c=>c.video_id===item.source_id&&Math.abs(c.start-spec.start)<.01&&Math.abs(c.end-spec.end)<.01);if(index<0)return notify('The original selection has changed. Add this version from the library instead.');remember();cut.clips[index]={video_id:item.id,start:0,end:item.duration_s,mute:cut.clips[index].mute};changed();renderCut();await saveCut()},card);if(item.regenerate_of)button('Replace this clip',async()=>{const spec=item.regenerate_of;const index=spec.clip_id?cut.clips.findIndex(c=>c.id===spec.clip_id):cut.clips.findIndex(c=>c.video_id===spec.video_id&&Math.abs(c.start-spec.start)<.01&&Math.abs(c.end-spec.end)<.01);const target=cut.clips[index];
   // Identity (clip_id) alone isn't enough: the clip could since have been
   // re-trimmed or had its own source swapped by an earlier replace, and
   // both keep its id. Confirm its content still matches what regeneration
   // actually started from before overwriting it - otherwise a trim or
   // swap made while the job was running would be silently discarded.
   const unchanged=target&&target.video_id===spec.video_id&&Math.abs(target.start-spec.start)<.01&&Math.abs(target.end-spec.end)<.01;
   if(index<0||!unchanged)return notify('The original clip has moved or changed. Add this take from the library instead.');remember();cut.clips[index]={id:target.id,video_id:item.id,start:0,end:item.duration_s,mute:target.mute};changed();renderCut();await saveCut()},card)}else if(item.status==='waiting')button('Resume',async()=>{await api('/api/projects/'+project.id+'/videos/'+item.id+'/resume','POST',{});startMediaPoll()},card);jobs.append(card)}
 if(pendingInsert?.id){const item=filmMedia.find(i=>i.id===pendingInsert.id);if(item?.status==='complete'){const at=pendingInsert.index;pendingInsert=null;insert(item,at).catch(report)}}
 for(const card of $('film-exports').children){const video=card.querySelector('video');if(!video)continue;const item=filmMedia.find(i=>i.video_url===video.getAttribute('src'));if(item)button('Upscale film · FLUX',()=>{exportDialog.close();showEnhance(item,{start:0,end:item.duration_s},'upscale')},card)}};
 const priorSection=showFilmSection;showFilmSection=function(){if(filmSection!=='edit'){stop();closeClipMenu()}priorSection()};
 document.addEventListener('keydown',e=>{
  if(e.key.toLowerCase()!=='s'||e.metaKey||e.ctrlKey||e.altKey)return;
  if(filmSection!=='edit'||dialog.open||exportDialog.open)return;
  if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)||e.target.isContentEditable)return;
  if(!cut.clips[selected])return;
  e.preventDefault();splitAtPlayhead(selected);
 });
})();
