"""Improve the simulation-pipeline slide while preserving the user's other slides."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'raw-before.json').read_text())['structuredContent']
PAGE='pi_simple_20261022_s04'
slide=next(s for s in raw['slides'] if s['objectId']==PAGE)
elements={e['objectId']:e for e in slide['pageElements']}
requests=[];counter=0
INK='183139';GRAY='62747A';TEAL='087F7B';PALE='E1EFEB';LINE='D8DFD9';ARM='93A5AA';WHITE='FFFFFF'

def add(t,**v):requests.append({t:v})
def rgb(c):return {k:int(c[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}
def oid(kind):
 global counter
 counter+=1
 return f'pi_pipeline_v2_{kind}_{counter:03d}'
def props(x,y,w,h):
 return {'pageObjectId':PAGE,'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},
         'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}
def move(o,x,y,w,h):
 e=elements[o]
 cv=lambda d:d['magnitude']/12700 if d['unit']=='EMU' else d['magnitude']
 add('updatePageElementTransform',objectId=o,applyMode='ABSOLUTE',transform={
  'scaleX':w/cv(e['size']['width']),'scaleY':h/cv(e['size']['height']),
  'translateX':x,'translateY':y,'unit':'PT'})
def text_style(o,size,color,bold,align):
 add('updateTextStyle',objectId=o,textRange={'type':'ALL'},style={
  'fontFamily':'Arial','fontSize':{'magnitude':size,'unit':'PT'},'bold':bold,
  'foregroundColor':{'opaqueColor':{'rgbColor':rgb(color)}}},fields='fontFamily,fontSize,bold,foregroundColor')
 add('updateParagraphStyle',objectId=o,textRange={'type':'ALL'},style={
  'alignment':align,'lineSpacing':105,'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':0,'unit':'PT'},
  'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},'indentFirstLine':{'magnitude':0,'unit':'PT'}},
  fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')
def text(t,x,y,w,h,size=12,color=INK,bold=False,align='START',existing=None):
 if existing:
  o=existing
  add('deleteText',objectId=o,textRange={'type':'ALL'})
  add('insertText',objectId=o,insertionIndex=0,text=t)
  move(o,x-7.2,y-7.2,w+14.4,h+14.4)
 else:
  o=oid('text')
  add('createShape',objectId=o,shapeType='TEXT_BOX',elementProperties=props(x-7.2,y-7.2,w+14.4,h+14.4))
  add('insertText',objectId=o,insertionIndex=0,text=t)
 text_style(o,size,color,bold,align)
 return o
def shape(x,y,w,h,fill=WHITE,stroke=None,ellipse=False):
 o=oid('shape')
 add('createShape',objectId=o,shapeType='ELLIPSE' if ellipse else 'ROUND_RECTANGLE',elementProperties=props(x,y,w,h))
 add('updateShapeProperties',objectId=o,shapeProperties={
  'shapeBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(fill)},'alpha':1}},
  'outline':{'outlineFill':{'solidFill':{'color':{'rgbColor':rgb(stroke)}}},'weight':{'magnitude':.8,'unit':'PT'}} if stroke else {'propertyState':'NOT_RENDERED'}},
  fields='shapeBackgroundFill,outline')
 return o
def line(x1,y1,x2,y2,color=ARM,width=1,arrow=False):
 o=oid('line')
 p=props(x1,y1,max(abs(x2-x1),.001),max(abs(y2-y1),.001))
 p['transform'].update(scaleX=-1 if x2<x1 else 1,scaleY=-1 if y2<y1 else 1)
 add('createLine',objectId=o,lineCategory='STRAIGHT',elementProperties=p)
 add('updateLineProperties',objectId=o,lineProperties={'lineFill':{'solidFill':{'color':{'rgbColor':rgb(color)}}},
  'weight':{'magnitude':width,'unit':'PT'},'endArrow':'OPEN_ARROW' if arrow else 'NONE'},fields='lineFill,weight,endArrow')
def original(n):return f'{PAGE}_original_{n:03d}'

# Reuse the existing three card structures, titles and trial measurements.
for n,x,w in [(174,36,112),(179,180,130),(184,342,142)]:
 move(original(n),x,132,w,150)
 if n==179:
  add('updateShapeProperties',objectId=original(n),shapeProperties={'shapeBackgroundFill':{
   'solidFill':{'color':{'rgbColor':rgb(PALE)},'alpha':1}}},fields='shapeBackgroundFill')

# Replace duplicated result views with the actual perception-to-control flow.
for n in [183,188,192,176,186]:
 if original(n) in elements:add('deleteObject',objectId=original(n))

text('Initial RGB',44,143,96,23,13.5,INK,True,'CENTER',original(175))
text('Mass estimator',190,143,110,23,13.5,TEAL,True,'CENTER',original(180))
text('Trained RL policy',350,143,126,23,13,INK,True,'CENTER',original(185))

shape(528,132,156,150)
text('Simulation',541,143,130,23,13.5,INK,True,'CENTER')

# Source camera image: the same raw image supplied to the estimator in episode 1.
initial=str((OUT.parent.parent/'runs/deployment/20261022_014201_067220/episode_001/initial.png').resolve())
add('createImage',objectId='pi_pipeline_v2_initial_rgb',url=initial,
 elementProperties=props(53,171,78,78))
text('Before contact',44,262,96,19,11.5,GRAY,False,'CENTER')

text('121.24 g',188,188,114,31,21,TEAL,True,'CENTER')
text('1.19 N to policy',188,222,114,20,11.5,TEAL,False,'CENTER')
text('Fixed for this rollout',188,260,114,19,10.5,GRAY,False,'CENTER')

# A small editable policy-network diagram.
columns=[3,4,3];x=376;y=178;w=74;h=42
for c in range(2):
 for a in range(columns[c]):
  for b in range(columns[c+1]):
   line(x+c*w/2,y+(a+.5)*h/columns[c],x+(c+1)*w/2,y+(b+.5)*h/columns[c+1],color='A5CBC0',width=.65)
for c,n in enumerate(columns):
 for j in range(n):shape(x+c*w/2-3,y+(j+.5)*h/n-3,6,6,INK,None,True)
text('State + estimate',350,255,126,19,11.5,GRAY,False,'CENTER')

# Retain the actual final robot frame from the representative 5 cm trial.
move(original(181),563.5,170,85,85)
text('Pick, lift and hold',540,262,132,19,11.5,GRAY,False,'CENTER')

line(154,208,174,208,TEAL,1.2,True)
line(316,208,336,208,TEAL,1.2,True)
line(490,208,522,208,TEAL,1.2,True)
text('actions',489,190,37,16,9.5,GRAY,False,'CENTER')

# Feedback goes to the policy, not to the fixed initial estimator.
line(606,282,606,300,ARM,1)
line(606,300,413,300,ARM,1)
line(413,300,413,282,ARM,1,True)
text('State + finger-force feedback · 50 steps',342,308,342,21,11.5,GRAY,False,'CENTER')
text('Current run: model weights and the mass estimate remain fixed.',36,334,648,21,12,INK)

# Preserve all three saved actual-versus-predicted measurements in a compact strip.
line(36,356,684,356,LINE,.8)
text('Example trials · actual mass → estimated mass',36,359,648,17,10.5,GRAY,False,'START',original(178))
text('4 cm: 64.0 → 62.32 g',36,380,204,20,12,TEAL,True,'START',original(177))
text('5 cm: 125.0 → 121.24 g',258,380,204,20,12,TEAL,True,'START',original(182))
text('6 cm: 216.0 → 212.45 g',480,380,204,20,12,TEAL,True,'START',original(187))

(OUT/'requests.json').write_text(json.dumps(requests,separators=(',',':')))
(OUT/'plan.json').write_text(json.dumps({'presentationId':raw['presentationId'],'slideId':PAGE,
 'sourceExemplar':'Current pipeline slide; reuse title, subtitle, three card frames, metric labels, and representative final frame.',
 'imageMapping':{'4 cm final':'delete duplicate result photo','5 cm final':'reuse as execution result','6 cm final':'delete duplicate result photo','5 cm raw initial RGB':'add as actual estimator input'},
 'imagePath':initial,'changedSlideOnly':4,'otherSlides':'preserve all user edits',
 'flow':'initial RGB -> mass estimator -> trained RL policy -> simulation; simulator state and forces feed back to policy; no estimator update'},indent=2))
print({'requests':len(requests),'imagePath':initial,'changedSlideOnly':4})
