import pytest

from scripts.scenarios import load_oracles, pipeline

ORACLES = load_oracles()["cases"]


def control(identity, at=10000, arm=False, flap="0", steer="0"):
    return dict(id=identity, at_us=at, kind="CONTROL_VALID", arm=arm, flap_token=flap, steer_token=steer)


def observation(identity, kind, at=10000):
    return dict(id=identity, at_us=at, kind=kind)


@pytest.fixture
def make_batch():
    def make(events, at=10000):
        recipe = dict(duration_us=15000, target_tick_us=at,
                      events=[observation("boot", "BOOT", 0), *events])
        accepted, batches = pipeline(recipe)
        return accepted, batches[at // 5000]
    return make
