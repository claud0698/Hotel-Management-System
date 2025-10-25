#!/bin/bash
# Setup GCP Permissions for Cloud Run Deployment

set -e

echo "🔐 Setting up GCP Permissions for Cloud Run"
echo "=========================================="

# Get current project
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Please run:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📋 Project: $PROJECT_ID"
echo "📋 Project Number: $PROJECT_NUMBER"
echo ""

# Get current user email
USER_EMAIL=$(gcloud config get-value account)
echo "👤 User: $USER_EMAIL"
echo ""

echo "🔧 Granting deployment permissions to your account..."
echo "   This allows you to deploy Cloud Run services"
echo ""

# Grant roles to user for deployment
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$USER_EMAIL" \
    --role="roles/run.admin" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$USER_EMAIL" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$USER_EMAIL" \
    --role="roles/cloudbuild.builds.editor" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$USER_EMAIL" \
    --role="roles/storage.admin" \
    --condition=None

echo "✅ Deployment permissions granted!"
echo ""

# Setup Cloud Run default service account
echo "🔧 Setting up Cloud Run runtime service account..."
echo "   This is what your app runs as"
echo ""

CLOUD_RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
echo "📋 Cloud Run Service Account: $CLOUD_RUN_SA"

# Grant storage permissions (for SQLite on Cloud Storage)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_RUN_SA" \
    --role="roles/storage.objectAdmin" \
    --condition=None

echo "✅ Runtime permissions granted!"
echo ""

echo "=========================================="
echo "✅ All permissions configured!"
echo ""
echo "📋 Summary:"
echo "   Your account ($USER_EMAIL) can:"
echo "   ✅ Deploy Cloud Run services"
echo "   ✅ Use service accounts"
echo "   ✅ Create builds"
echo "   ✅ Manage storage"
echo ""
echo "   Cloud Run service account can:"
echo "   ✅ Read/Write to Cloud Storage (for database)"
echo ""
echo "🚀 Next steps:"
echo "   1. Deploy to Cloud Run:"
echo "      cd backend && gcloud run deploy kos-api --source ."
echo ""
