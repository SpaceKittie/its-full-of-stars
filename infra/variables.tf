###################################################################################################
# Input Variables
###################################################################################################

variable "SNOWFLAKE_ACCOUNT" {}

variable "SNOWFLAKE_USER" {}
variable "SNOWFLAKE_PASSWORD" {
  sensitive = true
}

variable "SNOWFLAKE_ADMIN_ROLE" {
  description = "Role that Terraform will use to create the infrastructure and roles."
  default     = "ACCOUNTADMIN"
}