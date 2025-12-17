
import os
import logging
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from werkzeug.utils import secure_filename
import data_analyzer  # Import the analysis logic
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this for production
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['Result_FOLDER'] = os.path.join(os.getcwd(), 'results')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['Result_FOLDER'], exist_ok=True)

# Configure logging for the Flask app
logging.basicConfig(level=logging.DEBUG)

def params_to_list(files):
    # Depending on how the form sends data, files might be a list or logic needed
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    import uuid
    import shutil
    
    # Create a unique session ID for this request
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_folder, exist_ok=True)

    # Store session_id in user session
    session['session_id'] = session_id

    saved_files = []
    
    try:
        for file in files:
            if not file: continue
            
            try:
                data_analyzer.validate_file_extension(file.filename)
            except ValueError as e:
                flash(str(e))
                continue

            filename = secure_filename(file.filename)
            filepath = os.path.join(session_folder, filename)
            file.save(filepath)
            saved_files.append(filepath)

        if not saved_files:
            flash("No valid files uploaded.")
            shutil.rmtree(session_folder, ignore_errors=True) # Cleanup empty folder
            return render_template('index.html')
    except Exception as e:
        shutil.rmtree(session_folder, ignore_errors=True)
        raise e


    try:
        # Load Data
        dfs = data_analyzer.load_data(saved_files)
        
        # Analyze
        table_pks, relationships = data_analyzer.analyze_relationships(dfs)
        
        # Date Columns
        date_info = []
        for name, df in dfs.items():
            d_cols = data_analyzer.detect_date_columns(df)
            date_info.append({
                "File Name": name,
                "Date Columns": ", ".join(d_cols) if d_cols else "None"
            })

        # Generate Join Queries
        join_queries = data_analyzer.generate_join_queries(relationships)
        
        # Inject SQL into relationships for table display
        for i, rel in enumerate(relationships):
            if i < len(join_queries):
                rel['sql_query'] = join_queries[i]['sql']

        # Save Intermediate Results
        intermediate_data = {
            "relationships": relationships,
            "table_pks": table_pks,
            "date_info": date_info,
            "join_queries": join_queries
        }
        
        intermediate_file = os.path.join(session_folder, "intermediate_results.json")
        with open(intermediate_file, 'w') as f:
            json.dump(intermediate_data, f)

        # Prepare data for template
        # Convert PKS to list of dicts for easy iteration
        pk_display = [{"Table": k, "Keys": ", ".join(v)} for k, v in table_pks.items()]
        
        
        return render_template('index.html', 
                               analysis_done=True,
                               relationships=relationships, 
                               primary_keys=pk_display, 
                               date_columns=date_info,
                               join_queries=join_queries)

    except Exception as e:
        logging.error(f"Analysis failed: {e}", exc_info=True)
        flash(f"An error occurred during analysis: {str(e)}")
        return redirect(url_for('index'))
    # finally block removed as cleanup logic depends on whether we want to keep files for re-analysis or not

@app.route('/download/excel')
def download_excel():
    session_id = session.get('session_id')
    if not session_id:
        flash("No active analysis session found.")
        return redirect(url_for('index'))

    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    intermediate_file = os.path.join(session_folder, "intermediate_results.json")

    if not os.path.exists(intermediate_file):
        flash("Analysis data expired or not found.")
        return redirect(url_for('index'))

    try:
        with open(intermediate_file, 'r') as f:
            data = json.load(f)
        
        relationships = data.get('relationships', [])
        table_pks = data.get('table_pks', {})
        date_info = data.get('date_info', [])

        report_filename = "relationship_report.xlsx"
        report_path = os.path.join(session_folder, report_filename)
        
        data_analyzer.generate_excel_report(relationships, table_pks, date_info, report_path)
        
        return send_file(report_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Excel generation failed: {e}")
        flash("Failed to generate Excel report.")
        return redirect(url_for('index'))

@app.route('/download/json')
def download_json():
    session_id = session.get('session_id')
    if not session_id:
        flash("No active analysis session found.")
        return redirect(url_for('index'))

    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    intermediate_file = os.path.join(session_folder, "intermediate_results.json")

    if not os.path.exists(intermediate_file):
        flash("Analysis data expired or not found.")
        return redirect(url_for('index'))
    
    try:
        with open(intermediate_file, 'r') as f:
            data = json.load(f)
        
        relationships = data.get('relationships', [])
        table_pks = data.get('table_pks', {})
        date_info = data.get('date_info', [])
        
        json_filename = "analysis_results.json"
        json_path = os.path.join(session_folder, json_filename)
        
        # calling existing generate_json_report or just dumping existing data
        # data_analyzer.generate_json_report expects specific args, let's just dump our clean structure or reuse the function
        # reusing function to ensure consistency
        data_analyzer.generate_json_report(relationships, table_pks, date_info, json_path)
        
        return send_file(json_path, as_attachment=True)
    except Exception as e:
        logging.error(f"JSON generation failed: {e}")
        flash("Failed to generate JSON report.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
