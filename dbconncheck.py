from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

@app.get("/health/db")
def database_health():
    conn = None

    try:
        conn = mysql.connector.connect(
            host= "localhost",
            port= "3306",
            user= "itadmin",
            password= "Itadmin@123",
            database= "server_inventory",
            connection_timeout=3,
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return jsonify(status="ok", database="mysql"), 200

    except Error as err:
        app.logger.exception("MySQL health check failed")
        return jsonify(status="error", database="mysql", message=str(err)), 503

    finally:
        if conn is not None and conn.is_connected():
            conn.close()