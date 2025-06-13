-include .env
export

# --- Help ---
.PHONY: help
help:
	@echo "Commands:"
	@echo "  setup         - Generates terraform.tfvars from your .env file. Run this once."
	@echo "  all           - Run the full setup sequence: setup, infra-apply, dbt-init, up."
	@echo "  up            - Start the local Airflow environment (alias for astro-start)."
	@echo "  down          - Stop the local Airflow environment (alias for astro-stop)."
	@echo "  infra-plan    - Plan the infrastructure changes with Terraform."
	@echo "  infra-apply   - Apply the infrastructure changes with Terraform."
	@echo "  infra-destroy - Destroy the infrastructure with Terraform."
	@echo "  dbt-init      - Create raw tables for data ingestion."
	@echo "  dbt-run       - Run dbt to create tables."
	@echo "  dashboard     - Start the Streamlit dashboard."
	@echo "  astro-start   - Start the local Airflow environment."
	@echo "  astro-stop    - Stop the local Airflow environment."
	@echo "  astro-logs    - View the logs from the local Airflow environment."
	@echo "  clean         - Remove generated files."

# --- Infrastructure Management (Terraform) ---
.PHONY: infra-plan
infra-plan:
	@echo "--- Planning infrastructure changes ---"
	cd infra && terraform plan

.PHONY: infra-apply
infra-apply:
	@echo "--- Applying infrastructure changes ---"
	cd infra && terraform apply -auto-approve

.PHONY: infra-destroy
infra-destroy:
	@echo "--- Destroying infrastructure ---"
	cd infra && terraform destroy -auto-approve

# --- Project Setup ---
.PHONY: setup
setup: .env
	@echo "--- Generating terraform.tfvars from .env file ---"
	@echo "SNOWFLAKE_ACCOUNT  = \"$(SNOWFLAKE_ACCOUNT)\"" > infra/terraform.tfvars
	@echo "SNOWFLAKE_USER     = \"$(SNOWFLAKE_USER)\"" >> infra/terraform.tfvars
	@echo "SNOWFLAKE_PASSWORD = \"$(SNOWFLAKE_PASSWORD)\"" >> infra/terraform.tfvars
	@echo "✅ terraform.tfvars created successfully."
	@echo "--- Generating Streamlit secrets.toml ---"
	@mkdir -p .streamlit
	@echo "[snowflake]" > .streamlit/secrets.toml
	@echo "user = \"$(SNOWFLAKE_USER)\"" >> .streamlit/secrets.toml
	@echo "password = \"$(SNOWFLAKE_PASSWORD)\"" >> .streamlit/secrets.toml
	@echo "account = \"$(SNOWFLAKE_ACCOUNT)\"" >> .streamlit/secrets.toml
	@echo "warehouse = \"SPACE_CADET_WH\"" >> .streamlit/secrets.toml
	@echo "database = \"SPACE_CADET_DB\"" >> .streamlit/secrets.toml
	@echo "schema = \"MISSION_CONTROL\"" >> .streamlit/secrets.toml
	@echo "role = \"SPACE_CADET\"" >> .streamlit/secrets.toml
	@echo "✅ Streamlit secrets created successfully."

# --- Streamlit Dashboard ---
.PHONY: dashboard
dashboard:
	@echo "--- Starting Streamlit dashboard ---"
	streamlit run streamlit_app.py

# --- Local Airflow Development (Astro CLI) ---
.PHONY: up
up: astro-start

.PHONY: down
down: astro-stop

.PHONY: astro-start
astro-start:
	@echo "--- Starting local Airflow environment ---"
	cd astro && astro dev start

.PHONY: astro-stop
astro-stop:
	@echo "--- Stopping local Airflow environment ---"
	cd astro && astro dev stop

.PHONY: astro-logs
astro-logs:
	@echo "--- Viewing local Airflow logs ---"
	cd astro && astro dev logs --follow

# --- Full Sequence ---
.PHONY: all
all: setup infra-apply dbt-init up
	@echo "--- All steps completed successfully! ---"
	@echo "--- Next steps: ---"
	@echo "  1. Open the Airflow UI (Ports tab, port 8080)."
	@echo "  2. Enable and trigger the DAGs."
	@echo "  3. Run 'make dashboard' to view the results."

.PHONY: dbt-init
dbt-init:
	@echo "--- Creating raw tables with dbt macro ---"
	dbt run-operation create_raw_tables --project-dir ./astro/dbt --profiles-dir ./astro/dbt

# --- Cleanup ---
.PHONY: clean
clean:
	@echo "--- Cleaning up generated files ---"
	-cd astro && astro dev stop > /dev/null 2>&1
	rm -rf dbt/target dbt/dbt_packages astro
	cd infra && rm -rf .terraform* terraform.tfstate*