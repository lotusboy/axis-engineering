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


def run_validator(review_data, repo_path=None, require_schema=False):
    """Run validator with given review data, return (exit_code, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(review_data, f)
        temp_path = f.name

    try:
        cmd = [sys.executable, str(VALIDATOR), temp_path]
        if repo_path:
            cmd.extend(['--repo-path', repo_path])
        if require_schema:
            cmd.append('--require-schema')

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


def test_schema_rejects_misspelled_handle():
    """Test 5: Schema rejects misspelled handle when jsonschema installed."""
    try:
        import jsonschema
    except ImportError:
        print("⊘ Test 5 skipped: jsonschema not installed")
        return

    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["Gemba"],  # Misspelled - should be "Genba"
            "structure": "Pyramid",
            "stop": "None"
        },
        "bluf": "Test with misspelled handle.",
        "findings": [
            {
                "id": "F1",
                "handle": "Gemba",  # Also misspelled here
                "severity": "info",
                "type": "fact",
                "claim": "Test finding.",
                "citations": [
                    {"file": ".agents/skills/axis-engineering/assets/fixtures/login.ts", "line": 12}
                ]
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 1, f"Expected exit 1 for misspelled handle, got {exit_code}"
    assert "Schema conformance" in stdout and "violation" in stdout.lower(), (
        f"Expected schema conformance violation. Got: {stdout}"
    )
    print("✓ Test 5 passed: schema rejects misspelled handle")


def test_andon_by_category_maintainability():
    """Test 6: High maintainability defect does NOT trigger Andon (category narrows)."""
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["SOLID"],
            "structure": "Pyramid",
            "stop": "Andon"  # Andon enabled
        },
        "bluf": "Test with high maintainability defect - should pass Andon.",
        "findings": [
            {
                "id": "F1",
                "handle": "SOLID",
                "severity": "high",
                "type": "defect",
                "category": "maintainability",  # NOT security/data-loss
                "claim": "Code style issue.",
                "citations": [
                    {"file": ".agents/skills/axis-engineering/assets/fixtures/login.ts", "line": 12}
                ],
                "stop_triggered": False  # Should be allowed for maintainability
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 0, f"Expected exit 0 for high maintainability defect, got {exit_code}"
    assert "Andon" in stdout, f"Expected Andon check in output. Got: {stdout}"
    print("✓ Test 6 passed: high maintainability defect does not trigger Andon")


def test_andon_security_still_fires():
    """Test 7: High security defect DOES trigger Andon (category matches)."""
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["STRIDE"],
            "structure": "Pyramid",
            "stop": "Andon"  # Andon enabled
        },
        "bluf": "Test with high security defect - should fail Andon.",
        "findings": [
            {
                "id": "F1",
                "handle": "STRIDE",
                "severity": "high",
                "type": "defect",
                "category": "security",  # IS security - Andon relevant
                "claim": "Security vulnerability without stop_triggered.",
                "citations": [
                    {"file": ".agents/skills/axis-engineering/assets/fixtures/login.ts", "line": 34}
                ],
                "stop_triggered": False  # Should FAIL for security
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 1, f"Expected exit 1 for high security defect without stop, got {exit_code}"
    assert "Andon" in stdout and "violation" in stdout.lower(), (
        f"Expected Andon violation. Got: {stdout}"
    )
    print("✓ Test 7 passed: high security defect triggers Andon violation")


def test_schema_absent_advisory():
    """Test 8: Without jsonschema, invalid doc exits 2 (advisory) not 0."""
    try:
        import jsonschema
        # Temporarily hide jsonschema by running in a subprocess with modified env
        import os
        env = os.environ.copy()
        # Remove any python paths that might have jsonschema
        env['PYTHONPATH'] = ''
    except ImportError:
        pass  # jsonschema not installed, test can proceed normally

    # Invalid document (misspelled handle)
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["Gemba"],  # Misspelled
            "structure": "Pyramid",
            "stop": "None"
        },
        "bluf": "Invalid doc with misspelled handle.",
        "findings": [],
        "assumptions": []
    }

    # Use subprocess with PYTHONPATH stripped to simulate absent jsonschema
    import subprocess
    import sys
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(review, f)
        temp_path = f.name

    try:
        # Run with clean environment to simulate no jsonschema
        env = os.environ.copy()
        env['PYTHONPATH'] = '/nonexistent'  # Force import failure
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), temp_path, '--repo-path', str(REPO_ROOT)],
            capture_output=True,
            text=True,
            env=env
        )

        # Should be advisory (exit 2), not success (exit 0)
        assert result.returncode == 2, f"Expected exit 2 for advisory, got {result.returncode}. stderr: {result.stderr}"
        assert "⚠" in result.stdout or "not installed" in result.stdout.lower(), (
            f"Expected warning marker or 'not installed' message. Got: {result.stdout}"
        )
        print("✓ Test 8 passed: absent jsonschema → exit 2 (advisory)")
    finally:
        os.unlink(temp_path)


def test_require_schema_hard_fail():
    """Test 9: --require-schema fails hard (exit 1) when jsonschema absent."""
    import subprocess
    import sys
    import os
    import tempfile
    import json

    review = {
        "schema_version": "1.0.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Valid doc.",
        "findings": [],
        "assumptions": []
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(review, f)
        temp_path = f.name

    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = '/nonexistent'  # Force import failure
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), temp_path, '--repo-path', str(REPO_ROOT), '--require-schema'],
            capture_output=True,
            text=True,
            env=env
        )

        # Should fail hard (exit 1) with --require-schema
        assert result.returncode == 1, f"Expected exit 1 with --require-schema, got {result.returncode}"
        assert "required" in result.stdout.lower() or "not installed" in result.stdout.lower(), (
            f"Expected 'required' or 'not installed' message. Got: {result.stdout}"
        )
        print("✓ Test 9 passed: --require-schema → exit 1 (hard fail) when jsonschema absent")
    finally:
        os.unlink(temp_path)


def main():
    """Run all regression tests."""
    print("Running axis-validate regression tests...")
    print()

    try:
        test_all_pass_review()
        test_stop_none_allows_unflagged_high()
        test_dead_citation_fails()
        test_shipped_example_passes()
        test_schema_rejects_misspelled_handle()
        test_andon_by_category_maintainability()
        test_andon_security_still_fires()
        test_schema_absent_advisory()
        test_require_schema_hard_fail()
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
