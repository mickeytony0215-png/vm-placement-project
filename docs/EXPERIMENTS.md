# Experimental Design

## Overview

This document describes the experimental design for evaluating VM placement algorithms. The experiments compare four algorithms (ILP, FFD, BFD, RLS-FFD) across different problem scales using both synthetic and real-world workload data.

## Dataset

### PlanetLab Workload Traces

**Source**: https://github.com/beloglazov/planetlab-workload-traces

**Dataset Structure**:
- Date: 20110303 (March 3, 2011)
- Total VMs: 1052 VM traces
- Time Points: 288 per VM (24 hours × 12 samples/hour)
- Sampling Interval: 5 minutes
- Data Format: Plain text, one CPU utilization value per line (0-100%)

**Our Sampling Strategy**:
We use random sampling from the 1052 available VMs because:
1. ILP solver cannot handle 1052 VMs (computational limit)
2. Course project scope requires manageable scale
3. Random sampling maintains statistical representativeness
4. VM type distribution (60% Small, 30% Medium, 10% Large) is preserved

### VM Classification

VMs are automatically classified based on CPU utilization:

| Type | CPU Range | RAM Calculation | Typical Use Case | Expected % |
|------|-----------|-----------------|------------------|------------|
| Small | 0-30% | CPU × 0.5 | Web servers, caching | ~60% |
| Medium | 30-60% | CPU × 0.7 | Databases, app servers | ~30% |
| Large | 60-100% | CPU × 1.0 | Big data, ML training | ~10% |

**Rationale**: Larger VMs typically require more memory relative to CPU, reflecting real-world patterns where compute-intensive workloads also demand higher memory.

## Physical Machine Configuration

All PMs use identical specifications (homogeneous setup) to simplify analysis:

```
CPU Capacity:    100 units (normalized)
RAM Capacity:    100 GB (normalized)
Storage:         1000 GB
Idle Power:      100 W
Max Power:       300 W
```

**Energy Model**: Linear model
```
E = P_idle + (P_max - P_idle) × U_avg
where U_avg = (CPU_utilization + RAM_utilization) / 2
```

## Three Experiments

### Experiment 1: ILP Baseline (Small Scale)

**Objective**: Establish optimal solution baseline for comparison

**Configuration**:
- VMs: 25 (synthetic data)
- PMs: 5
- Dataset: Synthetic workload with controlled distribution
- Algorithms: ILP, FFD, BFD, RLS-FFD

**Why Synthetic Data?**
- ILP requires small problem size (< 50 VMs)
- Need controlled environment to verify algorithm correctness
- Establish true optimal solution for gap calculation

**Expected Outcomes**:
- ILP finds optimal solution in < 60 seconds
- FFD within 5-15% of optimal
- Demonstrate ILP computational limits

**Key Metric**: Optimality Gap = (FFD_PMs - ILP_PMs) / ILP_PMs × 100%

---

### Experiment 2: Real Workload (Medium Scale)

**Objective**: Evaluate algorithms on real-world data

**Configuration**:
- VMs: 80 (from PlanetLab 20110303)
- PMs: 15
- Dataset: PlanetLab midday snapshot (12:00, time_point=144)
- Algorithms: FFD, BFD, RLS-FFD (ILP excluded - too large)

**Why This Scale?**
- Represents realistic department/small datacenter
- PlanetLab data provides authentic workload patterns
- Large enough to show algorithm differences
- Small enough for course project feasibility

**VM Distribution** (expected):
- Small VMs: ~48 (60%)
- Medium VMs: ~24 (30%)
- Large VMs: ~8 (10%)

**Expected Outcomes**:
- RLS-FFD outperforms FFD/BFD by 5-10%
- Execution time: FFD < 0.01s, BFD < 0.01s, RLS-FFD ~0.1s
- All algorithms achieve >60% CPU utilization

---

### Experiment 3: Scalability Test (Large Scale)

**Objective**: Test algorithm performance at larger scale

**Configuration**:
- VMs: 150 (from PlanetLab 20110303)
- PMs: 30
- Dataset: PlanetLab midday snapshot
- Algorithms: FFD, BFD, RLS-FFD

**Why This Scale?**
- Tests scalability compared to Experiment 2
- Still manageable for course project
- Demonstrates algorithm efficiency differences

**Expected Outcomes**:
- RLS-FFD continues to outperform
- Execution time increases but remains reasonable
- Quality gap between algorithms becomes clearer

---

## Evaluation Metrics

### Primary Metrics

1. **Active PMs** (lower is better)
   - Primary optimization objective
   - Directly impacts energy consumption
   - Target: Minimize while maintaining >30% utilization

2. **Total Energy Consumption** (kWh, lower is better)
   - Calculated using linear energy model
   - Reflects real operational cost

3. **Average CPU Utilization** (%)
   - Target range: 60-80%
   - Too low: wasted resources
   - Too high: SLA violation risk

4. **Execution Time** (seconds)
   - Algorithm efficiency measure
   - Important for real-time placement decisions

5. **Optimality Gap** (%, Experiment 1 only)
   - Gap = (Heuristic_PMs - Optimal_PMs) / Optimal_PMs × 100%
   - Measures solution quality

### Secondary Metrics

- Average RAM Utilization
- Placement Rate (% of VMs successfully placed)

## Expected Results Summary

| Experiment | Scale | Best Algorithm | Key Finding |
|------------|-------|----------------|-------------|
| Exp 1 | 25 VMs | ILP (optimal) | FFD within 5-15% of optimal |
| Exp 2 | 80 VMs | RLS-FFD | 5-10% better than FFD/BFD |
| Exp 3 | 150 VMs | RLS-FFD | Maintains advantage at scale |

## References to Literature

Our experimental design follows established practices:

- **CloudBench (2018)**: Used full 1052 VMs, 41-50 PMs for dynamic consolidation
- **Beloglazov et al. (2012)**: Used PlanetLab for algorithm validation
- **Our Approach**: Static placement with sampling - appropriate for course project

**Key Difference**: Literature focuses on dynamic VM migration over 24 hours. We focus on static placement at single time point, which justifies our sampling approach.

## Execution Instructions

```bash
# Run all experiments
python experiments/run_all_experiments.py

# Results will be saved to:
# results/experiment_results_YYYYMMDD_HHMMSS.json
```

## Timeline

- **Week 5**: Download PlanetLab, run Experiment 1
- **Week 6**: Run Experiments 2-3
- **Week 7**: Analyze results, create visualizations
- **Week 8-9**: Write report, prepare presentation