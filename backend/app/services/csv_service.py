import csv
import io
import re
from typing import List, Dict, Any, Tuple
from app.core.logging_config import log_activity

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class CSVService:
    @staticmethod
    def parse_and_validate_csv(file_content: bytes) -> Dict[str, Any]:
        """
        Parses raw CSV bytes, validates emails, checks duplicates, and returns structured analysis.
        Does NOT silently discard invalid rows. Returns explicit failure reason per invalid row.
        """
        try:
            # Decode utf-8 / utf-8-sig
            text = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1")

        stream = io.StringIO(text)
        reader = csv.DictReader(stream)

        if not reader.fieldnames:
            return {
                "total_rows": 0,
                "valid_count": 0,
                "invalid_count": 0,
                "duplicate_count": 0,
                "valid_rows": [],
                "invalid_rows": [{"row": 0, "raw_data": {}, "reason": "CSV file is empty or has no header line"}],
                "detected_columns": []
            }

        headers = [h.strip() for h in reader.fieldnames if h]

        # Identify email column (support 'email', 'e-mail', 'mail', or first column matching email)
        email_col = None
        for h in headers:
            if h.lower() in ("email", "e-mail", "mail", "email_address"):
                email_col = h
                break

        # Identify name column (support 'name', 'full_name', 'first_name', 'recipient')
        name_col = None
        for h in headers:
            if h.lower() in ("name", "full_name", "first_name", "recipient", "username"):
                name_col = h
                break

        valid_rows = []
        invalid_rows = []
        seen_emails = set()
        duplicate_count = 0

        for row_num, raw_row in enumerate(reader, start=1):
            # Clean keys & values
            cleaned_row = {k.strip(): (v.strip() if v else "") for k, v in raw_row.items() if k}
            
            # Find email value
            email_val = ""
            if email_col and email_col in cleaned_row:
                email_val = cleaned_row[email_col]
            else:
                # Fallback: check all fields for email match
                for key, val in cleaned_row.items():
                    if EMAIL_REGEX.match(val):
                        email_val = val
                        if not email_col:
                            email_col = key
                        break

            # Find name value
            name_val = ""
            if name_col and name_col in cleaned_row:
                name_val = cleaned_row[name_col]
            else:
                name_val = email_val.split("@")[0] if email_val else "Recipient"

            if not email_val:
                invalid_rows.append({
                    "row": row_num,
                    "raw_data": cleaned_row,
                    "reason": "Missing email address field"
                })
                continue

            if not EMAIL_REGEX.match(email_val):
                invalid_rows.append({
                    "row": row_num,
                    "raw_data": cleaned_row,
                    "reason": f"Invalid email format: '{email_val}'"
                })
                continue

            lower_email = email_val.lower()
            if lower_email in seen_emails:
                duplicate_count += 1
                invalid_rows.append({
                    "row": row_num,
                    "raw_data": cleaned_row,
                    "reason": f"Duplicate email in CSV: '{email_val}'"
                })
                continue

            seen_emails.add(lower_email)

            # Store standard and dynamic custom fields
            custom_fields = {k: v for k, v in cleaned_row.items() if k not in (email_col, name_col)}

            valid_rows.append({
                "name": name_val or "Recipient",
                "email": lower_email,
                "subject": cleaned_row.get("subject", ""),
                "custom_fields": custom_fields,
                "raw_data": cleaned_row
            })

        log_activity(f"CSV Validation Completed: {len(valid_rows)} valid, {len(invalid_rows)} invalid (incl. {duplicate_count} duplicates)")

        return {
            "total_rows": len(valid_rows) + len(invalid_rows),
            "valid_count": len(valid_rows),
            "invalid_count": len(invalid_rows),
            "duplicate_count": duplicate_count,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "detected_columns": headers
        }

