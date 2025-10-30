
import os
import json
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition

# ---- Config from env ----
PROJECT = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
TOPIC = f"projects/{PROJECT}/topics/clicks"
BQ_DATASET = os.getenv("BQ_DATASET", "streaming_demo")
BQ_TABLE = os.getenv("BQ_TABLE", "clicks_stream")
STAGING = os.getenv("STAGING")  # gs://.../staging
TEMP = os.getenv("TEMP")        # gs://.../temp

if not PROJECT or not STAGING or not TEMP:
    raise SystemExit("Set env vars: PROJECT_ID, STAGING (gs://..), TEMP (gs://..). Optional: REGION, BQ_DATASET, BQ_TABLE.")

SCHEMA = {
    "fields": [
        {"name": "event_type", "type": "STRING"},
        {"name": "user_id", "type": "INTEGER"},
        {"name": "product_id", "type": "INTEGER"},
        {"name": "campaign", "type": "STRING"},
        {"name": "source", "type": "STRING"},
        {"name": "event_time", "type": "TIMESTAMP"},
        {"name": "server_ingest_time", "type": "TIMESTAMP"}
    ]
}

class ParseAndAugment(beam.DoFn):
    def process(self, element: bytes):
        try:
            obj = json.loads(element.decode("utf-8"))
            # normalize
            obj.setdefault("event_type", "click")
            obj.setdefault("user_id", None)
            obj.setdefault("product_id", None)
            obj.setdefault("campaign", None)
            obj.setdefault("source", None)
            # ensure times
            et = obj.get("event_time")
            if not et:
                obj["event_time"] = datetime.utcnow().isoformat() + "Z"
            obj["server_ingest_time"] = datetime.utcnow().isoformat() + "Z"
            yield obj
        except Exception:
            # In prod: send to DLQ Pub/Sub
            return

def run():
    job_name = f"clicks-to-bq"

    pipe_opts = {
        "project": PROJECT,
        "region": REGION,
        "runner": "DataflowRunner",
        "streaming": True,
        "staging_location": STAGING,
        "temp_location": TEMP,
        "job_name": job_name
    }
    options = PipelineOptions(flags=[], **pipe_opts)
    options.view_as(SetupOptions).save_main_session = True
    options.view_as(StandardOptions).streaming = True

    table_spec = f"{PROJECT}:{BQ_DATASET}.{BQ_TABLE}"

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(topic=TOPIC)
            | "ParseAugment" >> beam.ParDo(ParseAndAugment())
            | "WriteBQ" >> WriteToBigQuery(
                table=table_spec,
                schema=SCHEMA,
                write_disposition=BigQueryDisposition.WRITE_APPEND,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )

if __name__ == "__main__":
    run()
