# Virtual Machine Placement Problem (VM-PP)

## Project Overview

This project addresses the Virtual Machine Placement (VMP) problem in cloud computing environments. The VMP problem involves efficiently assigning Virtual Machines (VMs) to Physical Machines (PMs) while minimizing energy consumption, reducing the number of active servers, and maintaining service quality.

## Background

Cloud computing architectures rely on virtualization technology to provide flexible and scalable computing resources. The core challenge is to effectively place and manage VMs within the constraints of a limited number of PMs while avoiding performance degradation and resource overutilization.

## Problem Definition

**Given:**
- A set of Virtual Machines (VMs), where each VM has specific resource requirements (CPU cores, memory, storage capacity)
- A set of Physical Machines (PMs), where each PM has fixed resource capacities that cannot be exceeded
- System objectives and constraints including energy consumption, operational cost, SLA, communication latency, and network usage

**Goal:**
Determine a mapping f: V → P, assigning each virtual machine to exactly one physical machine, such that all resource and performance constraints are satisfied.

**Objectives:**
- Minimize the number of active physical machines
- Minimize overall energy consumption or operational cost
- Maximize resource utilization and load balance
- Ensure no PM is overloaded while satisfying all VM resource demands
- Optimize network traffic and reduce bandwidth bottlenecks
- Avoid unnecessary VM migrations to minimize reallocation overhead

## Why is this Problem NP-hard?

The VMP problem is closely related to several classic NP-hard optimization problems:
- Multi-dimensional Bin Packing Problem
- Multiple Knapsack Problem
- Task Scheduling Problem

The complexity arises from:
1. **Combinatorial Explosion**: With n VMs and m PMs, there are approximately m^n possible mappings
2. **Complex Resource Constraints**: Vector-valued VM demands (CPU, memory, storage, bandwidth) impose multi-dimensional constraints
3. **Multi-objective Decision Space**: Multiple conflicting objectives increase problem complexity
4. **Lack of Polynomial-time Algorithms**: No known polynomial-time algorithm can guarantee optimal solutions for large instances

## Project Structure

```
vm-placement-project/
├── README.md
├── docs/
│   ├── proposal.pdf
│   ├── literature_review.md
│   └── final_report.md
├── src/
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── nlp_solver.py
│   │   ├── ffd.py
│   │   ├── bfd.py
│   │   └── rls_ffd.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── vm_generator.py
│   │   └── pm_generator.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   └── metrics.py
│   └── main.py
├── data/
│   ├── small_scale/
│   └── medium_scale/
├── results/
│   ├── plots/
│   └── logs/
├── tests/
│   └── test_algorithms.py
├── requirements.txt
└── .gitignore
```

## Algorithms

This project implements and compares four algorithms:

1. **Nonlinear Programming (NLP)**: Optimal solutions for small-scale problems
2. **First Fit Decreasing (FFD)**: Greedy heuristic algorithm
3. **Best Fit Decreasing (BFD)**: Improved greedy heuristic
4. **Randomized Local Search with FFD Initialization (RLS-FFD)**: Meta-heuristic approach

## Project Timeline

| Week | Stage | Tasks |
|------|-------|-------|
| 1-2 (10/22-11/2) | Stage 1 | Literature Review, Resource Configuration, Metrics Definition |
| 3-4 (11/3-11/16) | Stage 2 | Algorithm Design and Implementation (NLP, FFD, BFD, RLS-FFD) |
| 5-7 (11/17-12/7) | Stage 3 | Experimental Evaluation (Small/Medium Scale Testing) |
| 8-9 (12/8-12/21) | Stage 4 | Results Analysis and Documentation |

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

## Usage

```bash
# Run the main program
python src/main.py

# Run specific algorithm
python src/main.py --algorithm ffd --scale small

# Run all experiments
python src/main.py --run-all
```

## Evaluation Metrics

- Number of active PMs
- Total energy consumption
- Resource utilization rate
- VM migration count
- SLA violation rate
- Algorithm execution time

## Results

Results will be documented in the `results/` directory, including:
- Performance comparison plots
- Detailed logs
- Statistical analysis

## Contributing

This is an academic project. Team members should follow the branching strategy and commit message conventions outlined in `docs/contributing.md`.

## Team Members

- All members participate in all stages
- Specific algorithm implementations assigned in Stage 2

## License

This project is for academic purposes only.

## References

- Literature review and references will be documented in `docs/literature_review.md`
- Related papers on VM placement algorithms
- Cloud computing datasets (PlanetLab, Google Cluster, Bitbrains)

## Contact

For questions or issues, please open an issue in the GitHub repository.
