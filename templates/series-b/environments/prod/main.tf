provider "aws" {
  region = "{{REGION}}"
}

variable "tags" {
  type = map(string)

  validation {
    condition = alltrue([
      contains(keys(var.tags), "owner"),
      contains(keys(var.tags), "purpose"),
      contains(keys(var.tags), "risk"),
      contains(keys(var.tags), "cost_center")
    ])
    error_message = "Missing required tags: owner, purpose, risk, cost_center"
  }
}

locals {
  phase = "{{PHASE}}"
  env   = "prod"
  name_prefix = "stp-${local.env}"
}

module "network" {
  source = "../../modules/network"
  cidr   = "10.0.0.0/16"
}

module "app" {
  source        = "../../modules/compute"
  instance_type = "t3.medium"
}

module "data" {
  source = "../../modules/data"
  name   = "${local.name_prefix}-demo"
}