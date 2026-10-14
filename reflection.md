# Lab 5: Static Code Analysis — Reflection

## 1. Tool Comparison: Pylint, Bandit, and Flake8

Each of the three static analysis tools serves a distinct purpose in the software development lifecycle:

| Feature | Flake8 | Pylint | Bandit |
| :--- | :--- | :--- | :--- |
| **Primary Focus** | Style and syntax conventions (PEP 8) | Code quality, maintainability, code smells, complexity | Security vulnerabilities and common CWE flaws |
| **Speed** | Very fast (lightweight) | Slower (deep AST parsing & type inference) | Fast to moderate (AST-based security rules) |
| **Scoring / Output** | List of rule violations (e.g., E501, F401) | Numerical score out of 10.00 with categorized messages | Severity (High/Med/Low) & Confidence ratings |
| **Strengths** | Ideal for rapid feedback in git pre-commit hooks and real-time editor linting | Flags subtle design bugs like mutable default arguments (`history=[]`), unmanaged file handles, and shadowed built-ins (`sum`) | Detects hardcoded secrets, dangerous imports (`ftplib`), insecure deserialization (`marshal`), and weak RNGs (`random`) |

**Key Takeaway**: No single static analysis tool is sufficient on its own. Flake8 ensures uniformity and readability; Pylint identifies maintainability hazards and anti-patterns; and Bandit guards against security exposures. Using them together forms a comprehensive static verification baseline.

---

## 2. Limitations of Static Analysis: Bugs Missed by Tools

Static analysis tools analyze code structure and semantics without executing runtime domain logic. Consequently, several severe functional bugs in `loan_calculator.py` were completely undetected by all three tools:

1. **Incorrect Monthly Interest Formula in EMI (`r = annual_rate / 12`)**:
   - Pylint and Flake8 validated the arithmetic syntax, but had no semantic understanding that financial interest rates expressed as percentages (e.g., 9 for 9%) must be divided by 1200 rather than 12. This produced an absurd monthly EMI of 375,000 on a 500,000 principal loan.
2. **Short-Circuiting Eligibility Flaws in `checkEligibility`**:
   - The original code evaluated `if credit_score > 750 or income > 25000: return True` before verifying the Fixed Obligation to Income Ratio (FOIR) or loan type. Consequently, an applicant with 80% FOIR (severe debt overload) and an applicant requesting an invalid loan type (`crypto`) were both erroneously approved. The linters saw syntactically valid conditionals and could not identify the broken business logic.
3. **Linear Summation in `maxLoanAmount`**:
   - The original logic summed monthly capacity repeatedly without applying present-value discounting for interest. Static analyzers could not determine that the formula violated standard financial mathematics.
4. **Invalid Credit Score Classification (`riskBand(950)`)**:
   - Because 950 is greater than 800, the function categorized it as `"LOW"` risk, failing to recognize that standard credit scores (CIBIL/FICO) are capped at 900 and 950 should be considered invalid.

**Conclusion**: Static analysis must always be paired with thorough unit testing, property-based testing, and domain verification. Linters ensure the code is written correctly, but testing ensures the *correct thing* is written.

---

## 3. Security Vulnerabilities and Remediation Trade-offs

Bandit identified several critical vulnerabilities that exposed the application to credential leakage, insecure data storage, and network eavesdropping:

- **Hardcoded Password (`B107`) & Plaintext FTP (`B402`, `B321`)**:
  - *Risk*: Plaintext credentials embedded in source code are committed to version control and visible to all repository collaborators. Plaintext FTP transmits credentials and sensitive borrower reports in cleartext across the network (CWE-319).
  - *Fix*: Extracted credentials to environment variables (`os.environ.get("BUREAU_USER")`, `os.environ.get("BUREAU_PASSWORD")`) and migrated toward encrypted transport (SFTP/FTPS).
- **Insecure Deserialization via `marshal` (`B302`)**:
  - *Risk*: Python's `marshal` module is intended strictly for internal `.pyc` bytecode serialization, not secure or robust data persistence (CWE-502). Loading untrusted data can lead to memory corruption or arbitrary execution.
  - *Fix*: Replaced `marshal` with standardized, human-readable, and secure `json` format, accompanied by data validation.
- **Pseudo-Random Application Identifiers (`B311`)**:
  - *Risk*: `random.randint` uses the Mersenne Twister PRNG, whose internal state can be deduced from observed outputs, allowing attackers to predict future application IDs (CWE-330).
  - *Fix*: Used Python's cryptographically secure `secrets.token_hex()` module.

---

## 4. Workflow Integration and Best Practices

To maximize the benefits of static code analysis while minimizing developer friction:

1. **Pre-Commit Hooks (Shift-Left Quality)**:
   - Run lightweight checks (`flake8`, formatting tools like `black`) locally on staged files before commit. This prevents style issues from polluting commit history.
2. **Continuous Integration (CI) Gates**:
   - Integrate `pylint` and `bandit` into the automated CI pipeline (e.g., GitHub Actions). Pull requests should require a minimum Pylint threshold (e.g., 9.5/10) and 0 High/Medium Bandit vulnerabilities before merging is permitted.
3. **Tuning and Baseline Management**:
   - Avoid developer fatigue by configuring `.pylintrc` or `.flake8` with agreed team standards rather than blindly enforcing arbitrary rules.
   - For legacy codebases, introduce tools with baseline files (e.g., `bandit -b`) to block new defects while incrementally paying down technical debt.
