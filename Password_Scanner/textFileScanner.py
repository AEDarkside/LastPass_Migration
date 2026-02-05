import pandas as pd
import os, re, csv, warnings
from pathlib import Path

#-----------------CONFIGURATION-----------------#
ROOT_DIR = r"<Replace with the root directory path>"  # Directory to scan
MARKER_DIR = "\\<Replace with the targeted dolder name>\\"
MARKER_FOLDER = "<Replace with the targeted dolder name>"
KEYWORDS = ["pw", "pwd", "password", "password:"]

pattern = re.compile(rf"(?i)\b({'|'.join(map(re.escape, KEYWORDS))})\b")

warnings.filterwarnings(
    "ignore",
    message=".*Sparkline Group extension is not supported.*",
    category=UserWarning
)

IGNORE_TERMS = ["LastPass"] # Add more later if needed
IGNORE_FOLDERS = ["<Replace with dolder name that should be ignored>"] # Add more later if needed
MAX_FILE_SIZE_MB = 20  # Maximum file size to analyze in megabytes
EXPORT_CSV = True # Set to True to export results to CSV
CSV_PATH = "sensitive_data_report.csv"

# File extensions to analyze
FILE_EXTENSIONS = {
    ".xls", ".xlsx"
}


# -----------------Helpers-----------------#
def scanner(path: Path):
    if ".txt" in FILE_EXTENSIONS:
        scan_file(path)
    elif ".xlsx" in FILE_EXTENSIONS:
        scan_excel_file(path)
    else:
        print("Feature is not available yet!")
        return False

def is_scan_target(path: Path) -> bool:
    # Check if in ignore folder
    for part in path.parts:
        if part in IGNORE_FOLDERS:
            return False
    return path.suffix.lower() in FILE_EXTENSIONS

def is_ignore_term_present(line: str) -> bool:
    for term in IGNORE_TERMS:
        if term.lower() in line.lower():
            return True
    return False

def get_technician_name(path: Path) -> str:
    parts = path.parts
    try:
        i = parts.index(MARKER_FOLDER)
        customer_folder = parts[i + 1]  # e.g., "Balaclava Glass - NM"
    except (ValueError, IndexError):
        return "Unknown"

    # Extract text after " - " (with spaces). If missing, return Unknown.
    if " - " not in customer_folder:
        return "Unknown"

    return customer_folder.split(" - ", 1)[1].strip()


#-----------------File Scanner-----------------#
# Function for Text file or Binary File only #
def scan_file(path: Path):
    try:
        size_bytes = path.stat().st_size
        if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
            return

        # Read as text; replace bad bytes so scan doesn't crash
        with path.open("r", encoding="utf-8", errors="replace") as file:
            for line_no, line in enumerate(file, start=1):
                match = pattern.search(line)
                if match:
                    if is_ignore_term_present(line):
                        continue
                    snippet = line.strip()
                    if len(snippet) > 300:
                        snippet = snippet[:300] + "…"
                    yield {
                        "file": str(path),
                        "technican Name": get_technician_name(path),
                        "line": line_no,
                        "keyword": match.group(1),
                        "snippet": snippet
                    }
    except (PermissionError, OSError):
        return
    except Exception as e:
        print(f"Error accessing folder {path: Path}: {e}")
        return False

# Function for Excel Sheet #
def scan_excel_file(path_obj: Path):
    try:
        hits = []
        path = str(path_obj)
        excel_file = pd.ExcelFile(path)
        
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet, dtype=str).fillna("") # force to read as strings

            for row_idx, row in df.iterrows():
                for column_idx, val in enumerate(row.tolist()):
                    snippet = str(val)
                
                if any(word in snippet.lower() for word in KEYWORDS):    
                    hits.append({
                        "file": str(path),
                        "sheet": sheet,
                        "row": int(row_idx) + 1,
                        "col": int(column_idx) + 1,
                        "snippet": snippet[:300]  # clip long content
                    })

        return hits
    except (PermissionError, OSError):
        return
    except Exception as e:
        print(f"Error accessing folder {path}: {e}")
        return False


#-----------------Directory Walk and Scan-----------------#
def walk_and_scan(root_dir: str):
    root = Path(root_dir)

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs (case-insensitive)
        dirnames[:] = [d for d in dirnames if d.lower()]

        for name in filenames:
            path = Path(dirpath) / name
            if not is_scan_target(path):
                continue
            scanner(path)

#-----------------CSV Export-----------------#
def write_csv(rows, out_path: str):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "technican Name", "line", "keyword", "snippet"])
        writer.writeheader()
        writer.writerows(rows)
        print(f"CSV written to {out_path}")

#-----------------Main-----------------#
if __name__ == "__main__":
    hits = []
    for hit in walk_and_scan(ROOT_DIR):
        hits.append(hit)
        print(f"[{hit['keyword']}] {hit['file']}:{hit['line']}")

    print(f"\nDone. Total hits: {len(hits)}")

    # Export to CSV if enabled
    if EXPORT_CSV and hits:
        write_csv(hits, CSV_PATH)
        print(f"Saved CSV: {CSV_PATH}")
