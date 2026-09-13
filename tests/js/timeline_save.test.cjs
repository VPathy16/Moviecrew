const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('moviecrew/portal/static/studio.html','utf8');
const source=html.slice(html.indexOf('let cutSavePromise=null;'),html.indexOf("$('cut-ratio').onchange",html.indexOf('let cutSavePromise=null;')));
function fixture(){
 const calls=[],pending=[];
 const context={cut:{revision:0,clips:[],aspect_ratio:'16:9'},cutDirty:true,project:{id:'a'},crypto:require('node:crypto').webcrypto,$:()=>({value:'16:9'}),api:(url,method,body)=>{calls.push(JSON.parse(JSON.stringify(body)));return new Promise((resolve,reject)=>pending.push({resolve,reject}))}};
 vm.createContext(context);vm.runInContext(source,context);return {context,calls,pending};
}
test('edits during save survive and serialize into next revision',async()=>{
 const {context:c,calls,pending}=fixture();const save=c.saveCut();
 c.cut.clips.push({id:'new',video_id:'v',start:0,end:2});
 pending[0].resolve({revision:1});await new Promise(setImmediate);
 assert.equal(c.cut.clips.length,1);assert.equal(calls.length,2);assert.equal(calls[1].revision,1);
 pending[1].resolve({revision:2});await save;assert.equal(c.cut.revision,2);assert.equal(c.cutDirty,false);
});
test('conflict retains local edits and dirty state',async()=>{
 const {context:c,pending}=fixture();const save=c.saveCut();pending[0].reject(Error('conflict'));
 await assert.rejects(save,/conflict/);assert.equal(c.cut.revision,0);assert.equal(c.cutDirty,true);
});
test('save response cannot update a different project',async()=>{
 const {context:c,pending}=fixture();const save=c.saveCut();c.project={id:'b'};c.cut={revision:10,clips:[]};pending[0].resolve({revision:1});await save;assert.equal(c.cut.revision,10);
});
