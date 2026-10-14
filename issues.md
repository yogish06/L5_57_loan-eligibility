# Lab 5: Static Code Analysis — Issues and Fixes

## Issue Documentation

| Issue                              | Type                 | Line(s)                                                 | Description                                                                                                           | Fix Approach                                                                      | Status |
| ---------------------------------- | -------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | :----: |
| Incorrect EMI calculation          | Functional bug       | Lines 14–18 (specifically line 15)                      | The annual percentage interest rate was used directly as a monthly rate.                                              | Convert the annual percentage rate to a monthly decimal rate by dividing by 1200. | Fixed  |
| Hardcoded FTP credentials          | Security — High      | Line 67                                                 | The FTP password was embedded in the source code.                                                                     | Read credentials from environment variables or a secrets manager.                 | Fixed  |
| Unencrypted FTP connection         | Security — High      | Lines 3, 68–71                                          | Ordinary FTP does not encrypt credentials or transferred data.                                                        | Use a properly configured secure transfer mechanism, such as FTPS or SFTP.        | Fixed  |
| Unsafe serialization choice        | Security/reliability | Lines 4, 57, 64                                         | Application records were stored using `marshal`, which is unsuitable as a robust application data interchange format. | Replace it with JSON and validate the loaded data.                                | Fixed  |
| Incorrect maximum loan calculation | Functional bug       | Lines 33–38 (specifically lines 35–38)                  | The calculation summed monthly repayment capacity without considering interest.                                       | Use the present-value formula for a fixed-payment loan.                           | Fixed  |
| Mutable default argument           | Code quality         | Line 20                                                 | The default list was shared across function calls.                                                                    | Use `None` as the default and initialize or update the list appropriately.        | Fixed  |
| Unused imports                     | Code quality         | Line 2                                                  | Several imported modules were never used.                                                                             | Remove unused imports.                                                            | Fixed  |
| Built-in name shadowing            | Code quality         | Line 34 (also lines 37–38)                              | The variable `sum` shadows Python's built-in `sum()` function.                                                        | Replace the variable and use a descriptive name or an appropriate formula.        | Fixed  |
| Unmanaged file handles             | Code quality         | Lines 56–58, 63–65, 70                                  | Files were opened and closed manually.                                                                                | Use context managers with `with` statements.                                      | Fixed  |
| Insecure identifier generation     | Security             | Lines 50–51                                             | The identifier used the non-cryptographic `random` module.                                                            | Use the `secrets` module when unpredictability is required.                       | Fixed  |
| Missing validation                 | Reliability          | Lines 14–18, 20–31, 33–38, 81–91                        | Invalid values could produce errors or misleading calculations.                                                       | Validate amounts, rates, loan terms, income, and credit scores.                   | Fixed  |
| Naming and documentation issues    | Style/code quality   | Lines 1, 14, 20, 33, 40, 50, 53, 61, 67, 73, 76, 81, 93 | Several function names did not follow conventional Python naming style, and documentation was incomplete.             | Use `snake_case` names and meaningful docstrings.                                 | Fixed  |

## Verification

After applying the fixes to `loan_calculator.py`, the following verification steps were executed:

1. **Loan Calculator Execution & Output Inspection**:
   - `calculate_emi(500000, 9, 5)` returns `10379.18` (corrected from erroneous `375000.0`).
   - `check_eligibility(35, 15000, 760, 12000, "personal")` returns `False` (corrected; FOIR of 80% is rejected).
   - `check_eligibility(30, 80000, 650, 0, "crypto")` returns `False` (corrected; unknown loan type rejected).
   - `max_loan_amount(40000, 5000, 9, 5)` returns `722600.60` (present-value formula used).
   - `risk_band(950)` returns `INVALID` (boundary check correctly rejects scores > 900).

2. **Pylint Verification**:
   - Score: **10.00 / 10.00** (target was > 9.5/10; increased by +4.83 from initial 5.17/10).
   - Report saved to `pylint_report.txt`.

3. **Bandit Security Scan**:
   - Findings: **0 issues identified** (0 High, 0 Medium, 0 Low).
   - Report saved to `bandit_report.txt`.

4. **Flake8 Style Check**:
   - Violations: **0 violations** (empty report indicating complete PEP 8 compliance).
   - Report saved to `flake8_report.txt`.
