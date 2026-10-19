# Failure discovery pilot

Analyzed 230 saved episodes: 154 original failures and 76 original successes.

Found **2 candidate behavior groups**. These are not verified physical failure types.

- Failure group sizes: {'group_1': 115, 'group_2': 39}. Small groups may be outliers rather than failure types.
- Held-out silhouette: 0.2671049610454707. Higher indicates more separated groups; negative indicates overlap.
- Mean seed-subset agreement (ARI): 1.0. One means identical assignments up to group names; zero is chance-level agreement.
- Seed-subset refits collapsing to one held-out group: 0/8.
- Stable-success proxy: 69 episodes. This uses provisional thresholds and does not replace original success.

See scores.json for all assumptions and limitations. Next: inspect representatives, check threshold sensitivity, and reproduce groups on a larger sample. Physical settings are revealed in separate CSVs after grouping; no causal conclusion is established.
