# Stationery Inventory SaaS

## Getting Started

### 1. Prerequisites
*   Python 3.x installed.

### 2. Setup
The project is already set up. If you need to reinstall:
```bash
python -m venv venv
venv\Scripts\activate
pip install django
python manage.py migrate
```

### 3. Running the Server
To start the application, run:
```bash
venv\Scripts\python manage.py runserver
```

### 4. Login
*   **URL:** `http://127.0.0.1:8000/login/`
*   **Username:** `admin`
*   **Password:** `admin123`

### 5. Features
*   **Dashboard:** View your inventory, costs, and total value.
*   **Add Category/Item/Purchase:** Manage your stock.
*   **Automatic WAC:** Cost updates automatically when you buy more stock.
*   **Print Report:** Click "Print Report" on the dashboard to generate a clean inventory list for printing.
