from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
raw = json.loads((OUT/'raw-before.json').read_text())['structuredContent']
source = raw['slides'][0]
PAGE = 'pi_next_steps_20261022'
mapping = {source['objectId']: PAGE}
for i,e in enumerate(source['pageElements']):
    mapping[e['objectId']] = f'{PAGE}_exemplar_{i:02d}'
elements = {mapping[e['objectId']]:e for e in source['pageElements']}
requests = [{'duplicateObject':{'objectId':source['objectId'],'objectIds':mapping}}]
INK='183139'; TEAL='087F7B'; GRAY='62747A'; PALE='E1EFEB'; WHITE='FFFFFF'
counter=0
def add(t,**v):requests.append({t:v})
def rgb(c):return {k:int(c[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}
def oid(kind):
    global counter
    counter+=1
    return f'{PAGE}_{kind}_{counter:02d}'
def original(n):return mapping[f'pi_simple_20261022_s01_original_{n:03d}']
def props(x,y,w,h):return {'pageObjectId':PAGE,'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}
def move(o,x,y,w,h):
    e=elements[o]
    pt=lambda d:d['magnitude']/12700 if d['unit']=='EMU' else d['magnitude']
    add('updatePageElementTransform',objectId=o,applyMode='ABSOLUTE',transform={'scaleX':w/pt(e['size']['width']),'scaleY':h/pt(e['size']['height']),'translateX':x,'translateY':y,'unit':'PT'})
def text(t,x,y,w,h,size,color=INK,bold=False,existing=None,align='START'):
    o=existing or oid('text')
    if existing:
        add('deleteText',objectId=o,textRange={'type':'ALL'})
        add('insertText',objectId=o,insertionIndex=0,text=t)
        move(o,x-7.2,y-7.2,w+14.4,h+14.4)
    else:
        add('createShape',objectId=o,shapeType='TEXT_BOX',elementProperties=props(x-7.2,y-7.2,w+14.4,h+14.4))
        add('insertText',objectId=o,insertionIndex=0,text=t)
    add('updateTextStyle',objectId=o,textRange={'type':'ALL'},style={'fontFamily':'Arial','fontSize':{'magnitude':size,'unit':'PT'},'bold':bold,'foregroundColor':{'opaqueColor':{'rgbColor':rgb(color)}}},fields='fontFamily,fontSize,bold,foregroundColor')
    add('updateParagraphStyle',objectId=o,textRange={'type':'ALL'},style={'alignment':align,'lineSpacing':110,'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'},'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},'indentFirstLine':{'magnitude':0,'unit':'PT'}},fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')
    return o
def box(x,y,w,h,fill):
    o=oid('stage')
    add('createShape',objectId=o,shapeType='ROUND_RECTANGLE',elementProperties=props(x,y,w,h))
    add('updateShapeProperties',objectId=o,shapeProperties={'shapeBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(fill)}}},'outline':{'propertyState':'NOT_RENDERED'}},fields='shapeBackgroundFill,outline')
    return o
def line(x1,y1,x2,y2,arrow=False):
    o=oid('line');p=props(x1,y1,max(abs(x2-x1),.001),max(abs(y2-y1),.001))
    p['transform'].update(scaleX=-1 if x2<x1 else 1,scaleY=-1 if y2<y1 else 1)
    add('createLine',objectId=o,lineCategory='STRAIGHT',elementProperties=p)
    add('updateLineProperties',objectId=o,lineProperties={'lineFill':{'solidFill':{'color':{'rgbColor':rgb(TEAL)}}},'weight':{'magnitude':1.15,'unit':'PT'},'endArrow':'OPEN_ARROW' if arrow else 'NONE'},fields='lineFill,weight,endArrow')

text('Next: let the estimator learn at deployment',36,44,648,32,19.35,INK,True,original(3))
text('Proposed loop: revise estimates from the robot’s response.',36,82,648,24,13.5,GRAY,False,original(4))

for x,label,caption,fill in [(36,'Estimate','Physical properties',PALE),(210,'Execute','Pick and lift',WHITE),(384,'Observe','Response + outcome',WHITE),(558,'Update','Revise estimate',PALE)]:
    box(x,122,126,44,fill)
    text(label,x+8,133,110,24,15,TEAL if fill==PALE else INK,True,align='CENTER')
    text(caption,x,175,126,20,12,GRAY,align='CENTER')
for x1,x2 in [(168,204),(342,378),(516,552)]:line(x1,144,x2,144,True)
line(621,198,621,212);line(621,212,99,212);line(99,212,99,198,True)

# Reuse the two-column hierarchy and marker circles from slide 1.
move(original(10),49,237,12,12)
move(original(73),386,237,12,12)
add('deleteObject',objectId=original(74))
text('Lessons so far',70,230,250,28,17.55,INK,True,original(12))
text('Next experiments',407,230,277,28,16.65,INK,True,original(75))
text('Visual estimation works; task benefit still needs comparison.\nFailure labels did not isolate the intended cause.',49,268,290,75,14.4,INK,False,original(13))
text('Compare fixed estimates, updated estimates and no estimator.\nUse CREST; vary movement conditions and materials.',386,268,298,75,14.4,INK,False,original(76))
text('Longer term: automate variable selection and expand training variation.',36,370,648,23,13.5,INK,False,original(91))

(OUT/'requests.json').write_text(json.dumps(requests,separators=(',',':')))
(OUT/'construction-plan.json').write_text(json.dumps({'slideId':PAGE,'narrativeRole':'Combine existing slides 5 and 6 into one proposed next-step slide','exemplar':source['objectId'],'construction':'duplicate native two-column slide 1 and reuse its title, subtitle, column headings, body frames, marker circles, and closing statement; add a four-stage proposed update loop','mediaMapping':'no media on exemplar','sourceSlides':[raw['slides'][4]['objectId'],raw['slides'][5]['objectId']],'preserveOriginalSlides':True,'targetIndex':4,'notes':'Keep the original research notes and arXiv reading link in speaker notes. Proposed updates are future work.'},indent=2))
print({'requests':len(requests),'slideId':PAGE})
