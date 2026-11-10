"""Uniform parameter segmentation. Return ordered curve parameters."""


def uniform_by_parameter(domain, segment_count):
    """Divide the parameter interval into equal increments."""
    start, end = domain
    if not start < end or segment_count < 3:
        raise ValueError("Use an increasing domain and at least three segments.")

    step = (end - start) / segment_count
    return [start + i * step for i in range(segment_count)] + [end]


if __name__ == "__main__":
    print(uniform_by_parameter((0.0, 1.0), 4))
