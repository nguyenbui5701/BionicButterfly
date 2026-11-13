"""PC-only scheduling views; enumeration does not authorize runtime output."""

from .scheduler import VirtualTickBatch, iter_virtual_ticks

__all__ = ["VirtualTickBatch", "iter_virtual_ticks"]
