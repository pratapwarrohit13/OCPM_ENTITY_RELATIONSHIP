import pandas as pd
import os
import glob
import logging
from typing import List, Dict, Tuple, Any

# ==============================================================================
# CONSTANTS
# ==============================================================================
LOG_FILE = "analyzer_debug.log"
SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.tsv', '.txt'}

def validate_file_extension(file_path: str):
    """
    Validates if the file extension is supported.
    Raises ValueError if not supported.
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"File format '{ext}' is not supported. Please upload a file with one of these extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

def load_data(file_paths: List[str]) -> Dict[str, pd.DataFrame]:
    """
    Loads data files into pandas DataFrames.
    """
    dataframes = {}
    for path in file_paths:
        filename = os.path.basename(path)
        try:
            # Validate format (redundant if filtered by glob, but good for safety)
            validate_file_extension(path)

            if path.endswith('.csv'):
                df = pd.read_csv(path)
            elif path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(path)
            elif path.endswith('.tsv'):
                df = pd.read_csv(path, sep='\t')
            elif path.endswith('.txt'):
                try:
                    df = pd.read_csv(path, sep=None, engine='python')
                except:
                    logging.debug(f"Separation failed for {filename}, falling back to tab.")
                    df = pd.read_csv(path, sep='\t')
            else:
                # Should be caught by validate_file_extension, but for logic completeness:
                raise ValueError(f"Unsupported format internally: {path}")
            
            dataframes[filename] = df
            logging.info(f"Loaded {filename} with shape {df.shape} (Rows, Cols)")
        except Exception as e:
            logging.error(f"Failed loading {filename}: {e}", exc_info=True)
            if isinstance(e, ValueError) and "not supported" in str(e):
                raise e # Re-raise validation errors if desired, or just log. user asked to throw exception.
                # However, loop continues. If strict mode is needed:
                # raise e 
    return dataframes

# ... [Keep detect_primary_keys, detect_date_columns, analyze_relationships as is] ...


def detect_primary_keys(df: pd.DataFrame) -> List[str]:
    """
    Identifies candidate primary keys.
    Criteria: Column must have unique values and NO unique/Null values.
    """
    pk_candidates = []
    for col in df.columns:
        # DEBUG: Checking column uniqueness and null status
        if df[col].is_unique and not df[col].isnull().any():
            pk_candidates.append(col)
    return pk_candidates

def detect_date_columns(df: pd.DataFrame) -> List[str]:
    """
    Identifies columns that look like dates.
    """
    date_cols = []
    for col in df.columns:
        # Optimization: Skip likely numeric/bool columns to reduce processing time
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_bool_dtype(df[col]):
             continue
             
        try:
            # DEBUG: Attempting datetime conversion
            pd.to_datetime(df[col], errors='raise')
            date_cols.append(col)
        except (ValueError, TypeError):
            continue
    return date_cols

def analyze_relationships(dataframes: Dict[str, pd.DataFrame]):
    """
    Core Logic: Inter-table relationship inference.
    Compares columns of every table against PKs of every other table.
    """
    
    # Step 1: Detect PKs for all tables
    logging.info("Detecting Primary Keys...")
    table_pks = {}
    for name, df in dataframes.items():
        pks = detect_primary_keys(df)
        table_pks[name] = pks
        if pks:
             logging.info(f"Table '{name}': Found {len(pks)} PK candidates ({', '.join(pks)})")
        else:
             logging.info(f"Table '{name}': No PK candidates found.")

    relationships = []

    # Step 2: Iterate through all pairs to find FKs
    files = list(dataframes.keys())
    logging.info(f"Analyzing {len(files)} files for relationships...")
    
    for i, child_file in enumerate(files):
        df_child = dataframes[child_file]
        
        for j, parent_file in enumerate(files):
            if i == j: continue # Skip self-comparison
            
            df_parent = dataframes[parent_file]
            parent_pks = table_pks[parent_file]
            
            for pk in parent_pks:
                # Heuristic: Check if Child Column values are a SUBSET of Parent PK values.
                # This implies Child.Col -> Parent.PK
                
                for col in df_child.columns:
                    try:
                        # Optimization: Filter out NaNs before comparison
                        child_vals = set(df_child[col].dropna().unique())
                        parent_vals = set(df_parent[pk].unique())
                        
                        if not child_vals:
                             continue

                        # DEBUG: subset check
                        if child_vals.issubset(parent_vals):
                            # Relationship Found!
                            
                            # Step 3: Determine Cardinality
                            if df_child[col].is_unique:
                                # If FK in child is unique, each parent row matches at most one child row.
                                cardinality = "1:1" 
                            else:
                                # If FK has duplicates, multiple child rows match one parent row.
                                cardinality = "n:1" 
                            
                            relationships.append({
                                "Child Table": child_file,
                                "Child Column (FK)": col,
                                "Parent Table": parent_file,
                                "Parent Column (PK)": pk,
                                "Cardinality": cardinality
                            })
                            logging.debug(f"Found {cardinality} relation: {child_file}.{col} -> {parent_file}.{pk}")
                    except Exception as e:
                        logging.warning(f"Error checking relationship {child_file}.{col} -> {parent_file}.{pk}: {e}")
                        continue

    logging.info(f"Relationship analysis complete. Found {len(relationships)} relationships.")
    return table_pks, relationships

def main():
    # Setup Logging
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w' # Overwrite log each run
    )
    
    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logging.info("Starting Data Relationship Analyzer Tool")
    
    print("===========================================")
    print("   DATA RELATIONSHIP ANALYZER TOOL")
    print("===========================================")
    
    try:
        # 1. Get Input Directory
        input_path = input("Enter the directory path containing CSV/Excel files: ").strip()
        input_path = input_path.strip('"').strip("'") 

        if not os.path.isdir(input_path):
            logging.error(f"Invalid directory path: {input_path}")
            print(f"[ERROR] Invalid directory path: {input_path}")
            return

        # 2. Find Files
        # We gather all files to check for supported ones
        all_files = glob.glob(os.path.join(input_path, "*.*"))
        
        # Filter for supported files
        compatible_files = [f for f in all_files if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
        
        # Exclude report
        compatible_files = [f for f in compatible_files if "relationship_report.xlsx" not in os.path.basename(f)]

        if not compatible_files:
            # Check if there were any files at all
            if not all_files:
                 logging.info(f"Directory is empty: {input_path}")
                 print(f"[INFO] Directory is empty: {input_path}")
                 return
            else:
                 # Directory has files, but none are supported. Throw Exception as requested.
                 found_exts = set(os.path.splitext(f)[1] for f in all_files)
                 err_msg = f"No supported files found. Found {found_exts}. Please provide files with supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
                 logging.error(err_msg)
                 raise Exception(err_msg)

        logging.info(f"Found {len(compatible_files)} compatible files to analyze.")
        print(f"[INFO] Found {len(compatible_files)} compatible files to analyze.")

        # 3. Load Data
        dfs = load_data(compatible_files)
        if not dfs:
            logging.error("No data could be loaded. Exiting.")
            print("[ERROR] No data could be loaded. Exiting.")
            return

        # 4. Analyze
        table_pks, relationships = analyze_relationships(dfs)
        
        # 5. Detect Dates (extra info)
        date_info = []
        for name, df in dfs.items():
            d_cols = detect_date_columns(df)
            if d_cols:
                logging.info(f"Table '{name}': Found {len(d_cols)} date columns ({', '.join(d_cols)})")
            
            date_info.append({
                "File Name": name,
                "Date Columns": ", ".join(d_cols) if d_cols else "None"
            })

        # 6. Export Report
        output_file = os.path.join(input_path, "relationship_report.xlsx")
        logging.info(f"Saving report to: {output_file}")
        print(f"[INFO] Saving report to: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet A: Relationships
            if relationships:
                rel_df = pd.DataFrame(relationships)
            else:
                rel_df = pd.DataFrame(columns=["Child Table", "Child Column (FK)", "Parent Table", "Parent Column (PK)", "Cardinality"])
                logging.warning("No relationships detected.")
                print("[WARN] No relationships detected.")
            
            rel_df.to_excel(writer, sheet_name="Relationships", index=False)
            
            # Sheet B: Primary Keys and Date Columns can be separate or combined.
            pk_data = [{"Table": name, "Primary Key Candidates": ", ".join(pks)} for name, pks in table_pks.items()]
            pk_df = pd.DataFrame(pk_data)
            pk_df.to_excel(writer, sheet_name="Primary Keys", index=False)
            
            date_df = pd.DataFrame(date_info)
            date_df.to_excel(writer, sheet_name="Date Columns", index=False)
            
        logging.info("Analysis complete.")
        print("[SUCCESS] Analysis complete! Check the report file.")
        
    except Exception as e:
        logging.critical(f"Unexpected error: {e}", exc_info=True)
        print(f"[ERROR] An error occurred: {e}")
        print("Check analyzer_debug.log for details.")

if __name__ == "__main__":
    main()
