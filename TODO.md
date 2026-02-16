# Project TODOs

This file collects all pending tasks and ideas for improvement found in the codebase.

## Features
- [ ] **Online Repository for the data**: Implement functionality to fetch data from an online repository.
- [ ] **Groupby per "imageset"**: Add capability to group data by "imageset".
- [ ] **Deselect Numerics**: Allow users to deselect numeric columns from analysis/visualization.
- [ ] **Dynamic Layout**: Currently x, y, z layout configurations are hardcoded for `multifil`. Make this dynamic based on dataset.

## Visualization
- [ ] **Dynamic Binning**: In `generate_plot` (functions.py), `nbinsx` and `nbinsy` for marginal plots (histogram/violin) should be dynamic, not hardcoded (currently 512 in comments).

## Bugs (Fixed)
- [x] **Histogram Click**: Clicking on histograms caused a crash due to missing `customdata`. Fixed in `callbacks.py`.
