output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.main.name
}

output "cluster_endpoint" {
  description = "AKS cluster endpoint"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.host
  sensitive   = true
}

output "kube_config" {
  description = "Kubeconfig for AKS"
  value       = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive   = true
}

output "location" {
  description = "Azure region"
  value       = var.location
}