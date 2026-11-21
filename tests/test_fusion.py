from nadi.sdaif.fusion import EvidenceInterval, fuse_evidence


def test_fusion_widens_when_evidence_disagrees():
    result = fuse_evidence([
        EvidenceInterval("bio", 0.2, 0.1, 0.3, reliability=1.0),
        EvidenceInterval("telemetry", 0.8, 0.7, 0.9, reliability=1.0),
    ])
    assert result.lower < result.probability < result.upper
    assert result.dominant_uncertainty in {"bio", "telemetry"}


def test_fusion_with_no_evidence_is_full_uncertainty():
    result = fuse_evidence([])
    assert (result.probability, result.lower, result.upper, result.support) == (0.5, 0.0, 1.0, 0.0)
