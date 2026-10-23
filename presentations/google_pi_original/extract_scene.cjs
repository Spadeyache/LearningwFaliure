const fs=require('fs');
const path=require('path');
const source=path.resolve(__dirname,'../pi_adaptation_update/build_deck.cjs');
const code=fs.readFileSync(source,'utf8').split('function svgFor(slide)')[0];
const scenes=new Function('require','__dirname',code+'\nreturn slides;')(require,path.dirname(source));
for(const slide of scenes)for(const o of slide.items)if(o.kind==='image')delete o.data;
fs.writeFileSync(path.join(__dirname,'scene.json'),JSON.stringify(scenes));
console.log(JSON.stringify({slides:scenes.length,items:scenes.reduce((n,s)=>n+s.items.length,0),images:scenes.flatMap(s=>s.items).filter(o=>o.kind==='image').length}));
