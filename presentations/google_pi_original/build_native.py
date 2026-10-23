"""Restore the original vector slide design in the existing Google deck."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
scene=json.loads((OUT/'scene.json').read_text())
before=json.loads((OUT/'raw-before.json').read_text())['structuredContent']
current={s['objectId']:s for s in before['slides']}
S=.45
requests=[];serial=0;page=None;image_requests=[]

def rgb(c):
    c=c.lstrip('#')
    return {k:int(c[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}
def add(t,**v):requests.append({t:v})
def oid():
    global serial
    serial+=1
    return f'{page}_original_{serial:03d}'
def ep(x,y,w,h):
    return {'pageObjectId':page,'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},
            'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}

# Preserve the user's most recent first-slide edits. Wrap the long title locally.
def shape_text(slide,object_id):
    e=next(e for e in slide['pageElements'] if e['objectId']==object_id)
    return ''.join(t.get('textRun',{}).get('content','') for t in e['shape']['text']['textElements']).strip()
first=current['pi_simple_20261022_s01']
user_title=shape_text(first,'pi_simple_20261022_s01_title')
user_body=shape_text(first,'pi_simple_20261022_s01_body')
for o in scene[0]['items']:
    if o['kind']=='text' and o['str']==scene[0]['title']:
        o.update(str=user_title.replace(' a task in ',' a task\nin '),size=43,lh=53,h=113)
    elif o['kind']=='text' and o['str'].startswith('How can a robot execute'):
        o.update(str=user_body,y=220,h=45)

batches=[]
for n,slide in enumerate(scene,1):
    page=f'pi_simple_20261022_s{n:02d}'
    assert page in current, f'Missing target slide: {page}'
    requests=[]
    for e in current[page]['pageElements']:
        add('deleteObject',objectId=e['objectId'])
    add('updatePageProperties',objectId=page,pageProperties={'pageBackgroundFill':{
        'solidFill':{'color':{'rgbColor':rgb('F6F4EF')},'alpha':1}}},fields='pageBackgroundFill')
    for o in slide['items']:
        if o['kind']=='rect' and o['x']==0 and o['y']==0 and o['w']==1600 and o['h']==900:
            continue
        obj=oid()
        if o['kind'] in ('rect','ellipse'):
            add('createShape',objectId=obj,shapeType='ELLIPSE' if o['kind']=='ellipse' else 'ROUND_RECTANGLE' if o.get('r',0)>0 else 'RECTANGLE',
                elementProperties=ep(o['x']*S,o['y']*S,o['w']*S,o['h']*S))
            fill=o.get('fill');stroke=o.get('stroke')
            p={'shapeBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(fill)},'alpha':1}} if fill and fill!='none' else {'propertyState':'NOT_RENDERED'},
               'outline':{'propertyState':'RENDERED','outlineFill':{'solidFill':{'color':{'rgbColor':rgb(stroke)}}},'weight':{'magnitude':o.get('sw',1)*S,'unit':'PT'},'dashStyle':'DASH' if o.get('dash') else 'SOLID'} if stroke else {'propertyState':'NOT_RENDERED'}}
            add('updateShapeProperties',objectId=obj,shapeProperties=p,fields='shapeBackgroundFill,outline')
        elif o['kind']=='line':
            dx=(o['x2']-o['x1'])*S;dy=(o['y2']-o['y1'])*S
            p=ep(o['x1']*S,o['y1']*S,max(abs(dx),.001),max(abs(dy),.001))
            p['transform'].update(scaleX=-1 if dx<0 else 1,scaleY=-1 if dy<0 else 1)
            add('createLine',objectId=obj,lineCategory='STRAIGHT',elementProperties=p)
            add('updateLineProperties',objectId=obj,lineProperties={
                'lineFill':{'solidFill':{'color':{'rgbColor':rgb(o['color'])}}},
                'weight':{'magnitude':o['sw']*S,'unit':'PT'},
                'dashStyle':'DASH' if o.get('dash') else 'SOLID','endArrow':'OPEN_ARROW' if o.get('arrow') else 'NONE'},
                fields='lineFill,weight,dashStyle,endArrow')
        elif o['kind']=='text':
            # Google text boxes have native insets; compensate to match the source's zero margins.
            add('createShape',objectId=obj,shapeType='TEXT_BOX',
                elementProperties=ep(o['x']*S-7.2,o['y']*S-7.2,o['w']*S+14.4,o['h']*S+14.4))
            add('insertText',objectId=obj,insertionIndex=0,text=o['str'])
            add('updateTextStyle',objectId=obj,textRange={'type':'ALL'},style={
                'fontFamily':'Arial','fontSize':{'magnitude':o['size']*S,'unit':'PT'},
                'bold':o['weight']>=600,'foregroundColor':{'opaqueColor':{'rgbColor':rgb(o['color'])}}},
                fields='fontFamily,fontSize,bold,foregroundColor')
            add('updateParagraphStyle',objectId=obj,textRange={'type':'ALL'},style={
                'alignment':o['align'],'lineSpacing':100*o['lh']/(o['size']*1.15),
                'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':0,'unit':'PT'},
                'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},
                'indentFirstLine':{'magnitude':0,'unit':'PT'}},
                fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')
            add('updateShapeProperties',objectId=obj,shapeProperties={'contentAlignment':'TOP',
                'outline':{'propertyState':'NOT_RENDERED'},'shapeBackgroundFill':{'propertyState':'NOT_RENDERED'}},
                fields='contentAlignment,outline,shapeBackgroundFill')
        elif o['kind']=='image':
            local=o['path']
            native='\\\\wsl.localhost\\Ubuntu'+local.replace('/','\\')
            image_requests.append({'slide':n,'path':local,'nativePath':native,'request':{
                'createImage':{'objectId':obj,'url':native,
                               'elementProperties':ep(o['x']*S,o['y']*S,o['w']*S,o['h']*S)}}})
    batches.append(requests)
for i in range(4):
    req=batches[i*2]+batches[i*2+1]
    (OUT/f'native-{i+1}.json').write_text(json.dumps(req,separators=(',',':')))
    print('batch',i+1,'requests',len(req))
(OUT/'images.json').write_text(json.dumps(image_requests,separators=(',',':')))
(OUT/'restore-plan.json').write_text(json.dumps({'presentationId':before['presentationId'],'revisionId':before['revisionId'],
    'targetSlideIds':[s['objectId'] for s in before['slides']],
    'source':'presentations/pi_adaptation_update/robot_adaptation_pi.pptx and vector previews',
    'firstSlideEditsPreserved':{'title':user_title,'body':user_body},
    'originalReferenceSlides':'Absent in latest user-edited deck; do not recreate.'},indent=2))
print('images',len(image_requests))
