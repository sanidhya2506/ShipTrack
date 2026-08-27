from flask import Flask, jsonify, send_file
import sqlite3
import csv
import os

app = Flask(__name__)

DATABASE = "database.db"
CSV_FOLDER = "output/processed_shipments.csv"

def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            order_id INTEGER,
            warehouse TEXT,
            carrier TEXT,
            city TEXT,
            product_category TEXT,
            order_date TEXT,
            promised_date TEXT,
            delivery_date TEXT,
            status TEXT,
            delivery_days INTEGER,
            days_late INTEGER
        )
    """)

    cursor.execute("DELETE FROM shipments")

    csv_file = CSV_FOLDER

    if not os.path.exists(csv_file):
        print("Processed CSV not found.")
        conn.close()
        return

    with open(csv_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO shipments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["order_id"], row["warehouse"], row["carrier"], row["city"],
                row["product_category"], row["order_date"], row["promised_date"],
                row["delivery_date"], row["status"], row["delivery_days"], row["days_late"]
            ))

    conn.commit()
    conn.close()
    print("SQLite database created successfully!")


@app.route("/")
def home():
    return send_file("dashboard.html")


@app.route("/api/metrics")
def metrics():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM shipments")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shipments WHERE status = 'DELIVERED'")
    delivered = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shipments WHERE status = 'LATE'")
    late = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(delivery_days) FROM shipments")
    average_delivery = cursor.fetchone()[0]

    late_rate = round((late / total_orders) * 100, 2) if total_orders > 0 else 0

    conn.close()

    return jsonify({
        "total_orders": total_orders,
        "delivered": delivered,
        "late": late,
        "late_rate": late_rate,
        "average_delivery": round(average_delivery, 2) if average_delivery else 0
    })


@app.route("/api/warehouses")
def warehouses():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT warehouse, COUNT(*) AS total_orders,
               SUM(CASE WHEN status = 'LATE' THEN 1 ELSE 0 END) AS late_orders
        FROM shipments GROUP BY warehouse
    """)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"warehouse": r[0], "total_orders": r[1], "late_orders": r[2]} for r in rows])


@app.route("/api/carriers")
def carriers():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT carrier, COUNT(*) AS total_orders,
               SUM(CASE WHEN status = 'LATE' THEN 1 ELSE 0 END) AS late_orders
        FROM shipments GROUP BY carrier
    """)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"carrier": r[0], "total_orders": r[1], "late_orders": r[2]} for r in rows])


create_database()

if __name__ == "__main__":
    app.run(debug=True)