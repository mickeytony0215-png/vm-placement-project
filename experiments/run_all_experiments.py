"""
Run All Experiments for VM Placement Project

This script runs three experiments:
1. ILP Baseline (25 VMs, 5 PMs)
2. Real Workload (Stress Test) - 80 VMs, 60 PMs
3. Scalability Test (Stress Test) - 150 VMs, 100 PMs
"""

import sys
import os
import json
import time
import random
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.nlp_solver import NLPSolver as ILPSolver
from src.algorithms.ffd import FirstFitDecreasing
from src.algorithms.bfd import BestFitDecreasing
from src.algorithms.rls_ffd import RandomizedLocalSearchFFD
from src.utils.planetlab_loader import PlanetLabLoader
from src.utils.vm_generator import generate_vms
from src.utils.pm_generator import generate_pms, generate_homogeneous_pms
from src.evaluation.metrics import evaluate_placement


def print_header(title):
    """Print experiment header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_results(algo_name, metrics, exec_time, gap=None):
    """Print algorithm results"""
    print(f"\n  >>> {algo_name} Results:")
    print(f"      Active PMs:     {metrics['active_pms']}")
    print(f"      Total Energy:   {metrics['total_energy']:.2f} kWh")
    print(f"      Avg CPU Util:   {metrics['avg_cpu_utilization']:.2f}%")
    print(f"      Avg RAM Util:   {metrics['avg_memory_utilization']:.2f}%")
    print(f"      Execution Time: {exec_time:.4f}s")
    if gap is not None:
        print(f"      Gap to Optimal: {gap:.2f}%")


def fix_vm_keys(vms):
    """Fix VM keys from PlanetLab loader."""
    for vm in vms:
        if 'cpu' in vm and 'cpu_demand' not in vm:
            vm['cpu_demand'] = vm['cpu']
        if 'ram' in vm and 'memory_demand' not in vm:
            vm['memory_demand'] = vm['ram']
    return vms


def apply_stress_test_logic(vms):
    """
    [CRITICAL CHANGE]
    Modifies VMs to create a 'Hard' Bin Packing instance.
    Strategy:
    1. Scale demands to be 'awkward' sizes (e.g. 40-70% of PM capacity).
    2. Create resource contention (High CPU/Low RAM vs Low CPU/High RAM).
    """
    print("  ⚡ Applying STRESS TEST logic (Skewed Resources + Awkward Sizes)...")
    
    # Assuming PMs are roughly Small(8), Med(16), Large(32).
    # We want to target around 12-18 CPU/RAM to be annoying for Medium PMs.
    
    for i, vm in enumerate(vms):
        # Base jitter to keep randomness
        base_val = random.uniform(10, 20) 
        
        if i % 2 == 0:
            # Type A: CPU Heavy, RAM Light
            # This requires a Medium(16) or Large(32) PM for CPU, but wastes RAM.
            vm['cpu_demand'] = base_val       # e.g., 15 (Fits tightly in Med)
            vm['memory_demand'] = base_val / 4 # e.g., 3.75
        else:
            # Type B: CPU Light, RAM Heavy
            # Complementary to Type A.
            vm['cpu_demand'] = base_val / 4    # e.g., 3.75
            vm['memory_demand'] = base_val     # e.g., 15
            
    return vms


def run_experiment_1():
    """
    Experiment 1: ILP Baseline
    - 25 VMs, 5 PMs
    - Synthetic data (Homogeneous)
    """
    print_header("EXPERIMENT 1: ILP Baseline (25 VMs, 5 PMs)")
    
    # Generate synthetic data
    print("\n  Generating synthetic workload...")
    vms = generate_vms(num_vms=25, seed=42)
    # Use Homogeneous for clear baseline comparison
    pms = generate_homogeneous_pms(num_pms=5, cpu_capacity=100, memory_capacity=100, seed=42)
    
    print(f"  Generated: 25 VMs, 5 PMs")
    
    results = {}
    
    # 1. Run ILP
    print("\n  Testing ILP (optimal solver)...")
    ilp = ILPSolver(time_limit=300)
    start = time.time()
    ilp_result = ilp.place(vms, pms)
    ilp_time = time.time() - start
    ilp_metrics = evaluate_placement(ilp_result, vms, pms)
    
    print_results("ILP", ilp_metrics, ilp_time)
    results['ILP'] = {
        'active_pms': ilp_metrics['active_pms'],
        'energy': ilp_metrics['total_energy'],
        'cpu_util': ilp_metrics['avg_cpu_utilization'],
        'time': ilp_time
    }
    
    # 2. Run others
    algorithms = {
        'FFD': FirstFitDecreasing(),
        'BFD': BestFitDecreasing(),
        'RLS-FFD': RandomizedLocalSearchFFD(max_iterations=1000)
    }
    
    optimal_pms = ilp_metrics['active_pms']
    
    for algo_name, algo in algorithms.items():
        print(f"\n  Testing {algo_name}...")
        start = time.time()
        result = algo.place(vms, pms)
        exec_time = time.time() - start
        metrics = evaluate_placement(result, vms, pms)
        
        gap = 0.0
        if optimal_pms > 0:
            gap = ((metrics['active_pms'] - optimal_pms) / optimal_pms * 100)
        
        print_results(algo_name, metrics, exec_time, gap)
        
        results[algo_name] = {
            'active_pms': metrics['active_pms'],
            'energy': metrics['total_energy'],
            'cpu_util': metrics['avg_cpu_utilization'],
            'time': exec_time,
            'gap': gap
        }
    
    return results


def run_experiment_2():
    """
    Experiment 2: Real Workload (Stress Test)
    - 80 VMs, 60 PMs
    - Skewed Resources
    """
    print_header("EXPERIMENT 2: Real Workload Stress Test (80 VMs)")
    
    loader = PlanetLabLoader("data/planetlab")
    
    try:
        vms = loader.load_vms('20110303', num_vms=80, time_point=144, seed=42)
        vms = fix_vm_keys(vms)
        # Apply the logic that makes it hard
        vms = apply_stress_test_logic(vms)
    except FileNotFoundError:
        print("\n  ❌ Error: PlanetLab dataset not found!")
        return None
    
    # Use Heterogeneous PMs
    # Increase count to 60 to ensure we have enough "buckets" for these large items
    print("\n  Generating Heterogeneous PMs...")
    pms = generate_pms(num_pms=60, seed=42)
    
    results = {}
    algorithms = {
        'FFD': FirstFitDecreasing(),
        'BFD': BestFitDecreasing(),
        'RLS-FFD': RandomizedLocalSearchFFD(max_iterations=2000)
    }
    
    for algo_name, algo in algorithms.items():
        print(f"\n  Testing {algo_name}...")
        start = time.time()
        result = algo.place(vms, pms)
        exec_time = time.time() - start
        metrics = evaluate_placement(result, vms, pms)
        
        print_results(algo_name, metrics, exec_time)
        
        results[algo_name] = {
            'active_pms': metrics['active_pms'],
            'energy': metrics['total_energy'],
            'cpu_util': metrics['avg_cpu_utilization'],
            'ram_util': metrics['avg_memory_utilization'],
            'time': exec_time
        }
    
    return results


def run_experiment_3():
    """
    Experiment 3: Scalability Test (Stress Test)
    - 150 VMs, 100 PMs
    - Skewed Resources
    """
    print_header("EXPERIMENT 3: Scalability Stress Test (150 VMs)")
    
    loader = PlanetLabLoader("data/planetlab")
    
    try:
        vms = loader.load_vms('20110303', num_vms=150, time_point=144, seed=42)
        vms = fix_vm_keys(vms)
        vms = apply_stress_test_logic(vms)
    except FileNotFoundError:
        print("\n  ❌ Error: PlanetLab dataset not found!")
        return None
    
    # Increase PMs substantially
    print("\n  Generating Heterogeneous PMs...")
    pms = generate_pms(num_pms=100, seed=42)
    
    results = {}
    algorithms = {
        'FFD': FirstFitDecreasing(),
        'BFD': BestFitDecreasing(),
        'RLS-FFD': RandomizedLocalSearchFFD(max_iterations=2000)
    }
    
    for algo_name, algo in algorithms.items():
        print(f"\n  Testing {algo_name}...")
        start = time.time()
        result = algo.place(vms, pms)
        exec_time = time.time() - start
        metrics = evaluate_placement(result, vms, pms)
        
        print_results(algo_name, metrics, exec_time)
        
        results[algo_name] = {
            'active_pms': metrics['active_pms'],
            'energy': metrics['total_energy'],
            'cpu_util': metrics['avg_cpu_utilization'],
            'time': exec_time
        }
    
    return results


def save_results(all_results):
    """Save experiment results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"experiment_results_{timestamp}.json")
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    return output_file


def main():
    """Run all experiments"""
    print("\n" + "="*70)
    print("  VM PLACEMENT EXPERIMENTS")
    print("  Course Final Project")
    print("="*70)
    
    all_results = {}
    
    # Experiment 1
    try:
        exp1_results = run_experiment_1()
        all_results['experiment_1'] = exp1_results
    except Exception as e:
        print(f"\n❌ Experiment 1 failed: {e}")
        all_results['experiment_1'] = {'error': str(e)}
    
    # Experiment 2
    try:
        exp2_results = run_experiment_2()
        if exp2_results:
            all_results['experiment_2'] = exp2_results
    except Exception as e:
        print(f"\n❌ Experiment 2 failed: {e}")
        import traceback
        traceback.print_exc()
        all_results['experiment_2'] = {'error': str(e)}
    
    # Experiment 3
    try:
        exp3_results = run_experiment_3()
        if exp3_results:
            all_results['experiment_3'] = exp3_results
    except Exception as e:
        print(f"\n❌ Experiment 3 failed: {e}")
        all_results['experiment_3'] = {'error': str(e)}
    
    # Save results
    output_file = save_results(all_results)
    
    print("\n" + "="*70)
    print("  ✓ ALL EXPERIMENTS COMPLETED!")
    print(f"  Results saved to: {output_file}")
    print("="*70)
    print()


if __name__ == "__main__":
    main()