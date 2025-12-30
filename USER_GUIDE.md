# 📊 OCPM Data Relationship Analyzer - User Guide

Hello there! 👋 Welcome to the **Data Relationship Analyzer**.

This tool helps you automatically discover relationships between your data tables. Simply upload your files, and we'll do the heavy lifting to find Primary Keys, Foreign Keys, and how your tables connect! 🚀

---

## 📂 Supported Data Formats

We support a wide range of file formats to make your life easier:
*   **Excel** (`.xlsx`, `.xls`)
*   **CSV** (`.csv`)
*   **JSON** (`.json`)
*   **Tab-Separated** (`.tsv`)
*   **Text** (`.txt`)

> **Note on Large Files**: We support large CSV and Text files! 🏋️‍♂️ The tool processes them in smart chunks, so you can upload files with millions of rows without crashing your browser.

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
*   Click the **"Choose Files"** button (or drag and drop your files into the box).
*   Select one or multiple files from your computer.
*   Click the **"Analyze Files"** button.
*   *Tip: You can select multiple CSVs, JSONs, or Excel sheets at once!*

### 2. Explore Your Results 🔍
Once the analysis is done, you'll see a dashboard with three main sections:

#### A. Inferred Relationships
This is the core of the analysis! ⭐ It shows which tables are connected as parents and children.
*   **Child Table**: The table containing the foreign key.
*   **Child Column (FK)**: The column linking to the parent.
*   **Parent Table**: The table containing the primary key.
*   **Parent Column (PK)**: The unique identifier in the parent table.
*   **Cardinality**: The type of relationship (e.g., `n:1` for Many-to-One).

#### B. Primary Key Candidates
This table lists each of your uploaded files and suggests columns that could serve as **Primary Keys** (unique identifiers for each row).

#### C. Date Columns
We automatically scan your data to find columns that contain dates or timestamps, which is useful for timeline analysis. 📅

### 3. Start Over (Reset) 🔄
*   Click the **"Home"** button in the top left corner. 🏠
*   This will **clear your session**, remove the uploaded files, and let you start fresh with a clean slate.

---

## 🧐 Troubleshooting

**Q: I clicked "Analyze Files" but nothing happened?**
A: Make sure you have selected at least one file!

**Q: My JSON file isn't working!**
A: Ensure your JSON is structured as a list of records (e.g., `[{"id": 1, "name": "A"}, ...]`). Complex nested structures might need to be flattened first.

**Q: The relationships look wrong.**
A: The tool estimates relationships based on column name matching (like `CustomerID` in one table matching `ID` in another) and data overlap. It's an intelligent assistant, but always use your domain knowledge to verify! 🧠

---

**Happy Analyzing!** 🎉
