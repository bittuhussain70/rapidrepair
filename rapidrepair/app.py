import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

from ml_estimator import RapidRepairEstimator, SERVICE_BASE


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "rapidrepair.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "rapidrepair-dev")
estimator = RapidRepairEstimator()


SERVICES = [
    {
        "slug": "ac-general-service",
        "category": "AC Service",
        "name": "AC General Service",
        "price": 499,
        "duration": "45 min",
        "badge": "Most booked",
        "description": "Filter cleaning, cooling check, drain check, and indoor unit wash.",
    },
    {
        "slug": "ac-jet-cleaning",
        "category": "AC Service",
        "name": "AC Jet Cleaning",
        "price": 899,
        "duration": "70 min",
        "badge": "Deep clean",
        "description": "High pressure indoor coil cleaning for better airflow and cooling.",
    },
    {
        "slug": "ac-repair",
        "category": "AC Repair",
        "name": "AC Repair Visit",
        "price": 349,
        "duration": "55 min",
        "badge": "Diagnosis",
        "description": "Technician visit for no cooling, water leakage, noise, or PCB checks.",
    },
    {
        "slug": "ac-gas-refill",
        "category": "AC Repair",
        "name": "Gas Refill and Leak Check",
        "price": 2199,
        "duration": "90 min",
        "badge": "Cooling fix",
        "description": "Pressure test, leak inspection, and gas refill estimate for split/window AC.",
    },
    {
        "slug": "ac-installation",
        "category": "Install",
        "name": "AC Installation",
        "price": 1499,
        "duration": "120 min",
        "badge": "Split AC",
        "description": "Indoor and outdoor mounting, copper pipe fitting, drain and performance test.",
    },
    {
        "slug": "ac-uninstallation",
        "category": "Install",
        "name": "AC Uninstallation",
        "price": 799,
        "duration": "75 min",
        "badge": "Relocation",
        "description": "Safe gas lock, unit removal, packing guidance, and basic wall cleanup.",
    },
    {
        "slug": "refrigerator-repair",
        "category": "Appliances",
        "name": "Refrigerator Repair",
        "price": 399,
        "duration": "65 min",
        "badge": "Appliance",
        "description": "Cooling, compressor, thermostat, and drainage issue diagnosis.",
    },
    {
        "slug": "washing-machine-repair",
        "category": "Appliances",
        "name": "Washing Machine Repair",
        "price": 449,
        "duration": "70 min",
        "badge": "Appliance",
        "description": "Top load, front load, drainage, vibration, and motor fault inspection.",
    },
    {
        "slug": "ro-service",
        "category": "Home Care",
        "name": "RO Service",
        "price": 399,
        "duration": "55 min",
        "badge": "Water",
        "description": "Filter check, TDS check, leakage inspection, and purifier cleaning.",
    },
    {
        "slug": "electrician-visit",
        "category": "Home Care",
        "name": "Electrician Visit",
        "price": 299,
        "duration": "45 min",
        "badge": "Home",
        "description": "Switchboard, fan, MCB, inverter point, and wiring issue diagnosis.",
    },
]


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                duration TEXT NOT NULL,
                badge TEXT NOT NULL,
                description TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                city TEXT NOT NULL,
                address TEXT NOT NULL,
                service_slug TEXT NOT NULL,
                preferred_slot TEXT NOT NULL,
                ac_type TEXT NOT NULL,
                tonnage REAL NOT NULL,
                unit_age INTEGER NOT NULL,
                urgency TEXT NOT NULL,
                estimate_price INTEGER NOT NULL,
                estimate_minutes INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                created_at TEXT NOT NULL
            )
            """
        )
        for service in SERVICES:
            db.execute(
                """
                INSERT INTO services (slug, category, name, price, duration, badge, description)
                VALUES (:slug, :category, :name, :price, :duration, :badge, :description)
                ON CONFLICT(slug) DO UPDATE SET
                    category=excluded.category,
                    name=excluded.name,
                    price=excluded.price,
                    duration=excluded.duration,
                    badge=excluded.badge,
                    description=excluded.description
                """,
                service,
            )
        db.commit()


def services_from_db():
    with get_db() as db:
        return db.execute("SELECT * FROM services ORDER BY id").fetchall()


@app.route("/")
def index():
    init_db()
    services = services_from_db()
    categories = []
    for service in services:
        if service["category"] not in categories:
            categories.append(service["category"])
    featured = [service for service in services if service["slug"].startswith("ac-")]
    with get_db() as db:
        booking_count = db.execute("SELECT COUNT(*) AS total FROM bookings").fetchone()["total"]
    return render_template(
        "index.html",
        services=services,
        featured=featured,
        categories=categories,
        booking_count=booking_count,
    )


@app.route("/book", methods=["POST"])
def book():
    init_db()
    form = request.form
    estimate = estimator.predict(form.to_dict())
    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO bookings (
                customer_name, phone, city, address, service_slug, preferred_slot,
                ac_type, tonnage, unit_age, urgency, estimate_price, estimate_minutes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form.get("customer_name", "").strip(),
                form.get("phone", "").strip(),
                form.get("city", "").strip(),
                form.get("address", "").strip(),
                form.get("service", "ac-general-service"),
                form.get("preferred_slot", "Today"),
                form.get("ac_type", "split"),
                float(form.get("tonnage", 1.5)),
                int(float(form.get("unit_age", 3))),
                form.get("urgency", "standard"),
                estimate.price,
                estimate.minutes,
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )
        db.commit()
        booking_id = cursor.lastrowid
    return redirect(url_for("booking_success", booking_id=booking_id))


@app.route("/booking/<int:booking_id>")
def booking_success(booking_id: int):
    init_db()
    with get_db() as db:
        booking = db.execute(
            """
            SELECT bookings.*, services.name AS service_name
            FROM bookings
            JOIN services ON services.slug = bookings.service_slug
            WHERE bookings.id = ?
            """,
            (booking_id,),
        ).fetchone()
    if booking is None:
        return redirect(url_for("index"))
    return render_template("success.html", booking=booking)


@app.route("/admin/bookings")
def admin_bookings():
    init_db()
    with get_db() as db:
        bookings = db.execute(
            """
            SELECT bookings.*, services.name AS service_name
            FROM bookings
            JOIN services ON services.slug = bookings.service_slug
            ORDER BY bookings.id DESC
            """
        ).fetchall()
    return render_template("admin.html", bookings=bookings)


@app.route("/api/estimate", methods=["POST"])
def api_estimate():
    estimate = estimator.predict(request.get_json(silent=True) or {})
    return jsonify(
        {
            "price": estimate.price,
            "minutes": estimate.minutes,
            "confidence": estimate.confidence,
            "note": estimate.note,
        }
    )


@app.route("/api/services")
def api_services():
    init_db()
    return jsonify([dict(service) for service in services_from_db()])


if __name__ == "__main__":
    init_db()
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
