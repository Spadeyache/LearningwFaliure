"""Read-only episode loading and derived, matched-seed gap construction."""
from pathlib import Path
import hashlib
import json
import numpy as np
from scipy.spatial.transform import Rotation

FACTORS = ['mass','object_friction','size','shape','com','goal_height','finger_friction','table_friction']
CHANNELS = ['relative_x','relative_y','relative_z','relative_rotation_x','relative_rotation_y','relative_rotation_z',
            'object_x','object_y','object_z','object_rotation_x','object_rotation_y','object_rotation_z',
            'tcp_object_distance','object_goal_distance','finger_width','left_compression','right_compression',
            'motor_limit','relative_velocity_z','tcp_height']
UNITS = ['m']*3+['rad']*3+['m']*3+['rad']*3+['m']*3+['N']*3+['m/s','m']
FACTOR_NAMES = ['Mass','Object friction','Size','Shape','COM offset','Lift target','Finger friction','Table friction']


def factor_values(c):
    p=c['properties']
    return dict(mass=p['mass_kg'], object_friction=p['static_friction'], size=p['size_xyz_m'][0],
        shape=p['shape'], com=p['com_offset_m'][0], goal_height=c['goal_clearance_m'],
        finger_friction=p['finger_friction'], table_friction=p['table_friction'])


def short_description(c, baseline):
    v,b=factor_values(c),factor_values(baseline)
    changes=[]
    for k in FACTORS:
        if v[k]!=b[k]:
            if k=='shape':changes.append(str(v[k]))
            elif k=='com':changes.append(f'COM {v[k]*1000:+g}mm')
            else:changes.append(f'{k.replace("_friction"," μ").replace("goal_height","lift")} ×{v[k]/b[k]:g}')
    return ', '.join(changes) or 'nominal'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rotation_gap(shift, nominal):
    return (Rotation.from_quat(shift, scalar_first=True)*Rotation.from_quat(nominal, scalar_first=True).inv()).as_rotvec()


def masked_interpolate(times, values, query):
    valid=(query>=times[0]-1e-8)&(query<=times[-1]+1e-8)
    output=np.column_stack([np.interp(query,times,values[:,j]) for j in range(values.shape[1])])
    output[~valid]=np.nan
    return output,valid


def load_dataset(root):
    root=Path(root); manifest=json.loads((root/'manifest.json').read_text())
    conditions=manifest['conditions']; baseline=next(c for c in conditions if not c['changed_properties'])
    index={c['condition_id']:i for i,c in enumerate(conditions)}
    nominal_values=factor_values(baseline)
    records=[]; hashes={}
    for path in sorted(root.glob('*.npz')):
        hashes[path.name]=sha256(path)
        with np.load(path,allow_pickle=False) as a:
            # No oracle property or outcome enters the measurement matrix.
            cid=str(a['label__condition_id']); c=conditions[index[cid]]
            if str(a['meta__experiment_identity'])!=manifest['identity']:raise ValueError('Mixed experiments')
            times=a['meta__state_time_s'].copy(); time=times[1:]
            rel=a['input__object_pose_tcp_m_wxyz'][1:].copy(); obj=a['input__object_pose_world_m_wxyz'][1:].copy()
            lr=a['input__finger_compression_mean_n'].copy()
            raw=np.column_stack([rel[:,:3],Rotation.from_quat(rel[:,3:],scalar_first=True).as_rotvec(),
                obj[:,:3],Rotation.from_quat(obj[:,3:],scalar_first=True).as_rotvec(),
                a['input__object_tcp_distance_m'][1:],a['input__object_goal_distance_m'][1:],a['input__finger_width_m'][1:],
                lr,a['input__grip_motor_limit_n'].mean(axis=1),a['input__relative_translation_response_tcp_m'][:,2]/np.diff(times),
                a['input__tcp_pose_world_m_wxyz'][1:,2]])
            values=factor_values(c); active=[k for k in FACTORS if values[k]!=nominal_values[k]]
            single=active[0] if len(active)==1 else ('nominal' if not active else 'mixed')
            magnitude=(values[single]/nominal_values[single] if single not in ('mixed','nominal','shape','com')
                       else (values['com']*1000 if single=='com' else np.nan))
            lift=int(a['label__first_lift_state_index'])
            failure_time=float(a['label__failure_time_s']); detection=float(a['label__failure_detection_time_s'])
            force=np.linalg.norm(a['sim__physics_object_pair_force_world_n'],axis=-1)
            records.append(dict(path=path,condition=index[cid],cid=cid,seed=int(a['label__seed']),
                success=bool(a['label__success_final']),rule=str(a['label__failure_type']),active=active,
                single=single,magnitude=magnitude,time=time,raw=raw,rel=rel,obj=obj,
                initial_pose=a['label__initial_object_pose_world_m_wxyz'].copy(),
                initial_joints=a['input__joint_position_rad_m'][0].copy(),goal=a['input__goal_position_world_m'].copy(),
                lift_time=float(times[lift]) if lift>=0 else np.nan,
                failure_time=failure_time,detection_time=detection,
                max_clearance=float(a['sim__object_clearance_m'].max()),
                motor_ceiling_fraction=float(np.mean(a['input__action_applied'][:,4]>=.99)),
                contact_force_peak=float(force.max()),reported_mass=float(a['input__reported_mass_kg']),values=values))
    if len(records)!=len(conditions)*manifest['config']['seed_count']:raise ValueError('Dataset is not complete')
    lookup={(r['cid'],r['seed']):r for r in records}
    if len(lookup)!=len(records):raise ValueError('Duplicate condition/seed')
    grid=np.arange(.05,5.0001,.05); liftgrid=np.arange(-.25,4.0001,.05)
    raw_all=[]; gaps=[]; masks=[]; aligned=[]; aligned_masks=[]
    for r in records:
        normal=lookup[(baseline['condition_id'],r['seed'])]
        # Compare the same elapsed time, never subtract quaternion components.
        t=np.union1d(r['time'],normal['time'])
        raw, valid=masked_interpolate(r['time'],r['raw'],t)
        base,bvalid=masked_interpolate(normal['time'],normal['raw'],t)
        g=raw-base
        # Current files share an exact time grid; do not silently interpolate rotations.
        if not np.array_equal(r['time'],normal['time']):raise ValueError('Rotation alignment requires common sampled times')
        g[:,3:6]=rotation_gap(r['rel'][:,3:],normal['rel'][:,3:])
        g[:,9:12]=rotation_gap(r['obj'][:,3:],normal['obj'][:,3:])
        gap, mask=masked_interpolate(t,g,grid)
        measured,_=masked_interpolate(r['time'],r['raw'],grid)
        raw_all.append(measured); gaps.append(gap); masks.append(mask)
        anchor=normal['lift_time'];r['nominal_lift_time']=anchor
        r['reset_matches_nominal']=bool(np.allclose(r['initial_pose'],normal['initial_pose'],atol=1e-7)
            and np.allclose(r['initial_joints'],normal['initial_joints'],atol=1e-7)
            and np.allclose(r['goal'],normal['goal'],atol=1e-7))
        if np.isfinite(anchor):a,m=masked_interpolate(t,g,liftgrid+anchor)
        else:a=np.full((len(liftgrid),len(CHANNELS)),np.nan);m=np.zeros(len(liftgrid),bool)
        aligned.append(a);aligned_masks.append(m)
    return dict(root=root,manifest=manifest,conditions=conditions,baseline=baseline,records=records,
        descriptions=[short_description(c,baseline) for c in conditions],hashes=hashes,
        time=grid,lift_time=liftgrid,raw=np.stack(raw_all),gap=np.stack(gaps),valid=np.stack(masks),
        lift_gap=np.stack(aligned),lift_valid=np.stack(aligned_masks),
        single=np.array([r['single'] for r in records]),seed=np.array([r['seed'] for r in records]),
        condition=np.array([r['condition'] for r in records]),success=np.array([r['success'] for r in records]),
        rule=np.array([r['rule'] for r in records]))
