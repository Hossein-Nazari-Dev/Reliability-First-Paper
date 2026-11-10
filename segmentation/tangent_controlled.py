"""Tangent-controlled segmentation. Return ordered curve parameters."""

from math import acos, hypot, isfinite, radians


def unit_tangent(tangent):
    length = hypot(*tangent)
    if not isfinite(length) or length == 0:
        return None
    return tuple(component / length for component in tangent)


def tangent_controlled(domain, angle_degrees, tangent_at, sample_count=200):
    """Retain a candidate if it turns sufficiently from the last retained tangent."""
    start, end = domain
    if not start < end or not 0 < angle_degrees <= 180 or sample_count < 3:
        raise ValueError("Use an increasing domain, angle in (0, 180], and at least three samples.")

    parameters = [start]
    reference = unit_tangent(tangent_at(start))
    if reference is None:
        return [start, end]

    step = (end - start) / (sample_count - 1)
    angle_threshold = radians(angle_degrees)
    for i in range(1, sample_count - 1):
        t = start + i * step
        candidate = unit_tangent(tangent_at(t))
        if candidate is None:
            continue
        cosine = sum(a * b for a, b in zip(reference, candidate))
        if acos(max(-1.0, min(1.0, cosine))) >= angle_threshold:
            parameters.append(t)
            reference = candidate
    parameters.append(end)
    return parameters


if __name__ == "__main__":
    from math import cos, sin, tau

    print(tangent_controlled((0.0, tau), 45, lambda t: (-sin(t), cos(t))))
