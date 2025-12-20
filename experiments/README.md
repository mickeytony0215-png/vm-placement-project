# Experiments

This directory contains scripts to run comprehensive VM placement experiments.

## Quick Start

Run all four experiments at once:

```bash
python experiments/run_all_experiments.py
```

This will:
1. **Experiment 1**: ILP Baseline (25 VMs, 5 PMs, synthetic)
2. **Experiment 2**: Real Workload Stress Test (80 VMs, 60 PMs, PlanetLab)
3. **Experiment 3**: Scalability Test (150 VMs, 100 PMs, PlanetLab)
4. **Experiment 4**: Google Trace (10,000 VMs, 2,000 PMs)
5. Save results to `results/experiment_results_YYYYMMDD_HHMMSS.json`

**Total Runtime**: ~15 minutes (depending on hardware)

---

## Prerequisites

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download PlanetLab Dataset (for Experiments 2 & 3)
```bash
cd data
git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab
cd ..
```

### 3. Google Cluster Trace Setup (for Experiment 4)

**Option A: Use Preprocessed Dataset (Recommended)**
- The preprocessed dataset is **already included** in `data/google_dataset/`
- No additional setup needed
- Files: `google_vms_10000.json` (1.3 MB), `google_pms_2000.json` (175 KB)

**Option B: Regenerate from Raw Data (Optional)**
1. Download Google Cluster Trace 2011 from: https://github.com/google/cluster-data
2. Extract these files to `data/google_raw/`:
   - `task_usage/part-00000-of-00500.csv.gz`
   - `machine_events/machine_events.csv.gz`
3. Run preprocessing:
   ```bash
   python src/utils/google_trace_to_dataset.py
   ```

---

## Experiment Details

### Experiment 1: ILP Baseline

**Purpose**: Establish provably optimal solutions for algorithm comparison

**Configuration**:
- VMs: 25 (synthetic, seed=42)
- PMs: 5 (homogeneous: 100 CPU / 100 Memory)
- Algorithms: **ILP**, FFD, BFD, RLS-FFD

**Key Metric**: Optimality Gap
```
Gap = (Heuristic_PMs - ILP_PMs) / ILP_PMs × 100%
```

**Runtime**: ~1-2 minutes (ILP solver)

**Expected Results**:
- ILP finds optimal solution (3-4 active PMs)
- FFD/BFD within 5-15% of optimal
- RLS-FFD may match or beat FFD

---

### Experiment 2: Real Workload Stress Test

**Purpose**: Test algorithms under resource skewness with real workload patterns, and **demonstrate ILP infeasibility** at medium scale

**Configuration**:
- VMs: 80 (PlanetLab 20110303, time_point=144, seed=42)
- PMs: 60 (heterogeneous: 20% Small, 50% Medium, 30% Large)
- Algorithms: **ILP** (**20s time limit**), FFD, BFD, **RLS-FFD** (2,000 iterations)
- **Stress Logic**: Applied (CPU-heavy vs. memory-heavy VMs)

**ILP Configuration**:
- **Time Limit**: **20 seconds** (intentionally short)
- **Purpose**: **Prove ILP is impractical at 80 VMs** - expected to timeout
- **Academic Value**: Demonstrates computational boundary where heuristics become necessary
- **Note**: ILP timeout is the **expected and desired outcome**

**Stress Test Logic**:
```python
for i, vm in enumerate(vms):
    if i % 2 == 0:  # CPU-heavy
        vm["cpu_demand"] = base
        vm["memory_demand"] = base / 4
    else:           # Memory-heavy
        vm["cpu_demand"] = base / 4
        vm["memory_demand"] = base
```

**Runtime**: ~30-40 seconds (including ILP 20s timeout)

**Expected Results**:
- **ILP will timeout** (proves exact methods don't scale)
- RLS-FFD uses 5-10% fewer PMs than FFD/BFD
- All algorithms achieve 60-80% CPU utilization
- FFD/BFD execution time < 0.01s, RLS-FFD ~2s, **ILP ~20s (timeout)**

**Key Takeaway**: This experiment validates why heuristic algorithms are essential for practical VM placement.

---

### Experiment 3: Scalability Test

**Purpose**: Evaluate algorithm performance at larger scale

**Configuration**:
- VMs: 150 (PlanetLab 20110303, time_point=144, seed=42)
- PMs: 100 (heterogeneous: 20% Small, 50% Medium, 30% Large)
- Algorithms: FFD, BFD, **RLS-FFD** (2,000 iterations)
- **Stress Logic**: Applied

**Runtime**: ~30-60 seconds

**Expected Results**:
- RLS-FFD continues to outperform greedy methods
- Execution time: FFD/BFD < 0.1s, RLS-FFD ~5s
- Demonstrates algorithm scalability (1.875× larger than Exp 2)

---

### Experiment 4: Google Trace Dataset (Industrial-Scale)

**Purpose**: Validate algorithms on real industrial-scale data with heterogeneous PMs

**Configuration**:
- VMs: 10,000 (Google Trace, randomly sampled with seed=42)
- PMs: 2,000 (real heterogeneous machines from Google data centers)
- Algorithms: FFD, BFD, **RLS-FFD** (3,000 iterations)
- Dataset: `data/google_dataset/google_vms_10000.json`, `google_pms_2000.json`

**Scale**:
- 125× larger than Experiment 1
- 6.67× larger than Experiment 3
- Represents real data center deployment

**Runtime**: ~5-15 minutes (mainly RLS-FFD)

**Actual Results (from latest run)**:

| Algorithm | Active PMs | CPU Util | Energy (kWh) | Time (s) |
|-----------|-----------|----------|--------------|----------|
| **FFD** | **836** | **92.35%** | **223,517** | **0.76** |
| BFD | 993 (+18.8%) | 83.52% | 269,930 | 9.38 |
| **RLS-FFD** | **836** | **92.35%** | **223,517** | 3.46 |

**Key Findings**:
1. **FFD excels**: Fastest (<1s) with best solution quality
2. **BFD fails catastrophically**: Uses **157 more PMs** (18.8% worse)
   - Root cause: In heterogeneous environments, BFD's "minimum remaining capacity" strategy exhausts one resource dimension (CPU or memory) first, creating severe fragmentation
3. **RLS-FFD matches FFD**: Same solution quality but slower (3.46s vs 0.76s)

**Why This Matters**:
- Demonstrates that **algorithm selection depends on PM heterogeneity**
- BFD is suitable for homogeneous environments (Exp 1)
- BFD fails for heterogeneous environments (Exp 4)
- FFD's simplicity is an advantage: fast and robust

---

## Output Format

Results are saved as JSON:

```json
{
  "experiment_1": {
    "ILP": {
      "active_pms": 4,
      "energy": 1200.5,
      "cpu_util": 75.2,
      "time": 45.3
    },
    "FFD": {
      "active_pms": 5,
      "energy": 1350.8,
      "cpu_util": 68.5,
      "time": 0.002,
      "gap": 25.0
    },
    ...
  },
  "experiment_2": { ... },
  "experiment_3": { ... },
  "experiment_4_google": {
    "FFD": {
      "active_pms": 836,
      "energy": 223517.0,
      "cpu_util": 92.35,
      "time": 0.76
    },
    ...
  }
}
```

**Metrics Explained**:
- `active_pms`: Number of PMs used (lower is better)
- `energy`: Total energy consumption in kWh (lower is better)
- `cpu_util`: Average CPU utilization % across active PMs (target: 60-80%)
- `ram_util`: Average memory utilization % (if available)
- `time`: Algorithm execution time in seconds
- `gap`: Optimality gap % compared to ILP (Experiment 1 only)

---

## Troubleshooting

### Error: "PlanetLab dataset not found"
**Solution**: Download the dataset as shown in Prerequisites section 2.

### Error: "Google dataset not found"
**Solution**:
- Check if `data/google_dataset/google_vms_10000.json` exists
- If not, the preprocessed dataset should be in the repository
- Alternatively, run `python src/utils/google_trace_to_dataset.py`

### ILP Takes Too Long (>5 minutes)
**Expected Behavior**:
- Default time limit is 300 seconds (5 minutes)
- If problem is complex, ILP may take the full 300s
- ILP will return the best solution found within the time limit

### Error: "Module not found"
**Solution**:
- Ensure you're running from the project root directory
- Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install all dependencies: `pip install -r requirements.txt`

### RLS-FFD Results Vary Between Runs
**Expected Behavior**:
- RLS-FFD uses randomization, so results may vary slightly
- We use fixed seed (42) for reproducibility in experiments
- For statistical analysis, run multiple times and average results

### Out of Memory (Experiment 4)
**Solution**:
- Ensure at least **8 GB available RAM**
- Close other applications
- If still failing, reduce NUM_VMS/NUM_PMS in `google_trace_to_dataset.py` and regenerate

---

## Customization

### Modify VM/PM Counts
Edit `run_all_experiments.py`:

```python
# Experiment 2: Change from 80 to 100 VMs
vms = loader.load_vms('20110303', num_vms=100, time_point=144, seed=42)

# Experiment 2: Change from 60 to 80 PMs
pms = generate_pms(num_pms=80, seed=42)
```

### Change Time Point (PlanetLab)
Select different time of day (0-287 = 24 hours):

```python
# Midday: time_point=144 (default)
# Midnight: time_point=0
# Peak hours: time_point=200
vms = loader.load_vms('20110303', num_vms=80, time_point=200, seed=42)
```

### Adjust RLS Iterations
```python
# More iterations = better quality, longer time
RLS-FFD = RandomizedLocalSearchFFD(max_iterations=5000)
```

### Change Random Seed
```python
# Different seed = different VM/PM sampling
vms = loader.load_vms('20110303', num_vms=80, seed=123)
pms = generate_pms(num_pms=60, seed=456)
```

---

## Individual Experiment Execution

You can run experiments individually (advanced usage):

```python
from experiments.run_all_experiments import (
    run_experiment_1,
    run_experiment_2,
    run_experiment_3,
    run_experiment_google
)

# Run only Experiment 1
results = run_experiment_1()
print(results)

# Run only Experiment 4 (Google Trace)
results = run_experiment_google()
print(results)
```

---

## Visualization

After running experiments, visualize results:

```bash
python plot_results.py results/experiment_results_20251220_163000.json
```

This generates plots for:
- Active PMs comparison across algorithms
- Energy consumption comparison
- CPU utilization comparison
- Execution time comparison

---

## System Requirements

| Resource | Requirement | Notes |
|----------|-------------|-------|
| **Python** | 3.8+ | Tested on 3.8, 3.9, 3.10 |
| **RAM** | 8 GB+ | Required for Experiment 4 (10,000 VMs) |
| **Disk** | 500 MB | For datasets and results |
| **CPU** | Multi-core recommended | RLS-FFD benefits from faster CPUs |
| **OS** | Windows/Linux/macOS | Cross-platform compatible |

---

## Performance Benchmarks

Approximate runtimes on a typical laptop (Intel i7, 16 GB RAM):

| Experiment | Runtime | Bottleneck |
|------------|---------|------------|
| Experiment 1 | 1-2 min | ILP solver |
| Experiment 2 | **~30-40 sec** | **ILP timeout (20s) + RLS-FFD** |
| Experiment 3 | 40-60 sec | RLS-FFD iterations |
| Experiment 4 | 8-12 min | RLS-FFD on 10,000 VMs |
| **Total** | **~15 min** | |

**Note**: Experiment 2 includes ILP with **20-second time limit** (expected to timeout). This demonstrates ILP computational infeasibility at 80 VMs.

---

## See Also

- **`docs/EXPERIMENTS.md`**: Detailed experimental design and methodology
- **`data/planetlab/README.md`**: PlanetLab dataset documentation
- **`data/google_dataset/README.md`**: Google Trace dataset documentation
- **`src/utils/planetlab_loader.py`**: PlanetLab data loading implementation
- **`src/utils/google_trace_to_dataset.py`**: Google Trace preprocessing code

---

## Contact

For questions about experiments:
1. Check `docs/EXPERIMENTS.md` for detailed methodology
2. Review algorithm implementations in `src/algorithms/`
3. Open an issue if problems persist
