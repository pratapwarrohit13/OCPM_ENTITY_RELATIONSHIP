# Data Relationship Analyzer - User Guide

This tool helps you understand the structure of your data by analyzing CSV, Excel, TSV, and TXT files in a directory. It automatically detects:
1. **Primary Keys**: Columns that uniquely identify rows.
2. **Relationships**: Connections between tables (Foreign Keys).
3. **Cardinality**: Whether a relationship is One-to-One (1:1) or Many-to-One (n:1).
4. **Date Columns**: Fields that contain date/time information.

## How to Use

### 1. Prerequisites
Ensure you have Python installed. Install the required libraries:
```bash
pip install pandas openpyxl
```

### 2. Run the Analyzer
Open your terminal or command prompt and run:
```bash
python data_analyzer.py
```

### 3. Provide Input
When prompted, paste the full path to the folder containing your data files.
*Example*: `C:\Users\MyName\Documents\ProjectData`

### 4. View Results
The tool will generate an Excel file named **`relationship_report.xlsx`** in the same folder.
Open it to see:
- **Relationships Tab**: Shows which tables are linked and how.
- **Primary Keys Tab**: Lists the candidate primary keys for each file.
- **Date Columns Tab**: Shows detected date fields.

## Troubleshooting

- **"No data loaded"**: Check if your files represent tabular data (CSV/Excel) and are not corrupted.
- **"Separation failed"**: For `.txt` files, ensure they are comma or tab separated.
- **Permission Errors**: Close the `relationship_report.xlsx` file if it's open in Excel before running the tool again.

## Features
- **Supports Multiple Formats**: `.csv`, `.xlsx`, `.xls`, `.tsv`, `.txt`.
- **Automatic Date Detection**: Scans potential date columns.
- **Smart Logic**: Infers relationships based on data matching (subset logic).
