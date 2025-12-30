<div align="center">

# 🔮 OCPM Data Relationship Analyzer

### 🤖 Automatically Discover Hidden Connections in Your Data

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=for-the-badge&logo=flask)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🚀 Why This Tool?

Tired of manually mapping tables? **OCPM Data Relationship Analyzer** brings the power of algorithmic inference to your local machine.

Simply drag-and-drop your dataset, and watch as it:
*   🕵️‍♂️ **Detects** Primary and Foreign Keys automatically.
*   🔗 **Infers** Relationships between disconnected tables.
*   📅 **Identifies** Date columns for timeline analysis.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **Multi-Format Support** | 📄 CSV, 📊 Excel (`.xlsx`, `.xls`), 📜 JSON, 📑 TSV, 📝 TXT |
| **Intelligent Inference** | Uses column name matching & cardinality analysis to find Parent-Child relationships. |
| **Primary Key Detection** | Automatically suggests potential primary keys for each table. |
| **Date Column Detection** | Scans your data to find columns containing date information. |
| **Session Control** | 🔄 "Home" button instantly resets your workspace for a fresh start. |
| **Big Data Ready** | 🏋️‍♂️ Smart chunking support for processing large files efficiently. |

---

## 🛠️ Quick Start

Get up and running in **less than 60 seconds**.

### 1. Installation

```bash
# Clone the repo (if you haven't already)
git clone https://github.com/yourusername/OCPM_ERD_FLASK.git

# Enter directory
cd OCPM_ERD_FLASK

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

### 3. Analyze!
Open your browser to: `http://127.0.0.1:5000` 🌍

---

## 📂 Project Structure

```bash
OCPM_ERD_FLASK/
├── 📂 templates/       # HTML Front-end
├── 🐍 app.py           # Flask Entry Point
├── 🐍 data_analyzer.py # Core Logic Engine
├── 📄 requirements.txt # Dependencies
└── 📝 README.md        # You are here!
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
