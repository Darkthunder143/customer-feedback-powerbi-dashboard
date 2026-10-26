#!/usr/bin/env python3
"""Refresh the existing HTML preview from original CSVs; retain shop keys for segmentation."""
from pathlib import Path
import csv,json,re
R=Path(__file__).resolve().parents[1]
def read(n):
 with (R/'data'/f'{n}.csv').open() as h:return list(csv.DictReader(h))
s,f,o=read('shops'),read('feedback'),read('operations');regions=list(dict.fromkeys(x['region'] for x in s));months=sorted({x['month_start'][:7] for x in o});region={x['shop_id']:regions.index(x['region']) for x in s}
rows=[[months.index(x['feedback_date'][:7]),region[x['shop_id']],['Complaint','Compliment','Suggestion'].index(x['feedback_type']),x['category'],int(x['csat_score']),int(x['resolution_status']=='Closed'),x['shop_id']] for x in f]
ops=[[months.index(x['month_start'][:7]),region[x['shop_id']],int(x['transactions']),float(x['avg_queue_minutes']),float(x['stock_availability_pct']),x['shop_id']] for x in o]
p=R/'dashboard/interactive_preview.html';text=p.read_text();line='const months='+json.dumps(months)+',regions='+json.dumps(regions)+',rows='+json.dumps(rows)+',ops='+json.dumps(ops)+';'
text=re.sub(r'^const months=.*$',lambda _:line,text,flags=re.M)
text=text.replace("long.map(x=>x[0]+'_'+x[1])","long.map(x=>x[0]+'_'+x[5])").replace("slowSet.has(x[0]+'_'+x[1])","slowSet.has(x[0]+'_'+x[6])")
text=text.replace("availLow.map(x=>x[0]+'_'+x[1])","availLow.map(x=>x[0]+'_'+x[5])").replace("lowSet.has(x[0]+'_'+x[1])","lowSet.has(x[0]+'_'+x[6])")
text=text.replace('function bar(names){','function bar(names,rate=false){').replace("'+n(count)+'","'+(rate?f(count):n(count))+'")
text=text.replace("['<6 min queue',rateShort]])","['<6 min queue',rateShort]],true)").replace("['≥93% available',highrate]])","['≥93% available',highrate]],true)")
text=text.replace('3. Publish a monthly complaint scorecard','3. Strengthen complaint follow-up').replace('Normalise complaint volume by store transactions and track category changes.','Triage open cases with named owners; add case ageing and closure quality before setting service targets.')
if 'Portfolio Demonstration | Synthetic Data | Not Actual Greggs Customer Information' not in text:
 text=text.replace('<main class="wrap">','<main class="wrap"><p class="notice">Portfolio Demonstration | Synthetic Data | Not Actual Greggs Customer Information</p>')
p.write_text(text)
