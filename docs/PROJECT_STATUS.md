# VM Placement Project - Current Status

**Last Updated**: December 20, 2024
**Project Phase**: Week 8-9 (Final Integration & Analysis)
**Status**: ✅ Google Cluster Trace Integration Complete

---

## 📊 Project Overview

This project implements and evaluates **four VM placement algorithms** (ILP, FFD, BFD, RLS-FFD) across **four experiments** with increasing scale:

| Experiment | VMs | PMs | Dataset | Status |
|------------|-----|-----|---------|--------|
| Exp 1 | 25 | 5 | Synthetic | ✅ Complete |
| Exp 2 | 80 | 60 | PlanetLab + Stress | ✅ Complete |
| Exp 3 | 150 | 100 | PlanetLab + Stress | ✅ Complete |
| Exp 4 | 10,000 | 2,000 | Google Trace 2011 | ✅ Complete |

---

## 🎯 Recent Achievements (Dec 20, 2024)

### 1. Google Cluster Trace Integration

**Milestone**: Successfully integrated industrial-scale dataset from Google's Borg system

**What Was Done**:
- Preprocessed 170,000+ tasks → 10,000 VMs
- Extracted 12,583 machines → 2,000 heterogeneous PMs
- Implemented peak demand strategy for static placement
- Created automated preprocessing pipeline

**Tools Developed**:
- `src/utils/google_trace_to_dataset.py`: CSV → JSON converter
- `data/google_dataset/`: Preprocessed datasets (1.5 MB total)

**Why This Matters**:
- PlanetLab lacks real PM capacity data (we had to use synthetic PMs)
- Google Trace provides **real heterogeneous PM configurations**
- Enables validation at **industrial scale** (10,000 VMs vs. previous 150 VMs)
- Tests algorithm **robustness** on authentic workload patterns

---

### 2. Experiment 4 Results - Critical Discovery

**Finding**: **BFD Algorithm Fails in Heterogeneous Environments**

| Algorithm | Active PMs | CPU Util | Energy (kWh) | Time (s) | Notes |
|-----------|-----------|----------|--------------|----------|-------|
| **FFD** | **836** | **92.35%** | **223,517** | **0.76** | ⭐ Best |
| BFD | 993 | 83.52% | 269,930 | 9.38 | ❌ Fails (+18.8%) |
| RLS-FFD | 836 | 92.35% | 223,517 | 3.46 | Matches FFD |

**Key Insights**:
1. **BFD uses 157 more PMs** (18.8% worse than FFD)
2. **Root Cause**: BFD's "minimum remaining capacity" strategy exhausts one resource dimension (CPU or memory) first when PM capacities have different ratios
3. **FFD is superior**: Simple, fast (<1s), and robust across heterogeneous environments
4. **RLS-FFD matches FFD**: Suggests FFD already found near-optimal solution

**Theoretical Explanation**:
- **Homogeneous PMs** (Exp 1): BFD works well, all PMs have same CPU/memory ratio
- **Heterogeneous PMs** (Exp 4): BFD creates severe fragmentation
  - Example: PM with 50 CPU / 25 Memory gets filled with CPU-heavy VMs
  - Memory is underutilized (wasted), but CPU is full (can't add more VMs)
  - FFD doesn't optimize for "best fit", so it avoids this trap

**Academic Contribution**:
- Most VM placement literature uses **homogeneous PMs** (unrealistic)
- Our work demonstrates **algorithm selection must consider PM heterogeneity**
- Provides empirical evidence against BFD for real-world data centers

---

## 📁 Dataset Summary

### PlanetLab Workload Traces
- **Source**: 1,052 VM CPU utilization traces (March 3, 2011)
- **Usage**: Experiments 2 & 3
- **Sampling**: Random selection with seed=42
- **Limitation**: No real PM capacity data (synthetic heterogeneous PMs used)
- **Stress Test**: Applied resource skewness (CPU-heavy vs. memory-heavy VMs)

### Google Cluster Trace 2011
- **Source**: Google Borg system production traces
- **Original Scale**: 12,583 machines, 170,000+ tasks, 29-day period
- **Our Sampling**: 10,000 VMs, 2,000 PMs (seed=42)
- **Advantages**:
  - ✅ Real heterogeneous PM capacities
  - ✅ Industrial-scale validation
  - ✅ Authentic workload patterns (long-tail distribution)
  - ✅ Peak demand strategy for static placement

**Dataset Files**:
```
data/
├── synthetic/small_scale/instance_01.json   (Exp 1)
├── planetlab/20110303/*.txt                 (Exp 2 & 3)
└── google_dataset/
    ├── google_vms_10000.json   (1.3 MB)     (Exp 4)
    └── google_pms_2000.json    (175 KB)     (Exp 4)
```

---

## 🔬 Experimental Design

### Experiment 1: ILP Baseline (Optimal Reference)
- **Goal**: Establish provably optimal solutions
- **Scale**: 25 VMs, 5 homogeneous PMs
- **Algorithms**: ILP, FFD, BFD, RLS-FFD
- **Key Metric**: Optimality Gap = (Heuristic - Optimal) / Optimal × 100%

### Experiment 2: Real Workload Stress Test
- **Goal**: Test under resource skewness
- **Scale**: 80 VMs, 60 heterogeneous PMs
- **Algorithms**: FFD, BFD, RLS-FFD (ILP too slow)
- **Challenge**: Stress logic creates CPU-heavy vs. memory-heavy VMs

### Experiment 3: Scalability Test
- **Goal**: Evaluate at larger scale
- **Scale**: 150 VMs, 100 heterogeneous PMs
- **Algorithms**: FFD, BFD, RLS-FFD
- **Observation**: 1.875× larger than Exp 2

### Experiment 4: Google Trace (Industrial-Scale)
- **Goal**: Real-world validation
- **Scale**: 10,000 VMs, 2,000 real heterogeneous PMs
- **Algorithms**: FFD, BFD, RLS-FFD
- **Discovery**: BFD fails, FFD dominates

---

## 🛠️ Technical Implementation

### Algorithms Implemented

1. **Integer Linear Programming (ILP)**
   - Tool: PuLP with CBC solver
   - Use Case: Small-scale optimal baseline (<50 VMs)
   - Time Limit: 300 seconds

2. **First Fit Decreasing (FFD)**
   - Strategy: Sort VMs descending, place in first PM that fits
   - Performance: <1s for 10,000 VMs
   - Result: Robust across all PM configurations

3. **Best Fit Decreasing (BFD)**
   - Strategy: Place in PM with minimum remaining capacity
   - Performance: Good for homogeneous PMs
   - Result: **Fails for heterogeneous PMs** (Exp 4: +18.8% PMs)

4. **Randomized Local Search with FFD (RLS-FFD)**
   - Strategy: Start with FFD, iteratively improve via random swaps
   - Iterations: 1000-3000 depending on scale
   - Result: 2-5% better than FFD in most cases, matches FFD in Exp 4

### Data Processing Pipeline

**PlanetLab Loader** (`src/utils/planetlab_loader.py`):
```python
1. Load CPU utilization from text files (0-100%)
2. Random sampling with fixed seed
3. Apply stress test logic (CPU/memory skewness)
4. Generate VM demands
```

**Google Trace Preprocessor** (`src/utils/google_trace_to_dataset.py`):
```python
1. Read task_usage.csv.gz (VM demands)
   - Aggregate by (job_id, task_index)
   - Compute: cpu_demand = max(cpu_rate) × 100
   - Compute: memory_demand = max(assigned_memory) × 100

2. Read machine_events.csv.gz (PM capacities)
   - Take latest capacity per machine
   - Extract: cpu_capacity, memory_capacity

3. Random sampling (10,000 VMs, 2,000 PMs, seed=42)
4. Output to JSON format
```

---

## 📈 Performance Summary

### Execution Time

| Experiment | FFD | BFD | RLS-FFD | ILP |
|------------|-----|-----|---------|-----|
| Exp 1 (25 VMs) | <0.01s | <0.01s | ~0.1s | ~60s |
| Exp 2 (80 VMs) | <0.01s | <0.01s | ~2s | N/A |
| Exp 3 (150 VMs) | ~0.05s | ~0.05s | ~5s | N/A |
| Exp 4 (10,000 VMs) | **0.76s** | 9.38s | 3.46s | N/A |

**Observations**:
- FFD scales excellently: ~13,000 VMs per second
- BFD slows down in heterogeneous environments
- RLS-FFD provides good quality but 4-5× slower than FFD
- ILP only feasible for <50 VMs

### Solution Quality

| Experiment | Best Algorithm | Optimality Gap | Notes |
|------------|----------------|----------------|-------|
| Exp 1 | ILP | 0% (optimal) | FFD/BFD within 5-15% |
| Exp 2 | RLS-FFD | Unknown | 5-10% better than FFD/BFD |
| Exp 3 | RLS-FFD | Unknown | Maintains advantage at scale |
| Exp 4 | **FFD** | Unknown | BFD fails (+18.8%), RLS matches FFD |

**Trend**: As PM heterogeneity increases, **FFD becomes relatively better** compared to BFD.

---

## 📚 Documentation Status

### Completed Documentation

| File | Status | Purpose |
|------|--------|---------|
| `README.md` | ✅ Updated | Main project overview, quick start |
| `PROJECT_STRUCTURE.md` | ✅ Updated | Complete directory tree, module descriptions |
| `docs/EXPERIMENTS.md` | ✅ Updated | Detailed experimental design (4 experiments) |
| `experiments/README.md` | ✅ Updated | Experiment execution guide |
| `data/google_dataset/README.md` | ✅ Created | Google Trace dataset documentation |
| `PROJECT_STATUS.md` | ✅ Created | This file - current project status |

### Legacy Files (Historical Reference)

| File | Status | Notes |
|------|--------|-------|
| `1209 dataset與進度更新.md` | 📝 Historical | Dec 9 progress update |
| `1209實驗設計規模.md` | 📝 Historical | Experiment scale design |
| `1209資料及使用說明.md` | 📝 Historical | Dataset usage guide |
| `1209VM 與 PM 容量設計.md` | 📝 Historical | VM/PM capacity design |
| `專案更新說明 - 2024_12_20.md` | 📝 Historical | Dec 20 update notes |

**Note**: Historical files preserved for reference. All information has been integrated into the main documentation.

---

## ✅ Completion Checklist

### Phase 1: Literature Review & Design (Week 1-2)
- ✅ Problem formulation
- ✅ Literature review (`docs/literature_review.md`)
- ✅ Algorithm selection (ILP, FFD, BFD, RLS-FFD)

### Phase 2: Implementation (Week 3-4)
- ✅ ILP solver (`src/algorithms/nlp_solver.py`)
- ✅ FFD algorithm (`src/algorithms/ffd.py`)
- ✅ BFD algorithm (`src/algorithms/bfd.py`)
- ✅ RLS-FFD algorithm (`src/algorithms/rls_ffd.py`)
- ✅ Evaluation metrics (`src/evaluation/metrics.py`)

### Phase 3: Experimentation (Week 5-7)
- ✅ Experiment 1: ILP Baseline
- ✅ Experiment 2: Real Workload Stress Test
- ✅ Experiment 3: Scalability Test
- ✅ PlanetLab dataset integration
- ✅ Synthetic data generation

### Phase 4: Google Trace Integration (Week 8-9)
- ✅ Google Trace data download
- ✅ Preprocessing pipeline (`google_trace_to_dataset.py`)
- ✅ Experiment 4: Industrial-scale validation
- ✅ Critical discovery: BFD failure in heterogeneous environments
- ✅ Documentation updates

### Phase 5: Analysis & Documentation (Week 8-9)
- ✅ Results analysis
- ✅ Documentation consolidation
- 🔄 Visualization (in progress)
- 🔄 Final report writing (in progress)

---

## 🎯 Next Steps

### Immediate Tasks (Dec 20-21)

1. **Visualization**
   - Create comparison plots for all 4 experiments
   - Highlight BFD failure in Experiment 4
   - Show scalability trends (execution time vs. problem size)

2. **Deep Analysis Report**
   - Write academic-style analysis of BFD failure
   - Explain resource fragmentation in heterogeneous environments
   - Provide theoretical justification

3. **Final Report**
   - Integrate all experimental results
   - Include literature comparison
   - Discuss contributions and limitations

### Optional Enhancements

- [ ] Multi-run statistical analysis (run each experiment 10 times)
- [ ] Additional datasets (Bitbrains, Azure traces)
- [ ] Network-aware placement extension
- [ ] Dynamic VM migration simulation

---

## 🏆 Project Highlights

### Technical Achievements

1. **Industrial-Scale Validation**
   - Successfully processed 10,000 VMs in <1 second (FFD)
   - Demonstrated scalability from 25 VMs to 10,000 VMs

2. **Critical Algorithm Discovery**
   - Identified BFD failure mode in heterogeneous environments
   - Provides practical guidance: Use FFD for heterogeneous data centers

3. **Dual Dataset Strategy**
   - Academic benchmark (PlanetLab) for method validation
   - Industrial dataset (Google Trace) for real-world validation

4. **Comprehensive Documentation**
   - 6 major documentation files
   - Complete experimental reproducibility (fixed seeds)
   - Clear usage instructions

### Academic Contributions

1. **Empirical Evidence**: BFD unsuitable for heterogeneous PM environments
2. **Dataset Integration**: Combined academic (PlanetLab) and industrial (Google) datasets
3. **Scalability Analysis**: Demonstrated FFD can handle 10,000+ VMs efficiently
4. **Stress Testing**: Created challenging scenarios with resource skewness

---

## 📊 Resource Requirements

### System Requirements (Verified)

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Python | 3.8+ | 3.9+ | Tested on 3.9 |
| RAM | 4 GB | 8 GB+ | Required for Exp 4 |
| Disk | 500 MB | 2 GB | For datasets |
| CPU | 2 cores | 4+ cores | RLS-FFD benefits |

### Dataset Sizes

| Dataset | Files | Total Size | Location |
|---------|-------|------------|----------|
| PlanetLab | 1,052 files | ~50 MB | `data/planetlab/` |
| Google (raw) | ~500 files | ~10 GB | `data/google_raw/` (excluded from repo) |
| Google (preprocessed) | 2 files | 1.5 MB | `data/google_dataset/` (in repo) |

---

## 📞 Contact & Support

### For Questions
1. Review relevant documentation file
2. Check `docs/EXPERIMENTS.md` for methodology
3. Inspect source code in `src/`
4. Open an issue for bugs or clarifications

### Project Repository
- Main branch: `main` (stable)
- Development branch: `test` (current work)
- Commit history: Fully documented

---

## 🔗 Quick Links

**Main Documentation**:
- [README.md](README.md) - Project overview
- [docs/EXPERIMENTS.md](docs/EXPERIMENTS.md) - Experimental design
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Code organization

**Dataset Documentation**:
- [data/planetlab/README.md](data/planetlab/README.md) - PlanetLab traces
- [data/google_dataset/README.md](data/google_dataset/README.md) - Google Trace

**Execution Guides**:
- [experiments/README.md](experiments/README.md) - How to run experiments

**Source Code**:
- [src/algorithms/](src/algorithms/) - Algorithm implementations
- [src/utils/](src/utils/) - Data processing utilities

---

**Last Updated**: December 20, 2024
**Project Status**: 95% Complete - Final documentation and analysis in progress
**Next Milestone**: Final report submission (Week 9)
