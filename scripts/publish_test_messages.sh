
#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?Set PROJECT_ID env var}"

for i in {1..25}; do
  gcloud pubsub topics publish clicks     --message='{"event_type":"click","user_id":1,"product_id":100}'
done
echo "Published 25 test messages to 'clicks'."
