variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "sh-migration-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "centralindia"
}

variable "cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "sh-aks"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "node_count" {
  description = "Number of nodes in AKS cluster"
  type        = number
  default     = 2
}

variable "node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "druid_node_count" {
  description = "Number of nodes for Druid workload"
  type        = number
  default     = 2
}