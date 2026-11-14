// Execute actual viewer JavaScript in an isolated DOM test double. No model or
// device interface is provided. Any attempted external call fails the test.
'use strict';
const fs=require('node:fs'),vm=require('node:vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const raw=JSON.stringify(input.rows), elements={}; let displayCalls=0;
function element(id){return elements[id]??=( {value:0,textContent:'',style:{},events:{},addEventListener(name,fn){this.events[name]=fn;}} );}
element('model-data').textContent=raw;
function forbidden(){throw Error('Viewer attempted an external API');}
const context=vm.createContext({document:{getElementById:element},setInterval:()=>1,clearInterval:()=>{},
 fetch:forbidden,XMLHttpRequest:forbidden,WebSocket:forbidden,postMessage:forbidden,
 navigator:{serial:{requestPort:forbidden},usb:{requestDevice:forbidden}}});
vm.runInContext(input.script,context,{timeout:1000});
for(const index of [0,29,30,31,38,66,67]){
 element('tick').value=index; element('tick').events.input();
 if(element('state').textContent!==input.rows[index][1])throw Error('State not rendered');
 const expected=input.rows[index][3];
 if(expected===null ? element('left').textContent!=='INHIBITED' : !element('left').textContent.startsWith(String(expected)+' micro'))throw Error('Effort not rendered');
 displayCalls++;
}
element('play').events.click();element('pause').events.click();element('start').events.click();
// Attempting to edit displayed values cannot alter recorded model data or run
// the Python model: only private playback data exists in this isolated viewer.
element('state').textContent='ACTUATION_ACTIVE';element('left').textContent='1000000';
element('start').events.click();
if(element('state').textContent!=='SELF_TEST')throw Error('Display did not reset');
if(element('model-data').textContent!==raw)throw Error('Viewer mutated original recording');
process.stdout.write(JSON.stringify({status:'PASS',display_checks:displayCalls,external_calls:0,core_callbacks:0}));
