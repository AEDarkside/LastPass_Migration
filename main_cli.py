import argparse
import os
import sys
import pandas as pd
from typing import Dict, Any, Optional

DEFAULT_FILENAME = "EntryList.csv"

LASTPASS_TEMPLATE: Dict[str, Any] = {
    "url": "http://sn",         # default placeholder when no URL provided
    "username": None,
    "password": None,
    "extra": "",
    "name": None,
    "grouping": "csv_import",
    "fav": None,
    "totp": 0,
}


def transform_row(row: pd.Series, template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Transform one source row into the LastPass CSV structure.

    Rules:
      - Skip entirely if Group contains 'ZZ Old Customers'.
      - Ignore 'ConnectionType'.
      - Map:
          Name  -> 'name'
          Url   -> 'url' (fallback 'http://sn' if missing)
          Group -> 'grouping' = 'csv_import/<Group>'
          CredentialUserName -> 'username'
          CredentialPassword -> 'password'
      - Any other non-empty fields are appended to 'extra' as "Key: Value\n".
      - If 'url' remains 'http://sn', move username/password into 'extra' and clear them.
    """
    transformed = dict(template)  # defensive copy
    transformed.setdefault("extra", "")

    # Normalize row to drop NaN for easier checks
    worker = row.dropna()

    # --- Hard skip: ZZ Old Customers ---
    group_val = worker.get("Group")
    if isinstance(group_val, str) and "zz old customers" in group_val.lower():
        # Skip this record entirely
        return None

    # --- Field mapping ---
    for key, value in worker.items():
        if key == "ConnectionType":
            # Explicitly ignored
            continue

        if key == "Group":
            # Regular grouping (ZZ Old Customers already handled above)
            val_str = str(value).strip()
            if val_str:
                transformed["grouping"] = f"csv_import/{val_str}"
            else:
                transformed.setdefault("grouping", "csv_import/Uncategorized")

        elif key in ("Name", "Url"):
            # name/url stored lowercase as per template keys
            transformed[key.lower()] = value

        elif key in ("CredentialUserName", "CredentialPassword"):
            out_key = key.replace("Credential", "").lower()  # username/password
            transformed[out_key] = value

        else:
            # Collect any non-mapped fields into 'extra'
            # Avoid cluttering with empty strings/None
            val_str = str(value).strip()
            if val_str:
                transformed["extra"] += f"{key}: {val_str}\n"

    # --- URL fallback & credential relocation ---
    # If url was never set (or matches the default placeholder), move creds to extra and clear them.
    if transformed.get("url", "http://sn") == "http://sn":
        if transformed.get("username") is not None:
            transformed["extra"] += f"Username: {transformed['username']}\n"
        if transformed.get("password") is not None:
            transformed["extra"] += f"Password: {transformed['password']}\n"
        transformed["username"], transformed["password"] = None, None

    # Ensure grouping always exists (even if Group was missing)
    transformed.setdefault("grouping", "csv_import/Uncategorized")

    return transformed


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Transform a CSV of credentials into a LastPass-compatible CSV."
    )
    parser.add_argument(
        "-i", "--input",
        default=DEFAULT_FILENAME,
        help=f"Input CSV file (default: {DEFAULT_FILENAME})",
    )
    parser.add_argument(
        "-o", "--output",
        default="LastPass_Import.csv",
        help="Output CSV file (default: LastPass_Import.csv)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    input_path = args.input
    output_path = args.output

    if not os.path.isfile(input_path):
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        return 2

    # Read source
    original_df = pd.read_csv(input_path)

    # Remove "Group/Folder" entries
    if "ConnectionType" in original_df.columns:
        original_df = original_df[original_df["ConnectionType"] != "Group/Folder"]

    # Transform rows
    output_rows = []
    for _, row in original_df.iterrows():
        out = transform_row(row, LASTPASS_TEMPLATE)
        if out is not None:  # skip ZZ Old Customers entirely
            output_rows.append(out)

    # Build final DataFrame with same columns as template
    transformed_df = pd.DataFrame(output_rows, columns=LASTPASS_TEMPLATE.keys())

    # Diagnostics
    print(transformed_df.info())

    # Save
    transformed_df.to_csv(output_path, index=False)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    sys.exit(main())
