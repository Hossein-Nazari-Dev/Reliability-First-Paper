"""Reproduce the three radiation selection rules and rank complete cases."""

from statistics import correlation, mean

from .data import (CLIMATES, EPSILON, METHODS, PRIMARY_TOLERANCE, PROFILES, TARGETS, TOLERANCES,
                   profile_id, radiation_cases, read_sequences)


def radiation_errors(rows, reference):
    return [100 * abs(row["radiation_mwh"] - reference) / reference for row in rows]


def reliable_start(errors, tolerance):
    """Return the zero-based start after the last increase that exceeds tolerance."""
    return max((i for i, (a, b) in enumerate(zip(errors, errors[1:]), 1)
                if b - a > tolerance + EPSILON), default=0)


def sustained_start(errors, target):
    """Return the start of the terminal in-band suffix, or len(errors) if empty."""
    return max((i for i, error in enumerate(errors, 1) if error > target + EPSILON), default=0)


def pick_minimum(rows, start):
    return min(range(start, len(rows)), key=lambda i: (
        rows[i]["segments"], rows[i]["rmce_fraction"], -i
    ), default=None)


def distinct_outputs(rows):
    fields = ("segments", "mce_m", "rmce_fraction", "radiation_mwh")
    return len({tuple(row[key] for key in fields) for row in rows})


def selection_fields(rule, index, rows, errors):
    if index is None:
        return {f"{rule}_{k}": None for k in (
            "segments", "step", "control", "radiation_deviation_pct", "rmce_pct", "tail_distinct", "tail_max_pct"
        )}
    row = rows[index]
    return {
        f"{rule}_segments": row["segments"],
        f"{rule}_step": index + 1,
        f"{rule}_control": row["control"],
        f"{rule}_radiation_deviation_pct": errors[index],
        f"{rule}_rmce_pct": 100 * row["rmce_fraction"],
        f"{rule}_tail_distinct": distinct_outputs(rows[index:]),
        f"{rule}_tail_max_pct": max(errors[index:]),
    }


def analyze_radiation(root, references):
    comparisons, scores, continuity, geometry = [], [], [], []
    for climate, method, case, path in radiation_cases(root):
        profile = profile_id(case)
        rows = read_sequences(path, method)[None]
        errors = radiation_errors(rows, references[climate, profile, 4000][0])
        paired_parameter = climate == "Tehran" and method == "uniform_by_parameter" and profile in ("cross", "polycurve")
        paired_arc_length = method == "uniform_by_length" and profile == "polycurve"
        if paired_parameter or paired_arc_length:
            i = reliable_start(errors, PRIMARY_TOLERANCE)
            continuity.append(dict(climate=climate, profile=profile, algorithm=method,
                                   preservation=case.endswith("_with_kinks"),
                                   entry_segments=rows[i]["segments"], region_rows=len(rows) - i,
                                   region_distinct=distinct_outputs(rows[i:])))
        if case.endswith("_without_kinks"):
            continue
        if climate == "Tehran" and (profile, method) in (
            ("ellipse", "uniform_by_length"), ("polycurve", "adaptive_by_chord")
        ):
            region = reliable_start(errors, PRIMARY_TOLERANCE)
            observations = {}
            for row, error in zip(rows[region:], errors[region:]):
                key = (row["segments"], row["mce_m"], row["rmce_fraction"], row["radiation_mwh"])
                observations.setdefault(key, error)
            for j, field in ((0, "segments"), (2, "rmce_fraction")):
                x = [key[j] for key in observations]
                y = list(observations.values())
                pearson = correlation(x, y) if len(set(x)) > 1 and len(set(y)) > 1 else None
                geometry.append(dict(climate=climate, profile=profile, algorithm=method,
                                     descriptor=field, observations=len(x), pearson_r=pearson))
        for tau in TOLERANCES:
            region = reliable_start(errors, tau)
            selections, target_counts, short_tails = [], {}, 0
            for target in TARGETS:
                first = next((i for i, error in enumerate(errors) if error <= target + EPSILON), None)
                start = sustained_start(errors, target)
                sustained = pick_minimum(rows, start)
                screened = pick_minimum(rows, max(start, region))
                target_counts[f"segments_at_{target:g}_pct"] = rows[screened]["segments"] if screened is not None else None
                if screened is not None:
                    selections.append(rows[screened]["segments"])
                    short_tails += distinct_outputs(rows[screened:]) < 3
                if tau == PRIMARY_TOLERANCE:
                    item = dict(climate=climate, profile=profile, algorithm=method, target_pct=target,
                                region_entry_step=region + 1, region_rows=len(rows) - region,
                                region_distinct=distinct_outputs(rows[region:]))
                    for rule, index in (("first", first), ("sustained", sustained), ("screened", screened)):
                        item.update(selection_fields(rule, index, rows, errors))
                    item["first_later_leaves_band"] = first is not None and max(errors[first:]) > target + EPSILON
                    item["screen_changes_selection"] = sustained is not None and screened is not None and sustained != screened
                    comparisons.append(item)
            scores.append(dict(climate=climate, profile=profile, algorithm=method, tau_pp=tau,
                               targets_reached=len(selections), mean_segments=mean(selections) if len(selections) == 4 else None,
                               short_tails=short_tails, **target_counts))
    for row in scores:
        score = row["mean_segments"]
        row["rank"] = None if score is None else 1 + sum(
            other["mean_segments"] is not None and other["mean_segments"] < score
            for other in scores if (other["climate"], other["profile"], other["tau_pp"]) ==
            (row["climate"], row["profile"], row["tau_pp"])
        )
    return comparisons, scores, continuity, geometry


def summarize_acceptance(rows):
    summary = []
    for climate in ("Tehran", "Glasgow"):
        for target in TARGETS:
            group = [r for r in rows if r["climate"] == climate and r["target_pct"] == target]
            summary.append(dict(climate=climate, target_pct=target, comparisons=len(group),
                                first_entry_later_exit=sum(r["first_later_leaves_band"] for r in group),
                                sustained_targets=sum(r["sustained_segments"] is not None for r in group),
                                screening_changes=sum(r["screen_changes_selection"] for r in group)))
    return summary


def summarize_selections(rows):
    choices = {(r["climate"], r["profile"], r["algorithm"], r["target_pct"]):
               r["screened_segments"] for r in rows}
    result = []
    for profile in PROFILES:
        for climate in CLIMATES:
            for method in METHODS:
                record = dict(profile=profile, climate=climate, algorithm=method)
                for target in TARGETS:
                    key = (climate, profile, method, target)
                    if key not in choices:
                        if method != "adaptive_by_curvature" or profile not in ("circle", "cross"):
                            raise ValueError(f"Missing comparison: {key}")
                        value = "N/A"
                    else:
                        count = choices[key]
                        value = "Not reached" if count is None else count
                    record[f"segments_at_{target:g}_pct"] = value
                result.append(record)
    return result
