#!/usr/bin/env python3
"""Create an analytical briefing, explicitly not a Power BI export."""
from pathlib import Path
import json,io
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1];V=json.loads((R/'validation/results.json').read_text());B=V['baseline'];OUT=R/'insights';TMP=Path('/tmp/customer-feedback-pdf');TMP.mkdir(exist_ok=True)
navy='#152D43';teal='#147D78';muted='#64748B';gold='#B77C24';bg='#F4F7FA'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':navy,'text.color':navy,'xtick.color':muted,'ytick.color':muted})
D='Portfolio Demonstration | Synthetic Data | Not Actual Greggs Customer Information'
f=pd.read_csv(R/'data/feedback.csv');o=pd.read_csv(R/'data/operations.csv');s=pd.read_csv(R/'data/shops.csv');a=pd.read_csv(R/'validation/shop_month_comparisons.csv')
def chart(fig,name):
 p=TMP/(name+'.png');fig.savefig(p,dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig);return p
fig,ax=plt.subplots(figsize=(6.8,2.8));f['month']=f.feedback_date.str[:7];g=f.groupby('month').size();c=f[f.feedback_type=='Complaint'].groupby('month').size();ax.plot(range(12),g.values,color=navy,marker='o',label='All feedback');ax.plot(range(12),c.values,color=teal,marker='o',label='Complaints');ax.set_xticks(range(12),['Oct','Nov','Dec','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep']);ax.set_ylim(0,260);ax.set_ylabel('Events');ax.legend(frameon=False,ncol=2,loc='upper left');ax.grid(axis='y',alpha=.15);trend=chart(fig,'trend')
fig,ax=plt.subplots(figsize=(6.8,2.8));cats=f[f.feedback_type=='Complaint'].category.value_counts().sort_values();ax.barh(cats.index,cats.values,color=[teal if x in ['Waiting time','Product availability'] else '#9AACBB' for x in cats.index]);ax.set_xlim(0,400)
for i,n in enumerate(cats.values):ax.text(n+5,i,str(n),va='center',fontsize=10)
ax.set_xlabel('Complaint events');category=chart(fig,'category')
fig,axes=plt.subplots(1,2,figsize=(12.5,3.2));
for ax,col,label in zip(axes,['avg_queue_minutes','stock_availability_pct'],['Average queue (minutes)','Stock availability (%)']):
 x=a[col]*(100 if col.startswith('stock') else 1);ax.scatter(x,a.rate,s=24,alpha=.6,color=teal,edgecolors='none');ax.set_xlabel(label);ax.set_ylabel('Complaints / 1,000 transactions');ax.set_ylim(0,float(a.rate.max())*1.08);ax.grid(alpha=.12)
scat=chart(fig,'scatter')
def para(c,txt,x,top,w,size=12,color=navy,leading=None):
 style=ParagraphStyle('body',fontName='DejaVu',fontSize=size,leading=leading or size*1.4,textColor=HexColor(color))
 p=Paragraph(txt,style);_,h=p.wrap(w,1000);p.drawOn(c,x,top-h);return h
W,H=1152,720
c=canvas.Canvas(str(OUT/'dashboard_analytical_briefing.pdf'),pagesize=(W,H));c.setTitle('Customer Feedback | Synthetic Analytical Briefing');c.setAuthor('Sanket Patel')
def base(num,title,sub):
 c.setFillColor(HexColor(bg));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor(teal));c.rect(32,H-57,6,26,fill=1,stroke=0)
 para(c,title,50,H-29,1050,25);para(c,sub,50,H-71,1050,11,muted)
 c.setStrokeColor(HexColor('#DCE4EB'));c.line(32,43,W-32,43)
 para(c,D,32,31,1050,9,muted);para(c,str(num),W-52,31,20,9,muted)
def kpi(x,label,value):
 c.setFillColor(HexColor('#FFFFFF'));c.roundRect(x,503,260,90,9,fill=1,stroke=0);para(c,label,x+17,574,225,11,muted);para(c,value,x+17,550,225,27,teal)
base(1,'Customer feedback | where to focus','Sanket Patel  /  Oct 2025 - Sep 2026  /  Analytical briefing - not a Power BI export')
for i,(label,value) in enumerate([('Feedback events','2,438'),('Average CSAT / 5','2.85'),('Negative feedback share','43.7%'),('Complaints / 1,000 transactions','0.270')]):kpi(32+i*276,label,value)
para(c,'Feedback volume over time',32,478,520,16);para(c,'Waiting and availability lead complaints',592,478,530,16)
c.drawImage(str(trend),32,235,535,220,mask='auto');c.drawImage(str(category),592,235,528,220,mask='auto')
para(c,'598 complaints (56.1%) concern waiting time or product availability.',32,200,1080,20,teal)
para(c,'24 fictional shops | 1,066 complaints | 3,941,570 transactions. Normalised rates use total selected-period transactions, not an average of shop rates. Feedback CSAT describes respondents, not all customers.',32,154,1070,13)
para(c,'Prepared native project source is included. Desktop refresh, DAX execution and interaction testing remain pending.',32,84,1070,11,muted);c.showPage()
base(2,'Operational signals | investigate, then test','288 shop-month observations  /  Correlation does not prove causation  /  Not a Power BI export')
c.drawImage(str(scat),32,294,1088,278,mask='auto')
para(c,'Queue >=6 min',40,267,490,18,teal);para(c,'0.322 vs 0.234 complaints / 1,000',40,236,490,19)
para(c,'529 / 1,642,607 transactions versus 537 / 2,298,963.<br/>116 higher-queue shop-months; 172 lower-queue shop-months.<br/>Descriptive Pearson r = 0.310 across shop-month rates.',40,201,495,12)
para(c,'Availability <93%',596,267,490,18,teal);para(c,'0.309 vs 0.236 complaints / 1,000',596,236,490,19)
para(c,'581 / 1,883,034 transactions versus 485 / 2,058,536.<br/>135 lower-stock shop-months; 153 higher-stock shop-months.<br/>Descriptive Pearson r = -0.275 across shop-month rates.',596,201,495,12)
para(c,'Interpretation limit: the generator deliberately creates these associations and fixes small feedback samples independently of transaction volume. Thresholds are illustrative. Repeated shop observations, reporting bias and unmeasured factors prevent causal interpretation.',40,119,1060,12,gold);c.showPage()
base(3,'Management priorities | measurable pilots','Full-period synthetic evidence  /  Three action priorities  /  Not a Power BI export')
items=[('01','Waiting friction','342 complaints | 32.1% of complaints','Investigate peak demand, task allocation and order mix. Pilot queue monitoring with matched comparison shops.','Waiting complaints / 1K and weighted queue minutes. Guardrail: order accuracy and labour hours.'),('02','Availability gaps','256 complaints | 24.0% of complaints','Investigate SKU/daypart shortages and forecast misses. Trial exception-led replenishment reviews.','Availability complaints / 1K and stock availability. Guardrail: waste and markdown cost.'),('03','Complaint follow-up','239 open | 77.6% closed | 55.5h closed-case mean','Investigate ownership, complexity and closure quality. Use weekly triage with named owners. No overdue claim.','Open count, closure share and closed-case hours. Add case ageing and reopen data before SLA assessment.')]
for i,(num,title,evidence,action,kpis) in enumerate(items):
 x=32+i*368;c.setFillColor(HexColor('#FFFFFF'));c.roundRect(x,213,352,365,10,fill=1,stroke=0)
 para(c,num,x+20,557,300,14,teal);para(c,title,x+20,525,310,20);para(c,evidence,x+20,483,310,12,teal)
 para(c,'<b>Investigate and act</b><br/>'+action,x+20,430,307,13)
 para(c,'<b>Measure success</b><br/>'+kpis,x+20,316,307,12)
para(c,'Proposed next step: four-week pilot with a baseline, matched shops and weekly reviews.',32,179,1080,18,teal)
para(c,'Agree definitions before setting targets. Do not promise an uplift from this artificial dataset. Open-case duration and snapshot timing are unavailable, so closure metrics cannot establish SLA performance.',32,137,1080,13)
para(c,'Portfolio status: source model, report pages and analysis prepared; native Desktop acceptance remains required.',32,78,1080,11,muted);c.save()
# One-page executive summary.
c=canvas.Canvas(str(OUT/'executive_summary.pdf'),pagesize=(595.28,841.89));c.setTitle('Executive Summary | Synthetic Customer Feedback');c.setAuthor('Sanket Patel');
para(c,'CUSTOMER FEEDBACK',40,800,510,11,teal);para(c,'Executive insight brief',40,774,510,25);para(c,'Sanket Patel | Quantitative analysis and retail operations',40,733,510,11,muted)
para(c,'<b>24 shops | 2,438 feedback events | 1,066 complaints</b><br/>Oct 2025 - Sep 2026. Average feedback CSAT: 2.85/5. Negative share: 43.7%. Complaint rate: 0.270 per 1,000 of 3,941,570 transactions.',40,695,510,11)
y=610
for num,title,evidence,action,kpis in items:
 para(c,num+' / '+title,40,y,510,15,teal);h=para(c,'<b>'+evidence+'.</b> '+action+' <b>KPIs:</b> '+kpis,40,y-28,510,11);y-=h+56
para(c,'<b>Decision:</b> Establish a baseline, agree definitions and run a proposed four-week pilot with matched shops and weekly reviews. No quantified improvement is promised.',40,y,510,11);y-=70
para(c,'<b>Limitations:</b> Synthetic, designed associations; correlation does not prove causation. Small fixed feedback samples are independent of transaction volume. Native PBIP source is prepared; Desktop refresh, DAX execution and interactions remain untested.',40,y,510,10,muted)
para(c,D,40,51,515,8,muted);c.save();print('Created analytical briefing (3 pages) and executive summary (1 page).')
