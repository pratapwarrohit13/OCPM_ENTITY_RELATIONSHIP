# 📊 OCPM Data Relationship Analyzer - User Guide

Hello there! 👋 Welcome to the **Data Relationship Analyzer**. 

This tool helps you automatically discover relationships between your data tables. Simply upload your files, and we'll do the heavy lifting to find Primary Keys, Foreign Keys, and how your tables connect! 🚀

---

## 📂 Supported Data Formats

We support a wide range of file formats to make your life easier:
*   **Excel** (`.xlsx`, `.xls`)
*   **CSV** (`.csv`)
*   **JSON** (`.json`) ✨ *New!*
*   **Tab-Separated** (`.tsv`)
*   **Text** (`.txt`)

---

## 🚀 How to Run the App

1.  Open your terminal or command prompt.
2.  Navigate to the project folder.
3.  Run the following command:
    ```bash
    python app.py
    ```
4.  Open your web browser and go to: `http://127.0.0.1:5000`

---

## 🛠️ Using the Tool

### 1. Upload Your Files
*   Click the **"Choose Files"** button.
*   Select one or multiple files from your computer.
*   Click **"Upload and Analyze"** button. 
*   *Tip: You can select multiple CSVs, JSONs, or Excel sheets at once!*

### 2. Explore Your Results 🔍
Once the analysis is done, you'll see a beautiful dashboard:

*   **Inferred Relationships Table**:
    *   This is the star of the show! ⭐ It shows which tables are acting as parents and children.
    *   **SQL Join Query**: We generate the exact SQL `JOIN` syntax for you.
    *   **Copy Button**: Click the little "Copy" button next to the SQL query to paste it directly into your database tool! 📋

*   **Filter Results**:
    *   Use the dropdown menu at the top to filter rows by specific tables. This also filters the SQL queries!

*   **Other Insights**:
    *   **Primary Key Candidates**: Potential unique identifiers for your tables.
    *   **Date Columns**: We identify which columns look like dates. 📅

### 3. Download Reports 📥
Want to take your data to go?
*   **Download Excel Report**: Get a full spreadsheet of the analysis.
*   **Download JSON Relationship**: Get the raw relationship data.
*   **Download PDF**: Get a clean, professional PDF report of the current view. 📄

### 4. Start Over (Reset) 🔄
*   Click the **"Home"** button in the top right corner. 🏠
*   This will **clear your session**, remove the uploaded files, and let you start fresh with a clean slate.

---

## 🧐 Troubleshooting

**Q: I clicked "Upload" but nothing happened?**
A: Make sure you selected at least one valid file! If valid, check the terminal for any error messages.

**Q: My JSON file isn't working!**
A: Ensure your JSON is structured as a list of records (e.g., `[{"id": 1, "name": "A"}, ...]`). Complex nested structures might need to be flattened first.

**Q: The relationships look wrong.**
A: The tool guesses relationships based on column names (like `CustomerID` matching `ID`) and data overlap. It's a helper, so always double-check with your domain knowledge! 🧠

---

**Happy Analyzing!** 🎉
