# Reliability First data and code

Datasets and Python code accompanying *Reliability First: Assessing Geometric Approximation in Building Performance Simulation*.

## Contents

| Path | Contents |
| --- | --- |
| [data/radiation](data/radiation) | 20,176 completed incident-radiation observations in 60 CSV files |
| [data/validation](data/validation) | 1,524 energy and daylight cases in four CSV files |
| [data/baselines.xlsx](data/baselines.xlsx) | 60 numerical radiation references |
| [data/README.md](data/README.md) | Dataset structure, field definitions, units and conventions |
| [data/SHA256SUMS](data/SHA256SUMS) | SHA-256 checksums for the distributed dataset files |
| [segmentation](segmentation) | Five standalone Python implementations of the vertex-selection rules |
| [analysis](analysis) | Python scripts for radiation screening, selection, ranking and validation analysis |
| [supplementary](supplementary) | Excel tables S1 and S2 and their reading guide |

The CSV files are organized by climate, algorithm and profile. Successful observations retain their recorded values and row order, including repeated numerical outputs. See the data dictionary for details.

## Run the analysis

Use Python 3.12 or later. From the repository root, run:

```sh
python -m pip install -r requirements.txt
python -m analysis
```

The scripts read the supplied datasets and create CSV files in `outputs/`. To choose another output directory:

```sh
python -m analysis --output path/to/results
```

Analysis settings are defined in [analysis/data.py](analysis/data.py). The analysis operates on recorded numerical outputs; it does not require Rhino, Grasshopper or the simulation engines.

## Generated files

| Output | Contents |
| --- | --- |
| `reference_sensitivity.csv` | Reference-resolution differences |
| `acceptance_rules.csv` | First-entry, sustained and screened selections by sequence and target |
| `supplementary_s1_summary.csv` | Acceptance-rule counts by climate and target |
| `supplementary_s2_selections.csv` | Selected segment counts by profile, climate, algorithm and target |
| `algorithm_ranks.csv` | Mean selected counts and ranks for each screening tolerance |
| `continuity_point_comparison.csv` | Entry segment counts and remaining-sequence lengths for paired preservation configurations |
| `geometric_associations.csv` | Associations between geometric descriptors and radiation deviation |
| `validation_correlations.csv` | Pearson and Spearman coefficients by output, climate, profile, WWR and refinement scope |
| `validation_selections.csv` | Selected-model and subsequent-refinement differences |
| `sensor_correlations.csv` | Associations between sensor-count and illuminance changes |
| `validation_geometry.csv` | Selected and final footprint areas and derived volumes |

## Segmentation implementations

The files in [segmentation](segmentation) return ordered curve parameters. Their curve-evaluation callbacks can be supplied by a geometry library. Each file includes a small runnable example, for instance:

```sh
python segmentation/uniform_by_length.py
```

## Software documentation

- **CurvAdapt:** [Product page](https://nexonest.com/projects-pages/curvAdapt.html) · [Wiki](https://nexonest.com/curvadapt-wiki.html)
- **NexoSolve:** [Product page](https://nexonest.com/projects-pages/nexoSolve.html) · [Wiki](https://nexonest.com/nexosolve-wiki.html)
