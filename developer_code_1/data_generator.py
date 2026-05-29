import psycopg2
import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

# Database connection
conn = psycopg2.connect(
    host="postgres",
    database="sh_db",
    user="sh",
    password="sh123"
)
cur = conn.cursor()

# Create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    type VARCHAR(50),
    status VARCHAR(20),
    install_date DATE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS assets (
    asset_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(20),
    plant_name VARCHAR(100),
    floor VARCHAR(20),
    criticality VARCHAR(20)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS maintenance (
    ticket_id VARCHAR(20) PRIMARY KEY,
    device_id VARCHAR(20),
    issue VARCHAR(200),
    status VARCHAR(20),
    scheduled_date DATE
)
""")
conn.commit()

# Insert dummy devices
devices = [
    ("SE-001", "Circuit Breaker A1", "Mumbai Plant", "breaker", "active", "2020-01-15"),
    ("SE-002", "Power Meter B2", "Mumbai Plant", "meter", "active", "2020-03-20"),
    ("SE-003", "UPS Unit C3", "Pune Plant", "ups", "active", "2019-06-10"),
    ("SE-004", "Transformer D4", "Pune Plant", "transformer", "maintenance", "2018-11-05"),
    ("SE-005", "Solar Inverter E5", "Delhi Plant", "inverter", "active", "2021-08-22"),
]

for d in devices:
    cur.execute("""
        INSERT INTO devices VALUES (%s,%s,%s,%s,%s,%s)
        ON CONFLICT (device_id) DO NOTHING
    """, d)

assets = [
    ("AST-001", "SE-001", "Mumbai Plant", "Floor 1", "critical"),
    ("AST-002", "SE-002", "Mumbai Plant", "Floor 2", "high"),
    ("AST-003", "SE-003", "Pune Plant", "Floor 1", "critical"),
    ("AST-004", "SE-004", "Pune Plant", "Floor 3", "medium"),
    ("AST-005", "SE-005", "Delhi Plant", "Rooftop", "high"),
]

for a in assets:
    cur.execute("""
        INSERT INTO assets VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (asset_id) DO NOTHING
    """, a)

maintenance = [
    ("TKT-001", "SE-004", "Overheating detected", "open", "2026-06-01"),
    ("TKT-002", "SE-001", "Routine inspection", "scheduled", "2026-06-15"),
    ("TKT-003", "SE-003", "Battery replacement", "in-progress", "2026-05-28"),
]

for m in maintenance:
    cur.execute("""
        INSERT INTO maintenance VALUES (%s,%s,%s,%s,%s)
        ON CONFLICT (ticket_id) DO NOTHING
    """, m)

conn.commit()
print("Database seeded with SH dummy data")

# Kafka Producer
producer = Producer({
    'bootstrap.servers': 'kafka:9092'
})

def send_message(topic, value):
    producer.produce(topic, value=json.dumps(value).encode('utf-8'))
    producer.poll(0)

print("Starting data stream...")

counter = 0
while True:
    for device_id in ["SE-001", "SE-002", "SE-003", "SE-004", "SE-005"]:
        # Telemetry
        telemetry = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "voltage": round(random.uniform(210, 240), 2),
            "current": round(random.uniform(10, 50), 2),
            "temperature": round(random.uniform(25, 85), 2),
            "power_kw": round(random.uniform(5, 100), 2),
            "frequency": round(random.uniform(49.5, 50.5), 2)
        }
        send_message('telemetry', telemetry)

        # Events
        if random.random() < 0.1:
            event = {
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": random.choice(["threshold_breach", "device_restart", "connection_lost", "maintenance_alert"]),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "message": f"Event detected on {device_id}"
            }
            send_message('events', event)

        # Logs
        log = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "level": random.choice(["INFO", "WARN", "ERROR"]),
            "message": f"Device {device_id} status check",
            "source": "device-agent"
        }
        send_message('logs', log)

    producer.flush()
    counter += 1
    print(f"Batch {counter} sent — {datetime.utcnow().isoformat()}")
    time.sleep(2)