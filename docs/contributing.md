# Contributing Guidelines

## Git Workflow

### Branch Strategy

- `main`: Stable production code
- `develop`: Development branch
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches

### Branching Rules

1. Create a new branch for each feature/stage:
   ```bash
   git checkout -b feature/stage1-literature-review
   git checkout -b feature/stage2-nlp-algorithm
   git checkout -b feature/stage2-heuristics
   ```

2. Regular commits with descriptive messages
3. Pull requests for code review before merging

### Commit Message Convention

Format: `<type>(<scope>): <subject>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

**Examples:**
```
feat(ffd): implement First Fit Decreasing algorithm
fix(metrics): correct energy calculation formula
docs(readme): update installation instructions
test(algorithms): add unit tests for BFD
```

## Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints where appropriate
- Docstrings for all functions and classes
- Maximum line length: 100 characters

### Example:
```python
def calculate_energy(utilization: float, power_max: float = 300) -> float:
    """
    Calculate energy consumption based on utilization.
    
    Args:
        utilization: Resource utilization ratio (0-1)
        power_max: Maximum power consumption in Watts
        
    Returns:
        Energy consumption in Watts
    """
    power_idle = 100
    return power_idle + (power_max - power_idle) * utilization
```

## Testing

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_algorithms.py -v
```

### Test Guidelines
- Write tests for all new features
- Aim for > 80% code coverage
- Test both normal and edge cases

## Code Review Process

1. Create pull request with descriptive title and description
2. Link related issues
3. Request review from team members
4. Address review comments
5. Merge after approval

## Documentation

### Code Documentation
- Add docstrings to all public functions/classes
- Update README.md for significant changes
- Document algorithm implementations

### Experimental Documentation
- Log all experimental parameters
- Document results in `results/` directory
- Update literature review with new findings

## Project Stages

### Stage 1: Literature Review (Weeks 1-2)
**Responsible:** All members
- Research existing VM placement algorithms
- Define resource configurations
- Establish evaluation metrics

### Stage 2: Algorithm Implementation (Weeks 3-4)
**Tasks:**
- Implement NLP/ILP solver
- Implement FFD algorithm
- Implement BFD algorithm
- Implement RLS-FFD algorithm

### Stage 3: Experimental Evaluation (Weeks 5-7)
**Responsible:** All members
- Small-scale testing (5 PMs, 25 VMs)
- Medium-scale testing (15 PMs, 80 VMs)
- Performance benchmarking
- Data collection and analysis

### Stage 4: Results Analysis and Documentation (Weeks 8-9)
**Responsible:** All members
- Analyze experimental results
- Write final report
- Prepare presentation

## Issue Tracking

### Issue Labels
- `enhancement`: New feature request
- `bug`: Bug report
- `documentation`: Documentation improvement
- `question`: Question or discussion
- `stage-1`, `stage-2`, etc.: Stage-specific tasks

### Creating Issues
1. Use descriptive title
2. Provide detailed description
3. Add appropriate labels
4. Assign to responsible person

## Communication

### Team Meetings
- Weekly progress meetings
- Document meeting notes in `docs/meetings/`

### Questions and Discussions
- Use GitHub issues for technical discussions
- Use project chat for quick questions

## Resources

### Useful Links
- [PlanetLab Dataset](http://www.planet-lab.org/)
- [Google Cluster Data](https://github.com/google/cluster-data)
- [PuLP Documentation](https://coin-or.github.io/pulp/)
- [NumPy Documentation](https://numpy.org/doc/)

### References
- Add references to `docs/literature_review.md`
- Use consistent citation format

---

*Remember: Good documentation and clean code benefit everyone!*
