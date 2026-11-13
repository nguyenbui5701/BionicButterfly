"""Pure M0 algebra. A result confers no runtime output/ARM permission."""


def mix_m0(flap_micro: int, steer_micro: int) -> tuple[int, int, tuple[str, ...]]:
    if type(flap_micro) is not int or type(steer_micro) is not int:
        raise TypeError("M0 inputs must be integers, excluding booleans")
    if not 0 <= flap_micro <= 1_000_000 or not -1_000_000 <= steer_micro <= 1_000_000:
        raise ValueError("M0 input outside approved domain")
    left, right = flap_micro - steer_micro, flap_micro + steer_micro
    tags = []
    for side, value in (("LEFT", left), ("RIGHT", right)):
        if value < 0:
            tags.append(side + "_LOW")
        elif value > 1_000_000:
            tags.append(side + "_HIGH")
    return max(0, min(1_000_000, left)), max(0, min(1_000_000, right)), tuple(sorted(tags))


mixM0 = mix_m0
