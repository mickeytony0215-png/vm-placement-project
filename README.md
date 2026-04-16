# Virtual Machine Placement Problem (VM-PP)

Solving the Virtual Machine Placement problem in cloud computing using exact optimization and heuristic algorithms. This project evaluates **four placement algorithms** across **four experiments** — from small-scale optimal baselines (25 VMs) to industrial-scale stress tests (10,000 VMs) using real Google Cluster Trace data.

## Algorithms

| Algorithm | Type | Strategy | Scalability |
|-----------|------|----------|-------------|
| **ILP** | Exact (PuLP/CBC) | Integer Linear Programming | < 50 VMs |
| **FFD** | Greedy heuristic | First Fit Decreasing | 10,000+ VMs |
| **BFD** | Greedy heuristic | Best Fit Decreasing | 10,000+ VMs |
| **RLS-FFD** | Meta-heuristic | Randomized Local Search + FFD | ~1,000 VMs |

## Experiments

| # | Scale | Dataset | Algorithms | Purpose |
|---|-------|---------|------------|---------|
| 1 | 25 VMs / 5 PMs | Synthetic | ILP, FFD, BFD, RLS-FFD | Optimal baseline |
| 2 | 80 VMs / 60 PMs | PlanetLab | FFD, BFD, RLS-FFD | Real workload + stress test |
| 3 | 150 VMs / 100 PMs | PlanetLab | FFD, BFD, RLS-FFD | Scalability test |
| 4 | 10,000 VMs / 2,000 PMs | Google Trace 2011 | FFD, BFD, RLS-FFD | Industrial-scale validation |

### Key Result (Experiment 4)

| Algorithm | Active PMs | CPU Utilization | Energy (kWh) | Time |
|-----------|-----------|-----------------|--------------|------|
| **FFD** | **836** | **92.35%** | **223,517** | **0.76s** |
| BFD | 993 (+18.8%) | 83.52% | 269,930 | 9.38s |
| RLS-FFD | 836 | 92.35% | 223,517 | 3.46s |

**Finding**: BFD fails in heterogeneous PM environments — its "minimum remaining capacity" strategy causes severe resource fragmentation when CPU/memory ratios vary across PMs.

## Project Structure

```
vm-placement-project/
├── src/                              # Source code
│   ├── algorithms/                   # Placement algorithms
│   │   ├── nlp_solver.py             #   ILP solver (PuLP/CBC)
│   │   ├── ffd.py                    #   First Fit Decreasing
│   │   ├── bfd.py                    #   Best Fit Decreasing
│   │   └── rls_ffd.py                #   Randomized Local Search + FFD
│   ├── evaluation/
│   │   └── metrics.py                #   Performance metrics
│   └── utils/
│       ├── vm_generator.py           #   Synthetic VM generator
│       ├── pm_generator.py           #   PM generator
│       ├── planetlab_loader.py       #   PlanetLab dataset loader
│       └── google_trace_to_dataset.py #  Google Trace preprocessor
│
├── data/
│   ├── synthetic/                    # Synthetic problem instances
│   ├── planetlab/                    # PlanetLab workload traces (git submodule)
│   └── google_dataset/               # Preprocessed Google Trace (JSON)
│
├── experiments/
│   └── run_all_experiments.py        # Run all 4 experiments
│
├── scripts/
│   ├── example.py                    # Quick demo script
│   └── plot_results.py               # Result visualization
│
├── results/                          # Experiment outputs (JSON)
├── tests/                            # Unit tests
└── docs/                             # Documentation
    ├── EXPERIMENTS.md                #   Detailed experimental design
    ├── PROJECT_STATUS.md             #   Project status & findings
    ├── PROJECT_STRUCTURE.md          #   Module descriptions
    └── literature_review.md          #   Research background
```

## Quick Start

```bash
# Clone and setup
git clone https://github.com/mickeytony0215-png/vm-placement-project.git
cd vm-placement-project
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download PlanetLab dataset (for Experiments 2 & 3)
cd data && git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab && cd ..

# Run all experiments
python experiments/run_all_experiments.py

# Visualize results
python scripts/plot_results.py
```

## Datasets

- **Synthetic** — controlled small-scale instances for ILP baseline (Exp 1)
- **[PlanetLab](https://github.com/beloglazov/planetlab-workload-traces)** — 1,052 real VM CPU traces, March 3, 2011 (Exp 2 & 3)
- **[Google Cluster Trace 2011](https://github.com/google/cluster-data)** — 12,583 real machines, 170,000+ tasks from Google Borg (Exp 4)

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Active PMs | Number of physical machines used | Minimize |
| Total Energy | Energy consumption (kWh) | Minimize |
| CPU Utilization | Average CPU usage across active PMs | 60-80% |
| Optimality Gap | (Heuristic - Optimal) / Optimal | < 15% |
| Execution Time | Algorithm runtime | < 10s for heuristics |

## Requirements

- Python 3.8+
- numpy, pandas, pulp, matplotlib

## License

Academic use only.

## References

- Beloglazov, A., & Buyya, R. (2012). Optimal online deterministic algorithms and adaptive heuristics for energy and performance efficient dynamic consolidation of virtual machines in cloud data centers.
- Google Cluster Data: https://github.com/google/cluster-data
- PlanetLab Traces: https://github.com/beloglazov/planetlab-workload-traces
