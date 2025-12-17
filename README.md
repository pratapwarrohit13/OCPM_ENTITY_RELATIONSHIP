<div align="center">

# 🔮 OCPM Data Relationship Analyzer

### 🤖 Automatically Discover Hidden Connections in Your Data

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-black?style=for-the-badge&logo=flask)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

[Report Bug](https://github.com/StartItUp/OCPM_ERD_FLASK/issues) · [Request Feature](https://github.com/StartItUp/OCPM_ERD_FLASK/issues)

</div>

---

## 🚀 Why This Tool?

Tired of manually mapping hundreds of tables? **OCPM Data Relationship Analyzer** brings the power of algorithmic inference to your local machine. 

Simply drag-and-drop your dataset, and watch as it:
*   🕵️‍♂️ **Detects** Primary and Foreign Keys automatically.
*   🔗 **Infers** Relationships between disconnected tables.
*   🧠 **Generates** SQL JOIN queries for you instantly.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **Multi-Format Support** | 📄 CSV, 📊 Excel (`.xlsx`, `.xls`), 📜 JSON, 📑 TSV, 📝 TXT |
| **Intelligent Inference** | Uses column name matching & cardinality analysis to find Parent-Child relationships. |
| **SQL Generator** | 🛠️ auto-generates `LEFT JOIN` queries ready to paste into your SQL client. |
| **Instant Exports** | 📥 Download your analysis as **PDF**, **Excel**, or raw **JSON**. |
| **Session Control** | 🔄 "Home" button instantly resets your workspace for a fresh start. |
| **Big Data Ready** | 🏋️‍♂️ Smart chunking support for processing large CSV/TXT files without crashing. |

---

## 🛠️ Quick Start

Get up and running in **less than 60 seconds**.

### 1. Installation

```bash
# Clone the repo
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

## 🎨 Visual Preview

> *Drag & Drop your files...* 
>
> ![Upload](https://via.placeholder.com/800x200?text=Upload+Your+Files+Here)

> *...And get instant Relationship Maps!*
>
> ![Results](https://via.placeholder.com/800x400?text=Analysis+Results+Dashboard)

---

## 📂 Project Structure

```bash
OCPM_ERD_FLASK/
├── 📂 templates/       # HTML Front-end
├── 📂 static/          # CSS & JavaScript
├── 📂 uploads/         # Temp storage for analysis
├── 🐍 app.py           # Flask Entry Point
├── 🐍 data_analyzer.py # Core Logic Engine
├── 📄 requirements.txt # Dependencies
└── 📝 README.md        # You are here!
```

---

## 🤝 Contributing

We love contributions! 
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">
  <sub>Built with ❤️ by the Antigravity Team</sub>
</div>
