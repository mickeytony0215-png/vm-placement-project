# Experiments

This directory contains scripts to run VM placement experiments.

## Quick Start

Run all experiments at once:

```bash
python experiments/run_all_experiments.py
```

This will:
1. Run Experiment 1: ILP Baseline (25 VMs, 5 PMs)
2. Run Experiment 2: Real Workload (80 VMs, 15 PMs)
3. Run Experiment 3: Scalability (150 VMs, 30 PMs)
4. Save results to `results/experiment_results_YYYYMMDD_HHMMSS.json`

## Prerequisites

Before running experiments:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download PlanetLab dataset** (required for Exp 2 & 3):
   ```bash
   cd data
   git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab
   cd ..
   ```

## Experiment Details

### Experiment 1: ILP Baseline
- **Goal**: Establish optimal solution baseline
- **Data**: Synthetic (25 VMs, 5 PMs)
- **Algorithms**: ILP, FFD
- **Time**: ~1-2 minutes

### Experiment 2: Real Workload
- **Goal**: Test on real PlanetLab data
- **Data**: PlanetLab 20110303 (80 VMs, 15 PMs)
- **Algorithms**: FFD, BFD, RLS-FFD
- **Time**: ~10-30 seconds

### Experiment 3: Scalability
- **Goal**: Test at larger scale
- **Data**: PlanetLab 20110303 (150 VMs, 30 PMs)
- **Algorithms**: FFD, BFD, RLS-FFD
- **Time**: ~30-60 seconds

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
    }
  },
  "experiment_2": { ... },
  "experiment_3": { ... }
}
```

## Troubleshooting

**Error: "PlanetLab dataset not found"**
- Download the dataset as shown in Prerequisites

**Error: "ILP takes too long"**
- Default time limit is 300 seconds (5 minutes)
- This is normal for Experiment 1
- If it exceeds limit, ILP returns best solution found

**Error: "Module not found"**
- Run from project root directory
- Ensure virtual environment is activated
- Check that all dependencies are installed

## Customization

To modify experiment parameters, edit `run_all_experiments.py`:

```python
# Change VM/PM counts
vms = loader.load_vms('20110303', num_vms=100)  # Change 80 to 100
pms = generate_pms(num_pms=20, ...)             # Change 15 to 20

# Change time point (0-287)
vms = loader.load_vms('20110303', num_vms=80, time_point=200)

# Change random seed
vms = loader.load_vms('20110303', num_vms=80, seed=123)
```

## Individual Experiments

You can also run experiments individually (advanced):

```python
from experiments.run_all_experiments import run_experiment_1

results = run_experiment_1()
print(results)
```

## See Also

- `docs/EXPERIMENTS.md` - Detailed experimental design
- `data/planetlab/README.md` - Dataset documentation
- `src/utils/planetlab_loader.py` - Data loading code