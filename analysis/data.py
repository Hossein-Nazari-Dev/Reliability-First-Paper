"""Read the public dataset and apply its recorded refinement order."""

import csv
import math
from pathlib import Path
from openpyxl import load_workbook

CLIMATES = ("Tehran", "Glasgow")
TARGETS = (5.0, 3.0, 0.86, 0.4)
TOLERANCES = (0.05, 0.1, 0.2, 0.3, 0.5)
PRIMARY_TOLERANCE = 0.2
EPSILON = 1e-12
PROFILES = ("circle", "ellipse", "cross", "N2", "N3", "polycurve")
METHODS = (
    "uniform_by_length", "uniform_by_parameter", "adaptive_by_curvature",
    "adaptive_by_tangent", "adaptive_by_chord",
)
REFERENCE_PROFILE = {"nurbs 2d": "N2", "nurbs 3d": "N3"}
RADIATION_FIELDS = {
    "out:segment number": "segments", "out:incident radiation": "radiation_mwh",
    "out:Emax": "mce_m", "out:Erel": "rmce_fraction", "out:shape area": "area_m2",
}
VALIDATION_FIELDS = {
    "out:Heating (kWh/m2)": "heating", "out:Cooling (kWh/m2)": "cooling",
    "out:EUI (kWh/m2)": "eui", "out:Avr Illuminance (lux)": "illuminance",
    "out:daylighting sensor number": "sensor_count",
}

def read_reference_results(path):
    """Return the reference radiation and geometric error indexed by climate, profile, and N."""
    book = load_workbook(path, read_only=True, data_only=True)
    references = {}
    try:
        for climate in CLIMATES:
            profile = None
            for label, count, radiation, mce in book[climate].iter_rows(min_row=2, values_only=True):
                if label:
                    profile = REFERENCE_PROFILE.get(label, label)
                key = (climate, profile, int(count))
                if key in references or not math.isfinite(radiation) or radiation <= 0:
                    raise ValueError(f"Invalid reference row: {key}")
                references[key] = (radiation, mce)
    finally:
        book.close()
    expected = {(c, p, n) for c in CLIMATES for p in PROFILES for n in (200, 500, 1000, 2000, 4000)}
    if set(references) != expected:
        raise ValueError("Expected all five reference resolutions for each climate and profile.")
    return references

def read_sequences(path, method, *, validation=False):
    """Return WWR-keyed sequences, ordered from coarse to fine by the input control."""
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        control, = [k for k in reader.fieldnames if k.startswith("in:") and k != "in:WWR"]
        fields = RADIATION_FIELDS | (VALIDATION_FIELDS if validation else {})
        by_wwr = {}
        for row in reader:
            if row["status"] != "Completed":
                raise ValueError(f"{path}: this analysis expects the distributed completed observations.")
            values = {name: float(row[k]) for k, name in fields.items()}
            values["control"] = float(row[control])
            if not all(math.isfinite(value) and value >= 0 for value in values.values()):
                raise ValueError(f"{path}: missing or invalid numeric output")
            n = values["segments"]
            if n < 3 or int(n) != n or values["radiation_mwh"] <= 0:
                raise ValueError(f"{path}: invalid segment count or radiation")
            values["segments"] = int(n)
            wwr = float(row["in:WWR"]) if validation else None
            by_wwr.setdefault(wwr, []).append(values)
    if not by_wwr:
        raise ValueError(f"{path}: empty dataset")
    for rows in by_wwr.values():
        if len({row["control"] for row in rows}) != len(rows):
            raise ValueError(f"{path}: repeated input controls")
        rows.sort(key=lambda row: row["control"], reverse=method.startswith("adaptive"))
    return by_wwr

def radiation_cases(root):
    for climate in CLIMATES:
        for path in sorted((root / climate).glob("*/*/results.csv")):
            yield climate, path.parent.parent.name, path.parent.name, path

def profile_id(case):
    return case.removesuffix("_with_kinks").removesuffix("_without_kinks")

def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Cannot write an empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

