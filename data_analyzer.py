import pandas as pd
import os
import glob
import logging
import json
from typing import List, Dict, Tuple, Any, Set

# ==============================================================================
# CONSTANTS
# ==============================================================================
LOG_FILE = "analyzer_debug.log"
SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.tsv', '.txt', '.json'}
CHUNK_SIZE = 50000  # Process 50k rows at a time for large files

# [CONFIG] Set your folder path here to avoid typing it every time.
# Example: INPUT_DIRECTORY = r"C:\Users\MyName\Documents\Data"
INPUT_DIRECTORY = r"" 


class AnalyzedTable:
    """
    Optimized structure to hold table metadata and samples without memory overhead.
    """
    def __init__(self, name: str):
        self.name = name
        self.row_count = 0
        self.columns = []
        self.dtypes = {}        # col -> dtype
        self.uniques: Dict[str, Set] = {}     # col -> set of unique values
        self.has_nulls = {}     # col -> bool
        self.sample_df = None   # For type inference (head)

    def is_col_unique(self, col: str) -> bool:
        """Checks if a column is a primary key candidate (Unique & No Nulls)."""
        if self.has_nulls.get(col, True):
            return False
        # If unique count == row count, it's unique
        return len(self.uniques.get(col, set())) == self.row_count


def validate_file_extension(file_path: str):
    """
    Validates if the file extension is supported.
    Raises ValueError if not supported.
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"File format '{ext}' is not supported. Please upload a file with one of these extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

def load_data(file_paths: List[str]) -> Dict[str, AnalyzedTable]:
    """
    Loads data files into AnalyzedTable objects using chunking for efficiency.
    """
    tables = {}
    for path in file_paths:
        filename = os.path.basename(path)
        try:
            validate_file_extension(path)
            table = AnalyzedTable(filename)
            
            # Helper to process a DataFrame chunk
            def process_df(df_chunk, is_first_chunk):
                if is_first_chunk:
                    table.sample_df = df_chunk.head(1000) # Keep a sample
                    table.columns = df_chunk.columns.tolist()
                    table.dtypes = df_chunk.dtypes.to_dict()
                
                table.row_count += len(df_chunk)
                
                for col in df_chunk.columns:
                    # Drop NaNs for unique set
                    valid_vals = df_chunk[col].dropna()
                    if len(valid_vals) < len(df_chunk[col]):
                        table.has_nulls[col] = True
                    else:
                        if col not in table.has_nulls: table.has_nulls[col] = False # Initialize

                    unique_updates = set(valid_vals.unique())
                    if col not in table.uniques:
                        table.uniques[col] = unique_updates
                    else:
                        table.uniques[col].update(unique_updates)

            # Loading Strategy based on file type
            if path.endswith(('.csv', '.txt', '.tsv')):
                # CHUNKED LOADING
                sep = '\t' if path.endswith('.tsv') else ','
                if path.endswith('.txt'): sep = None # Sniffer or python engine
                
                engine = 'python' if path.endswith('.txt') else 'c'
                # Use iterator
                try:
                    with pd.read_csv(path, sep=sep, chunksize=CHUNK_SIZE, engine=engine) as reader:
                        first = True
                        for chunk in reader:
                            process_df(chunk, first)
                            first = False
                except Exception as e:
                     # Fallback for small TXT files that might fail chunking or separator issues
                     logging.warning(f"Chunking failed for {filename}, trying full load: {e}")
                     df = pd.read_csv(path, sep=sep, engine=engine)
                     process_df(df, True)

            elif path.endswith('.json'):
                df = pd.read_json(path)
                process_df(df, True)

            elif path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(path)
                process_df(df, True)
            
            tables[filename] = table
            logging.info(f"Loaded {filename}: {table.row_count} rows processed.")

        except Exception as e:
            logging.error(f"Failed loading {filename}: {e}", exc_info=True)
            # Skip file on error
            
    return tables


def detect_primary_keys(table: AnalyzedTable) -> List[str]:
    """
    Identifies candidate primary keys from metadata.
    """
    pk_candidates = []
    for col in table.columns:
        if table.is_col_unique(col):
            pk_candidates.append(col)
    return pk_candidates

def detect_date_columns(table: AnalyzedTable) -> List[str]:
    """
    Identifies columns that look like dates using the sample.
    """
    date_cols = []
    df = table.sample_df
    if df is None or df.empty: return []

    for col in table.columns:
        if col not in df.columns: continue
        
        # Optimization: Skip likely numeric/bool columns
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_bool_dtype(df[col]):
             continue
             
        try:
            pd.to_datetime(df[col], errors='raise')
            date_cols.append(col)
        except (ValueError, TypeError):
            continue
    return date_cols

def analyze_relationships(tables: Dict[str, AnalyzedTable]):
    """
    Core Logic: Inter-table relationship inference.
    """
    # Step 1: Detect PKs
    logging.info("Detecting Primary Keys...")
    table_pks = {}
    for name, table in tables.items():
        pks = detect_primary_keys(table)
        table_pks[name] = pks
        if pks:
             logging.info(f"Table '{name}': Found {len(pks)} PK candidates ({', '.join(pks)})")
        else:
             logging.info(f"Table '{name}': No PK candidates found.")

    relationships = []
    
    files = list(tables.keys())
    logging.info(f"Analyzing {len(files)} files for relationships...")
    
    for i, child_file in enumerate(files):
        child_table = tables[child_file]
        
        for j, parent_file in enumerate(files):
            if i == j: continue
            
            parent_table = tables[parent_file]
            parent_pks = table_pks[parent_file]
            
            for pk in parent_pks:
                for col in child_table.columns:
                    try:
                        child_vals = child_table.uniques.get(col, set())
                        parent_vals = parent_table.uniques.get(pk, set())
                        
                        if not child_vals: continue

                        # --- Heuristic Name Check ---
                        parent_table_simple = os.path.splitext(parent_file)[0].lower().replace("s", "")
                        child_col_lower = col.lower()
                        pk_lower = pk.lower()
                        
                        is_name_match = (
                            child_col_lower == pk_lower or 
                            parent_table_simple in child_col_lower or
                            (pk_lower == "id" and child_col_lower.endswith("_id"))
                        )
                        
                        if not is_name_match: continue
                        
                        # --- Heuristic Data Type Check ---
                        child_dtype = child_table.dtypes.get(col)
                        parent_dtype = parent_table.dtypes.get(pk)
                        
                        is_child_numeric = pd.api.types.is_numeric_dtype(child_dtype)
                        is_parent_numeric = pd.api.types.is_numeric_dtype(parent_dtype)
                        
                        if is_child_numeric != is_parent_numeric: continue
                        
                        # --- Subset Check ---
                        if child_vals.issubset(parent_vals):
                            # Cardinality
                            if child_table.is_col_unique(col):
                                cardinality = "1:1"
                            else:
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
                        logging.warning(f"Error checking {child_file}.{col}: {e}")
                        continue
    
    logging.info(f"Relationship analysis complete. Found {len(relationships)} relationships.")
    return table_pks, relationships

def generate_join_queries(relationships: List[Dict]) -> List[Dict]:
    """
    Generates SQL JOIN queries based on inferred relationships.
    """
    queries = []
    for rel in relationships:
        child = rel['Child Table']
        parent = rel['Parent Table']
        child_clean = child.split('.')[0].replace(" ", "_").replace("-", "_")
        parent_clean = parent.split('.')[0].replace(" ", "_").replace("-", "_")
        child_col = rel['Child Column (FK)']
        parent_col = rel['Parent Column (PK)']
        
        query_sql = f"SELECT *\\nFROM {child_clean}\\nJOIN {parent_clean} ON {child_clean}.{child_col} = {parent_clean}.{parent_col};"
        
        # Use simple newline for clarity
        query_sql = f"SELECT *\\nFROM {child_clean}\\nJOIN {parent_clean} ON {child_clean}.{child_col} = {parent_clean}.{parent_col};"
        
        queries.append({
            'sql': query_sql,
            'child_table': child,
            'parent_table': parent
        })
    return queries

def generate_excel_report(relationships: List[Dict], table_pks: Dict[str, List[str]], date_info: List[Dict], output_file: str):
    logging.info(f"Saving report to: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        if relationships:
            rel_df = pd.DataFrame(relationships)
        else:
            rel_df = pd.DataFrame(columns=["Child Table", "Child Column (FK)", "Parent Table", "Parent Column (PK)", "Cardinality"])
        
        rel_df.to_excel(writer, sheet_name="Relationships", index=False)
        
        pk_data = [{"Table": name, "Primary Key Candidates": ", ".join(pks)} for name, pks in table_pks.items()]
        pd.DataFrame(pk_data).to_excel(writer, sheet_name="Primary Keys", index=False)
        pd.DataFrame(date_info).to_excel(writer, sheet_name="Date Columns", index=False)

def generate_json_report(relationships: List[Dict], table_pks: Dict[str, List[str]], date_info: List[Dict], output_file: str):
    logging.info(f"Saving JSON report to: {output_file}")
    data = {"relationships": relationships, "primary_keys": table_pks, "date_columns": date_info}
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

def generate_sql_ddl(tables: Dict[str, AnalyzedTable], table_pks: Dict[str, List[str]], relationships: List[Dict], output_file: str):
    """
    Generates a SQL DDL file to create tables and constraints.
    """
    logging.info(f"Saving SQL DDL to: {output_file}")
    
    statements = []
    
    def map_dtype(dtype):
        if pd.api.types.is_integer_dtype(dtype): return "INT"
        if pd.api.types.is_float_dtype(dtype): return "FLOAT"
        if pd.api.types.is_bool_dtype(dtype): return "BOOLEAN"
        if pd.api.types.is_datetime64_any_dtype(dtype): return "TIMESTAMP"
        return "VARCHAR(255)"

    for table_name, table in tables.items():
        clean_table_name = os.path.splitext(table_name)[0].replace(" ", "_").replace("-", "_")
        cols_def = []
        
        for col in table.columns:
            clean_col = col.replace(" ", "_").replace("-", "_")
            sql_type = map_dtype(table.dtypes[col])
            cols_def.append(f"    {clean_col} {sql_type}")
        
        pks = table_pks.get(table_name, [])
        if pks:
            clean_pks = [pk.replace(" ", "_") for pk in pks]
            cols_def.append(f"    PRIMARY KEY ({', '.join(clean_pks)})")
            
        create_stmt = f"CREATE TABLE {clean_table_name} (\\n" + ",\\n".join(cols_def) + "\\n);"
        statements.append(create_stmt)
        
    statements.append("")
    
    for rel in relationships:
        child_table = os.path.splitext(rel['Child Table'])[0].replace(" ", "_")
        child_col = rel['Child Column (FK)'].replace(" ", "_")
        parent_table = os.path.splitext(rel['Parent Table'])[0].replace(" ", "_")
        parent_col = rel['Parent Column (PK)'].replace(" ", "_")
        
        fk_stmt = f"ALTER TABLE {child_table} ADD FOREIGN KEY ({child_col}) REFERENCES {parent_table}({parent_col});"
        statements.append(fk_stmt)

    with open(output_file, 'w') as f:
        f.write("\\n".join(statements))

def main():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

    logging.info("Starting Celonis OCPM Data Analyzer")
    print("===========================================")
    print("   CELONIS OCPM DATA ANALYZER")
    print("===========================================")
    
    try:
        if INPUT_DIRECTORY and os.path.isdir(INPUT_DIRECTORY):
             input_path = INPUT_DIRECTORY
             print(f"[INFO] Using configured directory: {input_path}")
        else:
             input_path = input("Enter the directory path containing CSV/Excel files: ").strip().strip('"').strip("'")
             if not input_path: return

        if not os.path.isdir(input_path):
            logging.error(f"Invalid directory path: {input_path}")
            return

        all_files = glob.glob(os.path.join(input_path, "*.*"))
        compatible_files = [f for f in all_files if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
        compatible_files = [f for f in compatible_files if "relationship_report.xlsx" not in os.path.basename(f)]

        if not compatible_files:
            logging.error("No supported files found.")
            return

        logging.info(f"Found {len(compatible_files)} compatible files.")
        
        # Load Data (Optimized)
        tables = load_data(compatible_files)
        if not tables:
            logging.error("No data could be loaded.")
            return

        # Analyze
        table_pks, relationships = analyze_relationships(tables)
        
        # Detect Dates
        date_info = []
        for name, table in tables.items():
            d_cols = detect_date_columns(table)
            date_info.append({
                "File Name": name,
                "Date Columns": ", ".join(d_cols) if d_cols else "None"
            })

        # Exports
        output_file = os.path.join(input_path, "relationship_report.xlsx")
        generate_excel_report(relationships, table_pks, date_info, output_file)
        
        ddl_file = os.path.join(input_path, "schema_script.sql")
        generate_sql_ddl(tables, table_pks, relationships, ddl_file)
        
        logging.info("Analysis complete.")
        print("[SUCCESS] Analysis complete! Check the report files.")
        
    except Exception as e:
        logging.critical(f"Unexpected error: {e}", exc_info=True)
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()
