import pandas as pd;

#------------------Configurations-----------------#
WORK_DIR = ""
FILENAME = ""
DELIMITER = "\\"

EXPORT_CSV = True # Set to True to export results to CSV
CSV_PATH = "data_report.csv"

def load_csv_to_df():    
    try:
        df = pd.read_csv(WORK_DIR + FILENAME, delimiter=DELIMITER)
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

if __name__ == "__main__":
    if EXPORT_CSV:
        print(f"Saved CSV: {CSV_PATH}")