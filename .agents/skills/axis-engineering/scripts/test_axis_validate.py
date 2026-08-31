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


def test_unsupported_schema_version():
    """Test 10: Unsupported schema_version string → exit 1.

    The schema_version check itself is advisory, but jsonschema also rejects
    the value against the enum in review-schema.json, producing a hard
    schema_conformance failure. Net result: exit 1.
    """
    review = {
        "schema_version": "99.0.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Test with unknown schema version.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
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

    assert exit_code == 1, f"Expected exit 1 for unknown schema version (schema_conformance hard-fails), got {exit_code}"
    assert "mismatch" in stdout.lower() or "not one of" in stdout.lower(), (
        f"Expected version mismatch or schema violation. Got: {stdout}"
    )
    print("✓ Test 10 passed: unsupported schema_version → exit 1 (schema_conformance hard-fails)")


def test_handle_declared_but_no_findings():
    """Test 11: Handle in contract.axes with zero findings → exit 1 (hard fail)."""
    review = {
        "schema_version": "1.1.0",
        "contract": {"axes": ["Genba", "STRIDE"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Test with declared handle that has no findings.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "Test finding for Genba only.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
                ]
            }
            # STRIDE declared in axes but no STRIDE finding
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 1, f"Expected exit 1 for unfired handle, got {exit_code}"
    assert "STRIDE" in stdout, f"Expected STRIDE mentioned in failure. Got: {stdout}"
    print("✓ Test 11 passed: declared handle with no findings → exit 1")


def test_missing_assumptions_array():
    """Test 12: Missing assumptions array → exit 1 (hard fail on ledger check)."""
    review = {
        "schema_version": "1.1.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Test with missing assumptions.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "Test finding.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
                ]
            }
        ]
        # No "assumptions" key at all
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 1, f"Expected exit 1 for missing assumptions, got {exit_code}"
    assert "assumption" in stdout.lower() or "ledger" in stdout.lower(), (
        f"Expected ledger/assumption failure. Got: {stdout}"
    )
    print("✓ Test 12 passed: missing assumptions array → exit 1")


def test_path_traversal_blocked():
    """Test 13: Citation with path traversal (../../etc/passwd) → exit 1."""
    review = {
        "schema_version": "1.1.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Test path traversal guard.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "Test finding with traversal citation.",
                "citations": [
                    {"file": "../../etc/passwd", "line": 1}
                ]
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert exit_code == 1, f"Expected exit 1 for path traversal, got {exit_code}"
    assert "escapes" in stdout.lower() or "outside" in stdout.lower() or "traversal" in stdout.lower(), (
        f"Expected path-escapes-repo failure. Got: {stdout}"
    )
    print("✓ Test 13 passed: path traversal citation → exit 1")


def test_null_citations_no_crash():
    """Test 14: A finding with citations: null must not crash the validator (F-01)."""
    review = {
        "schema_version": "1.1.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Test finding with citations explicitly set to null.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "This finding has citations: null instead of an array.",
                "citations": None
            }
        ],
        "assumptions": []
    }

    exit_code, stdout, stderr = run_validator(review, str(REPO_ROOT))

    assert "Traceback" not in stdout and "Traceback" not in stderr, (
        f"Validator crashed on citations: null. stdout: {stdout} stderr: {stderr}"
    )
    assert exit_code == 1, f"Expected exit 1 (no citations), got {exit_code}"
    assert "no citations" in stdout.lower(), f"Expected 'no citations' failure. Got: {stdout}"
    print("✓ Test 14 passed: citations: null does not crash the validator")


def test_multi_json_block_picks_review():
    """Test 15: A Markdown doc with a decoy JSON block before the real review
    output must validate the review, not the decoy (F-05)."""
    review = {
        "schema_version": "1.1.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Real review buried after a decoy JSON block.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
                "severity": "info",
                "type": "fact",
                "category": "correctness",
                "claim": "This is the real finding.",
                "citations": [
                    {"file": "assets/fixtures/login.ts", "line": 12}
                ]
            }
        ],
        "assumptions": []
    }

    md_content = (
        "# Example\n\n"
        "Here is the schema shape:\n\n"
        "```json\n"
        '{"example": true, "not": "a review"}\n'
        "```\n\n"
        "Actual review output:\n\n"
        "```json\n"
        f"{json.dumps(review)}\n"
        "```\n"
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(md_content)
        temp_path = f.name

    try:
        cmd = [sys.executable, str(VALIDATOR), temp_path, "--repo-path", str(REPO_ROOT)]
        result = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        os.unlink(temp_path)

    # Without jsonschema, schema_conformance is always advisory (exit 2 even for
    # a fully valid doc - see Test 8), so the expected exit code depends on
    # whether jsonschema is available, not on the block-selection fix itself.
    expected_exit = 0 if JSONSCHEMA_AVAILABLE else 2
    assert result.returncode == expected_exit, (
        f"Expected exit {expected_exit}, got {result.returncode}. "
        f"stdout: {result.stdout} stderr: {result.stderr}"
    )
    # The real signal that the decoy block was skipped: the real finding's
    # citation resolved, proving the second block (not {"example": true}) was parsed.
    assert "Citation coverage: 1/1" in result.stdout and "Citation resolution: 1/1" in result.stdout, (
        f"Expected the real review's citation to resolve. Got: {result.stdout}"
    )
    print("✓ Test 15 passed: decoy JSON block before the real review is skipped")


def test_bad_schema_version_hard_fails_without_jsonschema():
    """Test 16: An unsupported schema_version must hard-fail (exit 1) even
    when jsonschema is absent, not silently pass (F-06)."""
    review = {
        "schema_version": "99.0.0",
        "contract": {"axes": ["Genba"], "structure": "Pyramid", "stop": "None"},
        "bluf": "Test with unknown schema version and jsonschema absent.",
        "findings": [
            {
                "id": "F1",
                "handle": "Genba",
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

    exit_code, stdout, stderr = run_validator_jsonschema_absent(review, str(REPO_ROOT))

    assert exit_code == 1, (
        f"Expected exit 1 for unsupported schema_version without jsonschema, got {exit_code}. "
        f"stdout: {stdout}"
    )
    assert "unsupported" in stdout.lower(), f"Expected 'unsupported' in output. Got: {stdout}"
    print("✓ Test 16 passed: unsupported schema_version hard-fails even without jsonschema")


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
            test_unsupported_schema_version()
            test_handle_declared_but_no_findings()
            test_missing_assumptions_array()
            test_path_traversal_blocked()
        else:
            print("⊘ Tests 1-7, 10-13 skipped: requires jsonschema")

        # These tests don't depend on jsonschema and always run
        test_null_citations_no_crash()
        test_multi_json_block_picks_review()

        # These tests simulate jsonschema absence and always run
        test_schema_absent_advisory()
        test_require_schema_hard_fail()
        test_bad_schema_version_hard_fails_without_jsonschema()
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
