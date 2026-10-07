// Event contract checks. These do not substitute for browser/layout/playback QA.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../product/review-003/index.html','utf8');
let saved={},download='',blob=null,scrolled=false;
const nodes={'#film':{currentTime:0,scrollIntoView(){scrolled=true}},'#notes':{value:''},'#notice':{textContent:''},'#save':{},'#export':{}};
const buttons=[{dataset:{time:'15.6'}}];
const ctx={document:{querySelector:s=>nodes[s],querySelectorAll:()=>buttons,createElement:()=>({click(){download=this.download}})},localStorage:{getItem:k=>saved[k],setItem:(k,v)=>saved[k]=v},URL:{createObjectURL:b=>(blob=b,'blob:test'),revokeObjectURL(){}},Blob,setTimeout:fn=>fn()};
vm.runInNewContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
buttons[0].onclick();assert.equal(nodes['#film'].currentTime,15.6);assert(scrolled);
nodes['#notes'].value='色层有关系，但节奏尚需观看';nodes['#save'].onclick();assert.equal(Object.values(saved)[0],nodes['#notes'].value);
nodes['#notes'].value='导出当前未保存内容';nodes['#export'].onclick();assert.equal(download,'art-review-notes.json');
blob.text().then(s=>{let d=JSON.parse(s);assert.equal(d.notes,'导出当前未保存内容');assert.equal(d.acceptance,'unclassified_notes');assert.equal(d.time,15.6);ctx.localStorage.setItem=()=>{throw Error('blocked')};nodes['#save'].onclick();assert(nodes['#notice'].textContent.includes('失败'));console.log('PASS: seek, local save, fresh export, unclassified feedback, storage failure')}).catch(e=>{console.error(e);process.exit(1)});
