"""
Virtual Machine Generator
"""
import numpy as np
from typing import List, Dict


def generate_vms(num_vms: int, seed: int = 42) -> List[Dict]:
    """
    Generate VM specifications with heterogeneous resource demands.
    
    Args:
        num_vms: Number of VMs to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of VM specifications
    """
    np.random.seed(seed)
    
    vms = []
    
    for i in range(num_vms):
        # VM types: small (30%), medium (50%), large (20%)
        vm_type = np.random.choice(['small', 'medium', 'large'], p=[0.3, 0.5, 0.2])
        
        if vm_type == 'small':
            # Small VMs: 1-2 CPUs, 1-4 GB RAM
            cpu_demand = np.random.randint(1, 3)
            memory_demand = np.random.randint(1, 5)
        elif vm_type == 'medium':
            # Medium VMs: 2-4 CPUs, 4-8 GB RAM
            cpu_demand = np.random.randint(2, 5)
            memory_demand = np.random.randint(4, 9)
        else:  # large
            # Large VMs: 4-8 CPUs, 8-16 GB RAM
            cpu_demand = np.random.randint(4, 9)
            memory_demand = np.random.randint(8, 17)
        
        vm = {
            'id': i,
            'type': vm_type,
            'cpu_demand': cpu_demand,
            'memory_demand': memory_demand,
            'storage_demand': np.random.randint(10, 100)  # 10-100 GB
        }
        
        vms.append(vm)
    
    return vms


def generate_vms_from_distribution(num_vms: int, 
                                   cpu_mean: float = 4.0, 
                                   cpu_std: float = 2.0,
                                   memory_mean: float = 8.0, 
                                   memory_std: float = 4.0,
                                   seed: int = 42) -> List[Dict]:
    """
    Generate VMs with normal distribution of resource demands.
    
    Args:
        num_vms: Number of VMs to generate
        cpu_mean: Mean CPU demand
        cpu_std: Standard deviation of CPU demand
        memory_mean: Mean memory demand
        memory_std: Standard deviation of memory demand
        seed: Random seed
        
    Returns:
        List of VM specifications
    """
    np.random.seed(seed)
    
    vms = []
    
    for i in range(num_vms):
        cpu_demand = max(1, int(np.random.normal(cpu_mean, cpu_std)))
        memory_demand = max(1, int(np.random.normal(memory_mean, memory_std)))
        
        vm = {
            'id': i,
            'cpu_demand': cpu_demand,
            'memory_demand': memory_demand,
            'storage_demand': np.random.randint(10, 100)
        }
        
        vms.append(vm)
    
    return vms


def generate_vms_with_pressure(num_vms: int, 
                               num_pms: int,
                               target_utilization: float = 0.75,
                               seed: int = 42) -> List[Dict]:
    """
    Generate VMs that create resource pressure at target utilization level.
    
    This ensures the problem is challenging but feasible.
    
    Args:
        num_vms: Number of VMs to generate
        num_pms: Number of PMs available
        target_utilization: Target average PM utilization (0-1)
        seed: Random seed
        
    Returns:
        List of VM specifications
    """
    np.random.seed(seed)
    
    # Assume PM capacity (will be used by PM generator)
    pm_cpu_capacity = 16
    pm_memory_capacity = 32
    
    # Calculate total available resources
    total_cpu = num_pms * pm_cpu_capacity
    total_memory = num_pms * pm_memory_capacity
    
    # Calculate target total demand
    target_cpu_demand = total_cpu * target_utilization
    target_memory_demand = total_memory * target_utilization
    
    vms = []
    current_cpu = 0
    current_memory = 0
    
    for i in range(num_vms):
        # Determine remaining budget
        remaining_vms = num_vms - i
        cpu_budget = (target_cpu_demand - current_cpu) / remaining_vms
        memory_budget = (target_memory_demand - current_memory) / remaining_vms
        
        # Generate demand around budget with some variance
        cpu_demand = max(1, int(np.random.normal(cpu_budget, cpu_budget * 0.3)))
        memory_demand = max(1, int(np.random.normal(memory_budget, memory_budget * 0.3)))
        
        # Ensure demands don't exceed PM capacity
        cpu_demand = min(cpu_demand, pm_cpu_capacity)
        memory_demand = min(memory_demand, pm_memory_capacity)
        
        vm = {
            'id': i,
            'cpu_demand': cpu_demand,
            'memory_demand': memory_demand,
            'storage_demand': np.random.randint(10, 100)
        }
        
        vms.append(vm)
        current_cpu += cpu_demand
        current_memory += memory_demand
    
    return vms
