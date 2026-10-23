from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'raw-before.json').read_text())['structuredContent']
slides=raw['slides']
elements={e['objectId']:e for s in slides for e in s['pageElements']}
requests=[]
INK='183139';GRAY='62747A';TEAL='087F7B'
def add(t,**kw):requests.append({t:kw})
def rgb(c):return {k:int(c[i:i+2],16)/255 for k,i in [('red',0),('green',2),('blue',4)]}
def pt(d):return d['magnitude']/12700 if d['unit']=='EMU' else d['magnitude']
def move(o,x,y,w,h):
 e=elements[o]
 add('updatePageElementTransform',objectId=o,applyMode='ABSOLUTE',transform={'scaleX':w/pt(e['size']['width']),'scaleY':h/pt(e['size']['height']),'translateX':x,'translateY':y,'unit':'PT'})
def format_text(o,size,color=INK,bold=False,align='START'):
 add('updateTextStyle',objectId=o,textRange={'type':'ALL'},style={'fontFamily':'Arial','fontSize':{'magnitude':size,'unit':'PT'},'bold':bold,'foregroundColor':{'opaqueColor':{'rgbColor':rgb(color)}}},fields='fontFamily,fontSize,bold,foregroundColor,link')
 add('updateParagraphStyle',objectId=o,textRange={'type':'ALL'},style={'alignment':align,'lineSpacing':110,'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'},'indentStart':{'magnitude':0,'unit':'PT'},'indentEnd':{'magnitude':0,'unit':'PT'},'indentFirstLine':{'magnitude':0,'unit':'PT'}},fields='alignment,lineSpacing,spaceAbove,spaceBelow,indentStart,indentEnd,indentFirstLine')
def replace(o,t,size=None,color=None,bold=None):
 add('deleteText',objectId=o,textRange={'type':'ALL'})
 add('insertText',objectId=o,insertionIndex=0,text=t)
 if size is not None:format_text(o,size,color or INK,bool(bold))
def text(page,o,t,x,y,w,h,size=14.4,color=INK,bold=False):
 if o in elements:replace(o,t)
 else:
  add('createShape',objectId=o,shapeType='TEXT_BOX',elementProperties={'pageObjectId':page,'size':{'width':{'magnitude':w+14.4,'unit':'PT'},'height':{'magnitude':h+14.4,'unit':'PT'}},'transform':{'scaleX':1,'scaleY':1,'translateX':x-7.2,'translateY':y-7.2,'unit':'PT'}})
  add('insertText',objectId=o,insertionIndex=0,text=t)
 if o in elements:move(o,x-7.2,y-7.2,w+14.4,h+14.4)
 format_text(o,size,color,bold)
def orig(s,n):return f'pi_simple_20261022_s{s:02d}_original_{n:03d}'

# 1: show the research goal before the current implementation.
replace(orig(1,3),'How can robots adapt existing skills\nto unfamiliar physical conditions?')
replace(orig(1,4),'Build and refine physical understanding through interaction.')
replace(orig(1,13),'A policy that can grasp and move\nacross variations of the same task.')
replace(orig(1,75),'Physical understanding')
replace(orig(1,76),'Estimate relevant properties.\nRefine them from observed outcomes.')
replace(orig(1,91),'Research focus: learning from interaction, including failures and unexpected responses.')

# 2: preserve the existing state/context-to-policy diagram and clarify its role.
replace(orig(2,94),'Enabling policy: state + physical context')
replace(orig(2,95),'Train across physical conditions so the policy can use\nenvironmental estimates to adapt its actions.')
replace(orig(2,104),'Known during training\nEstimated during deployment\nExamples: mass, friction')
move(orig(2,104),41.85,256.95,245.25,63)
replace(orig(2,146),'Enabling assumption: the policy can perform the required behavior under the tested conditions.',12,GRAY)

# 3: completed result stays intact; fix the material-scope contradiction.
replace(orig(3,150),'Initial visual mass estimation')
replace(orig(3,151),'Completed baseline: predict mass from an initial RGB image.\nCubes vary in size; material and density are fixed.')
replace(orig(3,158),'Held-out error')
add('updateShapeProperties',objectId=orig(3,155),shapeProperties={'shapeBackgroundFill':{'propertyState':'NOT_RENDERED'},'outline':{'propertyState':'NOT_RENDERED'}},fields='shapeBackgroundFill,outline')
# The memo is retained in notes; remove the raw repository path from the slide.
add('deleteObject',objectId=orig(3,166))

# 4: preserve actual images, numeric estimate, native policy graphic and feedback.
replace(orig(4,169),'Current pipeline in simulation')
replace(orig(4,170),'One initial image supplies mass to the policy; execution uses state and force feedback.')
replace('pi_pipeline_v2_text_051','Current implementation: the estimate and model weights stay fixed throughout execution.')

# 5: keep the user's text-and-arrow loop; no boxes or stage containers.
p5=slides[4]['objectId']
replace('pi_next_steps_20261022_exemplar_00','Next: refine understanding through interaction')
replace('pi_next_steps_20261022_exemplar_01','Proposed: use execution outcomes to improve task-relevant physical estimates.')
text(p5,'pi_reframe_known_title','First: refine known factors',49,235,290,27,16.65,INK,True)
text(p5,'pi_reframe_known_body','Use interaction to correct estimates\nof properties such as mass and friction.',49,274,290,58)
text(p5,'pi_reframe_unknown_title','Later: investigate missing factors',386,235,298,27,16.65,INK,True)
text(p5,'pi_reframe_unknown_body','Recognize when current estimates\ncannot explain the observed outcome.',386,274,298,58)
text(p5,'pi_reframe_open_question','Open question: what evidence should trigger an update, and what should change?',36,355,648,26,13.5)

# 6: make the proposed first test concrete, with the same two-column hierarchy.
p6=slides[5]['objectId'];pre='h437c0d080b9bf084_0_'
text(p6,pre+'15','First test: does estimate refinement help?',36,44,648,32,19.35,INK,True)
text(p6,pre+'16','Proposed simulation study: one object family, varied mass, fixed policy.',36,82,648,25,13.5,GRAY)
move(pre+'21',49,141,12,12);move(pre+'24',386,141,12,12)
text(p6,pre+'22','Controlled setup',70,134,270,28,17.55,INK,True)
text(p6,pre+'25','Matched comparisons',407,134,277,28,16.65,INK,True)
text(p6,pre+'23','Keep shape, appearance and friction fixed.\nCheck policy performance with true mass.\nCheck whether interaction reveals mass.',49,177,290,130)
text(p6,pre+'26','Initial estimate held fixed\nEstimate updated from interaction\nTrue mass supplied',386,177,298,130)
text(p6,pre+'27','Measure estimation error and task success under matched interaction budgets.',36,326,648,27,13.5)
text(p6,'pi_reframe_later_work','Later: CREST, broader materials and movement conditions, and learning across experience.',36,365,648,27,13.5)

notes=[
 'Updated research framing: the broad goal is deployment adaptation of an existing manipulation skill. For this study, physical understanding is operationalized as estimates of task-relevant physical properties. Movement capability is an enabling condition; the research focus is how observation and interaction improve the physical context available to the policy. Successes, failures and unexpected responses are evidence, not unique causal labels. Initial mass estimation is the first implementation. Recognizing previously unmodeled causes is a longer-term question, not an achieved result.',
 'Enabling capability: a controller must first be able to succeed in the tested physical conditions, and its behavior should depend usefully on the supplied context. RL training alone does not guarantee this. The planned height-generalization study remains future work: train across initial object heights and evaluate held-out heights. Separate interpolation from extrapolation and keep context accuracy distinct from policy capability.',
 'Completed visual-mass baseline: one material, fixed density/friction/camera, size variation. MAE is 2.76 g on 12 held-out sizes and 48 images, against a constant baseline of 106.37 g. This supports initial estimation in the controlled distribution, not adaptation during deployment or arbitrary-material mass inference. Source memo retained from the original slide: https://github.com/Spadeyache/adaptability ; runs/visual_mass/initial_rgb_mass/model/metrics.json and predictions.png.',
 'Current pipeline is a completed integration demonstration, not a learned online update. One raw initial RGB image is passed through the frozen mass estimator before contact. Mass is converted to supplied weight for the frozen policy. The policy receives robot/object state and finger normal-compression signals throughout execution. Both model weights and mass estimate remain fixed. Representative 5 cm cube: 125 g actual, 121.24 g estimated, 1.19 N supplied; 50 steps. Ground-truth mass is for evaluation only.',
 'Proposed research direction, not implemented: use observations and execution outcomes to revise task-relevant physical beliefs. Updating a current estimate is state/parameter inference; it need not change estimator weights. A shared learned updater could maintain a separate evolving belief for each encounter. Improving shared estimator weights across experiences is a distinct later choice. When current properties cannot explain an outcome, detecting model inadequacy, identifying a useful additional factor, and learning a correction are separate longer-term problems. An unexpected outcome alone does not prove a novel failure cause.',
 'Proposed first controlled test: one cube geometry and appearance, fixed friction/pose and a frozen policy. Vary actual mass and initial estimation error. Before training an updater, check that the policy is capable under the chosen masses and that accurate supplied mass usefully changes performance. Check that permitted action/observation histories distinguish mass; finger normal compression is not vertical load, and failure alone does not identify mass. Compare fixed initial estimate, interaction-updated estimate and true-mass reference under matched probing and task budgets. True mass is an information reference, not a guaranteed performance ceiling. Keep evaluation mass out of deployment features. See presentations/interaction_adaptation_experiment.md for the proposed study. Related reading retained from the original draft: https://arxiv.org/abs/2109.09180 (lifelong multi-task RL, background reading rather than the estimator-update method).'
]
for s,n in zip(slides[:6],notes):
 o=s['slideProperties']['notesPage']['notesProperties']['speakerNotesObjectId']
 add('insertText',objectId=o,insertionIndex=0,text=n+'\n\nEarlier notes retained below:\n')

(OUT/'requests.json').write_text(json.dumps(requests,separators=(',',':')))
(OUT/'construction-plan.json').write_text(json.dumps({'action':'Edit existing slides 1–6 in place; preserve slide order and draft slides 7–8','designExemplar':slides[0]['objectId'],'design':'Preserve warm off-white, navy/teal, Arial hierarchy, simple text columns and arrows. No boxes, header or footer.','mediaMapping':{'slide3 chart':'keep exact existing evidence','slide3 decorative frame':'hide fill and outline','slide4 initial/final photos':'keep','slide4 policy diagram':'keep'},'narrative':['Overall goal and physical-understanding focus','Enabling conditioned-policy capability','Completed initial-estimation result','Completed fixed-estimate simulation integration','Proposed refinement and longer-term missing factors','First controlled experiment'],'sourceNotes':'Preserved; revised framing prepended'},indent=2))
print({'requests':len(requests),'slidesEdited':6,'newBoxes':0,'newSlides':0})
