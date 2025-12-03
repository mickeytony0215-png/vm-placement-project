"""
Evaluation module for VM Placement
"""

from .metrics import (
    evaluate_placement,
    count_active_pms,
    calculate_energy_consumption,
    calculate_avg_cpu_utilization,
    calculate_avg_memory_utilization,
    calculate_fragmentation,
    calculate_load_balance,
    calculate_sla_violations
)

__all__ = [
    'evaluate_placement',
    'count_active_pms',
    'calculate_energy_consumption',
    'calculate_avg_cpu_utilization',
    'calculate_avg_memory_utilization',
    'calculate_fragmentation',
    'calculate_load_balance',
    'calculate_sla_violations'
]
