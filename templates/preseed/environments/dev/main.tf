provider "aws" {
  region = "{{REGION}}"
}

locals {
  phase = "{{PHASE}}"
}

module "network" {
  source = "../../modules/network"
  cidr   = "10.0.0.0/16"
}

module "app" {
  source        = "../../modules/compute"
  instance_type = "t3.micro"
}

module "data" {
  source = "../../modules/data"
  name   = "demo"
}