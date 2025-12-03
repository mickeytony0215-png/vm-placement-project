# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Extract and Navigate
```bash
# Extract the project
tar -xzf vm-placement-project.tar.gz
cd vm-placement-project
```

### Step 2: Set Up Environment
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run Quick Demo
```bash
# Run the example script
python example.py
```

Expected output: Comparison of FFD and BFD algorithms on a small-scale problem.

### Step 4: Run Unit Tests
```bash
# Install testing dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v
```

### Step 5: Run Full Experiments
```bash
# Small scale experiments (recommended for first run)
python src/main.py --algorithm all --scale small

# Medium scale experiments
python src/main.py --algorithm all --scale medium

# Run all combinations
python src/main.py --run-all
```

## 📊 What You Get

### Algorithms Implemented
1. **ILP (Integer Linear Programming)** - Optimal solutions for small problems
2. **FFD (First Fit Decreasing)** - Fast greedy heuristic
3. **BFD (Best Fit Decreasing)** - Improved greedy heuristic
4. **RLS-FFD** - Meta-heuristic with local search

### Evaluation Metrics
- Number of active PMs
- Total energy consumption
- CPU utilization
- Memory utilization
- Resource fragmentation
- Load balance score

### Problem Scales
- **Small**: 5 PMs, 25 VMs (ILP solvable)
- **Medium**: 15 PMs, 80 VMs (Heuristics only)

## 🔧 Customization

### Generate Custom Problem Instances
```python
from src.utils.vm_generator import generate_vms
from src.utils.pm_generator import generate_pms

# Generate 50 VMs and 10 PMs
vms = generate_vms(50, seed=123)
pms = generate_pms(10, seed=123)
```

### Use Specific Algorithm
```python
from src.algorithms.ffd import FirstFitDecreasing
from src.evaluation.metrics import evaluate_placement

# Run FFD
ffd = FirstFitDecreasing()
result = ffd.place(vms, pms)

# Evaluate
metrics = evaluate_placement(result, vms, pms)
print(f"Active PMs: {metrics['active_pms']}")
```

## 📁 Project Structure Overview

```
vm-placement-project/
├── src/                    # Source code
│   ├── algorithms/        # Four placement algorithms
│   ├── utils/            # VM/PM generators, data loader
│   ├── evaluation/       # Performance metrics
│   └── main.py          # Main entry point
├── tests/                # Unit tests
├── docs/                 # Documentation
├── data/                 # Problem instances
├── results/              # Experimental results
└── example.py           # Quick demo script
```

## 📝 Common Tasks

### Add New Algorithm
1. Create file in `src/algorithms/new_algo.py`
2. Implement `place(vms, pms)` method
3. Add to `__init__.py`
4. Run tests

### Modify Problem Parameters
Edit `src/utils/vm_generator.py` or `src/utils/pm_generator.py`:
- Change VM/PM size distributions
- Adjust resource capacities
- Modify heterogeneity levels

### Change Evaluation Metrics
Edit `src/evaluation/metrics.py`:
- Add new metric functions
- Update `evaluate_placement()`

## 🐛 Troubleshooting

### PuLP Not Installed
```bash
pip install pulp
```

### Import Errors
Make sure you're in the project root directory and have activated the virtual environment.

### Tests Failing
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests with verbose output
pytest tests/ -v
```

## 📚 Next Steps

1. **Read the full documentation**: `README.md`
2. **Review literature**: `docs/literature_review.md`
3. **Understand the code**: `PROJECT_STRUCTURE.md`
4. **Contribute**: `docs/contributing.md`

## 🎯 Project Timeline

- **Weeks 1-2**: Literature review and setup ✅
- **Weeks 3-4**: Algorithm implementation
- **Weeks 5-7**: Experimental evaluation
- **Weeks 8-9**: Results analysis and documentation

## 💡 Tips

- Start with small-scale problems to understand algorithm behavior
- Use `example.py` to quickly test changes
- Run tests frequently to catch bugs early
- Save experimental results for reproducibility

## 📞 Getting Help

- Check `README.md` for detailed documentation
- Review `docs/contributing.md` for guidelines
- Create GitHub issues for bugs or questions

---

**Happy coding! 🎉**

For detailed information, see:
- `README.md` - Full project documentation
- `PROJECT_STRUCTURE.md` - Detailed structure explanation
- `GIT_SETUP.md` - Git repository setup
