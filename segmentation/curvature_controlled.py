"""Curvature-controlled segmentation. Return ordered curve parameters."""

from math import isfinite


def curvature_controlled(domain, curvature_threshold, curvature_at, sample_count=200):
    """Retain candidates whose curvature magnitude reaches the threshold."""
    start, end = domain
    if not start < end or not 0 <= curvature_threshold or sample_count < 3:
        raise ValueError("Use an increasing domain, nonnegative threshold, and at least three samples.")

    parameters = [start]
    step = (end - start) / sample_count
    for i in range(1, sample_count):
        t = start + i * step
        curvature = abs(curvature_at(t))
        if isfinite(curvature) and curvature >= curvature_threshold:
            parameters.append(t)
    parameters.append(end)
    return parameters


if __name__ == "__main__":
    from math import tau

    # Curvature of a unit circle is constant.
    print(curvature_controlled((0.0, tau), 0.75, lambda t: 1.0, sample_count=8))
