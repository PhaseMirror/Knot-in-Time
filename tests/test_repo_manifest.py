import json
from pathlib import Path

from helix_hamiltonian import __version__

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_repo_manifest_is_valid_and_version_aligned():
    manifest_path = REPO_ROOT / "schemas" / "repo_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["repo"] == "helix-hamiltonian"
    assert manifest["version"] == __version__
    assert (
        manifest["canonical_documents"]["rfc_0001"]
        == "docs/sovereignty/RFC_0001-locked.md"
    )


def test_repo_manifest_verification_files_exist():
    manifest_path = REPO_ROOT / "schemas" / "repo_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for rel_path in manifest["verification"]["tests"]:
        assert (REPO_ROOT / rel_path).exists(), rel_path
