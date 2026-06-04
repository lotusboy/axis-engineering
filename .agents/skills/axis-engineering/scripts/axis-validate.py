#!/usr/bin/env python3
"""
axis-validate: Deterministic linter for Axis Engineering review output.

Validates contract conformance for structured review output.
Converts the Axis Contract from a prompt instruction (soft) into an enforced invariant (hard).

Usage:
    python axis-validate.py <review.json|review.md> [--repo-path PATH]

Exit codes:
    0 - All checks passed
    1 - Hard failures (must fix)
    2 - Advisory warnings only
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def is_path_within_repo(full_path: Path, repo_root: Path) -> bool:
    """Check if resolved path is within repo root (robust against traversal attacks)."""
    try:
        # Use relative_to which raises ValueError if not a subpath
        full_path.relative_to(repo_root)
        return True
    except ValueError:
        return False


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate Axis Engineering review output against contract"
    )
    parser.add_argument(
        "review_path",
        help="Path to review file (.json or .md with embedded JSON block)"
    )
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to repository root for citation resolution (default: current directory)"
    )
    return parser.parse_args()


def load_review_data(review_path: str) -> Dict[str, Any]:
    """Load review data from JSON file or extract from Markdown."""
    path = Path(review_path)
    
    if not path.exists():
        print(f"ERROR: Review file not found: {review_path}", file=sys.stderr)
        sys.exit(1)
    
    content = path.read_text(encoding="utf-8")
    
    # If it's a .md file, try to extract JSON from ```json code block
    if path.suffix.lower() == ".md":
        # Look for ```json ... ``` block
        json_match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            print("ERROR: No JSON code block found in Markdown file", file=sys.stderr)
            sys.exit(1)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def validate_schema_version(data: Dict[str, Any]) -> Tuple[bool, str, List[Dict]]:
    """Check schema version is present and valid."""
    version = data.get("schema_version")
    if not version:
        return False, "Missing schema_version field", [{"issue": "schema_version is required"}]
    if version != "1.0.0":
        return True, f"Schema version mismatch: expected 1.0.0, got {version} (advisory)", []
    return True, f"Schema version: {version}", []


def check_citation_coverage(findings: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict]]:
    """
    Check 1: Citation coverage.
    Every 'defect' and 'fact' finding must have ≥1 citation.
    'recommendation' and 'absence' findings are exempt.
    """
    failures = []
    total_defect_fact = 0
    cited_defect_fact = 0
    
    for finding in findings:
        finding_type = finding.get("type", "defect")
        finding_id = finding.get("id", "unknown")
        
        if finding_type in ("defect", "fact"):
            total_defect_fact += 1
            citations = finding.get("citations", [])
            if not citations:
                failures.append({
                    "finding_id": finding_id,
                    "issue": f"{finding_type} finding has no citations (required)"
                })
            else:
                cited_defect_fact += 1
    
    if failures:
        return False, f"Citation coverage: {cited_defect_fact}/{total_defect_fact} (failures: {len(failures)})", failures
    
    return True, f"Citation coverage: {cited_defect_fact}/{total_defect_fact}", []


def check_citation_resolution(findings: List[Dict[str, Any]], repo_path: str) -> Tuple[bool, str, List[Dict]]:
    """
    Check 2: Citation resolution.
    For each citation:
    - File must exist at repo_path/file
    - Line number must be within file's actual line count
    """
    failures = []
    total_citations = 0
    resolved_citations = 0
    repo_root = Path(repo_path).resolve()
    
    for finding in findings:
        citations = finding.get("citations", [])
        finding_id = finding.get("id", "unknown")
        
        for citation in citations:
            total_citations += 1
            file_path = citation.get("file", "")
            line_num = citation.get("line", 0)
            
            # Normalize path and resolve relative to repo root
            try:
                full_path = (repo_root / file_path).resolve()
                # Ensure it's within repo root (security check - robust against traversal)
                if not is_path_within_repo(full_path, repo_root):
                    failures.append({
                        "finding_id": finding_id,
                        "citation": f"{file_path}:{line_num}",
                        "issue": "Citation path escapes repository root"
                    })
                    continue
            except Exception as e:
                failures.append({
                    "finding_id": finding_id,
                    "citation": f"{file_path}:{line_num}",
                    "issue": f"Invalid path: {e}"
                })
                continue
            
            # Check file exists
            if not full_path.exists():
                failures.append({
                    "finding_id": finding_id,
                    "citation": f"{file_path}:{line_num}",
                    "issue": f"File not found: {file_path}"
                })
                continue
            
            # Check it's a file (not directory)
            if not full_path.is_file():
                failures.append({
                    "finding_id": finding_id,
                    "citation": f"{file_path}:{line_num}",
                    "issue": f"Not a file: {file_path}"
                })
                continue
            
            # Check line number is valid
            try:
                line_count = sum(1 for _ in full_path.open(encoding="utf-8", errors="ignore"))
                if line_num < 1 or line_num > line_count:
                    failures.append({
                        "finding_id": finding_id,
                        "citation": f"{file_path}:{line_num}",
                        "issue": f"Line {line_num} out of range (file has {line_count} lines)"
                    })
                    continue
            except Exception as e:
                failures.append({
                    "finding_id": finding_id,
                    "citation": f"{file_path}:{line_num}",
                    "issue": f"Cannot read file: {e}"
                })
                continue
            
            resolved_citations += 1
    
    if failures:
        return False, f"Citation resolution: {resolved_citations}/{total_citations} (dead: {len(failures)})", failures
    
    return True, f"Citation resolution: {resolved_citations}/{total_citations}", []


def check_handle_firing(contract: Dict[str, Any], findings: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict]]:
    """
    Check 3: Handle firing.
    Every handle named in contract.axes must own ≥1 finding.
    Guards against cargo-culting ("I said STRIDE but produced zero security findings").
    """
    contract_handles = set(contract.get("axes", []))
    fired_handles = set()
    
    for finding in findings:
        handle = finding.get("handle")
        if handle:
            fired_handles.add(handle)
    
    unfired_handles = contract_handles - fired_handles
    
    if unfired_handles:
        handle_list = ", ".join(sorted(unfired_handles))
        return False, f"Handle firing: {len(fired_handles)}/{len(contract_handles)} (unfired: {handle_list})", [
            {"handle": h, "issue": "Named in contract but no findings produced"} for h in unfired_handles
        ]
    
    return True, f"Handle firing: {', '.join(sorted(fired_handles))}", []


def check_ledger_integrity(assumptions: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict]]:
    """
    Check 4: Ledger integrity.
    Assumptions array must be present.
    Track unknown assumptions (warn if silently dropped between runs - not implemented for single-run check).
    """
    if assumptions is None:
        return False, "Ledger integrity: Missing assumptions array", [{"issue": "assumptions field is required"}]
    
    unknown_count = sum(1 for a in assumptions if a.get("status") == "unknown")
    verified_count = sum(1 for a in assumptions if a.get("status") == "verified")
    refuted_count = sum(1 for a in assumptions if a.get("status") == "refuted")
    
    return True, f"Ledger integrity: {unknown_count} unknown, {verified_count} verified, {refuted_count} refuted", []


def check_andon_rule(findings: List[Dict[str, Any]], contract: Dict[str, Any]) -> Tuple[bool, str, List[Dict]]:
    """
    Check 5: Andon rule.
    If contract.stop == "Andon" and any finding has severity "critical" or "high"
    AND type "defect", then stop_triggered must be true on that finding.
    """
    # Short-circuit if Andon is not enabled
    if contract.get("stop") != "Andon":
        return True, "Andon rule: not enabled (stop != Andon)", []

    violations = []

    for finding in findings:
        severity = finding.get("severity", "")
        finding_type = finding.get("type", "")
        stop_triggered = finding.get("stop_triggered", False)
        finding_id = finding.get("id", "unknown")
        
        if severity in ("critical", "high") and finding_type == "defect" and not stop_triggered:
            violations.append({
                "finding_id": finding_id,
                "severity": severity,
                "issue": f"{severity} severity defect but stop_triggered=false (Andon rule violation)"
            })
    
    if violations:
        return False, f"Andon rule: {len(violations)} violations", violations
    
    return True, "Andon rule: All critical/high defects have stop_triggered", []


def format_conformance_report(results: List[Tuple[str, bool, str, List[Dict]]]) -> str:
    """Format the conformance report for output."""
    lines = [
        "axis-validate: Contract Conformance Report",
        "==========================================",
        ""
    ]
    
    passed_count = sum(1 for _, p, _, _ in results if p)
    total = len(results)

    lines.append(f"Overall: {passed_count}/{total} checks passed")
    lines.append("")

    for check_name, passed, message, failures in results:
        status = "✓" if passed else "✗"
        lines.append(f"  {check_name}: {message} {status}")

        if failures:
            for failure in failures:
                finding_id = failure.get("finding_id", failure.get("handle", ""))
                issue = failure.get("issue", str(failure))
                if finding_id:
                    lines.append(f"      {finding_id}: {issue}")
                else:
                    lines.append(f"      {issue}")

    lines.append("")

    if passed_count == total:
        lines.append("All checks passed. Contract is conformant.")
    elif passed_count >= total - 1:
        lines.append("Minor issues detected. Review recommended.")
    else:
        lines.append("Failures must be resolved before review is accepted.")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    
    # Load review data
    data = load_review_data(args.review_path)
    
    # Extract components
    contract = data.get("contract", {})
    findings = data.get("findings", [])
    assumptions = data.get("assumptions", [])
    
    # Run all checks
    results = []
    
    # Check 0: Schema version
    passed, message, _ = validate_schema_version(data)
    results.append(("schema_version", passed, message, []))
    
    # Check 1: Citation coverage
    passed, message, failures = check_citation_coverage(findings)
    results.append(("citations", passed, message, failures))
    
    # Check 2: Citation resolution
    passed, message, failures = check_citation_resolution(findings, args.repo_path)
    results.append(("resolution", passed, message, failures))
    
    # Check 3: Handle firing
    passed, message, failures = check_handle_firing(contract, findings)
    results.append(("handles", passed, message, failures))
    
    # Check 4: Ledger integrity
    passed, message, failures = check_ledger_integrity(assumptions)
    results.append(("ledger", passed, message, failures))
    
    # Check 5: Andon rule
    passed, message, failures = check_andon_rule(findings, contract)
    results.append(("andon", passed, message, failures))
    
    # Output report
    report = format_conformance_report(results)
    print(report)
    
    # Determine exit code
    # Exit 2 = advisory warnings only (e.g., schema version drift)
    # Exit 1 = hard failures (citations, handles, andon violations)
    # Exit 0 = all passed
    hard_failures = 0
    advisory_warnings = 0
    
    for check_name, passed, message, _ in results:
        if not passed:
            if check_name == "schema_version" and "mismatch" in message:
                advisory_warnings += 1
            else:
                hard_failures += 1
    
    if hard_failures > 0:
        sys.exit(1)
    if advisory_warnings > 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
