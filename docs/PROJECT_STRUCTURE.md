# Project Structure

## Complete Directory Tree

```
vm-placement-project/
│
├── README.md                          # Main project documentation
├── PROJECT_STRUCTURE.md               # This file
├── GIT_SETUP.md                       # Git repository setup instructions
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── plot_results.py                    # Visualization script for experiment results
│
├── docs/                              # Documentation
│   ├── EXPERIMENTS.md                 # Detailed experimental design
│   └── literature_review.md           # Research literature review
│
├── src/                               # Source code
│   ├── algorithms/                    # VM placement algorithms
│   │   ├── __init__.py
│   │   ├── nlp_solver.py              # Integer Linear Programming (ILP) solver
│   │   ├── ffd.py                     # First Fit Decreasing heuristic
│   │   ├── bfd.py                     # Best Fit Decreasing heuristic
│   │   └── rls_ffd.py                 # Randomized Local Search with FFD
│   │
│   ├── utils/                         # Utility modules
│   │   ├── __init__.py
│   │   ├── vm_generator.py            # Synthetic VM instance generator
│   │   ├── pm_generator.py            # PM instance generator (homogeneous/heterogeneous)
│   │   ├── planetlab_loader.py        # PlanetLab dataset loader
│   │   └── google_trace_to_dataset.py # Google Trace preprocessor (CSV → JSON)
│   │
│   └── evaluation/                    # Evaluation and metrics
│       ├── __init__.py
│       └── metrics.py                 # Performance metrics calculation
│
├── data/                              # Datasets
│   ├── synthetic/                     # Synthetic problem instances
│   │   └── small_scale/
│   │       └── instance_01.json       # 25 VMs, 5 PMs (for Experiment 1)
│   │
│   ├── planetlab/                     # PlanetLab workload traces
│   │   ├── README.md                  # PlanetLab dataset documentation
│   │   └── 20110303/                  # March 3, 2011 traces
│   │       └── *.txt                  # 1,052 VM CPU utilization files
│   │
│   ├── google_raw/                    # Google Cluster Trace raw data (not in repo)
│   │   ├── task_usage/                # VM resource usage CSVs (gzipped)
│   │   │   └── part-00000-of-00500.csv.gz
│   │   └── machine_events/            # PM capacity data CSVs (gzipped)
│   │       └── machine_events.csv.gz
│   │
│   └── google_dataset/                # Processed Google Trace (JSON format)
│       ├── README.md                  # Google dataset documentation
│       ├── google_vms_10000.json      # 10,000 VMs (1.3 MB)
│       └── google_pms_2000.json       # 2,000 PMs (175 KB)
│
├── experiments/                       # Experiment scripts
│   ├── README.md                      # Experiment execution guide
│   └── run_all_experiments.py         # Main script to run all 4 experiments
│
└── results/                           # Experimental results (generated)
    └── experiment_results_*.json      # Results timestamped JSON files
```

---

## Module Descriptions

### Source Code (`src/`)

#### Algorithms (`src/algorithms/`)

All algorithm modules implement a common interface:
```python
class AlgorithmBase:
    def place(self, vms: List[dict], pms: List[dict]) -> dict:
        """
        Args:
            vms: List of VM dicts with keys: id, cpu_demand, memory_demand
            pms: List of PM dicts with keys: id, cpu_capacity, memory_capacity

        Returns:
            {
                'placement': {vm_id: pm_id},
                'success': True/False,
                'message': str
            }
        """
```

**`nlp_solver.py`** - Integer Linear Programming
- Uses PuLP library with CBC solver
- Provides provably optimal solutions for small instances (<50 VMs)
- Time limit: 300 seconds
- Returns best solution found if timeout occurs

**`ffd.py`** - First Fit Decreasing
- Greedy heuristic: Sort VMs descending, place each in first PM that fits
- Complexity: O(n log n + nm) where n=VMs, m=PMs
- Extremely fast: <1s for 10,000 VMs
- Robust across homogeneous and heterogeneous environments

**`bfd.py`** - Best Fit Decreasing
- Greedy heuristic: Sort VMs descending, place each in PM with minimum remaining capacity
- Complexity: O(n log n + nm)
- Works well in homogeneous environments
- **WARNING**: Fails in heterogeneous environments (see Experiment 4 results)

**`rls_ffd.py`** - Randomized Local Search with FFD
- Meta-heuristic: Start with FFD, iteratively improve via random swaps
- Parameters: `max_iterations` (default: 1000)
- Complexity: O(k × n × m) where k=iterations
- Typically 2-5% better than FFD, execution time <10s for 150 VMs

#### Utilities (`src/utils/`)

**`vm_generator.py`** - VM Instance Generator
- Generates synthetic VM workloads
- Supports uniform, normal, and custom distributions
- Configurable CPU/memory demand ranges
- Used in Experiment 1

**`pm_generator.py`** - PM Instance Generator
- Generates homogeneous or heterogeneous PM pools
- Heterogeneous types: Small (8/16), Medium (16/32), Large (32/64)
- Configurable capacity and energy model parameters
- Used in Experiments 1, 2, 3

**`planetlab_loader.py`** - PlanetLab Dataset Loader
- Loads CPU utilization traces from PlanetLab text files
- Supports random sampling with seed for reproducibility
- Applies stress test logic (CPU-heavy vs. memory-heavy VMs)
- Time point selection (0-287 for 24-hour period)
- Used in Experiments 2 & 3

**`google_trace_to_dataset.py`** - Google Trace Preprocessor
- Converts raw Google Trace CSV files to JSON datasets
- Processes `task_usage` (VM demands) and `machine_events` (PM capacities)
- Aggregates tasks by (job_id, task_index) to form VMs
- Applies peak demand strategy: max(cpu_rate), max(assigned_memory)
- Random sampling: 10,000 VMs from 170,000+ tasks, 2,000 PMs from 12,583 machines
- Configurable parameters: NUM_VMS, NUM_PMS, RANDOM_SEED
- Execution: `python src/utils/google_trace_to_dataset.py`

#### Evaluation (`src/evaluation/`)

**`metrics.py`** - Performance Metrics
- `evaluate_placement(placement, vms, pms)`: Calculates all metrics
- Metrics calculated:
  - **Active PMs**: Number of PMs with at least one VM
  - **Total Energy**: Sum of energy consumption across all active PMs
  - **CPU/Memory Utilization**: Average usage across active PMs
  - **Resource Balance**: Standard deviation of PM utilizations
  - **Feasibility Check**: Verifies no PM exceeds capacity

Energy Model (linear):
```python
energy = idle_power + (max_power - idle_power) * utilization
utilization = (cpu_used + memory_used) / (cpu_capacity + memory_capacity)
```

---

### Data Directories (`data/`)

#### `data/synthetic/`
- Small-scale problem instances for Experiment 1
- Generated using `vm_generator.py` and `pm_generator.py`
- Fixed seed (42) for reproducibility

#### `data/planetlab/`
- Clone of https://github.com/beloglazov/planetlab-workload-traces
- 1,052 VM traces from March 3, 2011
- Each file: 288 lines (24 hours, 5-min intervals), CPU utilization (0-100%)
- Setup: `cd data && git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab`

#### `data/google_raw/`
- **NOT included in repository** (too large: ~10 GB)
- Download from: https://github.com/google/cluster-data
- Required files:
  - `task_usage/part-00000-of-00500.csv.gz` (VM demands)
  - `machine_events/machine_events.csv.gz` (PM capacities)
- Place in `data/google_raw/` directory before preprocessing

#### `data/google_dataset/`
- **Included in repository** (preprocessed, manageable size)
- Generated by `src/utils/google_trace_to_dataset.py`
- `google_vms_10000.json`: 10,000 VMs with peak CPU/memory demands
- `google_pms_2000.json`: 2,000 real heterogeneous PMs
- Random sampling seed: 42 (reproducible)

---

### Experiments (`experiments/`)

**`run_all_experiments.py`** - Main Experiment Runner

Runs four experiments sequentially:

1. **Experiment 1**: ILP Baseline (25 VMs, 5 PMs, synthetic)
   - Algorithms: ILP, FFD, BFD, RLS-FFD
   - Purpose: Establish optimal baseline

2. **Experiment 2**: Real Workload Stress Test (80 VMs, 60 PMs, PlanetLab)
   - Algorithms: FFD, BFD, RLS-FFD
   - Applies stress test logic (resource skewness)
   - RLS iterations: 2,000

3. **Experiment 3**: Scalability Test (150 VMs, 100 PMs, PlanetLab)
   - Algorithms: FFD, BFD, RLS-FFD
   - Applies stress test logic
   - RLS iterations: 2,000

4. **Experiment 4**: Google Trace (10,000 VMs, 2,000 PMs)
   - Algorithms: FFD, BFD, RLS-FFD
   - Real heterogeneous PMs
   - RLS iterations: 3,000

**Output Format**:
```json
{
  "experiment_1": {
    "ILP": {"active_pms": 4, "energy": 1200.5, "cpu_util": 75.2, "time": 45.3},
    "FFD": {"active_pms": 5, "energy": 1350.8, "cpu_util": 68.5, "time": 0.002, "gap": 25.0}
  },
  "experiment_2": { ... },
  "experiment_3": { ... },
  "experiment_4_google": { ... }
}
```

---

### Results (`results/`)

- **Generated automatically** when running experiments
- Filenames: `experiment_results_YYYYMMDD_HHMMSS.json`
- Contains complete metrics for all experiments
- Can be visualized using `plot_results.py`

---

## Usage Examples

### Running Experiments

```bash
# Run all 4 experiments
python experiments/run_all_experiments.py

# Output will be saved to results/
```

### Preprocessing Google Trace

```bash
# First-time setup: Convert raw CSV to JSON
python src/utils/google_trace_to_dataset.py

# This generates:
#   data/google_dataset/google_vms_10000.json
#   data/google_dataset/google_pms_2000.json
```

### Visualizing Results

```bash
python plot_results.py results/experiment_results_20251220_163000.json
```

---

## Development Workflow

### 1. Adding a New Algorithm

1. Create file in `src/algorithms/` (e.g., `genetic_algorithm.py`)
2. Implement `place(vms, pms)` method following the interface
3. Add import to `src/algorithms/__init__.py`
4. Add algorithm to `run_all_experiments.py`:
   ```python
   from src.algorithms.genetic_algorithm import GeneticAlgorithm

   algorithms = {
       "GA": GeneticAlgorithm(),
       ...
   }
   ```

### 2. Adding a New Metric

1. Add function to `src/evaluation/metrics.py`
2. Update `evaluate_placement()` to include new metric
3. Update experiment scripts to display new metric

### 3. Adding a New Dataset

1. Create loader in `src/utils/` (e.g., `bitbrains_loader.py`)
2. Implement loading logic following PlanetLab/Google examples
3. Add dataset directory under `data/`
4. Update `run_all_experiments.py` to include new experiment

---

## Key Files

### Configuration Files

**`requirements.txt`**
```
numpy>=1.21.0
pandas>=1.3.0
pulp>=2.5.1
matplotlib>=3.4.0
```

**`.gitignore`**
- Python cache: `__pycache__/`, `*.pyc`
- Virtual environments: `venv/`, `env/`
- Large data files: `data/google_raw/`
- Temporary results: `results/*.json` (except selected final results)

---

## File Sizes

| Directory/File | Size | Notes |
|----------------|------|-------|
| `data/planetlab/` | ~50 MB | Include in repo |
| `data/google_raw/` | ~10 GB | **Exclude** from repo |
| `data/google_dataset/` | ~1.5 MB | Include in repo (preprocessed) |
| `src/` | ~50 KB | All source code |
| `docs/` | ~100 KB | Documentation |

---

## Extension Points

### Multi-objective Optimization
- Modify `src/evaluation/metrics.py` to support Pareto front calculation
- Implement NSGA-II or similar in `src/algorithms/`

### Dynamic VM Placement
- Extend algorithms to support VM migration
- Add time-series workload simulation
- Track migration cost metrics

### Network-aware Placement
- Add network topology data structures
- Implement bandwidth-aware placement algorithms
- Include communication cost in objective function

---

For detailed experimental design, see `docs/EXPERIMENTS.md`.
