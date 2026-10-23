from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'raw-before.json').read_text())['structuredContent']
source=raw['slides'][0]
PAGE='pi_adaptability_vision_zero'
mapping={source['objectId']:PAGE}
for i,e in enumerate(source['pageElements']):mapping[e['objectId']]=f'{PAGE}_native_{i:02d}'
elements={mapping[e['objectId']]:e for e in source['pageElements']}
req=[{'duplicateObject':{'objectId':source['objectId'],'objectIds':mapping}}]
INK='183139';TEAL='087F7B';GRAY='62747A';LINE='93A5AA'
counter=0
def add(t,**v):req.append({t:v})
def rgb(c):return {k:int(c[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}
def orig(n):return mapping[f'pi_simple_20261022_s01_original_{n:03d}']
def props(x,y,w,h):return {'pageObjectId':PAGE,'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}
def oid(kind):
 global counter
 counter+=1
 return f'{PAGE}_{kind}_{counter:02d}'
def move(o,x,y,w,h):
 e=elements[o]
 cv=lambda d:d['magnitude']/12700 if d['unit']=='EMU' else d['magnitude']
 add('updatePageElementTransform',objectId=o,applyMode='ABSOLUTE',transform={'scaleX':w/cv(e['size']['width']),'scaleY':h/cv(e['size']['height']),'translateX':x,'translateY':y,'unit':'PT'})
def text(t,x,y,w,h,size=14.4,color=INK,bold=False,align='START',existing=None):
 o=existing or oid('text')
 if existing:
  add('deleteText',objectId=o,textRange={'type':'ALL'})
  move(o,x-7.2,y-7.2,w+14.4,h+14.4)
 else:add('createShape',objectId=o,shapeType='TEXT_BOX',elementProperties=props(x-7.2,y-7.2,w+14.4,h+14.4))
 add('insertText',objectId=o,insertionIndex=0,text=t)
 add('updateTextStyle',objectId=o,textRange={'type':'ALL'},style={'fontFamily':'Arial','fontSize':{'magnitude':size,'unit':'PT'},'bold':bold,'italic':False,'underline':False,'foregroundColor':{'opaqueColor':{'rgbColor':rgb(color)}}},fields='fontFamily,fontSize,bold,italic,underline,foregroundColor,link')
 add('updateParagraphStyle',objectId=o,textRange={'type':'ALL'},style={'alignment':align,'lineSpacing':110,'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'},'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},'indentFirstLine':{'magnitude':0,'unit':'PT'}},fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')
 return o
def line(x1,y1,x2,y2,color=TEAL,arrow=False):
 o=oid('line');p=props(x1,y1,max(abs(x2-x1),.001),max(abs(y2-y1),.001))
 p['transform'].update(scaleX=-1 if x2<x1 else 1,scaleY=-1 if y2<y1 else 1)
 add('createLine',objectId=o,lineCategory='STRAIGHT',elementProperties=p)
 add('updateLineProperties',objectId=o,lineProperties={'lineFill':{'solidFill':{'color':{'rgbColor':rgb(color)}}},'weight':{'magnitude':1.15,'unit':'PT'},'endArrow':'OPEN_ARROW' if arrow else 'NONE'},fields='lineFill,weight,endArrow')

text('My view of robot adaptability',36,44,648,32,19.35,bold=True,existing=orig(3))
text('Within one task, learn from success, failure and unexpected responses.',36,83,648,25,13.5,GRAY,existing=orig(4))

text('Execute with current skills + understanding',173,124,375,25,14.4,bold=True,align='CENTER')
line(360,153,360,172,arrow=True)
text('What needs to change?',217,181,286,28,16.65,TEAL,True,'CENTER')

# Two complementary areas of learning; text and native arrows, no boxes.
line(360,209,360,221)
line(180,221,535,221)
line(180,221,180,238,arrow=True)
line(535,221,535,238,arrow=True)
move(orig(10),49,254,12,12)
move(orig(73),386,254,12,12)
add('deleteObject',objectId=orig(74))
text('Movement capability',70,247,270,28,17.55,bold=True,existing=orig(12))
text('Physical understanding',407,247,277,28,16.65,bold=True,existing=orig(75))
text('Recognize skill limits\nAdapt or learn new movements',49,285,290,48,14.4,existing=orig(13))
text('Refine object and situation estimates\nLearn missing physical factors',386,285,298,48,14.4,existing=orig(76))

# Feedback returns both kinds of learning to future execution.
line(180,333,180,341,LINE)
line(535,333,535,341,LINE)
line(180,341,700,341,LINE)
line(700,341,700,136,LINE)
line(700,136,562,136,LINE,True)
text('Scope of learning: this encounter · this object · broader experience',36,369,648,24,13.5,existing=orig(91))

(OUT/'requests.json').write_text(json.dumps(req,separators=(',',':')))
(OUT/'construction-plan.json').write_text(json.dumps({'newSlideId':PAGE,'narrativeRole':'Slide zero: overall vision of adaptability within a single task','exemplarSlideId':source['objectId'],'construction':'Duplicate the native two-column opening slide, reuse title/subtitle/two headings/two bodies/two circle markers and closing statement, add an editable interaction/learning feedback diagram','mediaMapping':'No media on exemplar','speakerNotes':'Do not add notes; verify new notes are empty','style':'Existing warm off-white, navy and teal, Arial. No boxes, header or footer.','targetPosition':0,'preserveOtherSlides':True},indent=2))
print({'requests':len(req),'newSlideId':PAGE,'addedNotes':0,'addedBoxes':0})
