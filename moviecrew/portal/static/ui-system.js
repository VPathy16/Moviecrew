/* Preserve existing dialog actions while sharing their close affordance. */
(() => {
 const closeIcon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg>';
 function decorate(){
  document.querySelectorAll('dialog button').forEach(button=>{
   if(button.classList.contains('mc-close')||button.classList.contains('editor-close'))return;
   if(!['Close','×','✕'].includes(button.textContent.trim()))return;
   button.classList.add('mc-close');button.setAttribute('aria-label','Close dialog');button.title='Close dialog';button.innerHTML=closeIcon;button.closest('dialog').append(button);
  });
 }
 decorate();let pending=false;
 new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;decorate()})}).observe(document.body,{childList:true,subtree:true});
})();
