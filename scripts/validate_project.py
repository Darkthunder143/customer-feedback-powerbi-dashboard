#!/usr/bin/env python3
"""Read-only source validation and independent KPI oracle. Python standard library."""
import csv, json, hashlib, math
from pathlib import Path
from datetime import date
from collections import Counter
R=Path(__file__).resolve().parents[1]; out=R/'validation';out.mkdir(exist_ok=True)
def load(n):
 with (R/'data'/f'{n}.csv').open(newline='') as f:return list(csv.DictReader(f))
s,o,f=map(load,['shops','operations','feedback']);checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
ids={x['shop_id'] for x in s};keys={(x['shop_id'],x['month_start']) for x in o}
check('Shop primary key unique and nonblank',len(ids)==len(s)==24 and '' not in ids)
check('Operations unique shop-month grain',len(keys)==len(o)==288)
check('Feedback primary key unique and nonblank',len({x['feedback_id'] for x in f})==len(f)==2438 and all(x['feedback_id'] for x in f))
months=sorted({x['month_start'] for x in o});check('Complete 24 x 12 shop-month grid',keys=={(sid,month) for sid in ids for month in months})
for x in o:
 check('Operations valid: '+x['shop_id']+' '+x['month_start'], x['shop_id'] in ids and date.fromisoformat(x['month_start']).day==1 and int(x['transactions'])>0 and float(x['avg_queue_minutes'])>=0 and float(x['staffing_hours'])>0 and float(x['avg_basket_gbp'])>0 and all(0<=float(x[k])<=1 for k in ['stock_availability_pct','on_time_online_orders_pct']))
for x in f:
 d=date.fromisoformat(x['feedback_date']);key=(x['shop_id'],d.replace(day=1).isoformat())
 assert key in keys,(x['feedback_id'],'orphan')
 assert 1<=int(x['csat_score'])<=5
 assert x['feedback_type'] in ['Complaint','Compliment','Suggestion']
 assert x['resolution_status'] in ['Open','Closed']
 assert (x['resolution_status']=='Open')==(x['resolution_hours']=='')
 assert not x['resolution_hours'] or float(x['resolution_hours'])>=0
 assert x['sentiment']=={'Complaint':'Negative','Compliment':'Positive','Suggestion':'Neutral'}[x['feedback_type']]
 assert all(x[k] for k in x if k!='resolution_hours')
checks+=['Feedback foreign keys and ISO dates','CSAT integer range 1-5','Required feedback values and enum domains','Resolution missingness and nonnegative hours','Sentiment mapping matches type']
def calc(ff,oo):
 c=[x for x in ff if x['feedback_type']=='Complaint'];t=sum(int(x['transactions']) for x in oo);closed=[x for x in c if x['resolution_status']=='Closed']
 return {'feedback':len(ff),'complaints':len(c),'transactions':t,'csat':sum(int(x['csat_score']) for x in ff)/len(ff) if ff else None,'negative_share':len(c)/len(ff) if ff else None,'rate':len(c)*1000/t if t else None,'open':len(c)-len(closed),'closed':len(closed),'resolution_share':len(closed)/len(c) if c else None,'resolved_hours':sum(float(x['resolution_hours']) for x in closed)/len(closed) if closed else None,'queue':sum(float(x['avg_queue_minutes'])*int(x['transactions']) for x in oo)/t if t else None,'stock':sum(float(x['stock_availability_pct'])*int(x['transactions']) for x in oo)/t if t else None}
a=calc(f,o);check('Known baseline totals',(a['complaints'],a['transactions'],a['open'])==(1066,3941570,239))
regions=sorted({x['region'] for x in s});rows=[]
for region in ['ALL']+regions:
 sid={x['shop_id'] for x in s if region=='ALL' or x['region']==region}
 for month in ['ALL']+months:
  ff=[x for x in f if x['shop_id'] in sid and (month=='ALL' or x['feedback_date'][:7]==month[:7])];oo=[x for x in o if x['shop_id'] in sid and (month=='ALL' or x['month_start']==month)]
  v=calc(ff,oo);rows.append({'region':region,'month':month,**v})
  check('Slice exposure '+region+' '+month,len(oo)==len(sid)*(12 if month=='ALL' else 1))
with (out/'expected_slices.csv').open('w',newline='') as h:
 w=csv.DictWriter(h,fieldnames=rows[0],lineterminator="\n");w.writeheader();w.writerows(rows)
c=Counter((x['shop_id'],x['feedback_date'][:7]+'-01') for x in f if x['feedback_type']=='Complaint')
shopmonths=[dict(x,complaints=c[(x['shop_id'],x['month_start'])],rate=1000*c[(x['shop_id'],x['month_start'])]/int(x['transactions'])) for x in o]
def segment(col,threshold,above):
 oo=[x for x in o if (float(x[col])>=threshold)==above];kk={(x['shop_id'],x['month_start']) for x in oo};ff=[x for x in f if (x['shop_id'],x['feedback_date'][:7]+'-01') in kk];return dict(shop_months=len(oo),**calc(ff,oo))
def corr(col):
 xs=[float(x[col]) for x in shopmonths];ys=[x['rate'] for x in shopmonths];xm=sum(xs)/len(xs);ym=sum(ys)/len(ys)
 return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/math.sqrt(sum((x-xm)**2 for x in xs)*sum((y-ym)**2 for y in ys))
segments={'queue_ge6':segment('avg_queue_minutes',6,True),'queue_lt6':segment('avg_queue_minutes',6,False),'stock_lt93':segment('stock_availability_pct',.93,False),'stock_ge93':segment('stock_availability_pct',.93,True)}
check('Segment numerator reconciliation',segments['queue_ge6']['complaints']+segments['queue_lt6']['complaints']==1066)
check('Segment denominator reconciliation',segments['stock_lt93']['transactions']+segments['stock_ge93']['transactions']==3941570)
check('Zero-denominator remains undefined',calc([],[])['rate'] is None)
# Feedback-side category filtering must never filter the transaction fact.
for cat in {x['category'] for x in f}:
 check('Category denominator '+cat,calc([x for x in f if x['category']==cat],o)['transactions']==3941570)
summary={'status':'PASS - independent Python data and arithmetic checks, NOT DAX/M engine execution','checks_passed':len(checks),'baseline':a,'segments':segments,'pearson_shop_month':{k:corr(k) for k in ['avg_queue_minutes','stock_availability_pct']},'categories':dict(Counter(x['category'] for x in f if x['feedback_type']=='Complaint')),'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'data').glob('*.csv'))},'pending':['Power Query refresh','DAX query execution','PBIP opening in Desktop','Slicer and drillthrough interactions','Conditional formatting rendering','PBIX save and reopen','Native screenshots and PDF export']}
(out/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
with (out/'shop_month_comparisons.csv').open('w',newline='') as h:
 w=csv.DictWriter(h,fieldnames=shopmonths[0],lineterminator="\n");w.writeheader();w.writerows(shopmonths)
print(json.dumps(summary,indent=2))
