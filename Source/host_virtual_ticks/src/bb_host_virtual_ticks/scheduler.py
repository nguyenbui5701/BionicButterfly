"""One-pass, lazy enumeration of the approved fixed 5 ms clock plan."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from bb_host_preflight_m0 import AcceptedPreflight

_STEP_US = 5000


@dataclass(frozen=True, slots=True)
class VirtualTickBatch:
    """Immutable grouping of original observations, not a committed decision."""

    tick_index: int
    eval_at_us: int
    events: tuple[Mapping, ...]


def iter_virtual_ticks(accepted: AcceptedPreflight) -> Iterator[VirtualTickBatch]:
    """Return a fresh one-shot iterator over every tick, T0 through duration.

    Pass a result from TASK-001 validate_wire, not a manually constructed result.
    Wrong input types/obviously broken boundary objects fail at call time, before
    any iterator/tick is returned. This checks the trusted library boundary; it
    neither revalidates JSON nor authenticates host execution permission.

    Events retain object identity, values and source order. Each invocation has
    independent local state; only its current batch and one lookahead are held.
    """
    if type(accepted) is not AcceptedPreflight:
        raise TypeError("expected TASK-001 AcceptedPreflight from validate_wire")
    scenario = accepted.scenario
    if accepted.status != "ACCEPTED_PREFLIGHT" or type(scenario) is not MappingProxyType:
        raise ValueError("expected the immutable preflight result boundary")
    events = scenario["events"]
    duration = scenario["duration_us"]
    if type(events) is not tuple or type(duration) is not int:
        raise ValueError("expected validated events and integer duration")
    if not 5000 <= duration <= 60_000_000 or duration % _STEP_US:
        raise ValueError("expected the approved duration domain")
    return _batches(events, duration)


def _batches(events: tuple, duration: int) -> Iterator[VirtualTickBatch]:
    source = iter(events)
    pending = next(source, None)
    pending_at = pending["event_at_us"] if pending is not None else None
    for tick_index, eval_at_us in enumerate(range(0, duration + 1, _STEP_US)):
        batch = []
        while pending is not None and pending_at <= eval_at_us:
            batch.append(pending)
            pending = next(source, None)
            pending_at = pending["event_at_us"] if pending is not None else None
        # Sorted, preflight-validated source timestamps ensure that all earlier
        # events were consumed already: T0={0}, other windows=(previous,T].
        yield VirtualTickBatch(tick_index, eval_at_us, tuple(batch))
