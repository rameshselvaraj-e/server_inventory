from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
import mysql.connector
from mysql.connector import Error
from datetime import date
#import pandas as pd
import os, io
import csv

app = Flask(__name__)
#app.secret_key = 'server_inventory_secret_key_2024'
app.secret_key = 'sim_secret_key'
# ─── DB CONFIG ────────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'database': 'server_inventory',
    'user': 'admin',
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
        'gpu':      query("SELECT COUNT(*) as c FROM gpu_inventory",       fetchone=True)['c'],
        'storage':  query("SELECT COUNT(*) as c FROM storage_inventory",   fetchone=True)['c'],
        'disposal': query("SELECT COUNT(*) as c FROM disposal_inventory", fetchone=True)['c'],
        'physical_active':  query("SELECT COUNT(*) as c FROM physical_inventory WHERE status='active'",  fetchone=True)['c'],
        'physical_decom':  query("SELECT COUNT(*) as c FROM physical_inventory WHERE status='decommissioned'",  fetchone=True)['c'],
        'vm_running':       query("SELECT COUNT(*) as c FROM virtual_inventory WHERE status='running'",  fetchone=True)['c'],
        'vm_stopped':       query("SELECT COUNT(*) as c FROM virtual_inventory WHERE status='stopped'",  fetchone=True)['c'],
        'license_active':  query("SELECT COUNT(*) as c FROM license_inventory WHERE status='active'",  fetchone=True)['c'],
        'license_expiring': query("SELECT COUNT(*) as c FROM license_inventory WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) AND expiry_date >= CURDATE()", fetchone=True)['c'],
        'license_expired':  query("SELECT COUNT(*) as c FROM license_inventory WHERE status='expired'",  fetchone=True)['c'],
        'warranty_active': query("SELECT COUNT(*) as c FROM warranty_info WHERE status='active'", fetchone=True)['c'],
        'warranty_expired': query("SELECT COUNT(*) as c FROM warranty_info WHERE status='expired'", fetchone=True)['c'],
        'warranty_extended': query("SELECT COUNT(*) as c FROM warranty_info WHERE status='extended'", fetchone=True)['c'],
        'gpu_active':       query("SELECT COUNT(*) as c FROM gpu_inventory WHERE status='active'", fetchone=True)['c'],
        'storage_faulty':   query("SELECT COUNT(*) as c FROM storage_inventory WHERE status IN ('faulty','degraded')", fetchone=True)['c'],
        'total_storage_tb': query("SELECT COALESCE(ROUND(SUM(capacity_tb),1),0) as c FROM storage_inventory WHERE status != 'decommissioned'", fetchone=True)['c'],
        'disposal_list': query("SELECT COUNT(*) as c FROM disposal_inventory WHERE status='decommissioned'",  fetchone=True)['c'],
        'site':  query("SELECT COUNT(*) as c FROM site_info",   fetchone=True)['c'],
        'cables_qty': query("SELECT COALESCE(SUM(quantity),0) as c FROM cable_inventory WHERE status!='disposed'", fetchone=True)['c'],
        'cables_used': query("SELECT COALESCE(SUM(used),0) as c FROM cable_inventory WHERE Used!=0",  fetchone=True)['c'],
        'cables_available': query("SELECT COALESCE(SUM(available),0) as c FROM cable_inventory WHERE available!=0",  fetchone=True)['c'],
        }
    return render_template('index.html', stats=stats)
    #    'cables': query("SELECT COUNT(*) as c FROM cable_inventory",   fetchone=True)['c'],
    #    'cables_qty': query("SELECT COALESCE(SUM(quantity),0)  as c FROM cable_inventory WHERE status != 'disposed'", fetchone=True)['c'],
    #    'parts_list':  query("SELECT COUNT(*) as c FROM Inv_parts",  fetchone=True)['c'],
    #    'parts_Used': query("SELECT COUNT(*) as c FROM Inv_parts WHERE Used = 1",  fetchone=True)['c'],
    #    'parts_Available':  query("SELECT COUNT(*) as c FROM Inv_parts WHERE Available = 1",  fetchone=True)['c'],

# ═══════════════════════════════════════════════════════════════════════════════
# SITES INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/site')
def site_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM site_info WHERE 1=1"
    params = []
    if search:
        sql += " AND (entity LIKE %s OR site_name LIKE %s)"
        params += [f'%{search}%'] * 2
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY created_at ASC"
    rows = query(sql, params)
    return render_template('site/list.html', rows=rows, search=search, status=status)

@app.route('/site/add', methods=['GET','POST'])
def site_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO site_info
            (entity,site_name,address,contact_name,contact_email,notes)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (f['entity'],f['site_name'],f['address'],f['contact_name'],f['contact_email'],f['notes']))
        flash('Sites added!', 'success')
        return redirect(url_for('site_list'))
    return render_template('site/form.html', row=None, action='Add')

@app.route('/site/edit/<int:id>', methods=['GET','POST'])
def site_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE site_info SET
            entity=%s,site_name=%s,address=%s,contact_name=%s,contact_email=%s,notes=%s WHERE id=%s""",
            (f['entity'],f['site_name'],f['address'],f['contact_name'],f['contact_email'],f['notes'],id))
        flash('Sites updated!', 'success')
        return redirect(url_for('site_list'))
    row = query("SELECT * FROM site_info WHERE id=%s", (id,), fetchone=True)
    return render_template('site/form.html', row=row, action='Edit')

@app.route('/site/delete/<int:id>', methods=['POST'])
def site_delete(id):
    query("DELETE FROM site_info WHERE id=%s", (id,))
    flash('Site deleted.', 'warning')
    return redirect(url_for('site_list'))

@app.route('/site/export')
def site_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM site_info ORDER BY site_name ASC") or []

    headers = [
        'ID', 'Entity', 'Site Name', 'Address', 'Contact Name',
        'Contact Email', 'Notes'
    ]

    keys = [
        'id', 'entity', 'site_name', 'address', 'contact_name',
        'contact_email', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[S] if row[S] is not None else '' for S in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=site_export.csv'
        }
    )


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
        sql += " AND (hostname LIKE %s OR asset_tag LIKE %s OR serial_number LIKE %s OR manufacturer LIKE %s OR datacenter LIKE %s)"
        params += [f'%{search}%'] * 5
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY hostname ASC"
    rows = query(sql, params)
    return render_template('physical/list.html', rows=rows, search=search, status=status)

@app.route('/physical/add', methods=['GET','POST'])
def physical_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO physical_inventory
            (hostname,asset_tag,server_type,manufacturer,model,serial_number,cpu_type,cpu_cores,
             ram_gb,storage,datacenter,rack_location,mgmt_ipaddrs,server_ipaddrs,os,status,owners,support_end_date,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['hostname'],f['asset_tag'],f['server_type'],f['manufacturer'],f['model'],
             f['serial_number'],f['cpu_type'],f.get('cpu_cores') or None,f.get('ram_gb') or None,
             f['storage'],f['datacenter'],f['rack_location'],f['mgmt_ipaddrs'],f['server_ipaddrs'],f['os'],
             f['status'],f['owners'],f.get('support_end_date') or None,f['notes']))
        flash('Physical server added successfully!', 'success')
        return redirect(url_for('physical_list'))
    return render_template('physical/form.html', row=None, action='Add')

@app.route('/physical/edit/<int:id>', methods=['GET','POST'])
def physical_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE physical_inventory SET
            hostname=%s,asset_tag=%s,server_type=%s,manufacturer=%s,model=%s,serial_number=%s,
            cpu_type=%s,cpu_cores=%s,ram_gb=%s,storage=%s,datacenter=%s,rack_location=%s,
            mgmt_ipaddrs=%s,server_ipaddrs=%s,os=%s,status=%s,owners=%s,support_end_date=%s,notes=%s WHERE id=%s""",
            (f['hostname'],f['asset_tag'],f['server_type'],f['manufacturer'],f['model'],
             f['serial_number'],f['cpu_type'],f.get('cpu_cores') or None,f.get('ram_gb') or None,
             f['storage'],f['datacenter'],f['rack_location'],f['mgmt_ipaddrs'],f['server_ipaddrs'],f['os'],
             f['status'],f['owners'],f.get('support_end_date') or None,f['notes'],id))
        flash('Physical server updated!', 'success')
        return redirect(url_for('physical_list'))
    row = query("SELECT * FROM physical_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('physical/form.html', row=row, action='Edit')

@app.route('/physical/delete/<int:id>', methods=['POST'])
def physical_delete(id):
    query("DELETE FROM physical_inventory WHERE id=%s", (id,))
    flash('Physical server deleted.', 'warning')
    return redirect(url_for('physical_list'))

@app.route('/physical/export')
def physical_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM physical_inventory ORDER BY datacenter ASC") or []

    headers = [
        'ID', 'Host Name', 'Asset Tag', 'Server Type', 'Manufacturer', 'Model', 'Serial Number', 'CPU Type', 'CPU_Cores',
        'RAM(GB)', 'Storage', 'Datacenter', 'Rack Location', 'MGMT_IP', 'Server IP', 'OS', 'Status', 'Owners', 'Support End', 'Notes'
    ]

    keys = [
        'id', 'hostname', 'asset_tag', 'server_type', 'manufacturer', 'model', 'serial_number', 'cpu_type', 'cpu_cores',
        'ram_gb', 'storage', 'datacenter', 'rack_location', 'mgmt_ipaddrs', 'server_ipaddrs', 'os', 'status', 'owners', 'support_end_date', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[P] if row[P] is not None else '' for P in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=physical_export.csv'
        }
    )

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
        sql += " AND (vm_name LIKE %s OR ip_address LIKE %s OR host_server LIKE %s OR owner LIKE %s OR location LIKE %s)"
        params += [f'%{search}%'] * 5
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY vm_name ASC"
    rows = query(sql, params)
    return render_template('virtual/list.html', rows=rows, search=search, status=status)

@app.route('/virtual/add', methods=['GET','POST'])
def virtual_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO virtual_inventory
            (vm_name,host_server,hypervisor,vcpu,ram_gb,storage_gb,ip_address,os,environment,status,owner,role,location,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['vm_name'],f['host_server'],f['hypervisor'],f.get('vcpu') or None,
             f.get('ram_gb') or None,f.get('storage_gb') or None,f['ip_address'],
             f['os'],f['environment'],f['status'],f['owner'],f['role'],f['location'],f['notes']))
        flash('Virtual machine added!', 'success')
        return redirect(url_for('virtual_list'))
    return render_template('virtual/form.html', row=None, action='Add')

@app.route('/virtual/edit/<int:id>', methods=['GET','POST'])
def virtual_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE virtual_inventory SET
            vm_name=%s,host_server=%s,hypervisor=%s,vcpu=%s,ram_gb=%s,storage_gb=%s,
            ip_address=%s,os=%s,environment=%s,status=%s,owner=%s,role=%s,location=%s,notes=%s WHERE id=%s""",
            (f['vm_name'],f['host_server'],f['hypervisor'],f.get('vcpu') or None,
             f.get('ram_gb') or None,f.get('storage_gb') or None,f['ip_address'],
             f['os'],f['environment'],f['status'],f['owner'],f['role'],f['location'],f['notes'],id))
        flash('Virtual machine updated!', 'success')
        return redirect(url_for('virtual_list'))
    row = query("SELECT * FROM virtual_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('virtual/form.html', row=row, action='Edit')

@app.route('/virtual/delete/<int:id>', methods=['POST'])
def virtual_delete(id):
    query("DELETE FROM virtual_inventory WHERE id=%s", (id,))
    flash('Virtual machine deleted.', 'warning')
    return redirect(url_for('virtual_list'))

@app.route('/virtual/export')
def virtual_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM virtual_inventory ORDER BY vm_name ASC") or []

    headers = [
        'ID', 'VMName', 'Server Name', 'Hypervisor', 'VCPU', 'RAM(GB)', 'Storage(GB)', 'IP Address', 'OS',
        'Environment', 'Status', 'Owners', 'Role', 'Location', 'Notes'
    ]

    keys = [
        'id', 'vm_name', 'host_server', 'hypervisor', 'vcpu', 'ram_gb', 'storage_gb', 'ip_address', 'os',
        'environment', 'status', 'owner', 'role', 'location', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[V] if row[V] is not None else '' for V in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=virtual_export.csv'
        }
    )


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
            (software_name,vendor,customer_number,license_type,license_key,quantity,used_count,assigned_to,
             purchase_date,expiry_date,cost,support_contact,notes,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['software_name'],f['vendor'],f['customer_number'],f['license_type'],f['license_key'],
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
            software_name=%s,vendor=%s,customer_number=%s,license_type=%s,license_key=%s,quantity=%s,used_count=%s,
            assigned_to=%s,purchase_date=%s,expiry_date=%s,cost=%s,support_contact=%s,
            notes=%s,status=%s WHERE id=%s""",
            (f['software_name'],f['vendor'],f['customer_number'],f['license_type'],f['license_key'],
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

@app.route('/license/export')
def license_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM license_inventory ORDER BY expiry_date ASC") or []

    headers = [
        'ID', 'Software Name', 'Vendor', 'customer_number', 'License Type', 'License Key', 'Quantity', 'Used', 'Assigned To', 'Purchase Date',
        'Expiry Date', 'Cost', 'Support Contact', 'Notes', 'Status'
    ]

    keys = [
        'id', 'software_name', 'vendor', 'customer_number', 'license_type', 'license_key', 'quantity', 'used_count', 'assigned_to',
        'purchase_date', 'expiry_date', 'cost', 'support_contact', 'notes', 'status'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[L] if row[L] is not None else '' for L in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=license_export.csv'
        }
    )
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
        sql += " AND (asset_tag LIKE %s OR server_name LIKE %s OR manufacturer LIKE %s OR serial_number LIKE %s OR status LIKE %s)"
        params += [f'%{search}%'] * 5
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY support_end_date ASC"
    rows = query(sql, params)
    return render_template('warranty/list.html', rows=rows, search=search, status=status)

@app.route('/warranty/add', methods=['GET','POST'])
def warranty_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO warranty_info
            (asset_tag,server_name,manufacturer,model,serial_number,service_support,shipped_date,
             support_start_date,support_end_date,warranty_status,support_level,support_contact,owners,contract_number,manage_by,status,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['asset_tag'],f['server_name'],f['manufacturer'],f['model'],f['serial_number'],
             f['service_support'],f.get('shipped_date') or None,f.get('support_start_date') or None,f.get('support_end_date') or None,f.get('warranty_status') or None,
             f['support_level'],f['support_contact'],f['owners'],f['contract_number'],
             f['manage_by'],f['status'],f['notes']))
        flash('Warranty record added!', 'success')
        return redirect(url_for('warranty_list'))
    return render_template('warranty/form.html', row=None, action='Add')

@app.route('/warranty/edit/<int:id>', methods=['GET','POST'])
def warranty_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE warranty_info SET
            asset_tag=%s,server_name=%s,manufacturer=%s,model=%s,serial_number=%s,
            service_support=%s,shipped_date=%s,support_start_date=%s,support_end_date=%s,warranty_status=%s,support_level=%s,support_contact=%s,owners=%s,
            contract_number=%s,manage_by=%s,status=%s,notes=%s WHERE id=%s""",
            (f['asset_tag'],f['server_name'],f['manufacturer'],f['model'],f['serial_number'],
             f['service_support'],f.get('shipped_date') or None,f.get('support_start_date') or None,f.get('support_end_date') or None,f.get('warranty_status') or None,
             f['support_level'],f['support_contact'],f['owners'],f['contract_number'],
             f['manage_by'],f['status'],f['notes'], id))
        flash('Warranty updated!', 'success')
        return redirect(url_for('warranty_list'))
    row = query("SELECT * FROM warranty_info WHERE id=%s", (id,), fetchone=True)
    return render_template('warranty/form.html', row=row, action='Edit')

@app.route('/warranty/delete/<int:id>', methods=['POST'])
def warranty_delete(id):
    query("DELETE FROM warranty_info WHERE id=%s", (id,))
    flash('Warranty record deleted.', 'warning')
    return redirect(url_for('warranty_list'))

@app.route('/warranty/export')
def warranty_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM warranty_info ORDER BY support_end_date ASC") or []

    headers = [
        'ID', 'Asset Tag', 'Server Name', 'Manufacturer', 'Model',
        'Serial Number', 'Service Support', 'Support Start Date',
        'Support End Date', 'Warranty Status', 'Support Level', 'Support Contact',
        'Owners', 'Contract Number', 'Managed By', 'Notes', 'Status'
    ]

    keys = [
        'id', 'asset_tag', 'server_name', 'manufacturer', 'model',
        'serial_number', 'service_support', 'support_start_date',
        'support_end_date', 'warranty_status', 'support_level', 'support_contact',
        'owners', 'contract_number', 'manage_by', 'notes', 'status'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[k] if row[k] is not None else '' for k in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=warranty_export.csv'
        }
    )


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
            (vendor_name,category,contact_email,contact_phone,account_manager,
             am_email,am_phone,website,login_id,address,contract_start,contract_end,payment_terms,
             account_number,notes,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['vendor_name'],f['category'],f['contact_email'],f['contact_phone'],
             f['account_manager'],f['am_email'],f['am_phone'],f['website'],f['login_id'],f['address'],
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
            vendor_name=%s,category=%s,contact_email=%s,contact_phone=%s,
            account_manager=%s,am_email=%s,am_phone=%s,website=%s,login_id=%s,address=%s,
            contract_start=%s,contract_end=%s,payment_terms=%s,account_number=%s,
            notes=%s,status=%s WHERE id=%s""",
            (f['vendor_name'],f['category'],f['contact_email'],f['contact_phone'],
             f['account_manager'],f['am_email'],f['am_phone'],f['website'],f['login_id'],f['address'],
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

@app.route('/vendor/export')
def vendor_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM vendor_info ORDER BY vendor_name ASC") or []

    headers = [
        'ID', 'Vendor Name', 'Category', 'Contact Email', 'Contact Phone', 'Account Manager', 'AM Email', 'AM Phone', 'Website', 'Login ID', 'Address', 'Contract Start', 'Contract End',
        'Payment Terms', 'Account Number', 'Notes', 'status'
    ]

    keys = [
        'id', 'vendor_name', 'category', 'contact_email', 'contact_phone', 'account_manager', 'am_email',
        'am_phone', 'website', 'login_id', 'address', 'contract_start', 'contract_end', 'payment_terms',
        'account_number', 'notes', 'status'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[E] if row[E] is not None else '' for E in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=vendor_export.csv'
        }
    )
# ═══════════════════════════════════════════════════════════════════════════════
# GPU INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/gpu')
def gpu_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM gpu_inventory WHERE 1=1"
    params = []
    if search:
        sql += " AND (server_name LIKE %s OR manufacturer LIKE %s OR gpu_model LIKE %s OR status LIKE %s OR owners LIKE %s)"
        params += [f'%{search}%'] * 5
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY server_name DESC"
    rows = query(sql, params)
    return render_template('gpu/list.html', rows=rows, search=search, status=status)

def get_data():
        conn = mysql.connector.connect(**DB_CONFIG)

        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT owners, COALESCE( gpu_model, 'TOTAL GPU') AS model, SUM(no_of_gpu) AS total_gpu
            FROM gpu_inventory
            GROUP BY owners, gpu_model WITH ROLLUP;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return data

@app.route('/gpu/dash')
def gpu_dash():
    data = get_data()
    return render_template('gpu/dashboard.html', gpu_data=data)

@app.route('/gpu/add', methods=['GET','POST'])
def gpu_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO gpu_inventory
            (server_name,ip_address,manufacturer,gpu_model,gpu_serial,server_model,server_serial_number,vram_gb,gpu_uuid,cuda_vers,no_of_gpu,driver_version,
            firmware_version,environment,status,purchase_date,owners,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['server_name'],f['ip_address'],f['manufacturer'],f['gpu_model'],f['gpu_serial'],f['server_model'],f['server_serial_number'],
             f.get('vram_gb') or None,f.get('gpu_uuid') or None,f['cuda_vers'],
             f['no_of_gpu'],f['driver_version'],f['firmware_version'],
             f['environment'],f['status'],f.get('purchase_date') or None,f['owners'],f['notes']))
        flash('GPU record added successfully!', 'success')
        return redirect(url_for('gpu_list'))
    return render_template('gpu/form.html', row=None, action='Add')

@app.route('/gpu/edit/<int:id>', methods=['GET','POST'])
def gpu_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE gpu_inventory SET
            server_name=%s,ip_address=%s,manufacturer=%s,gpu_model=%s,gpu_serial=%s,server_model=%s,server_serial_number=%s,vram_gb=%s,gpu_uuid=%s,cuda_vers=%s,no_of_gpu=%s,driver_version=%s,
            firmware_version=%s,environment=%s,status=%s,purchase_date=%s,owners=%s,notes=%s WHERE id=%s""",
            (f['server_name'],f['ip_address'],f['manufacturer'],f['gpu_model'],f['gpu_serial'],f['server_model'],f['server_serial_number'],
             f.get('vram_gb') or None,f.get('gpu_uuid') or None,f.get('cuda_vers') or None,
             f['no_of_gpu'],f['driver_version'],f['firmware_version'],f['environment'],f['status'],
             f.get('purchase_date') or None,f['owners'],f['notes'],id))
        flash('GPU record updated!', 'success')
        return redirect(url_for('gpu_list'))
    row = query("SELECT * FROM gpu_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('gpu/form.html', row=row, action='Edit')

@app.route('/gpu/delete/<int:id>', methods=['POST'])
def gpu_delete(id):
    query("DELETE FROM gpu_inventory WHERE id=%s", (id,))
    flash('GPU record deleted.', 'warning')
    return redirect(url_for('gpu_list'))

@app.route('/gpu/export')
def gpu_export():
    # Fetch all GPUs data
    rows = query("SELECT * FROM gpu_inventory ORDER BY server_name ASC") or []

    headers = [
        'ID', 'Server Name', 'Server IP Address', 'Manufacturer', 'GPU Model', 'GPU Serial', 'Server Model', 'Server Serial Number',
        'GPU RAM', 'GPU UUID', 'CUDA Vers', 'No Of GPUs', 'Driver Vers', 'FW Vers', 'Enviroenment', 'Status', 'Purchase Date', 'Owners',
        'Notes'
    ]

    keys = [
        'id', 'server_name', 'ip_address', 'manufacturer', 'gpu_model', 'gpu_serial', 'server_model',
        'server_serial_number', 'vram_gb', 'gpu_uuid', 'cuda_vers', 'no_of_gpu', 'driver_version',
        'firmware_version', 'environment', 'status', 'purchase_date', 'owners', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[g] if row[g] is not None else '' for g in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=gpu_export.csv'
        }
    )
# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/storage')
def storage_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM storage_inventory WHERE 1=1"
    params = []
    if search:
        sql += " AND (cluster_name LIKE %s OR manufacturer LIKE %s OR model LIKE %s OR node_name LIKE %s OR serial_number LIKE %s)"
        params += [f'%{search}%'] * 5
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY cluster_name DESC"
    rows = query(sql, params)
    return render_template('storage/list.html', rows=rows, search=search, status=status)

@app.route('/storage/add', methods=['GET','POST'])
def storage_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO storage_inventory
            (cluster_name,cluster_ipaddrs,node_name,node_ipaddrs,mgmt_ipaddrs,service_ipaddrs,interclus_ipaddrs,
            storage_type,manufacturer,model,serial_number,capacity_tb,asset_tag,used_tb,
            environment,status,purchase_date,support_end,owners,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['cluster_name'],f['cluster_ipaddrs'],f['node_name'],f['node_ipaddrs'],f['mgmt_ipaddrs'],
             f['service_ipaddrs'],f['interclus_ipaddrs'],f['storage_type'],f['manufacturer'],f['model'],
             f['serial_number'],f.get('capacity_tb') or None,f['asset_tag'],f.get('used_tb') or None,
             f['environment'],f['status'],f.get('purchase_date') or None,f.get('support_end'),
             f['owners'],f['notes']))
        flash('Storage device added successfully!', 'success')
        return redirect(url_for('storage_list'))
    return render_template('storage/form.html', row=None, action='Add')

@app.route('/storage/edit/<int:id>', methods=['GET','POST'])
def storage_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE storage_inventory SET
            cluster_name=%s,cluster_ipaddrs=%s,node_name=%s,node_ipaddrs=%s,mgmt_ipaddrs=%s,service_ipaddrs=%s,
            interclus_ipaddrs=%s,storage_type=%s,manufacturer=%s,model=%s,serial_number=%s,
            capacity_tb=%s,asset_tag=%s,used_tb=%s,environment=%s,status=%s,purchase_date=%s,
            support_end=%s,owners=%s,notes=%s WHERE id=%s""",
            (f['cluster_name'],f['cluster_ipaddrs'],f['node_name'],f['node_ipaddrs'],f['mgmt_ipaddrs'],
             f['service_ipaddrs'],f['interclus_ipaddrs'],f['storage_type'],f['manufacturer'],f['model'],
             f['serial_number'],f.get('capacity_tb') or None,f['asset_tag'],f.get('used_tb') or None,
             f['environment'],f['status'],f.get('purchase_date') or None,f.get('support_end'),
             f['owners'],f['notes'],id))

        flash('Storage device updated!', 'success')
        return redirect(url_for('storage_list'))
    row = query("SELECT * FROM storage_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('storage/form.html', row=row, action='Edit')

@app.route('/storage/delete/<int:id>', methods=['POST'])
def storage_delete(id):
    query("DELETE FROM storage_inventory WHERE id=%s", (id,))
    flash('Storage device deleted.', 'warning')
    return redirect(url_for('storage_list'))

@app.route('/storage/export')
def storage_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM storage_inventory ORDER BY cluster_name ASC") or []

    headers = [
        'ID', 'Cluster Name', 'Cluster IP Address', 'Node Name', 'Node IP Address', 'MGMT IP Address', 'Service IP Address', 'InterCluster IP',
        'Storage Type', 'Manufacturer', 'Model', 'Serial Number', 'Capacity(TB)', 'Asset Tag', 'Used(TB)', 'Environment', 'Status', 'Purchase Date',
        'Support End', 'Owners', 'Notes'
    ]

    keys = [
        'id', 'cluster_name', 'cluster_ipaddrs', 'node_name', 'node_ipaddrs', 'mgmt_ipaddrs', 'service_ipaddrs', 'interclus_ipaddrs',
        'storage_type', 'manufacturer', 'model', 'serial_number', 'capacity_tb', 'asset_tag', 'used_tb',
        'environment', 'status', 'purchase_date', 'support_end', 'owners', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[T] if row[T] is not None else '' for T in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=storage_export.csv'
        }
    )
# ═══════════════════════════════════════════════════════════════════════════════
# DISPOSAL INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/disposal')
def disposal_list():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    sql = "SELECT * FROM disposal_inventory WHERE 1=1"
    params = []
    if search:
        sql += " AND (hostname LIKE %s OR asset_tag LIKE %s OR serial_number LIKE %s OR manufacturer LIKE %s OR owners LIKE %s)"
        params += [f'%{search}%'] * 5
    if status:
        sql += " AND status=%s"
        params.append(status)
    sql += " ORDER BY decom_date DESC"
    rows = query(sql, params)
    return render_template('disposal/list.html', rows=rows, search=search, status=status)

@app.route('/disposal/add', methods=['GET','POST'])
def disposal_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO disposal_inventory
            (hostname,asset_tag,server_type,manufacturer,model,serial_number,cpu_type,cpu_cores,
             ram_gb,storage,datacenter,rack_location,mgmt_ipaddrs,server_ipaddrs,os,status,owners,support_end_date,decom_date,disposal_date,notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['hostname'],f['asset_tag'],f['server_type'],f['manufacturer'],f['model'],
             f['serial_number'],f['cpu_type'],f.get('cpu_cores') or None,f.get('ram_gb') or None,
             f['storage'],f['datacenter'],f['rack_location'],f['mgmt_ipaddrs'],f['server_ipaddrs'],f['os'],
             f['status'],f['owners'],f.get('support_end_date') or None,f.get('decom_date') or None,f.get('disposal_date') or None,f['notes']))
        flash('Physical server added successfully!', 'success')
        return redirect(url_for('disposal_list'))
    return render_template('disposal/form.html', row=None, action='Add')

@app.route('/disposal/edit/<int:id>', methods=['GET','POST'])
def disposal_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE disposal_inventory SET
            hostname=%s,asset_tag=%s,server_type=%s,manufacturer=%s,model=%s,serial_number=%s,
            cpu_type=%s,cpu_cores=%s,ram_gb=%s,storage=%s,datacenter=%s,rack_location=%s,
            mgmt_ipaddrs=%s,server_ipaddrs=%s,os=%s,status=%s,owners=%s,support_end_date=%s,decom_date=%s,disposal_date=%s,notes=%s WHERE id=%s""",
            (f['hostname'],f['asset_tag'],f['server_type'],f['manufacturer'],f['model'],
             f['serial_number'],f['cpu_type'],f.get('cpu_cores') or None,f.get('ram_gb') or None,
             f['storage'],f['datacenter'],f['rack_location'],f['mgmt_ipaddrs'],f['server_ipaddrs'],f['os'],
             f['status'],f['owners'],f.get('support_end_date') or None,f.get('decom_date') or None,f.get('disposal_date') or None,f['notes'],id))
        flash('Devices updated!', 'success')
        return redirect(url_for('disposal_list'))
    row = query("SELECT * FROM disposal_inventory WHERE id=%s", (id,), fetchone=True)
    return render_template('disposal/form.html', row=row, action='Edit')

@app.route('/disposal/delete/<int:id>', methods=['POST'])
def disposal_delete(id):
    query("DELETE FROM disposal_inventory WHERE id=%s", (id,))
    flash('Devices deleted.', 'warning')
    return redirect(url_for('disposal_list'))

@app.route('/disposal/export')
def disposal_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM disposal_inventory ORDER BY created_at DESC") or []

    headers = [
        'ID', 'Server Name', 'Asset Tag', 'Type', 'Manufacturer', 'Model',
        'Serial Number', 'CPU', 'CPU Cores', 'RAM', 'Storage', 'Data Center', 'Rack Location', 'MGMT IP Address', 'Server IP Address',
         'OS', 'Status', 'Owners', 'Support End Date', 'Decomm Date', 'Disposal Date', 'Notes'
    ]

    keys = [
        'id', 'hostname', 'asset_tag', 'server_type', 'manufacturer', 'model',
        'serial_number', 'cpu_type', 'cpu_cores', 'ram_gb', 'storage',  'datacenter', 'rack_location',
        'mgmt_ipaddrs', 'server_ipaddrs', 'os', 'status', 'owners', 'support_end_date', 'decom_date', 'disposal_date', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[k] if row[k] is not None else '' for k in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=disposal_export.csv'
        }
    )
# ═══════════════════════════════════════════════════════════════════════════════
# CABLES INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/cables')
def cable_list():
    search     = request.args.get('search','').strip()
    status     = request.args.get('status','')
    cable_type = request.args.get('cable_type','')
    sql        = "SELECT * FROM cable_inventory WHERE 1=1"
    params     = []
    if search:
        sql += (" AND (cable_name LIKE %s OR cable_type LIKE %s OR manufacturer LIKE %s"
        " OR project_name LIKE %s)")
        params += ['%'+search+'%']*4
    if status:
        sql += " AND status=%s"; params.append(status)
    if cable_type:
        sql += " AND cable_type=%s"; params.append(cable_type)
    sql += " ORDER BY project_name, cable_name"
    rows = query(sql, params)

    def _q(s,p=None): return query(s,p,fetchone=True) or {}
    stats = {
        'total':     (_q("SELECT COUNT(*) c FROM cable_inventory") or {}).get('c', 0),
        'in_stock':  (_q("SELECT COUNT(*) c FROM cable_inventory WHERE status='in_stock'") or {}).get('c', 0),
        'in_use':    (_q("SELECT COUNT(*) c FROM cable_inventory WHERE status='in_use'") or {}).get('c', 0),
        'total_qty': (_q("SELECT COALESCE(SUM(quantity),0) c FROM cable_inventory WHERE status!='disposed'") or {}).get('c', 0),
        'total_used': (_q("SELECT COALESCE(SUM(used),0) c FROM cable_inventory WHERE status!='available'") or {}).get('c', 0),
        'total_available': (_q("SELECT COALESCE(SUM(available),0) c FROM cable_inventory WHERE status!='used'") or {}).get('c', 0),
    #    'total_value': (_q("SELECT COALESCE(SUM(unit_cost*quantity),0) c FROM cable_inventory WHERE status!='disposed'") or {}).get('c', 0),
        'by_type':   query("SELECT cable_type, COUNT(*) cnt, COALESCE(SUM(quantity),0) qty, COALESCE(SUM(used),0) used, COALESCE(SUM(available),0) avl FROM cable_inventory GROUP BY cable_type ORDER BY cnt DESC LIMIT 8") or [],
    #    'by_type_count': (_q("SELECT cable_type, COUNT(*) cnt, COALESCE(SUM(quantity),0) AS qty, COALESCE(SUM(used),0) AS used, COALESCE(SUM(available),0) AS avl FROM cable_inventory GROUP BY cable_type ORDER BY cnt DESC LIMIT 8") or [],
        }
    return render_template('cables/list.html', rows=rows, search=search,
                           status=status, cable_type=cable_type, stats=stats)

@app.route('/cables/add', methods=['GET','POST'])
def cable_add():
    if request.method == 'POST':
        f = request.form
        query("""INSERT INTO cable_inventory
            (cable_name,project_name,lab_name,purchase_order,cable_type,
            length_m,speed_gbps,manufacturer,part_number,serial_number,
            quantity,used,available,location,datacenter,
            rack_location,vendor,purchase_date,tracking_number,received_date,
            condition_state,status,owners,notes)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (f['cable_name'],f['project_name'],f['lab_name'],f['purchase_order'],f['cable_type'],
            f.get('length_m') or None,f.get('speed_gbps') or None,f['manufacturer'],f['part_number'],f['serial_number'],
            f.get('quantity') or 1,f.get('used') or None,f.get('available') or None,f['location'],f['datacenter'],
            f['rack_location'],f['vendor'],f.get('purchase_date') or None,f['tracking_number'],f['received_date'],
            f['condition_state'],f['status'],f['owners'],f['notes']))
        flash('Cable added successfully!','success')
        return redirect(url_for('cable_list'))
    return render_template('cables/form.html', row=None, action='Add')


@app.route('/cables/edit/<int:id>', methods=['GET','POST'])
def cable_edit(id):
    if request.method == 'POST':
        f = request.form
        query("""UPDATE cable_inventory SET
            cable_name=%s,project_name=%s,lab_name=%s,purchase_order=%s,cable_type=%s,
            length_m=%s,speed_gbps=%s,manufacturer=%s,part_number=%s,serial_number=%s,
            quantity=%s,used=%s,available=%s,location=%s,datacenter=%s,
            rack_location=%s,vendor=%s,purchase_date=%s,tracking_number=%s,received_date=%s,
            condition_state=%s,status=%s,owners=%s,notes=%s WHERE id=%s""",
            (f['cable_name'],f['project_name'],f['lab_name'],f['purchase_order'],f['cable_type'],
            f.get('length_m') or None,f.get('speed_gbps') or None,f['manufacturer'],f['part_number'],f['serial_number'],
            f.get('quantity') or 1,f.get('used') or None,f.get('available') or None,f['location'],f['datacenter'],
            f['rack_location'],f['vendor'],f.get('purchase_date') or None,f['tracking_number'],f['received_date'],
            f['condition_state'],f['status'],f['owners'],f['notes'],id))
        flash('Cable updated!','success')
        return redirect(url_for('cable_list'))
    row = query("SELECT * FROM cable_inventory WHERE id=%s",(id,),fetchone=True)
    return render_template('cables/form.html', row=row, action='Edit')

@app.route('/cables/delete/<int:id>', methods=['POST'])
def cable_delete(id):
    query("DELETE FROM cable_inventory WHERE id=%s",(id,))
    flash('Cable deleted.','warning')
    return redirect(url_for('cable_list'))

@app.route('/cables/export')
def cable_export():
    # Fetch all warranty data
    rows = query("SELECT * FROM cable_inventory ORDER BY created_at DESC") or []

    headers = [
        'ID', 'Project Name', 'Purchase Order', 'Lab Name / IT', 'Cable Name',
        'Cable Type', 'Cable Length', 'Speed(GBPS)', 'Manufacture', 'Part Number',
        'Serial Number', 'Quantity', 'Used', 'Available', 'Location',
        'Datacenter', 'Rack Location', 'Vendor Name', 'Purchase Date', 'Tracking #',
        'Received Date', 'Stauts1', 'Status2', 'Owners', 'Notes',
    ]

    keys = [
        'id', 'project_name', 'purchase_order', 'lab_name', 'cable_name',
        'cable_type', 'length_m', 'speed_gbps', 'manufacturer', 'part_number',
        'serial_number',  'quantity', 'used', 'available', 'location',
        'datacenter', 'rack_location', 'vendor', 'purchase_date', 'tracking_number',
        'received_date', 'condition_state', 'status', 'owners', 'notes'
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    writer.writerow(headers)

    # Write data rows
    for row in rows:
        writer.writerow([row[k] if row[k] is not None else '' for k in keys])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=cables_export.csv'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

# ═══════════════════════════════════════════════════════════════════════════════
# PARTS & CABLES INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════
#@app.route('/parts')
#def parts_list():
#    search = request.args.get('search', '')
#    status = request.args.get('status', '')
#    sql = "SELECT * FROM parts_inventory WHERE 1=1"
#    params = []
#    if search:
#        sql += " AND (project_name LIKE %s OR cable_length LIKE %s OR product_make LIKE %s)"
#        params += [f'%{search}%'] * 3
#    if status:
#        sql += " AND status=%s"
#        params.append(status)
#    sql += " ORDER BY project_name DESC"
#    rows = query(sql, params)
#    return render_template('parts/list.html', rows=rows, search=search, status=status)

#@app.route('/parts/add', methods=['GET','POST'])
#def parts_add():
#    if request.method == 'POST':
#        f = request.form
#        query("""INSERT INTO parts_inventory
#            (project_name, owners, location, lab_name, purchase_order, product_make, part_number, cable_type, data_speed, cable_length, quantity, used, available, description, shipment_info, tracking_number, received_date, remarks)
#            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
#            (f['project_name'],f['owners'],f['location'],f['lab_name'],f['purchase_order'],
#             f['product_make'],f['part_number'],f['cable_type'],f['data_speed'],f['cable_length'],f['quantity'],f['used'],f['available'],
#             f['description'],f['shipment_info'],f['tracking_number'],f['received_date'],f['remarks']))
#        flash('Items added successfully!', 'success')
#        return redirect(url_for('parts_list'))
#    return render_template('parts/form.html', row=None, action='Add')

#@app.route('/parts/edit/<int:id>', methods=['GET','POST'])
#def parts_edit(id):
#    if request.method == 'POST':
#        f = request.form
#        query("""UPDATE parts_inventory SET
#            project_name=%s,owners=%s,location=%s,lab_name=%s,purchase_order=%s,product_make=%s,
#            part_number=%s,cable_type=%s,data_speed=%s,cable_length=%s,quantity=%s,used=%s,
#            available=%s,description=%s,shipment_info=%s,tracking_number=%s,received_date=%s,remarks=%s WHERE id=%s""",
#            (f['project_name'],f['owners'],f['location'],f['lab_name'],f['purchase_order'],f['product_make'],f['part_number'],
#            f['cable_type'],f['data_speed'],f['cable_length'],f['quantity'],f['used'],f['available'],f['description'],f['description'],
#            f['shipment_info'],f['tracking_number'],f['received_date'],f['remarks'],id))
#        flash('Items updated!', 'success')
#        return redirect(url_for('parts_list'))
#    row = query("SELECT * FROM parts_inventory WHERE id=%s", (id,), fetchone=True)
#    return render_template('parts/form.html', row=row, action='Edit')

#@app.route('/parts/delete/<int:id>', methods=['POST'])
#def parts_delete(id):
#    query("DELETE FROM parts_inventory WHERE id=%s", (id,))
#    flash('Item deleted.', 'warning')
#    return redirect(url_for('parts_list'))
