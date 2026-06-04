#!/usr/bin/env python3
"""
Regression tests for axis-validate.py

Run with: python3 scripts/test_axis_validate.py
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Path to the validator script
SCRIPT_DIR = Path(__file__).parent
VALIDATOR = SCRIPT_DIR / "axis-validate.py"
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # Up to repo root


def run_validator(review_data, repo_path=None):
    """Run validator with given review data, return (exit_code, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(review_data, f)
        temp_path = f.name

    try:
        cmd = [sys.executable, str(VALIDATOR), temp_path]
        if repo_path:
            cmd.extend(['--repo-path', repo_path])

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    finally:
        os.unlink(temp_path)


def test_all_pass_review():
    """Test 1: All-pass review exits 0 and prints 'All checks passed'."""
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["Genba"],
            "structure": "Pyramid",
            "stop": "None"
        },
        "bluf": "Test review that passes all checks.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "claim": "This is a test finding.",
                "citations": [
                    {"file": ".agents/skills/axis-engineering/assets/fixtures/login.ts", "line": 12}
                ]
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
    assert "All checks passed" in stdout, f"Expected 'All checks passed' in stdout. Got: {stdout}"
    print("✓ Test 1 passed: all-pass review exits 0 with 'All checks passed'")


def test_stop_none_allows_unflagged_high():
    """Test 2: stop:'None' review with unflagged high defect passes Andon check."""
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["STRIDE"],
            "structure": "Pyramid",
            "stop": "None"  # Andon NOT enabled
        },
        "bluf": "Test review with stop:None and high defect without stop_triggered.",
        "findings": [
            {
                "id": "F1",
                "handle": "STRIDE",
                "severity": "high",
                "type": "defect",
                "claim": "High severity defect without stop_triggered.",
                "citations": [
                    {"file": ".agents/skills/axis-engineering/assets/fixtures/login.ts", "line": 23}
                ],
                "stop_triggered": False  # Should be allowed when stop:None
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 0, f"Expected exit 0, got {exit_code}. stderr: {stderr}"
    assert "Andon rule: not enabled" in stdout, f"Expected 'Andon rule: not enabled'. Got: {stdout}"
    print("✓ Test 2 passed: stop:None allows unflagged high defects")


def test_dead_citation_fails():
    """Test 3: Review citing nonexistent file fails resolution check."""
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["Genba"],
            "structure": "Pyramid",
            "stop": "None"
        },
        "bluf": "Test review citing nonexistent file.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "claim": "This finding cites a nonexistent file.",
                "citations": [
                    {"file": "nonexistent/file/that/does/not/exist.ts", "line": 1}
                ]
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 1, f"Expected exit 1 for dead citation, got {exit_code}"
    assert "File not found" in stdout, f"Expected 'File not found' in stdout. Got: {stdout}"
    print("✓ Test 3 passed: dead citation review fails with exit 1")


def test_shipped_example_passes():
    """Test 4: assets/review-example.json validates with --repo-path ."""
    example_path = SCRIPT_DIR.parent / "assets" / "review-example.json"

    cmd = [
        sys.executable, str(VALIDATOR),
        str(example_path),
        "--repo-path", str(REPO_ROOT)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    assert result.returncode == 0, (
        f"Expected exit 0 for shipped example, got {result.returncode}. "
        f"stderr: {result.stderr}"
    )
    assert "All checks passed" in result.stdout, (
        f"Expected 'All checks passed' for example. Got: {result.stdout}"
    )
    print("✓ Test 4 passed: shipped review-example.json validates successfully")


def main():
    """Run all regression tests."""
    print("Running axis-validate regression tests...")
    print()

    try:
        test_all_pass_review()
        test_stop_none_allows_unflagged_high()
        test_dead_citation_fails()
        test_shipped_example_passes()
        print()
        print("All tests passed!")
        return 0
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
