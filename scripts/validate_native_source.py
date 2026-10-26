#!/usr/bin/env python3
"""Validate JSON against Microsoft schemas plus referential/layout checks; not a Desktop test."""
import json, urllib.request, urllib.parse, hashlib
from pathlib import Path
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
R=Path(__file__).resolve().parents[1];P=R/'dashboard/CustomerFeedback';cache=Path('/tmp/customer-feedback-schema-cache');cache.mkdir(exist_ok=True)
def fetch(uri):
 uri=uri.split('#')[0]
 # Microsoft's filter schema declares a dotted $id but is hosted with a hyphen.
 uri=uri.replace('/schema.embedded.json', '/schema-embedded.json')
 p=cache/(hashlib.sha256(uri.encode()).hexdigest()+'.json')
 if not p.exists():
  with urllib.request.urlopen(uri,timeout=40) as f:p.write_bytes(f.read())
 return json.loads(p.read_text())
files=[]
for p in P.rglob('*'):
 if p.suffix not in ['.json','.pbip','.pbir','.pbism']:continue
 j=json.loads(p.read_text())
 if '$schema' in j:
  schema=fetch(j['$schema'])
  registry=Registry(retrieve=lambda uri: Resource.from_contents(fetch(uri), default_specification=DRAFT7))
  jsonschema.Draft7Validator(schema,registry=registry).validate(j);files.append(str(p.relative_to(R)))
model=json.loads((P/'CustomerFeedback.SemanticModel/model.bim').read_text())['model'];tables={t['name']:t for t in model['tables']}
for rel in model['relationships']:
 for side in ['from','to']:assert rel[side+'Column'] in {c['name'] for c in tables[rel[side+'Table']]['columns']}
 assert rel['crossFilteringBehavior']=='oneDirection'
for p in P.rglob('visual.json'):
 v=json.loads(p.read_text());pos=v['position'];assert 0<=pos['x'] and 0<=pos['y'] and pos['x']+pos['width']<=1440 and pos['y']+pos['height']<=900
 def walk(o):
  if isinstance(o,dict):
   for kind in ['Column','Measure']:
    if kind in o:
     e=o[kind];t=e['Expression']['SourceRef'].get('Entity')
     if t:assert e['Property'] in {x['name'] for x in tables[t]['columns' if kind=='Column' else 'measures']},(p,e)
   for x in o.values():walk(x)
  elif isinstance(o,list):
   for x in o:walk(x)
 walk(v)
result={'status':'PASS - JSON schemas, field bindings, relationship references and canvas bounds only','schema_files':len(files),'visuals':len(list(P.rglob('visual.json'))),'measures':sum(len(t.get('measures',[])) for t in tables.values()),'runtime_status':'NOT TESTED in Power BI Desktop','files':files}
(R/'validation/native_source_checks.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='files'})
