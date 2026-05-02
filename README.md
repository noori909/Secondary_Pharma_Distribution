# Quetta Pharma Distribution System 💊

A robust, enterprise-grade management solution specifically engineered for **Secondary Pharmaceutical Distributors**. This system streamlines inventory tracking, credit-based sales, automated cloud-security, and high-precision financial reporting.

---

## 🏗️ The 2ndry Distribution Business Logic

Unlike standard retail software, this system is architected to handle the complex margin structures of a **Secondary Pharma Distributor**:

*   **Pricelist Logic (TP Calculation)**: The system automatically maintains companies' instructed margins. Goods are tracked by **MRP** (Maximum Retail Price), but the **TP** (Trade Price) is locked at **MRP - 15%**.
*   **Variable Discounting**: It handles specialized customer-tiering. While the company provides the base TP, distributors can apply further **bonuses and discounts** (e.g., 0%, 4%, 7%, 12%) based on specific customer volume or company-mandated targets.
*   **The 8% Final Margin**: The core financial engine calculates the distributor's net profit as a clean **8% of the total liquidated revenue** (the actual collected sum after all TP and bonus discounts are applied).

---

## 🚀 Key Features

### 1. Automated E.O.D Intelligence 📧
At 10:00 PM daily (or upon application shutdown), the "Postman" logic fires:
*   Generates a professional **HTML Sales Summary**.
*   Dispatches it directly to the boss's and stakeholders' inboxes.
*   Provides a clear breakdown of **Cash Collected** vs. **Credit Pending**.

### 2. Triple-Layer Data Security 🛡️
*   **Local Persistence**: Automated SQLite database management.
*   **Time-Stamped Backups**: Every session creates a local `.zip` archive (keeping the last 30 days).
*   **Cloud Vault (Google Drive)**: Every backup is automatically mirrored to a designated **Google Drive Folder** for off-site disaster recovery.

### 3. Professional PDF Suite 📑
*   **Sales Receipts**: Branded receipts with business contact info, tiered discount percentages, and legal disclaimers.
*   **Report Exporting**: Export any filtered view (date ranges, specific areas, or sales reps) into a high-quality PDF document for physical records.

### 4. Zero-Friction Distribution 📦
The application is delivered as a **portable Windows Executable (.exe)**. 
*   **Machine Independent**: No Python installation required.
*   **Smart AppData**: Stores all databases and backups in the Windows `%APPDATA%` directory to avoid file-permission errors.
*   **OAuth Security**: Uses official Google OAuth2 for cloud syncing. Authenticates once per machine and runs silently thereafter.

---

## 📂 Project Structure

```text
PharmaProject/
├── main.py                 # Entry point (Tkinter Mainloop)
├── config.py               # Windows AppData & Path routing
├── data/
│   ├── database.py         # SQLAlchemy engine & URL mapping
│   ├── models.py           # SQL Schema (Products, Sales, Reps, etc.)
│   └── init_db.py          # Migration logic & DB creation
├── logic/
│   ├── backup_logic.py     # ZIP & Rotation algorithms
│   └── profit_logic.py     # Secondary margin calculations
├── services/
│   ├── gdrive_service.py   # Google Drive API (OAuth Desktop)
│   ├── email_service.py    # SMTP Postman logic (HTML Templates)
│   └── scheduler.py        # Background 10 PM daemon threads
└── ui/
    ├── main_app.py         # Navigation & Window Management
    ├── dashboard.py        # Business Intelligence Overview
    ├── sales_ui.py         # The Sales & Invoice Engine
    └── reports_ui.py       # Data filtering & PDF exporting
```

---

## 🛠️ Technology Stack
*   **Language**: Python 3.x
*   **UI Framework**: Tkinter (Stylized Modern Dark/Light Theme)
*   **ORM**: SQLAlchemy (SQLite Engine)
*   **Reporting**: ReportLab (PDF Generation)
*   **Cloud**: Google Drive V3 API, SMTP (Gmail App Passwords)
*   **Packaging**: PyInstaller (Windows Standalone)

---

## 👨‍💻 Developer Note
Designed with a focus on simplicity, speed, and reliability for warehouse environments. Built to ensure that even if the local computer fails, the business records remain safely immortalized in the cloud.

## Future Updates
* Cloud Integration 
* Updated email with products and reps info
* Company classification 
* More flexibility in pricing items even on the dashboard
* Products vise profit reports
* Profit placing on companies (hard coded for each)
* A dashboard app for the reps to place their orders with discounts ready to be printed
* An editable email list to send the reports to Bosses, new emails can be added and unused alcan be deleted directly from the app.
