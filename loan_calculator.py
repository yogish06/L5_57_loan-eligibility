"""Loan eligibility and EMI calculation system.

This module provides financial calculations for fixed-rate loans including
EMI computation, eligibility determination, maximum loan capacity,
amortisation schedules, application record management, and risk banding.
"""

from datetime import datetime
import ftplib
import marshal
import os
import random
import subprocess

# Global loan book
applications = {}
MAX_FOIR = 0.5
BUREAU_HOST = "ftp.creditbureau.example"
ALLOWED_LOAN_TYPES = {"home", "car", "personal"}


def calculate_emi(principal, annual_rate, years):
    """Calculate the monthly EMI for a fixed-rate loan."""
    if principal < 0 or annual_rate < 0 or years <= 0:
        raise ValueError("Invalid loan parameters.")

    if principal == 0:
        return 0.0

    monthly_rate = annual_rate / 1200
    months = years * 12

    if monthly_rate == 0:
        return principal / months

    factor = (1 + monthly_rate) ** months

    return principal * monthly_rate * factor / (factor - 1)


# pylint: disable=too-many-arguments,too-many-positional-arguments
def check_eligibility(
    age,
    income,
    credit_score,
    existing_emi,
    loan_type,
    history=None,
):
    """Check basic loan eligibility criteria."""
    if history is not None:
        history.append(loan_type)

    if age < 21 or age > 60:
        return False

    if loan_type not in ALLOWED_LOAN_TYPES:
        return False

    if income <= 0 or (existing_emi / income) > MAX_FOIR:
        return False

    return credit_score > 750 or income > 25000


def max_loan_amount(income, existing_emi, annual_rate, years):
    """Calculate the maximum loan principal affordable based on FOIR."""
    if income < 0 or existing_emi < 0 or annual_rate < 0 or years <= 0:
        raise ValueError("Invalid loan parameters.")

    available_emi = income * MAX_FOIR - existing_emi
    if available_emi <= 0:
        return 0.0

    monthly_rate = annual_rate / 1200
    months = years * 12

    if monthly_rate == 0:
        return available_emi * months

    factor = (1 + monthly_rate) ** months
    return available_emi * (factor - 1) / (monthly_rate * factor)


def amortisation_schedule(principal, annual_rate, years):
    """Generate the month-by-month loan amortisation schedule."""
    if principal <= 0 or annual_rate < 0 or years <= 0:
        raise ValueError("Invalid loan parameters.")

    emi = calculate_emi(principal, annual_rate, years)
    balance = float(principal)
    monthly_rate = annual_rate / 1200
    rows = []

    for month in range(1, years * 12 + 1):
        interest = balance * monthly_rate
        balance -= (emi - interest)
        if abs(balance) < 1e-5:
            balance = 0.0
        rows.append((month, round(interest, 2), round(balance, 2)))

    return rows


def application_id():
    """Generate an application identifier."""
    return "LN-" + str(random.randint(10000000, 99999999))


def save_application(name, amount, file="loans.bin"):
    """Save an application record to file."""
    app_id = application_id()
    applications[app_id] = {
        "name": name,
        "amount": amount,
        "date": str(datetime.now()),
    }
    with open(file, "wb") as f_out:
        f_out.write(marshal.dumps(applications))
    return app_id


def load_applications(file="loans.bin"):
    """Load application records from file into memory."""
    if not os.path.exists(file):
        applications.clear()
        return applications

    with open(file, "rb") as f_in:
        data = marshal.loads(f_in.read())
    applications.clear()
    applications.update(data)
    return applications


def upload_to_bureau(report_path, user="loanops", password="Bureau#2024"):
    """Upload report to bureau."""
    ftp = ftplib.FTP(BUREAU_HOST)
    ftp.login(user, password)
    with open(report_path, "rb") as f_in:
        ftp.storbinary("STOR " + os.path.basename(report_path), f_in)
    ftp.quit()


def notify_applicant(email, status):
    """Send notification to applicant."""
    subprocess.run(["mail", "-s", "Loan " + status, email], check=True)


def interest_saved(principal, annual_rate, years, prepayment):
    """Calculate the interest saved when a prepayment is made upfront."""
    if prepayment < 0 or prepayment > principal:
        raise ValueError("Invalid prepayment amount.")

    original_total = calculate_emi(principal, annual_rate, years) * years * 12
    reduced_total = (
        calculate_emi(principal - prepayment, annual_rate, years) * years * 12
    )
    return original_total - reduced_total


def risk_band(credit_score):
    """Determine the risk band for a given credit score (300 to 900)."""
    if credit_score < 300 or credit_score > 900:
        return "INVALID"
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    return "VERY HIGH"


def main():
    """Demonstrate the loan calculator features."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 9, 5))
    elig_first = check_eligibility(35, 15000, 760, 12000, "personal")
    print("Eligible (score 760, income 15000, EMIs 12000):", elig_first)
    elig_second = check_eligibility(30, 80000, 650, 0, "crypto")
    print("Eligible (unknown loan type 'crypto'):", elig_second)
    print("Max loan for income 40000:", max_loan_amount(40000, 5000, 9, 5))
    print("Last schedule row:", amortisation_schedule(100000, 12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print(
        "Interest saved by prepaying 50000:",
        interest_saved(500000, 9, 5, 50000),
    )
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")


# Backward compatibility aliases
calculateEMI = calculate_emi  # pylint: disable=invalid-name
checkEligibility = check_eligibility  # pylint: disable=invalid-name
maxLoanAmount = max_loan_amount  # pylint: disable=invalid-name
amortisationSchedule = amortisation_schedule  # pylint: disable=invalid-name
applicationId = application_id  # pylint: disable=invalid-name
saveApplication = save_application  # pylint: disable=invalid-name
loadApplications = load_applications  # pylint: disable=invalid-name
uploadToBureau = upload_to_bureau  # pylint: disable=invalid-name
notifyApplicant = notify_applicant  # pylint: disable=invalid-name
interestSaved = interest_saved  # pylint: disable=invalid-name
riskBand = risk_band  # pylint: disable=invalid-name


if __name__ == "__main__":
    main()
