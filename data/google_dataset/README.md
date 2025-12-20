# Google Cluster Trace 2011 Dataset

This directory contains preprocessed VM and PM datasets extracted from the **Google Cluster Trace 2011**, used for Experiment 4 (industrial-scale validation).

## Dataset Files

| File | Size | Description |
|------|------|-------------|
| `google_vms_10000.json` | 1.3 MB | 10,000 VM instances with peak resource demands |
| `google_pms_2000.json` | 175 KB | 2,000 heterogeneous physical machines |

## Dataset Origin

**Source**: Google Cluster Data (2011) - Borg System Production Traces

**Official Repository**: https://github.com/google/cluster-data

**Original Scale**:
- 12,583 physical machines
- 170,000+ tasks (jobs)
- 29-day trace period (May 2011)

**Our Sampling**:
- Randomly sampled 10,000 VMs from 170,000+ tasks
- Randomly sampled 2,000 PMs from 12,583 machines
- Fixed random seed: `RANDOM_SEED = 42` (reproducible)

---

## Data Format

### VM Data (`google_vms_10000.json`)

Each VM entry contains:

```json
{
  "id": 0,
  "job_id": 6221861800,
  "task_index": 17070,
  "cpu_demand": 1.0,
  "memory_demand": 1.0
}
```

**Field Descriptions**:
- `id`: Sequential VM identifier (0-9999)
- `job_id`: Original Google Trace job identifier
- `task_index`: Original task index within the job
- `cpu_demand`: Peak CPU demand in [0-100] scale
- `memory_demand`: Peak memory demand in [0-100] scale

**Resource Calculation** (from `task_usage.csv`):
```python
cpu_demand = max(cpu_rate) × 100
memory_demand = max(assigned_memory) × 100
```

**Why Peak Strategy?**
- Static placement must handle worst-case load
- Using `max()` ensures VMs don't exceed PM capacity under any scenario
- Reflects conservative data center provisioning practices

---

### PM Data (`google_pms_2000.json`)

Each PM entry contains:

```json
{
  "id": 6641580,
  "cpu_capacity": 50.0,
  "memory_capacity": 49.95
}
```

**Field Descriptions**:
- `id`: Original Google Trace machine identifier
- `cpu_capacity`: Total CPU capacity in [0-100] scale
- `memory_capacity`: Total memory capacity in [0-100] scale

**Resource Calculation** (from `machine_events.csv`):
```python
cpu_capacity = cpu_capacity × 100
memory_capacity = memory_capacity × 100
```

**Heterogeneous PM Examples**:
```
PM Type 1: CPU=50.0,  Memory=49.95  (balanced, ~50/50)
PM Type 2: CPU=50.0,  Memory=24.93  (CPU-heavy, ~50/25)
PM Type 3: CPU=25.0,  Memory=24.98  (small, balanced)
PM Type 4: CPU=12.5,  Memory=12.46  (very small)
```

**Key Insight**: Real Google data centers have **heterogeneous PM configurations** with varying CPU/memory ratios, unlike synthetic datasets with uniform PM types.

---

## Data Preprocessing

The datasets were generated using `src/utils/google_trace_to_dataset.py`.

### Preprocessing Steps:

1. **Load Task Usage Data** (`task_usage/*.csv.gz`):
   - Extract fields: `job_id`, `task_index`, `cpu_rate`, `assigned_memory`
   - Aggregate by `(job_id, task_index)` to form unique VMs
   - Compute peak demands: `max(cpu_rate)`, `max(assigned_memory)`

2. **Load Machine Events** (`machine_events/*.csv.gz`):
   - Extract fields: `machine_id`, `cpu_capacity`, `memory_capacity`
   - Take latest record per machine (most recent capacity)

3. **Random Sampling**:
   - Sample 10,000 VMs from 170,000+ candidates
   - Sample 2,000 PMs from 12,583 machines
   - Use fixed seed (42) for reproducibility

4. **Normalization**:
   - Scale CPU/memory to [0-100] range
   - Clip values: `clip(lower=1.0, upper=100.0)`
   - Ensures compatibility with placement algorithms

### Regenerating the Dataset

If you need to regenerate or customize the dataset:

```bash
# Ensure raw Google Trace data is in data/google_raw/
# - task_usage/part-00000-of-00500.csv.gz
# - machine_events/machine_events.csv.gz

python src/utils/google_trace_to_dataset.py
```

**Customization** (edit `google_trace_to_dataset.py`):
```python
NUM_VMS = 10000      # Change VM count
NUM_PMS = 2000       # Change PM count
RANDOM_SEED = 42     # Change seed for different sampling
```

---

## Dataset Statistics

### VM Resource Demands

**Distribution Summary** (from 10,000 VMs):
- Mean CPU demand: ~12.5%
- Mean memory demand: ~8.3%
- Max CPU demand: 100% (some VMs are very large)
- Max memory demand: 100%
- **Long-tail distribution**: Most VMs are small, few are very large

**VM Types** (estimated):
- Small VMs (<10% CPU): ~60%
- Medium VMs (10-30% CPU): ~30%
- Large VMs (>30% CPU): ~10%

### PM Capacities

**Distribution Summary** (from 2,000 PMs):
- CPU capacity range: [12.5, 50.0]
- Memory capacity range: [12.46, 49.95]
- **Heterogeneous**: CPU/memory ratios vary significantly
- Common configurations: 50/50, 50/25, 25/25, 12.5/12.5

**PM Heterogeneity Impact**:
- FFD handles heterogeneity well (simple, robust)
- BFD fails catastrophically (see Experiment 4 results)
- Reason: BFD's "minimum remaining capacity" strategy exhausts one resource dimension first

---

## Usage in Experiment 4

### Loading the Dataset

```python
import json
from pathlib import Path

base = Path("data/google_dataset")

with open(base / "google_vms_10000.json", "r") as f:
    vms = json.load(f)

with open(base / "google_pms_2000.json", "r") as f:
    pms = json.load(f)

print(f"Loaded {len(vms)} VMs, {len(pms)} PMs")
```

### Experiment 4 Results

| Algorithm | Active PMs | CPU Util | Energy (kWh) | Time (s) |
|-----------|-----------|----------|--------------|----------|
| **FFD** | **836** | **92.35%** | **223,517** | **0.76** |
| BFD | 993 (+18.8%) | 83.52% | 269,930 | 9.38 |
| **RLS-FFD** | **836** | **92.35%** | **223,517** | 3.46 |

**Key Findings**:
1. Only **836 PMs needed** out of 2,000 available (41.8% utilization)
2. FFD achieves **92.35% CPU utilization** (near-optimal packing)
3. BFD uses **157 more PMs** due to heterogeneity-induced fragmentation
4. FFD processes **10,000 VMs in 0.76 seconds** (13,000+ VMs/second)

---

## Comparison with PlanetLab

| Aspect | PlanetLab | Google Cluster Trace |
|--------|-----------|---------------------|
| **Data Source** | Academic testbed | Industrial production system |
| **Scale** | 1,052 VMs | 10,000 VMs (sampled from 170,000+) |
| **VM Data** | CPU utilization only | CPU + Memory demands |
| **PM Data** | None (synthetic) | **Real heterogeneous capacities** |
| **Representativeness** | Research workloads | **Real-world data center workloads** |
| **Usage** | Experiments 2 & 3 | Experiment 4 |

**Why Both Datasets?**
- **PlanetLab**: Academic standard, algorithm validation, controlled testing
- **Google Trace**: Industrial validation, heterogeneity testing, scalability demonstration

---

## Data Integrity

### Verification

To verify dataset integrity:

```bash
# Check file sizes
ls -lh data/google_dataset/

# Expected:
# google_vms_10000.json: ~1.3 MB
# google_pms_2000.json: ~175 KB

# Check record counts
python -c "import json; print(len(json.load(open('data/google_dataset/google_vms_10000.json'))))"
# Expected: 10000

python -c "import json; print(len(json.load(open('data/google_dataset/google_pms_2000.json'))))"
# Expected: 2000
```

### Checksums (Optional)

If you need to verify dataset authenticity, compare with these characteristics:
- Total VMs: 10,000
- Total PMs: 2,000
- First VM ID: 0
- First PM ID: 6641580 (original Google machine ID)
- Random seed used: 42

---

## References

### Google Cluster Trace Documentation
- **Paper**: Reiss, C., Wilkes, J., & Hellerstein, J. L. (2011). *Google cluster-usage traces: format + schema*. Google Inc., Mountain View, CA, USA, Technical Report.
- **Dataset**: https://github.com/google/cluster-data
- **Schema**: https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md

### Original Data Fields Used

**From `task_usage` table**:
- `job_id`: Unique job identifier
- `task_index`: Task index within job
- `cpu_rate`: CPU usage rate [0, 1] (normalized)
- `assigned_memory`: Memory assigned to task [0, 1] (normalized)

**From `machine_events` table**:
- `machine_id`: Unique machine identifier
- `cpu_capacity`: Machine CPU capacity [0, 1] (normalized)
- `memory_capacity`: Machine memory capacity [0, 1] (normalized)

---

## License

The Google Cluster Trace dataset is provided by Google under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

**Citation**:
```
Reiss, C., Wilkes, J., & Hellerstein, J. L. (2011).
Google cluster-usage traces: format + schema.
Google Inc., Mountain View, CA, USA, Technical Report.
```

---

## Contact

For questions about this dataset:
1. Review `src/utils/google_trace_to_dataset.py` for preprocessing logic
2. Check `docs/EXPERIMENTS.md` for experimental methodology
3. Refer to official Google Cluster Trace documentation
4. Open an issue if problems persist
