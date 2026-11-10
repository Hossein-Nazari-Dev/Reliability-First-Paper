"""Run the article's numerical analyses on the distributed CSV files."""

from argparse import ArgumentParser
from pathlib import Path
from .data import read_reference_results, write_csv
from .screening import analyze_radiation, summarize_acceptance, summarize_selections
from .validation import analyze_validation


def main():
    root = Path(__file__).resolve().parents[1]
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=root / "data")
    parser.add_argument("--output", type=Path, default=root / "outputs")
    args = parser.parse_args()
    references = read_reference_results(args.data / "baselines.xlsx")
    comparisons, scores, continuity, geometry_correlations = analyze_radiation(args.data / "radiation", references)
    correlations, selections, sensors, geometry = analyze_validation(args.data / "validation", references)
    sensitivity = [
        dict(climate=c, profile=p, segments=n, radiation_mwh=rad, sampled_mce_m=mce,
             signed_difference_pct=100*(rad-references[c,p,4000][0])/references[c,p,4000][0])
        for (c,p,n),(rad,mce) in sorted(references.items())
    ]
    tables = {
        "reference_sensitivity": sensitivity, "acceptance_rules": comparisons,
        "supplementary_s1_summary": summarize_acceptance(comparisons), "algorithm_ranks": scores,
        "supplementary_s2_selections": summarize_selections(comparisons),
        "continuity_point_comparison": continuity, "geometric_associations": geometry_correlations,
        "validation_correlations": correlations,
        "validation_selections": selections, "sensor_correlations": sensors,
        "validation_geometry": geometry,
    }
    for name, rows in tables.items():
        write_csv(args.output / (name + ".csv"), rows)
        print(f"{name}.csv  {len(rows)} rows")


if __name__ == "__main__":
    main()

