from __future__ import annotations

from nadi.provenance import audit_manifest, freeze_manifest


def test_core_resources_freeze_and_verify():
    freeze_manifest()
    result = audit_manifest()
    assert result["passed"], result

