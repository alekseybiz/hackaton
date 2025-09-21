import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/inspect_xlsx.py path/to/file.xlsx")
        sys.exit(1)
    xlsx_path = Path(sys.argv[1])
    try:
        import pandas as pd
    except Exception as e:
        print("Pandas is required. Install with: pip install pandas openpyxl")
        raise

    xls = pd.ExcelFile(xlsx_path)
    print("Sheets:", xls.sheet_names)
    for name in xls.sheet_names:
        print("\n=== Sheet:", name, "===")
        df = xls.parse(name, nrows=10)
        print("Columns:")
        for col in df.columns:
            print(" -", col)
        print("\nHead:")
        # Show first 5 rows compactly
        print(df.head(5).to_markdown(index=False))

if __name__ == "__main__":
    main()


