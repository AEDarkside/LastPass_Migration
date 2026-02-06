import pandas as pd
from pathlib import Path

#------------------Configurations-----------------#
WORK_DIR = ""
FILENAME = "targeted_excel_list.csv"
DELIMITER = "\\"

MARKER_FOLDER = "Customer"

EXPORT_CSV = True # Set to True to export results to CSV
CSV_PATH = "data_output.csv"

#----------------------Helper Functions----------------------#
def load_csv_to_df(path: Path):    
    try:
        df = pd.read_csv(path, encoding="utf-8")

        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def get_technician_name(path: Path) -> str:
    parts = Path(path).parts
    try:
        i = parts.index(MARKER_FOLDER)
        customer_folder = parts[i + 1]  # e.g., "Balaclava Glass - NM"
    except (ValueError, IndexError):
        return "Unknown"

    # Extract text after " - " (with spaces). If missing, return Unknown.
    if " - " not in customer_folder:
        return "Unknown"

    return customer_folder.split(" - ", 1)[1].strip()

#----------------------Main Execution----------------------#
def data_extraction(df: pd.DataFrame):
    if df is None:
        print("No DataFrame to process.")
        return None

    # Assuming the paths are in a column named 'file_path'
    if 'file_path' not in df.columns:
        print("Column 'file_path' not found in DataFrame.")
        return None

    # Extracting paths for technician names
    df["technician_name"] = df["file_path"].apply(get_technician_name)

    return df

if __name__ == "__main__":
    processed_df = data_extraction(load_csv_to_df(Path(WORK_DIR + FILENAME)))

    if EXPORT_CSV:
        try:
            processed_df.to_csv(CSV_PATH, index=False)
        except Exception as e:
            print(f"Error saving CSV: {e}")
    else:
        print(f"Error saving CSV: {CSV_PATH}")