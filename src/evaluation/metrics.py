"""
Evaluation Metrics for VM Placement
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def evaluate_placement(result: Dict, vms: List[Dict], pms: List[Dict]) -> Dict:
    """
    Evaluate VM placement solution using multiple metrics.
    
    Args:
        result: Placement result from algorithm
        vms: List of VM specifications
        pms: List of PM specifications
        
    Returns:
        Dictionary of evaluation metrics
    """
    placement = result.get('placement', {})
    pm_status = result.get('pm_status', {})
    
    metrics = {}
    
    # 1. Number of active PMs (primary objective)
    metrics['active_pms'] = count_active_pms(pm_status)
    
    # 2. Total energy consumption
    metrics['total_energy'] = calculate_energy_consumption(pm_status, pms)
    
    # 3. Resource utilization
    metrics['avg_cpu_utilization'] = calculate_avg_cpu_utilization(pm_status, pms)
    metrics['avg_memory_utilization'] = calculate_avg_memory_utilization(pm_status, pms)
    
    # 4. Placement success rate
    metrics['placement_rate'] = len(placement) / len(vms) if vms else 0
    
    # 5. Resource fragmentation
    metrics['fragmentation_score'] = calculate_fragmentation(pm_status, pms)
    
    # 6. Load balance
    metrics['load_balance_score'] = calculate_load_balance(pm_status, pms)
    
    logger.info(f"Evaluation metrics: {metrics}")
    
    return metrics


def count_active_pms(pm_status: Dict) -> int:
    """Count number of active (non-empty) PMs"""
    return sum(1 for pm_state in pm_status.values() if pm_state.get('is_active', False))


def calculate_energy_consumption(pm_status: Dict, pms: List[Dict]) -> float:
    """
    Calculate total energy consumption.
    
    Energy model: E = P_idle + (P_max - P_idle) * utilization
    """
    total_energy = 0
    
    for pm in pms:
        pm_state = pm_status.get(pm['id'], {})
        
        if pm_state.get('is_active', False):
            # Get PM power characteristics
            power_idle = pm.get('power_idle', 100)  # W
            power_max = pm.get('power_max', 300)    # W
            
            # Calculate average utilization
            cpu_util = 1 - (pm_state.get('cpu_available', 0) / pm['cpu_capacity'])
            memory_util = 1 - (pm_state.get('memory_available', 0) / pm['memory_capacity'])
            avg_util = (cpu_util + memory_util) / 2
            
            # Linear energy model
            energy = power_idle + (power_max - power_idle) * avg_util
            total_energy += energy
    
    return total_energy


def calculate_avg_cpu_utilization(pm_status: Dict, pms: List[Dict]) -> float:
    """Calculate average CPU utilization across active PMs"""
    active_pms = [pm for pm in pms if pm_status.get(pm['id'], {}).get('is_active', False)]
    
    if not active_pms:
        return 0.0
    
    total_util = 0
    for pm in active_pms:
        pm_state = pm_status[pm['id']]
        cpu_used = pm['cpu_capacity'] - pm_state.get('cpu_available', pm['cpu_capacity'])
        util = cpu_used / pm['cpu_capacity']
        total_util += util
    
    return total_util / len(active_pms)


def calculate_avg_memory_utilization(pm_status: Dict, pms: List[Dict]) -> float:
    """Calculate average memory utilization across active PMs"""
    active_pms = [pm for pm in pms if pm_status.get(pm['id'], {}).get('is_active', False)]
    
    if not active_pms:
        return 0.0
    
    total_util = 0
    for pm in active_pms:
        pm_state = pm_status[pm['id']]
        memory_used = pm['memory_capacity'] - pm_state.get('memory_available', pm['memory_capacity'])
        util = memory_used / pm['memory_capacity']
        total_util += util
    
    return total_util / len(active_pms)


def calculate_fragmentation(pm_status: Dict, pms: List[Dict]) -> float:
    """
    Calculate resource fragmentation score.
    
    Fragmentation occurs when resources are scattered across many PMs
    with small remaining capacities, making it hard to place new VMs.
    
    Lower score is better.
    """
    active_pms = [pm for pm in pms if pm_status.get(pm['id'], {}).get('is_active', False)]
    
    if not active_pms:
        return 0.0
    
    fragmentation = 0
    
    for pm in active_pms:
        pm_state = pm_status[pm['id']]
        
        # Calculate normalized remaining capacity
        cpu_remaining_ratio = pm_state.get('cpu_available', 0) / pm['cpu_capacity']
        memory_remaining_ratio = pm_state.get('memory_available', 0) / pm['memory_capacity']
        
        # Fragmentation increases with unbalanced remaining resources
        balance_diff = abs(cpu_remaining_ratio - memory_remaining_ratio)
        fragmentation += balance_diff
    
    return fragmentation / len(active_pms) if active_pms else 0


def calculate_load_balance(pm_status: Dict, pms: List[Dict]) -> float:
    """
    Calculate load balance score across active PMs.
    
    Uses coefficient of variation of PM utilizations.
    Lower score indicates better balance.
    """
    active_pms = [pm for pm in pms if pm_status.get(pm['id'], {}).get('is_active', False)]
    
    if not active_pms:
        return 0.0
    
    utilizations = []
    
    for pm in active_pms:
        pm_state = pm_status[pm['id']]
        cpu_util = 1 - (pm_state.get('cpu_available', 0) / pm['cpu_capacity'])
        memory_util = 1 - (pm_state.get('memory_available', 0) / pm['memory_capacity'])
        avg_util = (cpu_util + memory_util) / 2
        utilizations.append(avg_util)
    
    if not utilizations:
        return 0.0
    
    # Calculate coefficient of variation
    import numpy as np
    mean_util = np.mean(utilizations)
    std_util = np.std(utilizations)
    
    if mean_util == 0:
        return 0.0
    
    cv = std_util / mean_util
    
    return cv


def calculate_sla_violations(pm_status: Dict, pms: List[Dict], threshold: float = 0.8) -> int:
    """
    Calculate number of SLA violations (PMs exceeding utilization threshold).
    
    Args:
        pm_status: Current PM status
        pms: PM specifications
        threshold: Utilization threshold for SLA violation
        
    Returns:
        Number of PMs violating SLA
    """
    violations = 0
    
    for pm in pms:
        pm_state = pm_status.get(pm['id'], {})
        
        if pm_state.get('is_active', False):
            cpu_util = 1 - (pm_state.get('cpu_available', 0) / pm['cpu_capacity'])
            memory_util = 1 - (pm_state.get('memory_available', 0) / pm['memory_capacity'])
            
            if cpu_util > threshold or memory_util > threshold:
                violations += 1
    
    return violations
