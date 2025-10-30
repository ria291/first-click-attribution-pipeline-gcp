
# First-Click Attribution Streaming Pipeline (Midpoint)

This repo contains a working **Google Cloud streaming pipeline** for the midpoint demo:
**Pub/Sub → Dataflow (Apache Beam) → BigQuery**.

- **Current scope (Day 3):** Ingests `click` events from Pub/Sub and streams them into BigQuery (`streaming_demo.clicks_stream`).
- **Next (Day 4+):** Add `checkouts` ingestion and implement the **first-click attribution** join.

## Architecture (Midpoint)
```
[Publisher / gcloud publish] --> Pub/Sub (clicks) --> Dataflow (Beam) --> BigQuery (streaming_demo.clicks_stream)
                                   ^                                         |
                                   |_________________ test queries __________|
```

## Prerequisites
- GCP project with billing enabled (e.g., `streaming-project-476403`)
- Python 3.10+
- `gcloud` CLI authenticated to the right project
- APIs enabled: Pub/Sub, Dataflow, BigQuery, Storage

## Quickstart

### 1) Set environment variables
```bash
export PROJECT_ID="streaming-project-476403"
export REGION="us-central1"
export BUCKET="streaming-demo-$PROJECT_ID"
export STAGING="gs://$BUCKET/staging"
export TEMP="gs://$BUCKET/temp"
# BigQuery dataset created in us-central1 (or US): streaming_demo
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Create Pub/Sub topic and test publisher
```bash
gcloud pubsub topics create clicks
python3 scripts/publisher.py   # publishes ~1 msg/sec to 'clicks'
```

### 4) Create BigQuery dataset (once)
```bash
bq --location=${REGION} mk --dataset "${PROJECT_ID}:streaming_demo"
```

### 5) Grant Dataflow worker BigQuery permissions (once)
```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA" --role="roles/pubsub.subscriber"
gcloud projects add-iam-policy-binding $PROJECT_ID   --member="serviceAccount:$SA" --role="roles/storage.objectAdmin"
```

### 6) Run Dataflow (Pub/Sub → BigQuery)
```bash
python3 src/pipeline_clicks_to_bq.py
```

### 7) Query BigQuery
```bash
bq query --location=${REGION} --use_legacy_sql=false "SELECT event_type, COUNT(*) AS events
 FROM \`${PROJECT_ID}.streaming_demo.clicks_stream\`
 GROUP BY event_type
 ORDER BY events DESC"
```

## Repo Layout
```
first-click-attribution/
├─ src/
│  └─ pipeline_clicks_to_bq.py      # Beam pipeline: Pub/Sub -> BigQuery
├─ scripts/
│  ├─ publisher.py                  # Publishes clicks to Pub/Sub
│  └─ publish_test_messages.sh      # Quick burst of messages
├─ infra/
│  ├─ setup_gcp.sh                  # Enables APIs, creates bucket paths (optional)
│  └─ iam_grants.sh                 # Grants worker roles
├─ config/
│  ├─ env.example                   # Template for env vars
│  └─ schemas/                      # (placeholder) JSON schemas
├─ docs/
│  ├─ architecture.png              # (add your diagram here)
│  ├─ midpoint-report.pdf           # (add your report here)
│  ├─ demo-script.md                # Talking points for 5–10 min demo
│  ├─ demo-video-link.txt           # Paste your video URL
│  └─ screenshots/                  # Console proofs
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## Notes
- Keep all resources in the same region (e.g., `us-central1`).
- Cancel old Dataflow jobs to avoid name collisions or extra costs.
- For the final phase, add the `checkouts` stream and attribution pipeline.
