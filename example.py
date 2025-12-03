"""
Quick Start Example - VM Placement Demo

This script demonstrates how to use the VM placement algorithms.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from algorithms.ffd import FirstFitDecreasing
from algorithms.bfd import BestFitDecreasing
from utils.vm_generator import generate_vms
from utils.pm_generator import generate_pms
from evaluation.metrics import evaluate_placement

print("=" * 60)
print("Virtual Machine Placement - Quick Start Demo")
print("=" * 60)

# Generate problem instance
print("\n1. Generating problem instance...")
print("   - Small scale: 5 PMs, 25 VMs")
vms = generate_vms(num_vms=25, seed=42)
pms = generate_pms(num_pms=5, seed=42)

print(f"   Generated {len(vms)} VMs:")
print(f"   - Small: {sum(1 for vm in vms if vm['type'] == 'small')} VMs")
print(f"   - Medium: {sum(1 for vm in vms if vm['type'] == 'medium')} VMs")
print(f"   - Large: {sum(1 for vm in vms if vm['type'] == 'large')} VMs")

print(f"\n   Generated {len(pms)} PMs:")
print(f"   - Small: {sum(1 for pm in pms if pm['type'] == 'small')} PMs")
print(f"   - Medium: {sum(1 for pm in pms if pm['type'] == 'medium')} PMs")
print(f"   - Large: {sum(1 for pm in pms if pm['type'] == 'large')} PMs")

# Run FFD algorithm
print("\n2. Running First Fit Decreasing (FFD) Algorithm...")
ffd = FirstFitDecreasing()
result_ffd = ffd.place(vms, pms)
metrics_ffd = evaluate_placement(result_ffd, vms, pms)

print("   FFD Results:")
print(f"   - VMs placed: {len(result_ffd['placement'])}/{len(vms)}")
print(f"   - Active PMs: {metrics_ffd['active_pms']}")
print(f"   - Energy consumption: {metrics_ffd['total_energy']:.2f} W")
print(f"   - Avg CPU utilization: {metrics_ffd['avg_cpu_utilization']:.2%}")
print(f"   - Avg Memory utilization: {metrics_ffd['avg_memory_utilization']:.2%}")

# Run BFD algorithm
print("\n3. Running Best Fit Decreasing (BFD) Algorithm...")
bfd = BestFitDecreasing()
result_bfd = bfd.place(vms, pms)
metrics_bfd = evaluate_placement(result_bfd, vms, pms)

print("   BFD Results:")
print(f"   - VMs placed: {len(result_bfd['placement'])}/{len(vms)}")
print(f"   - Active PMs: {metrics_bfd['active_pms']}")
print(f"   - Energy consumption: {metrics_bfd['total_energy']:.2f} W")
print(f"   - Avg CPU utilization: {metrics_bfd['avg_cpu_utilization']:.2%}")
print(f"   - Avg Memory utilization: {metrics_bfd['avg_memory_utilization']:.2%}")

# Compare results
print("\n4. Algorithm Comparison:")
print("-" * 60)
print(f"{'Metric':<30} {'FFD':<15} {'BFD':<15}")
print("-" * 60)
print(f"{'Active PMs':<30} {metrics_ffd['active_pms']:<15} {metrics_bfd['active_pms']:<15}")
print(f"{'Energy (W)':<30} {metrics_ffd['total_energy']:<15.2f} {metrics_bfd['total_energy']:<15.2f}")
print(f"{'CPU Utilization':<30} {metrics_ffd['avg_cpu_utilization']:<15.2%} {metrics_bfd['avg_cpu_utilization']:<15.2%}")
print(f"{'Memory Utilization':<30} {metrics_ffd['avg_memory_utilization']:<15.2%} {metrics_bfd['avg_memory_utilization']:<15.2%}")
print("-" * 60)

# Determine winner
if metrics_ffd['active_pms'] < metrics_bfd['active_pms']:
    winner = "FFD"
elif metrics_bfd['active_pms'] < metrics_ffd['active_pms']:
    winner = "BFD"
else:
    if metrics_ffd['total_energy'] < metrics_bfd['total_energy']:
        winner = "FFD"
    else:
        winner = "BFD"

print(f"\nBest algorithm for this instance: {winner}")

print("\n" + "=" * 60)
print("Demo completed successfully!")
print("=" * 60)
print("\nNext steps:")
print("1. Run full experiments: python src/main.py --run-all")
print("2. Run tests: pytest tests/")
print("3. Customize problem: Modify vm_generator.py and pm_generator.py")
