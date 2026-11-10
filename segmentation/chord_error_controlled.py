"""Chord-error-controlled segmentation. Return ordered curve parameters."""

from math import dist, isfinite


def distance_to_segment(point, start, end):
    """Euclidean distance to the finite chord, including a collapsed chord."""
    chord = tuple(b - a for a, b in zip(start, end))
    squared_length = sum(component**2 for component in chord)
    if squared_length == 0:
        return dist(point, start)

    projection = sum((p - a) * d for p, a, d in zip(point, start, chord)) / squared_length
    fraction = max(0.0, min(1.0, projection))
    closest = tuple(a + fraction * d for a, d in zip(start, chord))
    return dist(point, closest)


def chord_error_controlled(domain, error_tolerance, point_at, arc_length, minimum_length=0.01):
    """Split each interval at its sampled maximum curve-to-chord distance."""
    start, end = domain
    if not start < end or not 0 < error_tolerance or not 0 <= minimum_length:
        raise ValueError("Use an increasing domain, positive tolerance, and nonnegative minimum length.")

    parameters = [start]
    parameter_epsilon = 1e-9 * (end - start)
    subdivisions = 20  # Fixed within-interval error evaluation, as used in the study.

    def subdivide(a, b):
        if arc_length(a, b) <= minimum_length:
            parameters.append(b)
            return

        pa, pb = point_at(a), point_at(b)
        maximum_error = 0.0
        split = (a + b) / 2
        for i in range(1, subdivisions):
            t = a + (b - a) * i / subdivisions
            error = distance_to_segment(point_at(t), pa, pb)
            if isfinite(error) and error > maximum_error:
                maximum_error, split = error, t
        if maximum_error <= error_tolerance or min(split - a, b - split) <= parameter_epsilon:
            parameters.append(b)
            return

        subdivide(a, split)
        subdivide(split, b)

    subdivide(start, end)
    return parameters


if __name__ == "__main__":
    from math import cos, sin, tau

    print(chord_error_controlled((0.0, tau), 0.02, lambda t: (cos(t), sin(t)), lambda a, b: b - a))
