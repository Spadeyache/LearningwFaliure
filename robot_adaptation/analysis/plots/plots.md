# Plot plan for the collected pick-and-lift data

This is the editable input to `plot.py`. Each row under **Plots** generates one PNG.
Dataset: `/home/ubuntu/faliure/runs/failure_collection/varied_fixed40g`.
Dataset fingerprint: `00564dcc270025005feff1a7588b7c5e0c793be7cc0a1125ae01c1bc1a8f1322`

There are 60 physical settings, each with 10 starting seeds: 600 episodes. The 46 plot rows below cover all 60 settings. Reference attempts are shared, not additional experiments.

## Variables

| Variable name for code | Meaning | Unit in plots | Collected values |
| --- | --- | --- | --- |
| mass | Actual object mass | g | 40, 100, 500 |
| object_friction | Object static/dynamic friction (changed together) | coefficient | 0.1, 0.4, 1.0 |
| size | Cube side / sphere diameter | mm | 30, 40, 50 |
| shape | Object shape | category | cube, sphere |
| com | Object COM offset along X | mm | -5, 0, +5 |
| goal_height | Required vertical lift | cm | 10, 20, 30 |
| finger_friction | Finger surface friction | coefficient | 0.1, 0.2, 0.5 |
| table_friction | Table surface friction | coefficient | 0.1, 0.3, 0.8 |

Nominal C01: mass 100 g; object friction 0.4; 40 mm cube; COM 0 mm; lift 20 cm; finger friction 0.2; table friction 0.3. The robot always receives a fixed 40 g estimate.

## How to edit

- Add or edit a row in **Plots**. Delete a row to stop generating that plot.
- **Plot** is a unique filename without `.png`, using lowercase letters, digits, `_` or `-`.
- **Variables** lists the panels to draw, separated by commas. Every variable changed in the selected conditions must be listed; the script rejects hidden extra changes.
- **Conditions** lists exact condition IDs, such as `C17,C18`, or an inclusive range such as `C29-C31`. Use the catalog below to choose.
- **Reference** `yes` adds the ten nominal C01 attempts. `no` does not add them.
- **Title** is the displayed plot title. Do not put a `|` character inside a cell.

Example: the `object_friction_only` row selects C04 and C05 plus C01, so mass and every other physical setting stay nominal.
Same-direction and opposite-direction pair experiments were both collected. Their separate rows select their actual condition IDs; directions describe ordered levels, not an exact proportional law.
Mixed rows each select one complete collected setting plus nominal, so no other mixed settings are pooled into that plot.

## Plots

| Plot | Variables | Conditions | Reference | Title |
| --- | --- | --- | --- | --- |
| mass_only | mass | C02,C03 | yes | Mass only; all other settings fixed |
| object_friction_only | object_friction | C04,C05 | yes | Object friction only; all other settings fixed |
| size_only | size | C06,C07 | yes | Size only; all other settings fixed |
| shape_only | shape | C08 | yes | Shape only; all other settings fixed |
| com_only | com | C09,C10 | yes | COM offset only; all other settings fixed |
| goal_height_only | goal_height | C11,C12 | yes | Lift target only; all other settings fixed |
| finger_friction_only | finger_friction | C13,C14 | yes | Finger friction only; all other settings fixed |
| table_friction_only | table_friction | C15,C16 | yes | Table friction only; all other settings fixed |
| mass_object_friction_together | mass,object_friction | C17,C18 | yes | Mass + Object friction: same direction |
| mass_object_friction_opposite | mass,object_friction | C19,C20 | yes | Mass + Object friction: opposite directions |
| mass_size_together | mass,size | C21,C22 | yes | Mass + Size: same direction |
| mass_size_opposite | mass,size | C23,C24 | yes | Mass + Size: opposite directions |
| mass_goal_height_together | mass,goal_height | C25,C26 | yes | Mass + Lift target: same direction |
| mass_goal_height_opposite | mass,goal_height | C27,C28 | yes | Mass + Lift target: opposite directions |
| mixed_c29 | mass,object_friction,size,finger_friction | C29 | yes | Mixed C29: Mass + Object friction + Size + Finger friction |
| mixed_c30 | mass,object_friction,com | C30 | yes | Mixed C30: Mass + Object friction + COM offset |
| mixed_c31 | mass,object_friction,size,goal_height | C31 | yes | Mixed C31: Mass + Object friction + Size + Lift target |
| mixed_c32 | mass,object_friction,size,shape,com,goal_height,table_friction | C32 | yes | Mixed C32: Mass + Object friction + Size + Shape + COM offset + Lift target + Table friction |
| mixed_c33 | size,shape,goal_height,finger_friction,table_friction | C33 | yes | Mixed C33: Size + Shape + Lift target + Finger friction + Table friction |
| mixed_c34 | object_friction,finger_friction | C34 | yes | Mixed C34: Object friction + Finger friction |
| mixed_c35 | mass,object_friction,size,shape,finger_friction,table_friction | C35 | yes | Mixed C35: Mass + Object friction + Size + Shape + Finger friction + Table friction |
| mixed_c36 | mass,shape,com,finger_friction,table_friction | C36 | yes | Mixed C36: Mass + Shape + COM offset + Finger friction + Table friction |
| mixed_c37 | mass,size,com,finger_friction | C37 | yes | Mixed C37: Mass + Size + COM offset + Finger friction |
| mixed_c38 | mass,size,finger_friction | C38 | yes | Mixed C38: Mass + Size + Finger friction |
| mixed_c39 | mass,size,shape,com,goal_height,table_friction | C39 | yes | Mixed C39: Mass + Size + Shape + COM offset + Lift target + Table friction |
| mixed_c40 | object_friction,size,com,goal_height,finger_friction | C40 | yes | Mixed C40: Object friction + Size + COM offset + Lift target + Finger friction |
| mixed_c41 | mass,size,shape,goal_height,finger_friction | C41 | yes | Mixed C41: Mass + Size + Shape + Lift target + Finger friction |
| mixed_c42 | object_friction,size,finger_friction | C42 | yes | Mixed C42: Object friction + Size + Finger friction |
| mixed_c43 | mass,object_friction,size,goal_height,table_friction | C43 | yes | Mixed C43: Mass + Object friction + Size + Lift target + Table friction |
| mixed_c44 | mass,object_friction,com,finger_friction | C44 | yes | Mixed C44: Mass + Object friction + COM offset + Finger friction |
| mixed_c45 | mass,object_friction,size,finger_friction | C45 | yes | Mixed C45: Mass + Object friction + Size + Finger friction |
| mixed_c46 | mass,object_friction,com,finger_friction,table_friction | C46 | yes | Mixed C46: Mass + Object friction + COM offset + Finger friction + Table friction |
| mixed_c47 | mass,shape,com,goal_height,finger_friction | C47 | yes | Mixed C47: Mass + Shape + COM offset + Lift target + Finger friction |
| mixed_c48 | mass,object_friction,size,com,finger_friction,table_friction | C48 | yes | Mixed C48: Mass + Object friction + Size + COM offset + Finger friction + Table friction |
| mixed_c49 | mass,object_friction,com,goal_height | C49 | yes | Mixed C49: Mass + Object friction + COM offset + Lift target |
| mixed_c50 | size,goal_height,finger_friction,table_friction | C50 | yes | Mixed C50: Size + Lift target + Finger friction + Table friction |
| mixed_c51 | size,goal_height,finger_friction | C51 | yes | Mixed C51: Size + Lift target + Finger friction |
| mixed_c52 | mass,size,shape,table_friction | C52 | yes | Mixed C52: Mass + Size + Shape + Table friction |
| mixed_c53 | mass,object_friction,size,shape,com,finger_friction | C53 | yes | Mixed C53: Mass + Object friction + Size + Shape + COM offset + Finger friction |
| mixed_c54 | object_friction,size,goal_height | C54 | yes | Mixed C54: Object friction + Size + Lift target |
| mixed_c55 | size,shape,com,goal_height,finger_friction,table_friction | C55 | yes | Mixed C55: Size + Shape + COM offset + Lift target + Finger friction + Table friction |
| mixed_c56 | mass,shape,com,goal_height,table_friction | C56 | yes | Mixed C56: Mass + Shape + COM offset + Lift target + Table friction |
| mixed_c57 | mass,object_friction,size,shape,goal_height | C57 | yes | Mixed C57: Mass + Object friction + Size + Shape + Lift target |
| mixed_c58 | mass,size,goal_height | C58 | yes | Mixed C58: Mass + Size + Lift target |
| mixed_c59 | mass,object_friction,com,goal_height,table_friction | C59 | yes | Mixed C59: Mass + Object friction + COM offset + Lift target + Table friction |
| mixed_c60 | mass,object_friction,com,goal_height,finger_friction,table_friction | C60 | yes | Mixed C60: Mass + Object friction + COM offset + Lift target + Finger friction + Table friction |

## Condition catalog

This is a reference table. The **Plots** table controls selection; physical values are always verified against the saved NPZ files. Episode numbers are from the original collection order.

| ID | Episodes | Design | Mass g | Object friction | Size mm | Shape | COM X mm | Lift cm | Finger friction | Table friction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | 1-10 | nominal | 100 | 0.4 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C02 | 11-20 | single | 40 | 0.4 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C03 | 21-30 | single | 500 | 0.4 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C04 | 31-40 | single | 100 | 0.1 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C05 | 41-50 | single | 100 | 1 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C06 | 51-60 | single | 100 | 0.4 | 30 | cube | 0 | 20 | 0.2 | 0.3 |
| C07 | 61-70 | single | 100 | 0.4 | 50 | cube | 0 | 20 | 0.2 | 0.3 |
| C08 | 71-80 | single | 100 | 0.4 | 40 | sphere | 0 | 20 | 0.2 | 0.3 |
| C09 | 81-90 | single | 100 | 0.4 | 40 | cube | -5 | 20 | 0.2 | 0.3 |
| C10 | 91-100 | single | 100 | 0.4 | 40 | cube | 5 | 20 | 0.2 | 0.3 |
| C11 | 101-110 | single | 100 | 0.4 | 40 | cube | 0 | 10 | 0.2 | 0.3 |
| C12 | 111-120 | single | 100 | 0.4 | 40 | cube | 0 | 30 | 0.2 | 0.3 |
| C13 | 121-130 | single | 100 | 0.4 | 40 | cube | 0 | 20 | 0.1 | 0.3 |
| C14 | 131-140 | single | 100 | 0.4 | 40 | cube | 0 | 20 | 0.5 | 0.3 |
| C15 | 141-150 | single | 100 | 0.4 | 40 | cube | 0 | 20 | 0.2 | 0.1 |
| C16 | 151-160 | single | 100 | 0.4 | 40 | cube | 0 | 20 | 0.2 | 0.8 |
| C17 | 161-170 | same direction | 40 | 0.1 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C18 | 171-180 | same direction | 500 | 1 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C19 | 181-190 | opposite directions | 40 | 1 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C20 | 191-200 | opposite directions | 500 | 0.1 | 40 | cube | 0 | 20 | 0.2 | 0.3 |
| C21 | 201-210 | same direction | 40 | 0.4 | 30 | cube | 0 | 20 | 0.2 | 0.3 |
| C22 | 211-220 | same direction | 500 | 0.4 | 50 | cube | 0 | 20 | 0.2 | 0.3 |
| C23 | 221-230 | opposite directions | 40 | 0.4 | 50 | cube | 0 | 20 | 0.2 | 0.3 |
| C24 | 231-240 | opposite directions | 500 | 0.4 | 30 | cube | 0 | 20 | 0.2 | 0.3 |
| C25 | 241-250 | same direction | 40 | 0.4 | 40 | cube | 0 | 10 | 0.2 | 0.3 |
| C26 | 251-260 | same direction | 500 | 0.4 | 40 | cube | 0 | 30 | 0.2 | 0.3 |
| C27 | 261-270 | opposite directions | 40 | 0.4 | 40 | cube | 0 | 30 | 0.2 | 0.3 |
| C28 | 271-280 | opposite directions | 500 | 0.4 | 40 | cube | 0 | 10 | 0.2 | 0.3 |
| C29 | 281-290 | mixed | 500 | 1 | 30 | cube | 0 | 20 | 0.5 | 0.3 |
| C30 | 291-300 | mixed | 40 | 0.1 | 40 | cube | 5 | 20 | 0.2 | 0.3 |
| C31 | 301-310 | mixed | 40 | 1 | 30 | cube | 0 | 10 | 0.2 | 0.3 |
| C32 | 311-320 | mixed | 40 | 0.1 | 50 | sphere | 5 | 30 | 0.2 | 0.1 |
| C33 | 321-330 | mixed | 100 | 0.4 | 50 | sphere | 0 | 10 | 0.5 | 0.1 |
| C34 | 331-340 | mixed | 100 | 0.1 | 40 | cube | 0 | 20 | 0.1 | 0.3 |
| C35 | 341-350 | mixed | 500 | 1 | 30 | sphere | 0 | 20 | 0.5 | 0.1 |
| C36 | 351-360 | mixed | 40 | 0.4 | 40 | sphere | -5 | 20 | 0.5 | 0.8 |
| C37 | 361-370 | mixed | 500 | 0.4 | 50 | cube | -5 | 20 | 0.1 | 0.3 |
| C38 | 371-380 | mixed | 40 | 0.4 | 50 | cube | 0 | 20 | 0.1 | 0.3 |
| C39 | 381-390 | mixed | 500 | 0.4 | 50 | sphere | 5 | 10 | 0.2 | 0.8 |
| C40 | 391-400 | mixed | 100 | 0.1 | 50 | cube | -5 | 10 | 0.5 | 0.3 |
| C41 | 401-410 | mixed | 40 | 0.4 | 30 | sphere | 0 | 30 | 0.1 | 0.3 |
| C42 | 411-420 | mixed | 100 | 1 | 30 | cube | 0 | 20 | 0.5 | 0.3 |
| C43 | 421-430 | mixed | 500 | 0.1 | 30 | cube | 0 | 10 | 0.2 | 0.1 |
| C44 | 431-440 | mixed | 500 | 0.1 | 40 | cube | 5 | 20 | 0.1 | 0.3 |
| C45 | 441-450 | mixed | 40 | 1 | 50 | cube | 0 | 20 | 0.1 | 0.3 |
| C46 | 451-460 | mixed | 500 | 0.1 | 40 | cube | 5 | 20 | 0.5 | 0.8 |
| C47 | 461-470 | mixed | 500 | 0.4 | 40 | sphere | -5 | 30 | 0.1 | 0.3 |
| C48 | 471-480 | mixed | 500 | 0.1 | 30 | cube | -5 | 20 | 0.1 | 0.1 |
| C49 | 481-490 | mixed | 40 | 0.1 | 40 | cube | -5 | 10 | 0.2 | 0.3 |
| C50 | 491-500 | mixed | 100 | 0.4 | 30 | cube | 0 | 10 | 0.1 | 0.8 |
| C51 | 501-510 | mixed | 100 | 0.4 | 30 | cube | 0 | 30 | 0.1 | 0.3 |
| C52 | 511-520 | mixed | 40 | 0.4 | 50 | sphere | 0 | 20 | 0.2 | 0.1 |
| C53 | 521-530 | mixed | 40 | 1 | 30 | sphere | 5 | 20 | 0.5 | 0.3 |
| C54 | 531-540 | mixed | 100 | 1 | 30 | cube | 0 | 30 | 0.2 | 0.3 |
| C55 | 541-550 | mixed | 100 | 0.4 | 50 | sphere | -5 | 30 | 0.5 | 0.1 |
| C56 | 551-560 | mixed | 40 | 0.4 | 40 | sphere | -5 | 30 | 0.2 | 0.1 |
| C57 | 561-570 | mixed | 40 | 1 | 50 | sphere | 0 | 10 | 0.2 | 0.3 |
| C58 | 571-580 | mixed | 40 | 0.4 | 30 | cube | 0 | 10 | 0.2 | 0.3 |
| C59 | 581-590 | mixed | 500 | 1 | 40 | cube | -5 | 30 | 0.2 | 0.8 |
| C60 | 591-600 | mixed | 40 | 1 | 40 | cube | 5 | 10 | 0.5 | 0.1 |

## Interpretation

The X axis always retains the original episode positions 1-600. Unrelated episodes are blank. Green circles are successful attempts and red crosses are failures. Each selected condition reuses the same ten starting seeds.
Shape/size changes can alter the initial support height. All physical settings outside the listed variables are held nominal; the same seed is reused across comparisons.
These are the combinations actually collected, not every mathematically possible combination. A failure color describes an outcome; identifying a physical cause requires comparing the controlled settings.
