# Dense collection plot plan

Dataset: `/home/ubuntu/faliure/runs/failure_collection/dense_single_pair_fixed40g`.
Dataset fingerprint: `42702ad022043ffb8e0688e9d3a376957ff9644007e10e312eee49416a78affe`

2983 settings; 307 plots. Each comparison includes the shared nominal attempts.
Edit rows under **Plots** to choose comparisons. Conditions are listed in collection order.
Same/opposite direction describes the ordered parameter sweeps, not an exact physical proportional law.
Shape crossings are categorical and have no same/opposite interpretation.
Linked physical quantities may change: object dynamic friction = static friction × ratio; inertia follows mass/size unless independently scaled.
Starting-position/yaw rows show commanded offsets from each seed’s reset pose; all episodes retain the complete initial pose.

## Variables

| Variable | Meaning | Plot unit |
| --- | --- | --- |
| angular_damping | Object angular damping | coefficient |
| com_x | COM X offset | mm |
| com_y | COM Y offset | mm |
| com_z | COM Z offset | mm |
| dynamic_friction_ratio | Sliding / static friction ratio | ratio |
| finger_friction | Finger friction | coefficient |
| goal_height | Lift height | cm |
| inertia_scale | Inertia scale | multiplier |
| linear_damping | Object linear damping | coefficient |
| mass | Mass | g |
| object_friction | Object friction | coefficient |
| restitution | Object restitution | coefficient |
| shape | Shape | category |
| size | Size | mm |
| spawn_x | Starting X offset | mm |
| spawn_y | Starting Y offset | mm |
| spawn_yaw | Starting yaw offset | degrees |
| table_friction | Table friction | coefficient |

## Plots

| Plot | Variables | Conditions | Reference | Title |
| --- | --- | --- | --- | --- |
| angular_damping_only | angular_damping | C01,C127,C128,C129,C130,C131,C132,C133,C134,C135,C136 | yes | Object angular damping only; other factors nominal |
| com_x_only | com_x | C01,C67,C68,C69,C70,C71,C72,C73,C74,C75,C76 | yes | COM X offset only; other factors nominal |
| com_y_only | com_y | C01,C77,C78,C79,C80,C81,C82,C83,C84,C85,C86 | yes | COM Y offset only; other factors nominal |
| com_z_only | com_z | C01,C87,C88,C89,C90,C91,C92,C93,C94,C95,C96 | yes | COM Z offset only; other factors nominal |
| dynamic_friction_ratio_only | dynamic_friction_ratio | C01,C24,C25,C26,C27,C28,C29,C30,C31,C32,C33 | yes | Sliding / static friction ratio only; other factors nominal |
| finger_friction_only | finger_friction | C01,C34,C35,C36,C37,C38,C39,C40,C41,C42,C43,C44 | yes | Finger friction only; other factors nominal |
| goal_height_only | goal_height | C01,C97,C98,C99,C100,C101,C102,C103,C104,C105,C106 | yes | Lift height only; other factors nominal |
| inertia_scale_only | inertia_scale | C01,C167,C168,C169,C170,C171,C172,C173,C174,C175,C176,C177 | yes | Inertia scale only; other factors nominal |
| linear_damping_only | linear_damping | C01,C117,C118,C119,C120,C121,C122,C123,C124,C125,C126 | yes | Object linear damping only; other factors nominal |
| mass_only | mass | C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12 | yes | Mass only; other factors nominal |
| object_friction_only | object_friction | C01,C13,C14,C15,C16,C17,C18,C19,C20,C21,C22,C23 | yes | Object friction only; other factors nominal |
| restitution_only | restitution | C01,C107,C108,C109,C110,C111,C112,C113,C114,C115,C116 | yes | Object restitution only; other factors nominal |
| shape_only | shape | C01,C66 | yes | Shape only; other factors nominal |
| size_only | size | C01,C56,C57,C58,C59,C60,C61,C62,C63,C64,C65 | yes | Size only; other factors nominal |
| spawn_x_only | spawn_x | C01,C137,C138,C139,C140,C141,C142,C143,C144,C145,C146 | yes | Starting X offset only; other factors nominal |
| spawn_y_only | spawn_y | C01,C147,C148,C149,C150,C151,C152,C153,C154,C155,C156 | yes | Starting Y offset only; other factors nominal |
| spawn_yaw_only | spawn_yaw | C01,C157,C158,C159,C160,C161,C162,C163,C164,C165,C166 | yes | Starting yaw offset only; other factors nominal |
| table_friction_only | table_friction | C01,C45,C46,C47,C48,C49,C50,C51,C52,C53,C54,C55 | yes | Table friction only; other factors nominal |
| angular_damping_inertia_scale_together | angular_damping,inertia_scale | C168,C2845,C2846,C2847,C2848,C2849,C2850,C2851,C2852,C2853,C2854 | yes | Object angular damping + Inertia scale: same-direction sweep |
| angular_damping_spawn_x_together | angular_damping,spawn_x | C131,C138,C2791,C2792,C2793,C2794,C2795,C2796,C2797,C2798,C2799 | yes | Object angular damping + Starting X offset: same-direction sweep |
| angular_damping_spawn_y_together | angular_damping,spawn_y | C131,C148,C2809,C2810,C2811,C2812,C2813,C2814,C2815,C2816,C2817 | yes | Object angular damping + Starting Y offset: same-direction sweep |
| angular_damping_spawn_yaw_together | angular_damping,spawn_yaw | C131,C158,C2827,C2828,C2829,C2830,C2831,C2832,C2833,C2834,C2835 | yes | Object angular damping + Starting yaw offset: same-direction sweep |
| com_x_angular_damping_together | com_x,angular_damping | C68,C131,C2033,C2034,C2035,C2036,C2037,C2038,C2039,C2040,C2041 | yes | COM X offset + Object angular damping: same-direction sweep |
| com_x_com_y_together | com_x,com_y | C01,C1937,C1938,C1939,C1940,C1941,C1942,C1943,C1944,C1945,C1946 | yes | COM X offset + COM Y offset: same-direction sweep |
| com_x_com_z_together | com_x,com_z | C01,C1957,C1958,C1959,C1960,C1961,C1962,C1963,C1964,C1965,C1966 | yes | COM X offset + COM Z offset: same-direction sweep |
| com_x_goal_height_together | com_x,goal_height | C01,C1977,C1978,C1979,C1980,C1981,C1982,C1983,C1984,C1985,C1986 | yes | COM X offset + Lift height: same-direction sweep |
| com_x_inertia_scale_together | com_x,inertia_scale | C172,C2111,C2112,C2113,C2114,C2115,C2116,C2117,C2118,C2119,C2120 | yes | COM X offset + Inertia scale: same-direction sweep |
| com_x_linear_damping_together | com_x,linear_damping | C67,C121,C2015,C2016,C2017,C2018,C2019,C2020,C2021,C2022,C2023 | yes | COM X offset + Object linear damping: same-direction sweep |
| com_x_restitution_together | com_x,restitution | C67,C111,C1997,C1998,C1999,C2000,C2001,C2002,C2003,C2004,C2005 | yes | COM X offset + Object restitution: same-direction sweep |
| com_x_spawn_x_together | com_x,spawn_x | C01,C2051,C2052,C2053,C2054,C2055,C2056,C2057,C2058,C2059,C2060 | yes | COM X offset + Starting X offset: same-direction sweep |
| com_x_spawn_y_together | com_x,spawn_y | C01,C2071,C2072,C2073,C2074,C2075,C2076,C2077,C2078,C2079,C2080 | yes | COM X offset + Starting Y offset: same-direction sweep |
| com_x_spawn_yaw_together | com_x,spawn_yaw | C01,C2091,C2092,C2093,C2094,C2095,C2096,C2097,C2098,C2099,C2100 | yes | COM X offset + Starting yaw offset: same-direction sweep |
| com_y_angular_damping_together | com_y,angular_damping | C78,C131,C2207,C2208,C2209,C2210,C2211,C2212,C2213,C2214,C2215 | yes | COM Y offset + Object angular damping: same-direction sweep |
| com_y_com_z_together | com_y,com_z | C01,C2131,C2132,C2133,C2134,C2135,C2136,C2137,C2138,C2139,C2140 | yes | COM Y offset + COM Z offset: same-direction sweep |
| com_y_goal_height_together | com_y,goal_height | C01,C2151,C2152,C2153,C2154,C2155,C2156,C2157,C2158,C2159,C2160 | yes | COM Y offset + Lift height: same-direction sweep |
| com_y_inertia_scale_together | com_y,inertia_scale | C172,C2285,C2286,C2287,C2288,C2289,C2290,C2291,C2292,C2293,C2294 | yes | COM Y offset + Inertia scale: same-direction sweep |
| com_y_linear_damping_together | com_y,linear_damping | C77,C121,C2189,C2190,C2191,C2192,C2193,C2194,C2195,C2196,C2197 | yes | COM Y offset + Object linear damping: same-direction sweep |
| com_y_restitution_together | com_y,restitution | C77,C111,C2171,C2172,C2173,C2174,C2175,C2176,C2177,C2178,C2179 | yes | COM Y offset + Object restitution: same-direction sweep |
| com_y_spawn_x_together | com_y,spawn_x | C01,C2225,C2226,C2227,C2228,C2229,C2230,C2231,C2232,C2233,C2234 | yes | COM Y offset + Starting X offset: same-direction sweep |
| com_y_spawn_y_together | com_y,spawn_y | C01,C2245,C2246,C2247,C2248,C2249,C2250,C2251,C2252,C2253,C2254 | yes | COM Y offset + Starting Y offset: same-direction sweep |
| com_y_spawn_yaw_together | com_y,spawn_yaw | C01,C2265,C2266,C2267,C2268,C2269,C2270,C2271,C2272,C2273,C2274 | yes | COM Y offset + Starting yaw offset: same-direction sweep |
| com_z_angular_damping_together | com_z,angular_damping | C88,C131,C2361,C2362,C2363,C2364,C2365,C2366,C2367,C2368,C2369 | yes | COM Z offset + Object angular damping: same-direction sweep |
| com_z_goal_height_together | com_z,goal_height | C01,C2305,C2306,C2307,C2308,C2309,C2310,C2311,C2312,C2313,C2314 | yes | COM Z offset + Lift height: same-direction sweep |
| com_z_inertia_scale_together | com_z,inertia_scale | C172,C2439,C2440,C2441,C2442,C2443,C2444,C2445,C2446,C2447,C2448 | yes | COM Z offset + Inertia scale: same-direction sweep |
| com_z_linear_damping_together | com_z,linear_damping | C87,C121,C2343,C2344,C2345,C2346,C2347,C2348,C2349,C2350,C2351 | yes | COM Z offset + Object linear damping: same-direction sweep |
| com_z_restitution_together | com_z,restitution | C87,C111,C2325,C2326,C2327,C2328,C2329,C2330,C2331,C2332,C2333 | yes | COM Z offset + Object restitution: same-direction sweep |
| com_z_spawn_x_together | com_z,spawn_x | C01,C2379,C2380,C2381,C2382,C2383,C2384,C2385,C2386,C2387,C2388 | yes | COM Z offset + Starting X offset: same-direction sweep |
| com_z_spawn_y_together | com_z,spawn_y | C01,C2399,C2400,C2401,C2402,C2403,C2404,C2405,C2406,C2407,C2408 | yes | COM Z offset + Starting Y offset: same-direction sweep |
| com_z_spawn_yaw_together | com_z,spawn_yaw | C01,C2419,C2420,C2421,C2422,C2423,C2424,C2425,C2426,C2427,C2428 | yes | COM Z offset + Starting yaw offset: same-direction sweep |
| dynamic_friction_ratio_angular_damping_together | dynamic_friction_ratio,angular_damping | C25,C136,C993,C994,C995,C996,C997,C998,C999,C1000,C1001 | yes | Sliding / static friction ratio + Object angular damping: same-direction sweep |
| dynamic_friction_ratio_com_x_together | dynamic_friction_ratio,com_x | C29,C76,C885,C886,C887,C888,C889,C890,C891,C892,C893 | yes | Sliding / static friction ratio + COM X offset: same-direction sweep |
| dynamic_friction_ratio_com_y_together | dynamic_friction_ratio,com_y | C29,C86,C903,C904,C905,C906,C907,C908,C909,C910,C911 | yes | Sliding / static friction ratio + COM Y offset: same-direction sweep |
| dynamic_friction_ratio_com_z_together | dynamic_friction_ratio,com_z | C29,C96,C921,C922,C923,C924,C925,C926,C927,C928,C929 | yes | Sliding / static friction ratio + COM Z offset: same-direction sweep |
| dynamic_friction_ratio_finger_friction_together | dynamic_friction_ratio,finger_friction | C44,C819,C820,C821,C822,C823,C824,C825,C826,C827,C828 | yes | Sliding / static friction ratio + Finger friction: same-direction sweep |
| dynamic_friction_ratio_goal_height_together | dynamic_friction_ratio,goal_height | C29,C106,C939,C940,C941,C942,C943,C944,C945,C946,C947 | yes | Sliding / static friction ratio + Lift height: same-direction sweep |
| dynamic_friction_ratio_inertia_scale_together | dynamic_friction_ratio,inertia_scale | C177,C1064,C1065,C1066,C1067,C1068,C1069,C1070,C1071,C1072,C1073 | yes | Sliding / static friction ratio + Inertia scale: same-direction sweep |
| dynamic_friction_ratio_linear_damping_together | dynamic_friction_ratio,linear_damping | C24,C126,C975,C976,C977,C978,C979,C980,C981,C982,C983 | yes | Sliding / static friction ratio + Object linear damping: same-direction sweep |
| dynamic_friction_ratio_restitution_together | dynamic_friction_ratio,restitution | C24,C116,C957,C958,C959,C960,C961,C962,C963,C964,C965 | yes | Sliding / static friction ratio + Object restitution: same-direction sweep |
| dynamic_friction_ratio_size_together | dynamic_friction_ratio,size | C29,C65,C857,C858,C859,C860,C861,C862,C863,C864,C865 | yes | Sliding / static friction ratio + Size: same-direction sweep |
| dynamic_friction_ratio_spawn_x_together | dynamic_friction_ratio,spawn_x | C29,C146,C1010,C1011,C1012,C1013,C1014,C1015,C1016,C1017,C1018 | yes | Sliding / static friction ratio + Starting X offset: same-direction sweep |
| dynamic_friction_ratio_spawn_y_together | dynamic_friction_ratio,spawn_y | C29,C156,C1028,C1029,C1030,C1031,C1032,C1033,C1034,C1035,C1036 | yes | Sliding / static friction ratio + Starting Y offset: same-direction sweep |
| dynamic_friction_ratio_spawn_yaw_together | dynamic_friction_ratio,spawn_yaw | C29,C166,C1046,C1047,C1048,C1049,C1050,C1051,C1052,C1053,C1054 | yes | Sliding / static friction ratio + Starting yaw offset: same-direction sweep |
| dynamic_friction_ratio_table_friction_together | dynamic_friction_ratio,table_friction | C55,C838,C839,C840,C841,C842,C843,C844,C845,C846,C847 | yes | Sliding / static friction ratio + Table friction: same-direction sweep |
| finger_friction_angular_damping_together | finger_friction,angular_damping | C35,C1253,C1254,C1255,C1256,C1257,C1258,C1259,C1260,C1261,C1262 | yes | Finger friction + Object angular damping: same-direction sweep |
| finger_friction_com_x_together | finger_friction,com_x | C39,C1135,C1136,C1137,C1138,C1139,C1140,C1141,C1142,C1143,C1144 | yes | Finger friction + COM X offset: same-direction sweep |
| finger_friction_com_y_together | finger_friction,com_y | C39,C1155,C1156,C1157,C1158,C1159,C1160,C1161,C1162,C1163,C1164 | yes | Finger friction + COM Y offset: same-direction sweep |
| finger_friction_com_z_together | finger_friction,com_z | C39,C1175,C1176,C1177,C1178,C1179,C1180,C1181,C1182,C1183,C1184 | yes | Finger friction + COM Z offset: same-direction sweep |
| finger_friction_goal_height_together | finger_friction,goal_height | C39,C1195,C1196,C1197,C1198,C1199,C1200,C1201,C1202,C1203,C1204 | yes | Finger friction + Lift height: same-direction sweep |
| finger_friction_inertia_scale_together | finger_friction,inertia_scale | C1332,C1333,C1334,C1335,C1336,C1337,C1338,C1339,C1340,C1341,C1342 | yes | Finger friction + Inertia scale: same-direction sweep |
| finger_friction_linear_damping_together | finger_friction,linear_damping | C34,C1234,C1235,C1236,C1237,C1238,C1239,C1240,C1241,C1242,C1243 | yes | Finger friction + Object linear damping: same-direction sweep |
| finger_friction_restitution_together | finger_friction,restitution | C34,C1215,C1216,C1217,C1218,C1219,C1220,C1221,C1222,C1223,C1224 | yes | Finger friction + Object restitution: same-direction sweep |
| finger_friction_size_together | finger_friction,size | C39,C1104,C1105,C1106,C1107,C1108,C1109,C1110,C1111,C1112,C1113 | yes | Finger friction + Size: same-direction sweep |
| finger_friction_spawn_x_together | finger_friction,spawn_x | C39,C1272,C1273,C1274,C1275,C1276,C1277,C1278,C1279,C1280,C1281 | yes | Finger friction + Starting X offset: same-direction sweep |
| finger_friction_spawn_y_together | finger_friction,spawn_y | C39,C1292,C1293,C1294,C1295,C1296,C1297,C1298,C1299,C1300,C1301 | yes | Finger friction + Starting Y offset: same-direction sweep |
| finger_friction_spawn_yaw_together | finger_friction,spawn_yaw | C39,C1312,C1313,C1314,C1315,C1316,C1317,C1318,C1319,C1320,C1321 | yes | Finger friction + Starting yaw offset: same-direction sweep |
| finger_friction_table_friction_together | finger_friction,table_friction | C1083,C1084,C1085,C1086,C1087,C1088,C1089,C1090,C1091,C1092,C1093 | yes | Finger friction + Table friction: same-direction sweep |
| goal_height_angular_damping_together | goal_height,angular_damping | C98,C131,C2495,C2496,C2497,C2498,C2499,C2500,C2501,C2502,C2503 | yes | Lift height + Object angular damping: same-direction sweep |
| goal_height_inertia_scale_together | goal_height,inertia_scale | C172,C2573,C2574,C2575,C2576,C2577,C2578,C2579,C2580,C2581,C2582 | yes | Lift height + Inertia scale: same-direction sweep |
| goal_height_linear_damping_together | goal_height,linear_damping | C97,C121,C2477,C2478,C2479,C2480,C2481,C2482,C2483,C2484,C2485 | yes | Lift height + Object linear damping: same-direction sweep |
| goal_height_restitution_together | goal_height,restitution | C97,C111,C2459,C2460,C2461,C2462,C2463,C2464,C2465,C2466,C2467 | yes | Lift height + Object restitution: same-direction sweep |
| goal_height_spawn_x_together | goal_height,spawn_x | C01,C2513,C2514,C2515,C2516,C2517,C2518,C2519,C2520,C2521,C2522 | yes | Lift height + Starting X offset: same-direction sweep |
| goal_height_spawn_y_together | goal_height,spawn_y | C01,C2533,C2534,C2535,C2536,C2537,C2538,C2539,C2540,C2541,C2542 | yes | Lift height + Starting Y offset: same-direction sweep |
| goal_height_spawn_yaw_together | goal_height,spawn_yaw | C01,C2553,C2554,C2555,C2556,C2557,C2558,C2559,C2560,C2561,C2562 | yes | Lift height + Starting yaw offset: same-direction sweep |
| linear_damping_angular_damping_together | linear_damping,angular_damping | C117,C127,C2701,C2702,C2703,C2704,C2705,C2706,C2707,C2708,C2709 | yes | Object linear damping + Object angular damping: same-direction sweep |
| linear_damping_inertia_scale_together | linear_damping,inertia_scale | C167,C2772,C2773,C2774,C2775,C2776,C2777,C2778,C2779,C2780,C2781 | yes | Object linear damping + Inertia scale: same-direction sweep |
| linear_damping_spawn_x_together | linear_damping,spawn_x | C121,C137,C2718,C2719,C2720,C2721,C2722,C2723,C2724,C2725,C2726 | yes | Object linear damping + Starting X offset: same-direction sweep |
| linear_damping_spawn_y_together | linear_damping,spawn_y | C121,C147,C2736,C2737,C2738,C2739,C2740,C2741,C2742,C2743,C2744 | yes | Object linear damping + Starting Y offset: same-direction sweep |
| linear_damping_spawn_yaw_together | linear_damping,spawn_yaw | C121,C157,C2754,C2755,C2756,C2757,C2758,C2759,C2760,C2761,C2762 | yes | Object linear damping + Starting yaw offset: same-direction sweep |
| mass_angular_damping_together | mass,angular_damping | C03,C409,C410,C411,C412,C413,C414,C415,C416,C417,C418 | yes | Mass + Object angular damping: same-direction sweep |
| mass_com_x_together | mass,com_x | C07,C291,C292,C293,C294,C295,C296,C297,C298,C299,C300 | yes | Mass + COM X offset: same-direction sweep |
| mass_com_y_together | mass,com_y | C07,C311,C312,C313,C314,C315,C316,C317,C318,C319,C320 | yes | Mass + COM Y offset: same-direction sweep |
| mass_com_z_together | mass,com_z | C07,C331,C332,C333,C334,C335,C336,C337,C338,C339,C340 | yes | Mass + COM Z offset: same-direction sweep |
| mass_dynamic_friction_ratio_together | mass,dynamic_friction_ratio | C12,C199,C200,C201,C202,C203,C204,C205,C206,C207,C208 | yes | Mass + Sliding / static friction ratio: same-direction sweep |
| mass_finger_friction_together | mass,finger_friction | C218,C219,C220,C221,C222,C223,C224,C225,C226,C227,C228 | yes | Mass + Finger friction: same-direction sweep |
| mass_goal_height_together | mass,goal_height | C07,C351,C352,C353,C354,C355,C356,C357,C358,C359,C360 | yes | Mass + Lift height: same-direction sweep |
| mass_inertia_scale_together | mass,inertia_scale | C488,C489,C490,C491,C492,C493,C494,C495,C496,C497,C498 | yes | Mass + Inertia scale: same-direction sweep |
| mass_linear_damping_together | mass,linear_damping | C02,C390,C391,C392,C393,C394,C395,C396,C397,C398,C399 | yes | Mass + Object linear damping: same-direction sweep |
| mass_object_friction_together | mass,object_friction | C178,C179,C180,C181,C182,C183,C184,C185,C186,C187,C188 | yes | Mass + Object friction: same-direction sweep |
| mass_restitution_together | mass,restitution | C02,C371,C372,C373,C374,C375,C376,C377,C378,C379,C380 | yes | Mass + Object restitution: same-direction sweep |
| mass_size_together | mass,size | C07,C260,C261,C262,C263,C264,C265,C266,C267,C268,C269 | yes | Mass + Size: same-direction sweep |
| mass_spawn_x_together | mass,spawn_x | C07,C428,C429,C430,C431,C432,C433,C434,C435,C436,C437 | yes | Mass + Starting X offset: same-direction sweep |
| mass_spawn_y_together | mass,spawn_y | C07,C448,C449,C450,C451,C452,C453,C454,C455,C456,C457 | yes | Mass + Starting Y offset: same-direction sweep |
| mass_spawn_yaw_together | mass,spawn_yaw | C07,C468,C469,C470,C471,C472,C473,C474,C475,C476,C477 | yes | Mass + Starting yaw offset: same-direction sweep |
| mass_table_friction_together | mass,table_friction | C239,C240,C241,C242,C243,C244,C245,C246,C247,C248,C249 | yes | Mass + Table friction: same-direction sweep |
| object_friction_angular_damping_together | object_friction,angular_damping | C14,C719,C720,C721,C722,C723,C724,C725,C726,C727,C728 | yes | Object friction + Object angular damping: same-direction sweep |
| object_friction_com_x_together | object_friction,com_x | C18,C601,C602,C603,C604,C605,C606,C607,C608,C609,C610 | yes | Object friction + COM X offset: same-direction sweep |
| object_friction_com_y_together | object_friction,com_y | C18,C621,C622,C623,C624,C625,C626,C627,C628,C629,C630 | yes | Object friction + COM Y offset: same-direction sweep |
| object_friction_com_z_together | object_friction,com_z | C18,C641,C642,C643,C644,C645,C646,C647,C648,C649,C650 | yes | Object friction + COM Z offset: same-direction sweep |
| object_friction_dynamic_friction_ratio_together | object_friction,dynamic_friction_ratio | C23,C509,C510,C511,C512,C513,C514,C515,C516,C517,C518 | yes | Object friction + Sliding / static friction ratio: same-direction sweep |
| object_friction_finger_friction_together | object_friction,finger_friction | C528,C529,C530,C531,C532,C533,C534,C535,C536,C537,C538 | yes | Object friction + Finger friction: same-direction sweep |
| object_friction_goal_height_together | object_friction,goal_height | C18,C661,C662,C663,C664,C665,C666,C667,C668,C669,C670 | yes | Object friction + Lift height: same-direction sweep |
| object_friction_inertia_scale_together | object_friction,inertia_scale | C798,C799,C800,C801,C802,C803,C804,C805,C806,C807,C808 | yes | Object friction + Inertia scale: same-direction sweep |
| object_friction_linear_damping_together | object_friction,linear_damping | C13,C700,C701,C702,C703,C704,C705,C706,C707,C708,C709 | yes | Object friction + Object linear damping: same-direction sweep |
| object_friction_restitution_together | object_friction,restitution | C13,C681,C682,C683,C684,C685,C686,C687,C688,C689,C690 | yes | Object friction + Object restitution: same-direction sweep |
| object_friction_size_together | object_friction,size | C18,C570,C571,C572,C573,C574,C575,C576,C577,C578,C579 | yes | Object friction + Size: same-direction sweep |
| object_friction_spawn_x_together | object_friction,spawn_x | C18,C738,C739,C740,C741,C742,C743,C744,C745,C746,C747 | yes | Object friction + Starting X offset: same-direction sweep |
| object_friction_spawn_y_together | object_friction,spawn_y | C18,C758,C759,C760,C761,C762,C763,C764,C765,C766,C767 | yes | Object friction + Starting Y offset: same-direction sweep |
| object_friction_spawn_yaw_together | object_friction,spawn_yaw | C18,C778,C779,C780,C781,C782,C783,C784,C785,C786,C787 | yes | Object friction + Starting yaw offset: same-direction sweep |
| object_friction_table_friction_together | object_friction,table_friction | C549,C550,C551,C552,C553,C554,C555,C556,C557,C558,C559 | yes | Object friction + Table friction: same-direction sweep |
| restitution_angular_damping_together | restitution,angular_damping | C107,C127,C2611,C2612,C2613,C2614,C2615,C2616,C2617,C2618,C2619 | yes | Object restitution + Object angular damping: same-direction sweep |
| restitution_inertia_scale_together | restitution,inertia_scale | C167,C2682,C2683,C2684,C2685,C2686,C2687,C2688,C2689,C2690,C2691 | yes | Object restitution + Inertia scale: same-direction sweep |
| restitution_linear_damping_together | restitution,linear_damping | C01,C2593,C2594,C2595,C2596,C2597,C2598,C2599,C2600,C2601,C2602 | yes | Object restitution + Object linear damping: same-direction sweep |
| restitution_spawn_x_together | restitution,spawn_x | C111,C137,C2628,C2629,C2630,C2631,C2632,C2633,C2634,C2635,C2636 | yes | Object restitution + Starting X offset: same-direction sweep |
| restitution_spawn_y_together | restitution,spawn_y | C111,C147,C2646,C2647,C2648,C2649,C2650,C2651,C2652,C2653,C2654 | yes | Object restitution + Starting Y offset: same-direction sweep |
| restitution_spawn_yaw_together | restitution,spawn_yaw | C111,C157,C2664,C2665,C2666,C2667,C2668,C2669,C2670,C2671,C2672 | yes | Object restitution + Starting yaw offset: same-direction sweep |
| size_angular_damping_together | size,angular_damping | C57,C131,C1728,C1729,C1730,C1731,C1732,C1733,C1734,C1735,C1736 | yes | Size + Object angular damping: same-direction sweep |
| size_com_x_together | size,com_x | C01,C1612,C1613,C1614,C1615,C1616,C1617,C1618,C1619,C1620,C1621 | yes | Size + COM X offset: same-direction sweep |
| size_com_y_together | size,com_y | C01,C1632,C1633,C1634,C1635,C1636,C1637,C1638,C1639,C1640,C1641 | yes | Size + COM Y offset: same-direction sweep |
| size_com_z_together | size,com_z | C01,C1652,C1653,C1654,C1655,C1656,C1657,C1658,C1659,C1660,C1661 | yes | Size + COM Z offset: same-direction sweep |
| size_goal_height_together | size,goal_height | C01,C1672,C1673,C1674,C1675,C1676,C1677,C1678,C1679,C1680,C1681 | yes | Size + Lift height: same-direction sweep |
| size_inertia_scale_together | size,inertia_scale | C172,C1806,C1807,C1808,C1809,C1810,C1811,C1812,C1813,C1814,C1815 | yes | Size + Inertia scale: same-direction sweep |
| size_linear_damping_together | size,linear_damping | C56,C121,C1710,C1711,C1712,C1713,C1714,C1715,C1716,C1717,C1718 | yes | Size + Object linear damping: same-direction sweep |
| size_restitution_together | size,restitution | C56,C111,C1692,C1693,C1694,C1695,C1696,C1697,C1698,C1699,C1700 | yes | Size + Object restitution: same-direction sweep |
| size_spawn_x_together | size,spawn_x | C01,C1746,C1747,C1748,C1749,C1750,C1751,C1752,C1753,C1754,C1755 | yes | Size + Starting X offset: same-direction sweep |
| size_spawn_y_together | size,spawn_y | C01,C1766,C1767,C1768,C1769,C1770,C1771,C1772,C1773,C1774,C1775 | yes | Size + Starting Y offset: same-direction sweep |
| size_spawn_yaw_together | size,spawn_yaw | C01,C1786,C1787,C1788,C1789,C1790,C1791,C1792,C1793,C1794,C1795 | yes | Size + Starting yaw offset: same-direction sweep |
| spawn_x_inertia_scale_together | spawn_x,inertia_scale | C172,C2904,C2905,C2906,C2907,C2908,C2909,C2910,C2911,C2912,C2913 | yes | Starting X offset + Inertia scale: same-direction sweep |
| spawn_x_spawn_y_together | spawn_x,spawn_y | C01,C2864,C2865,C2866,C2867,C2868,C2869,C2870,C2871,C2872,C2873 | yes | Starting X offset + Starting Y offset: same-direction sweep |
| spawn_x_spawn_yaw_together | spawn_x,spawn_yaw | C01,C2884,C2885,C2886,C2887,C2888,C2889,C2890,C2891,C2892,C2893 | yes | Starting X offset + Starting yaw offset: same-direction sweep |
| spawn_y_inertia_scale_together | spawn_y,inertia_scale | C172,C2944,C2945,C2946,C2947,C2948,C2949,C2950,C2951,C2952,C2953 | yes | Starting Y offset + Inertia scale: same-direction sweep |
| spawn_y_spawn_yaw_together | spawn_y,spawn_yaw | C01,C2924,C2925,C2926,C2927,C2928,C2929,C2930,C2931,C2932,C2933 | yes | Starting Y offset + Starting yaw offset: same-direction sweep |
| spawn_yaw_inertia_scale_together | spawn_yaw,inertia_scale | C172,C2964,C2965,C2966,C2967,C2968,C2969,C2970,C2971,C2972,C2973 | yes | Starting yaw offset + Inertia scale: same-direction sweep |
| table_friction_angular_damping_together | table_friction,angular_damping | C46,C1502,C1503,C1504,C1505,C1506,C1507,C1508,C1509,C1510,C1511 | yes | Table friction + Object angular damping: same-direction sweep |
| table_friction_com_x_together | table_friction,com_x | C50,C1384,C1385,C1386,C1387,C1388,C1389,C1390,C1391,C1392,C1393 | yes | Table friction + COM X offset: same-direction sweep |
| table_friction_com_y_together | table_friction,com_y | C50,C1404,C1405,C1406,C1407,C1408,C1409,C1410,C1411,C1412,C1413 | yes | Table friction + COM Y offset: same-direction sweep |
| table_friction_com_z_together | table_friction,com_z | C50,C1424,C1425,C1426,C1427,C1428,C1429,C1430,C1431,C1432,C1433 | yes | Table friction + COM Z offset: same-direction sweep |
| table_friction_goal_height_together | table_friction,goal_height | C50,C1444,C1445,C1446,C1447,C1448,C1449,C1450,C1451,C1452,C1453 | yes | Table friction + Lift height: same-direction sweep |
| table_friction_inertia_scale_together | table_friction,inertia_scale | C1581,C1582,C1583,C1584,C1585,C1586,C1587,C1588,C1589,C1590,C1591 | yes | Table friction + Inertia scale: same-direction sweep |
| table_friction_linear_damping_together | table_friction,linear_damping | C45,C1483,C1484,C1485,C1486,C1487,C1488,C1489,C1490,C1491,C1492 | yes | Table friction + Object linear damping: same-direction sweep |
| table_friction_restitution_together | table_friction,restitution | C45,C1464,C1465,C1466,C1467,C1468,C1469,C1470,C1471,C1472,C1473 | yes | Table friction + Object restitution: same-direction sweep |
| table_friction_size_together | table_friction,size | C50,C1353,C1354,C1355,C1356,C1357,C1358,C1359,C1360,C1361,C1362 | yes | Table friction + Size: same-direction sweep |
| table_friction_spawn_x_together | table_friction,spawn_x | C50,C1521,C1522,C1523,C1524,C1525,C1526,C1527,C1528,C1529,C1530 | yes | Table friction + Starting X offset: same-direction sweep |
| table_friction_spawn_y_together | table_friction,spawn_y | C50,C1541,C1542,C1543,C1544,C1545,C1546,C1547,C1548,C1549,C1550 | yes | Table friction + Starting Y offset: same-direction sweep |
| table_friction_spawn_yaw_together | table_friction,spawn_yaw | C50,C1561,C1562,C1563,C1564,C1565,C1566,C1567,C1568,C1569,C1570 | yes | Table friction + Starting yaw offset: same-direction sweep |
| angular_damping_inertia_scale_opposite | angular_damping,inertia_scale | C176,C2849,C2855,C2856,C2857,C2858,C2859,C2860,C2861,C2862,C2863 | yes | Object angular damping + Inertia scale: opposite-direction sweep |
| angular_damping_spawn_x_opposite | angular_damping,spawn_x | C131,C145,C2800,C2801,C2802,C2803,C2804,C2805,C2806,C2807,C2808 | yes | Object angular damping + Starting X offset: opposite-direction sweep |
| angular_damping_spawn_y_opposite | angular_damping,spawn_y | C131,C155,C2818,C2819,C2820,C2821,C2822,C2823,C2824,C2825,C2826 | yes | Object angular damping + Starting Y offset: opposite-direction sweep |
| angular_damping_spawn_yaw_opposite | angular_damping,spawn_yaw | C131,C165,C2836,C2837,C2838,C2839,C2840,C2841,C2842,C2843,C2844 | yes | Object angular damping + Starting yaw offset: opposite-direction sweep |
| com_x_angular_damping_opposite | com_x,angular_damping | C75,C131,C2042,C2043,C2044,C2045,C2046,C2047,C2048,C2049,C2050 | yes | COM X offset + Object angular damping: opposite-direction sweep |
| com_x_com_y_opposite | com_x,com_y | C01,C1947,C1948,C1949,C1950,C1951,C1952,C1953,C1954,C1955,C1956 | yes | COM X offset + COM Y offset: opposite-direction sweep |
| com_x_com_z_opposite | com_x,com_z | C01,C1967,C1968,C1969,C1970,C1971,C1972,C1973,C1974,C1975,C1976 | yes | COM X offset + COM Z offset: opposite-direction sweep |
| com_x_goal_height_opposite | com_x,goal_height | C01,C1987,C1988,C1989,C1990,C1991,C1992,C1993,C1994,C1995,C1996 | yes | COM X offset + Lift height: opposite-direction sweep |
| com_x_inertia_scale_opposite | com_x,inertia_scale | C172,C2121,C2122,C2123,C2124,C2125,C2126,C2127,C2128,C2129,C2130 | yes | COM X offset + Inertia scale: opposite-direction sweep |
| com_x_linear_damping_opposite | com_x,linear_damping | C76,C121,C2024,C2025,C2026,C2027,C2028,C2029,C2030,C2031,C2032 | yes | COM X offset + Object linear damping: opposite-direction sweep |
| com_x_restitution_opposite | com_x,restitution | C76,C111,C2006,C2007,C2008,C2009,C2010,C2011,C2012,C2013,C2014 | yes | COM X offset + Object restitution: opposite-direction sweep |
| com_x_spawn_x_opposite | com_x,spawn_x | C01,C2061,C2062,C2063,C2064,C2065,C2066,C2067,C2068,C2069,C2070 | yes | COM X offset + Starting X offset: opposite-direction sweep |
| com_x_spawn_y_opposite | com_x,spawn_y | C01,C2081,C2082,C2083,C2084,C2085,C2086,C2087,C2088,C2089,C2090 | yes | COM X offset + Starting Y offset: opposite-direction sweep |
| com_x_spawn_yaw_opposite | com_x,spawn_yaw | C01,C2101,C2102,C2103,C2104,C2105,C2106,C2107,C2108,C2109,C2110 | yes | COM X offset + Starting yaw offset: opposite-direction sweep |
| com_y_angular_damping_opposite | com_y,angular_damping | C85,C131,C2216,C2217,C2218,C2219,C2220,C2221,C2222,C2223,C2224 | yes | COM Y offset + Object angular damping: opposite-direction sweep |
| com_y_com_z_opposite | com_y,com_z | C01,C2141,C2142,C2143,C2144,C2145,C2146,C2147,C2148,C2149,C2150 | yes | COM Y offset + COM Z offset: opposite-direction sweep |
| com_y_goal_height_opposite | com_y,goal_height | C01,C2161,C2162,C2163,C2164,C2165,C2166,C2167,C2168,C2169,C2170 | yes | COM Y offset + Lift height: opposite-direction sweep |
| com_y_inertia_scale_opposite | com_y,inertia_scale | C172,C2295,C2296,C2297,C2298,C2299,C2300,C2301,C2302,C2303,C2304 | yes | COM Y offset + Inertia scale: opposite-direction sweep |
| com_y_linear_damping_opposite | com_y,linear_damping | C86,C121,C2198,C2199,C2200,C2201,C2202,C2203,C2204,C2205,C2206 | yes | COM Y offset + Object linear damping: opposite-direction sweep |
| com_y_restitution_opposite | com_y,restitution | C86,C111,C2180,C2181,C2182,C2183,C2184,C2185,C2186,C2187,C2188 | yes | COM Y offset + Object restitution: opposite-direction sweep |
| com_y_spawn_x_opposite | com_y,spawn_x | C01,C2235,C2236,C2237,C2238,C2239,C2240,C2241,C2242,C2243,C2244 | yes | COM Y offset + Starting X offset: opposite-direction sweep |
| com_y_spawn_y_opposite | com_y,spawn_y | C01,C2255,C2256,C2257,C2258,C2259,C2260,C2261,C2262,C2263,C2264 | yes | COM Y offset + Starting Y offset: opposite-direction sweep |
| com_y_spawn_yaw_opposite | com_y,spawn_yaw | C01,C2275,C2276,C2277,C2278,C2279,C2280,C2281,C2282,C2283,C2284 | yes | COM Y offset + Starting yaw offset: opposite-direction sweep |
| com_z_angular_damping_opposite | com_z,angular_damping | C95,C131,C2370,C2371,C2372,C2373,C2374,C2375,C2376,C2377,C2378 | yes | COM Z offset + Object angular damping: opposite-direction sweep |
| com_z_goal_height_opposite | com_z,goal_height | C01,C2315,C2316,C2317,C2318,C2319,C2320,C2321,C2322,C2323,C2324 | yes | COM Z offset + Lift height: opposite-direction sweep |
| com_z_inertia_scale_opposite | com_z,inertia_scale | C172,C2449,C2450,C2451,C2452,C2453,C2454,C2455,C2456,C2457,C2458 | yes | COM Z offset + Inertia scale: opposite-direction sweep |
| com_z_linear_damping_opposite | com_z,linear_damping | C96,C121,C2352,C2353,C2354,C2355,C2356,C2357,C2358,C2359,C2360 | yes | COM Z offset + Object linear damping: opposite-direction sweep |
| com_z_restitution_opposite | com_z,restitution | C96,C111,C2334,C2335,C2336,C2337,C2338,C2339,C2340,C2341,C2342 | yes | COM Z offset + Object restitution: opposite-direction sweep |
| com_z_spawn_x_opposite | com_z,spawn_x | C01,C2389,C2390,C2391,C2392,C2393,C2394,C2395,C2396,C2397,C2398 | yes | COM Z offset + Starting X offset: opposite-direction sweep |
| com_z_spawn_y_opposite | com_z,spawn_y | C01,C2409,C2410,C2411,C2412,C2413,C2414,C2415,C2416,C2417,C2418 | yes | COM Z offset + Starting Y offset: opposite-direction sweep |
| com_z_spawn_yaw_opposite | com_z,spawn_yaw | C01,C2429,C2430,C2431,C2432,C2433,C2434,C2435,C2436,C2437,C2438 | yes | COM Z offset + Starting yaw offset: opposite-direction sweep |
| dynamic_friction_ratio_angular_damping_opposite | dynamic_friction_ratio,angular_damping | C33,C127,C997,C1002,C1003,C1004,C1005,C1006,C1007,C1008,C1009 | yes | Sliding / static friction ratio + Object angular damping: opposite-direction sweep |
| dynamic_friction_ratio_com_x_opposite | dynamic_friction_ratio,com_x | C29,C67,C894,C895,C896,C897,C898,C899,C900,C901,C902 | yes | Sliding / static friction ratio + COM X offset: opposite-direction sweep |
| dynamic_friction_ratio_com_y_opposite | dynamic_friction_ratio,com_y | C29,C77,C912,C913,C914,C915,C916,C917,C918,C919,C920 | yes | Sliding / static friction ratio + COM Y offset: opposite-direction sweep |
| dynamic_friction_ratio_com_z_opposite | dynamic_friction_ratio,com_z | C29,C87,C930,C931,C932,C933,C934,C935,C936,C937,C938 | yes | Sliding / static friction ratio + COM Z offset: opposite-direction sweep |
| dynamic_friction_ratio_finger_friction_opposite | dynamic_friction_ratio,finger_friction | C34,C824,C829,C830,C831,C832,C833,C834,C835,C836,C837 | yes | Sliding / static friction ratio + Finger friction: opposite-direction sweep |
| dynamic_friction_ratio_goal_height_opposite | dynamic_friction_ratio,goal_height | C29,C97,C948,C949,C950,C951,C952,C953,C954,C955,C956 | yes | Sliding / static friction ratio + Lift height: opposite-direction sweep |
| dynamic_friction_ratio_inertia_scale_opposite | dynamic_friction_ratio,inertia_scale | C167,C1069,C1074,C1075,C1076,C1077,C1078,C1079,C1080,C1081,C1082 | yes | Sliding / static friction ratio + Inertia scale: opposite-direction sweep |
| dynamic_friction_ratio_linear_damping_opposite | dynamic_friction_ratio,linear_damping | C01,C979,C984,C985,C986,C987,C988,C989,C990,C991,C992 | yes | Sliding / static friction ratio + Object linear damping: opposite-direction sweep |
| dynamic_friction_ratio_restitution_opposite | dynamic_friction_ratio,restitution | C01,C961,C966,C967,C968,C969,C970,C971,C972,C973,C974 | yes | Sliding / static friction ratio + Object restitution: opposite-direction sweep |
| dynamic_friction_ratio_size_opposite | dynamic_friction_ratio,size | C29,C56,C866,C867,C868,C869,C870,C871,C872,C873,C874 | yes | Sliding / static friction ratio + Size: opposite-direction sweep |
| dynamic_friction_ratio_spawn_x_opposite | dynamic_friction_ratio,spawn_x | C29,C137,C1019,C1020,C1021,C1022,C1023,C1024,C1025,C1026,C1027 | yes | Sliding / static friction ratio + Starting X offset: opposite-direction sweep |
| dynamic_friction_ratio_spawn_y_opposite | dynamic_friction_ratio,spawn_y | C29,C147,C1037,C1038,C1039,C1040,C1041,C1042,C1043,C1044,C1045 | yes | Sliding / static friction ratio + Starting Y offset: opposite-direction sweep |
| dynamic_friction_ratio_spawn_yaw_opposite | dynamic_friction_ratio,spawn_yaw | C29,C157,C1055,C1056,C1057,C1058,C1059,C1060,C1061,C1062,C1063 | yes | Sliding / static friction ratio + Starting yaw offset: opposite-direction sweep |
| dynamic_friction_ratio_table_friction_opposite | dynamic_friction_ratio,table_friction | C45,C843,C848,C849,C850,C851,C852,C853,C854,C855,C856 | yes | Sliding / static friction ratio + Table friction: opposite-direction sweep |
| finger_friction_angular_damping_opposite | finger_friction,angular_damping | C43,C1257,C1263,C1264,C1265,C1266,C1267,C1268,C1269,C1270,C1271 | yes | Finger friction + Object angular damping: opposite-direction sweep |
| finger_friction_com_x_opposite | finger_friction,com_x | C39,C1145,C1146,C1147,C1148,C1149,C1150,C1151,C1152,C1153,C1154 | yes | Finger friction + COM X offset: opposite-direction sweep |
| finger_friction_com_y_opposite | finger_friction,com_y | C39,C1165,C1166,C1167,C1168,C1169,C1170,C1171,C1172,C1173,C1174 | yes | Finger friction + COM Y offset: opposite-direction sweep |
| finger_friction_com_z_opposite | finger_friction,com_z | C39,C1185,C1186,C1187,C1188,C1189,C1190,C1191,C1192,C1193,C1194 | yes | Finger friction + COM Z offset: opposite-direction sweep |
| finger_friction_goal_height_opposite | finger_friction,goal_height | C39,C1205,C1206,C1207,C1208,C1209,C1210,C1211,C1212,C1213,C1214 | yes | Finger friction + Lift height: opposite-direction sweep |
| finger_friction_inertia_scale_opposite | finger_friction,inertia_scale | C1337,C1343,C1344,C1345,C1346,C1347,C1348,C1349,C1350,C1351,C1352 | yes | Finger friction + Inertia scale: opposite-direction sweep |
| finger_friction_linear_damping_opposite | finger_friction,linear_damping | C44,C1238,C1244,C1245,C1246,C1247,C1248,C1249,C1250,C1251,C1252 | yes | Finger friction + Object linear damping: opposite-direction sweep |
| finger_friction_restitution_opposite | finger_friction,restitution | C44,C1219,C1225,C1226,C1227,C1228,C1229,C1230,C1231,C1232,C1233 | yes | Finger friction + Object restitution: opposite-direction sweep |
| finger_friction_size_opposite | finger_friction,size | C39,C1114,C1115,C1116,C1117,C1118,C1119,C1120,C1121,C1122,C1123 | yes | Finger friction + Size: opposite-direction sweep |
| finger_friction_spawn_x_opposite | finger_friction,spawn_x | C39,C1282,C1283,C1284,C1285,C1286,C1287,C1288,C1289,C1290,C1291 | yes | Finger friction + Starting X offset: opposite-direction sweep |
| finger_friction_spawn_y_opposite | finger_friction,spawn_y | C39,C1302,C1303,C1304,C1305,C1306,C1307,C1308,C1309,C1310,C1311 | yes | Finger friction + Starting Y offset: opposite-direction sweep |
| finger_friction_spawn_yaw_opposite | finger_friction,spawn_yaw | C39,C1322,C1323,C1324,C1325,C1326,C1327,C1328,C1329,C1330,C1331 | yes | Finger friction + Starting yaw offset: opposite-direction sweep |
| finger_friction_table_friction_opposite | finger_friction,table_friction | C1088,C1094,C1095,C1096,C1097,C1098,C1099,C1100,C1101,C1102,C1103 | yes | Finger friction + Table friction: opposite-direction sweep |
| goal_height_angular_damping_opposite | goal_height,angular_damping | C105,C131,C2504,C2505,C2506,C2507,C2508,C2509,C2510,C2511,C2512 | yes | Lift height + Object angular damping: opposite-direction sweep |
| goal_height_inertia_scale_opposite | goal_height,inertia_scale | C172,C2583,C2584,C2585,C2586,C2587,C2588,C2589,C2590,C2591,C2592 | yes | Lift height + Inertia scale: opposite-direction sweep |
| goal_height_linear_damping_opposite | goal_height,linear_damping | C106,C121,C2486,C2487,C2488,C2489,C2490,C2491,C2492,C2493,C2494 | yes | Lift height + Object linear damping: opposite-direction sweep |
| goal_height_restitution_opposite | goal_height,restitution | C106,C111,C2468,C2469,C2470,C2471,C2472,C2473,C2474,C2475,C2476 | yes | Lift height + Object restitution: opposite-direction sweep |
| goal_height_spawn_x_opposite | goal_height,spawn_x | C01,C2523,C2524,C2525,C2526,C2527,C2528,C2529,C2530,C2531,C2532 | yes | Lift height + Starting X offset: opposite-direction sweep |
| goal_height_spawn_y_opposite | goal_height,spawn_y | C01,C2543,C2544,C2545,C2546,C2547,C2548,C2549,C2550,C2551,C2552 | yes | Lift height + Starting Y offset: opposite-direction sweep |
| goal_height_spawn_yaw_opposite | goal_height,spawn_yaw | C01,C2563,C2564,C2565,C2566,C2567,C2568,C2569,C2570,C2571,C2572 | yes | Lift height + Starting yaw offset: opposite-direction sweep |
| linear_damping_angular_damping_opposite | linear_damping,angular_damping | C125,C136,C2704,C2710,C2711,C2712,C2713,C2714,C2715,C2716,C2717 | yes | Object linear damping + Object angular damping: opposite-direction sweep |
| linear_damping_inertia_scale_opposite | linear_damping,inertia_scale | C177,C2776,C2782,C2783,C2784,C2785,C2786,C2787,C2788,C2789,C2790 | yes | Object linear damping + Inertia scale: opposite-direction sweep |
| linear_damping_spawn_x_opposite | linear_damping,spawn_x | C121,C146,C2727,C2728,C2729,C2730,C2731,C2732,C2733,C2734,C2735 | yes | Object linear damping + Starting X offset: opposite-direction sweep |
| linear_damping_spawn_y_opposite | linear_damping,spawn_y | C121,C156,C2745,C2746,C2747,C2748,C2749,C2750,C2751,C2752,C2753 | yes | Object linear damping + Starting Y offset: opposite-direction sweep |
| linear_damping_spawn_yaw_opposite | linear_damping,spawn_yaw | C121,C166,C2763,C2764,C2765,C2766,C2767,C2768,C2769,C2770,C2771 | yes | Object linear damping + Starting yaw offset: opposite-direction sweep |
| mass_angular_damping_opposite | mass,angular_damping | C11,C413,C419,C420,C421,C422,C423,C424,C425,C426,C427 | yes | Mass + Object angular damping: opposite-direction sweep |
| mass_com_x_opposite | mass,com_x | C07,C301,C302,C303,C304,C305,C306,C307,C308,C309,C310 | yes | Mass + COM X offset: opposite-direction sweep |
| mass_com_y_opposite | mass,com_y | C07,C321,C322,C323,C324,C325,C326,C327,C328,C329,C330 | yes | Mass + COM Y offset: opposite-direction sweep |
| mass_com_z_opposite | mass,com_z | C07,C341,C342,C343,C344,C345,C346,C347,C348,C349,C350 | yes | Mass + COM Z offset: opposite-direction sweep |
| mass_dynamic_friction_ratio_opposite | mass,dynamic_friction_ratio | C02,C204,C209,C210,C211,C212,C213,C214,C215,C216,C217 | yes | Mass + Sliding / static friction ratio: opposite-direction sweep |
| mass_finger_friction_opposite | mass,finger_friction | C223,C229,C230,C231,C232,C233,C234,C235,C236,C237,C238 | yes | Mass + Finger friction: opposite-direction sweep |
| mass_goal_height_opposite | mass,goal_height | C07,C361,C362,C363,C364,C365,C366,C367,C368,C369,C370 | yes | Mass + Lift height: opposite-direction sweep |
| mass_inertia_scale_opposite | mass,inertia_scale | C493,C499,C500,C501,C502,C503,C504,C505,C506,C507,C508 | yes | Mass + Inertia scale: opposite-direction sweep |
| mass_linear_damping_opposite | mass,linear_damping | C12,C394,C400,C401,C402,C403,C404,C405,C406,C407,C408 | yes | Mass + Object linear damping: opposite-direction sweep |
| mass_object_friction_opposite | mass,object_friction | C183,C189,C190,C191,C192,C193,C194,C195,C196,C197,C198 | yes | Mass + Object friction: opposite-direction sweep |
| mass_restitution_opposite | mass,restitution | C12,C375,C381,C382,C383,C384,C385,C386,C387,C388,C389 | yes | Mass + Object restitution: opposite-direction sweep |
| mass_size_opposite | mass,size | C07,C270,C271,C272,C273,C274,C275,C276,C277,C278,C279 | yes | Mass + Size: opposite-direction sweep |
| mass_spawn_x_opposite | mass,spawn_x | C07,C438,C439,C440,C441,C442,C443,C444,C445,C446,C447 | yes | Mass + Starting X offset: opposite-direction sweep |
| mass_spawn_y_opposite | mass,spawn_y | C07,C458,C459,C460,C461,C462,C463,C464,C465,C466,C467 | yes | Mass + Starting Y offset: opposite-direction sweep |
| mass_spawn_yaw_opposite | mass,spawn_yaw | C07,C478,C479,C480,C481,C482,C483,C484,C485,C486,C487 | yes | Mass + Starting yaw offset: opposite-direction sweep |
| mass_table_friction_opposite | mass,table_friction | C244,C250,C251,C252,C253,C254,C255,C256,C257,C258,C259 | yes | Mass + Table friction: opposite-direction sweep |
| object_friction_angular_damping_opposite | object_friction,angular_damping | C22,C723,C729,C730,C731,C732,C733,C734,C735,C736,C737 | yes | Object friction + Object angular damping: opposite-direction sweep |
| object_friction_com_x_opposite | object_friction,com_x | C18,C611,C612,C613,C614,C615,C616,C617,C618,C619,C620 | yes | Object friction + COM X offset: opposite-direction sweep |
| object_friction_com_y_opposite | object_friction,com_y | C18,C631,C632,C633,C634,C635,C636,C637,C638,C639,C640 | yes | Object friction + COM Y offset: opposite-direction sweep |
| object_friction_com_z_opposite | object_friction,com_z | C18,C651,C652,C653,C654,C655,C656,C657,C658,C659,C660 | yes | Object friction + COM Z offset: opposite-direction sweep |
| object_friction_dynamic_friction_ratio_opposite | object_friction,dynamic_friction_ratio | C13,C514,C519,C520,C521,C522,C523,C524,C525,C526,C527 | yes | Object friction + Sliding / static friction ratio: opposite-direction sweep |
| object_friction_finger_friction_opposite | object_friction,finger_friction | C533,C539,C540,C541,C542,C543,C544,C545,C546,C547,C548 | yes | Object friction + Finger friction: opposite-direction sweep |
| object_friction_goal_height_opposite | object_friction,goal_height | C18,C671,C672,C673,C674,C675,C676,C677,C678,C679,C680 | yes | Object friction + Lift height: opposite-direction sweep |
| object_friction_inertia_scale_opposite | object_friction,inertia_scale | C803,C809,C810,C811,C812,C813,C814,C815,C816,C817,C818 | yes | Object friction + Inertia scale: opposite-direction sweep |
| object_friction_linear_damping_opposite | object_friction,linear_damping | C23,C704,C710,C711,C712,C713,C714,C715,C716,C717,C718 | yes | Object friction + Object linear damping: opposite-direction sweep |
| object_friction_restitution_opposite | object_friction,restitution | C23,C685,C691,C692,C693,C694,C695,C696,C697,C698,C699 | yes | Object friction + Object restitution: opposite-direction sweep |
| object_friction_size_opposite | object_friction,size | C18,C580,C581,C582,C583,C584,C585,C586,C587,C588,C589 | yes | Object friction + Size: opposite-direction sweep |
| object_friction_spawn_x_opposite | object_friction,spawn_x | C18,C748,C749,C750,C751,C752,C753,C754,C755,C756,C757 | yes | Object friction + Starting X offset: opposite-direction sweep |
| object_friction_spawn_y_opposite | object_friction,spawn_y | C18,C768,C769,C770,C771,C772,C773,C774,C775,C776,C777 | yes | Object friction + Starting Y offset: opposite-direction sweep |
| object_friction_spawn_yaw_opposite | object_friction,spawn_yaw | C18,C788,C789,C790,C791,C792,C793,C794,C795,C796,C797 | yes | Object friction + Starting yaw offset: opposite-direction sweep |
| object_friction_table_friction_opposite | object_friction,table_friction | C554,C560,C561,C562,C563,C564,C565,C566,C567,C568,C569 | yes | Object friction + Table friction: opposite-direction sweep |
| restitution_angular_damping_opposite | restitution,angular_damping | C115,C136,C2614,C2620,C2621,C2622,C2623,C2624,C2625,C2626,C2627 | yes | Object restitution + Object angular damping: opposite-direction sweep |
| restitution_inertia_scale_opposite | restitution,inertia_scale | C177,C2686,C2692,C2693,C2694,C2695,C2696,C2697,C2698,C2699,C2700 | yes | Object restitution + Inertia scale: opposite-direction sweep |
| restitution_linear_damping_opposite | restitution,linear_damping | C116,C126,C2597,C2603,C2604,C2605,C2606,C2607,C2608,C2609,C2610 | yes | Object restitution + Object linear damping: opposite-direction sweep |
| restitution_spawn_x_opposite | restitution,spawn_x | C111,C146,C2637,C2638,C2639,C2640,C2641,C2642,C2643,C2644,C2645 | yes | Object restitution + Starting X offset: opposite-direction sweep |
| restitution_spawn_y_opposite | restitution,spawn_y | C111,C156,C2655,C2656,C2657,C2658,C2659,C2660,C2661,C2662,C2663 | yes | Object restitution + Starting Y offset: opposite-direction sweep |
| restitution_spawn_yaw_opposite | restitution,spawn_yaw | C111,C166,C2673,C2674,C2675,C2676,C2677,C2678,C2679,C2680,C2681 | yes | Object restitution + Starting yaw offset: opposite-direction sweep |
| size_angular_damping_opposite | size,angular_damping | C64,C131,C1737,C1738,C1739,C1740,C1741,C1742,C1743,C1744,C1745 | yes | Size + Object angular damping: opposite-direction sweep |
| size_com_x_opposite | size,com_x | C01,C1622,C1623,C1624,C1625,C1626,C1627,C1628,C1629,C1630,C1631 | yes | Size + COM X offset: opposite-direction sweep |
| size_com_y_opposite | size,com_y | C01,C1642,C1643,C1644,C1645,C1646,C1647,C1648,C1649,C1650,C1651 | yes | Size + COM Y offset: opposite-direction sweep |
| size_com_z_opposite | size,com_z | C01,C1662,C1663,C1664,C1665,C1666,C1667,C1668,C1669,C1670,C1671 | yes | Size + COM Z offset: opposite-direction sweep |
| size_goal_height_opposite | size,goal_height | C01,C1682,C1683,C1684,C1685,C1686,C1687,C1688,C1689,C1690,C1691 | yes | Size + Lift height: opposite-direction sweep |
| size_inertia_scale_opposite | size,inertia_scale | C172,C1816,C1817,C1818,C1819,C1820,C1821,C1822,C1823,C1824,C1825 | yes | Size + Inertia scale: opposite-direction sweep |
| size_linear_damping_opposite | size,linear_damping | C65,C121,C1719,C1720,C1721,C1722,C1723,C1724,C1725,C1726,C1727 | yes | Size + Object linear damping: opposite-direction sweep |
| size_restitution_opposite | size,restitution | C65,C111,C1701,C1702,C1703,C1704,C1705,C1706,C1707,C1708,C1709 | yes | Size + Object restitution: opposite-direction sweep |
| size_spawn_x_opposite | size,spawn_x | C01,C1756,C1757,C1758,C1759,C1760,C1761,C1762,C1763,C1764,C1765 | yes | Size + Starting X offset: opposite-direction sweep |
| size_spawn_y_opposite | size,spawn_y | C01,C1776,C1777,C1778,C1779,C1780,C1781,C1782,C1783,C1784,C1785 | yes | Size + Starting Y offset: opposite-direction sweep |
| size_spawn_yaw_opposite | size,spawn_yaw | C01,C1796,C1797,C1798,C1799,C1800,C1801,C1802,C1803,C1804,C1805 | yes | Size + Starting yaw offset: opposite-direction sweep |
| spawn_x_inertia_scale_opposite | spawn_x,inertia_scale | C172,C2914,C2915,C2916,C2917,C2918,C2919,C2920,C2921,C2922,C2923 | yes | Starting X offset + Inertia scale: opposite-direction sweep |
| spawn_x_spawn_y_opposite | spawn_x,spawn_y | C01,C2874,C2875,C2876,C2877,C2878,C2879,C2880,C2881,C2882,C2883 | yes | Starting X offset + Starting Y offset: opposite-direction sweep |
| spawn_x_spawn_yaw_opposite | spawn_x,spawn_yaw | C01,C2894,C2895,C2896,C2897,C2898,C2899,C2900,C2901,C2902,C2903 | yes | Starting X offset + Starting yaw offset: opposite-direction sweep |
| spawn_y_inertia_scale_opposite | spawn_y,inertia_scale | C172,C2954,C2955,C2956,C2957,C2958,C2959,C2960,C2961,C2962,C2963 | yes | Starting Y offset + Inertia scale: opposite-direction sweep |
| spawn_y_spawn_yaw_opposite | spawn_y,spawn_yaw | C01,C2934,C2935,C2936,C2937,C2938,C2939,C2940,C2941,C2942,C2943 | yes | Starting Y offset + Starting yaw offset: opposite-direction sweep |
| spawn_yaw_inertia_scale_opposite | spawn_yaw,inertia_scale | C172,C2974,C2975,C2976,C2977,C2978,C2979,C2980,C2981,C2982,C2983 | yes | Starting yaw offset + Inertia scale: opposite-direction sweep |
| table_friction_angular_damping_opposite | table_friction,angular_damping | C54,C1506,C1512,C1513,C1514,C1515,C1516,C1517,C1518,C1519,C1520 | yes | Table friction + Object angular damping: opposite-direction sweep |
| table_friction_com_x_opposite | table_friction,com_x | C50,C1394,C1395,C1396,C1397,C1398,C1399,C1400,C1401,C1402,C1403 | yes | Table friction + COM X offset: opposite-direction sweep |
| table_friction_com_y_opposite | table_friction,com_y | C50,C1414,C1415,C1416,C1417,C1418,C1419,C1420,C1421,C1422,C1423 | yes | Table friction + COM Y offset: opposite-direction sweep |
| table_friction_com_z_opposite | table_friction,com_z | C50,C1434,C1435,C1436,C1437,C1438,C1439,C1440,C1441,C1442,C1443 | yes | Table friction + COM Z offset: opposite-direction sweep |
| table_friction_goal_height_opposite | table_friction,goal_height | C50,C1454,C1455,C1456,C1457,C1458,C1459,C1460,C1461,C1462,C1463 | yes | Table friction + Lift height: opposite-direction sweep |
| table_friction_inertia_scale_opposite | table_friction,inertia_scale | C1586,C1592,C1593,C1594,C1595,C1596,C1597,C1598,C1599,C1600,C1601 | yes | Table friction + Inertia scale: opposite-direction sweep |
| table_friction_linear_damping_opposite | table_friction,linear_damping | C55,C1487,C1493,C1494,C1495,C1496,C1497,C1498,C1499,C1500,C1501 | yes | Table friction + Object linear damping: opposite-direction sweep |
| table_friction_restitution_opposite | table_friction,restitution | C55,C1468,C1474,C1475,C1476,C1477,C1478,C1479,C1480,C1481,C1482 | yes | Table friction + Object restitution: opposite-direction sweep |
| table_friction_size_opposite | table_friction,size | C50,C1363,C1364,C1365,C1366,C1367,C1368,C1369,C1370,C1371,C1372 | yes | Table friction + Size: opposite-direction sweep |
| table_friction_spawn_x_opposite | table_friction,spawn_x | C50,C1531,C1532,C1533,C1534,C1535,C1536,C1537,C1538,C1539,C1540 | yes | Table friction + Starting X offset: opposite-direction sweep |
| table_friction_spawn_y_opposite | table_friction,spawn_y | C50,C1551,C1552,C1553,C1554,C1555,C1556,C1557,C1558,C1559,C1560 | yes | Table friction + Starting Y offset: opposite-direction sweep |
| table_friction_spawn_yaw_opposite | table_friction,spawn_yaw | C50,C1571,C1572,C1573,C1574,C1575,C1576,C1577,C1578,C1579,C1580 | yes | Table friction + Starting yaw offset: opposite-direction sweep |
| dynamic_friction_ratio_shape_categorical_cross | dynamic_friction_ratio,shape | C01,C24,C25,C26,C27,C28,C29,C30,C31,C32,C33,C66,C875,C876,C877,C878,C879,C880,C881,C882,C883,C884 | yes | Sliding / static friction ratio + Shape: shape crossing |
| finger_friction_shape_categorical_cross | finger_friction,shape | C01,C34,C35,C36,C37,C38,C39,C40,C41,C42,C43,C44,C66,C1124,C1125,C1126,C1127,C1128,C1129,C1130,C1131,C1132,C1133,C1134 | yes | Finger friction + Shape: shape crossing |
| mass_shape_categorical_cross | mass,shape | C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C66,C280,C281,C282,C283,C284,C285,C286,C287,C288,C289,C290 | yes | Mass + Shape: shape crossing |
| object_friction_shape_categorical_cross | object_friction,shape | C01,C13,C14,C15,C16,C17,C18,C19,C20,C21,C22,C23,C66,C590,C591,C592,C593,C594,C595,C596,C597,C598,C599,C600 | yes | Object friction + Shape: shape crossing |
| shape_angular_damping_categorical_cross | shape,angular_damping | C01,C66,C127,C128,C129,C130,C131,C132,C133,C134,C135,C136,C1886,C1887,C1888,C1889,C1890,C1891,C1892,C1893,C1894,C1895 | yes | Shape + Object angular damping: shape crossing |
| shape_com_x_categorical_cross | shape,com_x | C01,C66,C67,C68,C69,C70,C71,C72,C73,C74,C75,C76,C1826,C1827,C1828,C1829,C1830,C1831,C1832,C1833,C1834,C1835 | yes | Shape + COM X offset: shape crossing |
| shape_com_y_categorical_cross | shape,com_y | C01,C66,C77,C78,C79,C80,C81,C82,C83,C84,C85,C86,C1836,C1837,C1838,C1839,C1840,C1841,C1842,C1843,C1844,C1845 | yes | Shape + COM Y offset: shape crossing |
| shape_com_z_categorical_cross | shape,com_z | C01,C66,C87,C88,C89,C90,C91,C92,C93,C94,C95,C96,C1846,C1847,C1848,C1849,C1850,C1851,C1852,C1853,C1854,C1855 | yes | Shape + COM Z offset: shape crossing |
| shape_goal_height_categorical_cross | shape,goal_height | C01,C66,C97,C98,C99,C100,C101,C102,C103,C104,C105,C106,C1856,C1857,C1858,C1859,C1860,C1861,C1862,C1863,C1864,C1865 | yes | Shape + Lift height: shape crossing |
| shape_inertia_scale_categorical_cross | shape,inertia_scale | C01,C66,C167,C168,C169,C170,C171,C172,C173,C174,C175,C176,C177,C1926,C1927,C1928,C1929,C1930,C1931,C1932,C1933,C1934,C1935,C1936 | yes | Shape + Inertia scale: shape crossing |
| shape_linear_damping_categorical_cross | shape,linear_damping | C01,C66,C117,C118,C119,C120,C121,C122,C123,C124,C125,C126,C1876,C1877,C1878,C1879,C1880,C1881,C1882,C1883,C1884,C1885 | yes | Shape + Object linear damping: shape crossing |
| shape_restitution_categorical_cross | shape,restitution | C01,C66,C107,C108,C109,C110,C111,C112,C113,C114,C115,C116,C1866,C1867,C1868,C1869,C1870,C1871,C1872,C1873,C1874,C1875 | yes | Shape + Object restitution: shape crossing |
| shape_spawn_x_categorical_cross | shape,spawn_x | C01,C66,C137,C138,C139,C140,C141,C142,C143,C144,C145,C146,C1896,C1897,C1898,C1899,C1900,C1901,C1902,C1903,C1904,C1905 | yes | Shape + Starting X offset: shape crossing |
| shape_spawn_y_categorical_cross | shape,spawn_y | C01,C66,C147,C148,C149,C150,C151,C152,C153,C154,C155,C156,C1906,C1907,C1908,C1909,C1910,C1911,C1912,C1913,C1914,C1915 | yes | Shape + Starting Y offset: shape crossing |
| shape_spawn_yaw_categorical_cross | shape,spawn_yaw | C01,C66,C157,C158,C159,C160,C161,C162,C163,C164,C165,C166,C1916,C1917,C1918,C1919,C1920,C1921,C1922,C1923,C1924,C1925 | yes | Shape + Starting yaw offset: shape crossing |
| size_shape_categorical_cross | size,shape | C01,C56,C57,C58,C59,C60,C61,C62,C63,C64,C65,C66,C1602,C1603,C1604,C1605,C1606,C1607,C1608,C1609,C1610,C1611 | yes | Size + Shape: shape crossing |
| table_friction_shape_categorical_cross | table_friction,shape | C01,C45,C46,C47,C48,C49,C50,C51,C52,C53,C54,C55,C66,C1373,C1374,C1375,C1376,C1377,C1378,C1379,C1380,C1381,C1382,C1383 | yes | Table friction + Shape: shape crossing |

## Condition lookup

| ID | Saved condition ID | Deliberately changed factors | Values |
| --- | --- | --- | --- |
| C01 | e66c6f24e261b16e | none | nominal |
| C02 | d4173a83245d252d | mass | mass=0.04 |
| C03 | f7997ac669be0e02 | mass | mass=0.086 |
| C04 | 9e5657db99b14a6c | mass | mass=0.132 |
| C05 | 646e57b71bccfe86 | mass | mass=0.178 |
| C06 | 5d76685733360240 | mass | mass=0.224 |
| C07 | a3e83ae995a4a08b | mass | mass=0.27 |
| C08 | 97032c28af3a6254 | mass | mass=0.316 |
| C09 | debcc732ec75c99c | mass | mass=0.362 |
| C10 | 64cf8a5c004829ac | mass | mass=0.408 |
| C11 | 961c9e38a4b0f995 | mass | mass=0.454 |
| C12 | d282e9db20b191be | mass | mass=0.5 |
| C13 | 7829671da4f92fc3 | object_friction | object_friction=0.1 |
| C14 | 0eb427b1b288b735 | object_friction | object_friction=0.19 |
| C15 | fecdfee87ec68df2 | object_friction | object_friction=0.28 |
| C16 | 97242148e455d683 | object_friction | object_friction=0.37 |
| C17 | 4dcc5ca961ba0539 | object_friction | object_friction=0.46 |
| C18 | 948aad22280f049e | object_friction | object_friction=0.55 |
| C19 | 2cd7ac83fe4fc97e | object_friction | object_friction=0.64 |
| C20 | 6c05d20d4a019ea6 | object_friction | object_friction=0.73 |
| C21 | a4d475e97e04e77e | object_friction | object_friction=0.82 |
| C22 | c94229c237755603 | object_friction | object_friction=0.91 |
| C23 | d1d8c0bf25745743 | object_friction | object_friction=1.0 |
| C24 | d6f0fe8c37b0b223 | dynamic_friction_ratio | dynamic_friction_ratio=0.25 |
| C25 | 395dd20e1088d0dc | dynamic_friction_ratio | dynamic_friction_ratio=0.325 |
| C26 | b15be6fcf4f6a4cb | dynamic_friction_ratio | dynamic_friction_ratio=0.4 |
| C27 | 80ca031d632b8b9d | dynamic_friction_ratio | dynamic_friction_ratio=0.475 |
| C28 | 99cf1c79787a8c76 | dynamic_friction_ratio | dynamic_friction_ratio=0.55 |
| C29 | af3d4d89940409a1 | dynamic_friction_ratio | dynamic_friction_ratio=0.625 |
| C30 | 0ab3969bca709c93 | dynamic_friction_ratio | dynamic_friction_ratio=0.7 |
| C31 | 0145462c8e427d59 | dynamic_friction_ratio | dynamic_friction_ratio=0.775 |
| C32 | 08fb01cc9be5caba | dynamic_friction_ratio | dynamic_friction_ratio=0.85 |
| C33 | 9cc59edeebdaf8d7 | dynamic_friction_ratio | dynamic_friction_ratio=0.925 |
| C34 | 9f47f48f86848591 | finger_friction | finger_friction=0.1 |
| C35 | b79ec603e0816698 | finger_friction | finger_friction=0.14 |
| C36 | 5c2b8af035d93785 | finger_friction | finger_friction=0.18 |
| C37 | 9547776d88d22b2a | finger_friction | finger_friction=0.22 |
| C38 | 472a66566b75c2e2 | finger_friction | finger_friction=0.26 |
| C39 | e15158b82d3cf53a | finger_friction | finger_friction=0.3 |
| C40 | 053499b8aedef761 | finger_friction | finger_friction=0.34 |
| C41 | 0a39d2ee063efaed | finger_friction | finger_friction=0.38 |
| C42 | c1710c07c2fe0039 | finger_friction | finger_friction=0.42 |
| C43 | 09faaa3c4eb07b3c | finger_friction | finger_friction=0.46 |
| C44 | 568fb5b17c978357 | finger_friction | finger_friction=0.5 |
| C45 | 7aabcd73760bd2ad | table_friction | table_friction=0.1 |
| C46 | d524abeb55ae48cb | table_friction | table_friction=0.17 |
| C47 | 13b6d0dc43428799 | table_friction | table_friction=0.24 |
| C48 | fe6717a68f99e500 | table_friction | table_friction=0.31 |
| C49 | 70cbd1a6a2e38dff | table_friction | table_friction=0.38 |
| C50 | e8fe861cded03e86 | table_friction | table_friction=0.45 |
| C51 | f28a9e6e52c80e41 | table_friction | table_friction=0.52 |
| C52 | b65eed3da6ce6b7c | table_friction | table_friction=0.59 |
| C53 | 652ee1e7356656ec | table_friction | table_friction=0.66 |
| C54 | a7378d7d7d0f21d0 | table_friction | table_friction=0.73 |
| C55 | 4878fe1f282809f1 | table_friction | table_friction=0.8 |
| C56 | f834e4592ae2ac0c | size | size=0.03 |
| C57 | b145ae84798e0c4c | size | size=0.032 |
| C58 | 8603d9263a693ac4 | size | size=0.034 |
| C59 | f3237c4a773376ec | size | size=0.036 |
| C60 | 7591c91567ef132c | size | size=0.038 |
| C61 | 2577852360ef6ebc | size | size=0.042 |
| C62 | 20f38cbef222cb83 | size | size=0.044 |
| C63 | 7e0a45549a081bb4 | size | size=0.046 |
| C64 | f0f4621bd08f5f9f | size | size=0.048 |
| C65 | b78a140b532d74df | size | size=0.05 |
| C66 | 593433c30b9de5e8 | shape | shape=sphere |
| C67 | 6fd7ac4244a2783a | com_x | com_x=-0.005 |
| C68 | 5c1dc8fc7b87cbb6 | com_x | com_x=-0.004 |
| C69 | 907a74918929829e | com_x | com_x=-0.003 |
| C70 | dcdd979ee278d263 | com_x | com_x=-0.002 |
| C71 | 8ddf0060b35017d9 | com_x | com_x=-0.001 |
| C72 | 93a67904acf250b4 | com_x | com_x=0.001 |
| C73 | 4f6a6d819d199656 | com_x | com_x=0.002 |
| C74 | cc490ee82b8c9268 | com_x | com_x=0.003 |
| C75 | 8c19bf54c278ee9b | com_x | com_x=0.004 |
| C76 | 16700a0a1e9f1675 | com_x | com_x=0.005 |
| C77 | 332645597d1ac186 | com_y | com_y=-0.005 |
| C78 | c142de2805c587bd | com_y | com_y=-0.004 |
| C79 | 2be2bcac57ca4c0d | com_y | com_y=-0.003 |
| C80 | 3dd39813147793fc | com_y | com_y=-0.002 |
| C81 | 73f389464d5bfc72 | com_y | com_y=-0.001 |
| C82 | 0bd2c78bdf4995bb | com_y | com_y=0.001 |
| C83 | c32a422fca8bdca2 | com_y | com_y=0.002 |
| C84 | 10a75326c8e2c44b | com_y | com_y=0.003 |
| C85 | 05dd62f443561c13 | com_y | com_y=0.004 |
| C86 | e0a954719216234b | com_y | com_y=0.005 |
| C87 | 6db347a32c1a81c0 | com_z | com_z=-0.005 |
| C88 | 001a5fb1fd407e71 | com_z | com_z=-0.004 |
| C89 | 24ed56910a52c5c9 | com_z | com_z=-0.003 |
| C90 | ecdde9c8dfb2068b | com_z | com_z=-0.002 |
| C91 | 2b2be883f492ad9b | com_z | com_z=-0.001 |
| C92 | 6216fed8f13e7fc5 | com_z | com_z=0.001 |
| C93 | f0374de07f684561 | com_z | com_z=0.002 |
| C94 | 21ee5cdf829c3c9f | com_z | com_z=0.003 |
| C95 | 12b23b5825cc45cc | com_z | com_z=0.004 |
| C96 | 6aac76ec8ae07b68 | com_z | com_z=0.005 |
| C97 | bff73abd79590366 | goal_height | goal_height=0.1 |
| C98 | 280e7a1b417404ac | goal_height | goal_height=0.12 |
| C99 | 8c9f5afe1b534a9e | goal_height | goal_height=0.14 |
| C100 | 2d99deaa7762399b | goal_height | goal_height=0.16 |
| C101 | 88c2faa7f4260167 | goal_height | goal_height=0.18 |
| C102 | fb09e7361d5e080b | goal_height | goal_height=0.22 |
| C103 | 507d724019e335df | goal_height | goal_height=0.24 |
| C104 | d86f47dbd737b2dc | goal_height | goal_height=0.26 |
| C105 | a83f48f420b69e21 | goal_height | goal_height=0.28 |
| C106 | 1e2790637cdf00b9 | goal_height | goal_height=0.3 |
| C107 | 8924fa4a50e618d0 | restitution | restitution=0.05 |
| C108 | 957e197e74d137e3 | restitution | restitution=0.1 |
| C109 | 95fabe4a4b840fec | restitution | restitution=0.15 |
| C110 | ef2297034af69676 | restitution | restitution=0.2 |
| C111 | efae79772165c397 | restitution | restitution=0.25 |
| C112 | 25ba8a88c5e97ebd | restitution | restitution=0.3 |
| C113 | 7871f119fb500f80 | restitution | restitution=0.35 |
| C114 | 11e70c36e5aef645 | restitution | restitution=0.4 |
| C115 | 0ca509cbccdcb3fd | restitution | restitution=0.45 |
| C116 | 4beb0aacb8b00b3c | restitution | restitution=0.5 |
| C117 | 478a9ce7ba08f4c2 | linear_damping | linear_damping=0.1 |
| C118 | ea0f4b86d7d437b3 | linear_damping | linear_damping=0.2 |
| C119 | d9f7315cfc62e9c8 | linear_damping | linear_damping=0.3 |
| C120 | 8e8349b21eabf353 | linear_damping | linear_damping=0.4 |
| C121 | b600bb1521e99254 | linear_damping | linear_damping=0.5 |
| C122 | ba6f35353219936e | linear_damping | linear_damping=0.6 |
| C123 | 3a468d886f54ed56 | linear_damping | linear_damping=0.7 |
| C124 | 56743aabf50b5d53 | linear_damping | linear_damping=0.8 |
| C125 | 154d94a0f3e0b3b4 | linear_damping | linear_damping=0.9 |
| C126 | 550a24eb28da79b8 | linear_damping | linear_damping=1.0 |
| C127 | 1f70351a4dabb68d | angular_damping | angular_damping=0.0 |
| C128 | 25a8eeeccb7a3886 | angular_damping | angular_damping=0.1 |
| C129 | 8d8ee2af199cca2f | angular_damping | angular_damping=0.15 |
| C130 | fc1046ada883a000 | angular_damping | angular_damping=0.2 |
| C131 | 59afdfc40abc4567 | angular_damping | angular_damping=0.25 |
| C132 | e37a1749b505e049 | angular_damping | angular_damping=0.3 |
| C133 | ccc26aeb79b1ec6e | angular_damping | angular_damping=0.35 |
| C134 | 86b54b2cf4034849 | angular_damping | angular_damping=0.4 |
| C135 | 9af8fcdfe0d24135 | angular_damping | angular_damping=0.45 |
| C136 | cced49d8d513f872 | angular_damping | angular_damping=0.5 |
| C137 | 05537c6efd23a642 | spawn_x | spawn_x=-0.04 |
| C138 | 5c280b752099e336 | spawn_x | spawn_x=-0.032 |
| C139 | 80ec28e3922c71f1 | spawn_x | spawn_x=-0.024 |
| C140 | e0cf60e2f6b9eb75 | spawn_x | spawn_x=-0.016 |
| C141 | b51864d8b53fb883 | spawn_x | spawn_x=-0.008 |
| C142 | e9b5d128a3d0502b | spawn_x | spawn_x=0.008 |
| C143 | 27e2f30c1e02ff96 | spawn_x | spawn_x=0.016 |
| C144 | 528020af130ea1db | spawn_x | spawn_x=0.024 |
| C145 | 776ba15395ab5235 | spawn_x | spawn_x=0.032 |
| C146 | b25f96bb458a48bf | spawn_x | spawn_x=0.04 |
| C147 | 9ae93a6d2eb9d819 | spawn_y | spawn_y=-0.04 |
| C148 | 4f1c11f3911c9d9a | spawn_y | spawn_y=-0.032 |
| C149 | d83b566fda8a0448 | spawn_y | spawn_y=-0.024 |
| C150 | 2b1cff95e885c328 | spawn_y | spawn_y=-0.016 |
| C151 | 30147e9e8ae72e1a | spawn_y | spawn_y=-0.008 |
| C152 | b6256e6844878653 | spawn_y | spawn_y=0.008 |
| C153 | acab834c2a638254 | spawn_y | spawn_y=0.016 |
| C154 | 5faf77083444a3fb | spawn_y | spawn_y=0.024 |
| C155 | 00a93db01d7453be | spawn_y | spawn_y=0.032 |
| C156 | 8b2bcfc169bf74e3 | spawn_y | spawn_y=0.04 |
| C157 | 6f69d02b8b60ad16 | spawn_yaw | spawn_yaw=-0.523598775598 |
| C158 | 85a1363200de1de9 | spawn_yaw | spawn_yaw=-0.418879020478 |
| C159 | 45f477f144fe487c | spawn_yaw | spawn_yaw=-0.314159265359 |
| C160 | c0ceb952a4199cbd | spawn_yaw | spawn_yaw=-0.209439510239 |
| C161 | d9333f457452f5af | spawn_yaw | spawn_yaw=-0.10471975512 |
| C162 | 91f1d1d58fceb7a0 | spawn_yaw | spawn_yaw=0.10471975512 |
| C163 | 1e7fee2635e9cc73 | spawn_yaw | spawn_yaw=0.209439510239 |
| C164 | f4b4cafc9eb474ce | spawn_yaw | spawn_yaw=0.314159265359 |
| C165 | 546c9d796bed8d5c | spawn_yaw | spawn_yaw=0.418879020478 |
| C166 | d43aee35c35631ce | spawn_yaw | spawn_yaw=0.523598775598 |
| C167 | 0a7f90ae22e94100 | inertia_scale | inertia_scale=0.5 |
| C168 | f5fdda358a4b1686 | inertia_scale | inertia_scale=0.65 |
| C169 | 20558d8762a6b24e | inertia_scale | inertia_scale=0.8 |
| C170 | d3bb385222b09fb2 | inertia_scale | inertia_scale=0.95 |
| C171 | 20b3242f1c63b015 | inertia_scale | inertia_scale=1.1 |
| C172 | 0a827b8ddd9817e7 | inertia_scale | inertia_scale=1.25 |
| C173 | c747c85ce16b6886 | inertia_scale | inertia_scale=1.4 |
| C174 | 3a70fc4cd8b37340 | inertia_scale | inertia_scale=1.55 |
| C175 | 9f8c82a24bc30c52 | inertia_scale | inertia_scale=1.7 |
| C176 | fb7ac55e20eae3e5 | inertia_scale | inertia_scale=1.85 |
| C177 | 6e2c9018b05016ff | inertia_scale | inertia_scale=2.0 |
| C178 | 516488e006e018f8 | mass,object_friction | mass=0.04, object_friction=0.1 |
| C179 | 6d92cc4989f44316 | mass,object_friction | mass=0.086, object_friction=0.19 |
| C180 | bcd4d5d3f5e10a79 | mass,object_friction | mass=0.132, object_friction=0.28 |
| C181 | 3818e0ca63355b7a | mass,object_friction | mass=0.178, object_friction=0.37 |
| C182 | 6d4122f8d10d1565 | mass,object_friction | mass=0.224, object_friction=0.46 |
| C183 | 3fd5f45b18b9b0a2 | mass,object_friction | mass=0.27, object_friction=0.55 |
| C184 | 60a390dd0b1363ec | mass,object_friction | mass=0.316, object_friction=0.64 |
| C185 | 968bebae41e7f23d | mass,object_friction | mass=0.362, object_friction=0.73 |
| C186 | 1072b56a0d6e0312 | mass,object_friction | mass=0.408, object_friction=0.82 |
| C187 | 177e30b8b02bf1d5 | mass,object_friction | mass=0.454, object_friction=0.91 |
| C188 | 49a84e0f6da4153d | mass,object_friction | mass=0.5, object_friction=1.0 |
| C189 | 44f3d28e7358fb80 | mass,object_friction | mass=0.04, object_friction=1.0 |
| C190 | a781dc1a08e505d9 | mass,object_friction | mass=0.086, object_friction=0.91 |
| C191 | 64ba2ce5c563f74d | mass,object_friction | mass=0.132, object_friction=0.82 |
| C192 | 573bd183c3aac4ae | mass,object_friction | mass=0.178, object_friction=0.73 |
| C193 | 531b82d308ebe470 | mass,object_friction | mass=0.224, object_friction=0.64 |
| C194 | 7535ca6c1562781c | mass,object_friction | mass=0.316, object_friction=0.46 |
| C195 | 975c62163c642c37 | mass,object_friction | mass=0.362, object_friction=0.37 |
| C196 | 1b802778fa17f137 | mass,object_friction | mass=0.408, object_friction=0.28 |
| C197 | 5b4db044f6b2a011 | mass,object_friction | mass=0.454, object_friction=0.19 |
| C198 | 1ea0060ce71087f8 | mass,object_friction | mass=0.5, object_friction=0.1 |
| C199 | e4580606e7929c91 | mass,dynamic_friction_ratio | mass=0.04, dynamic_friction_ratio=0.25 |
| C200 | f5eb3347fdf81d18 | mass,dynamic_friction_ratio | mass=0.086, dynamic_friction_ratio=0.325 |
| C201 | ca44f7f2b2cc2a8a | mass,dynamic_friction_ratio | mass=0.132, dynamic_friction_ratio=0.4 |
| C202 | 5c9578bbc35e04d1 | mass,dynamic_friction_ratio | mass=0.178, dynamic_friction_ratio=0.475 |
| C203 | 443c00bb35720f55 | mass,dynamic_friction_ratio | mass=0.224, dynamic_friction_ratio=0.55 |
| C204 | 09b30a804a41df68 | mass,dynamic_friction_ratio | mass=0.27, dynamic_friction_ratio=0.625 |
| C205 | 7b4e8bacebf3ab8b | mass,dynamic_friction_ratio | mass=0.316, dynamic_friction_ratio=0.7 |
| C206 | bdb441694dc0e655 | mass,dynamic_friction_ratio | mass=0.362, dynamic_friction_ratio=0.775 |
| C207 | 53a28c9e37025451 | mass,dynamic_friction_ratio | mass=0.408, dynamic_friction_ratio=0.85 |
| C208 | 271df78df687856d | mass,dynamic_friction_ratio | mass=0.454, dynamic_friction_ratio=0.925 |
| C209 | 6b353b424cfb1479 | mass,dynamic_friction_ratio | mass=0.086, dynamic_friction_ratio=0.925 |
| C210 | 824c88c7820b2199 | mass,dynamic_friction_ratio | mass=0.132, dynamic_friction_ratio=0.85 |
| C211 | a6e77398307c70a0 | mass,dynamic_friction_ratio | mass=0.178, dynamic_friction_ratio=0.775 |
| C212 | f2c994cbd3550b61 | mass,dynamic_friction_ratio | mass=0.224, dynamic_friction_ratio=0.7 |
| C213 | 56a7bd4e5f55843d | mass,dynamic_friction_ratio | mass=0.316, dynamic_friction_ratio=0.55 |
| C214 | d45b55fb6f6bdb2b | mass,dynamic_friction_ratio | mass=0.362, dynamic_friction_ratio=0.475 |
| C215 | 9133237da6d10738 | mass,dynamic_friction_ratio | mass=0.408, dynamic_friction_ratio=0.4 |
| C216 | 60063f52b62a4e11 | mass,dynamic_friction_ratio | mass=0.454, dynamic_friction_ratio=0.325 |
| C217 | 8bba4be4c6d47d64 | mass,dynamic_friction_ratio | mass=0.5, dynamic_friction_ratio=0.25 |
| C218 | 13b2bc82f14d3caf | mass,finger_friction | mass=0.04, finger_friction=0.1 |
| C219 | 25cff12ddab8559f | mass,finger_friction | mass=0.086, finger_friction=0.14 |
| C220 | f2db3cb4ac101d9c | mass,finger_friction | mass=0.132, finger_friction=0.18 |
| C221 | 74aa25939499ea73 | mass,finger_friction | mass=0.178, finger_friction=0.22 |
| C222 | 14aa570df8dbcc32 | mass,finger_friction | mass=0.224, finger_friction=0.26 |
| C223 | e89641ca6c6c4179 | mass,finger_friction | mass=0.27, finger_friction=0.3 |
| C224 | 4a41c124d26dd09d | mass,finger_friction | mass=0.316, finger_friction=0.34 |
| C225 | 89e3fa403cc0e3b6 | mass,finger_friction | mass=0.362, finger_friction=0.38 |
| C226 | 9c06bcb486e7bd73 | mass,finger_friction | mass=0.408, finger_friction=0.42 |
| C227 | e8f2e9595dcb4290 | mass,finger_friction | mass=0.454, finger_friction=0.46 |
| C228 | 0af3ee63e886263d | mass,finger_friction | mass=0.5, finger_friction=0.5 |
| C229 | 7d64229f1e53bd0e | mass,finger_friction | mass=0.04, finger_friction=0.5 |
| C230 | 362cee081f76619b | mass,finger_friction | mass=0.086, finger_friction=0.46 |
| C231 | c8c63c83e20897ce | mass,finger_friction | mass=0.132, finger_friction=0.42 |
| C232 | c1f8b5ee7a3e2ef4 | mass,finger_friction | mass=0.178, finger_friction=0.38 |
| C233 | a2f9bf7575f09711 | mass,finger_friction | mass=0.224, finger_friction=0.34 |
| C234 | 8678a6157d01ed19 | mass,finger_friction | mass=0.316, finger_friction=0.26 |
| C235 | f2f65053a125dc0a | mass,finger_friction | mass=0.362, finger_friction=0.22 |
| C236 | 9265ff3701c27455 | mass,finger_friction | mass=0.408, finger_friction=0.18 |
| C237 | 8e051369c729f88b | mass,finger_friction | mass=0.454, finger_friction=0.14 |
| C238 | 2e7dc8493dc6e040 | mass,finger_friction | mass=0.5, finger_friction=0.1 |
| C239 | 93273b66f14072ed | mass,table_friction | mass=0.04, table_friction=0.1 |
| C240 | e5436f14adaff869 | mass,table_friction | mass=0.086, table_friction=0.17 |
| C241 | 7626a27e28952aec | mass,table_friction | mass=0.132, table_friction=0.24 |
| C242 | 5afeebf33a302b1b | mass,table_friction | mass=0.178, table_friction=0.31 |
| C243 | 6339853ef9e898e4 | mass,table_friction | mass=0.224, table_friction=0.38 |
| C244 | 6c51e128d1eb317a | mass,table_friction | mass=0.27, table_friction=0.45 |
| C245 | 8347bf42505b4117 | mass,table_friction | mass=0.316, table_friction=0.52 |
| C246 | 6320877d3402d4b8 | mass,table_friction | mass=0.362, table_friction=0.59 |
| C247 | 1eded380c0d3e58a | mass,table_friction | mass=0.408, table_friction=0.66 |
| C248 | fdffd09b7d0fd120 | mass,table_friction | mass=0.454, table_friction=0.73 |
| C249 | a1841236c34e7550 | mass,table_friction | mass=0.5, table_friction=0.8 |
| C250 | 90c30a6d812044ce | mass,table_friction | mass=0.04, table_friction=0.8 |
| C251 | 2186fbf0d0423255 | mass,table_friction | mass=0.086, table_friction=0.73 |
| C252 | 868feca377a806b7 | mass,table_friction | mass=0.132, table_friction=0.66 |
| C253 | 3cebb990a9cc8674 | mass,table_friction | mass=0.178, table_friction=0.59 |
| C254 | 9f4cf4209453550a | mass,table_friction | mass=0.224, table_friction=0.52 |
| C255 | 7abf33232be96535 | mass,table_friction | mass=0.316, table_friction=0.38 |
| C256 | 91136f973ee56b2e | mass,table_friction | mass=0.362, table_friction=0.31 |
| C257 | e418e58f67191e3f | mass,table_friction | mass=0.408, table_friction=0.24 |
| C258 | 0907a4999305a20c | mass,table_friction | mass=0.454, table_friction=0.17 |
| C259 | a9ca62c3e37117d9 | mass,table_friction | mass=0.5, table_friction=0.1 |
| C260 | 15e769e2a6a455f8 | mass,size | mass=0.04, size=0.03 |
| C261 | a8836ba4c9cdf738 | mass,size | mass=0.086, size=0.032 |
| C262 | 9113e4c4dc28de4a | mass,size | mass=0.132, size=0.034 |
| C263 | e95a91d6e25b8419 | mass,size | mass=0.178, size=0.036 |
| C264 | b28323a509eda022 | mass,size | mass=0.224, size=0.038 |
| C265 | d9cefcb73add37ff | mass,size | mass=0.316, size=0.042 |
| C266 | 21c3e6aad7255bee | mass,size | mass=0.362, size=0.044 |
| C267 | b09c099d1b56f02d | mass,size | mass=0.408, size=0.046 |
| C268 | db069ee79e583e91 | mass,size | mass=0.454, size=0.048 |
| C269 | d21e5f44c2d3cfa4 | mass,size | mass=0.5, size=0.05 |
| C270 | 13eace301b937bbf | mass,size | mass=0.04, size=0.05 |
| C271 | c2bdbe0e4ec45a09 | mass,size | mass=0.086, size=0.048 |
| C272 | dda33d6e41a38947 | mass,size | mass=0.132, size=0.046 |
| C273 | 8d97bee8f5ee84d5 | mass,size | mass=0.178, size=0.044 |
| C274 | 396481778092286e | mass,size | mass=0.224, size=0.042 |
| C275 | 601b8aa9c09e057f | mass,size | mass=0.316, size=0.038 |
| C276 | 229ebefa1ec84f11 | mass,size | mass=0.362, size=0.036 |
| C277 | d8b6fd0022c4e1d2 | mass,size | mass=0.408, size=0.034 |
| C278 | 2322554c3dd74f07 | mass,size | mass=0.454, size=0.032 |
| C279 | bf5052a1de6c319b | mass,size | mass=0.5, size=0.03 |
| C280 | 8b8ce82c5a347dac | mass,shape | mass=0.04, shape=sphere |
| C281 | 440171420020ab32 | mass,shape | mass=0.086, shape=sphere |
| C282 | 9981e7ab05e0a2cd | mass,shape | mass=0.132, shape=sphere |
| C283 | 65d4537f250ed175 | mass,shape | mass=0.178, shape=sphere |
| C284 | c67a3ea9c4a6dc4d | mass,shape | mass=0.224, shape=sphere |
| C285 | becaf7406ffbf088 | mass,shape | mass=0.27, shape=sphere |
| C286 | f91a5ecc047934d5 | mass,shape | mass=0.316, shape=sphere |
| C287 | 0ca136670443ea27 | mass,shape | mass=0.362, shape=sphere |
| C288 | 4d625029255e3c82 | mass,shape | mass=0.408, shape=sphere |
| C289 | 859e5efb92ded6bc | mass,shape | mass=0.454, shape=sphere |
| C290 | 80a984ae9de20ba5 | mass,shape | mass=0.5, shape=sphere |
| C291 | 226c3fe05faf6d0e | mass,com_x | mass=0.04, com_x=-0.005 |
| C292 | e228f8c9b1b2df7b | mass,com_x | mass=0.086, com_x=-0.004 |
| C293 | c902b81ba3cd82c6 | mass,com_x | mass=0.132, com_x=-0.003 |
| C294 | 7f70d616a3c5f418 | mass,com_x | mass=0.178, com_x=-0.002 |
| C295 | ae9d0361723cbe41 | mass,com_x | mass=0.224, com_x=-0.001 |
| C296 | 1cb0c082a09cfdd8 | mass,com_x | mass=0.316, com_x=0.001 |
| C297 | 56580e80c9f41afb | mass,com_x | mass=0.362, com_x=0.002 |
| C298 | 231a8687ab5792a6 | mass,com_x | mass=0.408, com_x=0.003 |
| C299 | d226072469d7f3aa | mass,com_x | mass=0.454, com_x=0.004 |
| C300 | 89c268bc01fa1d26 | mass,com_x | mass=0.5, com_x=0.005 |
| C301 | 1eb043202970fa0b | mass,com_x | mass=0.04, com_x=0.005 |
| C302 | d199254fe1766a62 | mass,com_x | mass=0.086, com_x=0.004 |
| C303 | 43220e01c3513e38 | mass,com_x | mass=0.132, com_x=0.003 |
| C304 | ce03b63756dc2ec9 | mass,com_x | mass=0.178, com_x=0.002 |
| C305 | d72e47278ed325ae | mass,com_x | mass=0.224, com_x=0.001 |
| C306 | d13eb642b6c2ab57 | mass,com_x | mass=0.316, com_x=-0.001 |
| C307 | 0be72ffd230cb037 | mass,com_x | mass=0.362, com_x=-0.002 |
| C308 | 564e6e9f04140084 | mass,com_x | mass=0.408, com_x=-0.003 |
| C309 | ab221288642a0ecc | mass,com_x | mass=0.454, com_x=-0.004 |
| C310 | 84d97ece0e457be0 | mass,com_x | mass=0.5, com_x=-0.005 |
| C311 | 4aa2b9318a0fb8c5 | mass,com_y | mass=0.04, com_y=-0.005 |
| C312 | bcbc03a6575322dc | mass,com_y | mass=0.086, com_y=-0.004 |
| C313 | 31954b1f3bc5549d | mass,com_y | mass=0.132, com_y=-0.003 |
| C314 | 9406903b9a003e5f | mass,com_y | mass=0.178, com_y=-0.002 |
| C315 | 42a6f297b2c56482 | mass,com_y | mass=0.224, com_y=-0.001 |
| C316 | af9853108607fb8e | mass,com_y | mass=0.316, com_y=0.001 |
| C317 | f81a42c86fa6fb9e | mass,com_y | mass=0.362, com_y=0.002 |
| C318 | c7222850230d5de7 | mass,com_y | mass=0.408, com_y=0.003 |
| C319 | 77f983d8ec7297e8 | mass,com_y | mass=0.454, com_y=0.004 |
| C320 | a79392ae57398bfb | mass,com_y | mass=0.5, com_y=0.005 |
| C321 | 8b22c989089523f5 | mass,com_y | mass=0.04, com_y=0.005 |
| C322 | f46ca5515a29e782 | mass,com_y | mass=0.086, com_y=0.004 |
| C323 | 723203a44e8d6706 | mass,com_y | mass=0.132, com_y=0.003 |
| C324 | aba4262851db0c5e | mass,com_y | mass=0.178, com_y=0.002 |
| C325 | fd360a8bcbd02429 | mass,com_y | mass=0.224, com_y=0.001 |
| C326 | d63dd3f5c6f36209 | mass,com_y | mass=0.316, com_y=-0.001 |
| C327 | bb1b9a00a96349e0 | mass,com_y | mass=0.362, com_y=-0.002 |
| C328 | 7ba413bf65dbb42e | mass,com_y | mass=0.408, com_y=-0.003 |
| C329 | b738cf409e950059 | mass,com_y | mass=0.454, com_y=-0.004 |
| C330 | a9e8da8d53873bbc | mass,com_y | mass=0.5, com_y=-0.005 |
| C331 | b65612ebd9e7e3e1 | mass,com_z | mass=0.04, com_z=-0.005 |
| C332 | a7d3f3ad490baae8 | mass,com_z | mass=0.086, com_z=-0.004 |
| C333 | 7d21b95031ff6664 | mass,com_z | mass=0.132, com_z=-0.003 |
| C334 | 6c12d9a8b606b54a | mass,com_z | mass=0.178, com_z=-0.002 |
| C335 | e02a8dfa79a85c80 | mass,com_z | mass=0.224, com_z=-0.001 |
| C336 | 3b30015dbaed469b | mass,com_z | mass=0.316, com_z=0.001 |
| C337 | 64d3b78de630e5bc | mass,com_z | mass=0.362, com_z=0.002 |
| C338 | 20d61650eb6f440b | mass,com_z | mass=0.408, com_z=0.003 |
| C339 | 1d055bbf62e3141c | mass,com_z | mass=0.454, com_z=0.004 |
| C340 | 5b30030391f534e4 | mass,com_z | mass=0.5, com_z=0.005 |
| C341 | 894483ca73982cb3 | mass,com_z | mass=0.04, com_z=0.005 |
| C342 | d504e64f1902989c | mass,com_z | mass=0.086, com_z=0.004 |
| C343 | 242480f890ee9672 | mass,com_z | mass=0.132, com_z=0.003 |
| C344 | 9bac7c9b1f43477b | mass,com_z | mass=0.178, com_z=0.002 |
| C345 | 77213499cf067515 | mass,com_z | mass=0.224, com_z=0.001 |
| C346 | 6431272d354961d8 | mass,com_z | mass=0.316, com_z=-0.001 |
| C347 | ba9094c7aa302d33 | mass,com_z | mass=0.362, com_z=-0.002 |
| C348 | 6467db86f2080878 | mass,com_z | mass=0.408, com_z=-0.003 |
| C349 | e6b8fcfe273b305d | mass,com_z | mass=0.454, com_z=-0.004 |
| C350 | e1138ce586746eb5 | mass,com_z | mass=0.5, com_z=-0.005 |
| C351 | 20bb6796b05eaee2 | mass,goal_height | mass=0.04, goal_height=0.1 |
| C352 | 0084536d5ee3454b | mass,goal_height | mass=0.086, goal_height=0.12 |
| C353 | 0856cdd31065d676 | mass,goal_height | mass=0.132, goal_height=0.14 |
| C354 | d2ad54a0545fde30 | mass,goal_height | mass=0.178, goal_height=0.16 |
| C355 | e7660d663087fd0b | mass,goal_height | mass=0.224, goal_height=0.18 |
| C356 | 8b04ac46d0c66e1f | mass,goal_height | mass=0.316, goal_height=0.22 |
| C357 | 9e0af5021fb32154 | mass,goal_height | mass=0.362, goal_height=0.24 |
| C358 | 4f8102ece6ecea03 | mass,goal_height | mass=0.408, goal_height=0.26 |
| C359 | b89ee699578edb6a | mass,goal_height | mass=0.454, goal_height=0.28 |
| C360 | 5ff43f8e32f20006 | mass,goal_height | mass=0.5, goal_height=0.3 |
| C361 | 65f7cdb9db181150 | mass,goal_height | mass=0.04, goal_height=0.3 |
| C362 | 2033a4f8b3211474 | mass,goal_height | mass=0.086, goal_height=0.28 |
| C363 | 5436fb7fd7e3f9f6 | mass,goal_height | mass=0.132, goal_height=0.26 |
| C364 | 0a2d41bdd4830d0f | mass,goal_height | mass=0.178, goal_height=0.24 |
| C365 | 63451b60b310fbb0 | mass,goal_height | mass=0.224, goal_height=0.22 |
| C366 | 278f24e192b0c90c | mass,goal_height | mass=0.316, goal_height=0.18 |
| C367 | 180785ff5588f6e3 | mass,goal_height | mass=0.362, goal_height=0.16 |
| C368 | 26580bf7b4611af2 | mass,goal_height | mass=0.408, goal_height=0.14 |
| C369 | 354f6d3cbe5119a7 | mass,goal_height | mass=0.454, goal_height=0.12 |
| C370 | 1917d4b1ee55aefd | mass,goal_height | mass=0.5, goal_height=0.1 |
| C371 | 5acdff7eb5378280 | mass,restitution | mass=0.086, restitution=0.05 |
| C372 | 8848667481534ab5 | mass,restitution | mass=0.132, restitution=0.1 |
| C373 | c48c6218ddf02a25 | mass,restitution | mass=0.178, restitution=0.15 |
| C374 | 3b60a8e74174519e | mass,restitution | mass=0.224, restitution=0.2 |
| C375 | 2a23f08b4b9b48e9 | mass,restitution | mass=0.27, restitution=0.25 |
| C376 | af2f4065bca99285 | mass,restitution | mass=0.316, restitution=0.3 |
| C377 | b2d22660068b1ee0 | mass,restitution | mass=0.362, restitution=0.35 |
| C378 | ba2e4fce2bced4f5 | mass,restitution | mass=0.408, restitution=0.4 |
| C379 | 55b0d63200c1f992 | mass,restitution | mass=0.454, restitution=0.45 |
| C380 | 4675f5f94b5ff362 | mass,restitution | mass=0.5, restitution=0.5 |
| C381 | ced8189c1d53c8b0 | mass,restitution | mass=0.04, restitution=0.5 |
| C382 | 8b7e5a33b0c69209 | mass,restitution | mass=0.086, restitution=0.45 |
| C383 | 44bf20be16873ed1 | mass,restitution | mass=0.132, restitution=0.4 |
| C384 | 0aa07adedc5f8e71 | mass,restitution | mass=0.178, restitution=0.35 |
| C385 | 93fd96390dd0def7 | mass,restitution | mass=0.224, restitution=0.3 |
| C386 | 3d626e2d87ff1d54 | mass,restitution | mass=0.316, restitution=0.2 |
| C387 | c2d12ea98dc3c622 | mass,restitution | mass=0.362, restitution=0.15 |
| C388 | 243844702265f87b | mass,restitution | mass=0.408, restitution=0.1 |
| C389 | 382baacdae8b8365 | mass,restitution | mass=0.454, restitution=0.05 |
| C390 | abd8e8919dc3d1fa | mass,linear_damping | mass=0.086, linear_damping=0.1 |
| C391 | 5c88675424e31555 | mass,linear_damping | mass=0.132, linear_damping=0.2 |
| C392 | 765fdb2093a96767 | mass,linear_damping | mass=0.178, linear_damping=0.3 |
| C393 | f4e8d225bd9a95c2 | mass,linear_damping | mass=0.224, linear_damping=0.4 |
| C394 | 9c89a5960056f231 | mass,linear_damping | mass=0.27, linear_damping=0.5 |
| C395 | 65def60afaf72c9c | mass,linear_damping | mass=0.316, linear_damping=0.6 |
| C396 | 0723471ce4653c67 | mass,linear_damping | mass=0.362, linear_damping=0.7 |
| C397 | dcb3219ad1282c83 | mass,linear_damping | mass=0.408, linear_damping=0.8 |
| C398 | 41db54e3b6731cf5 | mass,linear_damping | mass=0.454, linear_damping=0.9 |
| C399 | da1d95faefd1e9ab | mass,linear_damping | mass=0.5, linear_damping=1.0 |
| C400 | aad785850daf82c7 | mass,linear_damping | mass=0.04, linear_damping=1.0 |
| C401 | 1dfadeebc682946b | mass,linear_damping | mass=0.086, linear_damping=0.9 |
| C402 | 2f951f62c17dedc0 | mass,linear_damping | mass=0.132, linear_damping=0.8 |
| C403 | 444d18e61ef84fbc | mass,linear_damping | mass=0.178, linear_damping=0.7 |
| C404 | 21cadce625efc389 | mass,linear_damping | mass=0.224, linear_damping=0.6 |
| C405 | ee6e48137816f5fc | mass,linear_damping | mass=0.316, linear_damping=0.4 |
| C406 | 417d63dc8054157c | mass,linear_damping | mass=0.362, linear_damping=0.3 |
| C407 | 16ce8eca6594da65 | mass,linear_damping | mass=0.408, linear_damping=0.2 |
| C408 | 134cb03358f28d20 | mass,linear_damping | mass=0.454, linear_damping=0.1 |
| C409 | f7db846457ce2d18 | mass,angular_damping | mass=0.04, angular_damping=0.0 |
| C410 | d60c82a8af0560cf | mass,angular_damping | mass=0.132, angular_damping=0.1 |
| C411 | bd8d7a8c3a98da99 | mass,angular_damping | mass=0.178, angular_damping=0.15 |
| C412 | 59513613bc5d19e7 | mass,angular_damping | mass=0.224, angular_damping=0.2 |
| C413 | 9e094fddc84f6c4c | mass,angular_damping | mass=0.27, angular_damping=0.25 |
| C414 | a8c465700c82c637 | mass,angular_damping | mass=0.316, angular_damping=0.3 |
| C415 | de1f1e90b3671d2c | mass,angular_damping | mass=0.362, angular_damping=0.35 |
| C416 | 315679e652ed7d2a | mass,angular_damping | mass=0.408, angular_damping=0.4 |
| C417 | 25726d62cc6c7eda | mass,angular_damping | mass=0.454, angular_damping=0.45 |
| C418 | 7a5cb2e3989dca38 | mass,angular_damping | mass=0.5, angular_damping=0.5 |
| C419 | 9aca433b9b15461a | mass,angular_damping | mass=0.04, angular_damping=0.5 |
| C420 | 1f529236ce93e5bd | mass,angular_damping | mass=0.086, angular_damping=0.45 |
| C421 | cdaa15fa2eab4f78 | mass,angular_damping | mass=0.132, angular_damping=0.4 |
| C422 | cc54f3fb9ae83c05 | mass,angular_damping | mass=0.178, angular_damping=0.35 |
| C423 | e5d41ff84c19d4b8 | mass,angular_damping | mass=0.224, angular_damping=0.3 |
| C424 | 5034730fdc1c0686 | mass,angular_damping | mass=0.316, angular_damping=0.2 |
| C425 | 4a2c974918631e01 | mass,angular_damping | mass=0.362, angular_damping=0.15 |
| C426 | 21c3f55e079c3347 | mass,angular_damping | mass=0.408, angular_damping=0.1 |
| C427 | a731556bd250d82e | mass,angular_damping | mass=0.5, angular_damping=0.0 |
| C428 | 4f5cc5e2f6e3bd33 | mass,spawn_x | mass=0.04, spawn_x=-0.04 |
| C429 | e550bc53ff11108a | mass,spawn_x | mass=0.086, spawn_x=-0.032 |
| C430 | 172d7a3f7fd4e1a4 | mass,spawn_x | mass=0.132, spawn_x=-0.024 |
| C431 | 71969710fece9fd8 | mass,spawn_x | mass=0.178, spawn_x=-0.016 |
| C432 | 47d3fac04e9f1cba | mass,spawn_x | mass=0.224, spawn_x=-0.008 |
| C433 | 04a6d3c33ef92f5c | mass,spawn_x | mass=0.316, spawn_x=0.008 |
| C434 | 06e95979b0522daf | mass,spawn_x | mass=0.362, spawn_x=0.016 |
| C435 | f0f1940e81765803 | mass,spawn_x | mass=0.408, spawn_x=0.024 |
| C436 | 616c5ce3305d4d0a | mass,spawn_x | mass=0.454, spawn_x=0.032 |
| C437 | fe3df53af6852cea | mass,spawn_x | mass=0.5, spawn_x=0.04 |
| C438 | 756deab2e295bc8a | mass,spawn_x | mass=0.04, spawn_x=0.04 |
| C439 | ee3af657e8198f3e | mass,spawn_x | mass=0.086, spawn_x=0.032 |
| C440 | 6e9e2d2deb545c54 | mass,spawn_x | mass=0.132, spawn_x=0.024 |
| C441 | 29eaff7922d1fe84 | mass,spawn_x | mass=0.178, spawn_x=0.016 |
| C442 | 0475c476db6c80a9 | mass,spawn_x | mass=0.224, spawn_x=0.008 |
| C443 | d65d76fd71b8e4bc | mass,spawn_x | mass=0.316, spawn_x=-0.008 |
| C444 | 7fd5ebc5325ea6e5 | mass,spawn_x | mass=0.362, spawn_x=-0.016 |
| C445 | a5df390cc0fd999c | mass,spawn_x | mass=0.408, spawn_x=-0.024 |
| C446 | adfcf9ae2187565f | mass,spawn_x | mass=0.454, spawn_x=-0.032 |
| C447 | ec909ace4a3337a8 | mass,spawn_x | mass=0.5, spawn_x=-0.04 |
| C448 | 90d6b87d5607c795 | mass,spawn_y | mass=0.04, spawn_y=-0.04 |
| C449 | 79e578d3c18f2c25 | mass,spawn_y | mass=0.086, spawn_y=-0.032 |
| C450 | 9d923147004cc845 | mass,spawn_y | mass=0.132, spawn_y=-0.024 |
| C451 | 2af8557edf48ac67 | mass,spawn_y | mass=0.178, spawn_y=-0.016 |
| C452 | fa6e6f41a75eea79 | mass,spawn_y | mass=0.224, spawn_y=-0.008 |
| C453 | 9d901c8d760a2a07 | mass,spawn_y | mass=0.316, spawn_y=0.008 |
| C454 | 1018d05ed99f6d69 | mass,spawn_y | mass=0.362, spawn_y=0.016 |
| C455 | 78ebc5ba10084b5f | mass,spawn_y | mass=0.408, spawn_y=0.024 |
| C456 | d92bc433e629d983 | mass,spawn_y | mass=0.454, spawn_y=0.032 |
| C457 | 39566bfb0f066bc5 | mass,spawn_y | mass=0.5, spawn_y=0.04 |
| C458 | 6403b18012aca12d | mass,spawn_y | mass=0.04, spawn_y=0.04 |
| C459 | 61f4790a48fa576a | mass,spawn_y | mass=0.086, spawn_y=0.032 |
| C460 | 86795e36219cc862 | mass,spawn_y | mass=0.132, spawn_y=0.024 |
| C461 | 57134a37c1c8a391 | mass,spawn_y | mass=0.178, spawn_y=0.016 |
| C462 | 30af965dd9f5df55 | mass,spawn_y | mass=0.224, spawn_y=0.008 |
| C463 | ebb81b65a6eeaa4a | mass,spawn_y | mass=0.316, spawn_y=-0.008 |
| C464 | 51c8d3d34e522133 | mass,spawn_y | mass=0.362, spawn_y=-0.016 |
| C465 | d10ae810419aaf3c | mass,spawn_y | mass=0.408, spawn_y=-0.024 |
| C466 | 0cd12e7f111d21a9 | mass,spawn_y | mass=0.454, spawn_y=-0.032 |
| C467 | 371c906e77143c15 | mass,spawn_y | mass=0.5, spawn_y=-0.04 |
| C468 | 4c1f08088f1c3aac | mass,spawn_yaw | mass=0.04, spawn_yaw=-0.523598775598 |
| C469 | dba066e19a20fd9c | mass,spawn_yaw | mass=0.086, spawn_yaw=-0.418879020478 |
| C470 | be6815218e3bdeb1 | mass,spawn_yaw | mass=0.132, spawn_yaw=-0.314159265359 |
| C471 | 5b659b0d89d5ca4f | mass,spawn_yaw | mass=0.178, spawn_yaw=-0.209439510239 |
| C472 | 5ede6c923bf7b6b7 | mass,spawn_yaw | mass=0.224, spawn_yaw=-0.10471975512 |
| C473 | 88a80aad0dfb268b | mass,spawn_yaw | mass=0.316, spawn_yaw=0.10471975512 |
| C474 | b1a3e475b5008db0 | mass,spawn_yaw | mass=0.362, spawn_yaw=0.209439510239 |
| C475 | dd2176d8a07707b6 | mass,spawn_yaw | mass=0.408, spawn_yaw=0.314159265359 |
| C476 | 0417b69e3510c528 | mass,spawn_yaw | mass=0.454, spawn_yaw=0.418879020478 |
| C477 | 132c8b074f73aa40 | mass,spawn_yaw | mass=0.5, spawn_yaw=0.523598775598 |
| C478 | 55ed8fae5a0179a8 | mass,spawn_yaw | mass=0.04, spawn_yaw=0.523598775598 |
| C479 | a794bec89886781b | mass,spawn_yaw | mass=0.086, spawn_yaw=0.418879020478 |
| C480 | 2a5eb5fe6c61beee | mass,spawn_yaw | mass=0.132, spawn_yaw=0.314159265359 |
| C481 | 5d94a9f8e4c26743 | mass,spawn_yaw | mass=0.178, spawn_yaw=0.209439510239 |
| C482 | 9b0b6e99b48d223e | mass,spawn_yaw | mass=0.224, spawn_yaw=0.10471975512 |
| C483 | 67fc2e64adffdade | mass,spawn_yaw | mass=0.316, spawn_yaw=-0.10471975512 |
| C484 | e7504ed3996a7569 | mass,spawn_yaw | mass=0.362, spawn_yaw=-0.209439510239 |
| C485 | 93d165a469c77a0e | mass,spawn_yaw | mass=0.408, spawn_yaw=-0.314159265359 |
| C486 | e2a9dfebfab477d3 | mass,spawn_yaw | mass=0.454, spawn_yaw=-0.418879020478 |
| C487 | 3d12dfe20ee07f88 | mass,spawn_yaw | mass=0.5, spawn_yaw=-0.523598775598 |
| C488 | a85ea0014128cf56 | mass,inertia_scale | mass=0.04, inertia_scale=0.5 |
| C489 | b084dfed22453114 | mass,inertia_scale | mass=0.086, inertia_scale=0.65 |
| C490 | 5bfefc82e2ea5e69 | mass,inertia_scale | mass=0.132, inertia_scale=0.8 |
| C491 | 6c3042c6a0bec205 | mass,inertia_scale | mass=0.178, inertia_scale=0.95 |
| C492 | 634cdfc42b897178 | mass,inertia_scale | mass=0.224, inertia_scale=1.1 |
| C493 | 227ea3054ee2251c | mass,inertia_scale | mass=0.27, inertia_scale=1.25 |
| C494 | 487a86fbe9742046 | mass,inertia_scale | mass=0.316, inertia_scale=1.4 |
| C495 | c9d81b60cf024d3b | mass,inertia_scale | mass=0.362, inertia_scale=1.55 |
| C496 | b4242e718da25bd6 | mass,inertia_scale | mass=0.408, inertia_scale=1.7 |
| C497 | 96a60c4e20bb0aae | mass,inertia_scale | mass=0.454, inertia_scale=1.85 |
| C498 | 94a22504b33d6fd3 | mass,inertia_scale | mass=0.5, inertia_scale=2.0 |
| C499 | 463794a398a0342d | mass,inertia_scale | mass=0.04, inertia_scale=2.0 |
| C500 | fe2b3a3a97947850 | mass,inertia_scale | mass=0.086, inertia_scale=1.85 |
| C501 | a9dc94680b335dba | mass,inertia_scale | mass=0.132, inertia_scale=1.7 |
| C502 | a84c3671cf74a637 | mass,inertia_scale | mass=0.178, inertia_scale=1.55 |
| C503 | 457d89fd50551770 | mass,inertia_scale | mass=0.224, inertia_scale=1.4 |
| C504 | 3a8d171a3761d5e9 | mass,inertia_scale | mass=0.316, inertia_scale=1.1 |
| C505 | e127c3539bd61daa | mass,inertia_scale | mass=0.362, inertia_scale=0.95 |
| C506 | 4b52d0b0db093af8 | mass,inertia_scale | mass=0.408, inertia_scale=0.8 |
| C507 | beb2bfb9b106e0b6 | mass,inertia_scale | mass=0.454, inertia_scale=0.65 |
| C508 | 3a7f069d734a2010 | mass,inertia_scale | mass=0.5, inertia_scale=0.5 |
| C509 | abed073949fe6691 | object_friction,dynamic_friction_ratio | object_friction=0.1, dynamic_friction_ratio=0.25 |
| C510 | aefae2b27a7b6fbf | object_friction,dynamic_friction_ratio | object_friction=0.19, dynamic_friction_ratio=0.325 |
| C511 | 931b74f2edced955 | object_friction,dynamic_friction_ratio | object_friction=0.28, dynamic_friction_ratio=0.4 |
| C512 | 7f3c32d54b3df1e8 | object_friction,dynamic_friction_ratio | object_friction=0.37, dynamic_friction_ratio=0.475 |
| C513 | d8c6a06de41e45e4 | object_friction,dynamic_friction_ratio | object_friction=0.46, dynamic_friction_ratio=0.55 |
| C514 | 03a2ff1a485aac80 | object_friction,dynamic_friction_ratio | object_friction=0.55, dynamic_friction_ratio=0.625 |
| C515 | bf15abaf708f8a9c | object_friction,dynamic_friction_ratio | object_friction=0.64, dynamic_friction_ratio=0.7 |
| C516 | 62b531b63de7cd67 | object_friction,dynamic_friction_ratio | object_friction=0.73, dynamic_friction_ratio=0.775 |
| C517 | 47cddb34bc2a4fcc | object_friction,dynamic_friction_ratio | object_friction=0.82, dynamic_friction_ratio=0.85 |
| C518 | fba82299e8a640dd | object_friction,dynamic_friction_ratio | object_friction=0.91, dynamic_friction_ratio=0.925 |
| C519 | 428503c95f3a5e29 | object_friction,dynamic_friction_ratio | object_friction=0.19, dynamic_friction_ratio=0.925 |
| C520 | c9a0fab86ac4591b | object_friction,dynamic_friction_ratio | object_friction=0.28, dynamic_friction_ratio=0.85 |
| C521 | 25d676d06ea221a9 | object_friction,dynamic_friction_ratio | object_friction=0.37, dynamic_friction_ratio=0.775 |
| C522 | a28b870254201920 | object_friction,dynamic_friction_ratio | object_friction=0.46, dynamic_friction_ratio=0.7 |
| C523 | adb38fbab13c8839 | object_friction,dynamic_friction_ratio | object_friction=0.64, dynamic_friction_ratio=0.55 |
| C524 | d3477af00f17fab4 | object_friction,dynamic_friction_ratio | object_friction=0.73, dynamic_friction_ratio=0.475 |
| C525 | c1c2f3991b56bde9 | object_friction,dynamic_friction_ratio | object_friction=0.82, dynamic_friction_ratio=0.4 |
| C526 | 6a5a315a97232183 | object_friction,dynamic_friction_ratio | object_friction=0.91, dynamic_friction_ratio=0.325 |
| C527 | 957c3b8bf36326ae | object_friction,dynamic_friction_ratio | object_friction=1.0, dynamic_friction_ratio=0.25 |
| C528 | e5f7ed98de39cb7b | object_friction,finger_friction | object_friction=0.1, finger_friction=0.1 |
| C529 | b85e2cfe70c24ef0 | object_friction,finger_friction | object_friction=0.19, finger_friction=0.14 |
| C530 | 35e2f93c7c00b500 | object_friction,finger_friction | object_friction=0.28, finger_friction=0.18 |
| C531 | 61c1ad9459fff32f | object_friction,finger_friction | object_friction=0.37, finger_friction=0.22 |
| C532 | b6b8407247d73a84 | object_friction,finger_friction | object_friction=0.46, finger_friction=0.26 |
| C533 | 0bd14d26faad5caa | object_friction,finger_friction | object_friction=0.55, finger_friction=0.3 |
| C534 | 0739a9b7731c4ee8 | object_friction,finger_friction | object_friction=0.64, finger_friction=0.34 |
| C535 | 82a476bddceb1195 | object_friction,finger_friction | object_friction=0.73, finger_friction=0.38 |
| C536 | e1456ff181a71bc0 | object_friction,finger_friction | object_friction=0.82, finger_friction=0.42 |
| C537 | 0f17d103910471b9 | object_friction,finger_friction | object_friction=0.91, finger_friction=0.46 |
| C538 | e97b74acc4e1e827 | object_friction,finger_friction | object_friction=1.0, finger_friction=0.5 |
| C539 | 222dca2bebf8745d | object_friction,finger_friction | object_friction=0.1, finger_friction=0.5 |
| C540 | 016fac818503717c | object_friction,finger_friction | object_friction=0.19, finger_friction=0.46 |
| C541 | 6a459ee456e74a00 | object_friction,finger_friction | object_friction=0.28, finger_friction=0.42 |
| C542 | 9fe5cfea69500c66 | object_friction,finger_friction | object_friction=0.37, finger_friction=0.38 |
| C543 | d6e3e150c33a1788 | object_friction,finger_friction | object_friction=0.46, finger_friction=0.34 |
| C544 | 888f9b0b7bfc32d5 | object_friction,finger_friction | object_friction=0.64, finger_friction=0.26 |
| C545 | eed815f04805ebe3 | object_friction,finger_friction | object_friction=0.73, finger_friction=0.22 |
| C546 | 107a7929a69a6738 | object_friction,finger_friction | object_friction=0.82, finger_friction=0.18 |
| C547 | 0bab410c6ae2817a | object_friction,finger_friction | object_friction=0.91, finger_friction=0.14 |
| C548 | ff9356c9cbec2edb | object_friction,finger_friction | object_friction=1.0, finger_friction=0.1 |
| C549 | d530e723f98c0523 | object_friction,table_friction | object_friction=0.1, table_friction=0.1 |
| C550 | b6c2bc20457f8ae6 | object_friction,table_friction | object_friction=0.19, table_friction=0.17 |
| C551 | bfe0b6a576677e34 | object_friction,table_friction | object_friction=0.28, table_friction=0.24 |
| C552 | a87599a456b85f30 | object_friction,table_friction | object_friction=0.37, table_friction=0.31 |
| C553 | bcf9b9346d55f9ea | object_friction,table_friction | object_friction=0.46, table_friction=0.38 |
| C554 | 9b27672b83d46b1a | object_friction,table_friction | object_friction=0.55, table_friction=0.45 |
| C555 | d97f4033253337cb | object_friction,table_friction | object_friction=0.64, table_friction=0.52 |
| C556 | 759b0bdef2c0b305 | object_friction,table_friction | object_friction=0.73, table_friction=0.59 |
| C557 | bf7920bd205db2d2 | object_friction,table_friction | object_friction=0.82, table_friction=0.66 |
| C558 | 5aad0a9753a7c88a | object_friction,table_friction | object_friction=0.91, table_friction=0.73 |
| C559 | 72844e4efc65e708 | object_friction,table_friction | object_friction=1.0, table_friction=0.8 |
| C560 | ec5acf8fa3ea5560 | object_friction,table_friction | object_friction=0.1, table_friction=0.8 |
| C561 | 02ab244da520be8e | object_friction,table_friction | object_friction=0.19, table_friction=0.73 |
| C562 | 0ffd366d69d87d7e | object_friction,table_friction | object_friction=0.28, table_friction=0.66 |
| C563 | 9e81ebf6becb7e59 | object_friction,table_friction | object_friction=0.37, table_friction=0.59 |
| C564 | aa82109f63eb0fce | object_friction,table_friction | object_friction=0.46, table_friction=0.52 |
| C565 | 92a3237df294d8b6 | object_friction,table_friction | object_friction=0.64, table_friction=0.38 |
| C566 | 2183e7fc749004ae | object_friction,table_friction | object_friction=0.73, table_friction=0.31 |
| C567 | b5a905d3db0d8625 | object_friction,table_friction | object_friction=0.82, table_friction=0.24 |
| C568 | a6bfde82131f2b41 | object_friction,table_friction | object_friction=0.91, table_friction=0.17 |
| C569 | 9ee6423adff22c55 | object_friction,table_friction | object_friction=1.0, table_friction=0.1 |
| C570 | 55ec3ce163dd5f55 | object_friction,size | object_friction=0.1, size=0.03 |
| C571 | c8c436b77d472212 | object_friction,size | object_friction=0.19, size=0.032 |
| C572 | fd245dac8ea438fb | object_friction,size | object_friction=0.28, size=0.034 |
| C573 | 5440399022682df7 | object_friction,size | object_friction=0.37, size=0.036 |
| C574 | 441f372e933c55e0 | object_friction,size | object_friction=0.46, size=0.038 |
| C575 | 46b1d3cccc5e7a82 | object_friction,size | object_friction=0.64, size=0.042 |
| C576 | e00b11c630f671f4 | object_friction,size | object_friction=0.73, size=0.044 |
| C577 | a45f55a7fe268778 | object_friction,size | object_friction=0.82, size=0.046 |
| C578 | a8d86271e22ef139 | object_friction,size | object_friction=0.91, size=0.048 |
| C579 | b5c18a70f353d59f | object_friction,size | object_friction=1.0, size=0.05 |
| C580 | 6ff8b7fd4c6477e1 | object_friction,size | object_friction=0.1, size=0.05 |
| C581 | 0f8edf69f2972945 | object_friction,size | object_friction=0.19, size=0.048 |
| C582 | 4b330d54170ab9eb | object_friction,size | object_friction=0.28, size=0.046 |
| C583 | d0734f9e2ff88a47 | object_friction,size | object_friction=0.37, size=0.044 |
| C584 | e3f4044f7b64cd23 | object_friction,size | object_friction=0.46, size=0.042 |
| C585 | 0704b0c88ebd7389 | object_friction,size | object_friction=0.64, size=0.038 |
| C586 | 83ab8fd07212e8ac | object_friction,size | object_friction=0.73, size=0.036 |
| C587 | 2b3fc9c57c296662 | object_friction,size | object_friction=0.82, size=0.034 |
| C588 | 6651957fbcade6f6 | object_friction,size | object_friction=0.91, size=0.032 |
| C589 | 9d1fca897d0a0d09 | object_friction,size | object_friction=1.0, size=0.03 |
| C590 | b5b8fe24bdda5288 | object_friction,shape | object_friction=0.1, shape=sphere |
| C591 | ea1ba8481d1dda82 | object_friction,shape | object_friction=0.19, shape=sphere |
| C592 | 0e7f4fa27977e630 | object_friction,shape | object_friction=0.28, shape=sphere |
| C593 | b4aaf738b8c90756 | object_friction,shape | object_friction=0.37, shape=sphere |
| C594 | 6ae8f5f981d9ca3d | object_friction,shape | object_friction=0.46, shape=sphere |
| C595 | f27023daf006ee0f | object_friction,shape | object_friction=0.55, shape=sphere |
| C596 | bd74dad4d29a9ce0 | object_friction,shape | object_friction=0.64, shape=sphere |
| C597 | 553ad9c900108a88 | object_friction,shape | object_friction=0.73, shape=sphere |
| C598 | ae3fe7c876c24dec | object_friction,shape | object_friction=0.82, shape=sphere |
| C599 | 37b8dff0c10d9e7d | object_friction,shape | object_friction=0.91, shape=sphere |
| C600 | 9aeee83cb8360de5 | object_friction,shape | object_friction=1.0, shape=sphere |
| C601 | 19ce7c402afba08b | object_friction,com_x | object_friction=0.1, com_x=-0.005 |
| C602 | 26b3159b9943a7ff | object_friction,com_x | object_friction=0.19, com_x=-0.004 |
| C603 | 3e4a09826c078062 | object_friction,com_x | object_friction=0.28, com_x=-0.003 |
| C604 | 17088128993dc88e | object_friction,com_x | object_friction=0.37, com_x=-0.002 |
| C605 | f86a576f2502b625 | object_friction,com_x | object_friction=0.46, com_x=-0.001 |
| C606 | fbca2d7395f840c0 | object_friction,com_x | object_friction=0.64, com_x=0.001 |
| C607 | 6835035d0065809c | object_friction,com_x | object_friction=0.73, com_x=0.002 |
| C608 | fc2bdd11d0e0f653 | object_friction,com_x | object_friction=0.82, com_x=0.003 |
| C609 | 8091c7507bed4134 | object_friction,com_x | object_friction=0.91, com_x=0.004 |
| C610 | f614a5b49c691363 | object_friction,com_x | object_friction=1.0, com_x=0.005 |
| C611 | 862d978543add6a6 | object_friction,com_x | object_friction=0.1, com_x=0.005 |
| C612 | 13ed9035637a6b2f | object_friction,com_x | object_friction=0.19, com_x=0.004 |
| C613 | 44629b40b4a7c276 | object_friction,com_x | object_friction=0.28, com_x=0.003 |
| C614 | acc9647d6277163e | object_friction,com_x | object_friction=0.37, com_x=0.002 |
| C615 | b9290fa74f966871 | object_friction,com_x | object_friction=0.46, com_x=0.001 |
| C616 | b9dd4d0aa5dcac5c | object_friction,com_x | object_friction=0.64, com_x=-0.001 |
| C617 | 75887772ba1aeef2 | object_friction,com_x | object_friction=0.73, com_x=-0.002 |
| C618 | bcfbf847ddc6978d | object_friction,com_x | object_friction=0.82, com_x=-0.003 |
| C619 | 7fbdc432cd347301 | object_friction,com_x | object_friction=0.91, com_x=-0.004 |
| C620 | f287f3616f7774fd | object_friction,com_x | object_friction=1.0, com_x=-0.005 |
| C621 | 071f66d92a54a5c1 | object_friction,com_y | object_friction=0.1, com_y=-0.005 |
| C622 | 96cc05d5b559fd6f | object_friction,com_y | object_friction=0.19, com_y=-0.004 |
| C623 | 698dff2f6281b588 | object_friction,com_y | object_friction=0.28, com_y=-0.003 |
| C624 | c5f2bdc53f94c0d0 | object_friction,com_y | object_friction=0.37, com_y=-0.002 |
| C625 | 179507f02ab79b31 | object_friction,com_y | object_friction=0.46, com_y=-0.001 |
| C626 | 02f50045b2c4a834 | object_friction,com_y | object_friction=0.64, com_y=0.001 |
| C627 | 55a784a537dd4d37 | object_friction,com_y | object_friction=0.73, com_y=0.002 |
| C628 | 4ef5ca23cd941043 | object_friction,com_y | object_friction=0.82, com_y=0.003 |
| C629 | ffa59a3e6521eab5 | object_friction,com_y | object_friction=0.91, com_y=0.004 |
| C630 | bef372aea062f049 | object_friction,com_y | object_friction=1.0, com_y=0.005 |
| C631 | 99f6b74d3e32b3dd | object_friction,com_y | object_friction=0.1, com_y=0.005 |
| C632 | 6f102d96a7204f01 | object_friction,com_y | object_friction=0.19, com_y=0.004 |
| C633 | 1b50459e841777f2 | object_friction,com_y | object_friction=0.28, com_y=0.003 |
| C634 | dc3e607e766b7125 | object_friction,com_y | object_friction=0.37, com_y=0.002 |
| C635 | 107ac552877850db | object_friction,com_y | object_friction=0.46, com_y=0.001 |
| C636 | 5b9ac1c7c8acffaa | object_friction,com_y | object_friction=0.64, com_y=-0.001 |
| C637 | 46593a1c6ef17398 | object_friction,com_y | object_friction=0.73, com_y=-0.002 |
| C638 | bc1edae7c655de21 | object_friction,com_y | object_friction=0.82, com_y=-0.003 |
| C639 | b11d05b2c8876ebe | object_friction,com_y | object_friction=0.91, com_y=-0.004 |
| C640 | b2787522a09b3b3e | object_friction,com_y | object_friction=1.0, com_y=-0.005 |
| C641 | 2a45d9269634f470 | object_friction,com_z | object_friction=0.1, com_z=-0.005 |
| C642 | c13625ddba87e0cb | object_friction,com_z | object_friction=0.19, com_z=-0.004 |
| C643 | 563852a713ae99e4 | object_friction,com_z | object_friction=0.28, com_z=-0.003 |
| C644 | 3c745b4aaac7528a | object_friction,com_z | object_friction=0.37, com_z=-0.002 |
| C645 | 7858b0f3b7fda30f | object_friction,com_z | object_friction=0.46, com_z=-0.001 |
| C646 | 9dedd383dd7abded | object_friction,com_z | object_friction=0.64, com_z=0.001 |
| C647 | 402570885f849650 | object_friction,com_z | object_friction=0.73, com_z=0.002 |
| C648 | a6e40a7ffdbc6f9b | object_friction,com_z | object_friction=0.82, com_z=0.003 |
| C649 | cd1ce71e4aed0c62 | object_friction,com_z | object_friction=0.91, com_z=0.004 |
| C650 | 3f53b32f8118b23e | object_friction,com_z | object_friction=1.0, com_z=0.005 |
| C651 | 5f837fca5877ae8a | object_friction,com_z | object_friction=0.1, com_z=0.005 |
| C652 | 3381c68e5c1e8209 | object_friction,com_z | object_friction=0.19, com_z=0.004 |
| C653 | 4e3a671d3fbc37e0 | object_friction,com_z | object_friction=0.28, com_z=0.003 |
| C654 | 7364d5b7e7822e69 | object_friction,com_z | object_friction=0.37, com_z=0.002 |
| C655 | dac4b3b31bf63d8b | object_friction,com_z | object_friction=0.46, com_z=0.001 |
| C656 | dc5e6dedebd2c400 | object_friction,com_z | object_friction=0.64, com_z=-0.001 |
| C657 | 5f4867c58e480a2b | object_friction,com_z | object_friction=0.73, com_z=-0.002 |
| C658 | aa10baddf76de097 | object_friction,com_z | object_friction=0.82, com_z=-0.003 |
| C659 | e303b712aea2d29c | object_friction,com_z | object_friction=0.91, com_z=-0.004 |
| C660 | 198fff1b2ef8645f | object_friction,com_z | object_friction=1.0, com_z=-0.005 |
| C661 | 346e7af7bc1a2190 | object_friction,goal_height | object_friction=0.1, goal_height=0.1 |
| C662 | cda75b49fd9c16fc | object_friction,goal_height | object_friction=0.19, goal_height=0.12 |
| C663 | dd8c736f67a87a72 | object_friction,goal_height | object_friction=0.28, goal_height=0.14 |
| C664 | d6b7b6a679a21797 | object_friction,goal_height | object_friction=0.37, goal_height=0.16 |
| C665 | 4c6a733edc8bb77c | object_friction,goal_height | object_friction=0.46, goal_height=0.18 |
| C666 | 2c52adeb1dc42fb1 | object_friction,goal_height | object_friction=0.64, goal_height=0.22 |
| C667 | e2d16b6422887f02 | object_friction,goal_height | object_friction=0.73, goal_height=0.24 |
| C668 | 9c760589c06026bf | object_friction,goal_height | object_friction=0.82, goal_height=0.26 |
| C669 | 4daae7e5a727a823 | object_friction,goal_height | object_friction=0.91, goal_height=0.28 |
| C670 | 5487ae0e6aded038 | object_friction,goal_height | object_friction=1.0, goal_height=0.3 |
| C671 | 1efad5a8ce2d38d3 | object_friction,goal_height | object_friction=0.1, goal_height=0.3 |
| C672 | 67d89a81979adeed | object_friction,goal_height | object_friction=0.19, goal_height=0.28 |
| C673 | 4fa61ffa1ae4de45 | object_friction,goal_height | object_friction=0.28, goal_height=0.26 |
| C674 | 6a65a438128b89f4 | object_friction,goal_height | object_friction=0.37, goal_height=0.24 |
| C675 | 2b50185af4660248 | object_friction,goal_height | object_friction=0.46, goal_height=0.22 |
| C676 | ab1a519febb40dc9 | object_friction,goal_height | object_friction=0.64, goal_height=0.18 |
| C677 | ef429be64d63014a | object_friction,goal_height | object_friction=0.73, goal_height=0.16 |
| C678 | 452a5e31ead67d38 | object_friction,goal_height | object_friction=0.82, goal_height=0.14 |
| C679 | 76098dab49efa790 | object_friction,goal_height | object_friction=0.91, goal_height=0.12 |
| C680 | 9a4a6f0388932f99 | object_friction,goal_height | object_friction=1.0, goal_height=0.1 |
| C681 | 1d48f8ca20dbb798 | object_friction,restitution | object_friction=0.19, restitution=0.05 |
| C682 | baf41e95f37c763f | object_friction,restitution | object_friction=0.28, restitution=0.1 |
| C683 | 11125e71ae5aa0b8 | object_friction,restitution | object_friction=0.37, restitution=0.15 |
| C684 | a3cb4ccbb1b6d369 | object_friction,restitution | object_friction=0.46, restitution=0.2 |
| C685 | 30e05a0dcd0fa60b | object_friction,restitution | object_friction=0.55, restitution=0.25 |
| C686 | 424ebfa2df028189 | object_friction,restitution | object_friction=0.64, restitution=0.3 |
| C687 | 212bf21d01418321 | object_friction,restitution | object_friction=0.73, restitution=0.35 |
| C688 | b8224fd953f5f917 | object_friction,restitution | object_friction=0.82, restitution=0.4 |
| C689 | 797ac18aaa59d717 | object_friction,restitution | object_friction=0.91, restitution=0.45 |
| C690 | fd3d79690c9389b1 | object_friction,restitution | object_friction=1.0, restitution=0.5 |
| C691 | f044713f1548c8ab | object_friction,restitution | object_friction=0.1, restitution=0.5 |
| C692 | 10a4ab49acbd2dfe | object_friction,restitution | object_friction=0.19, restitution=0.45 |
| C693 | 337c2f35bdb695b8 | object_friction,restitution | object_friction=0.28, restitution=0.4 |
| C694 | ca3a3b0f22179e91 | object_friction,restitution | object_friction=0.37, restitution=0.35 |
| C695 | 350ae17df06344ed | object_friction,restitution | object_friction=0.46, restitution=0.3 |
| C696 | 99b6514aaeaedf60 | object_friction,restitution | object_friction=0.64, restitution=0.2 |
| C697 | e16b6c1788fc3443 | object_friction,restitution | object_friction=0.73, restitution=0.15 |
| C698 | 5a60c520d671f2fd | object_friction,restitution | object_friction=0.82, restitution=0.1 |
| C699 | 076d1e27ac36e65c | object_friction,restitution | object_friction=0.91, restitution=0.05 |
| C700 | 149c4e47374f7b0d | object_friction,linear_damping | object_friction=0.19, linear_damping=0.1 |
| C701 | 8eb2fc407c4d0896 | object_friction,linear_damping | object_friction=0.28, linear_damping=0.2 |
| C702 | 4834df3d7c5ab8a7 | object_friction,linear_damping | object_friction=0.37, linear_damping=0.3 |
| C703 | 7d2adca47f250848 | object_friction,linear_damping | object_friction=0.46, linear_damping=0.4 |
| C704 | f498dde5ea272dde | object_friction,linear_damping | object_friction=0.55, linear_damping=0.5 |
| C705 | ae301cc6e8f8f7eb | object_friction,linear_damping | object_friction=0.64, linear_damping=0.6 |
| C706 | 002fd9ae21e50ec7 | object_friction,linear_damping | object_friction=0.73, linear_damping=0.7 |
| C707 | 78137c9ce58321c1 | object_friction,linear_damping | object_friction=0.82, linear_damping=0.8 |
| C708 | 1173843a7787cf14 | object_friction,linear_damping | object_friction=0.91, linear_damping=0.9 |
| C709 | 057d108493b3e509 | object_friction,linear_damping | object_friction=1.0, linear_damping=1.0 |
| C710 | f2c86afc098f014b | object_friction,linear_damping | object_friction=0.1, linear_damping=1.0 |
| C711 | 3996fc3ee61e43b5 | object_friction,linear_damping | object_friction=0.19, linear_damping=0.9 |
| C712 | 23c31db2dec89d58 | object_friction,linear_damping | object_friction=0.28, linear_damping=0.8 |
| C713 | 4bfc7bf0b086927c | object_friction,linear_damping | object_friction=0.37, linear_damping=0.7 |
| C714 | fcdc8b5539dc251b | object_friction,linear_damping | object_friction=0.46, linear_damping=0.6 |
| C715 | 8ba11666c3973b58 | object_friction,linear_damping | object_friction=0.64, linear_damping=0.4 |
| C716 | 8d1a076e338cba54 | object_friction,linear_damping | object_friction=0.73, linear_damping=0.3 |
| C717 | 90be8efb3fd5091e | object_friction,linear_damping | object_friction=0.82, linear_damping=0.2 |
| C718 | 6917fd6de55dbea1 | object_friction,linear_damping | object_friction=0.91, linear_damping=0.1 |
| C719 | 128a18a420b9626c | object_friction,angular_damping | object_friction=0.1, angular_damping=0.0 |
| C720 | 36d3ef0cf856f114 | object_friction,angular_damping | object_friction=0.28, angular_damping=0.1 |
| C721 | a0eea70f55a3f476 | object_friction,angular_damping | object_friction=0.37, angular_damping=0.15 |
| C722 | ded6f1304d31242e | object_friction,angular_damping | object_friction=0.46, angular_damping=0.2 |
| C723 | 99c5f3ae15a8fcbf | object_friction,angular_damping | object_friction=0.55, angular_damping=0.25 |
| C724 | bf92fe8c2fcfdbad | object_friction,angular_damping | object_friction=0.64, angular_damping=0.3 |
| C725 | 1725c62bd2b47396 | object_friction,angular_damping | object_friction=0.73, angular_damping=0.35 |
| C726 | ea6eb334608f8c3f | object_friction,angular_damping | object_friction=0.82, angular_damping=0.4 |
| C727 | 9ee7a2feddb3eba9 | object_friction,angular_damping | object_friction=0.91, angular_damping=0.45 |
| C728 | 1583aebde8f8376c | object_friction,angular_damping | object_friction=1.0, angular_damping=0.5 |
| C729 | 06781349b9c7b5d0 | object_friction,angular_damping | object_friction=0.1, angular_damping=0.5 |
| C730 | 7bc382d6733f2b61 | object_friction,angular_damping | object_friction=0.19, angular_damping=0.45 |
| C731 | a4945f2b0fb9f280 | object_friction,angular_damping | object_friction=0.28, angular_damping=0.4 |
| C732 | e5783fe4358dfc23 | object_friction,angular_damping | object_friction=0.37, angular_damping=0.35 |
| C733 | 3774e6936e1c389e | object_friction,angular_damping | object_friction=0.46, angular_damping=0.3 |
| C734 | 6c2455e3ed1e091e | object_friction,angular_damping | object_friction=0.64, angular_damping=0.2 |
| C735 | ec4a4208081fcd4d | object_friction,angular_damping | object_friction=0.73, angular_damping=0.15 |
| C736 | f98b087897a2cc07 | object_friction,angular_damping | object_friction=0.82, angular_damping=0.1 |
| C737 | 13270e0ec44ed830 | object_friction,angular_damping | object_friction=1.0, angular_damping=0.0 |
| C738 | d318f957096fc45e | object_friction,spawn_x | object_friction=0.1, spawn_x=-0.04 |
| C739 | 371d35b2152759db | object_friction,spawn_x | object_friction=0.19, spawn_x=-0.032 |
| C740 | a9361fb764bc7dd8 | object_friction,spawn_x | object_friction=0.28, spawn_x=-0.024 |
| C741 | c3d69b9f006eaa89 | object_friction,spawn_x | object_friction=0.37, spawn_x=-0.016 |
| C742 | faeb2c40a05cca4b | object_friction,spawn_x | object_friction=0.46, spawn_x=-0.008 |
| C743 | b2f79e6f27456ea9 | object_friction,spawn_x | object_friction=0.64, spawn_x=0.008 |
| C744 | 02255c63851a90d2 | object_friction,spawn_x | object_friction=0.73, spawn_x=0.016 |
| C745 | 0b29f37fe2059dcf | object_friction,spawn_x | object_friction=0.82, spawn_x=0.024 |
| C746 | 6812ddd5b99ab7ea | object_friction,spawn_x | object_friction=0.91, spawn_x=0.032 |
| C747 | dc16d1f9de2d004b | object_friction,spawn_x | object_friction=1.0, spawn_x=0.04 |
| C748 | 6b39fe6925d9f990 | object_friction,spawn_x | object_friction=0.1, spawn_x=0.04 |
| C749 | 4e5805817a7777e7 | object_friction,spawn_x | object_friction=0.19, spawn_x=0.032 |
| C750 | bbeed9512e994f9f | object_friction,spawn_x | object_friction=0.28, spawn_x=0.024 |
| C751 | c49abe1a4e34e8d2 | object_friction,spawn_x | object_friction=0.37, spawn_x=0.016 |
| C752 | 40ee4cc65402c93a | object_friction,spawn_x | object_friction=0.46, spawn_x=0.008 |
| C753 | d1b8b5ac79d035f2 | object_friction,spawn_x | object_friction=0.64, spawn_x=-0.008 |
| C754 | 4b7d6063e9d14e08 | object_friction,spawn_x | object_friction=0.73, spawn_x=-0.016 |
| C755 | be3c17b070a64c11 | object_friction,spawn_x | object_friction=0.82, spawn_x=-0.024 |
| C756 | 2af9be17e7de8809 | object_friction,spawn_x | object_friction=0.91, spawn_x=-0.032 |
| C757 | 947d76f816e08038 | object_friction,spawn_x | object_friction=1.0, spawn_x=-0.04 |
| C758 | 47d1fe58aa90f935 | object_friction,spawn_y | object_friction=0.1, spawn_y=-0.04 |
| C759 | 601a80c0c7fa0434 | object_friction,spawn_y | object_friction=0.19, spawn_y=-0.032 |
| C760 | 7943674621294852 | object_friction,spawn_y | object_friction=0.28, spawn_y=-0.024 |
| C761 | cf137c798e7a9cdf | object_friction,spawn_y | object_friction=0.37, spawn_y=-0.016 |
| C762 | ef627cf3b93c177f | object_friction,spawn_y | object_friction=0.46, spawn_y=-0.008 |
| C763 | 54cb2ead98ded930 | object_friction,spawn_y | object_friction=0.64, spawn_y=0.008 |
| C764 | 5624fd7ed06e2044 | object_friction,spawn_y | object_friction=0.73, spawn_y=0.016 |
| C765 | 94cebadfebafe17a | object_friction,spawn_y | object_friction=0.82, spawn_y=0.024 |
| C766 | 6f459480665bfd4b | object_friction,spawn_y | object_friction=0.91, spawn_y=0.032 |
| C767 | c94ddebfe8b37e29 | object_friction,spawn_y | object_friction=1.0, spawn_y=0.04 |
| C768 | 4a5649cd89f77a10 | object_friction,spawn_y | object_friction=0.1, spawn_y=0.04 |
| C769 | 0ac466a734b70cbf | object_friction,spawn_y | object_friction=0.19, spawn_y=0.032 |
| C770 | e9812d34e941e942 | object_friction,spawn_y | object_friction=0.28, spawn_y=0.024 |
| C771 | a78ced43b15869dd | object_friction,spawn_y | object_friction=0.37, spawn_y=0.016 |
| C772 | d28599c6b3f22637 | object_friction,spawn_y | object_friction=0.46, spawn_y=0.008 |
| C773 | 7df6462aefefae45 | object_friction,spawn_y | object_friction=0.64, spawn_y=-0.008 |
| C774 | 372bf61de0415116 | object_friction,spawn_y | object_friction=0.73, spawn_y=-0.016 |
| C775 | 195b31f36b6c43ec | object_friction,spawn_y | object_friction=0.82, spawn_y=-0.024 |
| C776 | 64c19b149137a2bf | object_friction,spawn_y | object_friction=0.91, spawn_y=-0.032 |
| C777 | 5512b5a446f129e9 | object_friction,spawn_y | object_friction=1.0, spawn_y=-0.04 |
| C778 | de0582b8e053682c | object_friction,spawn_yaw | object_friction=0.1, spawn_yaw=-0.523598775598 |
| C779 | 35022c898f625deb | object_friction,spawn_yaw | object_friction=0.19, spawn_yaw=-0.418879020478 |
| C780 | 9cc706027ece97b6 | object_friction,spawn_yaw | object_friction=0.28, spawn_yaw=-0.314159265359 |
| C781 | f444669f5df24da5 | object_friction,spawn_yaw | object_friction=0.37, spawn_yaw=-0.209439510239 |
| C782 | 9e1438b5c08ade77 | object_friction,spawn_yaw | object_friction=0.46, spawn_yaw=-0.10471975512 |
| C783 | 520acf8053b42fa4 | object_friction,spawn_yaw | object_friction=0.64, spawn_yaw=0.10471975512 |
| C784 | 63da4cb357bd1caa | object_friction,spawn_yaw | object_friction=0.73, spawn_yaw=0.209439510239 |
| C785 | 3aa53cb9ab4a75c6 | object_friction,spawn_yaw | object_friction=0.82, spawn_yaw=0.314159265359 |
| C786 | d15bb048149354a7 | object_friction,spawn_yaw | object_friction=0.91, spawn_yaw=0.418879020478 |
| C787 | 580466e8ce2d6f96 | object_friction,spawn_yaw | object_friction=1.0, spawn_yaw=0.523598775598 |
| C788 | 9c48551ee59cad5e | object_friction,spawn_yaw | object_friction=0.1, spawn_yaw=0.523598775598 |
| C789 | c1b747ee2e10f9f9 | object_friction,spawn_yaw | object_friction=0.19, spawn_yaw=0.418879020478 |
| C790 | 714c3b14fa45b1d1 | object_friction,spawn_yaw | object_friction=0.28, spawn_yaw=0.314159265359 |
| C791 | 0d1fd2cfae58dd27 | object_friction,spawn_yaw | object_friction=0.37, spawn_yaw=0.209439510239 |
| C792 | a60993bb44e02528 | object_friction,spawn_yaw | object_friction=0.46, spawn_yaw=0.10471975512 |
| C793 | b5a1a59e9cbe7dba | object_friction,spawn_yaw | object_friction=0.64, spawn_yaw=-0.10471975512 |
| C794 | e0683c24bd19b743 | object_friction,spawn_yaw | object_friction=0.73, spawn_yaw=-0.209439510239 |
| C795 | 10dab32f2b5d7057 | object_friction,spawn_yaw | object_friction=0.82, spawn_yaw=-0.314159265359 |
| C796 | 8d8c56950b9b3ac1 | object_friction,spawn_yaw | object_friction=0.91, spawn_yaw=-0.418879020478 |
| C797 | 287baf8d57eb1737 | object_friction,spawn_yaw | object_friction=1.0, spawn_yaw=-0.523598775598 |
| C798 | 2204bcd414bbc6fb | object_friction,inertia_scale | object_friction=0.1, inertia_scale=0.5 |
| C799 | 6dcdcc66e995a8df | object_friction,inertia_scale | object_friction=0.19, inertia_scale=0.65 |
| C800 | d5e3bff1188d8ac4 | object_friction,inertia_scale | object_friction=0.28, inertia_scale=0.8 |
| C801 | 823dece34e3f4ba0 | object_friction,inertia_scale | object_friction=0.37, inertia_scale=0.95 |
| C802 | fdd81f38313ef827 | object_friction,inertia_scale | object_friction=0.46, inertia_scale=1.1 |
| C803 | 4feacbaae2281c2f | object_friction,inertia_scale | object_friction=0.55, inertia_scale=1.25 |
| C804 | 4902734666684a3e | object_friction,inertia_scale | object_friction=0.64, inertia_scale=1.4 |
| C805 | fe12d691737ddd06 | object_friction,inertia_scale | object_friction=0.73, inertia_scale=1.55 |
| C806 | 08f20c05c62e8b25 | object_friction,inertia_scale | object_friction=0.82, inertia_scale=1.7 |
| C807 | 407d702a56e3b02f | object_friction,inertia_scale | object_friction=0.91, inertia_scale=1.85 |
| C808 | e58df027cee0c4dc | object_friction,inertia_scale | object_friction=1.0, inertia_scale=2.0 |
| C809 | 5f5a5d3433fef17a | object_friction,inertia_scale | object_friction=0.1, inertia_scale=2.0 |
| C810 | ae73c13b4fbcea28 | object_friction,inertia_scale | object_friction=0.19, inertia_scale=1.85 |
| C811 | d389d80281092a01 | object_friction,inertia_scale | object_friction=0.28, inertia_scale=1.7 |
| C812 | ab2a9e7956663a0c | object_friction,inertia_scale | object_friction=0.37, inertia_scale=1.55 |
| C813 | 6ef788597977c524 | object_friction,inertia_scale | object_friction=0.46, inertia_scale=1.4 |
| C814 | 3963ce753beeeeac | object_friction,inertia_scale | object_friction=0.64, inertia_scale=1.1 |
| C815 | 4e4cea65106ceeea | object_friction,inertia_scale | object_friction=0.73, inertia_scale=0.95 |
| C816 | 7572f4629bf354c6 | object_friction,inertia_scale | object_friction=0.82, inertia_scale=0.8 |
| C817 | a0e990cca31848d0 | object_friction,inertia_scale | object_friction=0.91, inertia_scale=0.65 |
| C818 | 03a35f9d2a148a4a | object_friction,inertia_scale | object_friction=1.0, inertia_scale=0.5 |
| C819 | c160a1fd529caeef | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.25, finger_friction=0.1 |
| C820 | 66f582059aa2cab0 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.325, finger_friction=0.14 |
| C821 | f645c949420f4fd3 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.4, finger_friction=0.18 |
| C822 | 6791332577b9d016 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.475, finger_friction=0.22 |
| C823 | 4a7fed5a4dd9ad69 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.55, finger_friction=0.26 |
| C824 | 30eeaebc025d58de | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.625, finger_friction=0.3 |
| C825 | 76189681a7d81bd8 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.7, finger_friction=0.34 |
| C826 | a29494c08d27850d | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.775, finger_friction=0.38 |
| C827 | dffe0f0e1d11a3b1 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.85, finger_friction=0.42 |
| C828 | b41055e098bcb8a0 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.925, finger_friction=0.46 |
| C829 | f1784e4d3b120d60 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.25, finger_friction=0.5 |
| C830 | 79a8934b28e6f7bc | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.325, finger_friction=0.46 |
| C831 | 22575341650db0f7 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.4, finger_friction=0.42 |
| C832 | 490f0c5c76de52d2 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.475, finger_friction=0.38 |
| C833 | 802f865e201c9fb2 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.55, finger_friction=0.34 |
| C834 | 3dbb8f315814b493 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.7, finger_friction=0.26 |
| C835 | 0effbe9d8a69c2b7 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.775, finger_friction=0.22 |
| C836 | b25be270f7cb6d2c | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.85, finger_friction=0.18 |
| C837 | eb6dcf0595248545 | dynamic_friction_ratio,finger_friction | dynamic_friction_ratio=0.925, finger_friction=0.14 |
| C838 | 27e5a6475807ecfe | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.25, table_friction=0.1 |
| C839 | 1e988f3a2b66bfe5 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.325, table_friction=0.17 |
| C840 | 91564f1ae60ca8fd | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.4, table_friction=0.24 |
| C841 | 644cb171183d5e80 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.475, table_friction=0.31 |
| C842 | d1340ea75ddce4d0 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.55, table_friction=0.38 |
| C843 | 6af2f866370b0011 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.625, table_friction=0.45 |
| C844 | a4dc087ba9ff4382 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.7, table_friction=0.52 |
| C845 | cc969db331ba9036 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.775, table_friction=0.59 |
| C846 | 87ae075ef30b5057 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.85, table_friction=0.66 |
| C847 | 95bdcf0f037282db | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.925, table_friction=0.73 |
| C848 | a114612dc4619493 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.25, table_friction=0.8 |
| C849 | a1b81f4d267ed8f9 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.325, table_friction=0.73 |
| C850 | 86237adc8a57b7d4 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.4, table_friction=0.66 |
| C851 | ee05e97bca1af862 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.475, table_friction=0.59 |
| C852 | a44b3b1d54088234 | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.55, table_friction=0.52 |
| C853 | ba0d1190bbd72d2f | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.7, table_friction=0.38 |
| C854 | b176bd4b31d2f64c | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.775, table_friction=0.31 |
| C855 | a47926796f5849eb | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.85, table_friction=0.24 |
| C856 | 0ff8229e019826ee | dynamic_friction_ratio,table_friction | dynamic_friction_ratio=0.925, table_friction=0.17 |
| C857 | 52f25b8e11076903 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.25, size=0.03 |
| C858 | 4153bc0e632cdcc3 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.325, size=0.032 |
| C859 | e832479d940d20f9 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.4, size=0.034 |
| C860 | fdbab7749a0da006 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.475, size=0.036 |
| C861 | 19d1a4af95d3dcec | dynamic_friction_ratio,size | dynamic_friction_ratio=0.55, size=0.038 |
| C862 | 86d8201c8aee027e | dynamic_friction_ratio,size | dynamic_friction_ratio=0.7, size=0.042 |
| C863 | 9c677c094182b2e6 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.775, size=0.044 |
| C864 | f0722e4174ba2c23 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.85, size=0.046 |
| C865 | 154095b6c31016db | dynamic_friction_ratio,size | dynamic_friction_ratio=0.925, size=0.048 |
| C866 | 5d6469dfec9b926a | dynamic_friction_ratio,size | dynamic_friction_ratio=0.25, size=0.05 |
| C867 | d0b46d007d835130 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.325, size=0.048 |
| C868 | c69f5abaa7e59177 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.4, size=0.046 |
| C869 | f2d3092a6fbd149a | dynamic_friction_ratio,size | dynamic_friction_ratio=0.475, size=0.044 |
| C870 | 9572fcc5614bc882 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.55, size=0.042 |
| C871 | bfe4fad7b03390a8 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.7, size=0.038 |
| C872 | f23079b564ebed7a | dynamic_friction_ratio,size | dynamic_friction_ratio=0.775, size=0.036 |
| C873 | 8774392282730a9a | dynamic_friction_ratio,size | dynamic_friction_ratio=0.85, size=0.034 |
| C874 | 582425db8ddfb435 | dynamic_friction_ratio,size | dynamic_friction_ratio=0.925, size=0.032 |
| C875 | c7c06cefb2f06ab9 | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.25, shape=sphere |
| C876 | b59ce971f5b0ff50 | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.325, shape=sphere |
| C877 | 0a79ce14e6f0907c | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.4, shape=sphere |
| C878 | 5e6ff19e156ab70d | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.475, shape=sphere |
| C879 | 46bd38f39fb04674 | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.55, shape=sphere |
| C880 | 7f884b52b0f07361 | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.625, shape=sphere |
| C881 | 8094e60f22814c0c | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.7, shape=sphere |
| C882 | c50c7116c965fb4f | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.775, shape=sphere |
| C883 | b4426470f5d76877 | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.85, shape=sphere |
| C884 | b0382f864e00aaf1 | dynamic_friction_ratio,shape | dynamic_friction_ratio=0.925, shape=sphere |
| C885 | 6ca47410729ffd5b | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.25, com_x=-0.005 |
| C886 | 2de5e2f0247a991b | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.325, com_x=-0.004 |
| C887 | 74305aea5352355d | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.4, com_x=-0.003 |
| C888 | 5c00e56850f99491 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.475, com_x=-0.002 |
| C889 | 9b8dfddba49fdee9 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.55, com_x=-0.001 |
| C890 | 907780c222b7fa8d | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.7, com_x=0.001 |
| C891 | c1d545f55623c0ce | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.775, com_x=0.002 |
| C892 | 970ec043cc6bf008 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.85, com_x=0.003 |
| C893 | d3b909f0da1f64d6 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.925, com_x=0.004 |
| C894 | ce0142f7d9c40fe9 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.25, com_x=0.005 |
| C895 | 3aaa7d5602ef0008 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.325, com_x=0.004 |
| C896 | dae6e6a987dc2e4a | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.4, com_x=0.003 |
| C897 | bf8c99dc1cdd1c84 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.475, com_x=0.002 |
| C898 | 816b9e33892bcea7 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.55, com_x=0.001 |
| C899 | d3c846a28ac19a2b | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.7, com_x=-0.001 |
| C900 | 0a504a4c434b8a1c | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.775, com_x=-0.002 |
| C901 | 48e288cac3ee8ae4 | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.85, com_x=-0.003 |
| C902 | d5b20e3962d341de | dynamic_friction_ratio,com_x | dynamic_friction_ratio=0.925, com_x=-0.004 |
| C903 | 26dbf058121b6587 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.25, com_y=-0.005 |
| C904 | ec7520fe55512447 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.325, com_y=-0.004 |
| C905 | 8a45ceedebf5e3ef | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.4, com_y=-0.003 |
| C906 | 8c657c33e8a6e4c4 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.475, com_y=-0.002 |
| C907 | b8b4577148c9d95c | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.55, com_y=-0.001 |
| C908 | 4ea924cac2f01706 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.7, com_y=0.001 |
| C909 | 502f765687ade4ac | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.775, com_y=0.002 |
| C910 | a2df55a8ee6c2fa4 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.85, com_y=0.003 |
| C911 | 3f5ab117c080eac1 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.925, com_y=0.004 |
| C912 | f310d67bbfc59c94 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.25, com_y=0.005 |
| C913 | 356dc459f65ca7ed | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.325, com_y=0.004 |
| C914 | 013e7e743933a47f | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.4, com_y=0.003 |
| C915 | b9a67438c8a4b26c | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.475, com_y=0.002 |
| C916 | 74188b5756dcfe11 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.55, com_y=0.001 |
| C917 | 6c8b5da267957b68 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.7, com_y=-0.001 |
| C918 | 36e99539071379de | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.775, com_y=-0.002 |
| C919 | 4bdadd9f89089bca | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.85, com_y=-0.003 |
| C920 | 73a14ead69663ee6 | dynamic_friction_ratio,com_y | dynamic_friction_ratio=0.925, com_y=-0.004 |
| C921 | 88728fd52e35107a | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.25, com_z=-0.005 |
| C922 | b56f145b3e051bda | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.325, com_z=-0.004 |
| C923 | 3f49de558236dc5d | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.4, com_z=-0.003 |
| C924 | 34eee4e61c45897e | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.475, com_z=-0.002 |
| C925 | ae0c11af7d1f6982 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.55, com_z=-0.001 |
| C926 | 6aae7f89b3a602ae | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.7, com_z=0.001 |
| C927 | 378d80b420bedd89 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.775, com_z=0.002 |
| C928 | ada7c2641bf4e9c9 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.85, com_z=0.003 |
| C929 | 0f54fa3ff5349ab4 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.925, com_z=0.004 |
| C930 | 004c8c60c58c7d31 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.25, com_z=0.005 |
| C931 | 32eef962340c889d | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.325, com_z=0.004 |
| C932 | e056856061f85c8a | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.4, com_z=0.003 |
| C933 | d363e6f640da13e9 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.475, com_z=0.002 |
| C934 | b8d0db10a1b8272f | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.55, com_z=0.001 |
| C935 | 277285ee90fb20a8 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.7, com_z=-0.001 |
| C936 | 4c10fa1bb79caae3 | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.775, com_z=-0.002 |
| C937 | 1b1a293816fbdb6e | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.85, com_z=-0.003 |
| C938 | f8ed6736139bfb2a | dynamic_friction_ratio,com_z | dynamic_friction_ratio=0.925, com_z=-0.004 |
| C939 | 4febcca83868b03f | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.25, goal_height=0.1 |
| C940 | 8a3a6118dbdea8f3 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.325, goal_height=0.12 |
| C941 | 7b9b234e6be730d3 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.4, goal_height=0.14 |
| C942 | eb66dc9d86fe9054 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.475, goal_height=0.16 |
| C943 | 2cd395a0e1c17094 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.55, goal_height=0.18 |
| C944 | 1f31af70654222ff | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.7, goal_height=0.22 |
| C945 | 49666d05e1bec4e9 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.775, goal_height=0.24 |
| C946 | feca19c54c34d653 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.85, goal_height=0.26 |
| C947 | 4d744c2c86ef4c47 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.925, goal_height=0.28 |
| C948 | 1f04310d67c6334a | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.25, goal_height=0.3 |
| C949 | f5afe8b396e8a631 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.325, goal_height=0.28 |
| C950 | 22dad866361d4320 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.4, goal_height=0.26 |
| C951 | fcf93ae8ba44dcdc | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.475, goal_height=0.24 |
| C952 | 896dbdbefc0400d6 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.55, goal_height=0.22 |
| C953 | 997b078602de9e66 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.7, goal_height=0.18 |
| C954 | b4d05bb9dd9775c9 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.775, goal_height=0.16 |
| C955 | 168fc1b351ce99d6 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.85, goal_height=0.14 |
| C956 | 9ea8ae36fc9163d9 | dynamic_friction_ratio,goal_height | dynamic_friction_ratio=0.925, goal_height=0.12 |
| C957 | f485c05a530da3a1 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.325, restitution=0.05 |
| C958 | 8005f8b16e072de2 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.4, restitution=0.1 |
| C959 | d971f2929ebcfc4d | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.475, restitution=0.15 |
| C960 | 6ecaac38f3f756a4 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.55, restitution=0.2 |
| C961 | bbd9cdf5415837fa | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.625, restitution=0.25 |
| C962 | 2dfd639913029743 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.7, restitution=0.3 |
| C963 | c5683bef09bd0b2f | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.775, restitution=0.35 |
| C964 | 8c668246fcd0124b | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.85, restitution=0.4 |
| C965 | e42fbbb5cdfca9cd | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.925, restitution=0.45 |
| C966 | b8332c137fa78fb2 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.25, restitution=0.5 |
| C967 | bc2faf67393592b4 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.325, restitution=0.45 |
| C968 | 66094dada45572b7 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.4, restitution=0.4 |
| C969 | e3c8d866bf6ddb34 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.475, restitution=0.35 |
| C970 | ba44e94af16250db | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.55, restitution=0.3 |
| C971 | 1a4243e4a2dcf294 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.7, restitution=0.2 |
| C972 | 710cf165c681f687 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.775, restitution=0.15 |
| C973 | d9ba12fba5be5b2b | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.85, restitution=0.1 |
| C974 | 3c10bd522c349b89 | dynamic_friction_ratio,restitution | dynamic_friction_ratio=0.925, restitution=0.05 |
| C975 | 70f2d5016d86df2b | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.325, linear_damping=0.1 |
| C976 | 481f9757f6b0d2ed | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.4, linear_damping=0.2 |
| C977 | 60607e51d757c5f7 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.475, linear_damping=0.3 |
| C978 | 8d821c0c3198742b | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.55, linear_damping=0.4 |
| C979 | c0b1c95d60985688 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.625, linear_damping=0.5 |
| C980 | 27663d715bb89403 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.7, linear_damping=0.6 |
| C981 | 81dfebc64c184065 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.775, linear_damping=0.7 |
| C982 | 443008ad14005d0c | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.85, linear_damping=0.8 |
| C983 | 2416440956c9e028 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.925, linear_damping=0.9 |
| C984 | 3e3b65fa36f6dc10 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.25, linear_damping=1.0 |
| C985 | 25c6469335b73ab8 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.325, linear_damping=0.9 |
| C986 | 87b9a46fad0fdd9c | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.4, linear_damping=0.8 |
| C987 | 04f23fd969509035 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.475, linear_damping=0.7 |
| C988 | b9466219b926a05e | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.55, linear_damping=0.6 |
| C989 | 30b8ea4b86ea108b | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.7, linear_damping=0.4 |
| C990 | dae2f528abddbcc5 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.775, linear_damping=0.3 |
| C991 | a581504b032de0d3 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.85, linear_damping=0.2 |
| C992 | d401b172aad80ae1 | dynamic_friction_ratio,linear_damping | dynamic_friction_ratio=0.925, linear_damping=0.1 |
| C993 | 3e2f9b6408718414 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.25, angular_damping=0.0 |
| C994 | 6e4dc68c08084308 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.4, angular_damping=0.1 |
| C995 | a037bbde23ca6cf2 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.475, angular_damping=0.15 |
| C996 | e70051d9626e355e | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.55, angular_damping=0.2 |
| C997 | 7222d786c55d8a7a | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.625, angular_damping=0.25 |
| C998 | a0c6ceae9b10cf5a | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.7, angular_damping=0.3 |
| C999 | dedd0ef6331c2315 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.775, angular_damping=0.35 |
| C1000 | 3ee31f1d6baa96b6 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.85, angular_damping=0.4 |
| C1001 | 94e162ddd05c8d31 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.925, angular_damping=0.45 |
| C1002 | 4d7d41950134263f | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.25, angular_damping=0.5 |
| C1003 | b3cc88695d26402f | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.325, angular_damping=0.45 |
| C1004 | 61a467b1b0eae2a2 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.4, angular_damping=0.4 |
| C1005 | 1362812ea7ecd58e | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.475, angular_damping=0.35 |
| C1006 | 1dbeb00c13828ad5 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.55, angular_damping=0.3 |
| C1007 | 9cf7dc37667d9474 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.7, angular_damping=0.2 |
| C1008 | 5b8482643f6d308e | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.775, angular_damping=0.15 |
| C1009 | 9256521c5deac0e0 | dynamic_friction_ratio,angular_damping | dynamic_friction_ratio=0.85, angular_damping=0.1 |
| C1010 | 9c7d72c8c2b69f43 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.25, spawn_x=-0.04 |
| C1011 | 21c4c79c25b723f9 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.325, spawn_x=-0.032 |
| C1012 | a0db0cdec43d2c81 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.4, spawn_x=-0.024 |
| C1013 | 260a9987d4ccd07d | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.475, spawn_x=-0.016 |
| C1014 | 13b75360bf47c044 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.55, spawn_x=-0.008 |
| C1015 | 74cbb78a40c439db | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.7, spawn_x=0.008 |
| C1016 | 8311df8164509628 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.775, spawn_x=0.016 |
| C1017 | 2805c6150200d0b4 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.85, spawn_x=0.024 |
| C1018 | da74aae3e13c62c8 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.925, spawn_x=0.032 |
| C1019 | 8be3038776b09f95 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.25, spawn_x=0.04 |
| C1020 | cfb68a0e2e7da3c7 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.325, spawn_x=0.032 |
| C1021 | 2f089389ee60c136 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.4, spawn_x=0.024 |
| C1022 | 34e5971622521f04 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.475, spawn_x=0.016 |
| C1023 | f02b49d529189b2c | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.55, spawn_x=0.008 |
| C1024 | 261897405810e798 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.7, spawn_x=-0.008 |
| C1025 | cc9adba2a2dbb5f0 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.775, spawn_x=-0.016 |
| C1026 | c7f993eab556a57b | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.85, spawn_x=-0.024 |
| C1027 | b287019d5699eb68 | dynamic_friction_ratio,spawn_x | dynamic_friction_ratio=0.925, spawn_x=-0.032 |
| C1028 | ce297ce03655d068 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.25, spawn_y=-0.04 |
| C1029 | a7ce7a709673d099 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.325, spawn_y=-0.032 |
| C1030 | c924e944bb9d1fd5 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.4, spawn_y=-0.024 |
| C1031 | a862788effa2c0e1 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.475, spawn_y=-0.016 |
| C1032 | f02242c2c2c4db83 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.55, spawn_y=-0.008 |
| C1033 | 071c5402e1369787 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.7, spawn_y=0.008 |
| C1034 | 6cff5600d2a21004 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.775, spawn_y=0.016 |
| C1035 | 80212c572ca79a10 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.85, spawn_y=0.024 |
| C1036 | 3916e6c5a4849778 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.925, spawn_y=0.032 |
| C1037 | 3945c54dac5dd883 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.25, spawn_y=0.04 |
| C1038 | 9d36cfe11fbce5a9 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.325, spawn_y=0.032 |
| C1039 | 6a2170a44e28a359 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.4, spawn_y=0.024 |
| C1040 | 73723843ed3a14ad | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.475, spawn_y=0.016 |
| C1041 | b2c0266c1c7360a2 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.55, spawn_y=0.008 |
| C1042 | 852d2b70b3135e4c | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.7, spawn_y=-0.008 |
| C1043 | f255fefbf687ecd6 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.775, spawn_y=-0.016 |
| C1044 | b54a08cebb011fb6 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.85, spawn_y=-0.024 |
| C1045 | bafb7f8a6d34d260 | dynamic_friction_ratio,spawn_y | dynamic_friction_ratio=0.925, spawn_y=-0.032 |
| C1046 | 081e774b17c5b681 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.25, spawn_yaw=-0.523598775598 |
| C1047 | 89852af26bf0a8fd | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.325, spawn_yaw=-0.418879020478 |
| C1048 | 6744ac6c14e44c48 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.4, spawn_yaw=-0.314159265359 |
| C1049 | 7bf55d9933ff39e3 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.475, spawn_yaw=-0.209439510239 |
| C1050 | 449063e71cb821fb | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.55, spawn_yaw=-0.10471975512 |
| C1051 | 17ab8ea091b7033d | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.7, spawn_yaw=0.10471975512 |
| C1052 | 1b33e46f6b0b9c8d | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.775, spawn_yaw=0.209439510239 |
| C1053 | 631f842d37e87133 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.85, spawn_yaw=0.314159265359 |
| C1054 | 06f9932cab2b819b | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.925, spawn_yaw=0.418879020478 |
| C1055 | 99ce16477be16373 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.25, spawn_yaw=0.523598775598 |
| C1056 | f32bac3a5da3dbfe | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.325, spawn_yaw=0.418879020478 |
| C1057 | 8cd987ab0eb9342e | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.4, spawn_yaw=0.314159265359 |
| C1058 | d531d9a7f879ca2d | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.475, spawn_yaw=0.209439510239 |
| C1059 | 407c926fa8ef6d36 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.55, spawn_yaw=0.10471975512 |
| C1060 | ad2b211171e0767f | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.7, spawn_yaw=-0.10471975512 |
| C1061 | 167acf06813fc8e4 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.775, spawn_yaw=-0.209439510239 |
| C1062 | 2567145a2df72095 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.85, spawn_yaw=-0.314159265359 |
| C1063 | 116ba3ac3d8349a9 | dynamic_friction_ratio,spawn_yaw | dynamic_friction_ratio=0.925, spawn_yaw=-0.418879020478 |
| C1064 | 168443f8ce47254a | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.25, inertia_scale=0.5 |
| C1065 | 5fc7268172c4bb28 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.325, inertia_scale=0.65 |
| C1066 | c6ef744f6f033a63 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.4, inertia_scale=0.8 |
| C1067 | 1323d32ac0ce392b | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.475, inertia_scale=0.95 |
| C1068 | 0fc8a9cab06147fb | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.55, inertia_scale=1.1 |
| C1069 | b11ba4a9b21bba6e | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.625, inertia_scale=1.25 |
| C1070 | 1fef1df8b68ac184 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.7, inertia_scale=1.4 |
| C1071 | a226d7f8178be3ce | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.775, inertia_scale=1.55 |
| C1072 | f91c5a9b98747359 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.85, inertia_scale=1.7 |
| C1073 | 6f9deab4da5100ba | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.925, inertia_scale=1.85 |
| C1074 | e659d957265cf2df | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.25, inertia_scale=2.0 |
| C1075 | fae001a58f67a61a | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.325, inertia_scale=1.85 |
| C1076 | 739ca126f811b9fb | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.4, inertia_scale=1.7 |
| C1077 | 73bf8b141fa4e866 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.475, inertia_scale=1.55 |
| C1078 | 2a93bc0171a6064e | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.55, inertia_scale=1.4 |
| C1079 | fe098affa41e772b | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.7, inertia_scale=1.1 |
| C1080 | 13d450feb900bf77 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.775, inertia_scale=0.95 |
| C1081 | ac64a95f73519906 | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.85, inertia_scale=0.8 |
| C1082 | b0f61563b1e19c2b | dynamic_friction_ratio,inertia_scale | dynamic_friction_ratio=0.925, inertia_scale=0.65 |
| C1083 | 1899196bef24fb9b | finger_friction,table_friction | finger_friction=0.1, table_friction=0.1 |
| C1084 | eab46937b1fc3d49 | finger_friction,table_friction | finger_friction=0.14, table_friction=0.17 |
| C1085 | 11679dab11f4890a | finger_friction,table_friction | finger_friction=0.18, table_friction=0.24 |
| C1086 | d2de3e53a6460ff6 | finger_friction,table_friction | finger_friction=0.22, table_friction=0.31 |
| C1087 | 08a39a5739e17fef | finger_friction,table_friction | finger_friction=0.26, table_friction=0.38 |
| C1088 | b19cb8468c76685c | finger_friction,table_friction | finger_friction=0.3, table_friction=0.45 |
| C1089 | bb0155f837b6fcd4 | finger_friction,table_friction | finger_friction=0.34, table_friction=0.52 |
| C1090 | 89ce299ba71d568c | finger_friction,table_friction | finger_friction=0.38, table_friction=0.59 |
| C1091 | e6d3a4da89dc5fa6 | finger_friction,table_friction | finger_friction=0.42, table_friction=0.66 |
| C1092 | 1a75ac3ca93ddd71 | finger_friction,table_friction | finger_friction=0.46, table_friction=0.73 |
| C1093 | 5ad13a575ad8ae58 | finger_friction,table_friction | finger_friction=0.5, table_friction=0.8 |
| C1094 | efceaae860d1a3d1 | finger_friction,table_friction | finger_friction=0.1, table_friction=0.8 |
| C1095 | b591dc30545bbef1 | finger_friction,table_friction | finger_friction=0.14, table_friction=0.73 |
| C1096 | 5bcfc888f6629b27 | finger_friction,table_friction | finger_friction=0.18, table_friction=0.66 |
| C1097 | 11a7a3294edf36e6 | finger_friction,table_friction | finger_friction=0.22, table_friction=0.59 |
| C1098 | ba3dda1060647cfc | finger_friction,table_friction | finger_friction=0.26, table_friction=0.52 |
| C1099 | 319c7bb88688216f | finger_friction,table_friction | finger_friction=0.34, table_friction=0.38 |
| C1100 | 842c3cf9977c913d | finger_friction,table_friction | finger_friction=0.38, table_friction=0.31 |
| C1101 | 76f97821e443ada3 | finger_friction,table_friction | finger_friction=0.42, table_friction=0.24 |
| C1102 | 50b2f08ec7d1a71c | finger_friction,table_friction | finger_friction=0.46, table_friction=0.17 |
| C1103 | f0b1ab29980c9b7a | finger_friction,table_friction | finger_friction=0.5, table_friction=0.1 |
| C1104 | 263f13404a774a57 | finger_friction,size | finger_friction=0.1, size=0.03 |
| C1105 | 8d615ed140577e13 | finger_friction,size | finger_friction=0.14, size=0.032 |
| C1106 | f2af26a920d31e7a | finger_friction,size | finger_friction=0.18, size=0.034 |
| C1107 | 206421cb0247ff4f | finger_friction,size | finger_friction=0.22, size=0.036 |
| C1108 | c1929fabe63e2061 | finger_friction,size | finger_friction=0.26, size=0.038 |
| C1109 | 32b38a161db974c9 | finger_friction,size | finger_friction=0.34, size=0.042 |
| C1110 | 252f12db534e6d2e | finger_friction,size | finger_friction=0.38, size=0.044 |
| C1111 | 3283a28b26dc4fd0 | finger_friction,size | finger_friction=0.42, size=0.046 |
| C1112 | c0c373f1726b3981 | finger_friction,size | finger_friction=0.46, size=0.048 |
| C1113 | 59568809dcc51d9f | finger_friction,size | finger_friction=0.5, size=0.05 |
| C1114 | 0ac0912e4512b03f | finger_friction,size | finger_friction=0.1, size=0.05 |
| C1115 | 9b1a402927fedc72 | finger_friction,size | finger_friction=0.14, size=0.048 |
| C1116 | 17964eb8b1f5c8e6 | finger_friction,size | finger_friction=0.18, size=0.046 |
| C1117 | 9ad6926786e4509a | finger_friction,size | finger_friction=0.22, size=0.044 |
| C1118 | 8c73171f3820f203 | finger_friction,size | finger_friction=0.26, size=0.042 |
| C1119 | 2736cee5c13e36da | finger_friction,size | finger_friction=0.34, size=0.038 |
| C1120 | a805e15e1b991cd5 | finger_friction,size | finger_friction=0.38, size=0.036 |
| C1121 | 242868508495582f | finger_friction,size | finger_friction=0.42, size=0.034 |
| C1122 | 68fdd87d5b528551 | finger_friction,size | finger_friction=0.46, size=0.032 |
| C1123 | 5089583d0ab35f0b | finger_friction,size | finger_friction=0.5, size=0.03 |
| C1124 | b811bddc3c1f1103 | finger_friction,shape | finger_friction=0.1, shape=sphere |
| C1125 | 4f1bfb13028f15ea | finger_friction,shape | finger_friction=0.14, shape=sphere |
| C1126 | 20d7541f73cd05b2 | finger_friction,shape | finger_friction=0.18, shape=sphere |
| C1127 | e48f8a3fb7cfbd6e | finger_friction,shape | finger_friction=0.22, shape=sphere |
| C1128 | 4a772844437d4d81 | finger_friction,shape | finger_friction=0.26, shape=sphere |
| C1129 | 9f1885472a3b3080 | finger_friction,shape | finger_friction=0.3, shape=sphere |
| C1130 | a62123b7f4912623 | finger_friction,shape | finger_friction=0.34, shape=sphere |
| C1131 | 75903b7a366ed4bf | finger_friction,shape | finger_friction=0.38, shape=sphere |
| C1132 | 0f0dc272a6fc2f77 | finger_friction,shape | finger_friction=0.42, shape=sphere |
| C1133 | c5d7860a2b79fdab | finger_friction,shape | finger_friction=0.46, shape=sphere |
| C1134 | 6c0944cdbf437c07 | finger_friction,shape | finger_friction=0.5, shape=sphere |
| C1135 | 5c9da28cb306642e | finger_friction,com_x | finger_friction=0.1, com_x=-0.005 |
| C1136 | aa88418c9120401c | finger_friction,com_x | finger_friction=0.14, com_x=-0.004 |
| C1137 | 77b501edc27c4ec3 | finger_friction,com_x | finger_friction=0.18, com_x=-0.003 |
| C1138 | f868c41344c099c9 | finger_friction,com_x | finger_friction=0.22, com_x=-0.002 |
| C1139 | f30229a1847a5287 | finger_friction,com_x | finger_friction=0.26, com_x=-0.001 |
| C1140 | 62b338cc2fbb5cfb | finger_friction,com_x | finger_friction=0.34, com_x=0.001 |
| C1141 | ae02db375694eb64 | finger_friction,com_x | finger_friction=0.38, com_x=0.002 |
| C1142 | 9e05a530f4a2a7a7 | finger_friction,com_x | finger_friction=0.42, com_x=0.003 |
| C1143 | 27228bed70c9be7d | finger_friction,com_x | finger_friction=0.46, com_x=0.004 |
| C1144 | dbe03e7f64dd67f6 | finger_friction,com_x | finger_friction=0.5, com_x=0.005 |
| C1145 | caf24364ba8bf15c | finger_friction,com_x | finger_friction=0.1, com_x=0.005 |
| C1146 | 862f645ae1cc10b1 | finger_friction,com_x | finger_friction=0.14, com_x=0.004 |
| C1147 | ba1cc0f54c87d51a | finger_friction,com_x | finger_friction=0.18, com_x=0.003 |
| C1148 | a948658056c265cf | finger_friction,com_x | finger_friction=0.22, com_x=0.002 |
| C1149 | a4ecf8f1ec5b2113 | finger_friction,com_x | finger_friction=0.26, com_x=0.001 |
| C1150 | 1007df8a7597ee1a | finger_friction,com_x | finger_friction=0.34, com_x=-0.001 |
| C1151 | f32ea8bd46987d35 | finger_friction,com_x | finger_friction=0.38, com_x=-0.002 |
| C1152 | b5a98ce685b5cad6 | finger_friction,com_x | finger_friction=0.42, com_x=-0.003 |
| C1153 | d5a72d6de91f67b6 | finger_friction,com_x | finger_friction=0.46, com_x=-0.004 |
| C1154 | 0cbb7bb2ee9da900 | finger_friction,com_x | finger_friction=0.5, com_x=-0.005 |
| C1155 | 8903958b73f592b4 | finger_friction,com_y | finger_friction=0.1, com_y=-0.005 |
| C1156 | d3dbdb85652ddaa7 | finger_friction,com_y | finger_friction=0.14, com_y=-0.004 |
| C1157 | 2e42215730a23875 | finger_friction,com_y | finger_friction=0.18, com_y=-0.003 |
| C1158 | 53654da4ef57cf78 | finger_friction,com_y | finger_friction=0.22, com_y=-0.002 |
| C1159 | 21bb4d36c89fe607 | finger_friction,com_y | finger_friction=0.26, com_y=-0.001 |
| C1160 | 2555bef6e3ba9fab | finger_friction,com_y | finger_friction=0.34, com_y=0.001 |
| C1161 | 4c1aeee87f855e49 | finger_friction,com_y | finger_friction=0.38, com_y=0.002 |
| C1162 | a6c5b657165c399b | finger_friction,com_y | finger_friction=0.42, com_y=0.003 |
| C1163 | 0350df9d9bb66ae1 | finger_friction,com_y | finger_friction=0.46, com_y=0.004 |
| C1164 | 7283e610e5da3200 | finger_friction,com_y | finger_friction=0.5, com_y=0.005 |
| C1165 | b96bcb6b9a169c86 | finger_friction,com_y | finger_friction=0.1, com_y=0.005 |
| C1166 | 790ea94562a1d826 | finger_friction,com_y | finger_friction=0.14, com_y=0.004 |
| C1167 | f1d56f33d56163cf | finger_friction,com_y | finger_friction=0.18, com_y=0.003 |
| C1168 | 605d4f61a6d0752a | finger_friction,com_y | finger_friction=0.22, com_y=0.002 |
| C1169 | 0020cfcaeba9278c | finger_friction,com_y | finger_friction=0.26, com_y=0.001 |
| C1170 | f78f4b39baccdf20 | finger_friction,com_y | finger_friction=0.34, com_y=-0.001 |
| C1171 | f8ae3ff8cfb76aaf | finger_friction,com_y | finger_friction=0.38, com_y=-0.002 |
| C1172 | 6f14181159bb4cf9 | finger_friction,com_y | finger_friction=0.42, com_y=-0.003 |
| C1173 | ca3adb9e711a3e13 | finger_friction,com_y | finger_friction=0.46, com_y=-0.004 |
| C1174 | 23130ebd6873f7f8 | finger_friction,com_y | finger_friction=0.5, com_y=-0.005 |
| C1175 | afda4f630f8baf87 | finger_friction,com_z | finger_friction=0.1, com_z=-0.005 |
| C1176 | b78a5d1cb2420436 | finger_friction,com_z | finger_friction=0.14, com_z=-0.004 |
| C1177 | 1a154a635d6ea135 | finger_friction,com_z | finger_friction=0.18, com_z=-0.003 |
| C1178 | 1521cffaab52c2ab | finger_friction,com_z | finger_friction=0.22, com_z=-0.002 |
| C1179 | c2bcf00ef88c66b2 | finger_friction,com_z | finger_friction=0.26, com_z=-0.001 |
| C1180 | b6edc60d614f0c58 | finger_friction,com_z | finger_friction=0.34, com_z=0.001 |
| C1181 | 45747fd2a2016522 | finger_friction,com_z | finger_friction=0.38, com_z=0.002 |
| C1182 | 61761f78ab0b42e6 | finger_friction,com_z | finger_friction=0.42, com_z=0.003 |
| C1183 | 28b1df64755ea20b | finger_friction,com_z | finger_friction=0.46, com_z=0.004 |
| C1184 | 3f6c40be0636461a | finger_friction,com_z | finger_friction=0.5, com_z=0.005 |
| C1185 | 58c16b3d9f0d7a51 | finger_friction,com_z | finger_friction=0.1, com_z=0.005 |
| C1186 | 26a92b757b10a0bf | finger_friction,com_z | finger_friction=0.14, com_z=0.004 |
| C1187 | 00d6775f574bfa54 | finger_friction,com_z | finger_friction=0.18, com_z=0.003 |
| C1188 | b91a94caaa66eb74 | finger_friction,com_z | finger_friction=0.22, com_z=0.002 |
| C1189 | e508c8c0f607bf75 | finger_friction,com_z | finger_friction=0.26, com_z=0.001 |
| C1190 | 7d3b4bfd4f5e8cb4 | finger_friction,com_z | finger_friction=0.34, com_z=-0.001 |
| C1191 | 854c4bc492561f4a | finger_friction,com_z | finger_friction=0.38, com_z=-0.002 |
| C1192 | 1d8c153e9531b38e | finger_friction,com_z | finger_friction=0.42, com_z=-0.003 |
| C1193 | e7eac8a2715169be | finger_friction,com_z | finger_friction=0.46, com_z=-0.004 |
| C1194 | 520ee47fb30b2c82 | finger_friction,com_z | finger_friction=0.5, com_z=-0.005 |
| C1195 | e73897b88ff564aa | finger_friction,goal_height | finger_friction=0.1, goal_height=0.1 |
| C1196 | 5ded650d34c50984 | finger_friction,goal_height | finger_friction=0.14, goal_height=0.12 |
| C1197 | fc98b9730b2ea986 | finger_friction,goal_height | finger_friction=0.18, goal_height=0.14 |
| C1198 | d294be55c097560e | finger_friction,goal_height | finger_friction=0.22, goal_height=0.16 |
| C1199 | 916d5cc799e5d8bb | finger_friction,goal_height | finger_friction=0.26, goal_height=0.18 |
| C1200 | 92c291c7ec7bc467 | finger_friction,goal_height | finger_friction=0.34, goal_height=0.22 |
| C1201 | a72e54fc97b82524 | finger_friction,goal_height | finger_friction=0.38, goal_height=0.24 |
| C1202 | 037ff1e283d1e1de | finger_friction,goal_height | finger_friction=0.42, goal_height=0.26 |
| C1203 | 480e113d0a2ebe4c | finger_friction,goal_height | finger_friction=0.46, goal_height=0.28 |
| C1204 | 1573c734a68fba9e | finger_friction,goal_height | finger_friction=0.5, goal_height=0.3 |
| C1205 | f081a8882f91871d | finger_friction,goal_height | finger_friction=0.1, goal_height=0.3 |
| C1206 | 5d2e4236c0d431cf | finger_friction,goal_height | finger_friction=0.14, goal_height=0.28 |
| C1207 | b2b174b49c0cce3e | finger_friction,goal_height | finger_friction=0.18, goal_height=0.26 |
| C1208 | 0856cbb9a16741f8 | finger_friction,goal_height | finger_friction=0.22, goal_height=0.24 |
| C1209 | c8885f8e0b8457d9 | finger_friction,goal_height | finger_friction=0.26, goal_height=0.22 |
| C1210 | eceac0bf64fca96f | finger_friction,goal_height | finger_friction=0.34, goal_height=0.18 |
| C1211 | 9da11e5e0a568b55 | finger_friction,goal_height | finger_friction=0.38, goal_height=0.16 |
| C1212 | 072ee478cb94a44c | finger_friction,goal_height | finger_friction=0.42, goal_height=0.14 |
| C1213 | 119b4f7d8ec7a9a4 | finger_friction,goal_height | finger_friction=0.46, goal_height=0.12 |
| C1214 | e6cd74d46bcf55a0 | finger_friction,goal_height | finger_friction=0.5, goal_height=0.1 |
| C1215 | 0ff7489b53181ae7 | finger_friction,restitution | finger_friction=0.14, restitution=0.05 |
| C1216 | c8e71feae100f55a | finger_friction,restitution | finger_friction=0.18, restitution=0.1 |
| C1217 | 1cde06f242af5170 | finger_friction,restitution | finger_friction=0.22, restitution=0.15 |
| C1218 | 10e15ae58c20ceff | finger_friction,restitution | finger_friction=0.26, restitution=0.2 |
| C1219 | 89969a8057a86d8c | finger_friction,restitution | finger_friction=0.3, restitution=0.25 |
| C1220 | 7f30fb87a5d7bbf4 | finger_friction,restitution | finger_friction=0.34, restitution=0.3 |
| C1221 | 75f93e8b9589c6d9 | finger_friction,restitution | finger_friction=0.38, restitution=0.35 |
| C1222 | 8578928aef8ca378 | finger_friction,restitution | finger_friction=0.42, restitution=0.4 |
| C1223 | a07ac6efbf8df10d | finger_friction,restitution | finger_friction=0.46, restitution=0.45 |
| C1224 | e5305d47b38880ae | finger_friction,restitution | finger_friction=0.5, restitution=0.5 |
| C1225 | fde0cef6300c8ca7 | finger_friction,restitution | finger_friction=0.1, restitution=0.5 |
| C1226 | 886475f98d84d091 | finger_friction,restitution | finger_friction=0.14, restitution=0.45 |
| C1227 | 340093c85b4713e0 | finger_friction,restitution | finger_friction=0.18, restitution=0.4 |
| C1228 | 32a7ea83f96b8850 | finger_friction,restitution | finger_friction=0.22, restitution=0.35 |
| C1229 | 4087c6afe427f38c | finger_friction,restitution | finger_friction=0.26, restitution=0.3 |
| C1230 | 6819c94fde924343 | finger_friction,restitution | finger_friction=0.34, restitution=0.2 |
| C1231 | 6d7a4009304f98c3 | finger_friction,restitution | finger_friction=0.38, restitution=0.15 |
| C1232 | 2b91b8de3391de99 | finger_friction,restitution | finger_friction=0.42, restitution=0.1 |
| C1233 | 77cf1eae6d05ccc1 | finger_friction,restitution | finger_friction=0.46, restitution=0.05 |
| C1234 | d13078b1c50f776c | finger_friction,linear_damping | finger_friction=0.14, linear_damping=0.1 |
| C1235 | 7aec44fcec2d7293 | finger_friction,linear_damping | finger_friction=0.18, linear_damping=0.2 |
| C1236 | bd564f955b3aca4e | finger_friction,linear_damping | finger_friction=0.22, linear_damping=0.3 |
| C1237 | 180151fa3ec196e2 | finger_friction,linear_damping | finger_friction=0.26, linear_damping=0.4 |
| C1238 | 61b6643ba4df9466 | finger_friction,linear_damping | finger_friction=0.3, linear_damping=0.5 |
| C1239 | 75964f00c82d6bd6 | finger_friction,linear_damping | finger_friction=0.34, linear_damping=0.6 |
| C1240 | dcd13f078f3a1b09 | finger_friction,linear_damping | finger_friction=0.38, linear_damping=0.7 |
| C1241 | 5f640c875e59ab59 | finger_friction,linear_damping | finger_friction=0.42, linear_damping=0.8 |
| C1242 | 82c5a727cdde94cb | finger_friction,linear_damping | finger_friction=0.46, linear_damping=0.9 |
| C1243 | cae8aa17fe1b6079 | finger_friction,linear_damping | finger_friction=0.5, linear_damping=1.0 |
| C1244 | bc75430aef80f8be | finger_friction,linear_damping | finger_friction=0.1, linear_damping=1.0 |
| C1245 | 2d2a73af985c117e | finger_friction,linear_damping | finger_friction=0.14, linear_damping=0.9 |
| C1246 | 224291067b3e8735 | finger_friction,linear_damping | finger_friction=0.18, linear_damping=0.8 |
| C1247 | 52b7e604263de5a3 | finger_friction,linear_damping | finger_friction=0.22, linear_damping=0.7 |
| C1248 | e8cdce328bc06a8e | finger_friction,linear_damping | finger_friction=0.26, linear_damping=0.6 |
| C1249 | c82fec2952b652bf | finger_friction,linear_damping | finger_friction=0.34, linear_damping=0.4 |
| C1250 | 227ce2b705f0dc59 | finger_friction,linear_damping | finger_friction=0.38, linear_damping=0.3 |
| C1251 | 073745aab34a4961 | finger_friction,linear_damping | finger_friction=0.42, linear_damping=0.2 |
| C1252 | b9b4a3c316386568 | finger_friction,linear_damping | finger_friction=0.46, linear_damping=0.1 |
| C1253 | f5bb98589c97b6b5 | finger_friction,angular_damping | finger_friction=0.1, angular_damping=0.0 |
| C1254 | c9b675cf998ae6c5 | finger_friction,angular_damping | finger_friction=0.18, angular_damping=0.1 |
| C1255 | 95b07a6673c3c070 | finger_friction,angular_damping | finger_friction=0.22, angular_damping=0.15 |
| C1256 | 6681bc2b0732eb39 | finger_friction,angular_damping | finger_friction=0.26, angular_damping=0.2 |
| C1257 | 225d6dc5e26097b6 | finger_friction,angular_damping | finger_friction=0.3, angular_damping=0.25 |
| C1258 | d9a67da5939fda49 | finger_friction,angular_damping | finger_friction=0.34, angular_damping=0.3 |
| C1259 | bdc9badb5c5b3e65 | finger_friction,angular_damping | finger_friction=0.38, angular_damping=0.35 |
| C1260 | a58a5b78618440ac | finger_friction,angular_damping | finger_friction=0.42, angular_damping=0.4 |
| C1261 | 0f3811f63758b35d | finger_friction,angular_damping | finger_friction=0.46, angular_damping=0.45 |
| C1262 | 57107118c27fa622 | finger_friction,angular_damping | finger_friction=0.5, angular_damping=0.5 |
| C1263 | cc0e10b4176180d3 | finger_friction,angular_damping | finger_friction=0.1, angular_damping=0.5 |
| C1264 | bfd9b070db0121c3 | finger_friction,angular_damping | finger_friction=0.14, angular_damping=0.45 |
| C1265 | 94591f6a65412e39 | finger_friction,angular_damping | finger_friction=0.18, angular_damping=0.4 |
| C1266 | 3d58c0192968addc | finger_friction,angular_damping | finger_friction=0.22, angular_damping=0.35 |
| C1267 | 82cec87fef44731b | finger_friction,angular_damping | finger_friction=0.26, angular_damping=0.3 |
| C1268 | f67fef1ef2798785 | finger_friction,angular_damping | finger_friction=0.34, angular_damping=0.2 |
| C1269 | c0ecadc6b68f0192 | finger_friction,angular_damping | finger_friction=0.38, angular_damping=0.15 |
| C1270 | 54682417038d7a6d | finger_friction,angular_damping | finger_friction=0.42, angular_damping=0.1 |
| C1271 | b075814f23d05b6b | finger_friction,angular_damping | finger_friction=0.5, angular_damping=0.0 |
| C1272 | ffeccb82c931bb8e | finger_friction,spawn_x | finger_friction=0.1, spawn_x=-0.04 |
| C1273 | 2cfcb74130e47435 | finger_friction,spawn_x | finger_friction=0.14, spawn_x=-0.032 |
| C1274 | 4afb89990e485aa2 | finger_friction,spawn_x | finger_friction=0.18, spawn_x=-0.024 |
| C1275 | b2934a18a517bf20 | finger_friction,spawn_x | finger_friction=0.22, spawn_x=-0.016 |
| C1276 | 78d4800ed4fef521 | finger_friction,spawn_x | finger_friction=0.26, spawn_x=-0.008 |
| C1277 | d4ec004754c70ab4 | finger_friction,spawn_x | finger_friction=0.34, spawn_x=0.008 |
| C1278 | 787322f32b3be6af | finger_friction,spawn_x | finger_friction=0.38, spawn_x=0.016 |
| C1279 | 2fba0ee65237de4d | finger_friction,spawn_x | finger_friction=0.42, spawn_x=0.024 |
| C1280 | 568abf279fd96a59 | finger_friction,spawn_x | finger_friction=0.46, spawn_x=0.032 |
| C1281 | 625072af6ba98ba6 | finger_friction,spawn_x | finger_friction=0.5, spawn_x=0.04 |
| C1282 | d23ca2c61dcd5829 | finger_friction,spawn_x | finger_friction=0.1, spawn_x=0.04 |
| C1283 | 14ce30c0d9b31dcf | finger_friction,spawn_x | finger_friction=0.14, spawn_x=0.032 |
| C1284 | 6aadcf2c20367607 | finger_friction,spawn_x | finger_friction=0.18, spawn_x=0.024 |
| C1285 | a100eb7f1119ab50 | finger_friction,spawn_x | finger_friction=0.22, spawn_x=0.016 |
| C1286 | 4296e511df5dab34 | finger_friction,spawn_x | finger_friction=0.26, spawn_x=0.008 |
| C1287 | f189f740693be3e5 | finger_friction,spawn_x | finger_friction=0.34, spawn_x=-0.008 |
| C1288 | 362d64dd2e68878f | finger_friction,spawn_x | finger_friction=0.38, spawn_x=-0.016 |
| C1289 | 6f74156270640630 | finger_friction,spawn_x | finger_friction=0.42, spawn_x=-0.024 |
| C1290 | 7541ead1491e72d4 | finger_friction,spawn_x | finger_friction=0.46, spawn_x=-0.032 |
| C1291 | 4894a91074f3ec29 | finger_friction,spawn_x | finger_friction=0.5, spawn_x=-0.04 |
| C1292 | b4acb8f066a0f8a9 | finger_friction,spawn_y | finger_friction=0.1, spawn_y=-0.04 |
| C1293 | 2b62d614c8c36c55 | finger_friction,spawn_y | finger_friction=0.14, spawn_y=-0.032 |
| C1294 | b0494e173d7fd93e | finger_friction,spawn_y | finger_friction=0.18, spawn_y=-0.024 |
| C1295 | da73674dc4d220e8 | finger_friction,spawn_y | finger_friction=0.22, spawn_y=-0.016 |
| C1296 | 9dbe7042e1bb9194 | finger_friction,spawn_y | finger_friction=0.26, spawn_y=-0.008 |
| C1297 | 81519c53da2d088d | finger_friction,spawn_y | finger_friction=0.34, spawn_y=0.008 |
| C1298 | d292365342aef6b5 | finger_friction,spawn_y | finger_friction=0.38, spawn_y=0.016 |
| C1299 | bf57e2e66f37e0ca | finger_friction,spawn_y | finger_friction=0.42, spawn_y=0.024 |
| C1300 | e4ade17e4313d8cc | finger_friction,spawn_y | finger_friction=0.46, spawn_y=0.032 |
| C1301 | e0c52d5751494c2b | finger_friction,spawn_y | finger_friction=0.5, spawn_y=0.04 |
| C1302 | 8f213226522d0e2b | finger_friction,spawn_y | finger_friction=0.1, spawn_y=0.04 |
| C1303 | 0f608416b8817651 | finger_friction,spawn_y | finger_friction=0.14, spawn_y=0.032 |
| C1304 | 659850a67a4ad56d | finger_friction,spawn_y | finger_friction=0.18, spawn_y=0.024 |
| C1305 | d078cb994768478c | finger_friction,spawn_y | finger_friction=0.22, spawn_y=0.016 |
| C1306 | 2577c097d99dc04e | finger_friction,spawn_y | finger_friction=0.26, spawn_y=0.008 |
| C1307 | 4f797ae153426ccc | finger_friction,spawn_y | finger_friction=0.34, spawn_y=-0.008 |
| C1308 | 093aa4e0d8651f13 | finger_friction,spawn_y | finger_friction=0.38, spawn_y=-0.016 |
| C1309 | c5890b501cd9196b | finger_friction,spawn_y | finger_friction=0.42, spawn_y=-0.024 |
| C1310 | aaed7f9667138e35 | finger_friction,spawn_y | finger_friction=0.46, spawn_y=-0.032 |
| C1311 | b89dd647f4926c25 | finger_friction,spawn_y | finger_friction=0.5, spawn_y=-0.04 |
| C1312 | 15540351c2fec3a6 | finger_friction,spawn_yaw | finger_friction=0.1, spawn_yaw=-0.523598775598 |
| C1313 | bd838b9e1d6b12f7 | finger_friction,spawn_yaw | finger_friction=0.14, spawn_yaw=-0.418879020478 |
| C1314 | 39126dc5c987af74 | finger_friction,spawn_yaw | finger_friction=0.18, spawn_yaw=-0.314159265359 |
| C1315 | b459a2b8c6818069 | finger_friction,spawn_yaw | finger_friction=0.22, spawn_yaw=-0.209439510239 |
| C1316 | 26286b64c2935a2e | finger_friction,spawn_yaw | finger_friction=0.26, spawn_yaw=-0.10471975512 |
| C1317 | 6a92bdd06902be73 | finger_friction,spawn_yaw | finger_friction=0.34, spawn_yaw=0.10471975512 |
| C1318 | a28681c04b98a429 | finger_friction,spawn_yaw | finger_friction=0.38, spawn_yaw=0.209439510239 |
| C1319 | 14f207f27f9dcd8f | finger_friction,spawn_yaw | finger_friction=0.42, spawn_yaw=0.314159265359 |
| C1320 | b036af542a69dd60 | finger_friction,spawn_yaw | finger_friction=0.46, spawn_yaw=0.418879020478 |
| C1321 | c51c5995c7fd298d | finger_friction,spawn_yaw | finger_friction=0.5, spawn_yaw=0.523598775598 |
| C1322 | bd35f787f74adf6a | finger_friction,spawn_yaw | finger_friction=0.1, spawn_yaw=0.523598775598 |
| C1323 | 164290811d33b169 | finger_friction,spawn_yaw | finger_friction=0.14, spawn_yaw=0.418879020478 |
| C1324 | 090f74e19387e4af | finger_friction,spawn_yaw | finger_friction=0.18, spawn_yaw=0.314159265359 |
| C1325 | bae026b7614a2cce | finger_friction,spawn_yaw | finger_friction=0.22, spawn_yaw=0.209439510239 |
| C1326 | cbbf0096a6072a05 | finger_friction,spawn_yaw | finger_friction=0.26, spawn_yaw=0.10471975512 |
| C1327 | 84278b69a87e1432 | finger_friction,spawn_yaw | finger_friction=0.34, spawn_yaw=-0.10471975512 |
| C1328 | fd232a512425c70b | finger_friction,spawn_yaw | finger_friction=0.38, spawn_yaw=-0.209439510239 |
| C1329 | b47cc424ff770f66 | finger_friction,spawn_yaw | finger_friction=0.42, spawn_yaw=-0.314159265359 |
| C1330 | 95ef119a399f1502 | finger_friction,spawn_yaw | finger_friction=0.46, spawn_yaw=-0.418879020478 |
| C1331 | f90456f59880cefe | finger_friction,spawn_yaw | finger_friction=0.5, spawn_yaw=-0.523598775598 |
| C1332 | fdcd0aa8ac4476b2 | finger_friction,inertia_scale | finger_friction=0.1, inertia_scale=0.5 |
| C1333 | 17b4767f81ec42d6 | finger_friction,inertia_scale | finger_friction=0.14, inertia_scale=0.65 |
| C1334 | bf6f904a07fa6774 | finger_friction,inertia_scale | finger_friction=0.18, inertia_scale=0.8 |
| C1335 | 668ccc75ea2e7b48 | finger_friction,inertia_scale | finger_friction=0.22, inertia_scale=0.95 |
| C1336 | 72629dbb32ee1cd1 | finger_friction,inertia_scale | finger_friction=0.26, inertia_scale=1.1 |
| C1337 | 8a39e111a5a0a94b | finger_friction,inertia_scale | finger_friction=0.3, inertia_scale=1.25 |
| C1338 | 403ed308f97fc02d | finger_friction,inertia_scale | finger_friction=0.34, inertia_scale=1.4 |
| C1339 | 7005ca6e58e07116 | finger_friction,inertia_scale | finger_friction=0.38, inertia_scale=1.55 |
| C1340 | 76135110c1da7cc9 | finger_friction,inertia_scale | finger_friction=0.42, inertia_scale=1.7 |
| C1341 | 598b3137ad1cb751 | finger_friction,inertia_scale | finger_friction=0.46, inertia_scale=1.85 |
| C1342 | 66dde23e3085250b | finger_friction,inertia_scale | finger_friction=0.5, inertia_scale=2.0 |
| C1343 | b036f69db5d410a3 | finger_friction,inertia_scale | finger_friction=0.1, inertia_scale=2.0 |
| C1344 | 30f06bf7d1dd8829 | finger_friction,inertia_scale | finger_friction=0.14, inertia_scale=1.85 |
| C1345 | 574ec8efdff4684e | finger_friction,inertia_scale | finger_friction=0.18, inertia_scale=1.7 |
| C1346 | 28fc926903df8c5a | finger_friction,inertia_scale | finger_friction=0.22, inertia_scale=1.55 |
| C1347 | 561e98e9247aee5f | finger_friction,inertia_scale | finger_friction=0.26, inertia_scale=1.4 |
| C1348 | 586bf0b7f731b386 | finger_friction,inertia_scale | finger_friction=0.34, inertia_scale=1.1 |
| C1349 | de145f45f7fe30c3 | finger_friction,inertia_scale | finger_friction=0.38, inertia_scale=0.95 |
| C1350 | 1ed1e92268b83895 | finger_friction,inertia_scale | finger_friction=0.42, inertia_scale=0.8 |
| C1351 | 6d560d1158b791b7 | finger_friction,inertia_scale | finger_friction=0.46, inertia_scale=0.65 |
| C1352 | 8b6fc5f030f1ee10 | finger_friction,inertia_scale | finger_friction=0.5, inertia_scale=0.5 |
| C1353 | c8fe229560dc922c | table_friction,size | table_friction=0.1, size=0.03 |
| C1354 | dd2a64ccbbb88e2a | table_friction,size | table_friction=0.17, size=0.032 |
| C1355 | 36aa4c5406e35819 | table_friction,size | table_friction=0.24, size=0.034 |
| C1356 | 015ad83f5e978d79 | table_friction,size | table_friction=0.31, size=0.036 |
| C1357 | 7074ee866cc9fb88 | table_friction,size | table_friction=0.38, size=0.038 |
| C1358 | f9242d01734923ff | table_friction,size | table_friction=0.52, size=0.042 |
| C1359 | b35aed5025f5d1b6 | table_friction,size | table_friction=0.59, size=0.044 |
| C1360 | b982c30e896ebcb2 | table_friction,size | table_friction=0.66, size=0.046 |
| C1361 | f844f7444432a45b | table_friction,size | table_friction=0.73, size=0.048 |
| C1362 | 4b31fecb707ff366 | table_friction,size | table_friction=0.8, size=0.05 |
| C1363 | aa4d02f0e91bbf09 | table_friction,size | table_friction=0.1, size=0.05 |
| C1364 | 2d53dafbd0a762b2 | table_friction,size | table_friction=0.17, size=0.048 |
| C1365 | 4f0c4f621cd8f0ad | table_friction,size | table_friction=0.24, size=0.046 |
| C1366 | e839e42e5bc61205 | table_friction,size | table_friction=0.31, size=0.044 |
| C1367 | 60873087492a4622 | table_friction,size | table_friction=0.38, size=0.042 |
| C1368 | 4e25e96c68e30828 | table_friction,size | table_friction=0.52, size=0.038 |
| C1369 | f6ecea869a377625 | table_friction,size | table_friction=0.59, size=0.036 |
| C1370 | 607f4f4cff2e1af5 | table_friction,size | table_friction=0.66, size=0.034 |
| C1371 | fc60ade93c4259bd | table_friction,size | table_friction=0.73, size=0.032 |
| C1372 | 5d37cc22f6a0d27a | table_friction,size | table_friction=0.8, size=0.03 |
| C1373 | 49ee481699dd74fa | table_friction,shape | table_friction=0.1, shape=sphere |
| C1374 | 7d7926ace42fdda8 | table_friction,shape | table_friction=0.17, shape=sphere |
| C1375 | 7cae1cf44dac40d1 | table_friction,shape | table_friction=0.24, shape=sphere |
| C1376 | 46e9d2965b575f58 | table_friction,shape | table_friction=0.31, shape=sphere |
| C1377 | 281e3a20a7ea0813 | table_friction,shape | table_friction=0.38, shape=sphere |
| C1378 | 804e439318c496ba | table_friction,shape | table_friction=0.45, shape=sphere |
| C1379 | d6975ed7583ec6c0 | table_friction,shape | table_friction=0.52, shape=sphere |
| C1380 | 89aae9d3988739f6 | table_friction,shape | table_friction=0.59, shape=sphere |
| C1381 | 247d38dd2e699866 | table_friction,shape | table_friction=0.66, shape=sphere |
| C1382 | 5837b7f06a2714d9 | table_friction,shape | table_friction=0.73, shape=sphere |
| C1383 | 0cd7b9a2c982e933 | table_friction,shape | table_friction=0.8, shape=sphere |
| C1384 | 57f2591f738536a5 | table_friction,com_x | table_friction=0.1, com_x=-0.005 |
| C1385 | ce4d7486b67dd574 | table_friction,com_x | table_friction=0.17, com_x=-0.004 |
| C1386 | 9fd61d5d9f2a54c9 | table_friction,com_x | table_friction=0.24, com_x=-0.003 |
| C1387 | 4869d4da3253ac79 | table_friction,com_x | table_friction=0.31, com_x=-0.002 |
| C1388 | 13c57f4cfa12e010 | table_friction,com_x | table_friction=0.38, com_x=-0.001 |
| C1389 | be103f66420d4b4b | table_friction,com_x | table_friction=0.52, com_x=0.001 |
| C1390 | b9eb306862d42c6e | table_friction,com_x | table_friction=0.59, com_x=0.002 |
| C1391 | 6f41ad46c67b8d2d | table_friction,com_x | table_friction=0.66, com_x=0.003 |
| C1392 | 54cbae9394d20ac5 | table_friction,com_x | table_friction=0.73, com_x=0.004 |
| C1393 | e23c2e8cd3d09629 | table_friction,com_x | table_friction=0.8, com_x=0.005 |
| C1394 | 97fc33bc16250217 | table_friction,com_x | table_friction=0.1, com_x=0.005 |
| C1395 | 3cd55e48e4018fd8 | table_friction,com_x | table_friction=0.17, com_x=0.004 |
| C1396 | 2c0a9900f7709c56 | table_friction,com_x | table_friction=0.24, com_x=0.003 |
| C1397 | f2152ac61b1f0166 | table_friction,com_x | table_friction=0.31, com_x=0.002 |
| C1398 | b7dae32c01ecc0d2 | table_friction,com_x | table_friction=0.38, com_x=0.001 |
| C1399 | 531738433c20dcc6 | table_friction,com_x | table_friction=0.52, com_x=-0.001 |
| C1400 | 38501ea6b5bfce43 | table_friction,com_x | table_friction=0.59, com_x=-0.002 |
| C1401 | c4d88d1ae9a0d294 | table_friction,com_x | table_friction=0.66, com_x=-0.003 |
| C1402 | 9223adcae60586d2 | table_friction,com_x | table_friction=0.73, com_x=-0.004 |
| C1403 | 3cf20d39f5edc878 | table_friction,com_x | table_friction=0.8, com_x=-0.005 |
| C1404 | aded73e1fabbd062 | table_friction,com_y | table_friction=0.1, com_y=-0.005 |
| C1405 | e27c663842030c16 | table_friction,com_y | table_friction=0.17, com_y=-0.004 |
| C1406 | 7f46fee2807cb465 | table_friction,com_y | table_friction=0.24, com_y=-0.003 |
| C1407 | e67a6a118cfcbdfe | table_friction,com_y | table_friction=0.31, com_y=-0.002 |
| C1408 | 45f4bbb69c38436d | table_friction,com_y | table_friction=0.38, com_y=-0.001 |
| C1409 | d9b7b0d83c0e3061 | table_friction,com_y | table_friction=0.52, com_y=0.001 |
| C1410 | 20db7ba3aacfa239 | table_friction,com_y | table_friction=0.59, com_y=0.002 |
| C1411 | db05f758ec4cc33c | table_friction,com_y | table_friction=0.66, com_y=0.003 |
| C1412 | 6f1835520acf2fb0 | table_friction,com_y | table_friction=0.73, com_y=0.004 |
| C1413 | 66dc885db66efbc2 | table_friction,com_y | table_friction=0.8, com_y=0.005 |
| C1414 | 38580b6de309a4f1 | table_friction,com_y | table_friction=0.1, com_y=0.005 |
| C1415 | 278f6e43909251fd | table_friction,com_y | table_friction=0.17, com_y=0.004 |
| C1416 | d90d7c46fc3424ef | table_friction,com_y | table_friction=0.24, com_y=0.003 |
| C1417 | 10bc0e62ba7dff34 | table_friction,com_y | table_friction=0.31, com_y=0.002 |
| C1418 | 74663c86bf3b0fba | table_friction,com_y | table_friction=0.38, com_y=0.001 |
| C1419 | ac6f81b635718807 | table_friction,com_y | table_friction=0.52, com_y=-0.001 |
| C1420 | 1925683f125d1c30 | table_friction,com_y | table_friction=0.59, com_y=-0.002 |
| C1421 | 5fd3e6e5fa9c3c0f | table_friction,com_y | table_friction=0.66, com_y=-0.003 |
| C1422 | 5b8cb4ca652e8058 | table_friction,com_y | table_friction=0.73, com_y=-0.004 |
| C1423 | b9140a607c381ec0 | table_friction,com_y | table_friction=0.8, com_y=-0.005 |
| C1424 | 66df91258cea1ac4 | table_friction,com_z | table_friction=0.1, com_z=-0.005 |
| C1425 | a8a503132c6a7495 | table_friction,com_z | table_friction=0.17, com_z=-0.004 |
| C1426 | 05715c567b78676a | table_friction,com_z | table_friction=0.24, com_z=-0.003 |
| C1427 | 79147bb4580cf575 | table_friction,com_z | table_friction=0.31, com_z=-0.002 |
| C1428 | 15a16c8b5cbbafd8 | table_friction,com_z | table_friction=0.38, com_z=-0.001 |
| C1429 | 0f003087826d95c9 | table_friction,com_z | table_friction=0.52, com_z=0.001 |
| C1430 | a0438c7d98072604 | table_friction,com_z | table_friction=0.59, com_z=0.002 |
| C1431 | 5d3d51bcc1d046cd | table_friction,com_z | table_friction=0.66, com_z=0.003 |
| C1432 | cbad25668f25e4bd | table_friction,com_z | table_friction=0.73, com_z=0.004 |
| C1433 | f40cb3a1f2b9a110 | table_friction,com_z | table_friction=0.8, com_z=0.005 |
| C1434 | 8dfac778e02f9355 | table_friction,com_z | table_friction=0.1, com_z=0.005 |
| C1435 | 73d71e614a6056fd | table_friction,com_z | table_friction=0.17, com_z=0.004 |
| C1436 | 33f95c8b9c567e98 | table_friction,com_z | table_friction=0.24, com_z=0.003 |
| C1437 | 56b4f610fd399cf3 | table_friction,com_z | table_friction=0.31, com_z=0.002 |
| C1438 | 51fc44383eaaf2c2 | table_friction,com_z | table_friction=0.38, com_z=0.001 |
| C1439 | 28e543370f1cabe1 | table_friction,com_z | table_friction=0.52, com_z=-0.001 |
| C1440 | ad1deb80b78ee4df | table_friction,com_z | table_friction=0.59, com_z=-0.002 |
| C1441 | 669db9c406bca11b | table_friction,com_z | table_friction=0.66, com_z=-0.003 |
| C1442 | 90153f5af172b09f | table_friction,com_z | table_friction=0.73, com_z=-0.004 |
| C1443 | 089d2e12e09c48d9 | table_friction,com_z | table_friction=0.8, com_z=-0.005 |
| C1444 | f36fb55936f98586 | table_friction,goal_height | table_friction=0.1, goal_height=0.1 |
| C1445 | 49343115e4b821f4 | table_friction,goal_height | table_friction=0.17, goal_height=0.12 |
| C1446 | bc0d20449fc4a93c | table_friction,goal_height | table_friction=0.24, goal_height=0.14 |
| C1447 | 78eb726eb5698314 | table_friction,goal_height | table_friction=0.31, goal_height=0.16 |
| C1448 | 7edc52b65f925a4c | table_friction,goal_height | table_friction=0.38, goal_height=0.18 |
| C1449 | 9616eb391cb139dd | table_friction,goal_height | table_friction=0.52, goal_height=0.22 |
| C1450 | e587aeb15e05384e | table_friction,goal_height | table_friction=0.59, goal_height=0.24 |
| C1451 | b2e6bcd316cb4c4f | table_friction,goal_height | table_friction=0.66, goal_height=0.26 |
| C1452 | 1793eee58a7d73cb | table_friction,goal_height | table_friction=0.73, goal_height=0.28 |
| C1453 | e74d7254932a66e0 | table_friction,goal_height | table_friction=0.8, goal_height=0.3 |
| C1454 | ca0f0dd9022af4ef | table_friction,goal_height | table_friction=0.1, goal_height=0.3 |
| C1455 | 1ca5576782fb1284 | table_friction,goal_height | table_friction=0.17, goal_height=0.28 |
| C1456 | 8719c998d7dc137b | table_friction,goal_height | table_friction=0.24, goal_height=0.26 |
| C1457 | 1fb3c56e41990442 | table_friction,goal_height | table_friction=0.31, goal_height=0.24 |
| C1458 | bd805b48ee09f93a | table_friction,goal_height | table_friction=0.38, goal_height=0.22 |
| C1459 | f7add7e3e07f45bd | table_friction,goal_height | table_friction=0.52, goal_height=0.18 |
| C1460 | 37926257927b0588 | table_friction,goal_height | table_friction=0.59, goal_height=0.16 |
| C1461 | f0276b41ff6cdc23 | table_friction,goal_height | table_friction=0.66, goal_height=0.14 |
| C1462 | 18acfbb0573af615 | table_friction,goal_height | table_friction=0.73, goal_height=0.12 |
| C1463 | 9006adfcf7c11928 | table_friction,goal_height | table_friction=0.8, goal_height=0.1 |
| C1464 | cf3e9f8735fb6f4c | table_friction,restitution | table_friction=0.17, restitution=0.05 |
| C1465 | dd6a7594ec85ac45 | table_friction,restitution | table_friction=0.24, restitution=0.1 |
| C1466 | c60b510743414067 | table_friction,restitution | table_friction=0.31, restitution=0.15 |
| C1467 | b87d28d433a175bc | table_friction,restitution | table_friction=0.38, restitution=0.2 |
| C1468 | beb86e6703a821a1 | table_friction,restitution | table_friction=0.45, restitution=0.25 |
| C1469 | d4447e3e77885910 | table_friction,restitution | table_friction=0.52, restitution=0.3 |
| C1470 | c5a6e99c1ce9822e | table_friction,restitution | table_friction=0.59, restitution=0.35 |
| C1471 | c754948f20a3b9db | table_friction,restitution | table_friction=0.66, restitution=0.4 |
| C1472 | e688d2086563806f | table_friction,restitution | table_friction=0.73, restitution=0.45 |
| C1473 | 40a2a6f772f0863d | table_friction,restitution | table_friction=0.8, restitution=0.5 |
| C1474 | ec2f6b321685737c | table_friction,restitution | table_friction=0.1, restitution=0.5 |
| C1475 | 0551a9dd40cae870 | table_friction,restitution | table_friction=0.17, restitution=0.45 |
| C1476 | c052d76b2a5e5091 | table_friction,restitution | table_friction=0.24, restitution=0.4 |
| C1477 | fdd57bcf24f8cd3e | table_friction,restitution | table_friction=0.31, restitution=0.35 |
| C1478 | 2515fc931d41b8ae | table_friction,restitution | table_friction=0.38, restitution=0.3 |
| C1479 | de8142e8a9360f30 | table_friction,restitution | table_friction=0.52, restitution=0.2 |
| C1480 | 078dc14f009feaa5 | table_friction,restitution | table_friction=0.59, restitution=0.15 |
| C1481 | fbfd284591ca73da | table_friction,restitution | table_friction=0.66, restitution=0.1 |
| C1482 | f20d749ef1a65622 | table_friction,restitution | table_friction=0.73, restitution=0.05 |
| C1483 | 1716602805345f4c | table_friction,linear_damping | table_friction=0.17, linear_damping=0.1 |
| C1484 | 5ae945b4ee2cec43 | table_friction,linear_damping | table_friction=0.24, linear_damping=0.2 |
| C1485 | 1f14e1ef77337ca9 | table_friction,linear_damping | table_friction=0.31, linear_damping=0.3 |
| C1486 | cf19f60575c61031 | table_friction,linear_damping | table_friction=0.38, linear_damping=0.4 |
| C1487 | 5d27814f79b20433 | table_friction,linear_damping | table_friction=0.45, linear_damping=0.5 |
| C1488 | 93fee95c221cf37f | table_friction,linear_damping | table_friction=0.52, linear_damping=0.6 |
| C1489 | 0eb2698b643c9a22 | table_friction,linear_damping | table_friction=0.59, linear_damping=0.7 |
| C1490 | b4a61c24c1b195b0 | table_friction,linear_damping | table_friction=0.66, linear_damping=0.8 |
| C1491 | 05e7f289ea4550b8 | table_friction,linear_damping | table_friction=0.73, linear_damping=0.9 |
| C1492 | 36f4e89c61758faa | table_friction,linear_damping | table_friction=0.8, linear_damping=1.0 |
| C1493 | 4b15239309fe4d52 | table_friction,linear_damping | table_friction=0.1, linear_damping=1.0 |
| C1494 | c15b742ce30f4b7b | table_friction,linear_damping | table_friction=0.17, linear_damping=0.9 |
| C1495 | ff45fe71821ae188 | table_friction,linear_damping | table_friction=0.24, linear_damping=0.8 |
| C1496 | 4126dc423a349857 | table_friction,linear_damping | table_friction=0.31, linear_damping=0.7 |
| C1497 | b534d5e2b41ddb29 | table_friction,linear_damping | table_friction=0.38, linear_damping=0.6 |
| C1498 | ae044f77ad89555f | table_friction,linear_damping | table_friction=0.52, linear_damping=0.4 |
| C1499 | 0dcf05b028a00d36 | table_friction,linear_damping | table_friction=0.59, linear_damping=0.3 |
| C1500 | 0eba64575c6f4e38 | table_friction,linear_damping | table_friction=0.66, linear_damping=0.2 |
| C1501 | aab82b1074721e65 | table_friction,linear_damping | table_friction=0.73, linear_damping=0.1 |
| C1502 | cda8b3bbf15b844d | table_friction,angular_damping | table_friction=0.1, angular_damping=0.0 |
| C1503 | 94928ccf7d20eb04 | table_friction,angular_damping | table_friction=0.24, angular_damping=0.1 |
| C1504 | 9197f08fb57bd056 | table_friction,angular_damping | table_friction=0.31, angular_damping=0.15 |
| C1505 | ec7aff60edc3b305 | table_friction,angular_damping | table_friction=0.38, angular_damping=0.2 |
| C1506 | 978c3902d8feaa76 | table_friction,angular_damping | table_friction=0.45, angular_damping=0.25 |
| C1507 | 2befd86a3852e589 | table_friction,angular_damping | table_friction=0.52, angular_damping=0.3 |
| C1508 | 4c43ce4c330a5f5f | table_friction,angular_damping | table_friction=0.59, angular_damping=0.35 |
| C1509 | cdce0c2961176c4e | table_friction,angular_damping | table_friction=0.66, angular_damping=0.4 |
| C1510 | 621624228916394f | table_friction,angular_damping | table_friction=0.73, angular_damping=0.45 |
| C1511 | 26249eb48f7d2d41 | table_friction,angular_damping | table_friction=0.8, angular_damping=0.5 |
| C1512 | 982a9e308d7fe96e | table_friction,angular_damping | table_friction=0.1, angular_damping=0.5 |
| C1513 | 106fe46bb8663ec2 | table_friction,angular_damping | table_friction=0.17, angular_damping=0.45 |
| C1514 | ffccd2f48a3743e5 | table_friction,angular_damping | table_friction=0.24, angular_damping=0.4 |
| C1515 | 50f0e7904da692c5 | table_friction,angular_damping | table_friction=0.31, angular_damping=0.35 |
| C1516 | e8d46d2383b68147 | table_friction,angular_damping | table_friction=0.38, angular_damping=0.3 |
| C1517 | 4b45dd20421d5c84 | table_friction,angular_damping | table_friction=0.52, angular_damping=0.2 |
| C1518 | c3d3d9186f10eaef | table_friction,angular_damping | table_friction=0.59, angular_damping=0.15 |
| C1519 | 74606c913d27af04 | table_friction,angular_damping | table_friction=0.66, angular_damping=0.1 |
| C1520 | 07f08558d14044c5 | table_friction,angular_damping | table_friction=0.8, angular_damping=0.0 |
| C1521 | 07fc7e87cb30fe4d | table_friction,spawn_x | table_friction=0.1, spawn_x=-0.04 |
| C1522 | d5e309ad32936c22 | table_friction,spawn_x | table_friction=0.17, spawn_x=-0.032 |
| C1523 | 572c9d18eecd6351 | table_friction,spawn_x | table_friction=0.24, spawn_x=-0.024 |
| C1524 | 64c8099d11f793cb | table_friction,spawn_x | table_friction=0.31, spawn_x=-0.016 |
| C1525 | 552ec1c188592100 | table_friction,spawn_x | table_friction=0.38, spawn_x=-0.008 |
| C1526 | cd5b907e50acab0d | table_friction,spawn_x | table_friction=0.52, spawn_x=0.008 |
| C1527 | 374545c1e84b8861 | table_friction,spawn_x | table_friction=0.59, spawn_x=0.016 |
| C1528 | 6957b5b1ddb9c0ba | table_friction,spawn_x | table_friction=0.66, spawn_x=0.024 |
| C1529 | 3951ffa148e39b7f | table_friction,spawn_x | table_friction=0.73, spawn_x=0.032 |
| C1530 | 2761482278095544 | table_friction,spawn_x | table_friction=0.8, spawn_x=0.04 |
| C1531 | 0676b5f0a2544a1d | table_friction,spawn_x | table_friction=0.1, spawn_x=0.04 |
| C1532 | bebc24d287d00823 | table_friction,spawn_x | table_friction=0.17, spawn_x=0.032 |
| C1533 | d16fa61e974c84b0 | table_friction,spawn_x | table_friction=0.24, spawn_x=0.024 |
| C1534 | a300625755913703 | table_friction,spawn_x | table_friction=0.31, spawn_x=0.016 |
| C1535 | dd2b2c0c33860c44 | table_friction,spawn_x | table_friction=0.38, spawn_x=0.008 |
| C1536 | 107d683d48f9a228 | table_friction,spawn_x | table_friction=0.52, spawn_x=-0.008 |
| C1537 | 3dd5e0d0dc39b85d | table_friction,spawn_x | table_friction=0.59, spawn_x=-0.016 |
| C1538 | 590a65f1288fa71a | table_friction,spawn_x | table_friction=0.66, spawn_x=-0.024 |
| C1539 | b1fb7eb4eac7385b | table_friction,spawn_x | table_friction=0.73, spawn_x=-0.032 |
| C1540 | adecaba7b4a8fdf6 | table_friction,spawn_x | table_friction=0.8, spawn_x=-0.04 |
| C1541 | 722e98dabf5291de | table_friction,spawn_y | table_friction=0.1, spawn_y=-0.04 |
| C1542 | 6e040d1c6e795cb5 | table_friction,spawn_y | table_friction=0.17, spawn_y=-0.032 |
| C1543 | 72e5699db020acc0 | table_friction,spawn_y | table_friction=0.24, spawn_y=-0.024 |
| C1544 | d6931b4e6ee424be | table_friction,spawn_y | table_friction=0.31, spawn_y=-0.016 |
| C1545 | 95bc711f6c272556 | table_friction,spawn_y | table_friction=0.38, spawn_y=-0.008 |
| C1546 | 24b8e19164579639 | table_friction,spawn_y | table_friction=0.52, spawn_y=0.008 |
| C1547 | 13f3f88850d66a84 | table_friction,spawn_y | table_friction=0.59, spawn_y=0.016 |
| C1548 | 641e3e7ae8ba9ddb | table_friction,spawn_y | table_friction=0.66, spawn_y=0.024 |
| C1549 | 05b52d1d5034d4ab | table_friction,spawn_y | table_friction=0.73, spawn_y=0.032 |
| C1550 | fe0b913b6ee7c651 | table_friction,spawn_y | table_friction=0.8, spawn_y=0.04 |
| C1551 | a32bd7d15a9e5384 | table_friction,spawn_y | table_friction=0.1, spawn_y=0.04 |
| C1552 | 8876d21bfcc2a305 | table_friction,spawn_y | table_friction=0.17, spawn_y=0.032 |
| C1553 | d3a04fe0f50090b0 | table_friction,spawn_y | table_friction=0.24, spawn_y=0.024 |
| C1554 | 5c550239df675864 | table_friction,spawn_y | table_friction=0.31, spawn_y=0.016 |
| C1555 | 8dc4f475db97df65 | table_friction,spawn_y | table_friction=0.38, spawn_y=0.008 |
| C1556 | 0d1d9a77dc17df4d | table_friction,spawn_y | table_friction=0.52, spawn_y=-0.008 |
| C1557 | 711b5153db02d701 | table_friction,spawn_y | table_friction=0.59, spawn_y=-0.016 |
| C1558 | c4f961f36bb4c4d6 | table_friction,spawn_y | table_friction=0.66, spawn_y=-0.024 |
| C1559 | 9fc3cc94e88a8ac2 | table_friction,spawn_y | table_friction=0.73, spawn_y=-0.032 |
| C1560 | 1b7469594a1d8f02 | table_friction,spawn_y | table_friction=0.8, spawn_y=-0.04 |
| C1561 | 4360b71400a360eb | table_friction,spawn_yaw | table_friction=0.1, spawn_yaw=-0.523598775598 |
| C1562 | 076e08c63fdf7db5 | table_friction,spawn_yaw | table_friction=0.17, spawn_yaw=-0.418879020478 |
| C1563 | d04155506400d325 | table_friction,spawn_yaw | table_friction=0.24, spawn_yaw=-0.314159265359 |
| C1564 | 32d3be47604e04b4 | table_friction,spawn_yaw | table_friction=0.31, spawn_yaw=-0.209439510239 |
| C1565 | 080a238b7a879005 | table_friction,spawn_yaw | table_friction=0.38, spawn_yaw=-0.10471975512 |
| C1566 | 209a4dea79a7c5b0 | table_friction,spawn_yaw | table_friction=0.52, spawn_yaw=0.10471975512 |
| C1567 | a9dc574dd7bd9b1d | table_friction,spawn_yaw | table_friction=0.59, spawn_yaw=0.209439510239 |
| C1568 | 03a73621d0ae09d0 | table_friction,spawn_yaw | table_friction=0.66, spawn_yaw=0.314159265359 |
| C1569 | 591e1fcfbd670f04 | table_friction,spawn_yaw | table_friction=0.73, spawn_yaw=0.418879020478 |
| C1570 | d432c1f37b3a0e32 | table_friction,spawn_yaw | table_friction=0.8, spawn_yaw=0.523598775598 |
| C1571 | fa6a82e82880124a | table_friction,spawn_yaw | table_friction=0.1, spawn_yaw=0.523598775598 |
| C1572 | de616963e92e4579 | table_friction,spawn_yaw | table_friction=0.17, spawn_yaw=0.418879020478 |
| C1573 | 5f8a6f9597e66d0d | table_friction,spawn_yaw | table_friction=0.24, spawn_yaw=0.314159265359 |
| C1574 | d0bc7533affa1a17 | table_friction,spawn_yaw | table_friction=0.31, spawn_yaw=0.209439510239 |
| C1575 | 4454d9278bfe2399 | table_friction,spawn_yaw | table_friction=0.38, spawn_yaw=0.10471975512 |
| C1576 | 936a6fd90413dcd0 | table_friction,spawn_yaw | table_friction=0.52, spawn_yaw=-0.10471975512 |
| C1577 | 576bdd29c30869ec | table_friction,spawn_yaw | table_friction=0.59, spawn_yaw=-0.209439510239 |
| C1578 | 21b0bd29613daec2 | table_friction,spawn_yaw | table_friction=0.66, spawn_yaw=-0.314159265359 |
| C1579 | 1a039ed676173d23 | table_friction,spawn_yaw | table_friction=0.73, spawn_yaw=-0.418879020478 |
| C1580 | 0a8a79c24a5fceff | table_friction,spawn_yaw | table_friction=0.8, spawn_yaw=-0.523598775598 |
| C1581 | 9cb828ce97116ecb | table_friction,inertia_scale | table_friction=0.1, inertia_scale=0.5 |
| C1582 | 317eb18fdab8f2a9 | table_friction,inertia_scale | table_friction=0.17, inertia_scale=0.65 |
| C1583 | 56238e3a95cd57c8 | table_friction,inertia_scale | table_friction=0.24, inertia_scale=0.8 |
| C1584 | dcaf0efda3ddb5a2 | table_friction,inertia_scale | table_friction=0.31, inertia_scale=0.95 |
| C1585 | 45364a34441bf8d9 | table_friction,inertia_scale | table_friction=0.38, inertia_scale=1.1 |
| C1586 | 92155978723a58bd | table_friction,inertia_scale | table_friction=0.45, inertia_scale=1.25 |
| C1587 | 073e9bf1dd586cf2 | table_friction,inertia_scale | table_friction=0.52, inertia_scale=1.4 |
| C1588 | b92e121b237494c9 | table_friction,inertia_scale | table_friction=0.59, inertia_scale=1.55 |
| C1589 | be48bd3a87e3439c | table_friction,inertia_scale | table_friction=0.66, inertia_scale=1.7 |
| C1590 | 9900acff9a279d43 | table_friction,inertia_scale | table_friction=0.73, inertia_scale=1.85 |
| C1591 | bb12953882c9ecf1 | table_friction,inertia_scale | table_friction=0.8, inertia_scale=2.0 |
| C1592 | 29a8114e93b12c3f | table_friction,inertia_scale | table_friction=0.1, inertia_scale=2.0 |
| C1593 | 0ba43637aa2801ae | table_friction,inertia_scale | table_friction=0.17, inertia_scale=1.85 |
| C1594 | cc4103ad25d396bb | table_friction,inertia_scale | table_friction=0.24, inertia_scale=1.7 |
| C1595 | e2698bef45182be8 | table_friction,inertia_scale | table_friction=0.31, inertia_scale=1.55 |
| C1596 | 5443950b9d7078e0 | table_friction,inertia_scale | table_friction=0.38, inertia_scale=1.4 |
| C1597 | 7535cf7e234052d6 | table_friction,inertia_scale | table_friction=0.52, inertia_scale=1.1 |
| C1598 | 2dcc3a2d859b35c3 | table_friction,inertia_scale | table_friction=0.59, inertia_scale=0.95 |
| C1599 | ed0b377dd2bfdd7f | table_friction,inertia_scale | table_friction=0.66, inertia_scale=0.8 |
| C1600 | 3c9217efd8b58f6a | table_friction,inertia_scale | table_friction=0.73, inertia_scale=0.65 |
| C1601 | fab51075a5027cd2 | table_friction,inertia_scale | table_friction=0.8, inertia_scale=0.5 |
| C1602 | eb0225e0ef6ea4b8 | size,shape | size=0.03, shape=sphere |
| C1603 | 7dca4e88356bdbad | size,shape | size=0.032, shape=sphere |
| C1604 | 03dbcb181bde5abe | size,shape | size=0.034, shape=sphere |
| C1605 | 032c7c4e9e89d4c5 | size,shape | size=0.036, shape=sphere |
| C1606 | 565f2f6ed37d9d04 | size,shape | size=0.038, shape=sphere |
| C1607 | a177ac9ec0ded733 | size,shape | size=0.042, shape=sphere |
| C1608 | 617a7a750e416d87 | size,shape | size=0.044, shape=sphere |
| C1609 | 2b0fbed2f539d60e | size,shape | size=0.046, shape=sphere |
| C1610 | 95042fd6d0c23323 | size,shape | size=0.048, shape=sphere |
| C1611 | eda9530365a27d34 | size,shape | size=0.05, shape=sphere |
| C1612 | df0929389ee70a29 | size,com_x | size=0.03, com_x=-0.005 |
| C1613 | d8dbd9fc29d5e808 | size,com_x | size=0.032, com_x=-0.004 |
| C1614 | 422b00de6197690b | size,com_x | size=0.034, com_x=-0.003 |
| C1615 | be961ac2421b99c9 | size,com_x | size=0.036, com_x=-0.002 |
| C1616 | 4e0ebaf5253bc94e | size,com_x | size=0.038, com_x=-0.001 |
| C1617 | afe065efeb6a29da | size,com_x | size=0.042, com_x=0.001 |
| C1618 | b6bafc01b4ea1fc2 | size,com_x | size=0.044, com_x=0.002 |
| C1619 | 1e253f46396d9aa9 | size,com_x | size=0.046, com_x=0.003 |
| C1620 | 24957a2678a1c809 | size,com_x | size=0.048, com_x=0.004 |
| C1621 | b656e66e4f58ecdc | size,com_x | size=0.05, com_x=0.005 |
| C1622 | cad85a4641418f84 | size,com_x | size=0.03, com_x=0.005 |
| C1623 | 93762c7aed1c4881 | size,com_x | size=0.032, com_x=0.004 |
| C1624 | 0243476dd2851ef3 | size,com_x | size=0.034, com_x=0.003 |
| C1625 | b4bddbb56bfcfeaa | size,com_x | size=0.036, com_x=0.002 |
| C1626 | 348425ff0ffae6c1 | size,com_x | size=0.038, com_x=0.001 |
| C1627 | c584ab4e70043105 | size,com_x | size=0.042, com_x=-0.001 |
| C1628 | 09ad00061a29c987 | size,com_x | size=0.044, com_x=-0.002 |
| C1629 | 75f1ec649bcfc181 | size,com_x | size=0.046, com_x=-0.003 |
| C1630 | 25a3099e988ca10d | size,com_x | size=0.048, com_x=-0.004 |
| C1631 | ebc4c242a8e58625 | size,com_x | size=0.05, com_x=-0.005 |
| C1632 | d9390388dba41dd6 | size,com_y | size=0.03, com_y=-0.005 |
| C1633 | fbcaa588fb866c68 | size,com_y | size=0.032, com_y=-0.004 |
| C1634 | 1e7bfee8f59fc066 | size,com_y | size=0.034, com_y=-0.003 |
| C1635 | 11ecd334fe53a9ff | size,com_y | size=0.036, com_y=-0.002 |
| C1636 | 856d18da127a6053 | size,com_y | size=0.038, com_y=-0.001 |
| C1637 | b25a36ffb38acbb9 | size,com_y | size=0.042, com_y=0.001 |
| C1638 | 4b673bca66d62566 | size,com_y | size=0.044, com_y=0.002 |
| C1639 | 139922437e0ce8fb | size,com_y | size=0.046, com_y=0.003 |
| C1640 | 9c82f6eefebb45ce | size,com_y | size=0.048, com_y=0.004 |
| C1641 | 595fec2b74ec54bb | size,com_y | size=0.05, com_y=0.005 |
| C1642 | e1d8488ca0ccf019 | size,com_y | size=0.03, com_y=0.005 |
| C1643 | 2e5f332c94564f9b | size,com_y | size=0.032, com_y=0.004 |
| C1644 | 61848c038abe469d | size,com_y | size=0.034, com_y=0.003 |
| C1645 | 2f4688fac62b70fa | size,com_y | size=0.036, com_y=0.002 |
| C1646 | 0a71fad545d5384d | size,com_y | size=0.038, com_y=0.001 |
| C1647 | 4d8e667f2371abfe | size,com_y | size=0.042, com_y=-0.001 |
| C1648 | bd53323b6797e5ba | size,com_y | size=0.044, com_y=-0.002 |
| C1649 | dae7b89653febaae | size,com_y | size=0.046, com_y=-0.003 |
| C1650 | d92f956ca5592323 | size,com_y | size=0.048, com_y=-0.004 |
| C1651 | e12456d404e00270 | size,com_y | size=0.05, com_y=-0.005 |
| C1652 | 4217a221d26f9335 | size,com_z | size=0.03, com_z=-0.005 |
| C1653 | f22f428ba94c1cba | size,com_z | size=0.032, com_z=-0.004 |
| C1654 | 37ebd53c04b45b7f | size,com_z | size=0.034, com_z=-0.003 |
| C1655 | 86d15dcac1d7c0fd | size,com_z | size=0.036, com_z=-0.002 |
| C1656 | c663ea6489af6c38 | size,com_z | size=0.038, com_z=-0.001 |
| C1657 | 658d0300617c79e8 | size,com_z | size=0.042, com_z=0.001 |
| C1658 | 9a510e75103bf5c9 | size,com_z | size=0.044, com_z=0.002 |
| C1659 | a27299bae75757b6 | size,com_z | size=0.046, com_z=0.003 |
| C1660 | 21c9a949229cd794 | size,com_z | size=0.048, com_z=0.004 |
| C1661 | 1f66f4866a84c582 | size,com_z | size=0.05, com_z=0.005 |
| C1662 | ef1481311dd2cd09 | size,com_z | size=0.03, com_z=0.005 |
| C1663 | dc49c17e6b676d72 | size,com_z | size=0.032, com_z=0.004 |
| C1664 | 87c0ba632361feb7 | size,com_z | size=0.034, com_z=0.003 |
| C1665 | 977d126ea98c9b70 | size,com_z | size=0.036, com_z=0.002 |
| C1666 | b1623509476ea82a | size,com_z | size=0.038, com_z=0.001 |
| C1667 | 174fb74b7268a51c | size,com_z | size=0.042, com_z=-0.001 |
| C1668 | c5946c52052dfa92 | size,com_z | size=0.044, com_z=-0.002 |
| C1669 | 8711d01436ae698b | size,com_z | size=0.046, com_z=-0.003 |
| C1670 | 707633bb7410c265 | size,com_z | size=0.048, com_z=-0.004 |
| C1671 | 12a18b08197a48a3 | size,com_z | size=0.05, com_z=-0.005 |
| C1672 | d4abf168c96c2cde | size,goal_height | size=0.03, goal_height=0.1 |
| C1673 | 0d65ca911f9e7f6f | size,goal_height | size=0.032, goal_height=0.12 |
| C1674 | ab96985e6c10809a | size,goal_height | size=0.034, goal_height=0.14 |
| C1675 | 1dfadd4310214102 | size,goal_height | size=0.036, goal_height=0.16 |
| C1676 | 1e121933145bd349 | size,goal_height | size=0.038, goal_height=0.18 |
| C1677 | d81d7ecdf521ec13 | size,goal_height | size=0.042, goal_height=0.22 |
| C1678 | 3b435e9c4a53f94d | size,goal_height | size=0.044, goal_height=0.24 |
| C1679 | 60eb62ea5131401c | size,goal_height | size=0.046, goal_height=0.26 |
| C1680 | 8419b94cc697025f | size,goal_height | size=0.048, goal_height=0.28 |
| C1681 | 443e46cd9edef7e7 | size,goal_height | size=0.05, goal_height=0.3 |
| C1682 | e7e2d18cdac1c489 | size,goal_height | size=0.03, goal_height=0.3 |
| C1683 | a18ef8b861ef32f6 | size,goal_height | size=0.032, goal_height=0.28 |
| C1684 | e4aa0e143ce987e5 | size,goal_height | size=0.034, goal_height=0.26 |
| C1685 | 2f91020bcf707c9a | size,goal_height | size=0.036, goal_height=0.24 |
| C1686 | d68ceba06addc95b | size,goal_height | size=0.038, goal_height=0.22 |
| C1687 | ed710d96760f3317 | size,goal_height | size=0.042, goal_height=0.18 |
| C1688 | d388000ceb0c02ba | size,goal_height | size=0.044, goal_height=0.16 |
| C1689 | 6d3f679cb37cc64f | size,goal_height | size=0.046, goal_height=0.14 |
| C1690 | 67c29300a1fc1eeb | size,goal_height | size=0.048, goal_height=0.12 |
| C1691 | 0ee3dfca9377b37f | size,goal_height | size=0.05, goal_height=0.1 |
| C1692 | f0b3757e6725f9b2 | size,restitution | size=0.032, restitution=0.05 |
| C1693 | 52933b0cf24e777a | size,restitution | size=0.034, restitution=0.1 |
| C1694 | f4c9014805c688b9 | size,restitution | size=0.036, restitution=0.15 |
| C1695 | bd11a942f8b3b5ad | size,restitution | size=0.038, restitution=0.2 |
| C1696 | 0aa072d9b155ce04 | size,restitution | size=0.042, restitution=0.3 |
| C1697 | 4a760136c14fad42 | size,restitution | size=0.044, restitution=0.35 |
| C1698 | d93549e3a5ce25f2 | size,restitution | size=0.046, restitution=0.4 |
| C1699 | 8e267fcc877cf8c3 | size,restitution | size=0.048, restitution=0.45 |
| C1700 | 21556659e8a0cec8 | size,restitution | size=0.05, restitution=0.5 |
| C1701 | c9fac9b216c897eb | size,restitution | size=0.03, restitution=0.5 |
| C1702 | 1e372313cdd8dd01 | size,restitution | size=0.032, restitution=0.45 |
| C1703 | d6d2e545027a9d69 | size,restitution | size=0.034, restitution=0.4 |
| C1704 | 2ea51065b46c47b7 | size,restitution | size=0.036, restitution=0.35 |
| C1705 | a144593702e0788b | size,restitution | size=0.038, restitution=0.3 |
| C1706 | 03a7f4dac2da0101 | size,restitution | size=0.042, restitution=0.2 |
| C1707 | 6b6c2980e2c8ca59 | size,restitution | size=0.044, restitution=0.15 |
| C1708 | ff240f2a115e12ce | size,restitution | size=0.046, restitution=0.1 |
| C1709 | dae2768e7c615a00 | size,restitution | size=0.048, restitution=0.05 |
| C1710 | 805b1bdf0bc69ce7 | size,linear_damping | size=0.032, linear_damping=0.1 |
| C1711 | a8d2339cc71b98cf | size,linear_damping | size=0.034, linear_damping=0.2 |
| C1712 | d122acb961dfc93d | size,linear_damping | size=0.036, linear_damping=0.3 |
| C1713 | 963630124610354b | size,linear_damping | size=0.038, linear_damping=0.4 |
| C1714 | f8c7883fdea16f7f | size,linear_damping | size=0.042, linear_damping=0.6 |
| C1715 | f2f4cf6027781394 | size,linear_damping | size=0.044, linear_damping=0.7 |
| C1716 | 4acd89fdc8e6dc31 | size,linear_damping | size=0.046, linear_damping=0.8 |
| C1717 | c1a08b52e2ae0967 | size,linear_damping | size=0.048, linear_damping=0.9 |
| C1718 | 2d53d19584d28bc9 | size,linear_damping | size=0.05, linear_damping=1.0 |
| C1719 | 434fe0e2eb56e1a4 | size,linear_damping | size=0.03, linear_damping=1.0 |
| C1720 | a6954a5457ae7861 | size,linear_damping | size=0.032, linear_damping=0.9 |
| C1721 | 49ab55028cd7003f | size,linear_damping | size=0.034, linear_damping=0.8 |
| C1722 | 15fa5ee19a869196 | size,linear_damping | size=0.036, linear_damping=0.7 |
| C1723 | a806c02340271223 | size,linear_damping | size=0.038, linear_damping=0.6 |
| C1724 | 2ed3270413cc75c5 | size,linear_damping | size=0.042, linear_damping=0.4 |
| C1725 | 81943388a08ab361 | size,linear_damping | size=0.044, linear_damping=0.3 |
| C1726 | 51d234c77420f57f | size,linear_damping | size=0.046, linear_damping=0.2 |
| C1727 | 3da876efa0133891 | size,linear_damping | size=0.048, linear_damping=0.1 |
| C1728 | 851340f5477402ba | size,angular_damping | size=0.03, angular_damping=0.0 |
| C1729 | 26573a6d8c3b30a1 | size,angular_damping | size=0.034, angular_damping=0.1 |
| C1730 | 3636f3f5a60ba806 | size,angular_damping | size=0.036, angular_damping=0.15 |
| C1731 | 0a41d77a6acaa078 | size,angular_damping | size=0.038, angular_damping=0.2 |
| C1732 | 3a3740c85a7e5227 | size,angular_damping | size=0.042, angular_damping=0.3 |
| C1733 | 81086424f4e34421 | size,angular_damping | size=0.044, angular_damping=0.35 |
| C1734 | c8f08b92747efbf8 | size,angular_damping | size=0.046, angular_damping=0.4 |
| C1735 | 1f2af74864a179d5 | size,angular_damping | size=0.048, angular_damping=0.45 |
| C1736 | 316e4e3051fab883 | size,angular_damping | size=0.05, angular_damping=0.5 |
| C1737 | fb0c5272e6d9d063 | size,angular_damping | size=0.03, angular_damping=0.5 |
| C1738 | 2822e0723314297c | size,angular_damping | size=0.032, angular_damping=0.45 |
| C1739 | 68b9c14cc443ef88 | size,angular_damping | size=0.034, angular_damping=0.4 |
| C1740 | c6c7b4cb9f4ae2a2 | size,angular_damping | size=0.036, angular_damping=0.35 |
| C1741 | 4462a327ad0d691e | size,angular_damping | size=0.038, angular_damping=0.3 |
| C1742 | e76fdd101b2ad997 | size,angular_damping | size=0.042, angular_damping=0.2 |
| C1743 | 7be01ef9ac161330 | size,angular_damping | size=0.044, angular_damping=0.15 |
| C1744 | 7d5f19c0a7f613c5 | size,angular_damping | size=0.046, angular_damping=0.1 |
| C1745 | b721dc7e7a847a42 | size,angular_damping | size=0.05, angular_damping=0.0 |
| C1746 | 897b401cebe0874a | size,spawn_x | size=0.03, spawn_x=-0.04 |
| C1747 | 46aebc531ac17e4b | size,spawn_x | size=0.032, spawn_x=-0.032 |
| C1748 | e1c834064f4a8512 | size,spawn_x | size=0.034, spawn_x=-0.024 |
| C1749 | 08988a3ea375bac4 | size,spawn_x | size=0.036, spawn_x=-0.016 |
| C1750 | 032df3414c706632 | size,spawn_x | size=0.038, spawn_x=-0.008 |
| C1751 | 76b923858e6b9a2a | size,spawn_x | size=0.042, spawn_x=0.008 |
| C1752 | e165046786557ca4 | size,spawn_x | size=0.044, spawn_x=0.016 |
| C1753 | eab7feb774615d83 | size,spawn_x | size=0.046, spawn_x=0.024 |
| C1754 | fd9bdf30d01d0dc0 | size,spawn_x | size=0.048, spawn_x=0.032 |
| C1755 | 7bc5389da383e7f7 | size,spawn_x | size=0.05, spawn_x=0.04 |
| C1756 | da681b4187c182a0 | size,spawn_x | size=0.03, spawn_x=0.04 |
| C1757 | 998c9824e0583eed | size,spawn_x | size=0.032, spawn_x=0.032 |
| C1758 | 4a164cbdededed18 | size,spawn_x | size=0.034, spawn_x=0.024 |
| C1759 | 19a90f7cef5e8d2e | size,spawn_x | size=0.036, spawn_x=0.016 |
| C1760 | ca120dbf6986c98d | size,spawn_x | size=0.038, spawn_x=0.008 |
| C1761 | 5c11cf84edfaa47a | size,spawn_x | size=0.042, spawn_x=-0.008 |
| C1762 | 43f160aa0460e17b | size,spawn_x | size=0.044, spawn_x=-0.016 |
| C1763 | a4e6e6e77d051c13 | size,spawn_x | size=0.046, spawn_x=-0.024 |
| C1764 | 4e6b6773712f03b7 | size,spawn_x | size=0.048, spawn_x=-0.032 |
| C1765 | 45fa1eede4cb2131 | size,spawn_x | size=0.05, spawn_x=-0.04 |
| C1766 | 4db7f702adb88bde | size,spawn_y | size=0.03, spawn_y=-0.04 |
| C1767 | 4126c07c7dd1cf04 | size,spawn_y | size=0.032, spawn_y=-0.032 |
| C1768 | 99b1b1408ef74296 | size,spawn_y | size=0.034, spawn_y=-0.024 |
| C1769 | 67bdb4afa092a5a9 | size,spawn_y | size=0.036, spawn_y=-0.016 |
| C1770 | bba5f6d71dd568ed | size,spawn_y | size=0.038, spawn_y=-0.008 |
| C1771 | f4e661e52b18bd7c | size,spawn_y | size=0.042, spawn_y=0.008 |
| C1772 | b5de89dd0267aaa1 | size,spawn_y | size=0.044, spawn_y=0.016 |
| C1773 | 514deef5c60b6364 | size,spawn_y | size=0.046, spawn_y=0.024 |
| C1774 | fbeeaa5abd30569a | size,spawn_y | size=0.048, spawn_y=0.032 |
| C1775 | a7d36534c9359b42 | size,spawn_y | size=0.05, spawn_y=0.04 |
| C1776 | 34dd45e2a32673d0 | size,spawn_y | size=0.03, spawn_y=0.04 |
| C1777 | 309d5437f7c834ab | size,spawn_y | size=0.032, spawn_y=0.032 |
| C1778 | 6bd8a1f5c4efc532 | size,spawn_y | size=0.034, spawn_y=0.024 |
| C1779 | 5330fd314bbb6893 | size,spawn_y | size=0.036, spawn_y=0.016 |
| C1780 | 3574dadb0e38bda6 | size,spawn_y | size=0.038, spawn_y=0.008 |
| C1781 | 3294df75d04fd906 | size,spawn_y | size=0.042, spawn_y=-0.008 |
| C1782 | 6e28ebf1c7ee4ef3 | size,spawn_y | size=0.044, spawn_y=-0.016 |
| C1783 | 6acb37d8cf1cbb5a | size,spawn_y | size=0.046, spawn_y=-0.024 |
| C1784 | 78c3f6114d02ee0e | size,spawn_y | size=0.048, spawn_y=-0.032 |
| C1785 | 0de11cc3ade863af | size,spawn_y | size=0.05, spawn_y=-0.04 |
| C1786 | 8a3502fb3052a8df | size,spawn_yaw | size=0.03, spawn_yaw=-0.523598775598 |
| C1787 | 1a952da82715ad64 | size,spawn_yaw | size=0.032, spawn_yaw=-0.418879020478 |
| C1788 | 2fb2178bca70b7e7 | size,spawn_yaw | size=0.034, spawn_yaw=-0.314159265359 |
| C1789 | 15581b47e42b39e2 | size,spawn_yaw | size=0.036, spawn_yaw=-0.209439510239 |
| C1790 | fc9ded05c0e6bf77 | size,spawn_yaw | size=0.038, spawn_yaw=-0.10471975512 |
| C1791 | 2790c64c7b9aa3e5 | size,spawn_yaw | size=0.042, spawn_yaw=0.10471975512 |
| C1792 | a494fc7aeab188d6 | size,spawn_yaw | size=0.044, spawn_yaw=0.209439510239 |
| C1793 | 1539326aac60a90f | size,spawn_yaw | size=0.046, spawn_yaw=0.314159265359 |
| C1794 | 524911fff0bdce0e | size,spawn_yaw | size=0.048, spawn_yaw=0.418879020478 |
| C1795 | 16b907de92a74440 | size,spawn_yaw | size=0.05, spawn_yaw=0.523598775598 |
| C1796 | b399d90308ac449a | size,spawn_yaw | size=0.03, spawn_yaw=0.523598775598 |
| C1797 | 22104e678d35cba0 | size,spawn_yaw | size=0.032, spawn_yaw=0.418879020478 |
| C1798 | a7f02dead5b3f4af | size,spawn_yaw | size=0.034, spawn_yaw=0.314159265359 |
| C1799 | a13a8fa9a7b64f66 | size,spawn_yaw | size=0.036, spawn_yaw=0.209439510239 |
| C1800 | f11e5c86302d0d99 | size,spawn_yaw | size=0.038, spawn_yaw=0.10471975512 |
| C1801 | f11a9273852e838b | size,spawn_yaw | size=0.042, spawn_yaw=-0.10471975512 |
| C1802 | 98c09163e7a63800 | size,spawn_yaw | size=0.044, spawn_yaw=-0.209439510239 |
| C1803 | c0dcb6cf89a34f3e | size,spawn_yaw | size=0.046, spawn_yaw=-0.314159265359 |
| C1804 | 7e3165ffdf590799 | size,spawn_yaw | size=0.048, spawn_yaw=-0.418879020478 |
| C1805 | 7774b5acbb6092cf | size,spawn_yaw | size=0.05, spawn_yaw=-0.523598775598 |
| C1806 | 6b21f8a9cc37aca6 | size,inertia_scale | size=0.03, inertia_scale=0.5 |
| C1807 | e12569211c32de92 | size,inertia_scale | size=0.032, inertia_scale=0.65 |
| C1808 | e56f6bb7882e8006 | size,inertia_scale | size=0.034, inertia_scale=0.8 |
| C1809 | df6f514cf13bb1fd | size,inertia_scale | size=0.036, inertia_scale=0.95 |
| C1810 | 97a7cf9679b84186 | size,inertia_scale | size=0.038, inertia_scale=1.1 |
| C1811 | e6721b6d7ca56799 | size,inertia_scale | size=0.042, inertia_scale=1.4 |
| C1812 | 547b5fe133a769ab | size,inertia_scale | size=0.044, inertia_scale=1.55 |
| C1813 | 08bd28af977592cd | size,inertia_scale | size=0.046, inertia_scale=1.7 |
| C1814 | 4f69588ea36c2e13 | size,inertia_scale | size=0.048, inertia_scale=1.85 |
| C1815 | 6242de9d43679a6c | size,inertia_scale | size=0.05, inertia_scale=2.0 |
| C1816 | 0db048a67d980e75 | size,inertia_scale | size=0.03, inertia_scale=2.0 |
| C1817 | 77e05e4885b69cd5 | size,inertia_scale | size=0.032, inertia_scale=1.85 |
| C1818 | 60ea264163a6422b | size,inertia_scale | size=0.034, inertia_scale=1.7 |
| C1819 | 60b6743009c5432e | size,inertia_scale | size=0.036, inertia_scale=1.55 |
| C1820 | 716698621017f558 | size,inertia_scale | size=0.038, inertia_scale=1.4 |
| C1821 | 318f3d2475cdb818 | size,inertia_scale | size=0.042, inertia_scale=1.1 |
| C1822 | b8b3ee1be8b4a620 | size,inertia_scale | size=0.044, inertia_scale=0.95 |
| C1823 | 5927d556a9a04823 | size,inertia_scale | size=0.046, inertia_scale=0.8 |
| C1824 | 2b2b768c71755db6 | size,inertia_scale | size=0.048, inertia_scale=0.65 |
| C1825 | cb6797cca5c6c6e2 | size,inertia_scale | size=0.05, inertia_scale=0.5 |
| C1826 | 5bdcdac8bcc0f033 | shape,com_x | shape=sphere, com_x=-0.005 |
| C1827 | 4196f9208750d6b2 | shape,com_x | shape=sphere, com_x=-0.004 |
| C1828 | 9f692dffda1c7d24 | shape,com_x | shape=sphere, com_x=-0.003 |
| C1829 | 601a1108d8c9a971 | shape,com_x | shape=sphere, com_x=-0.002 |
| C1830 | fd712c28e11d3be6 | shape,com_x | shape=sphere, com_x=-0.001 |
| C1831 | 93db9af352206a59 | shape,com_x | shape=sphere, com_x=0.001 |
| C1832 | 0b53688d119a2923 | shape,com_x | shape=sphere, com_x=0.002 |
| C1833 | bb81fffda663b4e0 | shape,com_x | shape=sphere, com_x=0.003 |
| C1834 | 692b2bdc528438d2 | shape,com_x | shape=sphere, com_x=0.004 |
| C1835 | 58bf89276bca5b47 | shape,com_x | shape=sphere, com_x=0.005 |
| C1836 | 150af98b3ac3f4dc | shape,com_y | shape=sphere, com_y=-0.005 |
| C1837 | 3220f04aeac5f4d2 | shape,com_y | shape=sphere, com_y=-0.004 |
| C1838 | 5d35c0578570f1bc | shape,com_y | shape=sphere, com_y=-0.003 |
| C1839 | 5b8420a501585f70 | shape,com_y | shape=sphere, com_y=-0.002 |
| C1840 | 48f6891e8a520117 | shape,com_y | shape=sphere, com_y=-0.001 |
| C1841 | 5ea967e032253067 | shape,com_y | shape=sphere, com_y=0.001 |
| C1842 | 22d9cd5792c79c01 | shape,com_y | shape=sphere, com_y=0.002 |
| C1843 | e88098f58ed660fc | shape,com_y | shape=sphere, com_y=0.003 |
| C1844 | b41f8e8427836057 | shape,com_y | shape=sphere, com_y=0.004 |
| C1845 | 547b233241ecfc17 | shape,com_y | shape=sphere, com_y=0.005 |
| C1846 | 460e8ba72f587f9e | shape,com_z | shape=sphere, com_z=-0.005 |
| C1847 | 1a83d9c0c8a8199e | shape,com_z | shape=sphere, com_z=-0.004 |
| C1848 | 959619b8774b8d4c | shape,com_z | shape=sphere, com_z=-0.003 |
| C1849 | a4f1a0929ad47639 | shape,com_z | shape=sphere, com_z=-0.002 |
| C1850 | 39f7947c6380a56e | shape,com_z | shape=sphere, com_z=-0.001 |
| C1851 | c541b29a6d724cd1 | shape,com_z | shape=sphere, com_z=0.001 |
| C1852 | 80d0d679b2acb105 | shape,com_z | shape=sphere, com_z=0.002 |
| C1853 | 44d57a5fa59ab5fc | shape,com_z | shape=sphere, com_z=0.003 |
| C1854 | 5ee4d5196e52a48f | shape,com_z | shape=sphere, com_z=0.004 |
| C1855 | e97ca3fcbd8f13b6 | shape,com_z | shape=sphere, com_z=0.005 |
| C1856 | 4bd197725a59e847 | shape,goal_height | shape=sphere, goal_height=0.1 |
| C1857 | f0cb336c7663d9c0 | shape,goal_height | shape=sphere, goal_height=0.12 |
| C1858 | 40df7bba23363947 | shape,goal_height | shape=sphere, goal_height=0.14 |
| C1859 | 0a75d2e508c2339b | shape,goal_height | shape=sphere, goal_height=0.16 |
| C1860 | 1a6dca7944451327 | shape,goal_height | shape=sphere, goal_height=0.18 |
| C1861 | 86725505a004a90b | shape,goal_height | shape=sphere, goal_height=0.22 |
| C1862 | 1394fc0a591aa143 | shape,goal_height | shape=sphere, goal_height=0.24 |
| C1863 | 3fd33183d2ab2a8e | shape,goal_height | shape=sphere, goal_height=0.26 |
| C1864 | e2d329496b7ec12c | shape,goal_height | shape=sphere, goal_height=0.28 |
| C1865 | e8a34ff4564392f2 | shape,goal_height | shape=sphere, goal_height=0.3 |
| C1866 | df97abf4e9f3eb2f | shape,restitution | shape=sphere, restitution=0.05 |
| C1867 | 55e51e6acff64a3a | shape,restitution | shape=sphere, restitution=0.1 |
| C1868 | 4220fdf5bcdf564f | shape,restitution | shape=sphere, restitution=0.15 |
| C1869 | 83ab928a48a2cd7a | shape,restitution | shape=sphere, restitution=0.2 |
| C1870 | 5a3593b051510a5b | shape,restitution | shape=sphere, restitution=0.25 |
| C1871 | 483d70c0fee1fe23 | shape,restitution | shape=sphere, restitution=0.3 |
| C1872 | 598ee85f8ff851de | shape,restitution | shape=sphere, restitution=0.35 |
| C1873 | 1d72af1c9fdb782b | shape,restitution | shape=sphere, restitution=0.4 |
| C1874 | 9be7a62f20e9c692 | shape,restitution | shape=sphere, restitution=0.45 |
| C1875 | 5caa5637876a5279 | shape,restitution | shape=sphere, restitution=0.5 |
| C1876 | 4299fd2780cddd66 | shape,linear_damping | shape=sphere, linear_damping=0.1 |
| C1877 | 7d1afd860fbdd908 | shape,linear_damping | shape=sphere, linear_damping=0.2 |
| C1878 | db06983edb59e22a | shape,linear_damping | shape=sphere, linear_damping=0.3 |
| C1879 | a655205355d1ac79 | shape,linear_damping | shape=sphere, linear_damping=0.4 |
| C1880 | 40fe49d94d1b9641 | shape,linear_damping | shape=sphere, linear_damping=0.5 |
| C1881 | c5dc37e7e750e52a | shape,linear_damping | shape=sphere, linear_damping=0.6 |
| C1882 | d367c278a33950f3 | shape,linear_damping | shape=sphere, linear_damping=0.7 |
| C1883 | d6c28ae1cc72475d | shape,linear_damping | shape=sphere, linear_damping=0.8 |
| C1884 | 565348ed9df88c5e | shape,linear_damping | shape=sphere, linear_damping=0.9 |
| C1885 | c70b7a2d27de2a80 | shape,linear_damping | shape=sphere, linear_damping=1.0 |
| C1886 | 6cd5c317f63e8f7e | shape,angular_damping | shape=sphere, angular_damping=0.0 |
| C1887 | 52c954cca2615672 | shape,angular_damping | shape=sphere, angular_damping=0.1 |
| C1888 | 0ce330fc2693b668 | shape,angular_damping | shape=sphere, angular_damping=0.15 |
| C1889 | b2f82e62241f1a4d | shape,angular_damping | shape=sphere, angular_damping=0.2 |
| C1890 | 333b972075627c50 | shape,angular_damping | shape=sphere, angular_damping=0.25 |
| C1891 | ebd0df0180a213a1 | shape,angular_damping | shape=sphere, angular_damping=0.3 |
| C1892 | 0399523d9a13f637 | shape,angular_damping | shape=sphere, angular_damping=0.35 |
| C1893 | d53e770486d648fe | shape,angular_damping | shape=sphere, angular_damping=0.4 |
| C1894 | 9c6be6b56b841c71 | shape,angular_damping | shape=sphere, angular_damping=0.45 |
| C1895 | 82304874bb33bea3 | shape,angular_damping | shape=sphere, angular_damping=0.5 |
| C1896 | 8152149f06d1cb9c | shape,spawn_x | shape=sphere, spawn_x=-0.04 |
| C1897 | f5be72c32ddcf1b0 | shape,spawn_x | shape=sphere, spawn_x=-0.032 |
| C1898 | 35c47463c3ad6fa7 | shape,spawn_x | shape=sphere, spawn_x=-0.024 |
| C1899 | 9d3bf94deda29466 | shape,spawn_x | shape=sphere, spawn_x=-0.016 |
| C1900 | f33a1b4fd8482236 | shape,spawn_x | shape=sphere, spawn_x=-0.008 |
| C1901 | eec69dc76405d16a | shape,spawn_x | shape=sphere, spawn_x=0.008 |
| C1902 | 70fc79839cca8f7e | shape,spawn_x | shape=sphere, spawn_x=0.016 |
| C1903 | 05ef2b2976c66ad5 | shape,spawn_x | shape=sphere, spawn_x=0.024 |
| C1904 | 1f892310268dfe63 | shape,spawn_x | shape=sphere, spawn_x=0.032 |
| C1905 | f7fb4741a885d03f | shape,spawn_x | shape=sphere, spawn_x=0.04 |
| C1906 | d7139515d27f75a8 | shape,spawn_y | shape=sphere, spawn_y=-0.04 |
| C1907 | fe346176c28a38d8 | shape,spawn_y | shape=sphere, spawn_y=-0.032 |
| C1908 | 4c9c0ac338817b5e | shape,spawn_y | shape=sphere, spawn_y=-0.024 |
| C1909 | 703e02df348060da | shape,spawn_y | shape=sphere, spawn_y=-0.016 |
| C1910 | 3153f6c932d7a513 | shape,spawn_y | shape=sphere, spawn_y=-0.008 |
| C1911 | ef2e3016b6c880bc | shape,spawn_y | shape=sphere, spawn_y=0.008 |
| C1912 | beff8d203fee2b9a | shape,spawn_y | shape=sphere, spawn_y=0.016 |
| C1913 | 75ccd66745f9f796 | shape,spawn_y | shape=sphere, spawn_y=0.024 |
| C1914 | 0615d9305dbada86 | shape,spawn_y | shape=sphere, spawn_y=0.032 |
| C1915 | 61a69145bc5c6503 | shape,spawn_y | shape=sphere, spawn_y=0.04 |
| C1916 | c69f3d8e2f2f6102 | shape,spawn_yaw | shape=sphere, spawn_yaw=-0.523598775598 |
| C1917 | 3e006ad91f416e9c | shape,spawn_yaw | shape=sphere, spawn_yaw=-0.418879020478 |
| C1918 | ca52d6ba3d38dd8f | shape,spawn_yaw | shape=sphere, spawn_yaw=-0.314159265359 |
| C1919 | 9a07be2fd8d0023d | shape,spawn_yaw | shape=sphere, spawn_yaw=-0.209439510239 |
| C1920 | 4dd9c831df04a450 | shape,spawn_yaw | shape=sphere, spawn_yaw=-0.10471975512 |
| C1921 | 68e73c5c7c25f138 | shape,spawn_yaw | shape=sphere, spawn_yaw=0.10471975512 |
| C1922 | a9405587e7f7b825 | shape,spawn_yaw | shape=sphere, spawn_yaw=0.209439510239 |
| C1923 | 37c3c1bd95e5802b | shape,spawn_yaw | shape=sphere, spawn_yaw=0.314159265359 |
| C1924 | 7a93a421866e183a | shape,spawn_yaw | shape=sphere, spawn_yaw=0.418879020478 |
| C1925 | 85710402425f34dd | shape,spawn_yaw | shape=sphere, spawn_yaw=0.523598775598 |
| C1926 | 8d76a8917213c0b0 | shape,inertia_scale | shape=sphere, inertia_scale=0.5 |
| C1927 | 353cd484bb70f1f9 | shape,inertia_scale | shape=sphere, inertia_scale=0.65 |
| C1928 | d8b6a22ad04d4fea | shape,inertia_scale | shape=sphere, inertia_scale=0.8 |
| C1929 | de53f9b9d3abf67e | shape,inertia_scale | shape=sphere, inertia_scale=0.95 |
| C1930 | 35f7216b6f11d461 | shape,inertia_scale | shape=sphere, inertia_scale=1.1 |
| C1931 | 8f758230e82c303a | shape,inertia_scale | shape=sphere, inertia_scale=1.25 |
| C1932 | d5ee1bc717b8ef23 | shape,inertia_scale | shape=sphere, inertia_scale=1.4 |
| C1933 | 20eacc2ceea6af6a | shape,inertia_scale | shape=sphere, inertia_scale=1.55 |
| C1934 | 20a7169e088eb924 | shape,inertia_scale | shape=sphere, inertia_scale=1.7 |
| C1935 | dae81a2a88c6246c | shape,inertia_scale | shape=sphere, inertia_scale=1.85 |
| C1936 | 13a1315940d46a5c | shape,inertia_scale | shape=sphere, inertia_scale=2.0 |
| C1937 | 0a97a8e2debf32e9 | com_x,com_y | com_x=-0.005, com_y=-0.005 |
| C1938 | ca4a91ee4aa88084 | com_x,com_y | com_x=-0.004, com_y=-0.004 |
| C1939 | 91606c2968aaa065 | com_x,com_y | com_x=-0.003, com_y=-0.003 |
| C1940 | 315e975703c5bb3a | com_x,com_y | com_x=-0.002, com_y=-0.002 |
| C1941 | da87a8b901d308e3 | com_x,com_y | com_x=-0.001, com_y=-0.001 |
| C1942 | 1a3b9947d7c8ac8c | com_x,com_y | com_x=0.001, com_y=0.001 |
| C1943 | ae5d3f32504561ad | com_x,com_y | com_x=0.002, com_y=0.002 |
| C1944 | 680f86d6f1006423 | com_x,com_y | com_x=0.003, com_y=0.003 |
| C1945 | fecabd9859e7744e | com_x,com_y | com_x=0.004, com_y=0.004 |
| C1946 | 2ca496f367be9f78 | com_x,com_y | com_x=0.005, com_y=0.005 |
| C1947 | 05839bed7c8b0208 | com_x,com_y | com_x=-0.005, com_y=0.005 |
| C1948 | ea5d814e9777045c | com_x,com_y | com_x=-0.004, com_y=0.004 |
| C1949 | 4ac1b8cd34281923 | com_x,com_y | com_x=-0.003, com_y=0.003 |
| C1950 | c86b5fb2f4259710 | com_x,com_y | com_x=-0.002, com_y=0.002 |
| C1951 | 87efc74c35654d24 | com_x,com_y | com_x=-0.001, com_y=0.001 |
| C1952 | a67ba931405b84e4 | com_x,com_y | com_x=0.001, com_y=-0.001 |
| C1953 | 63c8c131de7ca6d2 | com_x,com_y | com_x=0.002, com_y=-0.002 |
| C1954 | 3e8f212e884ab6f7 | com_x,com_y | com_x=0.003, com_y=-0.003 |
| C1955 | 88d7b353811e0ac3 | com_x,com_y | com_x=0.004, com_y=-0.004 |
| C1956 | 52215c35af01e63c | com_x,com_y | com_x=0.005, com_y=-0.005 |
| C1957 | 87809b96d4db3fdf | com_x,com_z | com_x=-0.005, com_z=-0.005 |
| C1958 | 9914b3f9be865500 | com_x,com_z | com_x=-0.004, com_z=-0.004 |
| C1959 | bd97958630ef8076 | com_x,com_z | com_x=-0.003, com_z=-0.003 |
| C1960 | e2e528fa44faa14f | com_x,com_z | com_x=-0.002, com_z=-0.002 |
| C1961 | 3f1286416956f066 | com_x,com_z | com_x=-0.001, com_z=-0.001 |
| C1962 | f41a131939e9f7d7 | com_x,com_z | com_x=0.001, com_z=0.001 |
| C1963 | e9fc8651c38bbfdc | com_x,com_z | com_x=0.002, com_z=0.002 |
| C1964 | 7cd853e58e29e92e | com_x,com_z | com_x=0.003, com_z=0.003 |
| C1965 | 296d3495ebc87fa4 | com_x,com_z | com_x=0.004, com_z=0.004 |
| C1966 | 2677340965420f0d | com_x,com_z | com_x=0.005, com_z=0.005 |
| C1967 | 3184a35ceee2a632 | com_x,com_z | com_x=-0.005, com_z=0.005 |
| C1968 | 56ff74b2a06fc758 | com_x,com_z | com_x=-0.004, com_z=0.004 |
| C1969 | 1c3149f4799bce6d | com_x,com_z | com_x=-0.003, com_z=0.003 |
| C1970 | 5f527e462e585fc4 | com_x,com_z | com_x=-0.002, com_z=0.002 |
| C1971 | 4b221ca58ce5c282 | com_x,com_z | com_x=-0.001, com_z=0.001 |
| C1972 | 5ca6dec98daccf94 | com_x,com_z | com_x=0.001, com_z=-0.001 |
| C1973 | d7f4637c2a06cb01 | com_x,com_z | com_x=0.002, com_z=-0.002 |
| C1974 | 1070c14531d1db87 | com_x,com_z | com_x=0.003, com_z=-0.003 |
| C1975 | fa0549c2ea82d81d | com_x,com_z | com_x=0.004, com_z=-0.004 |
| C1976 | 3870cd317f1f6726 | com_x,com_z | com_x=0.005, com_z=-0.005 |
| C1977 | ad473adbde629fa8 | com_x,goal_height | com_x=-0.005, goal_height=0.1 |
| C1978 | be5f422a45263967 | com_x,goal_height | com_x=-0.004, goal_height=0.12 |
| C1979 | 9b5049b65acbd22a | com_x,goal_height | com_x=-0.003, goal_height=0.14 |
| C1980 | 8ecd387197b3b09e | com_x,goal_height | com_x=-0.002, goal_height=0.16 |
| C1981 | 79f19e7dd24f3d5f | com_x,goal_height | com_x=-0.001, goal_height=0.18 |
| C1982 | 9e844aafc1b7b4c7 | com_x,goal_height | com_x=0.001, goal_height=0.22 |
| C1983 | 2d50dd3ff7ec1cf9 | com_x,goal_height | com_x=0.002, goal_height=0.24 |
| C1984 | 6686881bb365dfe7 | com_x,goal_height | com_x=0.003, goal_height=0.26 |
| C1985 | 98d0fe46fe19c035 | com_x,goal_height | com_x=0.004, goal_height=0.28 |
| C1986 | 7b4725efb143336e | com_x,goal_height | com_x=0.005, goal_height=0.3 |
| C1987 | 5705e7e0d662f925 | com_x,goal_height | com_x=-0.005, goal_height=0.3 |
| C1988 | 809215072b003913 | com_x,goal_height | com_x=-0.004, goal_height=0.28 |
| C1989 | 6e277e40bfb15312 | com_x,goal_height | com_x=-0.003, goal_height=0.26 |
| C1990 | feee4de6263d46e0 | com_x,goal_height | com_x=-0.002, goal_height=0.24 |
| C1991 | 4d66faa74de7dbc5 | com_x,goal_height | com_x=-0.001, goal_height=0.22 |
| C1992 | 5b071c7294b251a8 | com_x,goal_height | com_x=0.001, goal_height=0.18 |
| C1993 | 2cad43a70e990177 | com_x,goal_height | com_x=0.002, goal_height=0.16 |
| C1994 | 4d4080af14edf924 | com_x,goal_height | com_x=0.003, goal_height=0.14 |
| C1995 | ee746ba8eeff4177 | com_x,goal_height | com_x=0.004, goal_height=0.12 |
| C1996 | ef9527e96cc9d929 | com_x,goal_height | com_x=0.005, goal_height=0.1 |
| C1997 | e6843cd77910d4b4 | com_x,restitution | com_x=-0.004, restitution=0.05 |
| C1998 | fbffee38a1abcce3 | com_x,restitution | com_x=-0.003, restitution=0.1 |
| C1999 | 69121218e2a8f3c4 | com_x,restitution | com_x=-0.002, restitution=0.15 |
| C2000 | cb76a3c3ddbda714 | com_x,restitution | com_x=-0.001, restitution=0.2 |
| C2001 | a15a271eb2275b0b | com_x,restitution | com_x=0.001, restitution=0.3 |
| C2002 | 68696d7b2889b2e3 | com_x,restitution | com_x=0.002, restitution=0.35 |
| C2003 | 689d8a1bd95f9b79 | com_x,restitution | com_x=0.003, restitution=0.4 |
| C2004 | 431f4fff8d11f4e6 | com_x,restitution | com_x=0.004, restitution=0.45 |
| C2005 | 582513d0dbda9cb4 | com_x,restitution | com_x=0.005, restitution=0.5 |
| C2006 | 53514d8f2962ff50 | com_x,restitution | com_x=-0.005, restitution=0.5 |
| C2007 | 988490ae996cb1d4 | com_x,restitution | com_x=-0.004, restitution=0.45 |
| C2008 | d52a55a9fb0b3002 | com_x,restitution | com_x=-0.003, restitution=0.4 |
| C2009 | 1d9add9968831fb4 | com_x,restitution | com_x=-0.002, restitution=0.35 |
| C2010 | 70c10406aab648da | com_x,restitution | com_x=-0.001, restitution=0.3 |
| C2011 | 448221a7bb7a8478 | com_x,restitution | com_x=0.001, restitution=0.2 |
| C2012 | 646c246d0a59052a | com_x,restitution | com_x=0.002, restitution=0.15 |
| C2013 | f23ac52acddd123e | com_x,restitution | com_x=0.003, restitution=0.1 |
| C2014 | 097b31b66dfbea51 | com_x,restitution | com_x=0.004, restitution=0.05 |
| C2015 | 624344201d64bd39 | com_x,linear_damping | com_x=-0.004, linear_damping=0.1 |
| C2016 | 2a6e81b27d29275c | com_x,linear_damping | com_x=-0.003, linear_damping=0.2 |
| C2017 | e23f42a82466ab2b | com_x,linear_damping | com_x=-0.002, linear_damping=0.3 |
| C2018 | 009110fd099adfdb | com_x,linear_damping | com_x=-0.001, linear_damping=0.4 |
| C2019 | 67c3c547ba2970e0 | com_x,linear_damping | com_x=0.001, linear_damping=0.6 |
| C2020 | e5eb091f0ef1e111 | com_x,linear_damping | com_x=0.002, linear_damping=0.7 |
| C2021 | b7e561d82ec2a7f1 | com_x,linear_damping | com_x=0.003, linear_damping=0.8 |
| C2022 | 423a8c01acafb37a | com_x,linear_damping | com_x=0.004, linear_damping=0.9 |
| C2023 | d35b2ec1bcce3fea | com_x,linear_damping | com_x=0.005, linear_damping=1.0 |
| C2024 | 6f97c70a07bc7ef8 | com_x,linear_damping | com_x=-0.005, linear_damping=1.0 |
| C2025 | 529562362745914f | com_x,linear_damping | com_x=-0.004, linear_damping=0.9 |
| C2026 | 29acd297d53447ea | com_x,linear_damping | com_x=-0.003, linear_damping=0.8 |
| C2027 | 92055eb2e8e6a877 | com_x,linear_damping | com_x=-0.002, linear_damping=0.7 |
| C2028 | 82597ced2adf92df | com_x,linear_damping | com_x=-0.001, linear_damping=0.6 |
| C2029 | 2beb4aff6ce99f82 | com_x,linear_damping | com_x=0.001, linear_damping=0.4 |
| C2030 | a01a69e5f96a3187 | com_x,linear_damping | com_x=0.002, linear_damping=0.3 |
| C2031 | 01ff82f6b2676ff8 | com_x,linear_damping | com_x=0.003, linear_damping=0.2 |
| C2032 | 72eb906af12b71e1 | com_x,linear_damping | com_x=0.004, linear_damping=0.1 |
| C2033 | ad70dba6d82ece8b | com_x,angular_damping | com_x=-0.005, angular_damping=0.0 |
| C2034 | 3c8e3506a73da7d5 | com_x,angular_damping | com_x=-0.003, angular_damping=0.1 |
| C2035 | de0dfff0111f45fc | com_x,angular_damping | com_x=-0.002, angular_damping=0.15 |
| C2036 | 178159c9ad0bd346 | com_x,angular_damping | com_x=-0.001, angular_damping=0.2 |
| C2037 | a03448f7d2a36795 | com_x,angular_damping | com_x=0.001, angular_damping=0.3 |
| C2038 | 2ab73c260b61dd83 | com_x,angular_damping | com_x=0.002, angular_damping=0.35 |
| C2039 | eaec9f7eb57682ef | com_x,angular_damping | com_x=0.003, angular_damping=0.4 |
| C2040 | b602861e75b85c7d | com_x,angular_damping | com_x=0.004, angular_damping=0.45 |
| C2041 | 0b9732e8fd6a84d1 | com_x,angular_damping | com_x=0.005, angular_damping=0.5 |
| C2042 | cd6549430618db1d | com_x,angular_damping | com_x=-0.005, angular_damping=0.5 |
| C2043 | 319c140261e59a1f | com_x,angular_damping | com_x=-0.004, angular_damping=0.45 |
| C2044 | 67bf232c86fb3d69 | com_x,angular_damping | com_x=-0.003, angular_damping=0.4 |
| C2045 | 48119cd70c6315fe | com_x,angular_damping | com_x=-0.002, angular_damping=0.35 |
| C2046 | dd8398032e5587ec | com_x,angular_damping | com_x=-0.001, angular_damping=0.3 |
| C2047 | 27fe9eca922c41d6 | com_x,angular_damping | com_x=0.001, angular_damping=0.2 |
| C2048 | 00e68d6766a4ea71 | com_x,angular_damping | com_x=0.002, angular_damping=0.15 |
| C2049 | 36898517c91bd1db | com_x,angular_damping | com_x=0.003, angular_damping=0.1 |
| C2050 | 19335076421f6aa9 | com_x,angular_damping | com_x=0.005, angular_damping=0.0 |
| C2051 | e42b954e91af77a0 | com_x,spawn_x | com_x=-0.005, spawn_x=-0.04 |
| C2052 | aca12cd3b316ff30 | com_x,spawn_x | com_x=-0.004, spawn_x=-0.032 |
| C2053 | 8164f14d6c22ff41 | com_x,spawn_x | com_x=-0.003, spawn_x=-0.024 |
| C2054 | 96250a1872db31d1 | com_x,spawn_x | com_x=-0.002, spawn_x=-0.016 |
| C2055 | 057798616e206e33 | com_x,spawn_x | com_x=-0.001, spawn_x=-0.008 |
| C2056 | 97e7647286d26c79 | com_x,spawn_x | com_x=0.001, spawn_x=0.008 |
| C2057 | a5e9e9614e2cfc72 | com_x,spawn_x | com_x=0.002, spawn_x=0.016 |
| C2058 | ab9bf8296d7981ac | com_x,spawn_x | com_x=0.003, spawn_x=0.024 |
| C2059 | ac120a8ff5d44356 | com_x,spawn_x | com_x=0.004, spawn_x=0.032 |
| C2060 | edc8a482e0aa1254 | com_x,spawn_x | com_x=0.005, spawn_x=0.04 |
| C2061 | 7bd18311ffa4f20e | com_x,spawn_x | com_x=-0.005, spawn_x=0.04 |
| C2062 | 951816e960779dbd | com_x,spawn_x | com_x=-0.004, spawn_x=0.032 |
| C2063 | 10495bc1cc64b8e5 | com_x,spawn_x | com_x=-0.003, spawn_x=0.024 |
| C2064 | b51e0e680a6f91b5 | com_x,spawn_x | com_x=-0.002, spawn_x=0.016 |
| C2065 | 716b088b86ce9670 | com_x,spawn_x | com_x=-0.001, spawn_x=0.008 |
| C2066 | c3e7ec5ae15085b8 | com_x,spawn_x | com_x=0.001, spawn_x=-0.008 |
| C2067 | be30d12ebf2deae1 | com_x,spawn_x | com_x=0.002, spawn_x=-0.016 |
| C2068 | f3cea0ca70a9abd3 | com_x,spawn_x | com_x=0.003, spawn_x=-0.024 |
| C2069 | abc45ce58f92b65c | com_x,spawn_x | com_x=0.004, spawn_x=-0.032 |
| C2070 | 2694e22a808a8043 | com_x,spawn_x | com_x=0.005, spawn_x=-0.04 |
| C2071 | 04ec0cca877fc40a | com_x,spawn_y | com_x=-0.005, spawn_y=-0.04 |
| C2072 | b5b83cb73fc6e63d | com_x,spawn_y | com_x=-0.004, spawn_y=-0.032 |
| C2073 | 5fa86af80e0ea540 | com_x,spawn_y | com_x=-0.003, spawn_y=-0.024 |
| C2074 | de860cbfcad87bfc | com_x,spawn_y | com_x=-0.002, spawn_y=-0.016 |
| C2075 | ebb46f5fab67a4fa | com_x,spawn_y | com_x=-0.001, spawn_y=-0.008 |
| C2076 | 4da87ad24d9eed52 | com_x,spawn_y | com_x=0.001, spawn_y=0.008 |
| C2077 | 6c8f457e390599a8 | com_x,spawn_y | com_x=0.002, spawn_y=0.016 |
| C2078 | 5bd8d3c0b666e0b1 | com_x,spawn_y | com_x=0.003, spawn_y=0.024 |
| C2079 | b6b72ebffd160904 | com_x,spawn_y | com_x=0.004, spawn_y=0.032 |
| C2080 | cf04723f14d50ed9 | com_x,spawn_y | com_x=0.005, spawn_y=0.04 |
| C2081 | 50051c76c66e38a0 | com_x,spawn_y | com_x=-0.005, spawn_y=0.04 |
| C2082 | 97cc378f7b3da960 | com_x,spawn_y | com_x=-0.004, spawn_y=0.032 |
| C2083 | 76f3dad7e6faddb5 | com_x,spawn_y | com_x=-0.003, spawn_y=0.024 |
| C2084 | 67c87c66bc519e23 | com_x,spawn_y | com_x=-0.002, spawn_y=0.016 |
| C2085 | 268abb0f24d8335f | com_x,spawn_y | com_x=-0.001, spawn_y=0.008 |
| C2086 | 24e73bf0f1bf4036 | com_x,spawn_y | com_x=0.001, spawn_y=-0.008 |
| C2087 | 742410a68edc47e5 | com_x,spawn_y | com_x=0.002, spawn_y=-0.016 |
| C2088 | 68cabde45e8d1a63 | com_x,spawn_y | com_x=0.003, spawn_y=-0.024 |
| C2089 | 76a9d86d8da1dcfd | com_x,spawn_y | com_x=0.004, spawn_y=-0.032 |
| C2090 | 5d4ed3ab6877adf7 | com_x,spawn_y | com_x=0.005, spawn_y=-0.04 |
| C2091 | 04a21a17b02bb24d | com_x,spawn_yaw | com_x=-0.005, spawn_yaw=-0.523598775598 |
| C2092 | cf8c1d318971b767 | com_x,spawn_yaw | com_x=-0.004, spawn_yaw=-0.418879020478 |
| C2093 | c9e1b8e67a14a52d | com_x,spawn_yaw | com_x=-0.003, spawn_yaw=-0.314159265359 |
| C2094 | 0af5521599e8bb0b | com_x,spawn_yaw | com_x=-0.002, spawn_yaw=-0.209439510239 |
| C2095 | 6cc7fb6c47612e50 | com_x,spawn_yaw | com_x=-0.001, spawn_yaw=-0.10471975512 |
| C2096 | e292b87030238883 | com_x,spawn_yaw | com_x=0.001, spawn_yaw=0.10471975512 |
| C2097 | 6e14b2fbeb55081c | com_x,spawn_yaw | com_x=0.002, spawn_yaw=0.209439510239 |
| C2098 | f363934553538d3f | com_x,spawn_yaw | com_x=0.003, spawn_yaw=0.314159265359 |
| C2099 | 54f32266bf3326e4 | com_x,spawn_yaw | com_x=0.004, spawn_yaw=0.418879020478 |
| C2100 | fb9bc48eae90d8b6 | com_x,spawn_yaw | com_x=0.005, spawn_yaw=0.523598775598 |
| C2101 | 71d17b972aa88de2 | com_x,spawn_yaw | com_x=-0.005, spawn_yaw=0.523598775598 |
| C2102 | 7c05818d65ed6d7a | com_x,spawn_yaw | com_x=-0.004, spawn_yaw=0.418879020478 |
| C2103 | 8eee596d5b86ba21 | com_x,spawn_yaw | com_x=-0.003, spawn_yaw=0.314159265359 |
| C2104 | 3d4dbf1f72f2942c | com_x,spawn_yaw | com_x=-0.002, spawn_yaw=0.209439510239 |
| C2105 | 98bbdbbd2666db0a | com_x,spawn_yaw | com_x=-0.001, spawn_yaw=0.10471975512 |
| C2106 | bf6fc8ecf2ca1594 | com_x,spawn_yaw | com_x=0.001, spawn_yaw=-0.10471975512 |
| C2107 | 59ad7fc5e2ad3fc8 | com_x,spawn_yaw | com_x=0.002, spawn_yaw=-0.209439510239 |
| C2108 | 4df6fc7082229669 | com_x,spawn_yaw | com_x=0.003, spawn_yaw=-0.314159265359 |
| C2109 | dd027059e668af6d | com_x,spawn_yaw | com_x=0.004, spawn_yaw=-0.418879020478 |
| C2110 | f1124968aa5777af | com_x,spawn_yaw | com_x=0.005, spawn_yaw=-0.523598775598 |
| C2111 | d1998eeb32d11b1a | com_x,inertia_scale | com_x=-0.005, inertia_scale=0.5 |
| C2112 | 98e16d2196ea4160 | com_x,inertia_scale | com_x=-0.004, inertia_scale=0.65 |
| C2113 | 768a56ee9e41be1f | com_x,inertia_scale | com_x=-0.003, inertia_scale=0.8 |
| C2114 | 4ece3ec5e2eb51a4 | com_x,inertia_scale | com_x=-0.002, inertia_scale=0.95 |
| C2115 | cfba935709d79cf7 | com_x,inertia_scale | com_x=-0.001, inertia_scale=1.1 |
| C2116 | 6767c4990e782210 | com_x,inertia_scale | com_x=0.001, inertia_scale=1.4 |
| C2117 | ca15d17b8ce2b9c1 | com_x,inertia_scale | com_x=0.002, inertia_scale=1.55 |
| C2118 | e12ab6cfae432ee8 | com_x,inertia_scale | com_x=0.003, inertia_scale=1.7 |
| C2119 | 6c19b008e8d663d5 | com_x,inertia_scale | com_x=0.004, inertia_scale=1.85 |
| C2120 | 3e1f57fe5d9fc8b9 | com_x,inertia_scale | com_x=0.005, inertia_scale=2.0 |
| C2121 | b6519e092fce28c1 | com_x,inertia_scale | com_x=-0.005, inertia_scale=2.0 |
| C2122 | 98aac437ad9e01dc | com_x,inertia_scale | com_x=-0.004, inertia_scale=1.85 |
| C2123 | 07d51ac516be9f9d | com_x,inertia_scale | com_x=-0.003, inertia_scale=1.7 |
| C2124 | d396d7ad8ff00cba | com_x,inertia_scale | com_x=-0.002, inertia_scale=1.55 |
| C2125 | 9e956256f9e2af14 | com_x,inertia_scale | com_x=-0.001, inertia_scale=1.4 |
| C2126 | e4501ab52e8cf02a | com_x,inertia_scale | com_x=0.001, inertia_scale=1.1 |
| C2127 | 0975f1099a489ef1 | com_x,inertia_scale | com_x=0.002, inertia_scale=0.95 |
| C2128 | d6aa6ee6d96bc401 | com_x,inertia_scale | com_x=0.003, inertia_scale=0.8 |
| C2129 | 302cdfadff91a615 | com_x,inertia_scale | com_x=0.004, inertia_scale=0.65 |
| C2130 | 2b901f7972d5aa68 | com_x,inertia_scale | com_x=0.005, inertia_scale=0.5 |
| C2131 | 90c32fbca75cba5e | com_y,com_z | com_y=-0.005, com_z=-0.005 |
| C2132 | bfc968f3673e8604 | com_y,com_z | com_y=-0.004, com_z=-0.004 |
| C2133 | fa7ea419e327ddff | com_y,com_z | com_y=-0.003, com_z=-0.003 |
| C2134 | f9821b9467e239cc | com_y,com_z | com_y=-0.002, com_z=-0.002 |
| C2135 | bd71d294fe518ecd | com_y,com_z | com_y=-0.001, com_z=-0.001 |
| C2136 | 57c7b33eedbf3ce1 | com_y,com_z | com_y=0.001, com_z=0.001 |
| C2137 | def6e12d67286cae | com_y,com_z | com_y=0.002, com_z=0.002 |
| C2138 | 5e01fbb2c7ea8485 | com_y,com_z | com_y=0.003, com_z=0.003 |
| C2139 | ef2ed0c3f0706261 | com_y,com_z | com_y=0.004, com_z=0.004 |
| C2140 | 0775a660eb13a42a | com_y,com_z | com_y=0.005, com_z=0.005 |
| C2141 | dcac6dd48b629364 | com_y,com_z | com_y=-0.005, com_z=0.005 |
| C2142 | 01d5c9b9ad9bb2ff | com_y,com_z | com_y=-0.004, com_z=0.004 |
| C2143 | a3cd937050a89972 | com_y,com_z | com_y=-0.003, com_z=0.003 |
| C2144 | 6ab50188124cd493 | com_y,com_z | com_y=-0.002, com_z=0.002 |
| C2145 | 10a39b390df3218a | com_y,com_z | com_y=-0.001, com_z=0.001 |
| C2146 | e1f3ad639d50b97f | com_y,com_z | com_y=0.001, com_z=-0.001 |
| C2147 | 4c1ec0f74bec80af | com_y,com_z | com_y=0.002, com_z=-0.002 |
| C2148 | d3187d9ef1a89c6a | com_y,com_z | com_y=0.003, com_z=-0.003 |
| C2149 | cdf07e37dd2cca5f | com_y,com_z | com_y=0.004, com_z=-0.004 |
| C2150 | 0a87336bcee56f4e | com_y,com_z | com_y=0.005, com_z=-0.005 |
| C2151 | eacdd23b55753174 | com_y,goal_height | com_y=-0.005, goal_height=0.1 |
| C2152 | 8a2a4bedc88f88bb | com_y,goal_height | com_y=-0.004, goal_height=0.12 |
| C2153 | d5b7b60ee0ee0550 | com_y,goal_height | com_y=-0.003, goal_height=0.14 |
| C2154 | 8437922bd8b1dcf2 | com_y,goal_height | com_y=-0.002, goal_height=0.16 |
| C2155 | 6e0ded9163c670a8 | com_y,goal_height | com_y=-0.001, goal_height=0.18 |
| C2156 | b2fe59a37670a9bf | com_y,goal_height | com_y=0.001, goal_height=0.22 |
| C2157 | 450da8359b5f1796 | com_y,goal_height | com_y=0.002, goal_height=0.24 |
| C2158 | 612514465a890a6e | com_y,goal_height | com_y=0.003, goal_height=0.26 |
| C2159 | 5c9fba37d9f3776b | com_y,goal_height | com_y=0.004, goal_height=0.28 |
| C2160 | 6d86301638acfe1f | com_y,goal_height | com_y=0.005, goal_height=0.3 |
| C2161 | 3383542a6fd7ecf2 | com_y,goal_height | com_y=-0.005, goal_height=0.3 |
| C2162 | a7e463a6b305a654 | com_y,goal_height | com_y=-0.004, goal_height=0.28 |
| C2163 | a969443eb1770367 | com_y,goal_height | com_y=-0.003, goal_height=0.26 |
| C2164 | c25ef4163ad4a1f3 | com_y,goal_height | com_y=-0.002, goal_height=0.24 |
| C2165 | e5afdd0104eaaf75 | com_y,goal_height | com_y=-0.001, goal_height=0.22 |
| C2166 | c5b0ccf9121c8a26 | com_y,goal_height | com_y=0.001, goal_height=0.18 |
| C2167 | 50b24ec74cad5b8c | com_y,goal_height | com_y=0.002, goal_height=0.16 |
| C2168 | d000804869aadc4e | com_y,goal_height | com_y=0.003, goal_height=0.14 |
| C2169 | 8b2e2c94ab020fc7 | com_y,goal_height | com_y=0.004, goal_height=0.12 |
| C2170 | 11f8297d8845eb90 | com_y,goal_height | com_y=0.005, goal_height=0.1 |
| C2171 | 00f4b5b3dad6050b | com_y,restitution | com_y=-0.004, restitution=0.05 |
| C2172 | d20b17fb68f63fce | com_y,restitution | com_y=-0.003, restitution=0.1 |
| C2173 | 354c2da3bc995b44 | com_y,restitution | com_y=-0.002, restitution=0.15 |
| C2174 | 9fdede9836113d7a | com_y,restitution | com_y=-0.001, restitution=0.2 |
| C2175 | c14ff83a69e324f6 | com_y,restitution | com_y=0.001, restitution=0.3 |
| C2176 | a09503822d18f1d2 | com_y,restitution | com_y=0.002, restitution=0.35 |
| C2177 | 9b7371f0c608c091 | com_y,restitution | com_y=0.003, restitution=0.4 |
| C2178 | 97dd2d8ff284dfb3 | com_y,restitution | com_y=0.004, restitution=0.45 |
| C2179 | 7a066bac8dae63e0 | com_y,restitution | com_y=0.005, restitution=0.5 |
| C2180 | 579b9d483499383a | com_y,restitution | com_y=-0.005, restitution=0.5 |
| C2181 | f6e0fd6c146d1c87 | com_y,restitution | com_y=-0.004, restitution=0.45 |
| C2182 | 47fee27d85ce5f53 | com_y,restitution | com_y=-0.003, restitution=0.4 |
| C2183 | ab44634d3718e70d | com_y,restitution | com_y=-0.002, restitution=0.35 |
| C2184 | cd07fb51ce16ed75 | com_y,restitution | com_y=-0.001, restitution=0.3 |
| C2185 | c4e37f5aeb69e882 | com_y,restitution | com_y=0.001, restitution=0.2 |
| C2186 | a8a673e093546799 | com_y,restitution | com_y=0.002, restitution=0.15 |
| C2187 | 919fd2b0eb8c6403 | com_y,restitution | com_y=0.003, restitution=0.1 |
| C2188 | 08f4ca900d3248f6 | com_y,restitution | com_y=0.004, restitution=0.05 |
| C2189 | e27b67913f693d39 | com_y,linear_damping | com_y=-0.004, linear_damping=0.1 |
| C2190 | 2a390076472b5b7f | com_y,linear_damping | com_y=-0.003, linear_damping=0.2 |
| C2191 | eb4669858d342297 | com_y,linear_damping | com_y=-0.002, linear_damping=0.3 |
| C2192 | 046ca973754f2d01 | com_y,linear_damping | com_y=-0.001, linear_damping=0.4 |
| C2193 | 5a7ebd7556919e7c | com_y,linear_damping | com_y=0.001, linear_damping=0.6 |
| C2194 | 43686d75c74efaa2 | com_y,linear_damping | com_y=0.002, linear_damping=0.7 |
| C2195 | e1c7ffd2eb217fe6 | com_y,linear_damping | com_y=0.003, linear_damping=0.8 |
| C2196 | 26ac5aa3634ffd0a | com_y,linear_damping | com_y=0.004, linear_damping=0.9 |
| C2197 | 256f4ef1c59ae746 | com_y,linear_damping | com_y=0.005, linear_damping=1.0 |
| C2198 | 0f5633a196089ccb | com_y,linear_damping | com_y=-0.005, linear_damping=1.0 |
| C2199 | 347bbaac01254a80 | com_y,linear_damping | com_y=-0.004, linear_damping=0.9 |
| C2200 | 23a7b740b226d66d | com_y,linear_damping | com_y=-0.003, linear_damping=0.8 |
| C2201 | 31934a9c558e954c | com_y,linear_damping | com_y=-0.002, linear_damping=0.7 |
| C2202 | f612cfdb063e1fcc | com_y,linear_damping | com_y=-0.001, linear_damping=0.6 |
| C2203 | aad8eaf537b8d6c7 | com_y,linear_damping | com_y=0.001, linear_damping=0.4 |
| C2204 | a960d2b13303279c | com_y,linear_damping | com_y=0.002, linear_damping=0.3 |
| C2205 | 35e5e07d99a33d77 | com_y,linear_damping | com_y=0.003, linear_damping=0.2 |
| C2206 | 773cdf639032b833 | com_y,linear_damping | com_y=0.004, linear_damping=0.1 |
| C2207 | d1541559b2fda8f7 | com_y,angular_damping | com_y=-0.005, angular_damping=0.0 |
| C2208 | 88ef9d902568f7a7 | com_y,angular_damping | com_y=-0.003, angular_damping=0.1 |
| C2209 | 1def9d051be5a413 | com_y,angular_damping | com_y=-0.002, angular_damping=0.15 |
| C2210 | 48d6765516ead732 | com_y,angular_damping | com_y=-0.001, angular_damping=0.2 |
| C2211 | 8ed358d3819c768f | com_y,angular_damping | com_y=0.001, angular_damping=0.3 |
| C2212 | d1cdd6d662096c48 | com_y,angular_damping | com_y=0.002, angular_damping=0.35 |
| C2213 | 4d0a569687240c46 | com_y,angular_damping | com_y=0.003, angular_damping=0.4 |
| C2214 | f1a570f4bd12c550 | com_y,angular_damping | com_y=0.004, angular_damping=0.45 |
| C2215 | 5c0a980c992ccba2 | com_y,angular_damping | com_y=0.005, angular_damping=0.5 |
| C2216 | 11354d3f3bf0e4e7 | com_y,angular_damping | com_y=-0.005, angular_damping=0.5 |
| C2217 | 945b6943ab4bbad0 | com_y,angular_damping | com_y=-0.004, angular_damping=0.45 |
| C2218 | 959cd8147e25c0d2 | com_y,angular_damping | com_y=-0.003, angular_damping=0.4 |
| C2219 | f6c7edea1beb393e | com_y,angular_damping | com_y=-0.002, angular_damping=0.35 |
| C2220 | c0c005fa3747c908 | com_y,angular_damping | com_y=-0.001, angular_damping=0.3 |
| C2221 | 80340f942a05767d | com_y,angular_damping | com_y=0.001, angular_damping=0.2 |
| C2222 | 98488ea833a6c8af | com_y,angular_damping | com_y=0.002, angular_damping=0.15 |
| C2223 | 57b40b7326403750 | com_y,angular_damping | com_y=0.003, angular_damping=0.1 |
| C2224 | 45ded1a6800b723b | com_y,angular_damping | com_y=0.005, angular_damping=0.0 |
| C2225 | e7b5c0735aa6e4d0 | com_y,spawn_x | com_y=-0.005, spawn_x=-0.04 |
| C2226 | a51d0dc4b47c9d86 | com_y,spawn_x | com_y=-0.004, spawn_x=-0.032 |
| C2227 | 638dc3654062e038 | com_y,spawn_x | com_y=-0.003, spawn_x=-0.024 |
| C2228 | c6b930dc67379ff9 | com_y,spawn_x | com_y=-0.002, spawn_x=-0.016 |
| C2229 | ce51e9763668efa9 | com_y,spawn_x | com_y=-0.001, spawn_x=-0.008 |
| C2230 | 00478a9a3a6f860b | com_y,spawn_x | com_y=0.001, spawn_x=0.008 |
| C2231 | 2b629a3f3a2e71cd | com_y,spawn_x | com_y=0.002, spawn_x=0.016 |
| C2232 | 0ca4718859a9eade | com_y,spawn_x | com_y=0.003, spawn_x=0.024 |
| C2233 | 2e6985f34004df14 | com_y,spawn_x | com_y=0.004, spawn_x=0.032 |
| C2234 | 91b8cd102831ed46 | com_y,spawn_x | com_y=0.005, spawn_x=0.04 |
| C2235 | 14d7d17ce1d6470c | com_y,spawn_x | com_y=-0.005, spawn_x=0.04 |
| C2236 | 0f94655b3510cd13 | com_y,spawn_x | com_y=-0.004, spawn_x=0.032 |
| C2237 | b20b3be7fda91e81 | com_y,spawn_x | com_y=-0.003, spawn_x=0.024 |
| C2238 | f7a025418b8ea665 | com_y,spawn_x | com_y=-0.002, spawn_x=0.016 |
| C2239 | 529021847f295516 | com_y,spawn_x | com_y=-0.001, spawn_x=0.008 |
| C2240 | 17b3cbefeb71a305 | com_y,spawn_x | com_y=0.001, spawn_x=-0.008 |
| C2241 | f419d46e331de315 | com_y,spawn_x | com_y=0.002, spawn_x=-0.016 |
| C2242 | 10d5f507f40a3e39 | com_y,spawn_x | com_y=0.003, spawn_x=-0.024 |
| C2243 | fb5b10096f57e3b4 | com_y,spawn_x | com_y=0.004, spawn_x=-0.032 |
| C2244 | d4272df2b45678e0 | com_y,spawn_x | com_y=0.005, spawn_x=-0.04 |
| C2245 | 86dc730548bb1a6a | com_y,spawn_y | com_y=-0.005, spawn_y=-0.04 |
| C2246 | abc77478f4ef22d8 | com_y,spawn_y | com_y=-0.004, spawn_y=-0.032 |
| C2247 | c8d8f59129621692 | com_y,spawn_y | com_y=-0.003, spawn_y=-0.024 |
| C2248 | 55bbbfa8e5c1d703 | com_y,spawn_y | com_y=-0.002, spawn_y=-0.016 |
| C2249 | 22b13a620a03c45f | com_y,spawn_y | com_y=-0.001, spawn_y=-0.008 |
| C2250 | 64bf53d7b9102f24 | com_y,spawn_y | com_y=0.001, spawn_y=0.008 |
| C2251 | 8b016ddb266a086c | com_y,spawn_y | com_y=0.002, spawn_y=0.016 |
| C2252 | e9cf44479dcf2264 | com_y,spawn_y | com_y=0.003, spawn_y=0.024 |
| C2253 | 188758b94c8e3760 | com_y,spawn_y | com_y=0.004, spawn_y=0.032 |
| C2254 | 539fa52994597212 | com_y,spawn_y | com_y=0.005, spawn_y=0.04 |
| C2255 | cb804f9bb720177b | com_y,spawn_y | com_y=-0.005, spawn_y=0.04 |
| C2256 | 5efc78dc14bae938 | com_y,spawn_y | com_y=-0.004, spawn_y=0.032 |
| C2257 | 18d08afee41b5dc3 | com_y,spawn_y | com_y=-0.003, spawn_y=0.024 |
| C2258 | e4da8280225eca2a | com_y,spawn_y | com_y=-0.002, spawn_y=0.016 |
| C2259 | dd83d33f087428e1 | com_y,spawn_y | com_y=-0.001, spawn_y=0.008 |
| C2260 | 5c8695374c441144 | com_y,spawn_y | com_y=0.001, spawn_y=-0.008 |
| C2261 | 65b99c717bad7cec | com_y,spawn_y | com_y=0.002, spawn_y=-0.016 |
| C2262 | 28c2d0f2a5a2c0f9 | com_y,spawn_y | com_y=0.003, spawn_y=-0.024 |
| C2263 | f6dae9ebb9ebf885 | com_y,spawn_y | com_y=0.004, spawn_y=-0.032 |
| C2264 | eda5c4bcf1dadd88 | com_y,spawn_y | com_y=0.005, spawn_y=-0.04 |
| C2265 | b33cb06cf779902a | com_y,spawn_yaw | com_y=-0.005, spawn_yaw=-0.523598775598 |
| C2266 | a729795765082dfb | com_y,spawn_yaw | com_y=-0.004, spawn_yaw=-0.418879020478 |
| C2267 | e3e857b3e1ead39c | com_y,spawn_yaw | com_y=-0.003, spawn_yaw=-0.314159265359 |
| C2268 | 61e31f43062286c9 | com_y,spawn_yaw | com_y=-0.002, spawn_yaw=-0.209439510239 |
| C2269 | 33bac1e4c6ec7a04 | com_y,spawn_yaw | com_y=-0.001, spawn_yaw=-0.10471975512 |
| C2270 | 1732bcba6143fd74 | com_y,spawn_yaw | com_y=0.001, spawn_yaw=0.10471975512 |
| C2271 | 49dbe44ec7d23a68 | com_y,spawn_yaw | com_y=0.002, spawn_yaw=0.209439510239 |
| C2272 | c69d3fe453c22879 | com_y,spawn_yaw | com_y=0.003, spawn_yaw=0.314159265359 |
| C2273 | 8b27be2de0c511cd | com_y,spawn_yaw | com_y=0.004, spawn_yaw=0.418879020478 |
| C2274 | 14944b2b50f8b1bd | com_y,spawn_yaw | com_y=0.005, spawn_yaw=0.523598775598 |
| C2275 | 9be4e1a7e706307b | com_y,spawn_yaw | com_y=-0.005, spawn_yaw=0.523598775598 |
| C2276 | 5c39a353272c94cb | com_y,spawn_yaw | com_y=-0.004, spawn_yaw=0.418879020478 |
| C2277 | b36baef3fd68532e | com_y,spawn_yaw | com_y=-0.003, spawn_yaw=0.314159265359 |
| C2278 | 593aaea9479e96ca | com_y,spawn_yaw | com_y=-0.002, spawn_yaw=0.209439510239 |
| C2279 | af3eb727a2c84cc0 | com_y,spawn_yaw | com_y=-0.001, spawn_yaw=0.10471975512 |
| C2280 | bc75e6b2a26de315 | com_y,spawn_yaw | com_y=0.001, spawn_yaw=-0.10471975512 |
| C2281 | e9ecf490e70d1fd7 | com_y,spawn_yaw | com_y=0.002, spawn_yaw=-0.209439510239 |
| C2282 | 3d302bbfeaaeba77 | com_y,spawn_yaw | com_y=0.003, spawn_yaw=-0.314159265359 |
| C2283 | af072fa9a4072a66 | com_y,spawn_yaw | com_y=0.004, spawn_yaw=-0.418879020478 |
| C2284 | 90d947b166e94e85 | com_y,spawn_yaw | com_y=0.005, spawn_yaw=-0.523598775598 |
| C2285 | b9145932b79923ec | com_y,inertia_scale | com_y=-0.005, inertia_scale=0.5 |
| C2286 | fbfe7ef7e4cf7703 | com_y,inertia_scale | com_y=-0.004, inertia_scale=0.65 |
| C2287 | 1661930d34bf2133 | com_y,inertia_scale | com_y=-0.003, inertia_scale=0.8 |
| C2288 | 992ace468359068d | com_y,inertia_scale | com_y=-0.002, inertia_scale=0.95 |
| C2289 | b0b2a57b8ed78e6e | com_y,inertia_scale | com_y=-0.001, inertia_scale=1.1 |
| C2290 | 64882c24889374ff | com_y,inertia_scale | com_y=0.001, inertia_scale=1.4 |
| C2291 | 647d7124dbd7fc76 | com_y,inertia_scale | com_y=0.002, inertia_scale=1.55 |
| C2292 | 5ac458701bde6c2a | com_y,inertia_scale | com_y=0.003, inertia_scale=1.7 |
| C2293 | 56efaf4c387377f3 | com_y,inertia_scale | com_y=0.004, inertia_scale=1.85 |
| C2294 | 688fc8c942cc3089 | com_y,inertia_scale | com_y=0.005, inertia_scale=2.0 |
| C2295 | d9a3d61ade17660f | com_y,inertia_scale | com_y=-0.005, inertia_scale=2.0 |
| C2296 | bfa3469c2b684078 | com_y,inertia_scale | com_y=-0.004, inertia_scale=1.85 |
| C2297 | bda0088a5816df58 | com_y,inertia_scale | com_y=-0.003, inertia_scale=1.7 |
| C2298 | 9dda1de5f7afd274 | com_y,inertia_scale | com_y=-0.002, inertia_scale=1.55 |
| C2299 | 2b5d0512789a6aa0 | com_y,inertia_scale | com_y=-0.001, inertia_scale=1.4 |
| C2300 | ac45dc0ae1673d19 | com_y,inertia_scale | com_y=0.001, inertia_scale=1.1 |
| C2301 | e0ec016dd2fb6e50 | com_y,inertia_scale | com_y=0.002, inertia_scale=0.95 |
| C2302 | b2c6e5a52f009400 | com_y,inertia_scale | com_y=0.003, inertia_scale=0.8 |
| C2303 | a80ca5bafd5aa2ad | com_y,inertia_scale | com_y=0.004, inertia_scale=0.65 |
| C2304 | 0b5a0f85434afedc | com_y,inertia_scale | com_y=0.005, inertia_scale=0.5 |
| C2305 | a2b3eebaa47a3e21 | com_z,goal_height | com_z=-0.005, goal_height=0.1 |
| C2306 | a3a4ba67c0498c5e | com_z,goal_height | com_z=-0.004, goal_height=0.12 |
| C2307 | ea5cbb5338dc7768 | com_z,goal_height | com_z=-0.003, goal_height=0.14 |
| C2308 | 787c9c6d5c89db6f | com_z,goal_height | com_z=-0.002, goal_height=0.16 |
| C2309 | 20529e1584acfdd7 | com_z,goal_height | com_z=-0.001, goal_height=0.18 |
| C2310 | a4b72611e63bb7b6 | com_z,goal_height | com_z=0.001, goal_height=0.22 |
| C2311 | ced86e575566dbfc | com_z,goal_height | com_z=0.002, goal_height=0.24 |
| C2312 | 482fd5fce44d1e9c | com_z,goal_height | com_z=0.003, goal_height=0.26 |
| C2313 | d100a5939a880415 | com_z,goal_height | com_z=0.004, goal_height=0.28 |
| C2314 | ee2d6639a7c2426e | com_z,goal_height | com_z=0.005, goal_height=0.3 |
| C2315 | 29092dce484d66cc | com_z,goal_height | com_z=-0.005, goal_height=0.3 |
| C2316 | adc9481f9b5910a8 | com_z,goal_height | com_z=-0.004, goal_height=0.28 |
| C2317 | 734cc6dbb7c23f8f | com_z,goal_height | com_z=-0.003, goal_height=0.26 |
| C2318 | 80f58ab4b233fe56 | com_z,goal_height | com_z=-0.002, goal_height=0.24 |
| C2319 | 0bf5c7ba834b4e16 | com_z,goal_height | com_z=-0.001, goal_height=0.22 |
| C2320 | 530740bc40fce65f | com_z,goal_height | com_z=0.001, goal_height=0.18 |
| C2321 | 7d12cc49490e8619 | com_z,goal_height | com_z=0.002, goal_height=0.16 |
| C2322 | 274248c2d00fc61d | com_z,goal_height | com_z=0.003, goal_height=0.14 |
| C2323 | 14fe9d567c60b98f | com_z,goal_height | com_z=0.004, goal_height=0.12 |
| C2324 | e8d0a31e5d722e4c | com_z,goal_height | com_z=0.005, goal_height=0.1 |
| C2325 | 265ea5ff7e670fbe | com_z,restitution | com_z=-0.004, restitution=0.05 |
| C2326 | 7541bd8b042ff7bc | com_z,restitution | com_z=-0.003, restitution=0.1 |
| C2327 | 4a3a4e6d4d844765 | com_z,restitution | com_z=-0.002, restitution=0.15 |
| C2328 | 6ccdf5366f60f42d | com_z,restitution | com_z=-0.001, restitution=0.2 |
| C2329 | 253f9abc8c524616 | com_z,restitution | com_z=0.001, restitution=0.3 |
| C2330 | dd06aac1c4c54baf | com_z,restitution | com_z=0.002, restitution=0.35 |
| C2331 | 3b8e1a0316d4297d | com_z,restitution | com_z=0.003, restitution=0.4 |
| C2332 | 69b6d3af434e3883 | com_z,restitution | com_z=0.004, restitution=0.45 |
| C2333 | 5604c399c8735b9b | com_z,restitution | com_z=0.005, restitution=0.5 |
| C2334 | 31b87f40051554a9 | com_z,restitution | com_z=-0.005, restitution=0.5 |
| C2335 | de2040e0a68fbeb4 | com_z,restitution | com_z=-0.004, restitution=0.45 |
| C2336 | abd7ea857a0f7382 | com_z,restitution | com_z=-0.003, restitution=0.4 |
| C2337 | be0cc47d20e168bd | com_z,restitution | com_z=-0.002, restitution=0.35 |
| C2338 | ca055a511f2c3093 | com_z,restitution | com_z=-0.001, restitution=0.3 |
| C2339 | 9a04463e7a4d2889 | com_z,restitution | com_z=0.001, restitution=0.2 |
| C2340 | b7b8d602bc3c28ff | com_z,restitution | com_z=0.002, restitution=0.15 |
| C2341 | c80af6c1aa58455f | com_z,restitution | com_z=0.003, restitution=0.1 |
| C2342 | cc275267bb6b3a1e | com_z,restitution | com_z=0.004, restitution=0.05 |
| C2343 | ab8ff8274c78b536 | com_z,linear_damping | com_z=-0.004, linear_damping=0.1 |
| C2344 | 53dcbc7fda0a5fc0 | com_z,linear_damping | com_z=-0.003, linear_damping=0.2 |
| C2345 | 97259ae727849c06 | com_z,linear_damping | com_z=-0.002, linear_damping=0.3 |
| C2346 | f3545237d2db3629 | com_z,linear_damping | com_z=-0.001, linear_damping=0.4 |
| C2347 | 9b901a9efc096f26 | com_z,linear_damping | com_z=0.001, linear_damping=0.6 |
| C2348 | 98bbd436993746c1 | com_z,linear_damping | com_z=0.002, linear_damping=0.7 |
| C2349 | 24f9677129968b10 | com_z,linear_damping | com_z=0.003, linear_damping=0.8 |
| C2350 | be4010779eae68ca | com_z,linear_damping | com_z=0.004, linear_damping=0.9 |
| C2351 | 0fdf3777f4416a55 | com_z,linear_damping | com_z=0.005, linear_damping=1.0 |
| C2352 | c7febe41afae76b5 | com_z,linear_damping | com_z=-0.005, linear_damping=1.0 |
| C2353 | 18a2f5f5b5ba92d6 | com_z,linear_damping | com_z=-0.004, linear_damping=0.9 |
| C2354 | 707423f8fa9cd69b | com_z,linear_damping | com_z=-0.003, linear_damping=0.8 |
| C2355 | e194ffe639cf51f1 | com_z,linear_damping | com_z=-0.002, linear_damping=0.7 |
| C2356 | 1826a3fbb65c336b | com_z,linear_damping | com_z=-0.001, linear_damping=0.6 |
| C2357 | 0cc029900797abed | com_z,linear_damping | com_z=0.001, linear_damping=0.4 |
| C2358 | fcac8a3afbaadcd2 | com_z,linear_damping | com_z=0.002, linear_damping=0.3 |
| C2359 | 480dea804c6d9e26 | com_z,linear_damping | com_z=0.003, linear_damping=0.2 |
| C2360 | 4e9204a284167dd3 | com_z,linear_damping | com_z=0.004, linear_damping=0.1 |
| C2361 | 3638ce435b2f742e | com_z,angular_damping | com_z=-0.005, angular_damping=0.0 |
| C2362 | 226d19cc07cdf394 | com_z,angular_damping | com_z=-0.003, angular_damping=0.1 |
| C2363 | 033bf03c046251d2 | com_z,angular_damping | com_z=-0.002, angular_damping=0.15 |
| C2364 | 77dc91320d392934 | com_z,angular_damping | com_z=-0.001, angular_damping=0.2 |
| C2365 | b0492d2f8211addc | com_z,angular_damping | com_z=0.001, angular_damping=0.3 |
| C2366 | a3f8bc4d4744546b | com_z,angular_damping | com_z=0.002, angular_damping=0.35 |
| C2367 | 60fc5929998020e7 | com_z,angular_damping | com_z=0.003, angular_damping=0.4 |
| C2368 | 6e155ec88587185f | com_z,angular_damping | com_z=0.004, angular_damping=0.45 |
| C2369 | 0d3d8a680856e7ed | com_z,angular_damping | com_z=0.005, angular_damping=0.5 |
| C2370 | fac366e2f191a621 | com_z,angular_damping | com_z=-0.005, angular_damping=0.5 |
| C2371 | 6976f449017d8e9e | com_z,angular_damping | com_z=-0.004, angular_damping=0.45 |
| C2372 | c43b83b62f25aa10 | com_z,angular_damping | com_z=-0.003, angular_damping=0.4 |
| C2373 | ec7cc9f74a712f02 | com_z,angular_damping | com_z=-0.002, angular_damping=0.35 |
| C2374 | ae4b95ced9a9b4c7 | com_z,angular_damping | com_z=-0.001, angular_damping=0.3 |
| C2375 | c879fbba40bd2753 | com_z,angular_damping | com_z=0.001, angular_damping=0.2 |
| C2376 | ea4b960675c8f958 | com_z,angular_damping | com_z=0.002, angular_damping=0.15 |
| C2377 | 659c3d03ec8b0ba6 | com_z,angular_damping | com_z=0.003, angular_damping=0.1 |
| C2378 | 1c357e5bf2d98132 | com_z,angular_damping | com_z=0.005, angular_damping=0.0 |
| C2379 | a9af0bca3c1d04d0 | com_z,spawn_x | com_z=-0.005, spawn_x=-0.04 |
| C2380 | 3990df5ebae0edbf | com_z,spawn_x | com_z=-0.004, spawn_x=-0.032 |
| C2381 | 24ca8cf27d74884a | com_z,spawn_x | com_z=-0.003, spawn_x=-0.024 |
| C2382 | 45182de2e21c0eca | com_z,spawn_x | com_z=-0.002, spawn_x=-0.016 |
| C2383 | 63494a4c049f77fd | com_z,spawn_x | com_z=-0.001, spawn_x=-0.008 |
| C2384 | 5d2894eeedade3fe | com_z,spawn_x | com_z=0.001, spawn_x=0.008 |
| C2385 | 7c61b7e1c4526650 | com_z,spawn_x | com_z=0.002, spawn_x=0.016 |
| C2386 | a4072340f6f15c92 | com_z,spawn_x | com_z=0.003, spawn_x=0.024 |
| C2387 | d3fe545be31d43b7 | com_z,spawn_x | com_z=0.004, spawn_x=0.032 |
| C2388 | fce66739c02dd8b2 | com_z,spawn_x | com_z=0.005, spawn_x=0.04 |
| C2389 | 5c73d378601a9f23 | com_z,spawn_x | com_z=-0.005, spawn_x=0.04 |
| C2390 | b48376471c62b716 | com_z,spawn_x | com_z=-0.004, spawn_x=0.032 |
| C2391 | 26c1d508678cda56 | com_z,spawn_x | com_z=-0.003, spawn_x=0.024 |
| C2392 | 22a9ee73bbd07c16 | com_z,spawn_x | com_z=-0.002, spawn_x=0.016 |
| C2393 | b338b1080a35a0e3 | com_z,spawn_x | com_z=-0.001, spawn_x=0.008 |
| C2394 | 11e547fc6d6329bc | com_z,spawn_x | com_z=0.001, spawn_x=-0.008 |
| C2395 | f9ec5d8e9de40262 | com_z,spawn_x | com_z=0.002, spawn_x=-0.016 |
| C2396 | 4b0a446f7648397b | com_z,spawn_x | com_z=0.003, spawn_x=-0.024 |
| C2397 | 41d50b4322bb0bdf | com_z,spawn_x | com_z=0.004, spawn_x=-0.032 |
| C2398 | 1cfbf9499aa9da49 | com_z,spawn_x | com_z=0.005, spawn_x=-0.04 |
| C2399 | 14b12e599d0b19af | com_z,spawn_y | com_z=-0.005, spawn_y=-0.04 |
| C2400 | 3b2b2dd1b6a82c7b | com_z,spawn_y | com_z=-0.004, spawn_y=-0.032 |
| C2401 | 4e0d58e743f295c0 | com_z,spawn_y | com_z=-0.003, spawn_y=-0.024 |
| C2402 | 604179ef510b20b1 | com_z,spawn_y | com_z=-0.002, spawn_y=-0.016 |
| C2403 | c441ec946a4d7e4a | com_z,spawn_y | com_z=-0.001, spawn_y=-0.008 |
| C2404 | 599a36cb8797b254 | com_z,spawn_y | com_z=0.001, spawn_y=0.008 |
| C2405 | 087f93c6b404fe84 | com_z,spawn_y | com_z=0.002, spawn_y=0.016 |
| C2406 | f89b7d053fbafab2 | com_z,spawn_y | com_z=0.003, spawn_y=0.024 |
| C2407 | 79a028fceb423765 | com_z,spawn_y | com_z=0.004, spawn_y=0.032 |
| C2408 | 29432c34dfbe905f | com_z,spawn_y | com_z=0.005, spawn_y=0.04 |
| C2409 | 2e3679a60772e3b1 | com_z,spawn_y | com_z=-0.005, spawn_y=0.04 |
| C2410 | aa58051cd673aa02 | com_z,spawn_y | com_z=-0.004, spawn_y=0.032 |
| C2411 | 42c5fc56cb951470 | com_z,spawn_y | com_z=-0.003, spawn_y=0.024 |
| C2412 | f6e896049e7c056c | com_z,spawn_y | com_z=-0.002, spawn_y=0.016 |
| C2413 | 5117299a98eafd6b | com_z,spawn_y | com_z=-0.001, spawn_y=0.008 |
| C2414 | 64731329adac075b | com_z,spawn_y | com_z=0.001, spawn_y=-0.008 |
| C2415 | 171c983edb4b407d | com_z,spawn_y | com_z=0.002, spawn_y=-0.016 |
| C2416 | b4dd6fcdcc6e556a | com_z,spawn_y | com_z=0.003, spawn_y=-0.024 |
| C2417 | 8279a44398c8afce | com_z,spawn_y | com_z=0.004, spawn_y=-0.032 |
| C2418 | 9eb6c6b573da6e69 | com_z,spawn_y | com_z=0.005, spawn_y=-0.04 |
| C2419 | 8ecdc1b3fbf29591 | com_z,spawn_yaw | com_z=-0.005, spawn_yaw=-0.523598775598 |
| C2420 | 01fb697772c1cc47 | com_z,spawn_yaw | com_z=-0.004, spawn_yaw=-0.418879020478 |
| C2421 | 4f0a59a3332b7ccc | com_z,spawn_yaw | com_z=-0.003, spawn_yaw=-0.314159265359 |
| C2422 | ce54ef39d8a1796c | com_z,spawn_yaw | com_z=-0.002, spawn_yaw=-0.209439510239 |
| C2423 | 2216bd48db531424 | com_z,spawn_yaw | com_z=-0.001, spawn_yaw=-0.10471975512 |
| C2424 | 823716d63970efed | com_z,spawn_yaw | com_z=0.001, spawn_yaw=0.10471975512 |
| C2425 | 23dc4b105c55d35a | com_z,spawn_yaw | com_z=0.002, spawn_yaw=0.209439510239 |
| C2426 | 10999feef15744b4 | com_z,spawn_yaw | com_z=0.003, spawn_yaw=0.314159265359 |
| C2427 | 3ea5806fa2dc881e | com_z,spawn_yaw | com_z=0.004, spawn_yaw=0.418879020478 |
| C2428 | 47af7b2e5625af63 | com_z,spawn_yaw | com_z=0.005, spawn_yaw=0.523598775598 |
| C2429 | 7116714cb0746cf9 | com_z,spawn_yaw | com_z=-0.005, spawn_yaw=0.523598775598 |
| C2430 | 96bbfd8c5dddc129 | com_z,spawn_yaw | com_z=-0.004, spawn_yaw=0.418879020478 |
| C2431 | 6c303f7364fbdc56 | com_z,spawn_yaw | com_z=-0.003, spawn_yaw=0.314159265359 |
| C2432 | 519f3e6a3f778d26 | com_z,spawn_yaw | com_z=-0.002, spawn_yaw=0.209439510239 |
| C2433 | 20004cc09871fd91 | com_z,spawn_yaw | com_z=-0.001, spawn_yaw=0.10471975512 |
| C2434 | 2ebf6906c2d8b7aa | com_z,spawn_yaw | com_z=0.001, spawn_yaw=-0.10471975512 |
| C2435 | bdd86d6a3f7536b8 | com_z,spawn_yaw | com_z=0.002, spawn_yaw=-0.209439510239 |
| C2436 | 00c88f7f44e7161c | com_z,spawn_yaw | com_z=0.003, spawn_yaw=-0.314159265359 |
| C2437 | 1a727059f155dfc7 | com_z,spawn_yaw | com_z=0.004, spawn_yaw=-0.418879020478 |
| C2438 | ddb7baaff790435f | com_z,spawn_yaw | com_z=0.005, spawn_yaw=-0.523598775598 |
| C2439 | c5703f7a90da07fd | com_z,inertia_scale | com_z=-0.005, inertia_scale=0.5 |
| C2440 | 8cd1e5c6e99724aa | com_z,inertia_scale | com_z=-0.004, inertia_scale=0.65 |
| C2441 | 138724d61bbd903a | com_z,inertia_scale | com_z=-0.003, inertia_scale=0.8 |
| C2442 | 038ef115f05325f5 | com_z,inertia_scale | com_z=-0.002, inertia_scale=0.95 |
| C2443 | 89e80051ce5680c1 | com_z,inertia_scale | com_z=-0.001, inertia_scale=1.1 |
| C2444 | c1b0f1df1287443c | com_z,inertia_scale | com_z=0.001, inertia_scale=1.4 |
| C2445 | 7cc8f6d860594d30 | com_z,inertia_scale | com_z=0.002, inertia_scale=1.55 |
| C2446 | a687bfead6bd8be4 | com_z,inertia_scale | com_z=0.003, inertia_scale=1.7 |
| C2447 | 9497e370291b3330 | com_z,inertia_scale | com_z=0.004, inertia_scale=1.85 |
| C2448 | d2848a3512c4c6fa | com_z,inertia_scale | com_z=0.005, inertia_scale=2.0 |
| C2449 | cf13c0dd05449b21 | com_z,inertia_scale | com_z=-0.005, inertia_scale=2.0 |
| C2450 | 48304c93c5f87670 | com_z,inertia_scale | com_z=-0.004, inertia_scale=1.85 |
| C2451 | 599c22abc9709685 | com_z,inertia_scale | com_z=-0.003, inertia_scale=1.7 |
| C2452 | bf389723f4bcfb16 | com_z,inertia_scale | com_z=-0.002, inertia_scale=1.55 |
| C2453 | 0359151c5c2f69b9 | com_z,inertia_scale | com_z=-0.001, inertia_scale=1.4 |
| C2454 | e79fa6da3bc75f5c | com_z,inertia_scale | com_z=0.001, inertia_scale=1.1 |
| C2455 | 63ebd81436dccf94 | com_z,inertia_scale | com_z=0.002, inertia_scale=0.95 |
| C2456 | 7ece1cbf2ef3b026 | com_z,inertia_scale | com_z=0.003, inertia_scale=0.8 |
| C2457 | 8daa6a39b9db8e1c | com_z,inertia_scale | com_z=0.004, inertia_scale=0.65 |
| C2458 | c4f739205c5f222a | com_z,inertia_scale | com_z=0.005, inertia_scale=0.5 |
| C2459 | adabe296c67456f9 | goal_height,restitution | goal_height=0.12, restitution=0.05 |
| C2460 | 95ea87bb8eb5336a | goal_height,restitution | goal_height=0.14, restitution=0.1 |
| C2461 | b1e2530b2c939d0e | goal_height,restitution | goal_height=0.16, restitution=0.15 |
| C2462 | 14ccf563827b5f99 | goal_height,restitution | goal_height=0.18, restitution=0.2 |
| C2463 | f421129b476dd0dd | goal_height,restitution | goal_height=0.22, restitution=0.3 |
| C2464 | e66d9c0177dd1519 | goal_height,restitution | goal_height=0.24, restitution=0.35 |
| C2465 | 277a2f358b56ffd1 | goal_height,restitution | goal_height=0.26, restitution=0.4 |
| C2466 | 0bc2b84916453fc3 | goal_height,restitution | goal_height=0.28, restitution=0.45 |
| C2467 | 38209adc16e7c51b | goal_height,restitution | goal_height=0.3, restitution=0.5 |
| C2468 | 26c8d3656171c169 | goal_height,restitution | goal_height=0.1, restitution=0.5 |
| C2469 | 5a4fe6b91633e0c0 | goal_height,restitution | goal_height=0.12, restitution=0.45 |
| C2470 | 074bdd6951e94d4a | goal_height,restitution | goal_height=0.14, restitution=0.4 |
| C2471 | ad5f3fa6cb82f9d8 | goal_height,restitution | goal_height=0.16, restitution=0.35 |
| C2472 | baf9661a5fdd42fb | goal_height,restitution | goal_height=0.18, restitution=0.3 |
| C2473 | c597e7a9e37badd8 | goal_height,restitution | goal_height=0.22, restitution=0.2 |
| C2474 | 37da78985bedf7b5 | goal_height,restitution | goal_height=0.24, restitution=0.15 |
| C2475 | 39e76c1d9167cef9 | goal_height,restitution | goal_height=0.26, restitution=0.1 |
| C2476 | b2d39284981b6f38 | goal_height,restitution | goal_height=0.28, restitution=0.05 |
| C2477 | da6532ea4067c41f | goal_height,linear_damping | goal_height=0.12, linear_damping=0.1 |
| C2478 | 3ef2dfa292c301d0 | goal_height,linear_damping | goal_height=0.14, linear_damping=0.2 |
| C2479 | a1b1d4b7dca811e9 | goal_height,linear_damping | goal_height=0.16, linear_damping=0.3 |
| C2480 | 285301d3d2072423 | goal_height,linear_damping | goal_height=0.18, linear_damping=0.4 |
| C2481 | 6ea35fe2bbf7dcaa | goal_height,linear_damping | goal_height=0.22, linear_damping=0.6 |
| C2482 | 996e3e9474814743 | goal_height,linear_damping | goal_height=0.24, linear_damping=0.7 |
| C2483 | 0e363a4b359de98d | goal_height,linear_damping | goal_height=0.26, linear_damping=0.8 |
| C2484 | e8cb2443e1b9a5b1 | goal_height,linear_damping | goal_height=0.28, linear_damping=0.9 |
| C2485 | 07e668054f249749 | goal_height,linear_damping | goal_height=0.3, linear_damping=1.0 |
| C2486 | 682a6ef027839e74 | goal_height,linear_damping | goal_height=0.1, linear_damping=1.0 |
| C2487 | 7f393226ebff3992 | goal_height,linear_damping | goal_height=0.12, linear_damping=0.9 |
| C2488 | d7b4ade977a06128 | goal_height,linear_damping | goal_height=0.14, linear_damping=0.8 |
| C2489 | 294527055eb5c97a | goal_height,linear_damping | goal_height=0.16, linear_damping=0.7 |
| C2490 | e99656ebe80fb0c1 | goal_height,linear_damping | goal_height=0.18, linear_damping=0.6 |
| C2491 | 90a14cd6f92ff3cc | goal_height,linear_damping | goal_height=0.22, linear_damping=0.4 |
| C2492 | 9f368350ceb81265 | goal_height,linear_damping | goal_height=0.24, linear_damping=0.3 |
| C2493 | 17592b4c6cef52f3 | goal_height,linear_damping | goal_height=0.26, linear_damping=0.2 |
| C2494 | 8b305f5af941bc78 | goal_height,linear_damping | goal_height=0.28, linear_damping=0.1 |
| C2495 | 6f64bd78984137c4 | goal_height,angular_damping | goal_height=0.1, angular_damping=0.0 |
| C2496 | a28236b10ea7b6a3 | goal_height,angular_damping | goal_height=0.14, angular_damping=0.1 |
| C2497 | bbe7e5bc2ab8bad8 | goal_height,angular_damping | goal_height=0.16, angular_damping=0.15 |
| C2498 | 32f04d4db20c5f32 | goal_height,angular_damping | goal_height=0.18, angular_damping=0.2 |
| C2499 | 066a47b2dba07972 | goal_height,angular_damping | goal_height=0.22, angular_damping=0.3 |
| C2500 | b11bebad7ed7bb91 | goal_height,angular_damping | goal_height=0.24, angular_damping=0.35 |
| C2501 | a11fb78d7c066b0d | goal_height,angular_damping | goal_height=0.26, angular_damping=0.4 |
| C2502 | e54e4a2ba2e255b3 | goal_height,angular_damping | goal_height=0.28, angular_damping=0.45 |
| C2503 | 34288c5aca19d3cc | goal_height,angular_damping | goal_height=0.3, angular_damping=0.5 |
| C2504 | 6f5e3ca8d4cdff42 | goal_height,angular_damping | goal_height=0.1, angular_damping=0.5 |
| C2505 | c03cce1f5491085e | goal_height,angular_damping | goal_height=0.12, angular_damping=0.45 |
| C2506 | 13dc34d8f0f868a8 | goal_height,angular_damping | goal_height=0.14, angular_damping=0.4 |
| C2507 | ca57ba8a517d6aef | goal_height,angular_damping | goal_height=0.16, angular_damping=0.35 |
| C2508 | 393f514836e3cda1 | goal_height,angular_damping | goal_height=0.18, angular_damping=0.3 |
| C2509 | e899b414b4a3cd2a | goal_height,angular_damping | goal_height=0.22, angular_damping=0.2 |
| C2510 | cf42082be03fc4d6 | goal_height,angular_damping | goal_height=0.24, angular_damping=0.15 |
| C2511 | f9a9e5d7496c58d6 | goal_height,angular_damping | goal_height=0.26, angular_damping=0.1 |
| C2512 | 1744e2544a8f2f7a | goal_height,angular_damping | goal_height=0.3, angular_damping=0.0 |
| C2513 | 5d9aaa811cb58392 | goal_height,spawn_x | goal_height=0.1, spawn_x=-0.04 |
| C2514 | c4af76fbf6a921a9 | goal_height,spawn_x | goal_height=0.12, spawn_x=-0.032 |
| C2515 | 60d5c6ac68fab929 | goal_height,spawn_x | goal_height=0.14, spawn_x=-0.024 |
| C2516 | c5645a9ddba1c95b | goal_height,spawn_x | goal_height=0.16, spawn_x=-0.016 |
| C2517 | e5fb23a2090113dd | goal_height,spawn_x | goal_height=0.18, spawn_x=-0.008 |
| C2518 | b8c9053d6c0c3839 | goal_height,spawn_x | goal_height=0.22, spawn_x=0.008 |
| C2519 | 008d797df21a9e81 | goal_height,spawn_x | goal_height=0.24, spawn_x=0.016 |
| C2520 | 9270da549e1d3694 | goal_height,spawn_x | goal_height=0.26, spawn_x=0.024 |
| C2521 | f61710d22c33ac94 | goal_height,spawn_x | goal_height=0.28, spawn_x=0.032 |
| C2522 | 9a4b14d66a4692e6 | goal_height,spawn_x | goal_height=0.3, spawn_x=0.04 |
| C2523 | 09a13cf5ebe61f53 | goal_height,spawn_x | goal_height=0.1, spawn_x=0.04 |
| C2524 | 7240b22c1fb632aa | goal_height,spawn_x | goal_height=0.12, spawn_x=0.032 |
| C2525 | d61de5fd9aab10b5 | goal_height,spawn_x | goal_height=0.14, spawn_x=0.024 |
| C2526 | 8f840c752651c307 | goal_height,spawn_x | goal_height=0.16, spawn_x=0.016 |
| C2527 | 6e719def31fe0351 | goal_height,spawn_x | goal_height=0.18, spawn_x=0.008 |
| C2528 | bf6f6d91866c102a | goal_height,spawn_x | goal_height=0.22, spawn_x=-0.008 |
| C2529 | c14a664ce3262738 | goal_height,spawn_x | goal_height=0.24, spawn_x=-0.016 |
| C2530 | 6a3e68c84d26edd7 | goal_height,spawn_x | goal_height=0.26, spawn_x=-0.024 |
| C2531 | 401486e30071d85b | goal_height,spawn_x | goal_height=0.28, spawn_x=-0.032 |
| C2532 | d74fd576d07f6fa2 | goal_height,spawn_x | goal_height=0.3, spawn_x=-0.04 |
| C2533 | ce450ea2c1905b8c | goal_height,spawn_y | goal_height=0.1, spawn_y=-0.04 |
| C2534 | 9a11fe48875a2802 | goal_height,spawn_y | goal_height=0.12, spawn_y=-0.032 |
| C2535 | 368c6325ad1b5283 | goal_height,spawn_y | goal_height=0.14, spawn_y=-0.024 |
| C2536 | 49301c6313a9d589 | goal_height,spawn_y | goal_height=0.16, spawn_y=-0.016 |
| C2537 | ac2306041766d244 | goal_height,spawn_y | goal_height=0.18, spawn_y=-0.008 |
| C2538 | dbf87b780970b921 | goal_height,spawn_y | goal_height=0.22, spawn_y=0.008 |
| C2539 | bfa442c8bc5fb472 | goal_height,spawn_y | goal_height=0.24, spawn_y=0.016 |
| C2540 | c6c062ad58a5b725 | goal_height,spawn_y | goal_height=0.26, spawn_y=0.024 |
| C2541 | 6936b00affb7a09e | goal_height,spawn_y | goal_height=0.28, spawn_y=0.032 |
| C2542 | 935057854cc38b7f | goal_height,spawn_y | goal_height=0.3, spawn_y=0.04 |
| C2543 | b0129b812a1098dd | goal_height,spawn_y | goal_height=0.1, spawn_y=0.04 |
| C2544 | 2dad1170f3e217dc | goal_height,spawn_y | goal_height=0.12, spawn_y=0.032 |
| C2545 | 7b7c2c12ff57723e | goal_height,spawn_y | goal_height=0.14, spawn_y=0.024 |
| C2546 | e8614aeba38310d0 | goal_height,spawn_y | goal_height=0.16, spawn_y=0.016 |
| C2547 | f31af4a2e494237d | goal_height,spawn_y | goal_height=0.18, spawn_y=0.008 |
| C2548 | d62a72eba6b93eb3 | goal_height,spawn_y | goal_height=0.22, spawn_y=-0.008 |
| C2549 | 22dc85edf4c8bd15 | goal_height,spawn_y | goal_height=0.24, spawn_y=-0.016 |
| C2550 | bb31428614a6bc9b | goal_height,spawn_y | goal_height=0.26, spawn_y=-0.024 |
| C2551 | e6ce1daf880136b3 | goal_height,spawn_y | goal_height=0.28, spawn_y=-0.032 |
| C2552 | 14c8ddbf16d0a0ee | goal_height,spawn_y | goal_height=0.3, spawn_y=-0.04 |
| C2553 | e95ed5ed199439b0 | goal_height,spawn_yaw | goal_height=0.1, spawn_yaw=-0.523598775598 |
| C2554 | ca192205726c5b57 | goal_height,spawn_yaw | goal_height=0.12, spawn_yaw=-0.418879020478 |
| C2555 | bd79c8eca4ce9cb6 | goal_height,spawn_yaw | goal_height=0.14, spawn_yaw=-0.314159265359 |
| C2556 | 50fc9b3af02122a9 | goal_height,spawn_yaw | goal_height=0.16, spawn_yaw=-0.209439510239 |
| C2557 | 6b044de11798a128 | goal_height,spawn_yaw | goal_height=0.18, spawn_yaw=-0.10471975512 |
| C2558 | 43142466a9e90c33 | goal_height,spawn_yaw | goal_height=0.22, spawn_yaw=0.10471975512 |
| C2559 | 12717c21b59ddc7e | goal_height,spawn_yaw | goal_height=0.24, spawn_yaw=0.209439510239 |
| C2560 | 5d8e40b7f2732b03 | goal_height,spawn_yaw | goal_height=0.26, spawn_yaw=0.314159265359 |
| C2561 | 49b64940d8356db3 | goal_height,spawn_yaw | goal_height=0.28, spawn_yaw=0.418879020478 |
| C2562 | be4c47794c316853 | goal_height,spawn_yaw | goal_height=0.3, spawn_yaw=0.523598775598 |
| C2563 | 5a310f4daa10b23e | goal_height,spawn_yaw | goal_height=0.1, spawn_yaw=0.523598775598 |
| C2564 | 41c135fa9162b5c7 | goal_height,spawn_yaw | goal_height=0.12, spawn_yaw=0.418879020478 |
| C2565 | d041aba743c439cb | goal_height,spawn_yaw | goal_height=0.14, spawn_yaw=0.314159265359 |
| C2566 | e4a541dfe9f97297 | goal_height,spawn_yaw | goal_height=0.16, spawn_yaw=0.209439510239 |
| C2567 | 54737c3a95a3e1e9 | goal_height,spawn_yaw | goal_height=0.18, spawn_yaw=0.10471975512 |
| C2568 | 5604db7c6faba118 | goal_height,spawn_yaw | goal_height=0.22, spawn_yaw=-0.10471975512 |
| C2569 | 05c079561173aedd | goal_height,spawn_yaw | goal_height=0.24, spawn_yaw=-0.209439510239 |
| C2570 | d0ec63bfd3c0f60c | goal_height,spawn_yaw | goal_height=0.26, spawn_yaw=-0.314159265359 |
| C2571 | 14c5368f3f710bca | goal_height,spawn_yaw | goal_height=0.28, spawn_yaw=-0.418879020478 |
| C2572 | 37ce3c055d3226a6 | goal_height,spawn_yaw | goal_height=0.3, spawn_yaw=-0.523598775598 |
| C2573 | bf5aa6db708f78b4 | goal_height,inertia_scale | goal_height=0.1, inertia_scale=0.5 |
| C2574 | 651cddb2a194e261 | goal_height,inertia_scale | goal_height=0.12, inertia_scale=0.65 |
| C2575 | 3d66b8f8e53e48b4 | goal_height,inertia_scale | goal_height=0.14, inertia_scale=0.8 |
| C2576 | 99bf714906096678 | goal_height,inertia_scale | goal_height=0.16, inertia_scale=0.95 |
| C2577 | 27b237f19d496a8b | goal_height,inertia_scale | goal_height=0.18, inertia_scale=1.1 |
| C2578 | 8ef22f19dfc2a513 | goal_height,inertia_scale | goal_height=0.22, inertia_scale=1.4 |
| C2579 | f5451ffafea75635 | goal_height,inertia_scale | goal_height=0.24, inertia_scale=1.55 |
| C2580 | cf973414130060ad | goal_height,inertia_scale | goal_height=0.26, inertia_scale=1.7 |
| C2581 | 5c3e030564cfcce6 | goal_height,inertia_scale | goal_height=0.28, inertia_scale=1.85 |
| C2582 | a079fda4826ac32e | goal_height,inertia_scale | goal_height=0.3, inertia_scale=2.0 |
| C2583 | 0317a9be0d0029ac | goal_height,inertia_scale | goal_height=0.1, inertia_scale=2.0 |
| C2584 | ef3fd16b41b6e0dc | goal_height,inertia_scale | goal_height=0.12, inertia_scale=1.85 |
| C2585 | b8c3128a83850441 | goal_height,inertia_scale | goal_height=0.14, inertia_scale=1.7 |
| C2586 | 7651bc4693d00770 | goal_height,inertia_scale | goal_height=0.16, inertia_scale=1.55 |
| C2587 | e5fb4a252924edfb | goal_height,inertia_scale | goal_height=0.18, inertia_scale=1.4 |
| C2588 | 5190c66e59f7c134 | goal_height,inertia_scale | goal_height=0.22, inertia_scale=1.1 |
| C2589 | d338a5cd4a6a2300 | goal_height,inertia_scale | goal_height=0.24, inertia_scale=0.95 |
| C2590 | 04b1af0a82a0dbff | goal_height,inertia_scale | goal_height=0.26, inertia_scale=0.8 |
| C2591 | a58f4037b0c20e95 | goal_height,inertia_scale | goal_height=0.28, inertia_scale=0.65 |
| C2592 | 91b245c728569dc1 | goal_height,inertia_scale | goal_height=0.3, inertia_scale=0.5 |
| C2593 | 9056bcab4033caea | restitution,linear_damping | restitution=0.05, linear_damping=0.1 |
| C2594 | fee22cc7ae6e4b58 | restitution,linear_damping | restitution=0.1, linear_damping=0.2 |
| C2595 | a7c802a7b13d773a | restitution,linear_damping | restitution=0.15, linear_damping=0.3 |
| C2596 | ee661fab1ad861e4 | restitution,linear_damping | restitution=0.2, linear_damping=0.4 |
| C2597 | 017cc9c82830cee2 | restitution,linear_damping | restitution=0.25, linear_damping=0.5 |
| C2598 | ca4f3b0b118d71d7 | restitution,linear_damping | restitution=0.3, linear_damping=0.6 |
| C2599 | fb96239b0eeedc45 | restitution,linear_damping | restitution=0.35, linear_damping=0.7 |
| C2600 | 03aa21e1c6f0f0d6 | restitution,linear_damping | restitution=0.4, linear_damping=0.8 |
| C2601 | 6e5c0875b8e2e770 | restitution,linear_damping | restitution=0.45, linear_damping=0.9 |
| C2602 | 78bbac3096e00751 | restitution,linear_damping | restitution=0.5, linear_damping=1.0 |
| C2603 | 6878a5b9e4add1d2 | restitution,linear_damping | restitution=0.05, linear_damping=0.9 |
| C2604 | 68bd45fee62ebe28 | restitution,linear_damping | restitution=0.1, linear_damping=0.8 |
| C2605 | e7bf20ca3d3ab176 | restitution,linear_damping | restitution=0.15, linear_damping=0.7 |
| C2606 | 81121253cb3db371 | restitution,linear_damping | restitution=0.2, linear_damping=0.6 |
| C2607 | 97f1f22bf0bac5fc | restitution,linear_damping | restitution=0.3, linear_damping=0.4 |
| C2608 | bec15f4da2cdef28 | restitution,linear_damping | restitution=0.35, linear_damping=0.3 |
| C2609 | 70125db5fe648777 | restitution,linear_damping | restitution=0.4, linear_damping=0.2 |
| C2610 | 44a713b74cb4b264 | restitution,linear_damping | restitution=0.45, linear_damping=0.1 |
| C2611 | 1dfdf3b99cf8be09 | restitution,angular_damping | restitution=0.1, angular_damping=0.1 |
| C2612 | a8e9e65f9cdaa55d | restitution,angular_damping | restitution=0.15, angular_damping=0.15 |
| C2613 | e0f0b3de9f91e845 | restitution,angular_damping | restitution=0.2, angular_damping=0.2 |
| C2614 | 57eac4bd3a30ac6e | restitution,angular_damping | restitution=0.25, angular_damping=0.25 |
| C2615 | 0ac1d1bf0aa6d27a | restitution,angular_damping | restitution=0.3, angular_damping=0.3 |
| C2616 | 32e028adfe7d6f4f | restitution,angular_damping | restitution=0.35, angular_damping=0.35 |
| C2617 | 69d3464866d21dae | restitution,angular_damping | restitution=0.4, angular_damping=0.4 |
| C2618 | fc255318a32f79a1 | restitution,angular_damping | restitution=0.45, angular_damping=0.45 |
| C2619 | 520505d6a06c8d93 | restitution,angular_damping | restitution=0.5, angular_damping=0.5 |
| C2620 | 837e28d3b57d1c99 | restitution,angular_damping | restitution=0.05, angular_damping=0.45 |
| C2621 | ff73e4f8342f033e | restitution,angular_damping | restitution=0.1, angular_damping=0.4 |
| C2622 | d2a8a2ed3ccf59f4 | restitution,angular_damping | restitution=0.15, angular_damping=0.35 |
| C2623 | 09bafbc9b4552a6c | restitution,angular_damping | restitution=0.2, angular_damping=0.3 |
| C2624 | 8845f4168f29f438 | restitution,angular_damping | restitution=0.3, angular_damping=0.2 |
| C2625 | 917614998d1e48cc | restitution,angular_damping | restitution=0.35, angular_damping=0.15 |
| C2626 | c1dd3ead281856d1 | restitution,angular_damping | restitution=0.4, angular_damping=0.1 |
| C2627 | 9f109ba028b442d5 | restitution,angular_damping | restitution=0.5, angular_damping=0.0 |
| C2628 | 16cb3f13c20f299f | restitution,spawn_x | restitution=0.05, spawn_x=-0.032 |
| C2629 | 0279551850d0b8ac | restitution,spawn_x | restitution=0.1, spawn_x=-0.024 |
| C2630 | a6d945f867d55acb | restitution,spawn_x | restitution=0.15, spawn_x=-0.016 |
| C2631 | a1a463af2377c32f | restitution,spawn_x | restitution=0.2, spawn_x=-0.008 |
| C2632 | e6f6421cfb28f38a | restitution,spawn_x | restitution=0.3, spawn_x=0.008 |
| C2633 | 1fa454b69aa4fc54 | restitution,spawn_x | restitution=0.35, spawn_x=0.016 |
| C2634 | 6d59cbf1bbbdeb1f | restitution,spawn_x | restitution=0.4, spawn_x=0.024 |
| C2635 | 374e17726d029f9c | restitution,spawn_x | restitution=0.45, spawn_x=0.032 |
| C2636 | 6ac66cf6eba3213f | restitution,spawn_x | restitution=0.5, spawn_x=0.04 |
| C2637 | c85ae5ed0f0424aa | restitution,spawn_x | restitution=0.05, spawn_x=0.032 |
| C2638 | 13287096cd55938d | restitution,spawn_x | restitution=0.1, spawn_x=0.024 |
| C2639 | 9769a9a8c96fbce1 | restitution,spawn_x | restitution=0.15, spawn_x=0.016 |
| C2640 | bcba4886242f5d91 | restitution,spawn_x | restitution=0.2, spawn_x=0.008 |
| C2641 | 1338f8b69e0a0034 | restitution,spawn_x | restitution=0.3, spawn_x=-0.008 |
| C2642 | e6fed066709fdc12 | restitution,spawn_x | restitution=0.35, spawn_x=-0.016 |
| C2643 | 5fa04e91d9232ade | restitution,spawn_x | restitution=0.4, spawn_x=-0.024 |
| C2644 | 26931456b5ca02b1 | restitution,spawn_x | restitution=0.45, spawn_x=-0.032 |
| C2645 | 844f8af9f1fac4d0 | restitution,spawn_x | restitution=0.5, spawn_x=-0.04 |
| C2646 | e4311a9defac6dcb | restitution,spawn_y | restitution=0.05, spawn_y=-0.032 |
| C2647 | 251138c505514857 | restitution,spawn_y | restitution=0.1, spawn_y=-0.024 |
| C2648 | da0639df6965ee45 | restitution,spawn_y | restitution=0.15, spawn_y=-0.016 |
| C2649 | 612eb8c462fcf228 | restitution,spawn_y | restitution=0.2, spawn_y=-0.008 |
| C2650 | ab05a9e133cfc5a5 | restitution,spawn_y | restitution=0.3, spawn_y=0.008 |
| C2651 | aa857fdb8b6e22bc | restitution,spawn_y | restitution=0.35, spawn_y=0.016 |
| C2652 | 3b152e9a1fa65407 | restitution,spawn_y | restitution=0.4, spawn_y=0.024 |
| C2653 | ca012ea8193d4278 | restitution,spawn_y | restitution=0.45, spawn_y=0.032 |
| C2654 | 3cdc10142a6fd49a | restitution,spawn_y | restitution=0.5, spawn_y=0.04 |
| C2655 | 1d62d24117e0d624 | restitution,spawn_y | restitution=0.05, spawn_y=0.032 |
| C2656 | 1b9c5bbe9941edaf | restitution,spawn_y | restitution=0.1, spawn_y=0.024 |
| C2657 | 7c0d51bc097e2046 | restitution,spawn_y | restitution=0.15, spawn_y=0.016 |
| C2658 | bba203844339e658 | restitution,spawn_y | restitution=0.2, spawn_y=0.008 |
| C2659 | c77e04a8a99c5b91 | restitution,spawn_y | restitution=0.3, spawn_y=-0.008 |
| C2660 | 2bf3a93efb222fd4 | restitution,spawn_y | restitution=0.35, spawn_y=-0.016 |
| C2661 | 5165c1fa0356eaa5 | restitution,spawn_y | restitution=0.4, spawn_y=-0.024 |
| C2662 | 320d398275063f22 | restitution,spawn_y | restitution=0.45, spawn_y=-0.032 |
| C2663 | 863e93b0bdbc4c92 | restitution,spawn_y | restitution=0.5, spawn_y=-0.04 |
| C2664 | a839f39ad387553f | restitution,spawn_yaw | restitution=0.05, spawn_yaw=-0.418879020478 |
| C2665 | 0ff8632c76e0e07b | restitution,spawn_yaw | restitution=0.1, spawn_yaw=-0.314159265359 |
| C2666 | 1be71143a56d0210 | restitution,spawn_yaw | restitution=0.15, spawn_yaw=-0.209439510239 |
| C2667 | ae3bdddc87b8eb21 | restitution,spawn_yaw | restitution=0.2, spawn_yaw=-0.10471975512 |
| C2668 | 9df71b3ae91d4ffc | restitution,spawn_yaw | restitution=0.3, spawn_yaw=0.10471975512 |
| C2669 | 75be25b05aba66c2 | restitution,spawn_yaw | restitution=0.35, spawn_yaw=0.209439510239 |
| C2670 | f4caf991b576382f | restitution,spawn_yaw | restitution=0.4, spawn_yaw=0.314159265359 |
| C2671 | 445a80e31877498e | restitution,spawn_yaw | restitution=0.45, spawn_yaw=0.418879020478 |
| C2672 | cbc8a4756d417719 | restitution,spawn_yaw | restitution=0.5, spawn_yaw=0.523598775598 |
| C2673 | 085fb0850e560d9f | restitution,spawn_yaw | restitution=0.05, spawn_yaw=0.418879020478 |
| C2674 | 77fc02572fdccd63 | restitution,spawn_yaw | restitution=0.1, spawn_yaw=0.314159265359 |
| C2675 | fdfd5d1d163b8c0c | restitution,spawn_yaw | restitution=0.15, spawn_yaw=0.209439510239 |
| C2676 | 8a066aada2a5e56b | restitution,spawn_yaw | restitution=0.2, spawn_yaw=0.10471975512 |
| C2677 | 055b8274373be055 | restitution,spawn_yaw | restitution=0.3, spawn_yaw=-0.10471975512 |
| C2678 | 3c4c0dde2c375e8b | restitution,spawn_yaw | restitution=0.35, spawn_yaw=-0.209439510239 |
| C2679 | 74905cc7448e13be | restitution,spawn_yaw | restitution=0.4, spawn_yaw=-0.314159265359 |
| C2680 | bc48631553d5a7bc | restitution,spawn_yaw | restitution=0.45, spawn_yaw=-0.418879020478 |
| C2681 | d9423e8e6d795787 | restitution,spawn_yaw | restitution=0.5, spawn_yaw=-0.523598775598 |
| C2682 | d3678ce990125d56 | restitution,inertia_scale | restitution=0.05, inertia_scale=0.65 |
| C2683 | 2f96da4fa985c7d7 | restitution,inertia_scale | restitution=0.1, inertia_scale=0.8 |
| C2684 | 4a220804fb0b9611 | restitution,inertia_scale | restitution=0.15, inertia_scale=0.95 |
| C2685 | ffe863daa339c223 | restitution,inertia_scale | restitution=0.2, inertia_scale=1.1 |
| C2686 | 7a9abb91d8d360bb | restitution,inertia_scale | restitution=0.25, inertia_scale=1.25 |
| C2687 | 75c3a96749eccd42 | restitution,inertia_scale | restitution=0.3, inertia_scale=1.4 |
| C2688 | 10a9389f6aff85c7 | restitution,inertia_scale | restitution=0.35, inertia_scale=1.55 |
| C2689 | 4551884beabe4850 | restitution,inertia_scale | restitution=0.4, inertia_scale=1.7 |
| C2690 | 259320916e07bf92 | restitution,inertia_scale | restitution=0.45, inertia_scale=1.85 |
| C2691 | ef62278acf66f65a | restitution,inertia_scale | restitution=0.5, inertia_scale=2.0 |
| C2692 | 9107cdd68eb7a97e | restitution,inertia_scale | restitution=0.05, inertia_scale=1.85 |
| C2693 | c69d9905d242554a | restitution,inertia_scale | restitution=0.1, inertia_scale=1.7 |
| C2694 | a447398ca09a548c | restitution,inertia_scale | restitution=0.15, inertia_scale=1.55 |
| C2695 | 40face7acc80eb69 | restitution,inertia_scale | restitution=0.2, inertia_scale=1.4 |
| C2696 | 63be840a729f879d | restitution,inertia_scale | restitution=0.3, inertia_scale=1.1 |
| C2697 | 4afd09da5e567d46 | restitution,inertia_scale | restitution=0.35, inertia_scale=0.95 |
| C2698 | bd94253beaadecae | restitution,inertia_scale | restitution=0.4, inertia_scale=0.8 |
| C2699 | 349dec42c7bad73a | restitution,inertia_scale | restitution=0.45, inertia_scale=0.65 |
| C2700 | cf7d207bff6822bd | restitution,inertia_scale | restitution=0.5, inertia_scale=0.5 |
| C2701 | 2007ef23c1da927b | linear_damping,angular_damping | linear_damping=0.2, angular_damping=0.1 |
| C2702 | ec9a2c04eac2f9c8 | linear_damping,angular_damping | linear_damping=0.3, angular_damping=0.15 |
| C2703 | ba03d4710c27e8ba | linear_damping,angular_damping | linear_damping=0.4, angular_damping=0.2 |
| C2704 | a06882eb339ded76 | linear_damping,angular_damping | linear_damping=0.5, angular_damping=0.25 |
| C2705 | 070887fc5f67d61a | linear_damping,angular_damping | linear_damping=0.6, angular_damping=0.3 |
| C2706 | e04f3753bfc0365d | linear_damping,angular_damping | linear_damping=0.7, angular_damping=0.35 |
| C2707 | 4a75c2c98de40281 | linear_damping,angular_damping | linear_damping=0.8, angular_damping=0.4 |
| C2708 | a2de87703ba63d79 | linear_damping,angular_damping | linear_damping=0.9, angular_damping=0.45 |
| C2709 | fbfe5c1be7387dfc | linear_damping,angular_damping | linear_damping=1.0, angular_damping=0.5 |
| C2710 | b5936f24f943e7bd | linear_damping,angular_damping | linear_damping=0.1, angular_damping=0.45 |
| C2711 | a8ef7abe35e53a78 | linear_damping,angular_damping | linear_damping=0.2, angular_damping=0.4 |
| C2712 | 8cf0ca5c72a81e35 | linear_damping,angular_damping | linear_damping=0.3, angular_damping=0.35 |
| C2713 | f563db83e5699924 | linear_damping,angular_damping | linear_damping=0.4, angular_damping=0.3 |
| C2714 | 74192b65aa77ecca | linear_damping,angular_damping | linear_damping=0.6, angular_damping=0.2 |
| C2715 | dae2ef5c76ad259a | linear_damping,angular_damping | linear_damping=0.7, angular_damping=0.15 |
| C2716 | 1f4d5fa294af6ab0 | linear_damping,angular_damping | linear_damping=0.8, angular_damping=0.1 |
| C2717 | ba2c24bd9a81e483 | linear_damping,angular_damping | linear_damping=1.0, angular_damping=0.0 |
| C2718 | 28aca01ba1dea1b3 | linear_damping,spawn_x | linear_damping=0.1, spawn_x=-0.032 |
| C2719 | bbecd0768e27a046 | linear_damping,spawn_x | linear_damping=0.2, spawn_x=-0.024 |
| C2720 | de2afdf71f2e1709 | linear_damping,spawn_x | linear_damping=0.3, spawn_x=-0.016 |
| C2721 | 3a35d55e9eb9eba2 | linear_damping,spawn_x | linear_damping=0.4, spawn_x=-0.008 |
| C2722 | abac93dca5e5d7c9 | linear_damping,spawn_x | linear_damping=0.6, spawn_x=0.008 |
| C2723 | ed873b81205c6aeb | linear_damping,spawn_x | linear_damping=0.7, spawn_x=0.016 |
| C2724 | 91a08a4ef4271a72 | linear_damping,spawn_x | linear_damping=0.8, spawn_x=0.024 |
| C2725 | 30cb03daa95de15f | linear_damping,spawn_x | linear_damping=0.9, spawn_x=0.032 |
| C2726 | 9d8599ff26686528 | linear_damping,spawn_x | linear_damping=1.0, spawn_x=0.04 |
| C2727 | 51271f5320a70fad | linear_damping,spawn_x | linear_damping=0.1, spawn_x=0.032 |
| C2728 | 7f6e86c5d2c9fbca | linear_damping,spawn_x | linear_damping=0.2, spawn_x=0.024 |
| C2729 | b9e6b13991f3160a | linear_damping,spawn_x | linear_damping=0.3, spawn_x=0.016 |
| C2730 | 731f800bcb693068 | linear_damping,spawn_x | linear_damping=0.4, spawn_x=0.008 |
| C2731 | 46cf74950021273f | linear_damping,spawn_x | linear_damping=0.6, spawn_x=-0.008 |
| C2732 | 733af86eaffc5982 | linear_damping,spawn_x | linear_damping=0.7, spawn_x=-0.016 |
| C2733 | d23a66d58b982224 | linear_damping,spawn_x | linear_damping=0.8, spawn_x=-0.024 |
| C2734 | d290b08b9bb2874a | linear_damping,spawn_x | linear_damping=0.9, spawn_x=-0.032 |
| C2735 | b1c9de20c66a11fb | linear_damping,spawn_x | linear_damping=1.0, spawn_x=-0.04 |
| C2736 | 8899e35142c2640f | linear_damping,spawn_y | linear_damping=0.1, spawn_y=-0.032 |
| C2737 | 3a8444eedc6e9ab5 | linear_damping,spawn_y | linear_damping=0.2, spawn_y=-0.024 |
| C2738 | d03bd395eb249359 | linear_damping,spawn_y | linear_damping=0.3, spawn_y=-0.016 |
| C2739 | d43900042025f364 | linear_damping,spawn_y | linear_damping=0.4, spawn_y=-0.008 |
| C2740 | 3bf6f0bd44a8b7d5 | linear_damping,spawn_y | linear_damping=0.6, spawn_y=0.008 |
| C2741 | 900d564a23c372e7 | linear_damping,spawn_y | linear_damping=0.7, spawn_y=0.016 |
| C2742 | 04cfcc117d2595dd | linear_damping,spawn_y | linear_damping=0.8, spawn_y=0.024 |
| C2743 | 4673da613a5188cc | linear_damping,spawn_y | linear_damping=0.9, spawn_y=0.032 |
| C2744 | ea45e8cf282f2c03 | linear_damping,spawn_y | linear_damping=1.0, spawn_y=0.04 |
| C2745 | b6f1ab727319e606 | linear_damping,spawn_y | linear_damping=0.1, spawn_y=0.032 |
| C2746 | 93806a7a33ffd402 | linear_damping,spawn_y | linear_damping=0.2, spawn_y=0.024 |
| C2747 | 88f184ec240586d6 | linear_damping,spawn_y | linear_damping=0.3, spawn_y=0.016 |
| C2748 | ad6a07814ead3726 | linear_damping,spawn_y | linear_damping=0.4, spawn_y=0.008 |
| C2749 | 4c9731783d0b2acc | linear_damping,spawn_y | linear_damping=0.6, spawn_y=-0.008 |
| C2750 | 4483e302667fafea | linear_damping,spawn_y | linear_damping=0.7, spawn_y=-0.016 |
| C2751 | cfb1286d9bf97e53 | linear_damping,spawn_y | linear_damping=0.8, spawn_y=-0.024 |
| C2752 | 107809077c286a5d | linear_damping,spawn_y | linear_damping=0.9, spawn_y=-0.032 |
| C2753 | b912fc53e4638f2d | linear_damping,spawn_y | linear_damping=1.0, spawn_y=-0.04 |
| C2754 | 6dcf05b2f7c38555 | linear_damping,spawn_yaw | linear_damping=0.1, spawn_yaw=-0.418879020478 |
| C2755 | 738410cda5235e29 | linear_damping,spawn_yaw | linear_damping=0.2, spawn_yaw=-0.314159265359 |
| C2756 | ffa7329938f8a51e | linear_damping,spawn_yaw | linear_damping=0.3, spawn_yaw=-0.209439510239 |
| C2757 | d352436165d30554 | linear_damping,spawn_yaw | linear_damping=0.4, spawn_yaw=-0.10471975512 |
| C2758 | 5b2a31dab6b10d90 | linear_damping,spawn_yaw | linear_damping=0.6, spawn_yaw=0.10471975512 |
| C2759 | 81a5729df7b9afbe | linear_damping,spawn_yaw | linear_damping=0.7, spawn_yaw=0.209439510239 |
| C2760 | 4854dc80f1b5643c | linear_damping,spawn_yaw | linear_damping=0.8, spawn_yaw=0.314159265359 |
| C2761 | d801740f1c70df58 | linear_damping,spawn_yaw | linear_damping=0.9, spawn_yaw=0.418879020478 |
| C2762 | 84d69ff8d3768f84 | linear_damping,spawn_yaw | linear_damping=1.0, spawn_yaw=0.523598775598 |
| C2763 | 7ffdeb5448917798 | linear_damping,spawn_yaw | linear_damping=0.1, spawn_yaw=0.418879020478 |
| C2764 | 894f7ca5febbdb7f | linear_damping,spawn_yaw | linear_damping=0.2, spawn_yaw=0.314159265359 |
| C2765 | 5ab4416e02b74872 | linear_damping,spawn_yaw | linear_damping=0.3, spawn_yaw=0.209439510239 |
| C2766 | f17c94476fec64cf | linear_damping,spawn_yaw | linear_damping=0.4, spawn_yaw=0.10471975512 |
| C2767 | 5fbc87ecf75d5eb8 | linear_damping,spawn_yaw | linear_damping=0.6, spawn_yaw=-0.10471975512 |
| C2768 | dc4d677b3d7ed423 | linear_damping,spawn_yaw | linear_damping=0.7, spawn_yaw=-0.209439510239 |
| C2769 | cc02119c52cfdd07 | linear_damping,spawn_yaw | linear_damping=0.8, spawn_yaw=-0.314159265359 |
| C2770 | 78786f853d48800f | linear_damping,spawn_yaw | linear_damping=0.9, spawn_yaw=-0.418879020478 |
| C2771 | 35fee43fe1daa95d | linear_damping,spawn_yaw | linear_damping=1.0, spawn_yaw=-0.523598775598 |
| C2772 | 303f714ab08b1f23 | linear_damping,inertia_scale | linear_damping=0.1, inertia_scale=0.65 |
| C2773 | 79a90574978286ed | linear_damping,inertia_scale | linear_damping=0.2, inertia_scale=0.8 |
| C2774 | 4f63e8137ec84143 | linear_damping,inertia_scale | linear_damping=0.3, inertia_scale=0.95 |
| C2775 | 5b82e9f183fdaf70 | linear_damping,inertia_scale | linear_damping=0.4, inertia_scale=1.1 |
| C2776 | 0d1e5476013782ff | linear_damping,inertia_scale | linear_damping=0.5, inertia_scale=1.25 |
| C2777 | cb420c2c00bfe483 | linear_damping,inertia_scale | linear_damping=0.6, inertia_scale=1.4 |
| C2778 | fba7cb8cbe91cd46 | linear_damping,inertia_scale | linear_damping=0.7, inertia_scale=1.55 |
| C2779 | 46c93ce7d0940187 | linear_damping,inertia_scale | linear_damping=0.8, inertia_scale=1.7 |
| C2780 | e09e54a8dbcd4cd1 | linear_damping,inertia_scale | linear_damping=0.9, inertia_scale=1.85 |
| C2781 | ab33fb5158a11e86 | linear_damping,inertia_scale | linear_damping=1.0, inertia_scale=2.0 |
| C2782 | 613f35606fb2f92e | linear_damping,inertia_scale | linear_damping=0.1, inertia_scale=1.85 |
| C2783 | 90434c0556defc77 | linear_damping,inertia_scale | linear_damping=0.2, inertia_scale=1.7 |
| C2784 | 5b6209ddb869c113 | linear_damping,inertia_scale | linear_damping=0.3, inertia_scale=1.55 |
| C2785 | 0dcdc6340a3155fa | linear_damping,inertia_scale | linear_damping=0.4, inertia_scale=1.4 |
| C2786 | a9fba9ad5b356a25 | linear_damping,inertia_scale | linear_damping=0.6, inertia_scale=1.1 |
| C2787 | e3ee0ae4de9e716b | linear_damping,inertia_scale | linear_damping=0.7, inertia_scale=0.95 |
| C2788 | 2a85cc02ab82bd6f | linear_damping,inertia_scale | linear_damping=0.8, inertia_scale=0.8 |
| C2789 | b7baee4f0e26058f | linear_damping,inertia_scale | linear_damping=0.9, inertia_scale=0.65 |
| C2790 | 04b2ba9f0249c3bc | linear_damping,inertia_scale | linear_damping=1.0, inertia_scale=0.5 |
| C2791 | 419ded6b255a1a7f | angular_damping,spawn_x | angular_damping=0.0, spawn_x=-0.04 |
| C2792 | e0cc010f1bfa5e98 | angular_damping,spawn_x | angular_damping=0.1, spawn_x=-0.024 |
| C2793 | 6829c32da3b35a44 | angular_damping,spawn_x | angular_damping=0.15, spawn_x=-0.016 |
| C2794 | 5a22d479faf31611 | angular_damping,spawn_x | angular_damping=0.2, spawn_x=-0.008 |
| C2795 | 5f742b65d2ec92f9 | angular_damping,spawn_x | angular_damping=0.3, spawn_x=0.008 |
| C2796 | 9293562836cab27c | angular_damping,spawn_x | angular_damping=0.35, spawn_x=0.016 |
| C2797 | c5821347775d4b5a | angular_damping,spawn_x | angular_damping=0.4, spawn_x=0.024 |
| C2798 | ebacdfbbf20ab0cb | angular_damping,spawn_x | angular_damping=0.45, spawn_x=0.032 |
| C2799 | fce9c8eed6973945 | angular_damping,spawn_x | angular_damping=0.5, spawn_x=0.04 |
| C2800 | 7f2aacc09f06cb65 | angular_damping,spawn_x | angular_damping=0.0, spawn_x=0.04 |
| C2801 | 1e9deba6020b6d0f | angular_damping,spawn_x | angular_damping=0.1, spawn_x=0.024 |
| C2802 | ff8a57d3334dab0e | angular_damping,spawn_x | angular_damping=0.15, spawn_x=0.016 |
| C2803 | 70d7aa2d014d516b | angular_damping,spawn_x | angular_damping=0.2, spawn_x=0.008 |
| C2804 | 72a34a177338521f | angular_damping,spawn_x | angular_damping=0.3, spawn_x=-0.008 |
| C2805 | 90b87ce6b14c23c0 | angular_damping,spawn_x | angular_damping=0.35, spawn_x=-0.016 |
| C2806 | 822137051aad81dd | angular_damping,spawn_x | angular_damping=0.4, spawn_x=-0.024 |
| C2807 | b1b44db437de0818 | angular_damping,spawn_x | angular_damping=0.45, spawn_x=-0.032 |
| C2808 | e9fe15b5aeec5bd2 | angular_damping,spawn_x | angular_damping=0.5, spawn_x=-0.04 |
| C2809 | 6f6ccfc3bb00b6e5 | angular_damping,spawn_y | angular_damping=0.0, spawn_y=-0.04 |
| C2810 | 8be98d75389cb8d7 | angular_damping,spawn_y | angular_damping=0.1, spawn_y=-0.024 |
| C2811 | e225581539ca29b7 | angular_damping,spawn_y | angular_damping=0.15, spawn_y=-0.016 |
| C2812 | f23a7c0d014b0fbf | angular_damping,spawn_y | angular_damping=0.2, spawn_y=-0.008 |
| C2813 | de190bec330a1f63 | angular_damping,spawn_y | angular_damping=0.3, spawn_y=0.008 |
| C2814 | 4bd8c8d1413971d1 | angular_damping,spawn_y | angular_damping=0.35, spawn_y=0.016 |
| C2815 | 04e438f3e03714c1 | angular_damping,spawn_y | angular_damping=0.4, spawn_y=0.024 |
| C2816 | 946fb90b1065cae9 | angular_damping,spawn_y | angular_damping=0.45, spawn_y=0.032 |
| C2817 | 530a797364bf6825 | angular_damping,spawn_y | angular_damping=0.5, spawn_y=0.04 |
| C2818 | 1bafefa4cd97a5b8 | angular_damping,spawn_y | angular_damping=0.0, spawn_y=0.04 |
| C2819 | b3d037db2d1d3fda | angular_damping,spawn_y | angular_damping=0.1, spawn_y=0.024 |
| C2820 | c4d70ba1018e832e | angular_damping,spawn_y | angular_damping=0.15, spawn_y=0.016 |
| C2821 | 6e387e667ce92efb | angular_damping,spawn_y | angular_damping=0.2, spawn_y=0.008 |
| C2822 | 16ff1d33fa2c5945 | angular_damping,spawn_y | angular_damping=0.3, spawn_y=-0.008 |
| C2823 | 69cf00771628e8fb | angular_damping,spawn_y | angular_damping=0.35, spawn_y=-0.016 |
| C2824 | c2ca8be0845837f3 | angular_damping,spawn_y | angular_damping=0.4, spawn_y=-0.024 |
| C2825 | 6b8694522374d056 | angular_damping,spawn_y | angular_damping=0.45, spawn_y=-0.032 |
| C2826 | 563361c6cad2ce5a | angular_damping,spawn_y | angular_damping=0.5, spawn_y=-0.04 |
| C2827 | 8fafcdd3e8b92c1f | angular_damping,spawn_yaw | angular_damping=0.0, spawn_yaw=-0.523598775598 |
| C2828 | 62483ba7c0aefc69 | angular_damping,spawn_yaw | angular_damping=0.1, spawn_yaw=-0.314159265359 |
| C2829 | b9241a063d4e45c2 | angular_damping,spawn_yaw | angular_damping=0.15, spawn_yaw=-0.209439510239 |
| C2830 | 3180f62461a47eea | angular_damping,spawn_yaw | angular_damping=0.2, spawn_yaw=-0.10471975512 |
| C2831 | fcc055ba636456e3 | angular_damping,spawn_yaw | angular_damping=0.3, spawn_yaw=0.10471975512 |
| C2832 | debc3daec99cbdf6 | angular_damping,spawn_yaw | angular_damping=0.35, spawn_yaw=0.209439510239 |
| C2833 | 5f5ec3e5f563cf14 | angular_damping,spawn_yaw | angular_damping=0.4, spawn_yaw=0.314159265359 |
| C2834 | 43bccc1d540f9dc9 | angular_damping,spawn_yaw | angular_damping=0.45, spawn_yaw=0.418879020478 |
| C2835 | f01f1748fe008a42 | angular_damping,spawn_yaw | angular_damping=0.5, spawn_yaw=0.523598775598 |
| C2836 | 6c475bf722cd9d20 | angular_damping,spawn_yaw | angular_damping=0.0, spawn_yaw=0.523598775598 |
| C2837 | 06423b549e5182b2 | angular_damping,spawn_yaw | angular_damping=0.1, spawn_yaw=0.314159265359 |
| C2838 | 05e7f51abe9b0513 | angular_damping,spawn_yaw | angular_damping=0.15, spawn_yaw=0.209439510239 |
| C2839 | 342632bbbc0911c8 | angular_damping,spawn_yaw | angular_damping=0.2, spawn_yaw=0.10471975512 |
| C2840 | 37fec71186a4d7ae | angular_damping,spawn_yaw | angular_damping=0.3, spawn_yaw=-0.10471975512 |
| C2841 | 20b4f9232a9d8f1f | angular_damping,spawn_yaw | angular_damping=0.35, spawn_yaw=-0.209439510239 |
| C2842 | a0d1ec525868ecd8 | angular_damping,spawn_yaw | angular_damping=0.4, spawn_yaw=-0.314159265359 |
| C2843 | 65cca1e74c3d1294 | angular_damping,spawn_yaw | angular_damping=0.45, spawn_yaw=-0.418879020478 |
| C2844 | 7e1be7f2816ac8b2 | angular_damping,spawn_yaw | angular_damping=0.5, spawn_yaw=-0.523598775598 |
| C2845 | 88c7df69e2f484d4 | angular_damping,inertia_scale | angular_damping=0.0, inertia_scale=0.5 |
| C2846 | 6d2beaa3a1d0aae6 | angular_damping,inertia_scale | angular_damping=0.1, inertia_scale=0.8 |
| C2847 | 8a4cee9038ef80a4 | angular_damping,inertia_scale | angular_damping=0.15, inertia_scale=0.95 |
| C2848 | e9beb418d8a81e2a | angular_damping,inertia_scale | angular_damping=0.2, inertia_scale=1.1 |
| C2849 | 81663da02cb0ca56 | angular_damping,inertia_scale | angular_damping=0.25, inertia_scale=1.25 |
| C2850 | 651078a84145d2ac | angular_damping,inertia_scale | angular_damping=0.3, inertia_scale=1.4 |
| C2851 | 1a84b41e624a75de | angular_damping,inertia_scale | angular_damping=0.35, inertia_scale=1.55 |
| C2852 | c842159f0874c100 | angular_damping,inertia_scale | angular_damping=0.4, inertia_scale=1.7 |
| C2853 | b3b1426a31c22460 | angular_damping,inertia_scale | angular_damping=0.45, inertia_scale=1.85 |
| C2854 | 8dc273dc4e0195e7 | angular_damping,inertia_scale | angular_damping=0.5, inertia_scale=2.0 |
| C2855 | 7bec932e5915b60c | angular_damping,inertia_scale | angular_damping=0.0, inertia_scale=2.0 |
| C2856 | b744e0b0847f8b70 | angular_damping,inertia_scale | angular_damping=0.1, inertia_scale=1.7 |
| C2857 | 981726f571382593 | angular_damping,inertia_scale | angular_damping=0.15, inertia_scale=1.55 |
| C2858 | bf3faf86f56e776d | angular_damping,inertia_scale | angular_damping=0.2, inertia_scale=1.4 |
| C2859 | f21d342418762d2e | angular_damping,inertia_scale | angular_damping=0.3, inertia_scale=1.1 |
| C2860 | 225f77713e14e448 | angular_damping,inertia_scale | angular_damping=0.35, inertia_scale=0.95 |
| C2861 | 52f10b386d8313f1 | angular_damping,inertia_scale | angular_damping=0.4, inertia_scale=0.8 |
| C2862 | 16802aeece67bb8b | angular_damping,inertia_scale | angular_damping=0.45, inertia_scale=0.65 |
| C2863 | 9536dd57c64a3d1e | angular_damping,inertia_scale | angular_damping=0.5, inertia_scale=0.5 |
| C2864 | 7ac889fa583d31d9 | spawn_x,spawn_y | spawn_x=-0.04, spawn_y=-0.04 |
| C2865 | 3b0b25bf8cdb5137 | spawn_x,spawn_y | spawn_x=-0.032, spawn_y=-0.032 |
| C2866 | 479c8693b2128102 | spawn_x,spawn_y | spawn_x=-0.024, spawn_y=-0.024 |
| C2867 | d49207e85954ff30 | spawn_x,spawn_y | spawn_x=-0.016, spawn_y=-0.016 |
| C2868 | b2b1a1602bccce40 | spawn_x,spawn_y | spawn_x=-0.008, spawn_y=-0.008 |
| C2869 | cee6e5a9ef8660f9 | spawn_x,spawn_y | spawn_x=0.008, spawn_y=0.008 |
| C2870 | 644a674c58aa323d | spawn_x,spawn_y | spawn_x=0.016, spawn_y=0.016 |
| C2871 | 2d656a741a157ac3 | spawn_x,spawn_y | spawn_x=0.024, spawn_y=0.024 |
| C2872 | fcb2d89e37dd756b | spawn_x,spawn_y | spawn_x=0.032, spawn_y=0.032 |
| C2873 | 6f2084da12b32cd1 | spawn_x,spawn_y | spawn_x=0.04, spawn_y=0.04 |
| C2874 | 2135c3fa3329420a | spawn_x,spawn_y | spawn_x=-0.04, spawn_y=0.04 |
| C2875 | 9fd9b576ca6e6118 | spawn_x,spawn_y | spawn_x=-0.032, spawn_y=0.032 |
| C2876 | 83997b7eb982cbd0 | spawn_x,spawn_y | spawn_x=-0.024, spawn_y=0.024 |
| C2877 | 5ccf80ec162c382f | spawn_x,spawn_y | spawn_x=-0.016, spawn_y=0.016 |
| C2878 | 4ffb02f07a2e70fe | spawn_x,spawn_y | spawn_x=-0.008, spawn_y=0.008 |
| C2879 | 4c3fcd442bfc50a2 | spawn_x,spawn_y | spawn_x=0.008, spawn_y=-0.008 |
| C2880 | aadd0c5d76b3987a | spawn_x,spawn_y | spawn_x=0.016, spawn_y=-0.016 |
| C2881 | 3c14e36af0554241 | spawn_x,spawn_y | spawn_x=0.024, spawn_y=-0.024 |
| C2882 | 5557e6bae056c30d | spawn_x,spawn_y | spawn_x=0.032, spawn_y=-0.032 |
| C2883 | e445771b898cc5a5 | spawn_x,spawn_y | spawn_x=0.04, spawn_y=-0.04 |
| C2884 | 314f92763f3be731 | spawn_x,spawn_yaw | spawn_x=-0.04, spawn_yaw=-0.523598775598 |
| C2885 | c03de70036533471 | spawn_x,spawn_yaw | spawn_x=-0.032, spawn_yaw=-0.418879020478 |
| C2886 | a5d63911c205d16f | spawn_x,spawn_yaw | spawn_x=-0.024, spawn_yaw=-0.314159265359 |
| C2887 | 4f4e4e20ca8cbe68 | spawn_x,spawn_yaw | spawn_x=-0.016, spawn_yaw=-0.209439510239 |
| C2888 | 0524c6ac14d0fce7 | spawn_x,spawn_yaw | spawn_x=-0.008, spawn_yaw=-0.10471975512 |
| C2889 | 82376e63735ef9d4 | spawn_x,spawn_yaw | spawn_x=0.008, spawn_yaw=0.10471975512 |
| C2890 | 3fbb6d07cd4a591a | spawn_x,spawn_yaw | spawn_x=0.016, spawn_yaw=0.209439510239 |
| C2891 | 98d582dfb8c62f37 | spawn_x,spawn_yaw | spawn_x=0.024, spawn_yaw=0.314159265359 |
| C2892 | 1a71ea4540a34db6 | spawn_x,spawn_yaw | spawn_x=0.032, spawn_yaw=0.418879020478 |
| C2893 | 324d1d73f38bcacf | spawn_x,spawn_yaw | spawn_x=0.04, spawn_yaw=0.523598775598 |
| C2894 | 2330e2096c728503 | spawn_x,spawn_yaw | spawn_x=-0.04, spawn_yaw=0.523598775598 |
| C2895 | 6597ed31e76e478c | spawn_x,spawn_yaw | spawn_x=-0.032, spawn_yaw=0.418879020478 |
| C2896 | 76a0aaf45fbd484e | spawn_x,spawn_yaw | spawn_x=-0.024, spawn_yaw=0.314159265359 |
| C2897 | b21d26d8decc5ba8 | spawn_x,spawn_yaw | spawn_x=-0.016, spawn_yaw=0.209439510239 |
| C2898 | 6f9363a1c248f6ec | spawn_x,spawn_yaw | spawn_x=-0.008, spawn_yaw=0.10471975512 |
| C2899 | bd47e8587135cd91 | spawn_x,spawn_yaw | spawn_x=0.008, spawn_yaw=-0.10471975512 |
| C2900 | ddbb9c7d41b10f9f | spawn_x,spawn_yaw | spawn_x=0.016, spawn_yaw=-0.209439510239 |
| C2901 | 8e05fe02107f7f39 | spawn_x,spawn_yaw | spawn_x=0.024, spawn_yaw=-0.314159265359 |
| C2902 | 38dfc0f9f549a3d2 | spawn_x,spawn_yaw | spawn_x=0.032, spawn_yaw=-0.418879020478 |
| C2903 | ff60581850dd0aa0 | spawn_x,spawn_yaw | spawn_x=0.04, spawn_yaw=-0.523598775598 |
| C2904 | 736159e90d6d476b | spawn_x,inertia_scale | spawn_x=-0.04, inertia_scale=0.5 |
| C2905 | f446628917b96312 | spawn_x,inertia_scale | spawn_x=-0.032, inertia_scale=0.65 |
| C2906 | 614dedfcc53cc6ff | spawn_x,inertia_scale | spawn_x=-0.024, inertia_scale=0.8 |
| C2907 | 27dabc5468bf69c7 | spawn_x,inertia_scale | spawn_x=-0.016, inertia_scale=0.95 |
| C2908 | ffd2d97bb23bd6db | spawn_x,inertia_scale | spawn_x=-0.008, inertia_scale=1.1 |
| C2909 | 68d71bd5f27c0f4a | spawn_x,inertia_scale | spawn_x=0.008, inertia_scale=1.4 |
| C2910 | dbc1dfbf11f4a8c0 | spawn_x,inertia_scale | spawn_x=0.016, inertia_scale=1.55 |
| C2911 | 08120675a19ae355 | spawn_x,inertia_scale | spawn_x=0.024, inertia_scale=1.7 |
| C2912 | 4241fb94d87686fc | spawn_x,inertia_scale | spawn_x=0.032, inertia_scale=1.85 |
| C2913 | 4f70a0edde11c4a6 | spawn_x,inertia_scale | spawn_x=0.04, inertia_scale=2.0 |
| C2914 | 8d23e60d18dab6f9 | spawn_x,inertia_scale | spawn_x=-0.04, inertia_scale=2.0 |
| C2915 | 0bc5efb65d48aa60 | spawn_x,inertia_scale | spawn_x=-0.032, inertia_scale=1.85 |
| C2916 | 256ff8cd2dd4a7e3 | spawn_x,inertia_scale | spawn_x=-0.024, inertia_scale=1.7 |
| C2917 | 7c0e9dab437b6ef2 | spawn_x,inertia_scale | spawn_x=-0.016, inertia_scale=1.55 |
| C2918 | ef0e7fdcb1e4b9dd | spawn_x,inertia_scale | spawn_x=-0.008, inertia_scale=1.4 |
| C2919 | 3feda670ebf511ce | spawn_x,inertia_scale | spawn_x=0.008, inertia_scale=1.1 |
| C2920 | 17045355c5dc5161 | spawn_x,inertia_scale | spawn_x=0.016, inertia_scale=0.95 |
| C2921 | c35f06467727c2fb | spawn_x,inertia_scale | spawn_x=0.024, inertia_scale=0.8 |
| C2922 | 2ebacec7f2116696 | spawn_x,inertia_scale | spawn_x=0.032, inertia_scale=0.65 |
| C2923 | b96c4623dff3b0b7 | spawn_x,inertia_scale | spawn_x=0.04, inertia_scale=0.5 |
| C2924 | ed1cc9d0cdf5e090 | spawn_y,spawn_yaw | spawn_y=-0.04, spawn_yaw=-0.523598775598 |
| C2925 | f6a5a21a0e65344c | spawn_y,spawn_yaw | spawn_y=-0.032, spawn_yaw=-0.418879020478 |
| C2926 | 16511f50c0f47f0a | spawn_y,spawn_yaw | spawn_y=-0.024, spawn_yaw=-0.314159265359 |
| C2927 | 7db7813a5fab7455 | spawn_y,spawn_yaw | spawn_y=-0.016, spawn_yaw=-0.209439510239 |
| C2928 | 8107de033081bb63 | spawn_y,spawn_yaw | spawn_y=-0.008, spawn_yaw=-0.10471975512 |
| C2929 | e8790a6eb42fb434 | spawn_y,spawn_yaw | spawn_y=0.008, spawn_yaw=0.10471975512 |
| C2930 | 279b16032881dd19 | spawn_y,spawn_yaw | spawn_y=0.016, spawn_yaw=0.209439510239 |
| C2931 | 9a6c5583476efba8 | spawn_y,spawn_yaw | spawn_y=0.024, spawn_yaw=0.314159265359 |
| C2932 | feb91b9eadd541d1 | spawn_y,spawn_yaw | spawn_y=0.032, spawn_yaw=0.418879020478 |
| C2933 | 5560308201c2f89a | spawn_y,spawn_yaw | spawn_y=0.04, spawn_yaw=0.523598775598 |
| C2934 | 3440f84127adcec0 | spawn_y,spawn_yaw | spawn_y=-0.04, spawn_yaw=0.523598775598 |
| C2935 | 713dcaffdd7a900d | spawn_y,spawn_yaw | spawn_y=-0.032, spawn_yaw=0.418879020478 |
| C2936 | 4a22e57d3e8fce0b | spawn_y,spawn_yaw | spawn_y=-0.024, spawn_yaw=0.314159265359 |
| C2937 | 64b4d657e0cf7232 | spawn_y,spawn_yaw | spawn_y=-0.016, spawn_yaw=0.209439510239 |
| C2938 | 672b142f058cf499 | spawn_y,spawn_yaw | spawn_y=-0.008, spawn_yaw=0.10471975512 |
| C2939 | 4bbf969b45c31362 | spawn_y,spawn_yaw | spawn_y=0.008, spawn_yaw=-0.10471975512 |
| C2940 | d99d95a38fb4d826 | spawn_y,spawn_yaw | spawn_y=0.016, spawn_yaw=-0.209439510239 |
| C2941 | 04845aad509e3034 | spawn_y,spawn_yaw | spawn_y=0.024, spawn_yaw=-0.314159265359 |
| C2942 | a0209424ae7aa9b7 | spawn_y,spawn_yaw | spawn_y=0.032, spawn_yaw=-0.418879020478 |
| C2943 | 9e1f76e0ee521d3f | spawn_y,spawn_yaw | spawn_y=0.04, spawn_yaw=-0.523598775598 |
| C2944 | d95c4df39d441771 | spawn_y,inertia_scale | spawn_y=-0.04, inertia_scale=0.5 |
| C2945 | baa6ac8969bf365a | spawn_y,inertia_scale | spawn_y=-0.032, inertia_scale=0.65 |
| C2946 | 6df62599b362602b | spawn_y,inertia_scale | spawn_y=-0.024, inertia_scale=0.8 |
| C2947 | facae0e439359cfe | spawn_y,inertia_scale | spawn_y=-0.016, inertia_scale=0.95 |
| C2948 | e3d9401687e153ae | spawn_y,inertia_scale | spawn_y=-0.008, inertia_scale=1.1 |
| C2949 | f84bb1db2cb9642b | spawn_y,inertia_scale | spawn_y=0.008, inertia_scale=1.4 |
| C2950 | e323a29f4d0116b7 | spawn_y,inertia_scale | spawn_y=0.016, inertia_scale=1.55 |
| C2951 | c8d4ed72e81baea2 | spawn_y,inertia_scale | spawn_y=0.024, inertia_scale=1.7 |
| C2952 | edfc0bb8c4d7cb2a | spawn_y,inertia_scale | spawn_y=0.032, inertia_scale=1.85 |
| C2953 | 150710b4508665d0 | spawn_y,inertia_scale | spawn_y=0.04, inertia_scale=2.0 |
| C2954 | 68aec3e1ca3e0835 | spawn_y,inertia_scale | spawn_y=-0.04, inertia_scale=2.0 |
| C2955 | 06b2144ba193efd7 | spawn_y,inertia_scale | spawn_y=-0.032, inertia_scale=1.85 |
| C2956 | 22177f21da1c7c12 | spawn_y,inertia_scale | spawn_y=-0.024, inertia_scale=1.7 |
| C2957 | 7cf71bbaa4bc0354 | spawn_y,inertia_scale | spawn_y=-0.016, inertia_scale=1.55 |
| C2958 | 27db9027f1f287b5 | spawn_y,inertia_scale | spawn_y=-0.008, inertia_scale=1.4 |
| C2959 | 8904aea0a484e527 | spawn_y,inertia_scale | spawn_y=0.008, inertia_scale=1.1 |
| C2960 | 659cccc0d0114f21 | spawn_y,inertia_scale | spawn_y=0.016, inertia_scale=0.95 |
| C2961 | d0051d6e1a704236 | spawn_y,inertia_scale | spawn_y=0.024, inertia_scale=0.8 |
| C2962 | 044258f8625cef12 | spawn_y,inertia_scale | spawn_y=0.032, inertia_scale=0.65 |
| C2963 | 592c966517707b30 | spawn_y,inertia_scale | spawn_y=0.04, inertia_scale=0.5 |
| C2964 | 85763d13322aa8ef | spawn_yaw,inertia_scale | spawn_yaw=-0.523598775598, inertia_scale=0.5 |
| C2965 | 91a7b91f92dcda3f | spawn_yaw,inertia_scale | spawn_yaw=-0.418879020478, inertia_scale=0.65 |
| C2966 | a036e19424f86bdb | spawn_yaw,inertia_scale | spawn_yaw=-0.314159265359, inertia_scale=0.8 |
| C2967 | 669c5c95f67c130f | spawn_yaw,inertia_scale | spawn_yaw=-0.209439510239, inertia_scale=0.95 |
| C2968 | 241becdd3c5bcd19 | spawn_yaw,inertia_scale | spawn_yaw=-0.10471975512, inertia_scale=1.1 |
| C2969 | 39e2224fc55f809a | spawn_yaw,inertia_scale | spawn_yaw=0.10471975512, inertia_scale=1.4 |
| C2970 | bdba70aeb1c18fe0 | spawn_yaw,inertia_scale | spawn_yaw=0.209439510239, inertia_scale=1.55 |
| C2971 | 9100cc5d24cd10e7 | spawn_yaw,inertia_scale | spawn_yaw=0.314159265359, inertia_scale=1.7 |
| C2972 | 44dc0425d4513edd | spawn_yaw,inertia_scale | spawn_yaw=0.418879020478, inertia_scale=1.85 |
| C2973 | 3fb58310140fad9a | spawn_yaw,inertia_scale | spawn_yaw=0.523598775598, inertia_scale=2.0 |
| C2974 | ef5560112f596b53 | spawn_yaw,inertia_scale | spawn_yaw=-0.523598775598, inertia_scale=2.0 |
| C2975 | 4f0185f3c3cbbc00 | spawn_yaw,inertia_scale | spawn_yaw=-0.418879020478, inertia_scale=1.85 |
| C2976 | a4c4bc9d027b4e65 | spawn_yaw,inertia_scale | spawn_yaw=-0.314159265359, inertia_scale=1.7 |
| C2977 | 15fe1d60a8846207 | spawn_yaw,inertia_scale | spawn_yaw=-0.209439510239, inertia_scale=1.55 |
| C2978 | 15bb974e47e18377 | spawn_yaw,inertia_scale | spawn_yaw=-0.10471975512, inertia_scale=1.4 |
| C2979 | 936a86774b9119d7 | spawn_yaw,inertia_scale | spawn_yaw=0.10471975512, inertia_scale=1.1 |
| C2980 | c5f8183a3f724e38 | spawn_yaw,inertia_scale | spawn_yaw=0.209439510239, inertia_scale=0.95 |
| C2981 | dcfb4f428d5315c4 | spawn_yaw,inertia_scale | spawn_yaw=0.314159265359, inertia_scale=0.8 |
| C2982 | f0beb560dd6505d7 | spawn_yaw,inertia_scale | spawn_yaw=0.418879020478, inertia_scale=0.65 |
| C2983 | 3bcced3eaefa1f25 | spawn_yaw,inertia_scale | spawn_yaw=0.523598775598, inertia_scale=0.5 |
