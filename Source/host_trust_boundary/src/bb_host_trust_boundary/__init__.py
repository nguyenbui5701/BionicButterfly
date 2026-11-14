"""TEST_ONLY reference comparison. None of these data objects is a credential."""

from .boundary import (ClaimedHostFingerprint, HostReferenceAssessment,
                       HostReferenceOutcome, HostReferenceReason,
                       assess_reference_host_boundary)

__all__ = ["ClaimedHostFingerprint", "HostReferenceAssessment", "HostReferenceOutcome",
           "HostReferenceReason", "assess_reference_host_boundary"]
