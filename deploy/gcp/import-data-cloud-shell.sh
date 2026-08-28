#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${1:-}"
DUMP_PATH="${2:-}"
REGION="${3:-us-central1}"
SQL_INSTANCE="${SQL_INSTANCE:-pip-mvp-postgres}"
DATABASE_NAME="${DATABASE_NAME:-pip_db}"
DATABASE_USER="${DATABASE_USER:-pip_user}"
BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-pip-mvp-import}"

if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "YOUR_GOOGLE_PROJECT_ID" || -z "$DUMP_PATH" ]]; then
  echo "Usage: ./deploy/gcp/import-data-cloud-shell.sh PROJECT_ID DUMP_PATH [REGION]" >&2
  exit 2
fi

if [[ ! -s "$DUMP_PATH" ]]; then
  echo "Database dump does not exist or is empty: $DUMP_PATH" >&2
  exit 1
fi

gcloud config set project "$PROJECT_ID"

BUCKET_URI="gs://${BUCKET_NAME}"
if ! gcloud storage buckets describe "$BUCKET_URI" \
  --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud storage buckets create "$BUCKET_URI" \
    --project "$PROJECT_ID" \
    --location "$REGION" \
    --uniform-bucket-level-access
fi

INSTANCE_SERVICE_ACCOUNT="$(gcloud sql instances describe "$SQL_INSTANCE" \
  --project "$PROJECT_ID" \
  --format='value(serviceAccountEmailAddress)')"

gcloud storage buckets add-iam-policy-binding "$BUCKET_URI" \
  --member="serviceAccount:$INSTANCE_SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin" \
  --condition=None >/dev/null

OBJECT_NAME="pip-mvp-data-$(date -u +%Y%m%d-%H%M%S).sql"
OBJECT_URI="${BUCKET_URI}/${OBJECT_NAME}"
UPLOADED=false

cleanup() {
  if [[ "$UPLOADED" == true ]]; then
    gcloud storage rm "$OBJECT_URI" --project "$PROJECT_ID" || \
      echo "WARNING: Remove the sensitive temporary object manually: $OBJECT_URI" >&2
  fi
}
trap cleanup EXIT

echo "Uploading the database dump..."
gcloud storage cp "$DUMP_PATH" "$OBJECT_URI" --project "$PROJECT_ID"
UPLOADED=true

echo "Importing data into Cloud SQL..."
gcloud sql import sql "$SQL_INSTANCE" "$OBJECT_URI" \
  --project "$PROJECT_ID" \
  --database "$DATABASE_NAME" \
  --user "$DATABASE_USER" \
  --quiet

echo
echo "Database migration completed successfully."
