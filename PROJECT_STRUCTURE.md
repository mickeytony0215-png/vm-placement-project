# Project Structure

```
vm-placement-project/
│
├── README.md                          # Main project documentation
├── LICENSE                            # MIT License
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore rules
├── GIT_SETUP.md                      # Git repository setup instructions
├── example.py                        # Quick start demo script
│
├── docs/                             # Documentation
│   ├── literature_review.md          # Research literature review
│   ├── contributing.md               # Contribution guidelines
│   └── final_report.md              # Final project report (TBD)
│
├── src/                              # Source code
│   ├── main.py                       # Main entry point
│   │
│   ├── algorithms/                   # Placement algorithms
│   │   ├── __init__.py
│   │   ├── ffd.py                   # First Fit Decreasing
│   │   ├── bfd.py                   # Best Fit Decreasing
│   │   ├── nlp_solver.py            # Integer Linear Programming
│   │   └── rls_ffd.py               # Randomized Local Search with FFD
│   │
│   ├── utils/                        # Utility modules
│   │   ├── __init__.py
│   │   ├── vm_generator.py          # VM instance generator
│   │   ├── pm_generator.py          # PM instance generator
│   │   └── data_loader.py           # Data loading utilities
│   │
│   └── evaluation/                   # Evaluation metrics
│       ├── __init__.py
│       └── metrics.py               # Performance metrics calculation
│
├── data/                             # Data storage
│   ├── small_scale/                 # Small-scale problem instances
│   │   └── .gitkeep
│   └── medium_scale/                # Medium-scale problem instances
│       └── .gitkeep
│
├── results/                          # Experimental results
│   ├── plots/                       # Visualization plots
│   │   └── .gitkeep
│   └── logs/                        # Execution logs
│       └── .gitkeep
│
└── tests/                            # Unit tests
    └── test_algorithms.py           # Algorithm unit tests
```

## Module Descriptions

### Source Code (`src/`)

#### Main Entry Point
- **`main.py`**: Command-line interface for running experiments
  - Supports multiple algorithms and problem scales
  - Handles experiment configuration and execution
  - Generates results and logs

#### Algorithms (`src/algorithms/`)
- **`ffd.py`**: First Fit Decreasing algorithm
  - Greedy heuristic
  - Fast execution
  - Good for initial solutions

- **`bfd.py`**: Best Fit Decreasing algorithm
  - Improved greedy heuristic
  - Better packing efficiency
  - Reduces resource fragmentation

- **`nlp_solver.py`**: Integer Linear Programming solver
  - Provides optimal solutions
  - Only suitable for small-scale problems (< 50 VMs)
  - Uses PuLP library

- **`rls_ffd.py`**: Randomized Local Search with FFD Initialization
  - Meta-heuristic approach
  - Iterative improvement
  - Escapes local optima

#### Utilities (`src/utils/`)
- **`vm_generator.py`**: Virtual Machine generation
  - Heterogeneous VM types (small, medium, large)
  - Configurable resource demands
  - Support for different distributions

- **`pm_generator.py`**: Physical Machine generation
  - Heterogeneous PM types
  - Configurable capacities
  - Energy consumption models

- **`data_loader.py`**: Data loading and saving
  - JSON format support
  - PlanetLab trace loading (planned)
  - Data persistence

#### Evaluation (`src/evaluation/`)
- **`metrics.py`**: Performance metrics
  - Number of active PMs
  - Energy consumption
  - Resource utilization
  - Load balance
  - SLA violations

### Data (`data/`)
- **`small_scale/`**: Small problem instances (5 PMs, 25 VMs)
- **`medium_scale/`**: Medium problem instances (15 PMs, 80 VMs)

### Results (`results/`)
- **`plots/`**: Visualization outputs (PNG, PDF)
- **`logs/`**: Execution logs and detailed results

### Tests (`tests/`)
- **`test_algorithms.py`**: Unit tests for all algorithms
  - Algorithm correctness tests
  - Feasibility checks
  - Integration tests

## Key Files

### Configuration Files
- **`requirements.txt`**: Python package dependencies
  - NumPy, Pandas, SciPy
  - Matplotlib, Seaborn
  - PuLP, OR-Tools
  - Testing frameworks

- **`.gitignore`**: Git ignore patterns
  - Python cache files
  - Virtual environments
  - Large data files
  - Temporary results

### Documentation Files
- **`README.md`**: Project overview and usage guide
- **`LICENSE`**: MIT License for academic use
- **`GIT_SETUP.md`**: Git repository setup instructions
- **`docs/contributing.md`**: Contribution guidelines

## Usage Examples

### Running Experiments

```bash
# Run all algorithms on small scale
python src/main.py --algorithm all --scale small

# Run specific algorithm
python src/main.py --algorithm ffd --scale medium

# Run all experiments
python src/main.py --run-all
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test
pytest tests/test_algorithms.py::TestFFDAlgorithm -v
```

### Quick Demo

```bash
# Run example script
python example.py
```

## Development Workflow

1. **Literature Review** (Weeks 1-2)
   - Update `docs/literature_review.md`
   - Define problem parameters

2. **Algorithm Implementation** (Weeks 3-4)
   - Implement in `src/algorithms/`
   - Add tests in `tests/`

3. **Experimental Evaluation** (Weeks 5-7)
   - Generate problem instances in `data/`
   - Run experiments via `src/main.py`
   - Save results to `results/`

4. **Analysis and Documentation** (Weeks 8-9)
   - Analyze results
   - Create visualizations
   - Write final report

## Extension Points

### Adding New Algorithms
1. Create new file in `src/algorithms/`
2. Implement `place(vms, pms)` method
3. Add to `src/algorithms/__init__.py`
4. Add tests in `tests/test_algorithms.py`
5. Update `src/main.py` to include new algorithm

### Adding New Metrics
1. Add function to `src/evaluation/metrics.py`
2. Update `evaluate_placement()` function
3. Add tests for new metric

### Supporting New Data Formats
1. Add loader to `src/utils/data_loader.py`
2. Update `load_vm_pm_data()` function
3. Document format in README

---

For detailed contribution guidelines, see `docs/contributing.md`
