#!/usr/bin/env node
// Lightweight CSV consistency checks, no dependencies.
const fs=require("node:fs");const path=require("node:path");
const root=path.join(__dirname,"..","data");
const load=name=>fs.readFileSync(path.join(root,name),"utf8").trim().split(/\r?\n/);
const feedback=load("feedback.csv"),ops=load("operations.csv"),shops=load("shops.csv");
const quoteField=s=>s.replace(/^"|"$/g,"").replace(/""/g,'"');
const split=s=>s.match(/("(?:[^"]|"")*"|[^,]*)(,|$)/g)?.map(x=>quoteField(x.slice(0,x.endsWith(",")?-1:undefined)))||[];
const fh=split(feedback[0]),oh=split(ops[0]),sh=split(shops[0]);
const at=(headers,row,col)=>split(row)[headers.indexOf(col)];
const ids=new Set(shops.slice(1).map(r=>at(sh,r,"shop_id")));
const opIds=new Set(ops.slice(1).map(r=>at(oh,r,"shop_id")+"|"+at(oh,r,"month_start").slice(0,7)));
if(ids.size!==24)throw new Error("Expected 24 shops");
if(ops.length-1!==288)throw new Error("Expected 288 operational observations");
let complaints=0;
for(const row of feedback.slice(1)){
 const sid=at(fh,row,"shop_id"),d=at(fh,row,"feedback_date");
 if(!ids.has(sid)||!opIds.has(sid+"|"+d.slice(0,7)))throw new Error("Unmatched feedback row: "+row);
 if(at(fh,row,"feedback_type")==="Complaint")complaints++;
 const score=Number(at(fh,row,"csat_score"));if(!Number.isInteger(score)||score<1||score>5)throw new Error("Invalid CSAT");
}
console.log("PASS",shops.length-1,"shops",ops.length-1,"shop-months",feedback.length-1,"feedback records",complaints,"complaints");
