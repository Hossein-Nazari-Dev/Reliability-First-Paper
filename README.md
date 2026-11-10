# Reliability First

Data and Python code accompanying *Reliability First: Assessing Geometric Approximation in Building Performance Simulation*.

## Contents

| Path | Contents |
| --- | --- |
| [data/radiation](data/radiation) | Completed incident-radiation observations for Tehran and Glasgow, organized by method and profile |
| [data/validation](data/validation) | Energy and daylight validation for the ellipse and complex composite profile at three window-to-wall ratios |
| [data/baselines.xlsx](data/baselines.xlsx) | Radiation references for six profiles, two climates and five reference resolutions |
| [segmentation](segmentation) | Five standalone Python implementations of the vertex-selection rules |
| [analysis](analysis) | Reproducible radiation screening, ranking, continuity comparisons and validation analyses |
| [supplementary](supplementary) | Excel tables S1 and S2 and their reading guide |

The datasets are available for independent evaluation and additional analyses. See the [data dictionary](data/README.md) for units, file coverage and data conventions.

## Run the analysis

Use Python 3.12 or later. From the repository root, run:

```sh
python -m pip install -r requirements.txt
python -m analysis
```

The command reads the supplied inputs and writes CSVs to `outputs/`. Use `--output <directory>` for another location. No simulation software is required to reproduce the analysis from the recorded outputs.

| Output | What it reports |
| --- | --- |
| `reference_sensitivity.csv` | Signed deviations from each matching 4000-segment radiation reference |
| `acceptance_rules.csv` | First entry, sustained selection, and reliable-region selection for each climate, profile, method and target at the primary tolerance |
| `supplementary_s1_summary.csv` | S1 counts by climate and target |
| `supplementary_s2_selections.csv` | S2 segment counts by profile, climate, algorithm and radiation target |
| `algorithm_ranks.csv` | Mean selected segment counts and ranks for all five tested screening tolerances |
| `continuity_point_comparison.csv` | Reliable-region entry for the with- and without-preservation comparisons |
| `geometric_associations.csv` | Pearson coefficients for the two Tehran examples in Figure 9 |
| `validation_correlations.csv` | Descriptive Pearson and Spearman coefficients by output, climate, profile, WWR and refinement scope |
| `validation_selections.csv` | Selected-model and subsequent refinement differences relative to the final validation model |
| `sensor_correlations.csv` | Association between magnitudes of successive sensor-count and illuminance changes for the composite profile |
| `validation_geometry.csv` | Footprint area and derived volume at the 0.4% selection and final validation model |

The primary screening tolerance is 0.2 percentage points. The radiation targets are 5%, 3%, 0.86%, and 0.4%. Method ranking selects the minimum actual segment count among eligible observations and averages over all four targets. The validation analysis selects the first eligible refinement step. Radiation deviations use the matching 4000-segment reference. Downstream differences use the final recorded model for the same profile, climate and WWR.

The Python implementations can also be run individually for small examples. Their curve-evaluation callbacks can be supplied by a geometry library. See [CurvAdapt Wiki](https://nexonest.com/curvadapt-wiki.html) for the corresponding Grasshopper components and their controls.

