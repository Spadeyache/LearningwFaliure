"""Build an on-slide, PI-facing story using existing native slide objects."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'raw-before.json').read_text())['structuredContent']
slides=raw['slides'];elements={e['objectId']:e for s in slides for e in s['pageElements']}
req=[];counter=0
INK='183139';TEAL='087F7B';GRAY='62747A';LINE='93A5AA';BG='F6F4EF';RED='C92B24'
def add(t,**v):req.append({t:v})
def rgb(c):return {k:int(c[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}
def pt(d):return d['magnitude']/12700 if d['unit']=='EMU' else d['magnitude']
def oid(kind):
 global counter
 counter+=1
 return f'pi_clear_{kind}_{counter:03d}'
def props(page,x,y,w,h):return {'pageObjectId':page,'size':{'width':{'magnitude':w,'unit':'PT'},'height':{'magnitude':h,'unit':'PT'}},'transform':{'scaleX':1,'scaleY':1,'translateX':x,'translateY':y,'unit':'PT'}}
def move(o,x,y,w,h):
 e=elements[o]
 add('updatePageElementTransform',objectId=o,applyMode='ABSOLUTE',transform={'scaleX':w/pt(e['size']['width']),'scaleY':h/pt(e['size']['height']),'translateX':x,'translateY':y,'unit':'PT'})
def text(page,t,x,y,w,h,size=14.4,color=INK,bold=False,align='START',existing=None):
 o=existing or oid('text')
 if existing:
  add('deleteText',objectId=o,textRange={'type':'ALL'})
  move(o,x-7.2,y-7.2,w+14.4,h+14.4)
 else:add('createShape',objectId=o,shapeType='TEXT_BOX',elementProperties=props(page,x-7.2,y-7.2,w+14.4,h+14.4))
 add('insertText',objectId=o,insertionIndex=0,text=t)
 add('deleteParagraphBullets',objectId=o,textRange={'type':'ALL'})
 add('updateTextStyle',objectId=o,textRange={'type':'ALL'},style={'fontFamily':'Arial','fontSize':{'magnitude':size,'unit':'PT'},'bold':bold,'italic':False,'underline':False,'foregroundColor':{'opaqueColor':{'rgbColor':rgb(color)}}},fields='fontFamily,fontSize,bold,italic,underline,foregroundColor,link')
 add('updateParagraphStyle',objectId=o,textRange={'type':'ALL'},style={'alignment':align,'lineSpacing':110,'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'},'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},'indentFirstLine':{'magnitude':0,'unit':'PT'}},fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')
 return o
def line(page,x1,y1,x2,y2,color=LINE,width=1.1,arrow=False,dashed=False):
 o=oid('line');p=props(page,x1,y1,max(abs(x2-x1),.001),max(abs(y2-y1),.001))
 p['transform'].update(scaleX=-1 if x2<x1 else 1,scaleY=-1 if y2<y1 else 1)
 add('createLine',objectId=o,lineCategory='STRAIGHT',elementProperties=p)
 add('updateLineProperties',objectId=o,lineProperties={'lineFill':{'solidFill':{'color':{'rgbColor':rgb(color)}}},'weight':{'magnitude':width,'unit':'PT'},'endArrow':'OPEN_ARROW' if arrow else 'NONE','dashStyle':'DASH' if dashed else 'SOLID'},fields='lineFill,weight,endArrow,dashStyle')
def shape(page,x,y,w,h,color=RED,ellipse=False):
 o=oid('object')
 add('createShape',objectId=o,shapeType='ELLIPSE' if ellipse else 'RECTANGLE',elementProperties=props(page,x,y,w,h))
 add('updateShapeProperties',objectId=o,shapeProperties={'shapeBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(color)}}},'outline':{'propertyState':'NOT_RENDERED'}},fields='shapeBackgroundFill,outline')
 return o
def slipping_cube(page,cx,cy):
 # Editable schematic, explicitly labeled illustrative on the slide.
 line(page,cx,cy-58,cx,cy-32,INK,3)
 line(page,cx-27,cy-32,cx+27,cy-32,INK,3)
 line(page,cx-27,cy-32,cx-27,cy+3,INK,3)
 line(page,cx+27,cy-32,cx+27,cy+3,INK,3)
 line(page,cx-27,cy+3,cx-18,cy+3,INK,3)
 line(page,cx+27,cy+3,cx+18,cy+3,INK,3)
 shape(page,cx-16,cy+21,32,32)
 line(page,cx+44,cy+9,cx+44,cy+53,RED,1.5,True,True)
def warm(page):add('updatePageProperties',objectId=page,pageProperties={'pageBackgroundFill':{'solidFill':{'color':{'rgbColor':rgb(BG)},'alpha':1}}},fields='pageBackgroundFill')
def original(s,n):return f'pi_simple_20261022_s{s:02d}_original_{n:03d}'
def title(page,o,t,size=19.35):text(page,t,36,44,648,34,size,bold=True,existing=o)
def subtitle(page,o,t):text(page,t,36,83,648,37,13.5,GRAY,existing=o)

# 1. Vision, grounded in one task and one ambiguous outcome.
p=slides[0]['objectId'];z='pi_adaptability_vision_zero_native_'
keep={z+f'{i:02d}' for i in [0,1,2,3,4,5,7,8,9]}
for e in slides[0]['pageElements']:
 if e['objectId'] not in keep:add('deleteObject',objectId=e['objectId'])
title(p,z+'00','Robot adaptation: learn what must change')
subtitle(p,z+'01','Illustrative pick-and-lift example: a cube slips during execution.')
slipping_cube(p,128,194)
text(p,'Observed: slip',42,266,172,25,15,bold=True,align='CENTER')
text(p,'Two possible learning needs',280,122,404,24,13.5,TEAL,True)
move(z+'05',280,164,12,12)
move(z+'02',280,259,12,12)
text(p,'Refine physical understanding',301,156,383,28,16.65,bold=True,existing=z+'07')
text(p,'The mass or friction estimate is wrong.\nAn existing movement may still succeed.',301,192,383,48,14.4,existing=z+'08')
text(p,'Expand movement capability',301,251,383,28,17.55,bold=True,existing=z+'03')
text(p,'The available grasp or motion is insufficient.\nLearn a different way to execute the task.',301,287,383,48,14.4,existing=z+'04')
line(p,207,224,266,180,TEAL,1.1,True)
line(p,207,224,266,275,TEAL,1.1,True)
text(p,'A failure alone does not identify the limitation; interaction must provide evidence.',36,341,648,26,13.5,existing=z+'09')
text(p,'The correction may belong to this encounter, this object or broader experience.',36,374,648,24,13.5)

# 2. Retention/generalization of a correction is part of the vision.
p=slides[1]['objectId']
title(p,original(1,3),'A useful correction must have the right scope')
subtitle(p,original(1,4),'Illustrative examples within the same pick-and-lift task.')
move(original(1,10),49,147,12,12);move(original(1,73),49,227,12,12)
add('deleteObject',objectId=original(1,74))
text(p,'This encounter',72,139,205,29,17.55,bold=True,existing=original(1,12))
text(p,'A contact or pose error occurs only in this attempt.\nRevise the current state or physical estimate.',310,139,374,56,14.4,existing=original(1,13))
text(p,'This object',72,219,205,29,16.65,bold=True,existing=original(1,75))
text(p,'Repeated encounters reveal a wrong mass belief for this cube.\nRetain a correction for this object.',310,219,374,56,14.4,existing=original(1,76))
shape(p,49,307,12,12,TEAL,True)
text(p,'Across objects',72,299,205,29,16.65,bold=True)
text(p,'Similar mismatches recur across objects.\nReconsider the shared estimator, physical model or skill.',310,299,374,56,14.4)
text(p,'Whether to retain or generalize a correction is itself a learning problem.',36,374,648,24,13.5,existing=original(1,91))

# 3. Where the current study enters the larger system.
p=slides[2]['objectId']
title(p,original(2,94),'Current work: isolate physical estimation',25.65)
subtitle(p,original(2,95),'Top-down pick and lift. A fixed RL policy receives state and an estimated object mass.')
text(p,'Robot + task state',49,148,214,28,14.85,bold=True,existing=original(2,100))
text(p,'Joints, gripper and object state',49,176,214,32,12.15,GRAY,existing=original(2,101))
text(p,'Estimated object mass',49,239,230,28,14.4,TEAL,True,existing=original(2,103))
text(p,'From the initial RGB image\nConverted to weight for the policy',49,269,230,52,12.15,TEAL,existing=original(2,104))
text(p,'Fixed RL policy',337,204,160,29,15.3,bold=True,align='CENTER',existing=original(2,142))
text(p,'Grasp and lift\nactions',548,198,136,55,14.85,bold=True,align='CENTER',existing=original(2,145))
text(p,'This setup isolates the context estimate; learning new movements is a longer-term direction.',36,346,648,33,13.5,existing=original(2,146))

# 4. Preserve the actual chart and metrics; make the scope and role explicit.
p=slides[3]['objectId']
title(p,original(3,150),'Result: initial visual mass estimation',25.65)
subtitle(p,original(3,151),'Fixed material and density; predict mass from appearance.\nTest on held-out cube sizes within the sampled range.')
text(p,'12 held-out sizes / 48 test images',36,309,648,28,14.4,bold=True,existing=original(3,164))
text(p,'Scope: one material; fixed density, friction and camera. Size interpolation only.',36,341,648,25,12.15,GRAY,existing=original(3,165))
text(p,'Next challenge: the same appearance can conceal a different mass.',36,374,648,24,13.5)

# 5. Keep actual images and policy diagram; distinguish integration from benefit.
p=slides[4]['objectId']
title(p,original(4,169),'Result: estimation connected to execution',25.65)
subtitle(p,original(4,170),'One initial image → one mass estimate → a fixed policy → pick-and-lift execution.')
text(p,'Example run: 125.0 g actual → 121.24 g estimated; cube lifted and held.',36,337,648,26,13.5,existing='pi_pipeline_v2_text_051')
text(p,'Estimate fixed during execution; benefit over nominal context remains unmeasured.',36,371,648,24,13.5)

# 6. Next question: mapping observed response patterns to candidate explanations.
p=slides[5]['objectId'];r='h437c0d080b9bf084_0_'
warm(p)
title(p,r+'5','Next: test what a failure reveals')
subtitle(p,r+'6','Proposed study: relate observed response patterns to candidate physical variables.')
slipping_cube(p,117,204)
text(p,'Observed: slip',36,275,172,25,15,bold=True,align='CENTER')
title(p,r+'5','Next: turn response patterns into update decisions')
subtitle(p,r+'6','Build on completed motion grouping and controlled mass/friction response comparisons.')
text(p,'Evidence and the remaining gap',280,126,404,25,14.85,TEAL,True)
text(p,'Motion',280,166,103,25,16.65,TEAL,True)
text(p,'Two broad trajectory groups.\nIntended causal types unvalidated.',398,163,286,48)
text(p,'Physics',280,227,103,25,16.65,TEAL,True)
text(p,'90 matched mass/friction trials;\n7 observed response profiles.',398,224,286,48)
text(p,'Next question',280,288,119,25,14.85,TEAL,True)
text(p,'Which evidence justifies changing an\nestimate, a model or a movement?',414,285,270,48)
for y in [180,241,302]:line(p,202,234,263,y,LINE,1,True)
text(p,'Changing actual physics is a different intervention from correcting the estimate.',36,345,648,24,13.5)
text(p,'Next: link observed patterns to useful update choices, then test those choices in execution.',36,375,648,24,13.5)

# 7. Proposed refinement pilot; the history-to-estimate mechanism remains a baseline.
p=slides[6]['objectId']
title(p,'pi_next_steps_20261022_exemplar_00','Then: test whether estimate updates help')
subtitle(p,'pi_next_steps_20261022_exemplar_01','Proposed pilot: one cube appearance, varied mass. Keep friction and policy fixed.')
for o,t,x,col in [('pi_next_steps_20261022_text_02','Initial estimate',44,TEAL),('pi_next_steps_20261022_text_05','Interaction',218,INK),('pi_next_steps_20261022_text_08','Revised estimate',392,TEAL),('pi_next_steps_20261022_text_11','Task execution',566,INK)]:
 text(p,t,x-7,133,124,30,15,col,True,'CENTER',o)
for n in [16,17,18]:add('deleteObject',objectId=f'pi_next_steps_20261022_line_{n}')
text(p,'Train the update rule in simulation; at test time only the estimate changes.',36,184,648,25,13.5)
text(p,'Check before training',49,232,290,28,16.65,bold=True,existing='pi_reframe_known_title')
text(p,'Does accurate context help this policy?\nCan the available interaction reveal mass?',49,270,290,77,14.4,existing='pi_reframe_known_body')
text(p,'Matched comparisons',386,232,298,28,16.65,bold=True,existing='pi_reframe_unknown_title')
text(p,'Initial estimate held fixed\nInteraction-updated estimate\nTrue mass supplied as a reference',386,270,298,77,14.4,existing='pi_reframe_unknown_body')
text(p,'Same interaction budget. Measure estimate error, task success and drops.',36,372,648,25,13.5,existing='pi_reframe_open_question')

# 8. Return to the full vision and separate next work from the longer-term agenda.
p=slides[7]['objectId'];r='h437c0d080b9bf084_0_'
title(p,r+'15','Longer term: choose the correction and its scope')
subtitle(p,r+'16','The fixed-policy study is one step toward improving both understanding and movement.')
move(r+'21',49,147,12,12);move(r+'24',386,147,12,12)
text(p,'Interpret the limitation',70,139,270,28,17.55,bold=True,existing=r+'22')
text(p,'Wrong physical estimate?\nMissing physical factor?\nInsufficient movement capability?',49,181,290,97,14.4,existing=r+'23')
text(p,'Choose what to retain',407,139,277,28,16.65,bold=True,existing=r+'25')
text(p,'A correction for this encounter?\nAn object-specific belief?\nA change shared across future encounters?',386,181,298,97,14.4,existing=r+'26')
text(p,'Established',36,316,204,23,14.85,TEAL,True,existing=r+'27')
text(p,'Initial estimate\n+ simulated execution',36,346,204,47,13.5,existing='pi_reframe_later_work')
text(p,'Next',264,316,190,23,14.85,TEAL,True)
text(p,'Failure signals\n+ estimate refinement',264,346,190,47,13.5)
text(p,'Longer term',492,316,192,23,14.85,TEAL,True)
text(p,'Expand physical models\n+ movement capabilities',492,346,192,47,13.5)
line(p,231,331,253,331,TEAL,1.1,True);line(p,459,331,481,331,TEAL,1.1,True)

# Everything needed by the reader is visible. Remove old notes from main slides.
for s in slides[:8]:
 n=s.get('slideProperties',{}).get('notesPage',{})
 note=n.get('notesProperties',{}).get('speakerNotesObjectId')
 content=''.join(t.get('textRun',{}).get('content','') for e in n.get('pageElements',[]) if e['objectId']==note for t in e.get('shape',{}).get('text',{}).get('textElements',[]))
 if note and content.strip():add('deleteText',objectId=note,textRange={'type':'ALL'})
# Preserve the unrelated draft page as an appendix, excluded from presentation.
add('updateSlideProperties',objectId=slides[8]['objectId'],slideProperties={'isSkipped':True},fields='isSkipped')

# Additional completed experiment requested at the end. Duplicate before editing
# its source, so all copied page elements have known IDs and none are stale.
append='pi_failure_discovery_result'
source=slides[1]
mapping={source['objectId']:append}
for i,e in enumerate(source['pageElements']):mapping[e['objectId']]=f'{append}_native_{i:02d}'
req.insert(0,{'duplicateObject':{'objectId':source['objectId'],'objectIds':mapping}})
for e in source['pageElements']:elements[mapping[e['objectId']]]=e
def copied(n):return mapping[original(1,n)]
for n in [10,73,74]:add('deleteObject',objectId=copied(n))
title(append,copied(3),'Failure-type discovery: behavior groups were not enough')
subtitle(append,copied(4),'Completed exploration: identify meaningful failure types from recorded motion and pose.')
text(append,'Motion / pose / force history → PCA + k-means → 2 candidate behavior groups',36,128,648,25,13.5)
add('createImage',objectId='pi_failure_behavior_plot',url=str(OUT/'failure_behavior_groups.png'),elementProperties=props(append,36,167,420,420*2.8/6.2))
text(append,'What emerged',480,165,204,27,16.65,bold=True,existing=copied(12))
text(append,'Two broad groups of behavior.\nThey did not establish the intended human-interpretable failure distinctions.',480,202,204,98,14.4,existing=copied(13))
text(append,'Still unresolved',480,301,204,27,16.65,bold=True,existing=copied(75))
text(append,'Causal explanations and known / unknown failure recognition remain unvalidated.',480,338,204,60,13.5,existing=copied(76))
text(append,'230 saved attempts · 154 failures · 2 candidate groups',36,371,420,24,13.5,existing=copied(91))

(OUT/'requests.json').write_text(json.dumps(req,separators=(',',':')))
(OUT/'construction-plan.json').write_text(json.dumps({'mainSlides':[{'id':s['objectId'],'role':role,'exemplar':s['objectId'],'construction':'edit existing native objects in place'} for s,role in zip(slides[:8],['Vision through a concrete failure','Scope of learned corrections','Current conditioned-policy setup','Completed visual mass result','Completed simulation integration','Proposed failure-variable study','Proposed estimate-refinement pilot','Longer-term research agenda'])],'mediaMapping':{'visual mass chart':'keep exact asset and metric values','initial RGB and final robot photo':'keep as actual integration evidence','new red cube/gripper schematics':'illustrative only, explicitly labeled'},'style':'Existing Arial, warm off-white, navy/teal; no container boxes; editable vector diagrams','notes':'Remove notes from eight main slides; add none','appendix':'Preserve unrelated draft text; mark skipped','originalSnapshot':'raw-before.json'},indent=2))
print({'requests':len(req),'mainSlides':8,'newSlides':0,'addedNotes':0})
