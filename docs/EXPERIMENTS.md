# Experimental Design

## Overview

This document describes the comprehensive experimental evaluation of four VM placement algorithms across four experiments with increasing scale and complexity. The experiments use both synthetic data, academic benchmarks (PlanetLab), and industrial-scale real-world datasets (Google Cluster Trace 2011).

**Algorithms Evaluated:**
- **ILP** (Integer Linear Programming): Exact optimization for baseline
- **FFD** (First Fit Decreasing): Fast greedy heuristic
- **BFD** (Best Fit Decreasing): Greedy with fragmentation reduction
- **RLS-FFD** (Randomized Local Search): Meta-heuristic optimization

---

## Datasets

### 1. Synthetic Data
- **Usage**: Experiment 1 only
- **Generation**: Controlled random generation with fixed seed
- **Purpose**: Small-scale baseline for ILP optimal solutions
- **Scale**: 25 VMs, 5 homogeneous PMs

### 2. PlanetLab Workload Traces

**Source**: https://github.com/beloglazov/planetlab-workload-traces

**Dataset Characteristics:**
- **Date**: March 3, 2011 (20110303)
- **Total VMs**: 1,052 VM CPU utilization traces
- **Time Points**: 288 per VM (24 hours × 12 samples/hour)
- **Sampling Interval**: 5 minutes
- **Data Format**: Plain text, one CPU utilization value per line (0-100%)

**Our Sampling Strategy:**
- Use random sampling from the 1,052 available VMs
- Maintain statistical representativeness
- Justification: ILP cannot handle 1,052 VMs; course project scope requires manageable scale

**Usage**: Experiments 2 & 3

**Limitation**: PlanetLab provides only CPU utilization, **not real PM capacity data**. We use synthetic heterogeneous PMs and apply stress test logic to create challenging scenarios.

### 3. Google Cluster Trace 2011

**Source**: Google Borg system production traces

**Dataset Characteristics:**
- **Original Scale**: 12,583 physical machines, 170,000+ tasks
- **Our Sampling**: 10,000 VMs, 2,000 PMs (random sampling with seed=42)
- **Data Files Used**:
  - `task_usage`: VM resource demands (CPU rate, memory usage)
  - `machine_events`: PM capacities (CPU, memory)

**Resource Calculation:**
- **VM CPU Demand**: `max(cpu_rate) × 100` (peak strategy)
- **VM Memory Demand**: `max(assigned_memory) × 100` (peak strategy)
- **PM CPU Capacity**: `cpu_capacity × 100`
- **PM Memory Capacity**: `memory_capacity × 100`

**Key Advantages:**
1. **Real heterogeneous PM configurations** (different CPU/memory ratios)
2. **Industrial-scale validation** (10,000 VMs)
3. **Authentic workload patterns** (long-tail distribution preserved)
4. **Peak demand strategy** ensures static placement handles worst-case load

**Usage**: Experiment 4

---

## Physical Machine Configurations

### Experiment 1: Homogeneous PMs
All PMs are identical:
```
CPU Capacity:    100 units
Memory Capacity: 100 GB
```

**Rationale**: Simplifies analysis for optimal baseline comparison.

### Experiments 2 & 3: Heterogeneous PMs

Synthetic heterogeneous configuration to simulate real data centers:

| PM Type | CPU | Memory | Probability | Characteristics |
|---------|-----|--------|-------------|-----------------|
| **Small** | 8 vCPU | 16 GB | 20% | Edge nodes, difficult to fit large VMs |
| **Medium** | 16 vCPU | 32 GB | 50% | Main workhorses; **designed to cause fragmentation** |
| **Large** | 32 vCPU | 64 GB | 30% | High-capacity nodes, optimization targets |

**Fragmentation Design:**
- Medium PMs have capacity that gets nearly filled by a single large VM
- Remaining capacity is often too small for another VM
- This challenges greedy algorithms to make better placement decisions

### Experiment 4: Real Heterogeneous PMs

From Google Trace `machine_events.csv`, examples of real PM configurations:
```
PM 1: CPU=50.0,  Memory=49.95  (balanced)
PM 2: CPU=50.0,  Memory=24.93  (CPU-heavy)
PM 3: CPU=25.0,  Memory=24.98  (small, balanced)
PM 4: CPU=12.5,  Memory=12.46  (very small)
```

**Key Challenge**: CPU/memory ratios vary significantly, exposing weaknesses in BFD's "minimum remaining capacity" strategy.

---

## Stress Test Logic (Experiments 2 & 3)

To make PlanetLab data more challenging, we apply **resource skewness**:

```python
for i, vm in enumerate(vms):
    base = random.uniform(10, 20)

    if i % 2 == 0:  # Type A: CPU-heavy
        vm["cpu_demand"] = base
        vm["memory_demand"] = base / 4
    else:           # Type B: Memory-heavy
        vm["cpu_demand"] = base / 4
        vm["memory_demand"] = base
```

**Effect:**
- Half the VMs are CPU-heavy (4:1 CPU/memory ratio)
- Half the VMs are memory-heavy (1:4 CPU/memory ratio)
- Creates worst-case bin packing scenarios where greedy algorithms struggle

---

## Four Experiments

### Experiment 1: ILP Baseline (Optimal Reference)

**Objective:** Establish provably optimal solutions to measure algorithm quality

**Configuration:**
- **VMs**: 25 (synthetic, generated with seed=42)
- **PMs**: 5 (homogeneous: 100 CPU / 100 Memory)
- **Algorithms**: ILP, FFD, BFD, RLS-FFD
- **ILP Time Limit**: 300 seconds

**Key Metric:** Optimality Gap
```
Gap = (Heuristic_Active_PMs - ILP_Active_PMs) / ILP_Active_PMs × 100%
```

**Expected Outcomes:**
- ILP finds optimal solution in < 60 seconds
- FFD within 5-15% of optimal
- Demonstrates computational limits of exact methods

**Why Synthetic Data?**
- ILP requires small problem size (< 50 VMs)
- Need controlled environment to verify algorithm correctness
- Establish true optimal baseline for gap calculation

---

### Experiment 2: Real Workload Stress Test

**Objective:** Evaluate algorithms under resource skewness with real workload patterns

**Configuration:**
- **VMs**: 80 (from PlanetLab 20110303, time_point=144, seed=42)
- **PMs**: 60 (heterogeneous: 20% Small, 50% Medium, 30% Large)
- **Algorithms**: **ILP** (with **20s time limit**), FFD, BFD, RLS-FFD
- **Stress Logic**: Applied (CPU-heavy vs. memory-heavy VMs)
- **RLS Iterations**: 2,000

**Why This Scale?**
- Represents realistic department/small datacenter
- PlanetLab provides authentic workload base patterns
- Sufficient scale to show algorithm differences
- **Demonstrates ILP computational infeasibility** at medium scale

**ILP Configuration:**
- **Time Limit**: **20 seconds** (intentionally short)
- **Purpose**: **Prove that ILP is impractical for 80 VMs**
- **Expected**: Will timeout, demonstrating exact methods don't scale
- **Academic Value**: Establishes computational boundary where heuristics become necessary

**Expected Outcomes:**
- **ILP will timeout** (expected and desired outcome to prove infeasibility)
- If ILP unexpectedly succeeds: Would show problem is easier than anticipated
- RLS-FFD expected to outperform FFD/BFD by 5-10%
- Execution time: FFD < 0.01s, BFD < 0.01s, RLS-FFD ~2s, **ILP ~20s (timeout)**
- CPU utilization: 60-80%

**Key Insight**: This experiment demonstrates the **practical necessity of heuristic algorithms** when exact methods become computationally intractable.

**Challenge:** 60 PMs available but algorithms should use far fewer by efficient packing.

---

### Experiment 3: Scalability Stress Test

**Objective:** Test algorithm performance at larger scale

**Configuration:**
- **VMs**: 150 (from PlanetLab 20110303, time_point=144, seed=42)
- **PMs**: 100 (heterogeneous: 20% Small, 50% Medium, 30% Large)
- **Algorithms**: FFD, BFD, RLS-FFD
- **Stress Logic**: Applied
- **RLS Iterations**: 2,000

**Why This Scale?**
- Tests scalability compared to Experiment 2 (1.875× larger)
- Still manageable for course project
- Demonstrates algorithm efficiency differences at scale

**Expected Outcomes:**
- RLS-FFD continues to outperform greedy methods
- Execution time increases but remains reasonable (<5s for heuristics)
- Quality gap between algorithms becomes more pronounced

---

### Experiment 4: Google Trace Dataset (Industrial-Scale Validation)

**Objective:** Validate algorithms on real industrial-scale data with heterogeneous PMs

**Configuration:**
- **VMs**: 10,000 (randomly sampled from Google Trace with seed=42)
- **PMs**: 2,000 (randomly sampled from 12,583 real machines)
- **Algorithms**: FFD, BFD, RLS-FFD (ILP impossible at this scale)
- **RLS Iterations**: 3,000
- **Dataset**: `data/google_dataset/google_vms_10000.json` and `google_pms_2000.json`

**Why This Scale?**
- Represents real data center deployment
- Tests algorithm robustness on authentic heterogeneous infrastructure
- 125× larger than Experiment 1, 6.67× larger than Experiment 3
- Stresses computational efficiency

**Data Preprocessing:**
See `src/utils/google_trace_to_dataset.py` for details on how raw Google Trace CSV files are converted to JSON datasets.

**Actual Results (from latest run):**

| Algorithm | Active PMs | CPU Util | Energy (kWh) | Exec Time |
|-----------|-----------|----------|--------------|-----------|
| **FFD** | **836** | **92.35%** | **223,517** | **0.76s** |
| BFD | 993 (+18.8%) | 83.52% | 269,930 | 9.38s |
| **RLS-FFD** | **836** | **92.35%** | **223,517** | 3.46s |

**Key Findings:**
1. **FFD excels**: Blazing fast (<1s) with excellent solution quality
2. **BFD fails catastrophically**: Uses 157 more PMs (18.8% worse)
   - **Root Cause**: In heterogeneous environments, BFD's "minimum remaining capacity" strategy causes one resource dimension (CPU or memory) to exhaust first, leaving the other dimension wasted
   - This creates severe fragmentation when CPU/memory ratios vary across PMs
3. **RLS-FFD matches FFD**: Same solution quality but 4.5× slower
   - Suggests FFD already found near-optimal solution for this instance
   - RLS improvements minimal due to good initial FFD placement

**Why This Matters:**
- Demonstrates that **algorithm selection depends on PM heterogeneity**
- BFD works well for homogeneous environments (Experiment 1)
- BFD fails for heterogeneous environments (Experiment 4)
- FFD's simplicity is an advantage: fast and robust across scenarios

---

## Evaluation Metrics

### Primary Metrics

1. **Active PMs** (lower is better)
   - Primary optimization objective
   - Directly impacts energy consumption and operational cost
   - Target: Minimize while maintaining reasonable utilization

2. **Total Energy Consumption** (kWh, lower is better)
   - Calculated using linear energy model:
     ```
     Energy(PM) = Idle_Power + (Max_Power - Idle_Power) × Utilization
     Utilization = (CPU_used + Memory_used) / (CPU_capacity + Memory_capacity)
     ```
   - Reflects real operational cost

3. **Average CPU Utilization** (%)
   - Target range: 60-80%
   - Too low (<30%): wasted resources
   - Too high (>90%): SLA violation risk, no headroom for peaks

4. **Average Memory Utilization** (%)
   - Similar target: 60-80%
   - Important for multi-dimensional bin packing evaluation

5. **Execution Time** (seconds)
   - Algorithm efficiency measure
   - Critical for real-time/dynamic placement scenarios
   - Expected: Greedy <1s, RLS <10s, ILP <300s (or timeout)

6. **Optimality Gap** (%, Experiment 1 only)
   - `Gap = (Heuristic_PMs - Optimal_PMs) / Optimal_PMs × 100%`
   - Measures solution quality against proven optimal
   - Target: <15% for good heuristics

### Secondary Metrics

- **Placement Success Rate**: Percentage of VMs successfully placed
- **Resource Balance**: Std. dev. of PM utilizations (lower = better load balance)

---

## Expected Results Summary

| Experiment | Scale | Best Algorithm | Key Finding |
|------------|-------|----------------|-------------|
| Exp 1 | 25 VMs | ILP (optimal) | FFD within 5-15% of optimal |
| Exp 2 | 80 VMs | RLS-FFD | **ILP times out (20s)** - proves exact methods impractical; RLS-FFD 5-10% better |
| Exp 3 | 150 VMs | RLS-FFD | Maintains advantage at scale, <5s runtime |
| Exp 4 | 10,000 VMs | **FFD** | BFD fails (+18.8%), FFD robust and fast (0.76s) |

---

## Comparison with Literature

### CloudBench (2018)
- Used full 1,052 PlanetLab VMs, 41-50 PMs
- Focus: **Dynamic VM consolidation** over 24 hours with migrations

### Beloglazov et al. (2012)
- Used PlanetLab for validation
- Focus: Energy-efficient resource management with dynamic workloads

### Our Approach
- **Static placement** at single time point
- **Sampling justified** by:
  1. Course project scope
  2. ILP computational limits
  3. Focus on algorithm comparison, not deployment simulation
- **Google Trace addition** provides industrial-scale validation missing in prior work

---

## Execution Instructions

### Run All Experiments
```bash
python experiments/run_all_experiments.py
```

**Output:**
- Real-time progress display
- Results saved to: `results/experiment_results_YYYYMMDD_HHMMSS.json`

### Run Individual Experiments
```python
from experiments.run_all_experiments import run_experiment_1, run_experiment_2, run_experiment_3, run_experiment_google

# Run specific experiment
results_exp1 = run_experiment_1()
results_exp4 = run_experiment_google()
```

### Visualize Results
```bash
python plot_results.py results/experiment_results_20251220_163000.json
```

---

## Timeline

| Week | Tasks |
|------|-------|
| **Week 5** | Download PlanetLab, implement dataset loaders, run Experiment 1 |
| **Week 6** | Run Experiments 2-3, initial analysis |
| **Week 7** | Integrate Google Trace, preprocess data, run Experiment 4 |
| **Week 8-9** | Analyze all results, create visualizations, write final report |

---

## System Requirements

- **Python**: 3.8+
- **Memory**: 8GB+ recommended for Experiment 4
- **Disk Space**: ~2GB for Google Trace raw data
- **Runtime**: ~15 minutes total for all experiments

---

## Troubleshooting

**Q: Experiment 4 fails with "FileNotFoundError"**
- Ensure Google dataset is preprocessed: `python src/utils/google_trace_to_dataset.py`
- Check files exist: `data/google_dataset/google_vms_10000.json`

**Q: ILP takes very long (>5 minutes)**
- This is expected for Experiment 1 if problem is complex
- ILP will return best solution found within 300s time limit

**Q: RLS-FFD results vary between runs**
- Expected due to randomness; use fixed seed for reproducibility
- Average results across multiple runs for statistical significance

---

## References

### Datasets
- **PlanetLab**: Beloglazov, A., & Buyya, R. (2012). *Optimal online deterministic algorithms and adaptive heuristics for energy and performance efficient dynamic consolidation of virtual machines in cloud data centers*. Concurrency and Computation: Practice and Experience, 24(13), 1397-1420.

- **Google Cluster Trace**: Reiss, C., Wilkes, J., & Hellerstein, J. L. (2011). *Google cluster-usage traces: format + schema*. Google Inc., Mountain View, CA, USA, Technical Report.

### Algorithms
- **FFD/BFD**: Johnson, D. S. (1973). *Near-optimal bin packing algorithms*. Doctoral Dissertation, MIT.
- **ILP for VM Placement**: Speitkamp, B., & Bichler, M. (2010). *A mathematical programming approach for server consolidation problems in virtualized data centers*. IEEE Transactions on Services Computing, 3(4), 266-278.
