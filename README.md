# Virtual Machine Placement Problem (VM-PP)

## Project Overview

This project addresses the Virtual Machine Placement (VMP) problem in cloud computing environments. The VMP problem involves efficiently assigning Virtual Machines (VMs) to Physical Machines (PMs) while minimizing energy consumption, reducing the number of active servers, and maintaining service quality.

The project implements and evaluates **four VM placement algorithms** using both **academic benchmarks (PlanetLab)** and **industrial-scale datasets (Google Cluster Trace 2011)**, enabling comprehensive performance analysis from small-scale optimal solutions to large-scale stress testing with 10,000 VMs.

## Background

Cloud computing architectures rely on virtualization technology to provide flexible and scalable computing resources. The core challenge is to effectively place and manage VMs within the constraints of a limited number of PMs while:
- Minimizing energy consumption and operational costs
- Avoiding performance degradation and resource overutilization
- Handling heterogeneous resource demands (CPU-heavy vs. memory-heavy workloads)
- Scaling to thousands of VMs in real-world data centers

## Problem Definition

**Given:**
- A set of Virtual Machines (VMs), where each VM has specific resource requirements (CPU, memory)
- A set of Physical Machines (PMs), where each PM has fixed resource capacities that cannot be exceeded
- System objectives and constraints including energy consumption, resource utilization, and SLA requirements

**Goal:**
Determine a mapping f: V → P, assigning each virtual machine to exactly one physical machine, such that all resource and performance constraints are satisfied.

**Objectives:**
- **Primary**: Minimize the number of active physical machines
- Minimize overall energy consumption and operational cost
- Maximize resource utilization while avoiding overload (target: 60-80% CPU)
- Handle heterogeneous PM configurations (different CPU/memory ratios)
- Ensure feasibility (no PM exceeds capacity constraints)

## Why is this Problem NP-hard?

The VMP problem is a variant of the **Multi-dimensional Bin Packing Problem**, which is NP-hard.

The complexity arises from:
1. **Combinatorial Explosion**: With n VMs and m PMs, there are m^n possible mappings
2. **Multi-dimensional Constraints**: Each VM requires (CPU, memory), and both must fit simultaneously
3. **Heterogeneous Resources**: Real-world PMs have different CPU/memory ratios, creating resource fragmentation
4. **No Polynomial-time Solution**: No algorithm can guarantee optimal solutions for large instances in polynomial time

## Project Structure

```
vm-placement-project/
├── README.md                          # Project overview
├── requirements.txt                   # Python dependencies
├── plot_results.py                    # Visualization script
│
├── docs/                             # Documentation
│   ├── EXPERIMENTS.md                # Experimental design
│   └── literature_review.md          # Research background
│
├── src/                              # Source code
│   ├── algorithms/                   # Placement algorithms
│   │   ├── nlp_solver.py            # Integer Linear Programming (ILP)
│   │   ├── ffd.py                   # First Fit Decreasing
│   │   ├── bfd.py                   # Best Fit Decreasing
│   │   └── rls_ffd.py               # Randomized Local Search FFD
│   │
│   ├── utils/                        # Utility modules
│   │   ├── vm_generator.py          # Synthetic VM generator
│   │   ├── pm_generator.py          # PM generator
│   │   ├── planetlab_loader.py      # PlanetLab dataset loader
│   │   └── google_trace_to_dataset.py  # Google Trace preprocessor
│   │
│   └── evaluation/                   # Evaluation metrics
│       └── metrics.py               # Performance calculation
│
├── data/                             # Datasets
│   ├── synthetic/                   # Synthetic instances
│   ├── planetlab/                   # PlanetLab workload traces
│   ├── google_raw/                  # Google Trace raw data (CSV)
│   └── google_dataset/              # Processed Google dataset (JSON)
│       ├── google_vms_10000.json   # 10,000 VMs
│       └── google_pms_2000.json    # 2,000 PMs
│
├── experiments/                      # Experiment scripts
│   └── run_all_experiments.py       # Run all 4 experiments
│
└── results/                          # Output directory
    └── experiment_results_*.json    # Experimental results
```

## Algorithms

This project implements and compares **four VM placement algorithms**:

### 1. Integer Linear Programming (ILP)
- **Type**: Exact optimization (finds provably optimal solutions)
- **Tool**: PuLP with CBC solver
- **Use Case**: Small-scale problems (<50 VMs) to establish optimal baseline
- **Performance**: Time limit 300s; guaranteed optimal if solved

### 2. First Fit Decreasing (FFD)
- **Type**: Greedy heuristic
- **Strategy**: Sort VMs by resource demand (descending), place each in the first PM that fits
- **Advantages**: Extremely fast (<1s for 10,000 VMs), simple implementation
- **Disadvantages**: May leave resource fragmentation

### 3. Best Fit Decreasing (BFD)
- **Type**: Greedy heuristic
- **Strategy**: Sort VMs by demand, place each in the PM with minimum remaining capacity that fits
- **Advantages**: Reduces fragmentation in homogeneous environments
- **Disadvantages**: **Fails in heterogeneous environments** (shown in Experiment 4)

### 4. Randomized Local Search with FFD (RLS-FFD)
- **Type**: Meta-heuristic
- **Strategy**: Start with FFD solution, iteratively improve via random swaps/moves
- **Advantages**: Escapes local optima, consistently outperforms greedy methods
- **Performance**: Typically 2-5% better than FFD, execution time <10s for 150 VMs

## Experimental Design

The project includes **four experiments** with increasing scale and complexity:

| Experiment | VMs | PMs | Dataset | Algorithms | Purpose |
|------------|-----|-----|---------|------------|---------|
| **Exp 1** | 25 | 5 | Synthetic | ILP, FFD, BFD, RLS-FFD | Establish optimal baseline |
| **Exp 2** | 80 | 60 | PlanetLab + Stress | **ILP (20s limit)**, FFD, BFD, RLS-FFD | **Prove ILP infeasibility** + stress test |
| **Exp 3** | 150 | 100 | PlanetLab + Stress | FFD, BFD, RLS-FFD | Scalability test |
| **Exp 4** | 10,000 | 2,000 | Google Trace 2011 | FFD, BFD, RLS-FFD | Industrial-scale validation |

### Key Features:
- **Experiment 1**: Uses ILP to find provably optimal solutions for gap analysis (25 VMs)
- **Experiment 2**: **Demonstrates ILP timeout** at 80 VMs (20s limit) - proves heuristics are necessary
- **Experiment 3**: Scalability testing with stress test logic (150 VMs, ILP excluded)
- **Experiment 4**: Uses real Google Cluster Trace with 12,583 machines and heterogeneous PM capacities

### Datasets

#### 1. PlanetLab Workload Traces
- **Source**: 1,052 VM CPU utilization traces (March 3, 2011)
- **Sampling**: 288 time points per VM (24 hours, 5-minute intervals)
- **Usage**: Experiments 2 & 3
- **Limitation**: No real PM capacity data (homogeneous PMs assumed)

#### 2. Google Cluster Trace 2011
- **Source**: Google Borg system production traces
- **Scale**: 12,583 real machines, 170,000+ tasks
- **Usage**: Experiment 4 (10,000 VMs, 2,000 PMs randomly sampled)
- **Advantages**:
  - Real heterogeneous PM configurations (CPU/memory ratios vary)
  - Peak demand strategy (max CPU/memory usage)
  - Industrial-scale validation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/vm-placement-project.git
cd vm-placement-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dataset Setup

**PlanetLab Dataset** (for Experiments 2 & 3):
```bash
cd data
git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab
cd ..
```

**Google Cluster Trace** (for Experiment 4):
1. Download from [Google Cluster Data](https://github.com/google/cluster-data)
2. Extract `task_usage` and `machine_events` CSV files
3. Place in `data/google_raw/` directory
4. Run preprocessing:
   ```bash
   python src/utils/google_trace_to_dataset.py
   ```

## Usage

### Run All Experiments
```bash
python experiments/run_all_experiments.py
```

This will:
1. Run all 4 experiments sequentially
2. Display real-time progress and results
3. Save results to `results/experiment_results_YYYYMMDD_HHMMSS.json`

### Visualize Results
```bash
python plot_results.py results/experiment_results_YYYYMMDD_HHMMSS.json
```

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Active PMs** | Number of physical machines used | Minimize |
| **Total Energy** | Energy consumption (kWh) | Minimize |
| **CPU Utilization** | Average CPU usage across active PMs | 60-80% |
| **Memory Utilization** | Average memory usage | 60-80% |
| **Execution Time** | Algorithm runtime (seconds) | <10s for heuristics |
| **Optimality Gap** | (Heuristic - Optimal) / Optimal × 100% | <15% |

## Key Results

### Experiment 4: Google Trace (10,000 VMs, 2,000 PMs)

| Algorithm | Active PMs | CPU Util | Energy (kWh) | Time (s) |
|-----------|-----------|----------|--------------|----------|
| **FFD** | **836** | **92.35%** | **223,517** | **0.76** |
| BFD | 993 (+18.8%) | 83.52% | 269,930 | 9.38 |
| **RLS-FFD** | **836** | **92.35%** | **223,517** | 3.46 |

**Key Finding**: BFD fails in heterogeneous environments, using **157 more PMs** than FFD/RLS-FFD due to resource fragmentation when CPU/memory ratios vary across PMs.

## Project Timeline

| Week | Stage | Tasks |
|------|-------|-------|
| 1-2 (10/22-11/2) | Literature Review | Problem formulation, dataset selection |
| 3-4 (11/3-11/16) | Algorithm Implementation | ILP, FFD, BFD, RLS-FFD |
| 5-7 (11/17-12/7) | Experiments 1-3 | PlanetLab-based testing |
| 8-9 (12/8-12/21) | Google Trace Integration | Experiment 4, final analysis |

## License

This project is for academic purposes only.

## References

### Datasets
- **PlanetLab**: [planetlab-workload-traces](https://github.com/beloglazov/planetlab-workload-traces)
- **Google Cluster Trace**: [cluster-data](https://github.com/google/cluster-data)

### Literature
- See `docs/literature_review.md` for detailed references
- Beloglazov et al. (2012): Energy-efficient resource management
- Google Borg System: Large-scale cluster management

## Contributing

This is an academic course project. For questions or collaboration, please open an issue.
