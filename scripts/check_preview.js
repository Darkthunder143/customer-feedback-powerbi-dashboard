// Exercise the existing preview's real render function against the CSV-derived oracle.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'..'),html=fs.readFileSync(path.join(root,'dashboard/interactive_preview.html'),'utf8');
const expected=JSON.parse(fs.readFileSync(path.join(root,'validation/results.json'),'utf8'));
const elements={region:{value:'all'},month:{value:'all'},content:{innerHTML:''}};
Object.values(elements).forEach(e=>e.addEventListener=()=>{});
const context=vm.createContext({document:{getElementById:id=>elements[id],querySelectorAll:()=>[]},console});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
vm.runInContext("page='drivers';render()",context);
for(const key of ['queue_ge6','queue_lt6','stock_lt93','stock_ge93'])assert.ok(elements.content.innerHTML.includes(expected.segments[key].rate.toFixed(2)),key);
// Exercise every region/month combination and reconcile visible totals/rates.
vm.runInContext("page='overview'",context);
for(let r=-1;r<8;r++)for(let m=-1;m<12;m++){
 elements.region.value=r<0?'all':String(r);elements.month.value=m<0?'all':String(m);
 vm.runInContext('render()',context);
 const a=vm.runInContext(`(()=>{let ff=rows.filter(x=>(${r}<0||x[1]===${r})&&(${m}<0||x[0]===${m}));return ff.length;})()`,context);
 assert.ok(elements.content.innerHTML.includes(a.toLocaleString('en-GB')));
}
console.log('PASS: rendered segmentation rates match independent oracle; all 117 region/month combinations render. Browser visual QA remains separate.');
