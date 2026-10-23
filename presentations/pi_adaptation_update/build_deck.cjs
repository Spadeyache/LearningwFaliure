/* Rebuild the editable deck, vector previews, and PDF with the bundled runtime. */
const fs = require('fs');
const path = require('path');
const deps = 'C:/Users/magic/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/';
const pptxgen = require(deps + 'pptxgenjs');
const { chromium } = require(deps + 'playwright');
const sharp = require(deps + 'sharp');
const { PDFDocument } = require(deps + 'pdf-lib');

const OUT = __dirname;
const W = 1600, H = 900, SCALE = 120;
const C = {
  paper: 'F6F4EF', white: 'FFFFFF', ink: '183139', muted: '62747A',
  teal: '087F7B', pale: 'E1EFEB', teal2: 'A5CBC0', line: 'D8DFD9',
  coral: 'C86B52', blush: 'F3E5DD', gray: 'E8ECE8', arm: '93A5AA',
  dark: '22434A', cube: 'DFC28E', cubeSide: 'BA9A61', yellow: 'F4E8CE',
};
const slides = [];
let s;
const esc = v => String(v).replace(/[&<>\"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[ch]));
function rect(x,y,w,h,fill=C.white,r=0,stroke=null,sw=1,dash=false) {
  s.items.push({kind:'rect',x,y,w,h,fill,r,stroke,sw,dash});
}
function ellipse(x,y,w,h,fill=C.ink,stroke=null,sw=1) {
  s.items.push({kind:'ellipse',x,y,w,h,fill,stroke,sw});
}
function line(x1,y1,x2,y2,color=C.line,sw=2,dash=false,arrow=false) {
  s.items.push({kind:'line',x1,y1,x2,y2,color,sw,dash,arrow});
}
function text(str,x,y,w,size=30,color=C.ink,weight=400,opts={}) {
  const lines = str.split('\n');
  const lh = opts.lh || Math.round(size * 1.22);
  s.items.push({kind:'text',str,x,y,w,h:opts.h || lines.length*lh+3,size,color,weight,lh,align:opts.align||'left', ...opts});
}
function pill(str,x,y,w,fill=C.pale,color=C.teal,size=20) {
  rect(x,y,w,38,fill,19);
  text(str,x,y+6,w,size,color,700,{align:'center',h:27});
}
function arrow(x1,y1,x2,y2,color=C.muted,dash=false,sw=3) {
  line(x1,y1,x2,y2,color,sw,dash,true);
}
function base(kicker,title,subtitle='',opts={}) {
  s={items:[],notes:'',title}; slides.push(s);
  rect(0,0,W,H,C.paper);
  rect(76,45,32,5,C.teal,2);
  text(kicker.toUpperCase(),124,34,1320,19,C.teal,700,{lh:25});
  text(title,76,96,1450,opts.titleSize||59,C.ink,700,{lh:opts.titleLH||67});
  if(subtitle) text(subtitle,80,opts.subY||188,1430,30,C.muted,400,{lh:39});
  line(80,844,1520,844,C.line,1.5);
  text('ROBOT ADAPTATION  /  PI RESEARCH UPDATE',80,862,1230,16,C.muted,400,{h:23});
  text(String(slides.length).padStart(2,'0')+' / 08',1390,859,130,19,C.muted,700,{align:'right',h:28});
  return s;
}
function circleLabel(str,x,y,fill=C.teal,color=C.white) {
  ellipse(x,y,40,40,fill); text(str,x,y+6,40,23,color,700,{align:'center',h:29});
}
function vector(x,y,w=190,h=58,highlight=true) {
  const gap=9,cell=(w-gap*3)/4;
  for(let i=0;i<4;i++) {
    rect(x+i*(cell+gap),y,cell,h,highlight?C.pale:C.gray,7);
    rect(x+i*(cell+gap)+cell*.25,y+h*(.23+.10*(i%3)),cell*.5,h*(.55-.1*(i%3)),highlight?C.teal:C.arm,4);
  }
}
function neural(x,y,w=150,h=110) {
  const columns=[3,4,3];
  for(let c=0;c<2;c++) for(let a=0;a<columns[c];a++) for(let b=0;b<columns[c+1];b++) {
    const ay=y+(a+.5)*h/columns[c],by=y+(b+.5)*h/columns[c+1];
    line(x+c*w/2,ay,x+(c+1)*w/2,by,C.teal2,1.5);
  }
  columns.forEach((n,c)=>{for(let a=0;a<n;a++) ellipse(x+c*w/2-9,y+(a+.5)*h/n-9,18,18,C.dark);});
}
function miniCondition(x,y,w=108,h=94,idx=0) {
  rect(x,y,w,h,C.white,12,C.line,1);
  rect(x+15,y+15,27,27,C.cube,4);
  line(x+13,y+46,x+47,y+46,C.arm,2);
  for(let b=0;b<3;b++) {
    rect(x+59,y+18+b*17,w-72,5,C.gray,2);
    rect(x+59,y+18+b*17,(w-72)*(.24+((idx*2+b)%5)*.16),5,b===0?C.teal:C.arm,2);
  }
  text(String(idx+1).padStart(2,'0'),x+15,y+h-31,w-30,16,C.muted,700,{h:23});
}

// Shared robot schematic. All parts become editable PowerPoint shapes.
function robotScene(x,y,w=400,h=265,phase='lift',accent=C.teal) {
  const scale=Math.min(w/400,h/265), ox=x+(w-400*scale)/2, oy=y+(h-265*scale)/2;
  const R=(a,b,c,d,fill,r=0,stroke=null,sw=1)=>rect(ox+a*scale,oy+b*scale,c*scale,d*scale,fill,r*scale,stroke,sw*scale);
  const L=(a,b,c,d,color,sw=3,dash=false,ar=false)=>line(ox+a*scale,oy+b*scale,ox+c*scale,oy+d*scale,color,sw*scale,dash,ar);
  const E=(a,b,c,d,fill,stroke=null,sw=1)=>ellipse(ox+a*scale,oy+b*scale,c*scale,d*scale,fill,stroke,sw*scale);
  const gx=293, gy=phase==='grasp'?145:phase==='approach'?85:65;
  const cubeY=phase==='lift'?102:180;
  L(196,222,390,222,C.arm,4);
  L(215,224,215,255,C.line,5);L(374,224,374,255,C.line,5);
  R(15,224,80,18,C.dark,4); R(40,194,31,30,C.arm,4);
  L(55,196,106,79,C.arm,20);L(106,79,209,59,C.arm,20);L(209,59,gx,gy-25,C.arm,16);
  E(39,180,32,32,C.dark);E(90,63,32,32,C.dark);E(196,46,26,26,C.dark);
  E(47,188,16,16,C.paper);E(99,72,14,14,C.paper);E(203,53,12,12,C.paper);
  L(gx,gy-25,gx,gy,C.dark,12);
  R(gx-36,gy,72,17,C.dark,5);
  const gap=phase==='approach'?48:28;
  R(gx-gap-10,gy+13,12,65,C.arm,3);R(gx+gap-2,gy+13,12,65,C.arm,3);
  R(gx-gap-10,gy+67,20,11,C.dark,3);R(gx+gap-10,gy+67,20,11,C.dark,3);
  R(gx-20,cubeY,40,40,phase==='slip'?C.coral:C.cube,5);
  R(gx+10,cubeY,10,40,phase==='slip'?C.coral:C.cubeSide,2);
  L(gx-20,cubeY+12,gx+20,cubeY+12,phase==='slip'?C.blush:C.yellow,1.4);
  if(phase==='lift') L(358,177,358,114,accent,4,false,true);
  if(phase==='approach') L(358,107,358,168,accent,4,false,true);
  if(phase==='grasp') {
    L(gx-65,197,gx-39,197,accent,3,false,true);
    L(gx+65,197,gx+39,197,accent,3,false,true);
  }
  if(phase==='slip') {
    R(gx-20,102,40,40,null,5,C.coral,2);
    L(358,128,358,190,C.coral,4,true,true);
  }
}
function camera(x,y,w=110) {
  rect(x,y+13,w,65,C.dark,10);
  rect(x+16,y,w*.37,23,C.dark,5);
  ellipse(x+w*.46,y+23,43,43,C.pale);
  ellipse(x+w*.46+10,y+33,23,23,C.teal);
  ellipse(x+12,y+26,10,10,C.teal2);
}


const ROOT = path.resolve(OUT,'../..');
const RESULT = path.join(ROOT,'runs/deployment/20261022_014201_067220');
function picture(file,x,y,w,h) {
  s.items.push({kind:'image',path:file,data:fs.readFileSync(file).toString('base64'),x,y,w,h});
}
function evidenceSource(str) {text(str,80,813,1440,16,C.muted,400,{h:23});}
function heightScene(x,y,w=400,h=270,level=0) {
  const sc=Math.min(w/400,h/280),ox=x+(w-400*sc)/2,oy=y+(h-280*sc)/2;
  const R=(a,b,c,d,fill,r=0)=>rect(ox+a*sc,oy+b*sc,c*sc,d*sc,fill,r*sc);
  const L=(a,b,c,d,color,sw=3,dash=false,ar=false)=>line(ox+a*sc,oy+b*sc,ox+c*sc,oy+d*sc,color,sw*sc,dash,ar);
  const E=(a,b,c,d,fill)=>ellipse(ox+a*sc,oy+b*sc,c*sc,d*sc,fill);
  const supportY=244-level*41,cubeY=supportY-40,gx=297,gy=cubeY-36;
  L(4,264,395,264,C.line,2,true);
  R(14,244,80,18,C.dark,4);R(39,215,31,29,C.arm,4);
  L(55,215,108,85,C.arm,19);L(108,85,202,66,C.arm,19);L(202,66,gx,gy-24,C.arm,15);
  E(39,199,32,32,C.dark);E(92,69,32,32,C.dark);E(189,53,26,26,C.dark);
  E(47,207,16,16,C.paper);E(101,78,14,14,C.paper);E(196,60,12,12,C.paper);
  L(gx,gy-24,gx,gy,C.dark,11);R(gx-35,gy,70,17,C.dark,4);
  R(gx-38,gy+15,11,63,C.arm,3);R(gx+27,gy+15,11,63,C.arm,3);
  R(gx-38,gy+67,20,11,C.dark,2);R(gx+18,gy+67,20,11,C.dark,2);
  R(gx-20,cubeY,40,40,C.cube,4);R(gx+10,cubeY,10,40,C.cubeSide,2);
  L(221,supportY,384,supportY,C.arm,4);L(237,supportY+3,237,264,C.line,5);L(369,supportY+3,369,264,C.line,5);
}

// 1 — Idea: two necessary components, both stated as hypotheses to test.
base('01 · Research idea','Adaptation needs capability and information','How can a robot execute a task in a situation it did not encounter during training?',{titleSize:57});
rect(80,288,690,421,C.white,22);rect(830,288,690,421,C.pale,22);
circleLabel('1',110,318,C.dark);text('Movement capability',170,318,560,39,C.ink,700);
text('Learn how to grasp and move\nacross variations of the same task.',113,396,600,32,C.ink,400,{lh:43});
neural(156,533,170,112);arrow(376,588,448,588,C.arm,false,3);robotScene(484,508,228,153,'lift');
circleLabel('2',860,318);text('Environment interpretation',920,318,560,37,C.ink,700);
text('Estimate the current conditions\nso the policy can use suitable actions.',863,396,600,32,C.ink,400,{lh:43});
camera(915,551,108);arrow(1070,588,1145,588,C.teal,false,3);vector(1190,558,239,69,true);
text('Working hypothesis: generalizable behavior and useful environmental context support adaptation.',80,756,1440,30,C.ink,400,{lh:39});
s.notes='We investigate how a robot can handle a deployment situation it did not encounter during training. The idea has two components. First, the controller needs a repertoire of grasping and movement behavior that generalizes within a task. Second, the system needs a useful interpretation of its current environment so that the conditioned policy can produce appropriate commands. These are research hypotheses, not guarantees provided by reinforcement learning. The task remains pick and lift with a consistent top-down grasp strategy. This framing follows the latest proposal: policy generalization is now an explicit enabling part of the study, while initial environment estimation remains a separate component.';

// 2 — Mechanism: separate training of behavior from supplying context.
base('02 · Proposed setup','An RL policy conditioned on environment','Standard state describes the robot and task; environmental parameters describe current conditions.',{titleSize:57});
rect(80,304,500,158,C.white,20);
text('Robot + task state',109,330,443,33,C.ink,700);
text('Joints, gripper pose, task state',109,391,443,27,C.muted);
rect(80,506,500,158,C.pale,20);
text('Environmental parameters',109,532,443,32,C.teal,700);
text('Known in training;\nestimated at deployment',109,587,443,27,C.teal,400,{lh:33});
arrow(603,385,689,430,C.arm,false,3);arrow(603,583,689,518,C.teal,false,3);
rect(725,376,350,215,C.white,22,C.line,1.5);
neural(818,399,165,105);text('RL policy',749,536,302,34,C.ink,700,{align:'center'});
arrow(1100,483,1164,483,C.arm,false,3);
rect(1196,407,324,155,C.gray,20);
text('Grasp and move\nactions',1219,442,278,33,C.ink,700,{align:'center',lh:43});
text('Training: learn policy weights from reward. Deployment test: keep those weights fixed.',80,721,1440,30,C.ink,400,{lh:39});
text('Assumption to test: varied training produces a policy capable of executing at held-out heights.',80,786,1440,26,C.muted);
s.notes='We assume an RL framework. The policy receives standard robot and task state plus a compact set of environmental parameters, and learns grasping and movement commands from task reward. During simulation training, selected environmental values can be supplied from the simulator. During estimated-context evaluation, the corresponding values must come from the estimator. RL is a method of training the controller; successful generalization must still be measured. Selected context variables could be guided by the existing CREST workflow, but no completed CREST selection is claimed here. The current policy has 45 state values including object pose, relative geometry, supplied weight, and finger-force observations. If the future estimator predicts height or pose, true copies and derived versions of those quantities must not bypass that estimator.';

// 3 — Measured finding: controlled mass prior.
base('03 · Finding 1 · Completed','A controlled visual mass estimate works','Fixed-density cubes provide a visible size-to-mass relationship.',{titleSize:57});
rect(80,286,1037,378,C.white,22);
picture(path.join(ROOT,'runs/visual_mass/initial_rgb_mass/model/predictions.png'),99,310,999,316);
rect(1152,286,368,378,C.pale,22);
text('TEST MASS ERROR',1177,314,318,20,C.teal,700);
text('2.76 g',1177,355,318,65,C.ink,700);
text('Mean absolute error',1177,438,318,25,C.muted);
line(1177,490,1495,490,C.teal2,1.5);
text('Constant baseline',1177,518,318,25,C.muted);
text('106.37 g',1177,561,318,43,C.ink,700);
text('12 held-out sizes / 48 test images',80,704,1440,32,C.ink,700);
text('Scope: one material, fixed density and friction, fixed camera. This tests interpolation over size.',80,763,1440,26,C.muted);
evidenceSource('Evidence: runs/visual_mass/initial_rgb_mass/model/metrics.json and predictions.png');
s.notes='Completed evidence: the saved initial-image CNN achieved test mean absolute mass error of 2.760891 g and RMSE 4.434443 g on 12 held-out cube sizes and 48 images. The constant training-mean predictor had 106.373742 g test MAE. The complete dataset contains 96 sizes and 384 images; all views of one object stay in one split. The model checkpoint was selected by validation loss, not test results. This is a controlled visual size-to-mass prior: density, material, friction, camera and background are fixed. It does not establish general mass inference for identical-looking objects of different densities. It is not a height-estimation result. Data source: runs/visual_mass/initial_rgb_mass/model/metrics.json. Plot: runs/visual_mass/initial_rgb_mass/model/predictions.png.';

// 4 — Measured finding: integrated execution, not a comparative benefit.
base('04 · Finding 2 · Completed','The full pipeline runs in simulation','Initial RGB image → mass estimate → supplied policy input → pick-and-lift execution.',{titleSize:57});
const actual=[64,125,216],predicted=[62.32,121.24,212.45],sizes=[4,5,6];
for(let i=0;i<3;i++) {
  const x=80+i*495;
  rect(x,282,450,400,C.white,22);
  text(`${sizes[i]} cm cube`,x+25,306,400,31,C.ink,700,{align:'center'});
  picture(path.join(RESULT,`episode_${String(i).padStart(3,'0')}`,'final.png'),x+116,358,218,218);
  text(`${actual[i].toFixed(1)} g → ${predicted[i].toFixed(2)} g`,x+25,595,400,29,C.teal,700,{align:'center'});
  text('actual mass → predicted mass',x+25,639,400,22,C.muted,400,{align:'center'});
}
rect(80,713,1440,61,C.pale,15);
text('3 configured trials · 3 final successes · 50 actions per trial',100,728,1400,31,C.ink,700,{align:'center'});
text('One seed per size. Integration is demonstrated; estimation benefit and unseen-height adaptation remain untested.',80,781,1440,23,C.muted);
evidenceSource('Evidence: runs/deployment/20261022_014201_067220/summary.json, manifest.json, and final frames');
s.notes='Completed integration demonstration: three configured cases, one seed per cube size, each completed the full 50-action, 2.5-second rollout and ended with task success and a grasp. The 4, 5 and 6 cm cubes had masses 64, 125 and 216 g; predicted masses were approximately 62.32, 121.24 and 212.45 g. Across the three trials the mass MAE was 2.996986 g. The estimate remained fixed throughout each episode. Final continuous success lasted about 2.10, 2.10 and 2.05 simulated seconds. These images are actual saved simulation frames. This establishes that the components can run together. Three trials are not a reliability estimate, and there is no matched true-estimate-versus-fixed-estimate benefit comparison here. The run used a saved frozen-movement/independent-strength v1 checkpoint, not a newly trained policy that generalizes over initial object elevation. Source: runs/deployment/20261022_014201_067220/summary.json and manifest.json.';

// 5 — New policy experiment, explicitly planned.
base('05 · Planned policy experiment','Train pick and lift across object heights','Vary initial object elevation relative to the arm while keeping the task and grasp strategy consistent.',{titleSize:56});
pill('TO BE DONE',1266,35,254,C.blush,C.coral,18);
['Training height h1','Training height h2','Training height h3'].forEach((label,i)=>{
  const x=80+i*495;
  rect(x,300,450,399,C.white,22);
  text(label,x+25,326,400,29,C.ink,700,{align:'center'});
  heightScene(x+20,399,410,273,i);
});
text('The robot base stays fixed. The object starts at different elevations.',80,740,1440,30,C.ink);
text('First height study: control mass, friction, object geometry, and required lift clearance.',80,794,1440,26,C.muted);
s.notes='This is proposed work and has not yet been done. Train a pick-and-lift RL policy across initial object elevations relative to a fixed robot base, for example by changing the height of a physically supported object. The three symbolic heights are schematic, not a chosen numerical training schedule. Height here means the initial object/support elevation, not merely the final lift target. Existing training varies a floating goal height; that does not establish training over initial object elevations. Keep mass, friction and geometry controlled in the first height study and keep required lift clearance above the supporting surface consistent. Define reachability and collision validity before training. The aim is to establish a controller that can execute the same task from multiple initial heights. Generalization to held-out heights remains an empirical question.';

// 6 — New deployment test: a held-out height, estimator target kept explicit.
base('06 · Planned deployment test','Deploy at a held-out initial height','Freeze the trained policy and provide environmental context estimated from deployment observations.',{titleSize:57});
text('HEIGHT SPLIT: SCHEMATIC',80,277,1400,19,C.muted,700);
rect(651,321,218,119,C.blush,15,null,1);
line(139,366,1470,366,C.arm,3);
const hx=[184,469,1075,1410];
hx.forEach((x,i)=>{ellipse(x-9,357,18,18,C.dark);text('h'+(i+1),x-55,401,110,25,C.muted,700,{align:'center'});});
ellipse(749,355,22,22,C.coral);text('held-out height',657,280,206,24,C.coral,700,{align:'center'});
text('h*',706,401,108,27,C.coral,700,{align:'center'});
const bx=[80,464,848,1232], bw=288;
const labels=['Initial\nobservations','Estimator\n(selected context)','Trained\npolicy','Pick-and-lift\nexecution'];
bx.forEach((x,i)=>{
  rect(x,532,bw,151,i===1?C.pale:C.white,18,i===1?C.teal:null,1.5);
  text(labels[i],x+18,569,bw-36,29,i===1?C.teal:C.ink,700,{align:'center',lh:38});
  if(i<3) arrow(x+bw+18,608,bx[i+1]-18,608,C.arm,false,2.5);
});
text('Report within-range held-out heights separately from heights beyond the training range.',80,734,1440,29,C.ink);
text('Current estimator: mass. Estimator target for the height study still needs to be specified.',80,792,1440,26,C.muted);
s.notes='The proposed deployment test uses initial object heights that are excluded from policy training. The number line is a schematic of within-range held-out evaluation, not a result or a chosen numeric schedule. A withheld height interval is stronger than treating a previously unsampled floating-point value as meaningfully novel. Evaluate outside-range extrapolation separately. Keep policy and estimator weights fixed during evaluation and record what heights each model saw during training. Use initial observations to estimate the selected context. The present estimator predicts mass, not object height. It is still open whether the new estimator should predict height, physical properties while height tests policy generalization, or both. If it predicts height, remove simulator-true object heights and any derived height features from deployment policy inputs. If it predicts mass only, height generalization and mass-estimation quality are separate factors and should be described as such.';

// 7 — Proposed rules, no fabricated evaluation outcomes.
base('07 · Proposed test rules','Separate policy capability from estimation','At each held-out height, compare the same frozen policy under three context inputs.',{titleSize:57});
rect(80,278,1440,303,C.white,20);
rect(80,278,1440,57,C.gray,15);
text('CONTEXT INPUT',107,296,450,20,C.muted,700);
text('QUESTION',613,296,867,20,C.muted,700);
const rows=[
 ['True context','Can the policy execute at the unseen height?'],
 ['Estimated context','How much performance is lost to estimation?'],
 ['Fixed / incorrect context','Does useful context improve execution?'],
];
rows.forEach((row,i)=>{
  const y=352+i*77;
  if(i) line(105,y-13,1495,y-13,C.line,1);
  text(row[0],107,y,460,29,i===1?C.teal:C.ink,700);
  text(row[1],613,y,867,29,C.ink);
});
const rules=[
 [80,624,'1','Reserve test heights before training.'],
 [830,624,'2','Match physical scenes and starts.'],
 [80,731,'3','Freeze models; predefine held success.'],
 [830,731,'4','Remove true copies of estimated inputs.'],
];
rules.forEach(([x,y,n,str])=>{circleLabel(n,x,y,C.teal);text(str,x+59,y+5,631,26,C.ink,400,{lh:34});});
s.notes='Proposed protocol. First define training and test height sets or held-out bands. Do not tune on final test episodes. At each held-out height and matched physical setting, run the same frozen policy with true selected context, estimated context, and a fixed or deliberately incorrect context. Match seeds and robot starts across these context conditions. True context tests the trained policy’s capability without that estimation error; compare estimated context against it to expose the estimation gap. Fixed or incorrect context tests whether useful conditioning matters. Use repeated starts and report counts, success rates with uncertainty, estimation error, grasp loss and relevant force or timing metrics. Set the goal tolerance, required support-relative clearance, and final hold window before evaluation. Ensure estimated-context deployment observations cannot also expose simulator-true copies of the estimated variables, including derived relative-position values when height or pose is estimated. The existing state interface includes such geometry, so this must be addressed if height is the estimator target. No evaluation result is claimed on this slide.';

// 8 — Status and a useful diagnostic for the PI discussion.
base('08 · Status and next step','What we can say now—and test next','Current evidence supports the components; the proposed comparison must establish adaptation.',{titleSize:57});
rect(80,284,690,344,C.pale,22);rect(830,284,690,344,C.white,22);
pill('DEMONSTRATED',111,313,265,C.teal,C.white,19);pill('NEXT EXPERIMENT',861,313,300,C.gray,C.muted,19);
text('Controlled image-to-mass estimate',112,392,620,30,C.ink,700);
text('2.76 g MAE on held-out cube sizes',112,438,620,26,C.muted);
text('Estimator-to-policy integration',112,503,620,30,C.ink,700);
text('Three configured full-horizon successes',112,549,620,26,C.muted);
text('Train across initial object heights',862,392,620,30,C.ink,700);
text('Establish policy capability with true context',862,438,620,26,C.muted);
text('Evaluate estimated context at held-out heights',862,503,620,28,C.ink,700);
text('Compare against true and fixed inputs',862,549,620,26,C.muted);
text('If true context fails: inspect policy capability and task feasibility.',80,683,1440,29,C.ink,700);
text('If true context succeeds but estimates fail: inspect estimation and policy sensitivity.',80,734,1440,29,C.ink,700);
text('Later stage: revise environmental estimates through interaction, success, and failure.',80,795,1440,26,C.muted);
s.notes='The defensible current claims are a controlled visual mass prior and a working integrated simulation pipeline for three configured cases. Neither proves that estimates improve execution relative to nominal inputs, nor that an RL policy generalizes over unseen initial object heights. The next experiment is to train across initial object heights, establish execution capability using correct context, and compare estimated and fixed context on matched held-out cases. If correct context fails, investigate policy generalization, task feasibility and control limitations before attributing failures to the estimator. If correct context succeeds but estimated context fails, investigate estimation errors and policy sensitivity to those errors. This is a diagnostic guide, not a unique causal identification claim. Later work can update estimates from interaction. For PI discussion, specify the estimator target, height split and evaluation criteria before running the proposed study.';


function svgFor(slide) {
  const out=[];
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L9,4 L0,8" fill="none" stroke="context-stroke" stroke-width="2" stroke-linejoin="round"/></marker></defs>`);
  slide.items.forEach(o=>{
    if(o.kind==='rect') out.push(`<rect x="${o.x}" y="${o.y}" width="${o.w}" height="${o.h}" rx="${o.r}" fill="${o.fill?'#'+o.fill:'none'}"${o.stroke?` stroke="#${o.stroke}" stroke-width="${o.sw}"`:''}${o.dash?' stroke-dasharray="9 7"':''}/>`);
    if(o.kind==='ellipse') out.push(`<ellipse cx="${o.x+o.w/2}" cy="${o.y+o.h/2}" rx="${o.w/2}" ry="${o.h/2}" fill="${o.fill?'#'+o.fill:'none'}"${o.stroke?` stroke="#${o.stroke}" stroke-width="${o.sw}"`:''}/>`);
    if(o.kind==='line') {
      out.push(`<line x1="${o.x1}" y1="${o.y1}" x2="${o.x2}" y2="${o.y2}" stroke="#${o.color}" stroke-width="${o.sw}" stroke-linecap="round"${o.dash?' stroke-dasharray="9 7"':''}/>`);
      if(o.arrow) {
        const a=Math.atan2(o.y2-o.y1,o.x2-o.x1),l=11+o.sw*.9,b=6+o.sw*.5;
        const xx=o.x2-l*Math.cos(a),yy=o.y2-l*Math.sin(a);
        out.push(`<path d="M${xx-b*Math.sin(a)},${yy+b*Math.cos(a)} L${o.x2},${o.y2} L${xx+b*Math.sin(a)},${yy-b*Math.cos(a)}" fill="none" stroke="#${o.color}" stroke-width="${o.sw}" stroke-linecap="round" stroke-linejoin="round"/>`);
      }
    }
    if(o.kind==='image') out.push(`<image x="${o.x}" y="${o.y}" width="${o.w}" height="${o.h}" href="data:image/png;base64,${o.data}" preserveAspectRatio="xMidYMid meet"/>`);
    if(o.kind==='text') {
      const anchor=o.align==='center'?'middle':o.align==='right'?'end':'start';
      const xx=o.align==='center'?o.x+o.w/2:o.align==='right'?o.x+o.w:o.x;
      out.push(`<text x="${xx}" y="${o.y+o.size*.91}" fill="#${o.color}" font-family="Arial, sans-serif" font-size="${o.size}" font-weight="${o.weight}" text-anchor="${anchor}" data-box-x="${o.x}" data-box-y="${o.y}" data-box-w="${o.w}" data-box-h="${o.h}">${o.str.split('\n').map((t,i)=>`<tspan x="${xx}" dy="${i?o.lh:0}">${esc(t)}</tspan>`).join('')}</text>`);
    }
  });
  out.push('</svg>'); return out.join('');
}

function addToPptx(pptx,slide,scene) {
  scene.items.forEach(o=>{
    if(o.kind==='rect'||o.kind==='ellipse') {
      const opts={x:o.x/SCALE,y:o.y/SCALE,w:o.w/SCALE,h:o.h/SCALE,
        fill:o.fill?{color:o.fill}:{color:C.paper,transparency:100},
        line:o.stroke?{color:o.stroke,width:o.sw*.6,...(o.dash?{dashType:'dash'}:{})}:{color:o.fill||C.paper,transparency:100}};
      if(o.r) opts.radius=o.r/SCALE;
      slide.addShape(o.kind==='ellipse'?pptx.ShapeType.ellipse:o.r?pptx.ShapeType.roundRect:pptx.ShapeType.rect,opts);
    }
    if(o.kind==='line') {
      slide.addShape(pptx.ShapeType.line,{
        x:Math.min(o.x1,o.x2)/SCALE,y:Math.min(o.y1,o.y2)/SCALE,
        w:Math.abs(o.x2-o.x1)/SCALE,h:Math.abs(o.y2-o.y1)/SCALE,
        flipH:o.x2<o.x1,flipV:o.y2<o.y1,
        line:{color:o.color,width:o.sw*.6,...(o.dash?{dashType:'dash'}:{}),...(o.arrow?{endArrowType:'triangle'}:{})},
      });
    }
    if(o.kind==='image') slide.addImage({path:o.path,x:o.x/SCALE,y:o.y/SCALE,w:o.w/SCALE,h:o.h/SCALE});
    if(o.kind==='text') {
      slide.addText(o.str,{x:o.x/SCALE,y:o.y/SCALE,w:o.w/SCALE,h:o.h/SCALE,
        fontFace:'Arial',fontSize:o.size*.6,color:o.color,bold:o.weight>=600,
        align:o.align,margin:0,breakLine:false,valign:'top',
        paraSpaceAfterPt:0,lineSpacingMultiple:1.05,lang:'en-US',
      });
    }
  });
  slide.addNotes(scene.notes);
}

async function main() {
  fs.mkdirSync(path.join(OUT,'previews'),{recursive:true});
  const pptx=new pptxgen();
  pptx.defineLayout({name:'CUSTOM',width:W/SCALE,height:H/SCALE});pptx.layout='CUSTOM';
  pptx.author='';pptx.subject='Research idea for mentor discussion';
  pptx.title='Robot adaptation: idea, evidence, and unseen-height experiment';
  pptx.company='';pptx.lang='en-US';
  pptx.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'en-US'};
  slides.forEach((scene,i)=>{
    addToPptx(pptx,pptx.addSlide(),scene);
    fs.writeFileSync(path.join(OUT,'previews',`slide-${String(i+1).padStart(2,'0')}.svg`),svgFor(scene));
  });
  await pptx.writeFile({fileName:path.join(OUT,'robot_adaptation_pi.pptx')});
  fs.writeFileSync(path.join(OUT,'slide_content.json'),JSON.stringify(slides.map(({title,notes})=>({title,notes})),null,2));

  const html=`<!doctype html><html><head><meta charset="utf-8"><title>Robot adaptation: idea, evidence, and unseen-height experiment</title><style>
  @page{size:13.333333in 7.5in;margin:0}*{box-sizing:border-box}html,body{margin:0;background:#${C.paper}}.slide{width:13.333333in;height:7.5in;page-break-after:always;break-after:page;overflow:hidden}.slide:last-child{page-break-after:auto;break-after:auto}.slide svg{display:block;width:100%;height:100%}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}@media screen{body{background:#d2d7d4;padding:20px}.slide{margin:0 auto 24px;box-shadow:0 4px 20px #0002}}@media print{body{padding:0}.slide{margin:0}}
  </style></head><body>${slides.map((scene,i)=>`<section class="slide" data-slide="${i+1}">${svgFor(scene)}</section>`).join('')}</body></html>`;
  const htmlFile=path.join(OUT,'robot_adaptation_pi.html');
  fs.writeFileSync(htmlFile,html);
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page=await browser.newPage({viewport:{width:1600,height:900},deviceScaleFactor:1});
  await page.setContent(html,{waitUntil:'load'});
  await page.emulateMedia({media:'print'});
  await page.pdf({path:path.join(OUT,'robot_adaptation_pi.pdf'),preferCSSPageSize:true,printBackground:true});
  const overflow=await page.evaluate(()=>{
    const issues=[];
    document.querySelectorAll('.slide').forEach(sl=>sl.querySelectorAll('text').forEach(t=>{
      const b=t.getBBox(), x=+t.dataset.boxX,y=+t.dataset.boxY,w=+t.dataset.boxW,h=+t.dataset.boxH;
      if(b.x<x-3||b.x+b.width>x+w+3||b.y<y-3||b.y+b.height>y+h+3) issues.push({slide:+sl.dataset.slide,text:t.textContent,bbox:{x:b.x,y:b.y,width:b.width,height:b.height},box:{x,y,w,h}});
    }));return issues;
  });
  for(let i=0;i<slides.length;i++) {
    await page.setContent(`<html><head><style>html,body{margin:0;width:1600px;height:900px;background:#${C.paper}}svg{display:block}</style></head><body>${svgFor(slides[i])}</body></html>`);
    await page.screenshot({path:path.join(OUT,'previews',`slide-${String(i+1).padStart(2,'0')}.png`)});
  }
  await browser.close();
  const thumbs=[];
  for(let i=0;i<slides.length;i++) thumbs.push(await sharp(path.join(OUT,'previews',`slide-${String(i+1).padStart(2,'0')}.png`)).resize(640,360).toBuffer());
  const canvas=sharp({create:{width:1328,height:1576,channels:3,background:'#d2d7d4'}});
  await canvas.composite(thumbs.map((input,i)=>({input,left:16+(i%2)*656,top:16+Math.floor(i/2)*392}))).png().toFile(path.join(OUT,'preview.png'));
  const pdf=await PDFDocument.load(fs.readFileSync(path.join(OUT,'robot_adaptation_pi.pdf')));
  const check={slides:slides.length,pdfPages:pdf.getPageCount(),textOverflow:overflow};
  fs.writeFileSync(path.join(OUT,'validation.json'),JSON.stringify(check,null,2));
  console.log(JSON.stringify({out:OUT,...check}));
}
main().catch(err=>{console.error(err);process.exitCode=1;});
