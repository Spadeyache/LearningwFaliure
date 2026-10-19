"""Render recorded poses for representative groups; no policy or physics rollout."""
import argparse
import csv
import json
from pathlib import Path
import sys
import numpy as np
import torch
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from failure_collection.environment import CollectionEnv
from mani_skill.utils.structs.pose import Pose


def render_examples(folder,per_group=1):
    examples=list(csv.DictReader((folder/'representative_episodes.csv').open()))
    output=folder/'examples';output.mkdir(exist_ok=True)
    groups=sorted({r['group'] for r in examples})
    rendered=[]
    torch.set_num_threads(1)
    for group in groups:
        candidates=[r for r in examples if r['group']==group]
        candidates.sort(key=lambda r:r['split']!='held_out_seed')
        seen=set();chosen=[]
        for row in candidates:
            seed=row['episode'].rsplit('_seed',1)[-1]
            if seed not in seen:
                chosen.append(row);seen.add(seed)
            if len(chosen)==per_group:break
        for number,row in enumerate(chosen,1):
            path=Path(row['source_file']);path=path if path.is_absolute() else ROOT/path
            with np.load(path,allow_pickle=False) as d:
                condition=json.loads(str(d['label__condition_json']))
                obj=d['input__object_pose_world_m_wxyz'].copy()
                qpos=d['input__joint_position_rad_m'].copy()
                goal=d['input__goal_position_world_m'].copy()
                time=d['meta__state_time_s'].copy()
                error=d['input__object_goal_distance_m'].copy()
            env=CollectionEnv(condition['properties'],human_render_camera_configs={'shader_pack':'minimal','width':384,'height':384})
            frames=[]
            try:
                env.reset(seed=int(row['episode'].rsplit('_seed',1)[-1]),options={'reconfigure':True})
                env.goal_site.set_pose(Pose.create_from_pq(goal,device=env.device))
                for step in range(0,len(obj),2):
                    env.agent.robot.set_qpos(torch.tensor(qpos[step:step+1],device=env.device))
                    env.cube.set_pose(Pose.create(torch.tensor(obj[step:step+1],device=env.device)))
                    pixels=env.render_rgb_array()[0].cpu().numpy().astype(np.uint8)
                    image=Image.fromarray(pixels);draw=ImageDraw.Draw(image)
                    draw.rectangle((0,0,image.width,49),fill='black')
                    draw.multiline_text((5,4),f'{group} | recorded-pose replay | {row["split"]}\n'
                        f't={time[step]:.2f}s | object rise={obj[step,2]-obj[0,2]:.3f}m\n'
                        f'goal error={error[step]:.3f}m',fill='white')
                    frames.append(image)
                name=f'{group}_{number:02d}.gif'
                frames[0].save(output/name,save_all=True,append_images=frames[1:],duration=round(1000*2*(time[1]-time[0])),loop=0)
                rendered.append(dict(group=group,file='examples/'+name,episode=row['episode'],split=row['split']))
                print('Saved recorded-pose replay:',name,flush=True)
            finally:env.close()
    (folder/'examples.json').write_text(json.dumps(rendered,indent=2)+'\n')
    return rendered


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);p.add_argument('--per-group',type=int,default=1)
    a=p.parse_args()
    if a.per_group<1:p.error('--per-group must be positive')
    render_examples(a.folder,a.per_group)
