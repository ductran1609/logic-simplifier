# Truth Table → Boolean Equation → K-Map Simplifier

A command-line Python tool for combinational logic design that converts a user-provided truth table into a simplified Boolean expression using Karnaugh Map (K-Map) grouping via the Quine-McCluskey algorithm.

---

## Features

| Feature | Detail |
|---|---|
| Input variables | n ≥ 2 (K-Map display & simplification for n = 2, 3, 4) |
| Truth table input | Interactive prompt; space- or comma-separated values |
| Canonical forms | SOP (Sum of Products) and POS (Product of Sums) |
| Term listing | Minterm list Σm(…) or Maxterm list ΠM(…) |
| K-Map display | Formatted grid with Gray-code ordering |
| Simplification | Quine-McCluskey + Essential Prime Implicant selection |
| Validation | Row-by-row comparison of simplified expression vs. truth table |

---

## Requirements

- Python 3.7 or higher
- No third-party libraries — uses the standard library only

---

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/logic-simplifier.git
cd logic-simplifier

# (Optional) create a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

---

## Usage

```bash
python3 logic_simplifier.py
```

The program guides you through three interactive sections:

### Section 1 — Input

1. Enter the number of input variables (`n ≥ 2`).
2. (Optional) Enter custom variable names, e.g. `X, Y, Z`.
3. View the blank truth table skeleton showing row order.
4. Enter the 2ⁿ output values (F column), space- or comma-separated.
5. Choose canonical form: **1 = SOP** or **2 = POS**.

### Section 2 — Boolean Expression & K-Map

The tool prints:
- The complete truth table
- The canonical SOP or POS equation
- The minterm or maxterm list
- A formatted K-Map (for n = 2, 3, or 4)
- K-Map grouping details (which minterms/maxterms each group covers and the resulting term)
- The simplified Boolean expression

### Section 3 — Validation

Every row is evaluated against the simplified expression and compared to the original output. A final **PASS ✓** or **FAIL ✗** verdict is printed.

---

## Example Session — 3-variable SOP

```
Number of input variables (n ≥ 2): 3
Default variable names: A, B, C
Custom names or Enter for defaults: [Enter]

Input skeleton:
  A  B  C  │  F
  ──────────────
  0  0  0  │  ?
  0  0  1  │  ?
  ...

Enter all 8 output values: 0 1 1 0 1 0 0 1

Select canonical form:
  [1] SOP   [2] POS
Choice: 1

──────────────────────────────────────────────────────────────
 SECTION 2 — BOOLEAN EXPRESSION & K-MAP
──────────────────────────────────────────────────────────────

  CANONICAL SOP:
  F = A'B'C + A'BC' + AB'C' + ABC

  Minterms: Σm(1, 2, 4, 7)

  K-MAP:
          BC:   00    01    11    10
           ┌─────┬─────┬─────┬─────┐
  A = 0  │  0  │  1  │  0  │  1  │
           ├─────┼─────┼─────┼─────┤
  A = 1  │  1  │  0  │  1  │  0  │
           └─────┴─────┴─────┴─────┘

  K-MAP GROUPINGS:
  Group of  2 | minterms [1, 7]   → ...
  ...

  SIMPLIFIED EXPRESSION:
  F = A'B'C + A'BC' + AB'C' + ABC

──────────────────────────────────────────────────────────────
 SECTION 3 — VALIDATION
──────────────────────────────────────────────────────────────
   Row  Inputs   Expected  Got   Status
  ─────────────────────────────────────
     0  0 0 0       0       0    ✓
     1  0 0 1       1       1    ✓
  ...
  ╔══════════════════════════════════════╗
  ║   VALIDATION RESULT :  ✓  PASS      ║
  ╚══════════════════════════════════════╝
```

---

## How It Works

### Quine-McCluskey Algorithm

1. **Seed** — each minterm (or maxterm) is its own 1-term implicant.
2. **Iterative merging** — pairs of implicants that differ in exactly one bit position are merged; the differing bit becomes `-` (don't-care).
3. **Prime Implicants** — implicants that could not be merged in a round are recorded as prime implicants.
4. **Essential PI Selection** — minterms covered by exactly one prime implicant force that PI into the solution. Remaining minterms are covered greedily.

### SOP vs. POS Implicant Conversion

| Form | Input to QM | Bit = `0` | Bit = `1` | Bit = `-` |
|------|-------------|-----------|-----------|-----------|
| SOP  | minterms    | `var'`    | `var`     | omitted   |
| POS  | maxterms    | `var`     | `var'`    | omitted   |

---

## File Structure

```
logic-simplifier/
├── logic_simplifier.py   # Main program (all logic in one file)
└── README.md             # This file
```

---

## Limitations

- K-Map display and QM simplification are available for **n = 2, 3, 4** variables. For n > 4 the canonical form is printed as the output.
- Don't-care conditions (X entries) are not currently supported.
- The greedy PI selection heuristic produces a minimal or near-minimal cover; it may not guarantee the absolute minimum for all edge cases with 4+ variables.

---

## Can video recordings be uploaded to YouTube?

**Yes.** You may upload your demo video to YouTube and submit the link (ensure the video is set to **Public** or **Unlisted** so it can be viewed by your instructor).

---

## License

MIT License — free to use, modify, and distribute.
