# src/gicd/scan.py
def run_gicd_scan(substrate):
    checks = {
        "Authority Ambiguity": verify_authority(substrate),
        "Incentive Misalignment": verify_incentives(substrate),
        "Cost Externalization": verify_costs(substrate),
        "Governance Capture": verify_governance(substrate),
        "Jurisdiction Compliance": verify_jurisdiction(substrate)  # NEW
    }
    return checks

def verify_jurisdiction(substrate):
    valid_regions = ["ca-central-1", "canadaeast"]
    if substrate.get("cloud_region") not in valid_regions:
        return {"status": "FAIL", "details": "Data residency violation"}
    return {
        "status": "PASS",
        "details": {
            "jurisdiction": substrate.get("jurisdiction", "CA-FED"),
            "cloud_region": substrate["cloud_region"]
        }
    }
