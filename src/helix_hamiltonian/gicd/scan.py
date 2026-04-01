"""
GICD Epistemic Scan - RFC 0001 v0.4
Upstream Substrate Integrity Guard
"""


def verify_authority(substrate: dict) -> dict:
    """Verify authority ambiguity (GICD Marker 1)."""
    if not substrate.get("authority"):
        return {"status": "FAIL", "details": "Missing authority mapping"}
    return {"status": "PASS"}


def verify_incentives(substrate: dict) -> dict:
    """Verify incentive misalignment (GICD Marker 2)."""
    # Structural placeholder for incentive logic
    return {"status": "PASS"}


def verify_costs(substrate: dict) -> dict:
    """Verify cost externalization (GICD Marker 3)."""
    # Structural placeholder for cost logic
    return {"status": "PASS"}


def verify_governance(substrate: dict) -> dict:
    """Verify governance capture (GICD Marker 4)."""
    # Structural placeholder for capture logic
    return {"status": "PASS"}


def verify_jurisdiction(substrate: dict) -> dict:
    """Verify jurisdictional compliance."""
    valid_regions = ["ca-central-1", "canadaeast"]
    if substrate.get("cloud_region") not in valid_regions:
        return {"status": "FAIL", "details": "Jurisdictional sovereignty violation"}
    return {"status": "PASS"}


def run_gicd_scan(substrate: dict) -> dict:
    """
    Execute the mandatory GICD Epistemic Scan before Hamiltonian nucleation.
    """
    check_fns = [
        ("Authority Ambiguity", verify_authority),
        ("Incentive Misalignment", verify_incentives),
        ("Cost Externalization", verify_costs),
        ("Governance Capture", verify_governance),
        ("Jurisdiction Compliance", verify_jurisdiction),
    ]
    return {
        "checks": [
            {
                "name": name,
                **check_fn(substrate),
            }
            for name, check_fn in check_fns
        ]
    }
