# LastPass_Migration
This project provides Python scripts to convert custom credential exports into a LastPass-compatible CSV format. It is designed for IT admins or users migrating credentials from other systems into LastPass.


Features
--------------------------------------------------------------------------------------------------------------------
✅ Reads input from Credentials exports from Revolutions Inc's Remote Desktop manager.
✅ Skips irrelevant rows (e.g., ConnectionType = Group/Folder).
✅ Excludes any entries belonging to the group "ZZ Old Customers".
✅ Maps fields:
Name → name
Url → url (fallback to http://sn if missing)
CredentialUserName → username
CredentialPassword → password
Group → grouping = csv_import/<Group>

✅ Appends all other fields to extra for reference.
✅ Handles missing URLs by moving credentials into extra.
✅ Outputs a clean LastPass_Import.csv ready for import.


--------------------------------------------------------------------------------------------------------------------
Files

main.py
Original implementation for transforming CSV data.
main_clean.py
Refactored, robust version:

Uses a dedicated transform_row() function.
Skips "ZZ Old Customers" entirely.
Ensures safe defaults with dict.setdefault().
Adds clear comments and type hints.


--------------------------------------------------------------------------------------------------------------------
Usage

Run:
# Original version
Place your source CSV file (EntryList.csv) in the project directory.
python main.py

# Clean, refactored version
CLI-friendly version of the script that accepts input and output file arguments
-i / --input → path to the source CSV (defaults to EntryList.csv)
-o / --output → path for the transformed CSV (defaults to LastPass_Import.csv)
Basic validation for missing input file

# Default: reads ./EntryList.csv and writes ./LastPass_Import.csv
python main_cli.py

# Specify files
python main_cli.py -i /path/to/source.csv -o /path/to/output.csv

# Long options
python main_cli.py --input ./EntryList.csv --output ./LastPass_Import.csv


--------------------------------------------------------------------------------------------------------------------

The script generates LastPass_Import.csv for LastPass import.

--------------------------------------------------------------------------------------------------------------------
Requirements

Python 3.8+
pandas (pip install pandas)