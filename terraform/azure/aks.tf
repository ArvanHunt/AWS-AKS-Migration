resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Project     = "schneider-migration"
    Environment = "demo"
  }
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.cluster_name
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.node_vm_size

    labels = {
      Project     = "schneider-migration"
      Environment = "demo"
    }
  }

  additional_node_pools {
    name       = "druidpool"
    node_count = var.druid_node_count
    vm_size    = var.node_vm_size

    labels = {
      workload = "druid"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Project     = "schneider-migration"
    Environment = "demo"
  }
}