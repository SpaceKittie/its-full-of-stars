# ===============================================================================
# Space Cadet Launch Pad Infrastructure
# ===============================================================================

# --- Provider Configuration ---
terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "0.77.0"
    }
  }
}

provider "snowflake" {
  role     = var.SNOWFLAKE_ADMIN_ROLE 
  user     = var.SNOWFLAKE_USER      
  password = var.SNOWFLAKE_PASSWORD   
  account  = var.SNOWFLAKE_ACCOUNT   
}

# --- Role ---
resource "snowflake_role" "main_role" {
  name    = "SPACE_CADET"
  comment = "Main role for the Space Cadet Launch Pad. Owns all project objects."
}

resource "snowflake_role_grants" "main_role_grant" {
  role_name = snowflake_role.main_role.name
  users     = [var.SNOWFLAKE_USER]
}

# --- Warehouse ---
resource "snowflake_warehouse" "main_wh" {
  name                = "SPACE_CADET_WH"
  comment             = "Main warehouse for the Space Cadet Launch Pad."
  warehouse_size      = "X-SMALL"
  auto_suspend        = 5
  auto_resume         = true
  initially_suspended = true
}

# --- Database ---
resource "snowflake_database" "main_db" {
  name    = "SPACE_CADET_DB"
  comment = "Database for the Space Cadet Launch Pad."
}

# --- Schemas ---
resource "snowflake_schema" "raw_schema" {
  database = snowflake_database.main_db.name
  name     = "CARGO_BAY"
}

resource "snowflake_schema" "staging_schema" {
  database = snowflake_database.main_db.name
  name     = "AIRLOCK"
}

resource "snowflake_schema" "marts_schema" {
  database = snowflake_database.main_db.name
  name     = "MISSION_CONTROL"
}

# --- Grants ---
resource "snowflake_grant_privileges_to_role" "db_privs" {
  privileges = ["ALL PRIVILEGES"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.main_db.name
  }
  role_name = snowflake_role.main_role.name
}

resource "snowflake_grant_privileges_to_role" "wh_privs" {
  privileges = ["ALL PRIVILEGES"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.main_wh.name
  }
  role_name = snowflake_role.main_role.name
}

resource "snowflake_grant_privileges_to_role" "raw_schema_privs" {
  privileges = ["ALL PRIVILEGES"]
  on_schema {
    schema_name = "\"${snowflake_database.main_db.name}\".\"${snowflake_schema.raw_schema.name}\""
  }
  role_name = snowflake_role.main_role.name
}

resource "snowflake_grant_privileges_to_role" "staging_schema_privs" {
  privileges = ["ALL PRIVILEGES"]
  on_schema {
    schema_name = "\"${snowflake_database.main_db.name}\".\"${snowflake_schema.staging_schema.name}\""
  }
  role_name = snowflake_role.main_role.name
}

resource "snowflake_grant_privileges_to_role" "marts_schema_privs" {
  privileges = ["ALL PRIVILEGES"]
  on_schema {
    schema_name = "\"${snowflake_database.main_db.name}\".\"${snowflake_schema.marts_schema.name}\""
  }
  role_name = snowflake_role.main_role.name
}