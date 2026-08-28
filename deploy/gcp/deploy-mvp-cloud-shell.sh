#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-pip-mvp}"
SQL_INSTANCE="${SQL_INSTANCE:-pip-mvp-postgres}"
DATABASE_NAME="${DATABASE_NAME:-pip_db}"
DATABASE_USER="${DATABASE_USER:-pip_user}"
RUNTIME_SERVICE_ACCOUNT="${RUNTIME_SERVICE_ACCOUNT:-pip-mvp-runtime}"
DATABASE_PASSWORD_SECRET="${DATABASE_PASSWORD_SECRET:-pip-mvp-db-password}"

if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "YOUR_GOOGLE_PROJECT_ID" ]]; then
  echo "Usage: ./deploy/gcp/deploy-mvp-cloud-shell.sh PROJECT_ID [REGION]" >&2
  exit 2
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud is required. Run this script in Google Cloud Shell." >&2
  exit 1
fi

echo "Configuring Google Cloud project: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  --project "$PROJECT_ID"

if ! gcloud sql instances describe "$SQL_INSTANCE" \
  --project "$PROJECT_ID" >/dev/null 2>&1; then
  echo "Creating Cloud SQL PostgreSQL instance..."
  gcloud sql instances create "$SQL_INSTANCE" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --database-version POSTGRES_16 \
    --edition ENTERPRISE \
    --tier db-f1-micro \
    --availability-type zonal \
    --storage-type SSD \
    --storage-size 10 \
    --storage-auto-increase \
    --backup-start-time 03:00 \
    --retained-backups-count 7
else
  echo "Cloud SQL instance already exists."
fi

if ! gcloud sql databases describe "$DATABASE_NAME" \
  --instance "$SQL_INSTANCE" \
  --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud sql databases create "$DATABASE_NAME" \
    --instance "$SQL_INSTANCE" \
    --project "$PROJECT_ID"
fi

read -r -s -p "Enter a password for Cloud SQL user '$DATABASE_USER': " DB_PASSWORD
echo

if [[ -z "$DB_PASSWORD" ]]; then
  echo "The database password cannot be empty." >&2
  exit 2
fi

if gcloud sql users list \
  --instance "$SQL_INSTANCE" \
  --project "$PROJECT_ID" \
  --filter="name=$DATABASE_USER" \
  --format="value(name)" | grep -Fxq "$DATABASE_USER"; then
  gcloud sql users set-password "$DATABASE_USER" \
    --instance "$SQL_INSTANCE" \
    --project "$PROJECT_ID" \
    --password "$DB_PASSWORD"
else
  gcloud sql users create "$DATABASE_USER" \
    --instance "$SQL_INSTANCE" \
    --project "$PROJECT_ID" \
    --password "$DB_PASSWORD"
fi

if ! gcloud secrets describe "$DATABASE_PASSWORD_SECRET" \
  --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud secrets create "$DATABASE_PASSWORD_SECRET" \
    --project "$PROJECT_ID" \
    --replication-policy automatic
fi

printf '%s' "$DB_PASSWORD" | gcloud secrets versions add \
  "$DATABASE_PASSWORD_SECRET" \
  --project "$PROJECT_ID" \
  --data-file=-
unset DB_PASSWORD

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" \
  --format='value(projectNumber)')"
BUILD_SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
RUNTIME_EMAIL="${RUNTIME_SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$BUILD_SERVICE_ACCOUNT" \
  --role="roles/run.builder" \
  --condition=None >/dev/null

if ! gcloud iam service-accounts describe "$RUNTIME_EMAIL" \
  --project "$PROJECT_ID" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$RUNTIME_SERVICE_ACCOUNT" \
    --project "$PROJECT_ID" \
    --display-name="PIP MVP Cloud Run runtime"
fi

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$RUNTIME_EMAIL" \
  --role="roles/cloudsql.client" \
  --condition=None >/dev/null

gcloud secrets add-iam-policy-binding "$DATABASE_PASSWORD_SECRET" \
  --project "$PROJECT_ID" \
  --member="serviceAccount:$RUNTIME_EMAIL" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None >/dev/null

CONNECTION_NAME="$(gcloud sql instances describe "$SQL_INSTANCE" \
  --project "$PROJECT_ID" \
  --format='value(connectionName)')"

ENV_VARS="CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,DB_USER=$DATABASE_USER,DB_NAME=$DATABASE_NAME,AI_ENABLED=false,SQL_ECHO=false"

echo "Building and deploying the single-container MVP..."
gcloud run deploy "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --source . \
  --service-account "$RUNTIME_EMAIL" \
  --set-cloudsql-instances "$CONNECTION_NAME" \
  --set-env-vars "$ENV_VARS" \
  --set-secrets="DB_PASS=${DATABASE_PASSWORD_SECRET}:latest" \
  --port 8080 \
  --cpu 1 \
  --memory 1Gi \
  --concurrency 40 \
  --min-instances 0 \
  --max-instances 2 \
  --allow-unauthenticated \
  --quiet

SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --format='value(status.url)')"

echo
echo "PIP MVP deployed successfully."
echo "Application: $SERVICE_URL"
echo "Health check: $SERVICE_URL/api/health"
echo
echo "Next: export the local PostgreSQL data, upload it to Cloud Shell, and run import-data-cloud-shell.sh."
