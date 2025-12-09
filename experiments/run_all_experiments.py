"""
Run All Experiments for VM Placement Project

This script runs three experiments:
1. ILP Baseline (25 VMs, 5 PMs) - with synthetic data
2. Real Workload (80 VMs, 15 PMs) - with PlanetLab data
3. Scalability Test (150 VMs, 30 PMs) - with PlanetLab data
"""

import sys
import os
import json
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.nlp_solver import NLPSolver as ILPSolver
from src.algorithms.ffd import FirstFitDecreasing
from src.algorithms.bfd import BestFitDecreasing
from src.algorithms.rls_ffd import RandomizedLocalSearchFFD
from src.utils.planetlab_loader import PlanetLabLoader
from src.utils.vm_generator import generate_vms
from src.utils.pm_generator import generate_pms
from src.evaluation.metrics import evaluate_placement


def print_header(title):
    """Print experiment header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_results(algo_name, metrics, exec_time):
    """Print algorithm results"""
    print(f"\n  >>> {algo_name} Results:")
    print(f"      Active PMs:     {metrics['active_pms']}")
    print(f"      Total Energy:   {metrics['total_energy']:.2f} kWh")
    print(f"      Avg CPU Util:   {metrics['avg_cpu_utilization']:.2f}%")
    print(f"      Avg RAM Util:   {metrics['avg_memory_utilization']:.2f}%")
    print(f"      Execution Time: {exec_time:.4f}s")


def run_experiment_1():
    """
    Experiment 1: ILP Baseline
    - 25 VMs, 5 PMs
    - Synthetic data
    - Goal: Establish optimal solution baseline
    """
    print_header("EXPERIMENT 1: ILP Baseline (25 VMs, 5 PMs)")
    
    # Generate synthetic data
    print("\n  Generating synthetic workload...")
    vms = generate_vms(num_vms=25, seed=42)
    pms = generate_pms(num_pms=5, cpu_capacity=100, ram_capacity=100, 
                       heterogeneous=False, seed=42)
    
    print(f"  Generated: 25 VMs, 5 PMs")
    
    results = {}
    
    # Test ILP
    print("\n  Testing ILP (optimal solver)...")
    ilp = ILPSolver(time_limit=300)  # 5 minutes max
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
    
    # Test FFD
    print("\n  Testing FFD...")
    ffd = FirstFitDecreasing()
    start = time.time()
    ffd_result = ffd.place(vms, pms)
    ffd_time = time.time() - start
    ffd_metrics = evaluate_placement(ffd_result, vms, pms)
    
    print_results("FFD", ffd_metrics, ffd_time)
    
    # Calculate gap
    gap = ((ffd_metrics['active_pms'] - ilp_metrics['active_pms']) / 
           ilp_metrics['active_pms'] * 100)
    print(f"\n  >>> Gap from Optimal: {gap:.2f}%")
    
    results['FFD'] = {
        'active_pms': ffd_metrics['active_pms'],
        'energy': ffd_metrics['total_energy'],
        'cpu_util': ffd_metrics['avg_cpu_utilization'],
        'time': ffd_time,
        'gap': gap
    }
    
    return results


def run_experiment_2():
    """
    Experiment 2: Real Workload
    - 80 VMs, 15 PMs
    - PlanetLab 20110303
    - Goal: Compare algorithms on real data
    """
    print_header("EXPERIMENT 2: Real Workload (80 VMs, 15 PMs)")
    
    # Load PlanetLab data
    loader = PlanetLabLoader("data/planetlab")
    
    try:
        vms = loader.load_vms('20110303', num_vms=80, time_point=144, seed=42)
    except FileNotFoundError:
        print("\n  ❌ Error: PlanetLab dataset not found!")
        print("  Please download it first:")
        print("    cd data")
        print("    git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab")
        return None
    
    pms = generate_pms(num_pms=15, cpu_capacity=100, ram_capacity=100, 
                       heterogeneous=False, seed=42)
    
    results = {}
    algorithms = {
        'FFD': FirstFitDecreasing(),
        'BFD': BestFitDecreasing(),
        'RLS-FFD': RandomizedLocalSearchFFD(max_iterations=100)
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
    Experiment 3: Scalability Test
    - 150 VMs, 30 PMs
    - PlanetLab 20110303
    - Goal: Test algorithm scalability
    """
    print_header("EXPERIMENT 3: Scalability Test (150 VMs, 30 PMs)")
    
    # Load PlanetLab data
    loader = PlanetLabLoader("data/planetlab")
    
    try:
        vms = loader.load_vms('20110303', num_vms=150, time_point=144, seed=42)
    except FileNotFoundError:
        print("\n  ❌ Error: PlanetLab dataset not found!")
        return None
    
    pms = generate_pms(num_pms=30, cpu_capacity=100, ram_capacity=100, 
                       heterogeneous=False, seed=42)
    
    results = {}
    algorithms = {
        'FFD': FirstFitDecreasing(),
        'BFD': BestFitDecreasing(),
        'RLS-FFD': RandomizedLocalSearchFFD(max_iterations=100)
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
    
    # Experiment 1: ILP Baseline
    try:
        exp1_results = run_experiment_1()
        all_results['experiment_1'] = exp1_results
    except Exception as e:
        print(f"\n❌ Experiment 1 failed: {e}")
        all_results['experiment_1'] = {'error': str(e)}
    
    # Experiment 2: Real Workload
    try:
        exp2_results = run_experiment_2()
        if exp2_results:
            all_results['experiment_2'] = exp2_results
    except Exception as e:
        print(f"\n❌ Experiment 2 failed: {e}")
        all_results['experiment_2'] = {'error': str(e)}
    
    # Experiment 3: Scalability
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