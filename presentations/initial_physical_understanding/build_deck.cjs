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
  text('INITIAL PHYSICAL UNDERSTANDING  /  MENTOR DISCUSSION',80,862,1230,16,C.muted,400,{h:23});
  text(String(slides.length).padStart(2,'0')+' / 07',1390,859,130,19,C.muted,700,{align:'right',h:28});
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

// 1 — Motivation.
base('01 · Motivation','When expected physics\nmeets the real world','How can robots handle deployment conditions\nthey did not encounter during training?',{titleSize:65,titleLH:72,subY:271});
rect(80,397,625,345,C.white,22);
rect(895,397,625,345,C.blush,22);
text('Expected conditions',110,421,540,29,C.ink,700);
text('Actual conditions',925,421,540,29,C.ink,700);
robotScene(142,470,485,248,'lift');
robotScene(958,470,485,248,'slip',C.coral);
arrow(744,560,855,560,C.coral,false,4);
text('Mismatch',724,593,155,23,C.coral,700,{align:'center'});
text('Physical conditions can differ from those assumed during training.',80,775,1440,29,C.ink);
s.notes='Broad question: How can robots at deployment handle situations they were not exposed to during training? One motivation is the gap between expected physical conditions and the actual environment. The drawing is a conceptual illustration, not an experimental result. The same object can behave differently when its physical properties differ from what the system assumes.';

// 2 — Hypothesis.
base('02 · Hypothesis','Use an estimate of the actual conditions','A policy trained across varied physical conditions could execute successfully\nwhen supplied with a sufficiently accurate estimate of its environment.');
text('TRAINING',80,293,440,19,C.muted,700);
rect(80,330,400,300,C.gray,22);
text('Varied physical conditions',104,352,350,27,C.ink,700);
for(let i=0;i<6;i++) miniCondition(105+(i%3)*119,408+Math.floor(i/3)*101,108,88,i);
arrow(508,466,610,466,C.muted,false,3);
rect(645,377,307,183,C.white,22,C.line,1.5);
neural(725,399,146,91);
text('Trained policy',665,511,267,28,C.ink,700,{align:'center'});
arrow(981,466,1077,466,C.muted,false,3);
rect(1110,330,410,300,C.white,22);
text('Fixed pick-and-lift task',1135,352,360,27,C.ink,700);
robotScene(1122,398,385,226,'lift');
pill('AT DEPLOYMENT',1000,641,307,C.pale,C.teal,19);
rect(645,694,307,91,C.teal,16);
text('Physical estimate',661,723,275,29,C.white,700,{align:'center'});
arrow(798,687,798,582,C.teal,false,3);
text('Estimate the conditions\nthe robot actually faces.',1000,700,490,28,C.muted,400,{lh:36});
s.notes='The hypothesis is that a policy trained over a range of physical conditions can use an approximation of the current environment as an input. The policy is part of the experimental setup. The contribution studied here is formation of the initial physical estimate. Later work may revise that estimate through interaction. No perfect-performance guarantee is assumed.';

// 3 — Scope.
base('03 · Scope','What we mean by understanding');
rect(80,223,1440,216,C.pale,22);
rect(80,223,9,216,C.teal,4);
text('Estimating task-relevant physical properties\nwell enough to support task execution.',124,266,1335,44,C.ink,700,{lh:58});
const cards=[
  {x:80,title:'Objective',body:'Pick and lift',tag:'FIXED',fill:C.white,tagFill:C.gray,tagInk:C.muted},
  {x:575,title:'Grasp strategy',body:'Top-down grasp',tag:'FIXED',fill:C.white,tagFill:C.gray,tagInk:C.muted},
  {x:1070,title:'Physical understanding',body:'Initial estimate',tag:'STUDIED',fill:C.white,tagFill:C.pale,tagInk:C.teal},
];
cards.forEach(c=>{
  rect(c.x,490,450,239,c.fill,20,c.tag==='STUDIED'?C.teal:null,2);
  text(c.title,c.x+25,520,400,25,C.muted,700);
  text(c.body,c.x+25,567,400,36,C.ink,700);
  pill(c.tag,c.x+25,655,136,c.tagFill,c.tagInk,18);
});
text('Fixing the objective and strategy keeps the focus on physical estimation.',80,776,1440,29,C.ink);
s.notes='For this experiment, understanding the world means estimating task-relevant physical properties well enough to support execution. In the broader problem a robot may need an objective and a range of solutions. Here we supply the objective and a particular solution family. Movement adaptation and general decision-making are outside the current research focus. The trained controller is used to test whether the initial physical estimate is useful.';

// 4 — Controlled task.
base('04 · Controlled task','One task. One grasp strategy.','Use a top-down pick and lift to isolate the physical-estimation question.');
['Approach','Grasp','Lift'].forEach((label,i)=>{
  const x=80+i*495;
  rect(x,292,450,420,C.white,22);
  circleLabel(String(i+1),x+25,317,i===2?C.teal:C.dark);
  text(label,x+85,320,330,32,C.ink,700);
  robotScene(x+18,398,414,274,['approach','grasp','lift'][i]);
  if(i<2) arrow(x+465,508,x+482,508,C.arm,false,2);
});
rect(80,748,1440,63,C.pale,15);
text('The objective and grasp strategy remain fixed throughout the experiment.',103,764,1394,29,C.ink,400,{align:'center'});
s.notes='The task is to pick up an object and lift it. We choose a top-down approach, grasp, and vertical lift in advance. This is a deliberate restriction: the experiment studies the robot’s initial approximation of physical conditions while keeping the high-level task and grasp strategy fixed. The diagrams are schematic, not a proposed new movement-learning contribution.';

// 5 — Simulation preparation.
base('05 · Simulation setup','Prepare the policy in simulation','Select a compact physical context, then train across variations in that context.');
const cx=[80,575,1070];
cx.forEach(x=>rect(x,286,450,449,C.white,22));
circleLabel('1',105,311,C.dark); text('Select relevant variables',163,315,342,27,C.ink,700);
pill('mass',110,388,132,C.gray,C.muted,21); pill('friction',259,388,183,C.gray,C.muted,21);
pill('geometry',110,443,206,C.gray,C.muted,21);pill('…',333,443,109,C.gray,C.muted,24);
text('Illustrative candidate properties',110,493,370,18,C.muted);
arrow(305,526,305,555,C.teal,false,2.5);
rect(166,568,278,67,C.pale,14);
text('CREST',176,583,258,29,C.teal,700,{align:'center'});
text('Keep the representation\nand computation manageable.',110,662,390,25,C.muted,400,{lh:32});
circleLabel('2',600,311,C.dark);text('Vary physical conditions',658,315,342,27,C.ink,700);
for(let i=0;i<6;i++) miniCondition(605+(i%3)*130,398+Math.floor(i/3)*111,113,96,i+1);
text('Sample varied combinations\nin the simulator.',605,662,390,25,C.muted,400,{lh:32});
circleLabel('3',1095,311,C.dark);text('Train a conditioned policy',1153,315,342,26,C.ink,700);
text('State + known physical context',1096,389,396,24,C.muted,400,{align:'center'});
vector(1202,439,186,53,true);
arrow(1295,507,1295,542,C.teal,false,2.5);
rect(1130,556,330,79,C.gray,15);
text('Policy training',1146,580,298,30,C.ink,700,{align:'center'});
text('Learn execution across\nthe modeled conditions.',1100,662,390,25,C.muted,400,{lh:32});
arrow(544,510,560,510,C.arm,false,2.5);arrow(1039,510,1055,510,C.arm,false,2.5);
text('Selected variables provide an approximation of the physical environment.',80,767,1440,28,C.ink);
text('Method reference: CREST · Lee et al., ICRA 2021 · arxiv.org/abs/2103.16772',80,812,1440,16,C.muted);
s.notes='Represent the environment using a selected set of variables. We propose using CREST to identify relevant context variables so that representation and computation remain manageable. The variable names shown are examples, not a reported selection result. Train the conditioned policy in simulation over variation in the modeled physical context. CREST relevance is conditional on the tested task, controller, ranges, and simulator; it does not guarantee complete coverage of real-world physics. Reference: Lee et al., Causal Reasoning in Simulation for Structure and Transfer Learning of Robot Manipulation Policies, ICRA 2021, https://arxiv.org/abs/2103.16772 .';

// 6 — Initial physical estimation.
base('06 · Current experiment','Form the initial estimate at deployment','Study how initial observations become a useful approximation of physical conditions.',{titleSize:56});
const nx=[80,452,824,1196], nw=324;
nx.forEach((x,i)=>rect(x,320,nw,278,i===1?C.pale:C.white,20,i===1?C.teal:null,2));
text('Observe',105,344,274,29,C.ink,700,{align:'center'});
camera(188,416,110);
text('Initial observations',103,548,278,24,C.muted,400,{align:'center'});
text('Estimate',477,344,274,29,C.teal,700,{align:'center'});
vector(514,429,200,65,true);
text('Selected physical properties',467,548,294,22,C.teal,400,{align:'center'});
text('Condition',849,344,274,29,C.ink,700,{align:'center'});
neural(908,411,155,100);
text('Policy trained in simulation',838,548,296,22,C.muted,400,{align:'center'});
text('Execute',1221,344,274,29,C.ink,700,{align:'center'});
robotScene(1209,397,296,153,'lift');
text('Fixed pick and lift',1220,548,276,24,C.muted,400,{align:'center'});
for(let i=0;i<3;i++) arrow(nx[i]+nw+12,457,nx[i+1]-15,457,C.arm,false,2.5);
line(614,615,614,650,C.teal,3);
pill('CURRENT FOCUS',470,664,288,C.teal,C.white,20);
text('How is the initial estimate formed?',80,732,1440,37,C.ink,700,{align:'center'});
text('Test whether sufficiently accurate estimates support successful execution in simulation.',80,789,1440,27,C.muted,400,{align:'center'});
s.notes='At deployment, initial observations are used to estimate the selected physical properties. The diagram illustrates a possible observation pathway; the sensing method is part of the experimental design. The estimates are supplied to the policy trained in simulation. We study how this initial approximation is formed and whether it supports execution. The representation can be approximate, but its usefulness is an empirical question. Correct selected parameters do not guarantee perfect performance, because omitted effects, policy limitations, and physical constraints can remain. This slide is a proposed setup, not a reported result.';

// 7 — Current stage and extension.
base('07 · Research direction','Initial understanding comes first','Start with the initial estimate; investigate revision through interaction in a later stage.');
rect(80,285,690,391,C.pale,22);
rect(830,285,690,391,null,22,C.arm,2,true);
pill('CURRENT EXPERIMENT',110,311,319,C.teal,C.white,19);
pill('LATER EXTENSION',860,311,280,C.gray,C.muted,19);
text('Form an initial\nphysical estimate.',113,388,590,39,C.ink,700,{lh:49});
text('Use observed responses\nto revise the estimate.',863,388,600,39,C.ink,700,{lh:49});
rect(113,530,239,83,C.white,14);
text('Initial estimate',126,556,213,25,C.teal,700,{align:'center'});
arrow(369,572,421,572,C.teal,false,2.5);
rect(439,530,286,83,C.white,14);
text('Task execution',452,556,260,25,C.ink,700,{align:'center'});
text('Success, failure, and interaction data',863,504,595,24,C.muted);
rect(863,552,239,83,C.white,14,C.line,1);
text('Revised estimate',876,579,213,24,C.muted,700,{align:'center'});
arrow(1115,594,1166,594,C.muted,true,2.5);
rect(1184,552,286,83,C.white,14,C.line,1);
text('Next execution',1197,579,260,24,C.muted,700,{align:'center'});
line(1328,646,1328,658,C.arm,2,true);
line(1328,658,982,658,C.arm,2,true);
arrow(982,658,982,647,C.arm,true,2);
text('Can a compact physical estimate support reliable\nexecution of a fixed manipulation task?',80,720,1440,38,C.ink,700,{lh:48});
s.notes='The first stage studies how a robot forms an initial approximation of the physical environment for a fixed manipulation task. A later stage can study how the robot revises that approximation using interaction, including observed responses associated with successes and failures. Outcome alone may not identify the cause; trajectories and sensor observations can provide richer evidence. Interaction-based refinement is future work and is not presented as part of the current contribution. The deck communicates a research idea and contains no newly claimed experimental results.';

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
  pptx.title='Initial physical understanding for robot deployment';
  pptx.company='';pptx.lang='en-US';
  pptx.theme={headFontFace:'Arial',bodyFontFace:'Arial',lang:'en-US'};
  slides.forEach((scene,i)=>{
    addToPptx(pptx,pptx.addSlide(),scene);
    fs.writeFileSync(path.join(OUT,'previews',`slide-${String(i+1).padStart(2,'0')}.svg`),svgFor(scene));
  });
  await pptx.writeFile({fileName:path.join(OUT,'initial_physical_understanding.pptx')});
  fs.writeFileSync(path.join(OUT,'slide_content.json'),JSON.stringify(slides.map(({title,notes})=>({title,notes})),null,2));

  const html=`<!doctype html><html><head><meta charset="utf-8"><title>Initial physical understanding for robot deployment</title><style>
  @page{size:13.333333in 7.5in;margin:0}*{box-sizing:border-box}html,body{margin:0;background:#${C.paper}}.slide{width:13.333333in;height:7.5in;page-break-after:always;break-after:page;overflow:hidden}.slide:last-child{page-break-after:auto;break-after:auto}.slide svg{display:block;width:100%;height:100%}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}@media screen{body{background:#d2d7d4;padding:20px}.slide{margin:0 auto 24px;box-shadow:0 4px 20px #0002}}@media print{body{padding:0}.slide{margin:0}}
  </style></head><body>${slides.map((scene,i)=>`<section class="slide" data-slide="${i+1}">${svgFor(scene)}</section>`).join('')}</body></html>`;
  const htmlFile=path.join(OUT,'initial_physical_understanding.html');
  fs.writeFileSync(htmlFile,html);
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page=await browser.newPage({viewport:{width:1600,height:900},deviceScaleFactor:1});
  await page.setContent(html,{waitUntil:'load'});
  await page.emulateMedia({media:'print'});
  await page.pdf({path:path.join(OUT,'initial_physical_understanding.pdf'),preferCSSPageSize:true,printBackground:true});
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
  const pdf=await PDFDocument.load(fs.readFileSync(path.join(OUT,'initial_physical_understanding.pdf')));
  const check={slides:slides.length,pdfPages:pdf.getPageCount(),textOverflow:overflow};
  fs.writeFileSync(path.join(OUT,'validation.json'),JSON.stringify(check,null,2));
  console.log(JSON.stringify({out:OUT,...check}));
}
main().catch(err=>{console.error(err);process.exitCode=1;});
