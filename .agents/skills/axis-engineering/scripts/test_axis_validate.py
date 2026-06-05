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
REPO_ROOT = SCRIPT_DIR.parent  # Skill root (scripts/ and assets/ are siblings)

# Detect jsonschema availability (determines which tests can run)
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


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


def run_validator_jsonschema_absent(review_data, repo_path=None, require_schema=False):
    """
    Run validator with jsonschema made absent via a shadow stub.
    Creates a temp directory with a fake jsonschema.py that raises ImportError,
    prepends it to PYTHONPATH so the validator sees 'absent' jsonschema.
    Returns (exit_code, stdout, stderr).
    """
    # Create temp dir with stub jsonschema.py
    with tempfile.TemporaryDirectory() as stub_dir:
        stub_path = Path(stub_dir) / "jsonschema.py"
        stub_path.write_text("raise ImportError('jsonschema shadow stub')")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(review_data, f)
            temp_path = f.name

        try:
            cmd = [sys.executable, str(VALIDATOR), temp_path]
            if repo_path:
                cmd.extend(['--repo-path', repo_path])
            if require_schema:
                cmd.append('--require-schema')

            # Prepend stub dir to PYTHONPATH to shadow real jsonschema
            env = os.environ.copy()
            old_pythonpath = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = str(stub_dir) + (os.pathsep + old_pythonpath if old_pythonpath else '')

            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
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
                "category": "correctness",
                "claim": "This is a test finding.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
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
                "category": "maintainability",
                "claim": "High severity defect without stop_triggered.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 23}
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
                "category": "correctness",
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
                "category": "correctness",
                "claim": "Test finding.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
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
                    {"file": "assets/fixtures/login.ts", "line": 12}
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
                    {"file": "assets/fixtures/login.ts", "line": 34}
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
    """Test 8: Without jsonschema, an otherwise-valid doc exits 2 (advisory) not 0."""
    # Self-consistent doc: the Genba handle is fired by F1 with a real citation,
    # so every check passes EXCEPT schema_conformance (advisory when jsonschema absent).
    review = {
        "schema_version": "1.0.0",
        "contract": {
            "axes": ["Genba"],
            "structure": "Pyramid",
            "stop": "None"
        },
        "bluf": "Valid doc to test advisory exit when jsonschema absent.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "This is a test finding.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
                ]
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator_jsonschema_absent(review, str(REPO_ROOT))

    # Should be advisory (exit 2), not success (exit 0)
    assert exit_code == 2, f"Expected exit 2 for advisory, got {exit_code}. stderr: {stderr}"
    assert "⚠" in stdout or "not installed" in stdout.lower(), (
        f"Expected warning marker or 'not installed' message. Got: {stdout}"
    )
    print("✓ Test 8 passed: absent jsonschema → exit 2 (advisory)")


def test_require_schema_hard_fail():
    """Test 9: --require-schema fails hard (exit 1) when jsonschema absent."""
    # Same self-consistent doc as Test 8; only difference is --require-schema,
    # which turns the absent-jsonschema advisory into a hard failure.
    review = {
        "schema_version": "1.0.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Valid doc.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "This is a test finding.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
                ]
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator_jsonschema_absent(review, str(REPO_ROOT), require_schema=True)

    # Should fail hard (exit 1) with --require-schema
    assert exit_code == 1, f"Expected exit 1 with --require-schema, got {exit_code}"
    assert "required" in stdout.lower() or "not installed" in stdout.lower(), (
        f"Expected 'required' or 'not installed' message. Got: {stdout}"
    )
    print("✓ Test 9 passed: --require-schema → exit 1 (hard fail) when jsonschema absent")


def main():
    """Run all regression tests."""
    print("Running axis-validate regression tests...")
    if not JSONSCHEMA_AVAILABLE:
        print("(jsonschema not installed; baseline tests 1-7 skipped)")
    print()

    try:
        # Baseline tests require jsonschema to pass (schema check is now mandatory)
        if JSONSCHEMA_AVAILABLE:
            test_all_pass_review()
            test_stop_none_allows_unflagged_high()
            test_dead_citation_fails()
            test_shipped_example_passes()
            test_schema_rejects_misspelled_handle()
            test_andon_by_category_maintainability()
            test_andon_security_still_fires()
        else:
            print("⊘ Tests 1-7 skipped: requires jsonschema")

        # These tests simulate jsonschema absence and always run
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
