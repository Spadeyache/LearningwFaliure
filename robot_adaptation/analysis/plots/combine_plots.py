#!/usr/bin/env python3
"""Combine a run's completed individual PNGs without recomputing its plots."""
import argparse
import json
import html
from pathlib import Path
from PIL import Image


def combine(folder, columns=1, tile_width=1500):
    folder=Path(folder)
    report=json.loads((folder/'selections.json').read_text())
    report=[r for r in report if not (r.get('name')=='nominal' and r.get('condition_ids')==['C01'])]
    if not report:
        raise ValueError('No completed plots to combine')
    columns=min(columns,len(report));padding=12;title_height=0
    items=[]
    for entry in report:
        name=entry['file']
        if Path(name).name!=name:
            raise ValueError('Expected plot PNGs directly inside the run folder')
        with Image.open(folder/name) as im:
            size=(tile_width,round(im.height*tile_width/im.width))
        items.append(dict(entry=entry,width=size[0],height=size[1]))
    row_heights=[max(x['height'] for x in items[i:i+columns])+title_height for i in range(0,len(items),columns)]
    width=columns*tile_width+(columns+1)*padding
    height=sum(row_heights)+(len(row_heights)+1)*padding
    # Large plans use several full-resolution sheets in one scrolling viewer.
    if height > 30000 or width*height > 180_000_000:
        result = combine_sheets(folder, items, columns, tile_width, padding)
        manifest_path = folder / 'manifest.json'
        if manifest_path.exists():
            import hashlib
            manifest = json.loads(manifest_path.read_text())
            manifest['combined'] = result
            manifest['combiner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        return result
    if width*height>180_000_000:
        raise ValueError('Combined image too large; reduce --tile-width or split the plan into runs')
    canvas=Image.new('RGB',(width,height),'white')
    tiles=[];y=padding
    for row_index,start in enumerate(range(0,len(items),columns)):
        for col,item in enumerate(items[start:start+columns]):
            x=padding+col*(tile_width+padding);entry=item['entry']
            with Image.open(folder/entry['file']) as im:
                resized=im.convert('RGB').resize((item['width'],item['height']),Image.Resampling.LANCZOS)
                canvas.paste(resized,(x,y+title_height))
            tiles.append(dict(x=x,y=y,width=tile_width,height=row_heights[row_index],file=entry['file'],title=entry['title']))
        y+=row_heights[row_index]+padding
    canvas.save(folder/'combined.png',optimize=False);canvas.close()
    (folder/'combined_layout.json').write_text(json.dumps(dict(width=width,height=height,tiles=tiles),indent=2)+'\n')
    page='''<!doctype html><html><head><meta charset="utf-8"><title>All plots together</title><style>
body{margin:0;font:16px system-ui;color:#17202a}header{padding:14px;background:#f1f4f8;position:sticky;top:0;z-index:2}button,a,input{margin-right:12px}#view{overflow:auto;height:calc(100vh - 110px);background:#e9edf2}img{display:block;max-width:none;cursor:zoom-in}small{display:block;margin-top:8px}</style></head><body>
<header><b>__COUNT__ comparison plots · __COLUMNS__ column(s)</b> · <a href="index.html">Individual plots</a> · <a href="combined.png" download>Download combined PNG</a><br>
<button id="fit">Fit width</button><button id="full">Full resolution</button><label>Zoom <input id="zoom" type="range" min="10" max="150" value="30"><span id="value"></span></label>
<small>Scroll to explore. Click a plot to open its full-size original. Green = success; red = failure.</small></header>
<div id="view"><img id="sheet" src="combined.png" alt="All generated episode parameter plots combined into one image"></div>
<script>const layout=__LAYOUT__,img=document.getElementById('sheet'),view=document.getElementById('view'),slider=document.getElementById('zoom');
function scale(p){img.style.width=(layout.width*p/100)+'px';slider.value=p;document.getElementById('value').textContent=Math.round(p)+'%'}
slider.oninput=()=>scale(Number(slider.value));document.getElementById('fit').onclick=()=>scale(Math.max(10,Math.min(150,(view.clientWidth-20)/layout.width*100)));
document.getElementById('full').onclick=()=>scale(100);img.onload=()=>document.getElementById('fit').click();
img.onclick=e=>{const r=img.getBoundingClientRect(),x=(e.clientX-r.left)*layout.width/r.width,y=(e.clientY-r.top)*layout.height/r.height;
const t=layout.tiles.find(t=>x>=t.x&&x<=t.x+t.width&&y>=t.y&&y<=t.y+t.height);if(t)window.open(t.file,'_blank','noopener')};</script></body></html>'''
    page=page.replace('__COUNT__',str(len(items))).replace('__COLUMNS__',str(columns))
    page=page.replace('__LAYOUT__',json.dumps(dict(width=width,height=height,tiles=tiles)).replace('<','\\u003c'))
    (folder/'combined.html').write_text(page)
    result=dict(plots=len(items),columns=columns,width=width,height=height,file='combined.png',viewer='combined.html')
    manifest_path=folder/'manifest.json'
    if manifest_path.exists():
        import hashlib
        manifest=json.loads(manifest_path.read_text());manifest['combined']=result
        manifest['combiner_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    return result


def combine_sheets(folder, items, columns, tile_width, padding):
    """Preserve readable text; show every sheet vertically in a single viewer."""
    width = columns * tile_width + (columns + 1) * padding
    batches, current, current_height = [], [], padding
    for start in range(0, len(items), columns):
        row = items[start:start + columns]
        h = max(item['height'] for item in row) + padding
        if current and current_height + h > min(24000, 60_000_000 // width):
            batches.append(current)
            current, current_height = [], padding
        current.append(row)
        current_height += h
    if current:
        batches.append(current)
    pages = []
    for number, batch in enumerate(batches, 1):
        height = padding + sum(max(i['height'] for i in row) + padding for row in batch)
        canvas = Image.new('RGB', (width, height), 'white')
        tiles, y = [], padding
        for row in batch:
            row_height = max(i['height'] for i in row)
            for col, item in enumerate(row):
                x = padding + col * (tile_width + padding)
                with Image.open(folder / item['entry']['file']) as image:
                    image = image.convert('RGB').resize((tile_width, item['height']), Image.Resampling.LANCZOS)
                    canvas.paste(image, (x, y))
                tiles.append(dict(x=x, y=y, width=tile_width, height=item['height'],
                                  file=item['entry']['file'], title=item['entry']['title']))
            y += row_height + padding
        name = f'combined_{number:03d}.png'
        canvas.save(folder / name)
        canvas.close()
        pages.append(dict(file=name, width=width, height=height, tiles=tiles))
    layout = dict(columns=columns, width=width, pages=pages, plots=len(items))
    (folder / 'combined_layout.json').write_text(json.dumps(layout, indent=2) + '\n')
    downloads = ' · '.join(f'<a href="{page["file"]}">PNG sheet {i}</a>' for i, page in enumerate(pages, 1))
    images = ''.join(f'<img loading="lazy" data-page="{i}" src="{page["file"]}" alt="Combined comparison sheet {i+1}">'
                     for i, page in enumerate(pages))
    page = ('<!doctype html><meta charset="utf-8"><title>All comparison plots</title>'
        '<style>body{margin:0;font:16px system-ui}header{position:sticky;top:0;background:#f1f4f8;padding:12px;z-index:2}'
        '#view{overflow:auto;height:calc(100vh - 125px)}img{display:block;max-width:none;cursor:zoom-in}small{display:block}</style>'
        f'<header><b>{len(items)} comparison plots · {columns} column(s) · one scrolling view</b> · '
        '<a href="index.html">Individual plots</a><br>'
        '<button id="fit">Fit width</button> <button id="full">Full resolution</button> '
        '<label>Zoom <input id="zoom" type="range" min="10" max="150" value="100"></label><br>' + downloads +
        '<small>Full-resolution PNGs are split into sheets to keep the browser usable. Click a plot to open its original.</small></header>'
        '<div id="view">' + images + '</div><script>const layout=' + json.dumps(layout).replace('<','\\u003c') + ';'
        'const view=document.getElementById("view"),slider=document.getElementById("zoom"),imgs=[...view.querySelectorAll("img")];'
        'function scale(p){imgs.forEach(im=>im.style.width=(layout.width*p/100)+"px");slider.value=p}'
        'slider.oninput=()=>scale(Number(slider.value));'
        'document.getElementById("fit").onclick=()=>scale(Math.max(10,Math.min(150,(view.clientWidth-20)/layout.width*100)));'
        'document.getElementById("full").onclick=()=>scale(100);'
        'imgs.forEach(im=>im.onclick=e=>{const p=layout.pages[Number(im.dataset.page)],r=im.getBoundingClientRect(),'
        'x=(e.clientX-r.left)*p.width/r.width,y=(e.clientY-r.top)*p.height/r.height;'
        'const t=p.tiles.find(t=>x>=t.x&&x<=t.x+t.width&&y>=t.y&&y<=t.y+t.height);'
        'if(t)window.open(t.file,"_blank","noopener")});document.getElementById("fit").click();</script>')
    (folder / 'combined.html').write_text(page)
    return dict(plots=len(items), columns=columns, width=width, sheets=len(pages),
                files=[p['file'] for p in pages], file=pages[0]['file'], viewer='combined.html')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path,help='Run folder containing selections.json and PNGs')
    parser.add_argument('--columns',type=int,default=1)
    parser.add_argument('--tile-width',type=int,default=1500)
    args=parser.parse_args()
    if args.columns<1 or args.tile_width<300:parser.error('columns must be positive; tile-width must be at least 300')
    print(json.dumps(combine(args.folder,args.columns,args.tile_width)))


if __name__=='__main__':main()
