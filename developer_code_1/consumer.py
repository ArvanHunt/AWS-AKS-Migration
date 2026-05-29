import json
import time
import requests
from datetime import datetime
from confluent_kafka import Consumer, KafkaError
from pymongo import MongoClient

# MongoDB connection
mongo_client = MongoClient(
    "mongodb://sh:sh123@mongodb.destination.svc.cluster.local:27017/sh_db?authSource=admin"
)
db = mongo_client["sh_db"]

print("Connected to MongoDB")

# Kafka Consumer
consumer = Consumer({
    'bootstrap.servers': 'kafka.source.svc.cluster.local:9092',
    'group.id': 'sh-migration-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
})

consumer.subscribe(['telemetry', 'events', 'logs'])

print("Consumer ready. Waiting for messages...")

# Druid ingestion endpoint
DRUID_ROUTER = "http://druid-router.destination.svc.cluster.local:8888"

def send_to_druid(datasource, data):
    try:
        payload = {
            "type": "index",
            "spec": {
                "type": "index",
                "ioConfig": {
                    "type": "index",
                    "inputSource": {
                        "type": "inline",
                        "data": json.dumps(data)
                    },
                    "inputFormat": {
                        "type": "json"
                    }
                },
                "dataSchema": {
                    "dataSource": datasource,
                    "timestampSpec": {
                        "column": "timestamp",
                        "format": "iso"
                    },
                    "dimensionsSpec": {
                        "dimensions": list(data.keys())
                    }
                },
                "tuningConfig": {
                    "type": "index"
                }
            }
        }
        requests.post(
            f"{DRUID_ROUTER}/druid/indexer/v1/task",
            json=payload,
            timeout=5
        )
    except Exception as e:
        print(f"Druid error: {e}")

telemetry_batch = []
events_batch = []

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            continue
        else:
            print(f"Error: {msg.error()}")
            continue

    topic = msg.topic()
    value = json.loads(msg.value().decode('utf-8'))

    if topic == 'telemetry':
        # Write to MongoDB
        db.telemetry.insert_one(value)
        telemetry_batch.append(value)

        # Send batch to Druid every 10 messages
        if len(telemetry_batch) >= 10:
            send_to_druid('sh-telemetry', telemetry_batch[-1])
            telemetry_batch = []
            print(f"Sent telemetry batch to Druid — {datetime.utcnow().isoformat()}")

    elif topic == 'events':
        db.events.insert_one(value)
        events_batch.append(value)
        if len(events_batch) >= 5:
            send_to_druid('sh-events', events_batch[-1])
            events_batch = []
            print(f"Sent events batch to Druid — {datetime.utcnow().isoformat()}")

    elif topic == 'logs':
        db.logs.insert_one(value)

    print(f"Topic: {topic} | Device: {value.get('device_id')} | Time: {value.get('timestamp')}")