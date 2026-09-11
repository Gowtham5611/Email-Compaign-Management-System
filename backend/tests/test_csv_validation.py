import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.csv_service import CSVService

def test_csv_parsing_and_validation():
    csv_content = (
        "name,email,subject,company,position\n"
        "Alice,alice@example.com,Welcome,Acme,Engineer\n"
        "Bob,invalid-email-format,Reminder,Beta,Manager\n"
        "Charlie,alice@example.com,Duplicate,Acme,Engineer\n"
        "David,david@domain.org,Invoice,Gamma,Analyst\n"
    ).encode("utf-8")

    result = CSVService.parse_and_validate_csv(csv_content)

    assert result["total_rows"] == 4
    assert result["valid_count"] == 2
    assert result["invalid_count"] == 2
    assert result["duplicate_count"] == 1

    valid_emails = [r["email"] for r in result["valid_rows"]]
    assert "alice@example.com" in valid_emails
    assert "david@domain.org" in valid_emails

    reasons = [inv["reason"] for inv in result["invalid_rows"]]
    assert any("Invalid email format" in r for r in reasons)
    assert any("Duplicate email in CSV" in r for r in reasons)

