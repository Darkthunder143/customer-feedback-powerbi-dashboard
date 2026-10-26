#!/usr/bin/env python3
"""Generate editable PBIP/PBIR/TMSL source. Desktop acceptance testing is still required."""
from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[1];P=R/'dashboard'/'CustomerFeedback';REPORT=P/'CustomerFeedback.Report';MODEL=P/'CustomerFeedback.SemanticModel'
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def schema(part,ver='1.0.0'):return 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'+part+'/'+ver+'/schema.json'
measures=json.loads((R/'scripts/measures.json').read_text())
(R/'dax/measures.dax').write_text('// Paste measures separately if using manual fallback. DimMonth filters both facts.\n\n'+'\n\n'.join(x['name']+' = '+x['expression'] for x in measures)+'\n')
tables=[]
for name,file in [('DimShop','shops'),('FactFeedback','feedback'),('FactOperations','operations'),('DimMonth',None),('DimDate',None)]:
 if file:
  with (R/'data'/f'{file}.csv').open() as f:cols=next(csv.reader(f))
  if name=='FactFeedback':cols+=['month_start']
 else:cols=['MonthStart','YearMonth','Year'] if name=='DimMonth' else ['Date','MonthStart','YearMonth']
 columns=[]
 for c in cols:
  t='dateTime' if c in ['feedback_date','month_start','Date','MonthStart'] else 'int64' if c in ['csat_score','transactions','staffing_hours','Year'] else 'double' if c in ['avg_queue_minutes','stock_availability_pct','avg_basket_gbp','on_time_online_orders_pct','resolution_hours'] else 'string'
  col={'name':c,'dataType':t,'sourceColumn':c,'summarizeBy':'none'}
  if t=='dateTime':col['formatString']='yyyy-MM-dd'
  if c in ['shop_id','month_start','MonthStart'] and name!='DimMonth':col['isHidden']=True
  if c=='YearMonth' and name=='DimMonth':col['sortByColumn']='MonthStart'
  if name=='DimDate' and c=='Date':col['isKey']=True
  columns.append(col)
 table={'name':name,'columns':columns,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':(R/'powerquery'/f'{name}.m').read_text().splitlines()}}]}
 if name=='FactFeedback':table['measures']=measures
 if name=='DimDate':table['dataCategory']='Time'
 tables.append(table)
rels=[]
for fact,col,dim,dc in [('FactFeedback','shop_id','DimShop','shop_id'),('FactOperations','shop_id','DimShop','shop_id'),('FactFeedback','month_start','DimMonth','MonthStart'),('FactOperations','month_start','DimMonth','MonthStart'),('FactFeedback','feedback_date','DimDate','Date')]:
 rels.append({'name':fact+'_'+dim,'fromTable':fact,'fromColumn':col,'toTable':dim,'toColumn':dc,'crossFilteringBehavior':'oneDirection','fromCardinality':'many','toCardinality':'one','isActive':True})
write(MODEL/'model.bim',{'name':'CustomerFeedback','compatibilityLevel':1600,'model':{'culture':'en-GB','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'en-GB','dataAccessOptions':{'legacyRedirects':True,'returnErrorValuesAsNull':True},'expressions':[{'name':'pDataFolder','kind':'m','expression':(R/'powerquery/pDataFolder.m').read_text().strip()}],'tables':tables,'relationships':rels}})
write(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'1.0','settings':{'qnaEnabled':False}})
write(P/'CustomerFeedback.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'CustomerFeedback.Report'}}],'settings':{'enableAutoRecovery':True}})
write(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../CustomerFeedback.SemanticModel'}}})
write(REPORT/'definition/version.json',{'$schema':schema('versionMetadata'),'version':'4.0.0'})
write(REPORT/'definition/report.json',{'$schema':schema('report','3.1.0'),'themeCollection':{},'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized'}})
# theme.json is available for manual import; visual typography/colors are explicit below.
write(REPORT/'definition/pages/pages.json',{'$schema':schema('pagesMetadata'),'pageOrder':['Overview','Operations','Recommendations'],'activePageName':'Overview'})
def lit(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else str(v) if isinstance(v,(float,int)) else "'"+v.replace("'","''")+"'"}}}
def field(table,col,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':col}}
def proj(table,col,measure=False):return {'field':field(table,col,measure),'queryRef':table+'.'+col,'nativeQueryRef':col}
def M(name):return proj('FactFeedback',name,True)
def C(table,name):return proj(table,name)
current=None;count=0
DISCLAIMER='Portfolio Demonstration | Synthetic Data | Not Actual Greggs Customer Information'
def visual(name,kind,x,y,w,h,roles=None,objects=None,title=None):
 global count
 count+=1
 v={'visualType':kind,'drillFilterOtherVisuals':True}
 if roles:v['query']={'queryState':{role:{'projections':values} for role,values in roles.items()}}
 if objects:v['objects']=objects
 v['visualContainerObjects']={'background':[{'properties':{'color':{'solid':{'color':lit('#FFFFFF')}},'transparency':lit(0)}}],'border':[{'properties':{'show':lit(False)}}]}
 if title:v['visualContainerObjects']['title']=[{'properties':{'show':lit(True),'text':lit(title),'fontFamily':lit('Segoe UI'),'fontSize':lit(13),'fontColor':{'solid':{'color':lit('#152D43')}}}}]
 item={'$schema':schema('visualContainer','2.1.0'),'name':name,'position':{'x':x,'y':y,'z':count,'width':w,'height':h,'tabOrder':count},'visual':v}
 write(current/'visuals'/name/'visual.json',item);return item

def text(name,txt,x,y,w,h,size=14,color='#152D43'):
 return visual(name,'textbox',x,y,w,h,objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI','fontSize':str(size)+'pt','color':color}}]} for line in txt.split('\n')]}}]})
def card(name,measure,x,y,w=280):
 return visual(name,'card',x,y,w,105,{'Values':[M(measure)]},objects={'labels':[{'properties':{'fontSize':lit(28),'color':{'solid':{'color':lit('#147D78')}}}}]},title=measure)
def page(name,title):
 global current,count
 count=0;current=REPORT/'definition/pages'/name
 p={'$schema':schema('page','2.0.0'),'name':name,'displayName':title,'displayOption':'FitToPage','width':1440,'height':900,'objects':{'background':[{'properties':{'color':{'solid':{'color':lit('#F4F7FA')}},'transparency':lit(0)}}]}}
 if name=='Operations':
  p['pageBinding']={'name':'ShopDrillthrough','type':'Drillthrough','parameters':[{'name':'Shop','boundFilter':'ShopFilter','fieldExpr':field('DimShop','shop_label')}],'acceptsFilterContext':'Default'}
  p['filterConfig']={'filters':[{'name':'ShopFilter','field':field('DimShop','shop_label'),'type':'Categorical'}]}
 write(current/'page.json',p)
 text('Title',title,24,16,970,46,24)
 text('Subtitle','Fictional UK bakery | Oct 2025 - Sep 2026 | Whole-month comparisons',24,66,1000,35,11,'#64748B')
 text('Disclaimer',DISCLAIMER,24,858,1392,28,11,'#64748B')
 for name_,col,table,x,w in [('Month','YearMonth','DimMonth',1020,190),('Region','region','DimShop',1220,196)]:
  item=visual(name_,'slicer',x,16,w,95,{'Values':[C(table,col)]},objects={'data':[{'properties':{'mode':lit('Dropdown')}}]},title=name_)
  item['visual']['syncGroup']={'groupName':name_,'fieldChanges':True,'filterChanges':True};write(current/'visuals'/name_/'visual.json',item)
page('Overview','Executive Customer Feedback Overview')
for i,m in enumerate(['Total Feedback','Average CSAT','Negative Feedback %','Complaints per 1K Transactions']):card('KPI'+str(i),m,24+350*i,125,342)
visual('MonthlyTrend','lineChart',24,250,680,275,{'Category':[C('DimMonth','YearMonth')],'Y':[M('Total Feedback'),M('Total Complaints')]},title='Monthly feedback and complaints')
visual('Categories','barChart',724,250,692,275,{'Category':[C('FactFeedback','category')],'Y':[M('Total Complaints')]},title='Complaint themes | count')
visual('Regions','barChart',24,545,680,280,{'Category':[C('DimShop','region')],'Y':[M('Complaints per 1K Transactions')],'Tooltips':[M('Total Complaints'),M('Total Transactions')]},title='Regional complaints per 1,000 transactions')
visual('ShopTable','tableEx',724,545,692,280,{'Values':[C('DimShop','shop_label'),M('Total Complaints'),M('Complaints per 1K Transactions'),M('Average CSAT')]},title='Shop comparison | right-click shop to drill through')
page('Operations','Operational Root Cause Analysis')
text('Causality','Exploratory association only: correlation does not prove causation. Synthetic patterns are programmed.',24,115,1390,35,12,'#9A5C13')
visual('QueueScatter','scatterChart',24,160,680,280,{'Category':[C('DimShop','shop_label')],'X':[M('Average Queue Minutes')],'Y':[M('Complaints per 1K Transactions')],'Size':[M('Total Transactions')],'Tooltips':[M('Total Complaints'),M('Stock Availability %'),M('Months Selected')]},title='Queue minutes vs complaint rate | one dot per shop, selected period')
visual('StockScatter','scatterChart',724,160,692,280,{'Category':[C('DimShop','shop_label')],'X':[M('Stock Availability %')],'Y':[M('Complaints per 1K Transactions')],'Size':[M('Total Transactions')],'Tooltips':[M('Total Complaints'),M('Average Queue Minutes')]},title='Stock availability vs complaint rate | selected-period shop averages')
visual('Trend','lineChart',24,455,452,250,{'Category':[C('DimMonth','YearMonth')],'Y':[M('Complaints per 1K Transactions')],'Tooltips':[M('Complaints MoM %'),M('Total Transactions')]},title='Month-by-month complaint rate')
visual('RegionMonth','pivotTable',492,455,452,250,{'Rows':[C('DimShop','region')],'Columns':[C('DimMonth','YearMonth')],'Values':[M('Complaints per 1K Transactions')]},objects={'values':[{'properties':{'fontColor':{'solid':{'color':{'expr':field('FactFeedback','Rate Colour',True)}}}},'selector':{'metadata':'FactFeedback.Complaints per 1K Transactions'}}]},title='Region x month | amber >= 0.300 (illustrative)')
visual('Categories','barChart',960,455,456,250,{'Category':[C('FactFeedback','category')],'Y':[M('Total Complaints')]},title='Complaint breakdown')
visual('Detail','tableEx',24,720,1392,120,{'Values':[C('DimShop','shop_label'),M('Total Complaints'),M('Total Transactions'),M('Average Queue Minutes'),M('Stock Availability %'),M('Complaints MoM %')]},title='Shop detail | clear ShopFilter in Filters pane to return to all shops')
page('Recommendations','Management Recommendations')
for i,m in enumerate(['Total Complaints','Open Complaints','Complaint Resolution %','Average Resolved Complaint Hours']):card('KPI'+str(i),m,24+350*i,125,342)
text('Scope','Evidence below uses the full synthetic period; KPI cards follow the filters. Thresholds are illustrative, not service standards.',24,242,1392,38,11,'#64748B')
texts=[('01 | Reduce waiting friction','342 waiting-time complaints (32.1% of complaints).\nQueue >=6 min: 0.322 complaints/1K vs 0.234 below 6 min.\nHypothesis: peaks and task allocation may create queues.\nInvestigate: hour-of-day demand, staffing and order mix.\nAction: pilot peak-hour queue monitoring in matched shops.\nKPI: waiting complaints/1K; weighted queue minutes.\nGuardrail: order accuracy and labour hours.'),('02 | Investigate availability gaps','256 availability complaints (24.0% of complaints).\nStock <93%: 0.309 complaints/1K vs 0.236 at >=93%.\nHypothesis: replenishment timing may miss demand.\nInvestigate: SKU/daypart gaps, forecasts and waste.\nAction: trial exception-led replenishment reviews.\nKPI: availability complaints/1K; stock availability.\nGuardrail: waste and markdown cost.'),('03 | Strengthen complaint follow-up','239 complaints remain open; 77.6% are closed.\nClosed cases average 55.5 hours to resolution.\nHypothesis: case allocation or complexity may delay closure.\nInvestigate: age, severity, ownership and reopen history.\nAction: weekly triage with named owners and next steps.\nKPI: open-case count; closure share; closed-case hours.\nGuardrail: closure quality; add ageing before judging SLA.')]
for i,(title,body) in enumerate(texts):
 x=24+i*468;text('ActionTitle'+str(i),title,x,300,450,50,17,'#147D78');text('ActionBody'+str(i),body,x,360,450,315,13)
text('Pilot','Proposed 4-week pilot: agree definitions and baseline first; compare with matched shops, review weekly and check unintended effects.\nNo promised uplift: the generator builds queue/stock relationships into the data. Small samples and selection bias limit interpretation.',24,710,1392,105,14)
print('Generated',len(list(REPORT.rglob('visual.json'))),'native visual definitions and',len(measures),'measures. Desktop validation pending.')
