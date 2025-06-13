set -e

echo "--- 🚀 Starting environment setup ---"

echo "--- Initializing Terraform ---"
cd infra
terraform init
cd ..

echo "--- Installing dbt dependencies ---"
dbt deps --project-dir ./astro/dbt --profiles-dir ./astro/dbt

echo "--- ✅ Environment setup complete! ---"