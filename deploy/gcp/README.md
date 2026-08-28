# PIP MVP deployment on Google Cloud

This profile deploys the smallest useful online PIP stack:

- **One public Cloud Run service** for the compiled React/Vite frontend and the
  FastAPI backend.
- **One Cloud SQL for PostgreSQL instance** for persistent application data.
- **Secret Manager** for the database password.
- Existing local PostgreSQL data migrated with a temporary private Cloud
  Storage object.

Redis, RabbitMQ, Qdrant, MinIO, Ollama and external AI generation are outside
this MVP. Deterministic Dashboard, Projects, WBS, Schedule, Cost, Risk, EVM and
file-import features remain available.

## Prerequisites

1. Google Cloud project with billing enabled.
2. Google Cloud CLI installed.
3. Docker Desktop running, including the local `pip-postgres` container.
4. Permission to manage Cloud Run, Cloud SQL, IAM, Secret Manager, Cloud Build
   and Cloud Storage in the selected project.

Authenticate once:

```powershell
gcloud auth login
gcloud auth list
gcloud config set project YOUR_GOOGLE_PROJECT_ID
```

## 1. Deploy the application and Cloud SQL

Run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\gcp\deploy-mvp.ps1 `
  -ProjectId "YOUR_GOOGLE_PROJECT_ID" `
  -Region "us-central1"
```

The script asks for a Cloud SQL password without storing it in the repository,
creates or reuses the required Google resources, builds the multi-stage
Dockerfile, and prints the Cloud Run URL.

Defaults:

| Resource | Default |
|---|---|
| Cloud Run service | `pip-mvp` |
| Cloud SQL instance | `pip-mvp-postgres` |
| Database | `pip_db` |
| Database user | `pip_user` |
| Region | `us-central1` |

## 2. Migrate the existing local PostgreSQL data

The migration replaces the schema and data in the target Cloud SQL database.
Run it only after confirming the target project and database names:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\gcp\migrate-postgres-data.ps1 `
  -ProjectId "YOUR_GOOGLE_PROJECT_ID" `
  -Region "us-central1"
```

Type `MIGRATE` when prompted. The script:

1. Runs `pg_dump` inside the local `pip-postgres` container.
2. Creates a byte-safe local SQL dump.
3. Uploads it temporarily to a Cloud Storage bucket.
4. Grants the Cloud SQL service account access.
5. Imports the dump into Cloud SQL as the application database user.
6. Deletes the temporary cloud copy, including after a failed import.
7. Keeps the local dump as a temporary backup.

The dump can contain sensitive project information and is ignored by Git.
Delete it after verifying the online application.

## 3. Verify

```powershell
$serviceUrl = gcloud run services describe pip-mvp `
  --project "YOUR_GOOGLE_PROJECT_ID" `
  --region "us-central1" `
  --format="value(status.url)"

Invoke-RestMethod ($serviceUrl + "/api/health")
Start-Process $serviceUrl
```

Expected health response:

```json
{
  "system": "PIP AI Platform",
  "status": "running",
  "mode": "mvp"
}
```

Verify Projects, WBS, Schedule and Cost in the browser before deleting the local
SQL dump.

## Update the MVP after a Git change

Run the deployment script again. It reuses Cloud SQL, the database, service
account and secret, then deploys a new Cloud Run revision.

## Logs and rollback

Read recent logs:

```powershell
gcloud run services logs read pip-mvp `
  --project "YOUR_GOOGLE_PROJECT_ID" `
  --region "us-central1" `
  --limit 100
```

List revisions:

```powershell
gcloud run revisions list `
  --service pip-mvp `
  --project "YOUR_GOOGLE_PROJECT_ID" `
  --region "us-central1"
```

## Cost controls

The deployment uses zero minimum Cloud Run instances, at most two instances,
and a small shared-core Cloud SQL tier. Cloud SQL remains billable while the
instance exists even when Cloud Run has scaled to zero. Configure a Google
Cloud budget alert before sharing the MVP publicly.

## Security scope

The MVP Cloud Run service is public and the current application does not yet
enforce user authentication. Use it only for controlled demonstrations and do
not upload confidential production documents until authentication and access
control are implemented.

## Browser-based Cloud Shell fallback

Use this path when Google blocks or filters the CLI download on the local
network. Cloud Shell already includes an authenticated `gcloud` installation.

### Package and upload the source

After applying and committing the patch on Windows:

```powershell
git archive --format=zip --output .\pip-mvp-source.zip HEAD
```

Open <https://shell.cloud.google.com/>, upload `pip-mvp-source.zip`, and run:

```bash
unzip pip-mvp-source.zip -d pip-mvp-source
cd pip-mvp-source
chmod +x deploy/gcp/*.sh

./deploy/gcp/deploy-mvp-cloud-shell.sh \
  "YOUR_GOOGLE_PROJECT_ID" \
  "us-central1"
```

### Export local PostgreSQL on Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass

& .\deploy\gcp\export-postgres-data.ps1 `
  -DumpPath ".\pip-mvp-data.sql"
```

Upload `pip-mvp-data.sql` to Cloud Shell. From the unpacked source directory,
import it with:

```bash
./deploy/gcp/import-data-cloud-shell.sh \
  "YOUR_GOOGLE_PROJECT_ID" \
  "$HOME/pip-mvp-data.sql" \
  "us-central1"
```

Delete the local and Cloud Shell copies after verifying the application because
the SQL dump contains project data:

```bash
rm -f "$HOME/pip-mvp-data.sql"
```

## Google Cloud references

- [Deploy FastAPI to Cloud Run](https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service)
- [Connect Cloud Run to Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres/connect-run)
- [Import SQL into Cloud SQL](https://docs.cloud.google.com/sql/docs/postgres/import-export/import-export-sql)
- [Use Secret Manager with Cloud Run](https://cloud.google.com/run/docs/configuring/services/secrets)
