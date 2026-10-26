#!/usr/bin/env node
// Deterministic synthetic portfolio data generator. Node.js 18+; no external dependencies.
// All outputs are fictional. Do not use or mix with employer records.
function generateSyntheticData(){
 let seed=26102026;
 function rand(){seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;}
 const regions=[
  ["Scotland",["Edinburgh","Glasgow","Aberdeen"]],
  ["North East",["Newcastle","Sunderland","Durham"]],
  ["North West",["Manchester","Liverpool","Preston"]],
  ["Yorkshire",["Leeds","Sheffield","York"]],
  ["Midlands",["Birmingham","Nottingham","Leicester"]],
  ["London & South East",["London","Brighton","Reading"]],
  ["South West",["Bristol","Exeter","Plymouth"]],
  ["Wales",["Cardiff","Swansea","Newport"]]
 ];
 const shops=[]; let idx=0;
 for(const [region,cities] of regions) for(const city of cities){idx++;shops.push({shop_id:`S${String(idx).padStart(3,"0")}`,shop_label:`Example Shop ${String(idx).padStart(2,"0")}`,city,region,format:idx%4===0?"Travel hub":"High street"});}
 const months=Array.from({length:12},(_,i)=>new Date(Date.UTC(2025,9+i,1)).toISOString().slice(0,10));
 const operations=[],feedback=[];
 const channels=["In-shop","Website","App","Email","Telephone"];
 const products=["Sandwiches","Hot drinks","Savouries","Sweet bakery","Breakfast","Other"];
 const orderChannels=["In-shop","Click & Collect","Delivery"];
 const categories=["Waiting time","Product availability","Order accuracy","Staff service","Food quality","Cleanliness","Digital ordering"];
 let feedbackNum=0;
 for(const shop of shops) for(let mi=0;mi<months.length;mi++){
  const month=months[mi],date=new Date(`${month}T00:00:00Z`), monthDays=new Date(Date.UTC(date.getUTCFullYear(),date.getUTCMonth()+1,0)).getUTCDate();
  const queue=+(2.6+rand()*5.3+(mi===2||mi===11?0.7:0)).toFixed(2);
  const stock=+(0.875+rand()*0.118-Math.max(0,queue-6)*0.002).toFixed(4);
  const txn=Math.round(6500+rand()*13500+(mi===2?1400:0));
  operations.push({shop_id:shop.shop_id,month_start:month,transactions:txn,avg_queue_minutes:queue,stock_availability_pct:stock,avg_basket_gbp:+(3.3+rand()*2.6).toFixed(2),staffing_hours:Math.round(950+rand()*650),on_time_online_orders_pct:+(0.80+rand()*.19).toFixed(4)});
  const n=6+Math.floor(rand()*6);
  for(let j=0;j<n;j++){
   let pComplaint=Math.min(0.69,Math.max(.22,.19+(queue-2.6)*.06+Math.max(0,.97-stock)*2.4));
   let q=rand(),type=q<pComplaint?"Complaint":q<.80?"Compliment":"Suggestion";
   let category;
   if(type==="Complaint"){
    const weights=[1+(queue-3)*1.4,1+Math.max(0,.97-stock)*55,1.8,1.5,1.6,.8,.85];
    let total=weights.reduce((a,b)=>a+b,0),z=rand()*total;let at=weights.findIndex(w=>(z-=w)<=0);category=categories[Math.max(0,at)];
   } else if(type==="Compliment") category=["Staff service","Food quality","Order accuracy","Product availability"][Math.floor(rand()*4)];
   else category=categories[Math.floor(rand()*categories.length)];
   const sentiment=type==="Complaint"?"Negative":type==="Compliment"?"Positive":"Neutral";
   const csat=type==="Complaint"?(rand()<.60?1:2):type==="Compliment"?(rand()<.45?4:5):3;
   const severity=type!=="Complaint"?"Low":rand()<.20?"High":rand()<.62?"Medium":"Low";
   const closed=rand()<(type==="Complaint"?.79:.94);
   const resHours=closed?+(1+rand()*(type==="Complaint"?110:36)).toFixed(1):"";
   const day=1+Math.floor(rand()*monthDays);
   const dateStr=`${month.slice(0,7)}-${String(day).padStart(2,"0")}`;
   const templates={
    "Complaint":`Customer reported an issue related to ${category.toLowerCase()} during a routine bakery visit.`,
    "Compliment":`Customer praised the experience relating to ${category.toLowerCase()}.`,
    "Suggestion":`Customer suggested an improvement concerning ${category.toLowerCase()}.`
   };
   feedbackNum++;
   feedback.push({feedback_id:`F${String(feedbackNum).padStart(5,"0")}`,feedback_date:dateStr,shop_id:shop.shop_id,feedback_channel:channels[Math.floor(rand()*channels.length)],feedback_type:type,category,sentiment,csat_score:csat,severity,resolution_status:closed?"Closed":"Open",resolution_hours:resHours,product_category:products[Math.floor(rand()*products.length)],order_channel:orderChannels[Math.floor(rand()*orderChannels.length)],feedback_text:templates[type]});
  }
 }
 feedback.sort((a,b)=>a.feedback_date.localeCompare(b.feedback_date)||a.feedback_id.localeCompare(b.feedback_id));
 return {shops,operations,feedback,months};
}
const fs=require("node:fs");const path=require("node:path");
const base=path.resolve(__dirname,"..","data");fs.mkdirSync(base,{recursive:true});
const quote=v=>'"'+String(v??"").replace(/"/g,'""')+'"';
const csv=(rows,cols)=>[cols.join(","),...rows.map(r=>cols.map(c=>quote(r[c])).join(","))].join("\n")+"\n";
const sample=generateSyntheticData();
fs.writeFileSync(path.join(base,"shops.csv"),csv(sample.shops,["shop_id","shop_label","city","region","format"]));
fs.writeFileSync(path.join(base,"operations.csv"),csv(sample.operations,["shop_id","month_start","transactions","avg_queue_minutes","stock_availability_pct","avg_basket_gbp","staffing_hours","on_time_online_orders_pct"]));
fs.writeFileSync(path.join(base,"feedback.csv"),csv(sample.feedback,["feedback_id","feedback_date","shop_id","feedback_channel","feedback_type","category","sentiment","csat_score","severity","resolution_status","resolution_hours","product_category","order_channel","feedback_text"]));
console.log("Created",sample.shops.length,"shops,",sample.operations.length,"operational shop-months and",sample.feedback.length,"feedback rows.");
