
#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID}"

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

roles=(
  roles/dataflow.worker
  roles/storage.objectAdmin
  roles/pubsub.subscriber
  roles/bigquery.dataEditor
)

for r in "${roles[@]}"; do
  echo "Granting $r to $SA"
  gcloud projects add-iam-policy-binding "$PROJECT_ID"     --member="serviceAccount:$SA" --role="$r" >/dev/null
done

echo "Done."
