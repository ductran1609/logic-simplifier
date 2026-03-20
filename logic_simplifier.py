#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║      Truth Table → Boolean Equation → K-Map Simplifier      ║
║      Combinational Logic Design Tool                         ║
╚══════════════════════════════════════════════════════════════╝

Converts a user-provided truth table into a canonical Boolean
expression (SOP or POS), displays a Karnaugh Map, performs
grouping via Quine-McCluskey, and validates the simplified result.
"""

import sys
from typing import List, Optional, Set, FrozenSet, Dict, Tuple

# ════════════════════════════════════════════════════════════════
# UTILITIES
# ════════════════════════════════════════════════════════════════

def int_to_bits(value: int, width: int) -> List[int]:
    """Convert integer to a list of bits (MSB first)."""
    return [(value >> (width - 1 - i)) & 1 for i in range(width)]

def banner(text: str, char: str = "═", width: int = 62) -> str:
    """Return a formatted section banner string."""
    pad = (width - len(text) - 2) // 2
    return f"\n{char * width}\n{' ' * pad} {text}\n{char * width}"

def hr(char: str = "─", width: int = 62) -> str:
    return char * width


# ════════════════════════════════════════════════════════════════
# SECTION 1 — INPUT SYSTEM
# ════════════════════════════════════════════════════════════════

def get_num_variables() -> int:
    """Prompt until the user enters a valid integer n ≥ 2."""
    while True:
        try:
            n = int(input("  Number of input variables (n ≥ 2): ").strip())
            if n >= 2:
                return n
            print("  ✗  n must be ≥ 2.\n")
        except ValueError:
            print("  ✗  Please enter a valid integer.\n")


def get_variable_names(n: int) -> List[str]:
    """Ask for custom variable names or fall back to A, B, C, …"""
    defaults = [chr(65 + i) for i in range(n)]   # A, B, C, …
    print(f"  Default variable names: {', '.join(defaults)}")
    raw = input("  Custom names (comma-separated) or Enter to accept defaults: ").strip()
    if not raw:
        return defaults
    names = [x.strip().upper() for x in raw.split(",")]
    if len(names) != n:
        print(f"  ✗  Expected {n} names — using defaults.")
        return defaults
    return names


def _print_blank_truth_table(n: int, vars: List[str]) -> None:
    """Display the input skeleton so the user knows the row order."""
    rows = 2 ** n
    header = "  " + "  ".join(f"{v}" for v in vars) + "  │  F"
    print(header)
    print("  " + hr("─", len(header) - 2))
    for i in range(rows):
        bits = int_to_bits(i, n)
        print("  " + "  ".join(str(b) for b in bits) + "  │  ?")
    print()


def get_truth_table_outputs(n: int, vars: List[str]) -> List[int]:
    """
    Collect 2ⁿ output bits from the user.
    Accepts values space- or comma-separated on one or multiple lines.
    """
    rows = 2 ** n
    print(f"\n  Input skeleton (row order is 0 → {rows - 1}):")
    _print_blank_truth_table(n, vars)
    print(f"  Enter all {rows} output values (0/1), space- or comma-separated.")

    outputs: List[int] = []
    while len(outputs) < rows:
        remaining = rows - len(outputs)
        raw = input(f"  > [{remaining} value(s) remaining] ").strip()
        if not raw:
            continue
        parts = raw.replace(",", " ").split()
        for p in parts:
            if len(outputs) == rows:
                break
            if p in ("0", "1"):
                outputs.append(int(p))
            else:
                print(f"  ✗  '{p}' is not valid — only 0 or 1 accepted.")
                break
    return outputs[:rows]


def validate_truth_table(outputs: List[int], n: int) -> bool:
    """Confirm row count and that every output value is 0 or 1."""
    rows = 2 ** n
    if len(outputs) != rows:
        print(f"  ✗  Expected {rows} rows, received {len(outputs)}.")
        return False
    for v in outputs:
        if v not in (0, 1):
            print(f"  ✗  Invalid output value: {v}")
            return False
    return True


def get_form_choice() -> str:
    """Ask the user to choose SOP or POS."""
    print()
    print("  Select canonical form:")
    print("    [1]  SOP — Sum of Products   (groups rows where F = 1, uses minterms)")
    print("    [2]  POS — Product of Sums   (groups rows where F = 0, uses maxterms)")
    while True:
        choice = input("  Choice [1/2]: ").strip()
        if choice == "1":
            return "SOP"
        if choice == "2":
            return "POS"
        print("  ✗  Enter 1 or 2.")


# ════════════════════════════════════════════════════════════════
# SECTION 2a — CANONICAL BOOLEAN EXPRESSIONS
# ════════════════════════════════════════════════════════════════

def get_minterms(outputs: List[int]) -> List[int]:
    return [i for i, v in enumerate(outputs) if v == 1]


def get_maxterms(outputs: List[int]) -> List[int]:
    return [i for i, v in enumerate(outputs) if v == 0]


def _minterm_product(idx: int, n: int, vars: List[str]) -> str:
    """Return the product term for a single minterm (all n literals)."""
    bits = int_to_bits(idx, n)
    return "".join(v if b else v + "'" for v, b in zip(vars, bits))


def _maxterm_sum(idx: int, n: int, vars: List[str]) -> str:
    """Return the sum term for a single maxterm (all n literals)."""
    bits = int_to_bits(idx, n)
    lits = [v if not b else v + "'" for v, b in zip(vars, bits)]
    return "(" + " + ".join(lits) + ")"


def canonical_sop(minterms: List[int], n: int, vars: List[str]) -> str:
    if not minterms:
        return "F = 0"
    if len(minterms) == 2 ** n:
        return "F = 1"
    return "F = " + " + ".join(_minterm_product(m, n, vars) for m in minterms)


def canonical_pos(maxterms: List[int], n: int, vars: List[str]) -> str:
    if not maxterms:
        return "F = 1"
    if len(maxterms) == 2 ** n:
        return "F = 0"
    return "F = " + "".join(_maxterm_sum(m, n, vars) for m in maxterms)


# ════════════════════════════════════════════════════════════════
# SECTION 2b — QUINE-McCLUSKEY SIMPLIFICATION
# ════════════════════════════════════════════════════════════════

def _qm_combine(a: str, b: str) -> Optional[str]:
    """
    Try to merge two QM implicant strings.
    Rules
    ─────
    • '-' in the same column → preserved.
    • '-' in different columns → cannot merge (return None).
    • Exactly one column differs (both non-dash) → replace with '-'.
    • More than one differing column → cannot merge (return None).
    """
    diffs = 0
    result = []
    for ca, cb in zip(a, b):
        if ca == cb:
            result.append(ca)
        elif ca == "-" or cb == "-":
            # Dashes in different positions — incompatible groups
            return None
        else:
            diffs += 1
            if diffs > 1:
                return None
            result.append("-")
    return "".join(result) if diffs == 1 else None


def quine_mccluskey(
    terms: List[int], n: int
) -> List[Tuple[str, FrozenSet[int]]]:
    """
    Full Quine-McCluskey procedure.

    Parameters
    ----------
    terms : row indices to cover (minterms for SOP, maxterms for POS)
    n     : number of variables

    Returns
    -------
    List of (implicant_bit_string, frozenset_of_covered_rows)
    """
    if not terms:
        return []

    # Seed: each term is its own implicant
    current: Dict[FrozenSet[int], str] = {
        frozenset([t]): bin(t)[2:].zfill(n) for t in terms
    }

    all_prime_implicants: List[Tuple[str, FrozenSet[int]]] = []

    while current:
        used: Set[FrozenSet[int]] = set()
        nxt: Dict[FrozenSet[int], str] = {}

        items = list(current.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                s1, b1 = items[i]
                s2, b2 = items[j]
                merged = _qm_combine(b1, b2)
                if merged is not None:
                    new_key = s1 | s2
                    if new_key not in nxt:
                        nxt[new_key] = merged
                    used.add(s1)
                    used.add(s2)

        # Terms that could not be merged are prime implicants
        for s, b in items:
            if s not in used:
                all_prime_implicants.append((b, s))

        current = nxt

    return all_prime_implicants


def select_essential_pis(
    prime_implicants: List[Tuple[str, FrozenSet[int]]],
    terms: List[int],
) -> List[Tuple[str, FrozenSet[int]]]:
    """
    Select a minimal cover of prime implicants using:
    1. Essential PI selection (minterms covered by only one PI).
    2. Greedy maximum-cover for any remaining uncovered terms.
    """
    remaining = set(terms)
    selected: List[Tuple[str, FrozenSet[int]]] = []
    pis = list(prime_implicants)

    # Pass 1 — essential PIs
    changed = True
    while changed and remaining:
        changed = False
        for m in list(remaining):
            covering = [pi for pi in pis if m in pi[1]]
            if len(covering) == 1:
                pi = covering[0]
                if pi not in selected:
                    selected.append(pi)
                    remaining -= pi[1]
                    changed = True

    # Pass 2 — greedy cover for any stragglers
    while remaining:
        best = max(pis, key=lambda pi: len(pi[1] & remaining))
        if best not in selected:
            selected.append(best)
        remaining -= best[1]

    return selected


def _implicant_to_sop_term(bits: str, vars: List[str]) -> str:
    """
    Convert a QM implicant bit string to a SOP product term.
    '1' → variable, '0' → variable', '-' → omitted.
    """
    lits = [
        v if b == "1" else v + "'"
        for v, b in zip(vars, bits)
        if b != "-"
    ]
    return "".join(lits) if lits else "1"


def _implicant_to_pos_term(bits: str, vars: List[str]) -> str:
    """
    Convert a QM implicant bit string (derived from maxterm grouping)
    to a POS sum term.
    '0' → variable, '1' → variable', '-' → omitted.
    """
    lits = [
        v if b == "0" else v + "'"
        for v, b in zip(vars, bits)
        if b != "-"
    ]
    return "(" + " + ".join(lits) + ")" if lits else "0"


def build_simplified_sop(
    selected: List[Tuple[str, FrozenSet[int]]], n: int, vars: List[str],
    minterms: List[int]
) -> str:
    if not minterms:
        return "F = 0"
    if len(minterms) == 2 ** n:
        return "F = 1"
    seen: Set[str] = set()
    terms = []
    for bits, _ in selected:
        t = _implicant_to_sop_term(bits, vars)
        if t not in seen:
            seen.add(t)
            terms.append(t)
    return "F = " + " + ".join(terms)


def build_simplified_pos(
    selected: List[Tuple[str, FrozenSet[int]]], n: int, vars: List[str],
    maxterms: List[int]
) -> str:
    if not maxterms:
        return "F = 1"
    if len(maxterms) == 2 ** n:
        return "F = 0"
    seen: Set[str] = set()
    terms = []
    for bits, _ in selected:
        t = _implicant_to_pos_term(bits, vars)
        if t not in seen:
            seen.add(t)
            terms.append(t)
    return "F = " + "".join(terms)


# ════════════════════════════════════════════════════════════════
# SECTION 2c — K-MAP DISPLAY
# ════════════════════════════════════════════════════════════════

# Gray code sequence for 2-bit axis: 00 → 01 → 11 → 10
_GRAY2 = [0, 1, 3, 2]


def _kmap_2var(outputs: List[int], vars: List[str]) -> str:
    """2-variable K-Map (2×2 grid)."""
    V0, V1 = vars[0], vars[1]
    lines = [
        f"          {V1}",
        f"        0     1",
        f"      ┌─────┬─────┐",
    ]
    for a in range(2):
        row = f"  {V0}={a} │"
        for b in range(2):
            row += f"  {outputs[a * 2 + b]}  │"
        lines.append(row)
        lines.append("      ├─────┼─────┤" if a == 0 else "      └─────┴─────┘")
    return "\n".join(lines)


def _kmap_3var(outputs: List[int], vars: List[str]) -> str:
    """3-variable K-Map (2×4 grid, rows=A, cols=BC in Gray order)."""
    V0, V1, V2 = vars[0], vars[1], vars[2]
    col_labels = "   00    01    11    10"
    lines = [
        f"          {V1}{V2}: {col_labels}",
        f"           ┌─────┬─────┬─────┬─────┐",
    ]
    for a in range(2):
        row = f"  {V0} = {a}  │"
        for bc in _GRAY2:
            row += f"  {outputs[a * 4 + bc]}  │"
        lines.append(row)
        lines.append("           ├─────┼─────┼─────┼─────┤" if a == 0
                     else "           └─────┴─────┴─────┴─────┘")
    return "\n".join(lines)


def _kmap_4var(outputs: List[int], vars: List[str]) -> str:
    """4-variable K-Map (4×4 grid, rows=AB, cols=CD in Gray order)."""
    V0, V1, V2, V3 = vars[0], vars[1], vars[2], vars[3]
    col_labels = "   00    01    11    10"
    lines = [
        f"              {V2}{V3}: {col_labels}",
        f"  {V0}{V1}        ┌─────┬─────┬─────┬─────┐",
    ]
    for i, ab in enumerate(_GRAY2):
        row = f"   {ab:02b}       │"
        for cd in _GRAY2:
            row += f"  {outputs[ab * 4 + cd]}  │"
        lines.append(row)
        lines.append("              ├─────┼─────┼─────┼─────┤" if i < 3
                     else "              └─────┴─────┴─────┴─────┘")
    return "\n".join(lines)


def display_kmap(outputs: List[int], n: int, vars: List[str]) -> str:
    if n == 2:
        return _kmap_2var(outputs, vars)
    if n == 3:
        return _kmap_3var(outputs, vars)
    if n == 4:
        return _kmap_4var(outputs, vars)
    return "  (K-Map display is supported for n = 2, 3, 4 only)"


def describe_kmap_groups(
    selected: List[Tuple[str, FrozenSet[int]]],
    vars: List[str],
    form: str,
) -> str:
    """
    Human-readable description of each K-Map group and the
    simplified term it contributes.
    """
    if not selected:
        return "  (no groups)"
    lines = []
    for bits, covered in selected:
        mts = sorted(covered)
        size = len(covered)
        if form == "SOP":
            expr = _implicant_to_sop_term(bits, vars)
            label = "minterm"
        else:
            expr = _implicant_to_pos_term(bits, vars)
            label = "maxterm"
        lines.append(
            f"  Group of {size:2d} | {label}s {mts!s:<30} →  {expr}"
        )
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════
# SECTION 3 — VALIDATION
# ════════════════════════════════════════════════════════════════

def validate_result(
    selected: List[Tuple[str, FrozenSet[int]]],
    outputs: List[int],
    n: int,
    form: str,
) -> bool:
    """
    Evaluate the simplified expression for all 2ⁿ input combinations
    and compare against the original truth table.

    SOP: row evaluates to 1 iff its index is in the union of covered sets.
    POS: row evaluates to 0 iff its index is in the union of covered sets.
    """
    covered: Set[int] = set()
    for _, s in selected:
        covered |= s

    rows = 2 ** n
    vars_header = "  ".join(v for v in ["Row"] + [f"  {v}" for v in []])
    col_w = max(n * 2, 5)

    header = (
        f"  {'Row':>4}  {'Inputs':<{col_w}}  {'Expected':^8}  "
        f"{'Got':^4}  Status"
    )
    print(header)
    print("  " + hr("─", len(header) - 2))

    all_pass = True
    for i in range(rows):
        bits = int_to_bits(i, n)
        inp = " ".join(str(b) for b in bits)
        expected = outputs[i]

        if form == "SOP":
            got = 1 if i in covered else 0
        else:
            got = 0 if i in covered else 1

        ok = got == expected
        if not ok:
            all_pass = False
        status = "✓" if ok else "✗ FAIL"
        print(
            f"  {i:>4}  {inp:<{col_w}}  {expected:^8}  {got:^4}  {status}"
        )

    return all_pass


# ════════════════════════════════════════════════════════════════
# OUTPUT HELPERS
# ════════════════════════════════════════════════════════════════

def print_truth_table(outputs: List[int], n: int, vars: List[str]) -> None:
    header = "  " + "  ".join(v for v in vars) + "  │  F"
    print(header)
    print("  " + hr("─", len(header) - 2))
    for i in range(2 ** n):
        bits = int_to_bits(i, n)
        row = "  ".join(str(b) for b in bits)
        print(f"  {row}  │  {outputs[i]}")


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main() -> None:
    print(banner("TRUTH TABLE  →  K-MAP SIMPLIFIER"))
    print("  Combinational Logic Design Tool\n")

    # ── SECTION 1 — INPUT ────────────────────────────────────────
    print(banner("SECTION 1 — INPUT", "─"))

    n    = get_num_variables()
    vars = get_variable_names(n)

    outputs = get_truth_table_outputs(n, vars)
    if not validate_truth_table(outputs, n):
        print("\n  ✗  Truth table failed validation. Exiting.")
        sys.exit(1)
    print("  ✓  Truth table accepted.\n")

    form = get_form_choice()

    # ── SECTION 2 — BOOLEAN EXPRESSION & K-MAP ──────────────────
    print(banner("SECTION 2 — BOOLEAN EXPRESSION & K-MAP", "─"))

    minterms = get_minterms(outputs)
    maxterms = get_maxterms(outputs)

    # 1. Truth Table (formatted)
    print("\n  ┌─ TRUTH TABLE " + "─" * 48 + "┐")
    print_truth_table(outputs, n, vars)

    # 2. Canonical Equation + Minterm/Maxterm list
    if form == "SOP":
        canon = canonical_sop(minterms, n, vars)
        term_label = "Minterms"
        term_list  = minterms
        sigma_str  = f"  F = Σm({', '.join(map(str, minterms))})"
    else:
        canon = canonical_pos(maxterms, n, vars)
        term_label = "Maxterms"
        term_list  = maxterms
        sigma_str  = f"  F = ΠM({', '.join(map(str, maxterms))})"

    print(f"\n  ┌─ CANONICAL {form} " + "─" * 44 + "┐")
    print(f"  {canon}")
    print(f"\n  ┌─ {term_label.upper()} LIST " + "─" * 48 + "┐")
    print(sigma_str)
    print(f"  {term_label}: {term_list}")

    # 3. K-Map & Simplification (n = 2..4)
    support_kmap = 2 <= n <= 4
    selected: List[Tuple[str, FrozenSet[int]]] = []

    if support_kmap:
        print(f"\n  ┌─ K-MAP " + "─" * 54 + "┐")
        print(display_kmap(outputs, n, vars))

        # Run QM on the appropriate index set
        qm_input = minterms if form == "SOP" else maxterms
        pis      = quine_mccluskey(qm_input, n)
        selected = select_essential_pis(pis, qm_input)

        print(f"\n  ┌─ K-MAP GROUPINGS " + "─" * 44 + "┐")
        print(describe_kmap_groups(selected, vars, form))

        # Simplified expression
        if form == "SOP":
            simplified = build_simplified_sop(selected, n, vars, minterms)
        else:
            simplified = build_simplified_pos(selected, n, vars, maxterms)

        print(f"\n  ┌─ SIMPLIFIED EXPRESSION " + "─" * 38 + "┐")
        print(f"  {simplified}")
    else:
        print(
            f"\n  ⚠  K-Map simplification is only supported for n = 2, 3, 4.\n"
            f"     Showing canonical form as the final expression."
        )
        simplified = canon
        # Build a trivial "selected" so validation still works
        if form == "SOP":
            selected = [(bin(m)[2:].zfill(n), frozenset([m])) for m in minterms]
        else:
            selected = [(bin(m)[2:].zfill(n), frozenset([m])) for m in maxterms]

    # ── SECTION 3 — VALIDATION ───────────────────────────────────
    print(banner("SECTION 3 — VALIDATION", "─"))
    print(f"\n  Evaluating simplified expression against truth table …\n")

    passed = validate_result(selected, outputs, n, form)

    print()
    if passed:
        print("  ╔══════════════════════════════════════╗")
        print("  ║   VALIDATION RESULT :  ✓  PASS      ║")
        print("  ║   Simplified expression is correct.  ║")
        print("  ╚══════════════════════════════════════╝")
    else:
        print("  ╔══════════════════════════════════════╗")
        print("  ║   VALIDATION RESULT :  ✗  FAIL      ║")
        print("  ║   Mismatch found — check groupings.  ║")
        print("  ╚══════════════════════════════════════╝")

    # ── SUMMARY ──────────────────────────────────────────────────
    print(banner("SUMMARY", "─"))
    print(f"  Variables      : {', '.join(vars)}  (n = {n})")
    print(f"  Form           : {form}")
    print(f"  Minterms       : {minterms}")
    print(f"  Maxterms       : {maxterms}")
    print(f"  Canonical      : {canon}")
    print(f"  Simplified     : {simplified}")
    print(f"  Validation     : {'PASS ✓' if passed else 'FAIL ✗'}")
    print()


if __name__ == "__main__":
    main()
