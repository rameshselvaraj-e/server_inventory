from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Welcome@123",
    "database": "server_inventory",
    "port": '3306'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/list")
def gpu_list():
    owner = request.args.get("owner", "").strip()
    model = request.args.get("model", "").strip()

    where_clauses = []
    params = []

    if owner:
        where_clauses.append("owner LIKE %s")
        params.append(f"%{owner}%")

    if model:
        where_clauses.append("model_name LIKE %s")
        params.append(f"%{model}%")

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(f"SELECT COUNT(*) AS total_gpus FROM gpu{where_sql}", params)
    total_gpus = cur.fetchone()["total_gpus"]

    cur.execute("SELECT COUNT(DISTINCT owner) AS total_owners FROM gpu")
    total_owners = cur.fetchone()["total_owners"]

    cur.execute(
        """
        SELECT model_name, COUNT(*) AS model_count
        FROM gpu
        GROUP BY model_name
        ORDER BY model_count DESC, model_name ASC
        """
    )
    model_counts = cur.fetchall()

    cur.execute(
        f"""
        SELECT id, owner, model_name, status
        FROM gpu
        {where_sql}
        ORDER BY id DESC
        """,
        params,    )
    gpus = cur.fetchall()

    cur.close()
    db.close()

    return render_template(
        "list.html",
        gpus=gpus,
        total_gpus=total_gpus,
        total_owners=total_owners,
        model_counts=model_counts,
        owner=owner,
        model=model,
    )

@app.route("/")
def index():
    return gpu_list()

if __name__ == "__main__":
    app.run(debug=True, host='192.168.73.128', port=5005)