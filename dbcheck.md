check DB Connectivity with itadmin user account.


-------------------------------------------------------
flask --app dbconncheck.py run --host 0.0.0.0 --port 5001


itadmin@vmwebapppr01:/data/server_inventory$ flask --app dbconncheck.py run --host 0.0.0.0 --port 5001
 * Serving Flask app 'dbconncheck.py'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://10.0.10.20:5001
Press CTRL+C to quit
10.0.0.186 - - [20/Sep/2026 02:17:40] "GET / HTTP/1.1" 404 -
10.0.0.186 - - [20/Sep/2026 02:17:51] "GET / HTTP/1.1" 404 -
127.0.0.1 - - [20/Sep/2026 02:18:15] "GET /health/db HTTP/1.1" 200 -
----------------------------------------------------
itadmin@vmwebapppr01:~$ sudo curl -i http://127.0.0.1:5001/health/db
HTTP/1.1 200 OK
Server: Werkzeug/3.1.8 Python/3.12.3
Date: Sun, 20 Sep 2026 02:18:15 GMT
Content-Type: application/json
Content-Length: 35
Connection: close

{"database":"mysql","status":"ok"}
itadmin@vmwebapppr01:~$
----------------------------------------------------------
