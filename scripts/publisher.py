
import os, json, time, random
from google.cloud import pubsub_v1

PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC = os.getenv("TOPIC", "clicks")

if not PROJECT_ID:
    raise SystemExit("Set PROJECT_ID env var, e.g., export PROJECT_ID=streaming-project-476403")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC)

print(f"Publishing to Pub/Sub topic: {topic_path}")
i = 0
try:
    while True:
        event = {
            "event_type": "click",
            "user_id": random.randint(1, 5),
            "product_id": random.randint(100, 105),
            "event_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "campaign": random.choice(["spring", "summer", "fall"]),
            "source": random.choice(["ads_x", "ads_y", "email"])
        }
        data = json.dumps(event).encode("utf-8")
        publisher.publish(topic_path, data)
        if i % 10 == 0:
            print("Published:", event)
        i += 1
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped publisher.")
