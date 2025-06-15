# 🚗 Al-Hafiz Autos – Spare Parts Management System

**Al-Hafiz Autos** is a desktop GUI application for managing auto parts inventory and generating printable bills. Built with **Python (Tkinter)** and **SQLite**, it is designed to support small businesses in managing stock, recording sales, and issuing invoices efficiently.

---

## ✅ Features

- User login with registration, password reset, and change
- Add, update, and delete spare parts from inventory
- Sell parts and automatically update stock
- Record customer name and auto-generate **invoice numbers**
- View full **sales history** and print individual invoices
- **Search sales by invoice number**
- Consistent, user-friendly interface with window centering

---

## 🧰 Tech Stack

- **Frontend:** Python Tkinter
- **Backend:** SQLite
- **Others:** UUID (for invoice generation), datetime

---

## 📸 Screenshots

> _Add screenshots here showing the login window, dashboard, and printed bill (optional)_

---
## 📂 Project Structure

```text
├── main.py               # Entry point
├── login_window.py       # Handles login and registration
├── dashboard_window.py   # Inventory and sales dashboard
├── inventory_manager.py  # Inventory database logic
├── sales_manager.py      # Handles sales, invoices, and storage
├── sale_window.py        # Sales history view and bill printing
├── search_invoice.py     # Search and print past invoices
├── bill_printer.py       # Generates and formats bill text
└── autos.db              # SQLite database file (auto-created)


---

## 🚀 Getting Started

1. Make sure Python 3 is installed.
2. Clone this repo:
   ```bash
   https://github.com/Umair-Farooque/SpareParts-Management-System.git
   cd SpareParts-Management-System
```bash
python main.py
```
📌 Usage Notes
All data is stored locally in autos.db

Bills are saved as text and can be sent to a printer using the OS default

Each sale is recorded with a unique invoice number for tracking

👨‍🔧 Developed By
M. Umair Farooq
