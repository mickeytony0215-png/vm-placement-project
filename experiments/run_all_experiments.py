"""
Run All Experiments for VM Placement Project

This script runs four experiments:
1. ILP Baseline (25 VMs, 5 PMs)
2. Real Workload (Stress Test) - 80 VMs, 60 PMs
3. Scalability Test (Stress Test) - 150 VMs, 100 PMs
4. Google Trace Dataset (10000 VMs, 2000 PMs)
"""

import sys
import os
import json
import time
import random
from datetime import datetime
from pathlib import Path

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


# ---------------------------------------------------
# Utility printing
# ---------------------------------------------------
def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_results(algo_name, metrics, exec_time, gap=None):
    print(f"\n  >>> {algo_name} Results:")
    print(f"      Active PMs:     {metrics['active_pms']}")
    print(f"      Total Energy:   {metrics['total_energy']:.2f} kWh")
    print(f"      Avg CPU Util:   {metrics['avg_cpu_utilization']:.2f}%")
    print(f"      Avg RAM Util:   {metrics.get('avg_memory_utilization', 0):.2f}%")
    print(f"      Execution Time: {exec_time:.4f}s")
    if gap is not None:
        print(f"      Gap to Optimal: {gap:.2f}%")


# ---------------------------------------------------
# Fix VM key names
# ---------------------------------------------------
def fix_vm_keys(vms):
    for vm in vms:
        if "cpu" in vm and "cpu_demand" not in vm:
            vm["cpu_demand"] = vm["cpu"]
        if "ram" in vm and "memory_demand" not in vm:
            vm["memory_demand"] = vm["ram"]
    return vms


# ---------------------------------------------------
# Stress Test Logic
# ---------------------------------------------------
def apply_stress_test_logic(vms):
    print("  ⚡ Applying STRESS TEST logic (Skewed Resources + Awkward Sizes)...")

    for i, vm in enumerate(vms):
        base = random.uniform(10, 20)

        if i % 2 == 0:
            vm["cpu_demand"] = base
            vm["memory_demand"] = base / 4
        else:
            vm["cpu_demand"] = base / 4
            vm["memory_demand"] = base

    return vms


# ---------------------------------------------------
# Experiment 1: ILP Baseline
# ---------------------------------------------------
def run_experiment_1():
    print_header("EXPERIMENT 1: ILP Baseline (25 VMs, 5 PMs)")

    vms = generate_vms(num_vms=25, seed=42)
    pms = generate_homogeneous_pms(num_pms=5, cpu_capacity=100, memory_capacity=100, seed=42)

    results = {}

    # ILP
    print("\n  Testing ILP (optimal solver)...")
    ilp = ILPSolver(time_limit=300)

    start = time.time()
    ilp_result = ilp.place(vms, pms)
    ilp_time = time.time() - start

    ilp_metrics = evaluate_placement(ilp_result, vms, pms)
    print_results("ILP", ilp_metrics, ilp_time)

    results["ILP"] = {
        "active_pms": ilp_metrics["active_pms"],
        "energy": ilp_metrics["total_energy"],
        "cpu_util": ilp_metrics["avg_cpu_utilization"],
        "time": ilp_time,
    }

    optimal_pms = ilp_metrics["active_pms"]

    # FFD / BFD / RLS-FFD
    algorithms = {
        "FFD": FirstFitDecreasing(),
        "BFD": BestFitDecreasing(),
        "RLS-FFD": RandomizedLocalSearchFFD(max_iterations=1000),
    }

    for name, algo in algorithms.items():
        print(f"\n  Testing {name}...")
        start = time.time()
        result = algo.place(vms, pms)
        t = time.time() - start
        m = evaluate_placement(result, vms, pms)

        gap = ((m["active_pms"] - optimal_pms) / optimal_pms * 100)

        print_results(name, m, t, gap)

        results[name] = {
            "active_pms": m["active_pms"],
            "energy": m["total_energy"],
            "cpu_util": m["avg_cpu_utilization"],
            "time": t,
            "gap": gap,
        }

    return results


# ---------------------------------------------------
# Experiment 2: Stress Test (80 VMs)
# ---------------------------------------------------
def run_experiment_2():
    print_header("EXPERIMENT 2: Real Workload Stress Test (80 VMs)")

    loader = PlanetLabLoader("data/planetlab")
    vms = loader.load_vms("20110303", num_vms=80, time_point=144, seed=42)
    vms = fix_vm_keys(vms)
    vms = apply_stress_test_logic(vms)

    pms = generate_pms(num_pms=60, seed=42)

    results = {}
    algorithms = {
        "FFD": FirstFitDecreasing(),
        "BFD": BestFitDecreasing(),
        "RLS-FFD": RandomizedLocalSearchFFD(max_iterations=2000),
    }

    for name, algo in algorithms.items():
        print(f"\n  Testing {name}...")
        start = time.time()
        result = algo.place(vms, pms)
        t = time.time() - start
        m = evaluate_placement(result, vms, pms)

        print_results(name, m, t)

        results[name] = {
            "active_pms": m["active_pms"],
            "energy": m["total_energy"],
            "cpu_util": m["avg_cpu_utilization"],
            "ram_util": m["avg_memory_utilization"],
            "time": t,
        }

    return results


# ---------------------------------------------------
# Experiment 3: Stress Test Large (150 VMs)
# ---------------------------------------------------
def run_experiment_3():
    print_header("EXPERIMENT 3: Scalability Stress Test (150 VMs)")

    loader = PlanetLabLoader("data/planetlab")
    vms = loader.load_vms("20110303", num_vms=150, time_point=144, seed=42)
    vms = fix_vm_keys(vms)
    vms = apply_stress_test_logic(vms)

    pms = generate_pms(num_pms=100, seed=42)

    results = {}
    algorithms = {
        "FFD": FirstFitDecreasing(),
        "BFD": BestFitDecreasing(),
        "RLS-FFD": RandomizedLocalSearchFFD(max_iterations=2000),
    }

    for name, algo in algorithms.items():
        print(f"\n  Testing {name}...")
        start = time.time()
        result = algo.place(vms, pms)
        t = time.time() - start
        m = evaluate_placement(result, vms, pms)

        print_results(name, m, t)

        results[name] = {
            "active_pms": m["active_pms"],
            "energy": m["total_energy"],
            "cpu_util": m["avg_cpu_utilization"],
            "time": t,
        }

    return results


# ---------------------------------------------------
# Google Trace Loader (10000 VM + 2000 PM)
# ---------------------------------------------------
def load_google_dataset():
    base = Path("data/google_dataset")

    print("\n📂 Loading Google Trace dataset ...")

    with open(base / "google_vms_10000.json", "r") as f:
        vms = json.load(f)

    with open(base / "google_pms_2000.json", "r") as f:
        pms = json.load(f)

    print(f"   → Loaded {len(vms)} VMs, {len(pms)} PMs")

    return vms, pms


# ---------------------------------------------------
# Experiment 4: Google Trace
# ---------------------------------------------------
def run_experiment_google():
    print_header("EXPERIMENT 4: Google Trace Dataset (10000 VMs, 2000 PMs)")

    vms, pms = load_google_dataset()

    results = {}
    algorithms = {
        "FFD": FirstFitDecreasing(),
        "BFD": BestFitDecreasing(),
        "RLS-FFD": RandomizedLocalSearchFFD(max_iterations=3000),
    }

    for name, algo in algorithms.items():
        print(f"\n  Testing {name} on Google Trace...")
        start = time.time()
        result = algo.place(vms, pms)
        t = time.time() - start
        m = evaluate_placement(result, vms, pms)

        print_results(name, m, t)

        results[name] = {
            "active_pms": m["active_pms"],
            "energy": m["total_energy"],
            "cpu_util": m["avg_cpu_utilization"],
            "time": t,
        }

    return results


# ---------------------------------------------------
# Save JSON
# ---------------------------------------------------
def save_results(all_results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = "results"
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"experiment_results_{timestamp}.json")

    with open(outfile, "w") as f:
        json.dump(all_results, f, indent=2)

    return outfile


# ---------------------------------------------------
# Main execution
# ---------------------------------------------------
def main():
    print("\n" + "=" * 70)
    print("  VM PLACEMENT EXPERIMENTS — Final Project")
    print("=" * 70)

    all_results = {}

    # Experiment 1
    try:
        all_results["experiment_1"] = run_experiment_1()
    except Exception as e:
        all_results["experiment_1"] = {"error": str(e)}

    # Experiment 2
    try:
        all_results["experiment_2"] = run_experiment_2()
    except Exception as e:
        all_results["experiment_2"] = {"error": str(e)}

    # Experiment 3
    try:
        all_results["experiment_3"] = run_experiment_3()
    except Exception as e:
        all_results["experiment_3"] = {"error": str(e)}

    # Experiment 4 – Google Trace
    try:
        all_results["experiment_4_google"] = run_experiment_google()
    except Exception as e:
        all_results["experiment_4_google"] = {"error": str(e)}

    # Save final JSON
    outfile = save_results(all_results)

    print("\n" + "=" * 70)
    print("  ✓ ALL EXPERIMENTS COMPLETED!")
    print(f"  Results saved to: {outfile}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
