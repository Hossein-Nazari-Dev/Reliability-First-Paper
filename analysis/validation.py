"""Reproduce descriptive radiation, energy and daylight comparisons."""

from statistics import correlation
from .data import CLIMATES, EPSILON, PRIMARY_TOLERANCE, TARGETS, TOLERANCES, read_sequences
from .screening import radiation_errors, reliable_start, sustained_start

CASES = {"ellipse": ("uniform_by_parameter", "ellipse"), "polycurve": ("adaptive_by_chord", "polycurve_with_kinks")}
METRICS = ("heating", "cooling", "eui", "illuminance")
WWRS = (0.3, 0.5, 0.7)


def associations(x, y):
    if len(x) < 2 or len(set(x)) < 2 or len(set(y)) < 2:
        return None, None
    return correlation(x, y), correlation(x, y, method="ranked")


def differences(values):
    return [b - a for a, b in zip(values, values[1:])]


def relative_errors(values, endpoint):
    if endpoint == 0:
        return None
    return [100 * abs(value - endpoint) / abs(endpoint) for value in values]


def analyze_validation(root, references):
    correlations, selections, sensor, geometry = [], [], [], []
    for city in CLIMATES:
        for profile, (method, case) in CASES.items():
            grid = read_sequences(root / city / method / case / "results.csv", method, validation=True)
            expected = 198 if profile == "ellipse" else 56
            if set(grid) != set(WWRS) or any(len(rows) != expected for rows in grid.values()):
                raise ValueError(f"Incomplete validation grid for {city} / {profile}")
            keys = ("control", "segments", "radiation_mwh", "mce_m", "rmce_fraction", "area_m2")
            paths = [[tuple(row[k] for k in keys) for row in grid[w]] for w in WWRS]
            if paths[0] != paths[1] or paths[0] != paths[2]:
                raise ValueError(f"Geometry or radiation differs across WWRs for {city} / {profile}")
            for wwr, rows in grid.items():
                base = dict(climate=city, profile=profile, wwr=wwr)
                rad = [row["radiation_mwh"] for row in rows]
                errors = radiation_errors(rows, references[city, profile, 4000][0])
                start = reliable_start(errors, PRIMARY_TOLERANCE)
                for metric in METRICS:
                    output = [row[metric] for row in rows]
                    error = relative_errors(output, output[-1])
                    for scope, i in (("full_sequence", 0), ("reliable_region", start)):
                        x, y = rad[i:], output[i:]
                        series = {"levels": (x, y), "successive_changes": (differences(x), differences(y))}
                        if error is not None:
                            series["absolute_reference_relative_deviations"] = (errors[i:], error[i:])
                        for kind, (a, b) in series.items():
                            pearson, spearman = associations(a, b)
                            correlations.append(dict(**base, metric=metric, scope=scope, series=kind,
                                                     observations=len(a), pearson_r=pearson, spearman_rho=spearman))
                    for tau in TOLERANCES:
                        begin = reliable_start(errors, tau)
                        for target in TARGETS:
                            index = max(begin, sustained_start(errors, target))
                            if index == len(rows):
                                continue
                            row = rows[index]
                            selections.append(dict(**base, metric=metric, tau_pp=tau, target_pct=target,
                                                   selected_step=index+1, segments=row["segments"], control=row["control"],
                                                   selected_value=output[index], final_value=output[-1],
                                                   final_segments=rows[-1]["segments"],
                                                   difference_pct=error[index] if error is not None else None,
                                                   tail_max_difference_pct=max(error[index:]) if error is not None else None))
                if wwr == 0.5:
                    i = max(start, sustained_start(errors, 0.4))
                    if i < len(rows):
                        selected_area, final_area = rows[i]["area_m2"], rows[-1]["area_m2"]
                        geometry.append(dict(climate=city, profile=profile, selected_segments=rows[i]["segments"],
                                             final_segments=rows[-1]["segments"], selected_area_m2=selected_area,
                                             final_area_m2=final_area, selected_volume_m3=3*selected_area,
                                             final_volume_m3=3*final_area, difference_pct=100*(selected_area-final_area)/final_area))
                if profile == "polycurve":
                    a = [abs(v) for v in differences([r["sensor_count"] for r in rows[start:]])]
                    b = [abs(v) for v in differences([r["illuminance"] for r in rows[start:]])]
                    for exclude in (False, True):
                        idx = [i for i in range(len(a)) if not exclude or start+i+1 not in (23, 44)]
                        pearson, _ = associations([a[i] for i in idx], [b[i] for i in idx])
                        sensor.append(dict(**base, excluded_principal_transitions=exclude,
                                           transitions=len(idx), pearson_r=pearson))
    return correlations, selections, sensor, geometry

