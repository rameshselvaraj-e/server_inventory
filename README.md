# Infrastructure — Server Inventory Management System

A full-stack CRUD web application for managing server infrastructure inventory.
Built with Python Flask, MySQL, HTML/CSS (dark industrial theme).

## Features
- **Physical Inventory** — rack/tower/blade servers, asset tracking, location
- **Virtual Inventory** — VMs, hypervisors, environments, owners
- **License Inventory** — software licenses, expiry tracking, usage counts
- **Warranty Info** — warranties, support levels, contract dates
- **Vendor Info** — vendor contacts, account managers, contract terms
- Search & filter on every page
- Status badges with color coding
- Dashboard with summary stats

## Project Structure
```
server_inventory/
├── app.py                  # Flask routes & DB logic
├── requirements.txt
├── schema.sql              # MySQL schema + sample data
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── index.html
    ├── physical/  list.html  form.html
    ├── virtual/   list.html  form.html
    ├── license/   list.html  form.html
    ├── warranty/  list.html  form.html
    └── vendor/    list.html  form.html
```

## Setup

### 1. MySQL Setup
```bash
mysql -u root -p < schema.sql
```

### 2. Python Environment
```bash
cd server_inventory
pip install -r requirements.txt
```

### 3. Configure DB credentials in app.py (or use env vars)
```python
DB_CONFIG = {
    'host':     'localhost',       # or DB_HOST env var
    'database': 'server_inventory',
    'user':     'root',
    'password': 'your_password',   # or DB_PASSWORD env var
}
```
Or set environment variables:
```bash
export DB_HOST=localhost
export DB_NAME=server_inventory
export DB_USER=root
export DB_PASSWORD=your_password
```

### 4. Run
```bash
python app.py
```
Open http://localhost:5000

## Environment Variables
| Variable      | Default            | Description         |
|---------------|--------------------|---------------------|
| DB_HOST       | localhost          | MySQL host          |
| DB_NAME       | server_inventory   | Database name       |
| DB_USER       | root               | MySQL user          |
| DB_PASSWORD   | your_password      | MySQL password      |
| DB_PORT       | 3306               | MySQL port          |
