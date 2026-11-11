# Dataset dictionary

The radiation directory contains **20,176 completed observations** in 60 CSVs. Continuity-point comparisons cover uniform parameter segmentation of the filleted cross and complex composite profile in Tehran, and uniform arc-length segmentation of the complex composite profile in both Tehran and Glasgow. The validation directory contains **1,524 completed cases** in four CSVs. The baseline workbook contains **60** reference results. Successful observations retain their recorded values and row order, including repeated numerical outputs. Failed observations and run-management fields are excluded from these review exports. In the original runs used here, the excluded failures occurred before the successful refinement sequence.

## Directory keys

- `circle`, `ellipse`, `cross`, `N2`, `N3`, and `polycurve` identify the six reference profiles. `N2` and `N3` are the degree-2 and degree-3 NURBS profiles. `polycurve` is the complex composite profile.
- `_with_kinks` identifies the configuration with automatic C1 continuity-point preservation. `_without_kinks` identifies the comparison configuration without that detection. The primary comparison uses `_with_kinks` where those variants exist.
- The curvature-threshold method was excluded from graded comparison for the circle and filleted cross.

## CSV fields

| Field | Meaning |
| --- | --- |
| `status`, `error` | Run status and diagnostic text |
| `in:...` | Method-specific input control. Uniform methods use requested segment count. Adaptive thresholds are chord error in metres, curvature in inverse metres, or tangent angle in degrees. |
| `in:WWR` | Window-to-wall ratio, expressed as a fraction |
| `out:segment number` | Actual number of polyline segments |
| `out:Emax` | Sampled maximum chord error, in metres |
| `out:Erel` | Sampled maximum chord error divided by the 200 m reference-profile length, expressed as a fraction |
| `out:incident radiation` | Annual incident solar energy on the assessed geometry, in MWh |
| `out:shape area` | Footprint area, in m² |
| `out:Heating (kWh/m2)`, `out:Cooling (kWh/m2)`, `out:EUI (kWh/m2)` | Annual floor-area-normalized energy outputs |
| `out:Avr Illuminance (lux)` | Average illuminance, in lux |
| `out:daylighting sensor number` | Number of daylight sensors |

The baseline workbook uses the same radiation and MCE units. Its resolutions are 200, 500, 1000, 2000 and 4000 segments. The SHA-256 inventory records the exact distributed dataset files.

