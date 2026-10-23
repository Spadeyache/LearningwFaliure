"""Create native Google Slides edits from the inspected Simple Light exemplar."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
SOURCE = 'had16bcee9dd7133_0_2'
SOURCE_TITLE = 'had16bcee9dd7133_0_3'
SOURCE_BODY = 'had16bcee9dd7133_0_4'
INK = '161616'
GRAY = '5B6165'
RULE = 'D6DADC'
TEAL = '147D78'
WHITE = 'FFFFFF'
W, H = 720, 405
requests = []
slide_requests = []
counter = 0
slide_id = None
notes = json.loads((OUT.parent / 'pi_adaptation_update' / 'slide_content.json').read_text())

def rgb(c):
    return {k: int(c[i:i+2], 16)/255 for k, i in [('red',0),('green',2),('blue',4)]}

def add(t, **v):
    requests.append({t:v})

def oid(kind):
    global counter
    counter += 1
    return f'{slide_id}_{kind}_{counter:03d}'

def props(x,y,w,h):
    return {'pageObjectId':slide_id,
            'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},
            'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}

def style_text(o, size=18, color=INK, bold=False, align='START'):
    add('updateTextStyle',objectId=o,textRange={'type':'ALL'},
        style={'fontFamily':'Arial','fontSize':{'magnitude':size,'unit':'PT'},
               'bold':bold,'foregroundColor':{'opaqueColor':{'rgbColor':rgb(color)}}},
        fields='fontFamily,fontSize,bold,foregroundColor')
    add('updateParagraphStyle',objectId=o,textRange={'type':'ALL'},
        style={'alignment':align,'lineSpacing':112,
               'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':0,'unit':'PT'},
               'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},
               'indentFirstLine':{'magnitude':0,'unit':'PT'}},
        fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')

def txt(t,x,y,w,h,size=18,color=INK,bold=False,align='START'):
    o=oid('text')
    add('createShape',objectId=o,shapeType='TEXT_BOX',elementProperties=props(x,y,w,h))
    add('insertText',objectId=o,insertionIndex=0,text=t)
    style_text(o,size,color,bold,align)
    add('updateShapeProperties',objectId=o,shapeProperties={
        'contentAlignment':'TOP','outline':{'propertyState':'NOT_RENDERED'},
        'shapeBackgroundFill':{'propertyState':'NOT_RENDERED'}},
        fields='contentAlignment,outline,shapeBackgroundFill')
    return o

def box(x,y,w,h,fill=None,stroke=RULE,sw=0.8,ellipse=False):
    o=oid('shape')
    add('createShape',objectId=o,shapeType='ELLIPSE' if ellipse else 'RECTANGLE',elementProperties=props(x,y,w,h))
    p={'outline':{'propertyState':'RENDERED','outlineFill':{'solidFill':{'color':{'rgbColor':rgb(stroke)}}},
                  'weight':{'magnitude':sw,'unit':'PT'}} if stroke else {'propertyState':'NOT_RENDERED'},
       'shapeBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(fill)},'alpha':1}} if fill else {'propertyState':'NOT_RENDERED'}}
    add('updateShapeProperties',objectId=o,shapeProperties=p,fields='outline,shapeBackgroundFill')
    return o

def ln(x1,y1,x2,y2,color=RULE,sw=0.8,arrow=False,dash=False):
    o=oid('line')
    ep=props(x1,y1,max(abs(x2-x1),.01),max(abs(y2-y1),.01))
    ep['transform'].update(scaleX=-1 if x2<x1 else 1,scaleY=-1 if y2<y1 else 1)
    add('createLine',objectId=o,lineCategory='STRAIGHT',elementProperties=ep)
    lp={'lineFill':{'solidFill':{'color':{'rgbColor':rgb(color)}}},
        'weight':{'magnitude':sw,'unit':'PT'},'endArrow':'FILL_ARROW' if arrow else 'NONE',
        'dashStyle':'DASH' if dash else 'SOLID'}
    add('updateLineProperties',objectId=o,lineProperties=lp,fields='lineFill,weight,endArrow,dashStyle')

def existing(o,t,x,y,w,h,size,color):
    # The chosen exemplar's title and body are uniform-style placeholders.
    add('deleteText',objectId=o,textRange={'type':'ALL'})
    add('insertText',objectId=o,insertionIndex=0,text=t)
    # Each source placeholder has a 3,000,000-EMU intrinsic rectangle.
    base=3000000/12700
    add('updatePageElementTransform',objectId=o,applyMode='ABSOLUTE',
        transform={'scaleX':w/base,'scaleY':h/base,'translateX':x,'translateY':y,'unit':'PT'})
    style_text(o,size,color,False)

def begin(i,title,body,status):
    global slide_id, requests
    requests=[]
    slide_id=f'pi_simple_20261022_s{i:02d}'
    title_id=slide_id+'_title'; body_id=slide_id+'_body'
    add('duplicateObject',objectId=SOURCE,objectIds={SOURCE:slide_id,SOURCE_TITLE:title_id,SOURCE_BODY:body_id})
    add('updatePageProperties',objectId=slide_id,pageProperties={
        'pageBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(WHITE)},'alpha':1}}},fields='pageBackgroundFill')
    existing(title_id,title,24.54,35.04,670.91,45.09,25.2,INK)
    existing(body_id,body,24.54,90.75,670.91,57,18,GRAY)
    txt(status,27,378,450,16,9.5,TEAL)
    txt(f'{i:02d} / 08',633,378,62,16,9.5,GRAY,align='END')

def end():
    slide_requests.append(requests.copy())

def mini_robot(x,y,level=0):
    # Same arm base; only the object's supported starting elevation changes.
    sy=112-level*21
    ln(x,y+128,x+175,y+128,RULE,.7,False,True)
    box(x+8,y+119,34,8,INK,None)
    ln(x+26,y+119,x+51,y+47,GRAY,5)
    ln(x+51,y+47,x+94,y+36,GRAY,5)
    ln(x+94,y+36,x+132,y+sy-51,GRAY,4)
    for a,b in [(26,119),(51,47),(94,36)]: box(x+a-3,y+b-3,6,6,WHITE,INK,1,True)
    ln(x+132,y+sy-51,x+132,y+sy-35,INK,3)
    ln(x+115,y+sy-35,x+149,y+sy-35,INK,3)
    ln(x+115,y+sy-35,x+115,y+sy-6,INK,2.5)
    ln(x+149,y+sy-35,x+149,y+sy-6,INK,2.5)
    box(x+122,y+sy-23,20,23,WHITE,TEAL,1.3)
    ln(x+100,y+sy,x+169,y+sy,GRAY,1)
    ln(x+105,y+sy,x+105,y+128,RULE,1)
    ln(x+164,y+sy,x+164,y+128,RULE,1)

begin(1,'Adaptation needs capability and information',
      'Can a robot execute a familiar task in an unseen situation?','IDEA / WORKING HYPOTHESIS')
txt('1  Movement capability',37,168,302,33,19,INK,True)
txt('Learn how to grasp and move\nacross variations of the same task.',37,214,302,64,18,GRAY)
ln(355,169,355,308)
txt('2  Environment interpretation',383,168,302,33,19,INK,True)
txt('Estimate current conditions\nto guide the policy’s actions.',383,214,302,64,18,GRAY)
txt('Generalizable behavior  +  useful environmental context',37,320,649,34,18,TEAL)
end()

begin(2,'Our setup: RL with environmental context',
      'Train a pick-and-lift policy with standard state and selected environmental parameters.',
      'PROPOSED SETUP')
txt('Robot + task state',37,167,215,32,18,INK,True)
txt('Joints, gripper pose, task state',37,200,230,29,13.5,GRAY)
txt('Environmental parameters',37,254,240,32,18,TEAL,True)
txt('Known in training; estimated at test',37,287,250,28,13.5,GRAY)
ln(270,190,309,223,GRAY,1,True);ln(270,273,309,246,TEAL,1,True)
box(324,208,155,61,None,INK,1)
txt('RL policy',333,223,137,34,20,INK,False,'CENTER')
ln(491,238,537,238,TEAL,1,True)
txt('Grasp + move',550,223,150,35,18,INK)
txt('Training: learn the weights.  Testing: freeze the policy.',37,335,649,30,16,GRAY)
end()

begin(3,'Result 1: a controlled initial mass estimate',
      'An image-only estimator learns the size-to-mass relationship under fixed density.',
      'COMPLETED / CONTROLLED SIMULATION BASELINE')
txt('2.76 g',38,164,280,77,51,INK)
txt('Test mean absolute error',40,247,280,31,18,INK)
ln(355,169,355,274)
txt('106.37 g',383,180,302,64,37,GRAY)
txt('Constant-prediction baseline',383,247,302,31,16,GRAY)
txt('12 held-out cube sizes / 48 test images',40,306,646,31,18,TEAL)
txt('Fixed material, density, friction and camera; held-out sizes test interpolation.',40,343,646,26,12.5,GRAY)
end()

begin(4,'Result 2: the estimator and policy are connected',
      'Three configured simulation trials ended with a grasped object at the target.',
      'COMPLETED / INTEGRATION DEMONSTRATION')
for j,(label,x) in enumerate([('Initial image',38),('Mass estimate',208),('RL policy',378),('Pick + lift',548)]):
    box(x,160,132,43,None,RULE,.8)
    txt(label,x+3,169,126,28,15.5,TEAL if j==1 else INK,False,'CENTER')
    if j<3: ln(x+138,181,x+162,181,TEAL,.9,True)
xs=[38,180,342,514]; widths=[128,149,158,166]
for x,w,t in zip(xs,widths,['Cube','Actual mass','Estimate','Final outcome']): txt(t,x,223,w,24,13.5,GRAY)
ln(38,252,682,252)
for j,row in enumerate([['4 cm','64.0 g','62.32 g','Success'],['5 cm','125.0 g','121.24 g','Success'],['6 cm','216.0 g','212.45 g','Success']]):
    yy=260+j*27
    for x,w,t in zip(xs,widths,row): txt(t,x,yy,w,25,16,TEAL if x==342 else INK)
txt('One start per size, 50 actions per trial. This is not a reliability estimate.',38,349,646,25,12.5,GRAY)
end()

begin(5,'Planned: train across initial object heights',
      'Learn grasping and movement from different starting heights relative to the arm.',
      'PLANNED / HEIGHT TRAINING TO BE DONE')
for j,x in enumerate([44,270,496]):
    mini_robot(x,165,j)
    txt('h'+str(j+1),x+52,302,93,29,17,INK,False,'CENTER')
txt('Keep the top-down strategy and required lift clearance consistent.',38,342,646,30,16,GRAY)
end()

begin(6,'Planned: test at heights unseen in training',
      'Freeze the trained policy and evaluate heights withheld before training.',
      'PLANNED / INITIAL-HEIGHT GENERALIZATION TEST')
box(62,183,466,37,'F5F6F6',None)
ln(62,202,671,202,GRAY,1)
for x,label in [(82,'h1'),(192,'h2'),(369,'h3'),(506,'h4')]:
    box(x-3,199,6,6,INK,None,ellipse=True)
    txt(label,x-22,227,44,25,13.5,GRAY,False,'CENTER')
for x,label,ty in [(280,'Held-out height',160),(639,'Beyond range',160)]:
    box(x-5,197,10,10,WHITE,TEAL,1.5,True)
    txt(label,x-68,ty,136,26,13.5,TEAL,True,'CENTER')
txt('Within training range',62,267,466,29,17,INK,False,'CENTER')
txt('Report interpolation and extrapolation separately.',38,311,646,28,17,INK)
txt('Current estimator: mass. The estimator target for this height study is still open.',38,348,646,25,12.5,GRAY)
end()

begin(7,'Test rules: isolate capability and estimation',
      'Use the same policy, physical scene and starting seed in each comparison.',
      'PROPOSED TEST RULES')
txt('Context input',38,153,205,27,14,GRAY)
txt('Question',278,153,402,27,14,GRAY)
ln(38,183,682,183)
for j,(left,right) in enumerate([
    ('True context','Can the policy handle the unseen height?'),
    ('Estimated context','How does estimation affect execution?'),
    ('Fixed nominal context','Does useful context improve execution?')]):
    yy=195+j*39
    txt(left,38,yy,222,31,16.5,TEAL if j==1 else INK,j==1)
    txt(right,278,yy,404,31,16,INK)
    if j<2: ln(38,yy+34,682,yy+34)
txt('Measure: held pick-and-lift success + estimation error.',38,324,646,29,16,INK)
txt('No test-height fine-tuning. Remove true copies of estimated inputs.',38,353,646,23,12.5,GRAY)
end()

begin(8,'What is established, and what comes next?',
      'The components are working; unseen-height adaptation still needs to be tested.',
      'PI DISCUSSION / NEXT EXPERIMENT')
txt('Established',38,160,291,32,19,TEAL,True)
txt('Controlled mass estimation\nEstimator–policy integration',38,205,291,75,18,INK)
ln(355,160,355,285)
txt('Next experiment',383,160,302,32,19,INK,True)
txt('Train across initial heights\nTest withheld heights\nCompare context inputs',383,205,302,85,18,INK)
txt('Open choice: what should the estimator predict?',38,311,646,31,18,INK)
txt('Height, physical properties, or both.',38,343,646,27,16,GRAY)
end()

raw=json.loads((OUT/'raw-template.json').read_text())['structuredContent']
originals=[x['objectId'] for x in raw['slides']]
new_ids=[f'pi_simple_20261022_s{i:02d}' for i in range(1,9)]
plan={'presentationId':raw['presentationId'],'originalRevisionId':raw.get('revisionId'),
      'originalSlideIds':originals,'newSlideIds':new_ids,
      'preservation':'Keep the six existing slides as skipped reference slides after the eight main slides.',
      'style':{'fontFamily':'Arial','titlePt':25.2,'bodyPt':18,'background':'FFFFFF','accent':TEAL},
      'slides':[{'narrativeRole':notes[i]['title'],'sourceExemplar':SOURCE,'layoutId':'p4',
                 'construction':'duplicate; replace uniform title and body; add editable diagram/text objects',
                 'mediaMapping':'No media in source exemplar.','newSlideId':new_ids[i],
                 'speakerNotes':notes[i]['notes']} for i in range(8)]}
(OUT/'construction-plan.json').write_text(json.dumps(plan,indent=2))
for k,group in enumerate([slide_requests[:4],slide_requests[4:]],1):
    req=[r for sr in group for r in sr]
    (OUT/f'requests-{k}.json').write_text(json.dumps(req,separators=(',',':')))
    print('batch',k,'requests',len(req))
print('Prepared 8 slides; existing 6 retained.')
