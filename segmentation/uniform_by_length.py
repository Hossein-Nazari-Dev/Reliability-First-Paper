"""Uniform arc-length segmentation. Return ordered curve parameters."""


def uniform_by_length(domain, segment_count, arc_length):
    """Find equal arc-length fractions using arc_length(a, b) in model units."""
    start, end = domain
    if not start < end or segment_count < 2:
        raise ValueError("Use an increasing domain and at least two segments.")

    total_length = arc_length(start, end)
    if not total_length > 0:
        raise ValueError("The curve must have positive length.")

    parameters = [start]
    for i in range(1, segment_count):
        target_length = total_length * i / segment_count
        lower, upper = parameters[-1], end
        for _ in range(48):
            midpoint = (lower + upper) / 2
            if arc_length(start, midpoint) < target_length:
                lower = midpoint
            else:
                upper = midpoint
        parameters.append((lower + upper) / 2)
    parameters.append(end)
    return parameters


if __name__ == "__main__":
    # Curve C(t) = (t**2, 0) on [0, 1].
    print(uniform_by_length((0.0, 1.0), 4, lambda a, b: b**2 - a**2))
