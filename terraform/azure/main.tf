terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.0"

  backend "s3" {
    bucket  = "sh-migration-tfstate-2026"
    key     = "azure/aks/terraform.tfstate"
    region  = "ap-south-1"
    encrypt = true
  }
}

provider "azurerm" {
  features {}
}