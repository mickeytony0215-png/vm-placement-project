"""
Physical Machine Generator
"""
import numpy as np
from typing import List, Dict


def generate_pms(num_pms: int, seed: int = 42) -> List[Dict]:
    """
    Generate PM specifications with heterogeneous resource capacities.
    
    Args:
        num_pms: Number of PMs to generate
        seed: Random seed for reproducibility
        
    Returns:
        List of PM specifications
    """
    np.random.seed(seed)
    
    pms = []
    
    for i in range(num_pms):
        # PM types: small (20%), medium (50%), large (30%)
        pm_type = np.random.choice(['small', 'medium', 'large'], p=[0.2, 0.5, 0.3])
        
        if pm_type == 'small':
            # Small PMs: 8 CPUs, 16 GB RAM
            cpu_capacity = 8
            memory_capacity = 16
        elif pm_type == 'medium':
            # Medium PMs: 16 CPUs, 32 GB RAM
            cpu_capacity = 16
            memory_capacity = 32
        else:  # large
            # Large PMs: 32 CPUs, 64 GB RAM
            cpu_capacity = 32
            memory_capacity = 64
        
        pm = {
            'id': i,
            'type': pm_type,
            'cpu_capacity': cpu_capacity,
            'memory_capacity': memory_capacity,
            'storage_capacity': 1000,  # 1 TB storage
            'power_idle': 100,  # Idle power consumption (W)
            'power_max': 300    # Maximum power consumption (W)
        }
        
        pms.append(pm)
    
    return pms


def generate_homogeneous_pms(num_pms: int,
                             cpu_capacity: int = 16,
                             memory_capacity: int = 32,
                             seed: int = 42) -> List[Dict]:
    """
    Generate homogeneous PMs with same specifications.
    
    Args:
        num_pms: Number of PMs to generate
        cpu_capacity: CPU capacity per PM
        memory_capacity: Memory capacity per PM (GB)
        seed: Random seed
        
    Returns:
        List of PM specifications
    """
    np.random.seed(seed)
    
    pms = []
    
    for i in range(num_pms):
        pm = {
            'id': i,
            'type': 'standard',
            'cpu_capacity': cpu_capacity,
            'memory_capacity': memory_capacity,
            'storage_capacity': 1000,
            'power_idle': 100,
            'power_max': 300
        }
        
        pms.append(pm)
    
    return pms


def generate_pms_with_diversity(num_pms: int, 
                                diversity_factor: float = 0.5,
                                base_cpu: int = 16,
                                base_memory: int = 32,
                                seed: int = 42) -> List[Dict]:
    """
    Generate PMs with controlled capacity diversity.
    
    Args:
        num_pms: Number of PMs to generate
        diversity_factor: Degree of heterogeneity (0=homogeneous, 1=highly diverse)
        base_cpu: Base CPU capacity
        base_memory: Base memory capacity
        seed: Random seed
        
    Returns:
        List of PM specifications
    """
    np.random.seed(seed)
    
    pms = []
    
    for i in range(num_pms):
        # Add variation based on diversity factor
        cpu_variation = int(base_cpu * diversity_factor * np.random.uniform(-0.5, 0.5))
        memory_variation = int(base_memory * diversity_factor * np.random.uniform(-0.5, 0.5))
        
        cpu_capacity = max(4, base_cpu + cpu_variation)
        memory_capacity = max(8, base_memory + memory_variation)
        
        pm = {
            'id': i,
            'cpu_capacity': cpu_capacity,
            'memory_capacity': memory_capacity,
            'storage_capacity': 1000,
            'power_idle': 100,
            'power_max': 300
        }
        
        pms.append(pm)
    
    return pms
