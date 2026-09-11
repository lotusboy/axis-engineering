#!/usr/bin/env python3
"""
Doc consistency tests for the Axis Engineering repository.

The same facts are stated in several places — the handle vocabulary appears in
four files, the Two-Pass run-folder convention in two. Nothing stopped those
copies drifting apart, and they did: a handle count said 34 while a fifth file
still said 33, the schema enum said "Seven Factors" while every doc said "Seven
Factors of Awakening" (which broke axis-validate at runtime), and README's
vocabulary table silently lost Chesterton's Fence while still claiming 36.

These tests make each of those a hard failure instead of something a human has
to notice.

Run with: python3 scripts/test_doc_consistency.py
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / ".agents" / "skills" / "axis-engineering"

VOCABULARY = SKILL / "references" / "vocabulary.md"
SCHEMA = SKILL / "assets" / "review-schema.json"
SKILL_MD = SKILL / "SKILL.md"
RECIPES = SKILL / "references" / "recipes.md"
README = REPO_ROOT / "README.md"
QUICK_REF = REPO_ROOT / "vocabulary-quick-ref.md"
TWO_PASS = REPO_ROOT / "two-pass-strategy.md"

# Shorter display names deliberately used in the one-page cheat sheet, where the
# column is narrow. Declared explicitly so a NEW unlisted variant fails the test:
# an abbreviation should be a decision someone made, not drift nobody noticed.
# Note "Seven Factors" — that exact short form leaking into review-schema.json is
# what broke axis-validate before, so aliases are permitted in prose only, never
# in the schema enum (see test_schema_enum_matches_vocabulary).
ALIASES = {
    "12-Factor": "12-Factor App",
    "Hexagonal": "Hexagonal Architecture",
    "Seven Factors": "Seven Factors of Awakening",
    "Fowler's Refactoring Catalog": "Fowler's Catalog",
}

# The Two-Pass run folder, as documented in two-pass-strategy.md and recipes.md.
RUN_FILES = [
    "00-contract.md",
    "01-pass1-prompt.md",
    "02-pass2-prompt.md",
    "03-synthesis-prompt.md",
    "04-pass1-output.md",
    "05-pass2-output.md",
    "06-synthesis.md",
]


def canonical(name: str) -> str:
    return ALIASES.get(name, name)


def bold_table_names(text: str) -> list:
    """Handle names from '| **Name** | ...' markdown table rows."""
    return [m.group(1).strip() for m in re.finditer(r"^\|\s*\*\*(.+?)\*\*\s*\|", text, re.M)]


def plain_table_names(text: str) -> list:
    """Handle names from '| Name | ...' rows (quick-ref uses no bold)."""
    names = []
    for m in re.finditer(r"^\|\s*([^|*\-\s][^|]*?)\s*\|", text, re.M):
        name = m.group(1).strip()
        if name and name != "Handle":
            names.append(name)
    return names


def section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def vocabulary_handles() -> list:
    return bold_table_names(VOCABULARY.read_text(encoding="utf-8"))


def test_vocabulary_has_no_duplicates():
    handles = vocabulary_handles()
    dupes = {h for h in handles if handles.count(h) > 1}
    assert not dupes, f"vocabulary.md lists the same handle twice: {sorted(dupes)}"
    print(f"✓ vocabulary.md has {len(handles)} unique handles (source of truth)")


def test_schema_enum_matches_vocabulary():
    """The schema enum must match vocabulary.md EXACTLY — no aliases.

    A mismatch here is not cosmetic: axis-validate rejects any review whose
    contract names a handle the enum doesn't carry.
    """
    handles = set(vocabulary_handles())
    enum = set(json.loads(SCHEMA.read_text(encoding="utf-8"))["$defs"]["handleEnum"]["enum"])

    missing = sorted(handles - enum)
    extra = sorted(enum - handles)
    assert not missing, f"In vocabulary.md but missing from review-schema.json enum: {missing}"
    assert not extra, f"In review-schema.json enum but not in vocabulary.md: {extra}"
    print(f"✓ review-schema.json enum matches vocabulary.md exactly ({len(enum)} handles)")


def test_readme_documents_every_handle():
    handles = set(vocabulary_handles())
    readme = section(README.read_text(encoding="utf-8"), "## Vocabulary Reference", "## The Axis Contract")
    documented = {canonical(n) for n in bold_table_names(readme)}

    missing = sorted(handles - documented)
    extra = sorted(documented - handles)
    assert not missing, f"Handles missing from README's Vocabulary Reference: {missing}"
    assert not extra, f"In README's Vocabulary Reference but not in vocabulary.md: {extra}"
    print(f"✓ README documents all {len(handles)} handles")


def test_quick_ref_documents_every_handle():
    handles = set(vocabulary_handles())
    documented = {canonical(n) for n in plain_table_names(QUICK_REF.read_text(encoding="utf-8"))}

    missing = sorted(handles - documented)
    extra = sorted(documented - handles)
    assert not missing, f"Handles missing from vocabulary-quick-ref.md: {missing}"
    assert not extra, (
        f"In vocabulary-quick-ref.md but not in vocabulary.md: {extra}. "
        f"If this is a deliberate short form, add it to ALIASES."
    )
    print(f"✓ vocabulary-quick-ref.md documents all {len(handles)} handles")


def test_handle_count_claims_are_accurate():
    """Every claim about the SIZE OF THE VOCABULARY must match reality.

    Deliberately narrow. Prose like "pick 2-3 handles per prompt" is advice about
    usage, not a claim about the vocabulary, so only these total-claim phrasings
    are checked:

        "36 behavior handles"   "36-handle reference"   "(36 total)"   "of 36 handles"
    """
    expected = len(vocabulary_handles())
    pattern = re.compile(
        r"(\d+)\s+behavior\s+handles\b"      # SKILL.md frontmatter description
        r"|(\d+)-handle\b"                    # "the full 36-handle reference"
        r"|\((\d+)\s+total\)"                 # review-schema.json enum description
        r"|\bof\s+(\d+)\s+handles\b"          # "full vocabulary of 36 handles"
    )

    failures = []
    found = 0
    for path in [README, SKILL_MD, QUICK_REF, VOCABULARY, SCHEMA, RECIPES, TWO_PASS]:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in pattern.finditer(line):
                claimed = int(next(g for g in m.groups() if g))
                found += 1
                if claimed != expected:
                    rel = path.relative_to(REPO_ROOT)
                    failures.append(f"{rel}:{lineno} claims {claimed}, expected {expected}")

    assert not failures, "Stale handle-count claims:\n  " + "\n  ".join(failures)
    # Guard against the test silently passing because a rewording stopped it
    # matching anything at all. Silence is not success.
    assert found >= 4, (
        f"Only found {found} handle-count claims — expected at least 4. "
        f"Did a doc reword its count claim? Update the pattern in this test."
    )
    print(f"✓ all {found} vocabulary-size claims say {expected}")


def test_run_folder_filenames_agree():
    """The Two-Pass run-folder convention is stated in two files; they must match."""
    for path in [TWO_PASS, RECIPES]:
        text = path.read_text(encoding="utf-8")
        found = set(re.findall(r"\b(\d\d-[a-z0-9-]+\.md)\b", text))
        rel = path.relative_to(REPO_ROOT)

        missing = sorted(set(RUN_FILES) - found)
        unknown = sorted(found - set(RUN_FILES))
        assert not missing, f"{rel} is missing run-folder files: {missing}"
        assert not unknown, f"{rel} names run-folder files not in the convention: {unknown}"
    print(f"✓ run-folder convention consistent across {len(RUN_FILES)} files in 2 docs")


TESTS = [
    test_vocabulary_has_no_duplicates,
    test_schema_enum_matches_vocabulary,
    test_readme_documents_every_handle,
    test_quick_ref_documents_every_handle,
    test_handle_count_claims_are_accurate,
    test_run_folder_filenames_agree,
]


def main() -> int:
    print("Running doc consistency tests...\n")
    failed = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001 - report and keep going
            print(f"✗ {test.__name__}: unexpected error: {e}")
            failed += 1

    print()
    if failed:
        print(f"{failed} of {len(TESTS)} checks failed.")
        return 1
    print("All doc consistency checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
