from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import date
import os

app = Flask(__name__)
#app.secret_key = 'server_inventory_secret_key_2024'

# ─── DB CONFIG ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'database': 'server_inventory',
    'user': 'root',
    'password': 'Welcome@123',
    'port': '3306',
    'autocommit': True
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"DB Connection error: {e}")
        return None

def query(sql, params=None, fetchone=False):
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        if sql.strip().upper().startswith('SELECT'):
            return cursor.fetchone() if fetchone else cursor.fetchall()
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Query error: {e}")
        return None
    finally:
        conn.close()

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    stats = {
        'physical': query("SELECT COUNT(*) as c FROM physical_inventory", fetchone=True)['c'],
        'virtual':  query("SELECT COUNT(*) as c FROM virtual_inventory",  fetchone=True)['c'],
        'license':  query("SELECT COUNT(*) as c FROM license_inventory",  fetchone=True)['c'],
        'warranty': query("SELECT COUNT(*) as c FROM warranty_info",       fetchone=True)['c'],
        'vendor':   query("SELECT COUNT(*) as c FROM vendor_info",         fetchone=True)['c'],
        'physical_active':  query("SELECT COUNT(*) as c FROM physical_inventory WHERE status='active'",  fetchone=True)['c'],
        'vm_running':       query("SELECT COUNT(*) as c FROM virtual_inventory WHERE status='running'",  fetchone=True)['c'],
        'license_expiring': query("SELECT COUNT(*) as c FROM license_inventory WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) AND expiry_date >= CURDATE()", fetchone=True)['c'],
        'warranty_expired': query("SELECT COUNT(*) as c FROM warranty_info WHERE status='expired'", fetchone=True)['c'],
    }
    return render_template('index.html', stats=stats)

# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICAL INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/physical')
def physical_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM physical_inventory WHERE 1=1"
    params = []
    if search:
        sql += " AND (hostname LIKE %s OR ip_address LIKE %s OR asset_tag LIKE %s OR manufacturer LIKE %s)"
        params += [f'%{search}%'] * 4
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY created_at DESC"
    rows = query(sql, params)
    return render_template('physical/list.html', rows=rows, search=search, status=status)

@app.route('/physical/add', methods=['GET','POST'])
def physical_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO physical_inventory
            (hostname,asset_tag,server_type,manufacturer,model,serial_number,cpu,cpu_cores,
             ram_gb,storage,datacenter,rack_location,ip_address,os,status,purchase_date,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['hostname'],f['asset_tag'],f['server_type'],f['manufacturer'],f['model'],
             f['serial_number'],f['cpu'],f.get('cpu_cores') or None,f.get('ram_gb') or None,
             f['storage'],f['datacenter'],f['rack_location'],f['ip_address'],f['os'],
             f['status'],f.get('purchase_date') or None,f['notes']))
        flash('Physical server added successfully!', 'success')
        return redirect(url_for('physical_list'))
    return render_template('physical/form.html', row=None, action='Add')

@app.route('/physical/edit/<int:id>', methods=['GET','POST'])
def physical_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE physical_inventory SET
            hostname=%s,asset_tag=%s,server_type=%s,manufacturer=%s,model=%s,serial_number=%s,
            cpu=%s,cpu_cores=%s,ram_gb=%s,storage=%s,datacenter=%s,rack_location=%s,
            ip_address=%s,os=%s,status=%s,purchase_date=%s,notes=%s WHERE id=%s""",
            (f['hostname'],f['asset_tag'],f['server_type'],f['manufacturer'],f['model'],
             f['serial_number'],f['cpu'],f.get('cpu_cores') or None,f.get('ram_gb') or None,
             f['storage'],f['datacenter'],f['rack_location'],f['ip_address'],f['os'],
             f['status'],f.get('purchase_date') or None,f['notes'],id))
        flash('Physical server updated!', 'success')
        return redirect(url_for('physical_list'))
    row = query("SELECT * FROM physical_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('physical/form.html', row=row, action='Edit')

@app.route('/physical/delete/<int:id>', methods=['POST'])
def physical_delete(id):
    query("DELETE FROM physical_inventory WHERE id=%s", (id,))
    flash('Physical server deleted.', 'warning')
    return redirect(url_for('physical_list'))

# ═══════════════════════════════════════════════════════════════════════════════
# VIRTUAL INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/virtual')
def virtual_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM virtual_inventory WHERE 1=1"
    params = []
    if search:
        sql += " AND (vm_name LIKE %s OR ip_address LIKE %s OR host_server LIKE %s OR owner LIKE %s)"
        params += [f'%{search}%'] * 4
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY created_at DESC"
    rows = query(sql, params)
    return render_template('virtual/list.html', rows=rows, search=search, status=status)

@app.route('/virtual/add', methods=['GET','POST'])
def virtual_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO virtual_inventory
            (vm_name,host_server,hypervisor,vcpu,ram_gb,storage_gb,ip_address,os,environment,status,owner,project,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['vm_name'],f['host_server'],f['hypervisor'],f.get('vcpu') or None,
             f.get('ram_gb') or None,f.get('storage_gb') or None,f['ip_address'],
             f['os'],f['environment'],f['status'],f['owner'],f['project'],f['notes']))
        flash('Virtual machine added!', 'success')
        return redirect(url_for('virtual_list'))
    return render_template('virtual/form.html', row=None, action='Add')

@app.route('/virtual/edit/<int:id>', methods=['GET','POST'])
def virtual_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE virtual_inventory SET
            vm_name=%s,host_server=%s,hypervisor=%s,vcpu=%s,ram_gb=%s,storage_gb=%s,
            ip_address=%s,os=%s,environment=%s,status=%s,owner=%s,project=%s,notes=%s WHERE id=%s""",
            (f['vm_name'],f['host_server'],f['hypervisor'],f.get('vcpu') or None,
             f.get('ram_gb') or None,f.get('storage_gb') or None,f['ip_address'],
             f['os'],f['environment'],f['status'],f['owner'],f['project'],f['notes'],id))
        flash('Virtual machine updated!', 'success')
        return redirect(url_for('virtual_list'))
    row = query("SELECT * FROM virtual_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('virtual/form.html', row=row, action='Edit')

@app.route('/virtual/delete/<int:id>', methods=['POST'])
def virtual_delete(id):
    query("DELETE FROM virtual_inventory WHERE id=%s", (id,))
    flash('Virtual machine deleted.', 'warning')
    return redirect(url_for('virtual_list'))

# ═══════════════════════════════════════════════════════════════════════════════
# LICENSE INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/license')
def license_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM license_inventory WHERE 1=1"
    params = []
    if search:
        sql += " AND (software_name LIKE %s OR vendor LIKE %s OR assigned_to LIKE %s)"
        params += [f'%{search}%'] * 3
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY expiry_date ASC"
    rows = query(sql, params)
    return render_template('license/list.html', rows=rows, search=search, status=status)

@app.route('/license/add', methods=['GET','POST'])
def license_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO license_inventory
            (software_name,vendor,license_type,license_key,quantity,used_count,assigned_to,
             purchase_date,expiry_date,cost,support_contact,notes,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['software_name'],f['vendor'],f['license_type'],f['license_key'],
             f.get('quantity') or 1,f.get('used_count') or 0,f['assigned_to'],
             f.get('purchase_date') or None,f.get('expiry_date') or None,
             f.get('cost') or None,f['support_contact'],f['notes'],f['status']))
        flash('License added!', 'success')
        return redirect(url_for('license_list'))
    return render_template('license/form.html', row=None, action='Add')

@app.route('/license/edit/<int:id>', methods=['GET','POST'])
def license_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE license_inventory SET
            software_name=%s,vendor=%s,license_type=%s,license_key=%s,quantity=%s,used_count=%s,
            assigned_to=%s,purchase_date=%s,expiry_date=%s,cost=%s,support_contact=%s,
            notes=%s,status=%s WHERE id=%s""",
            (f['software_name'],f['vendor'],f['license_type'],f['license_key'],
             f.get('quantity') or 1,f.get('used_count') or 0,f['assigned_to'],
             f.get('purchase_date') or None,f.get('expiry_date') or None,
             f.get('cost') or None,f['support_contact'],f['notes'],f['status'],id))
        flash('License updated!', 'success')
        return redirect(url_for('license_list'))
    row = query("SELECT * FROM license_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('license/form.html', row=row, action='Edit')

@app.route('/license/delete/<int:id>', methods=['POST'])
def license_delete(id):
    query("DELETE FROM license_inventory WHERE id=%s", (id,))
    flash('License deleted.', 'warning')
    return redirect(url_for('license_list'))

# ═══════════════════════════════════════════════════════════════════════════════
# WARRANTY INFO
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/warranty')
def warranty_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM warranty_info WHERE 1=1"
    params = []
    if search:
        sql += " AND (device_name LIKE %s OR manufacturer LIKE %s OR asset_tag LIKE %s OR serial_number LIKE %s)"
        params += [f'%{search}%'] * 4
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY end_date ASC"
    rows = query(sql, params)
    return render_template('warranty/list.html', rows=rows, search=search, status=status)

@app.route('/warranty/add', methods=['GET','POST'])
def warranty_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO warranty_info
            (asset_tag,device_name,manufacturer,model,serial_number,warranty_type,provider,
             start_date,end_date,support_level,support_contact,ticket_url,contract_number,cost,notes,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['asset_tag'],f['device_name'],f['manufacturer'],f['model'],f['serial_number'],
             f['warranty_type'],f['provider'],f.get('start_date') or None,f.get('end_date') or None,
             f['support_level'],f['support_contact'],f['ticket_url'],f['contract_number'],
             f.get('cost') or None,f['notes'],f['status']))
        flash('Warranty record added!', 'success')
        return redirect(url_for('warranty_list'))
    return render_template('warranty/form.html', row=None, action='Add')

@app.route('/warranty/edit/<int:id>', methods=['GET','POST'])
def warranty_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE warranty_info SET
            asset_tag=%s,device_name=%s,manufacturer=%s,model=%s,serial_number=%s,warranty_type=%s,
            provider=%s,start_date=%s,end_date=%s,support_level=%s,support_contact=%s,ticket_url=%s,
            contract_number=%s,cost=%s,notes=%s,status=%s WHERE id=%s""",
            (f['asset_tag'],f['device_name'],f['manufacturer'],f['model'],f['serial_number'],
             f['warranty_type'],f['provider'],f.get('start_date') or None,f.get('end_date') or None,
             f['support_level'],f['support_contact'],f['ticket_url'],f['contract_number'],
             f.get('cost') or None,f['notes'],f['status'],id))
        flash('Warranty updated!', 'success')
        return redirect(url_for('warranty_list'))
    row = query("SELECT * FROM warranty_info WHERE id=%s", (id,), fetchone=True)
    return render_template('warranty/form.html', row=row, action='Edit')

@app.route('/warranty/delete/<int:id>', methods=['POST'])
def warranty_delete(id):
    query("DELETE FROM warranty_info WHERE id=%s", (id,))
    flash('Warranty record deleted.', 'warning')
    return redirect(url_for('warranty_list'))

# ═══════════════════════════════════════════════════════════════════════════════
# VENDOR INFO
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/vendor')
def vendor_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM vendor_info WHERE 1=1"
    params = []
    if search:
        sql += " AND (vendor_name LIKE %s OR category LIKE %s OR contact_name LIKE %s)"
        params += [f'%{search}%'] * 3
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY vendor_name ASC"
    rows = query(sql, params)
    return render_template('vendor/list.html', rows=rows, search=search, status=status)

@app.route('/vendor/add', methods=['GET','POST'])
def vendor_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO vendor_info
            (vendor_name,category,contact_name,contact_email,contact_phone,account_manager,
             am_email,am_phone,website,address,contract_start,contract_end,payment_terms,
             account_number,notes,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['vendor_name'],f['category'],f['contact_name'],f['contact_email'],f['contact_phone'],
             f['account_manager'],f['am_email'],f['am_phone'],f['website'],f['address'],
             f.get('contract_start') or None,f.get('contract_end') or None,
             f['payment_terms'],f['account_number'],f['notes'],f['status']))
        flash('Vendor added!', 'success')
        return redirect(url_for('vendor_list'))
    return render_template('vendor/form.html', row=None, action='Add')

@app.route('/vendor/edit/<int:id>', methods=['GET','POST'])
def vendor_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE vendor_info SET
            vendor_name=%s,category=%s,contact_name=%s,contact_email=%s,contact_phone=%s,
            account_manager=%s,am_email=%s,am_phone=%s,website=%s,address=%s,
            contract_start=%s,contract_end=%s,payment_terms=%s,account_number=%s,
            notes=%s,status=%s WHERE id=%s""",
            (f['vendor_name'],f['category'],f['contact_name'],f['contact_email'],f['contact_phone'],
             f['account_manager'],f['am_email'],f['am_phone'],f['website'],f['address'],
             f.get('contract_start') or None,f.get('contract_end') or None,
             f['payment_terms'],f['account_number'],f['notes'],f['status'],id))
        flash('Vendor updated!', 'success')
        return redirect(url_for('vendor_list'))
    row = query("SELECT * FROM vendor_info WHERE id=%s", (id,), fetchone=True)
    return render_template('vendor/form.html', row=row, action='Edit')

@app.route('/vendor/delete/<int:id>', methods=['POST'])
def vendor_delete(id):
    query("DELETE FROM vendor_info WHERE id=%s", (id,))
    flash('Vendor deleted.', 'warning')
    return redirect(url_for('vendor_list'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
