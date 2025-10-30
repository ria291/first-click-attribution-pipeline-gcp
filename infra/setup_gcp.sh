
#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
BUCKET="${BUCKET:-streaming-demo-$PROJECT_ID}"

echo "Enabling APIs..."
gcloud services enable pubsub.googleapis.com dataflow.googleapis.com bigquery.googleapis.com storage.googleapis.com --project="$PROJECT_ID"

echo "Creating Pub/Sub topics..."
gcloud pubsub topics create clicks --project="$PROJECT_ID" || true

echo "Creating GCS bucket (if not exists)..."
gcloud storage buckets create "gs://$BUCKET" --project="$PROJECT_ID" --location="$REGION" || true

echo "Creating paths..."
echo "init" | gsutil cp - "gs://$BUCKET/staging/.init" || true
echo "init" | gsutil cp - "gs://$BUCKET/temp/.init" || true

echo "Done."
