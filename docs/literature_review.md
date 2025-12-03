# Literature Review

## Virtual Machine Placement Problem

### Overview
The Virtual Machine Placement (VMP) problem is a fundamental challenge in cloud computing resource management. It involves efficiently mapping virtual machines to physical servers while optimizing various objectives such as energy consumption, resource utilization, and service quality.

### Key Research Areas

#### 1. Problem Formulation
- Multi-dimensional bin packing
- Resource vector packing
- Multi-objective optimization

#### 2. Solution Approaches

##### Exact Methods
- Integer Linear Programming (ILP)
- Mixed Integer Programming (MIP)
- Branch and Bound
- **Limitation**: Only suitable for small-scale problems (< 50 VMs)

##### Heuristic Algorithms
- First Fit (FF)
- Best Fit (BF)
- First Fit Decreasing (FFD)
- Best Fit Decreasing (BFD)
- **Advantage**: Fast execution, suitable for large-scale problems

##### Meta-heuristic Algorithms
- Genetic Algorithms (GA)
- Particle Swarm Optimization (PSO)
- Simulated Annealing (SA)
- Ant Colony Optimization (ACO)
- **Advantage**: Better solution quality, but computationally expensive

#### 3. Optimization Objectives
- Minimize number of active PMs (energy efficiency)
- Minimize total energy consumption
- Maximize resource utilization
- Minimize SLA violations
- Minimize VM migration overhead
- Balance load across PMs

### Important Papers

#### Foundational Work
1. **"Energy-Efficient Management of Data Center Resources for Cloud Computing"**
   - Authors: [To be filled]
   - Key contribution: Energy-aware VM placement

2. **"Bin Packing Algorithms for Virtual Machine Placement in Cloud Computing"**
   - Authors: [To be filled]
   - Key contribution: Comparison of bin packing heuristics

#### Recent Advances
1. **Machine Learning Approaches**
   - Deep Reinforcement Learning for dynamic VM placement
   - Neural network-based prediction of resource demands

2. **Multi-objective Optimization**
   - Pareto-optimal solutions
   - Trade-offs between conflicting objectives

### Datasets

#### 1. PlanetLab Traces
- Real-world VM workload traces
- CPU utilization data from 1000+ VMs
- 500+ geographically distributed locations
- **Source**: http://www.planet-lab.org/

#### 2. Google Cluster Data
- Large-scale cluster traces
- Task scheduling and resource usage
- **Source**: https://github.com/google/cluster-data

#### 3. Bitbrains Traces
- Data center workload traces
- VM resource usage patterns
- **Source**: http://gwa.ewi.tudelft.nl/datasets/gwa-t-12-bitbrains

### Key Findings from Literature

1. **Problem Complexity**
   - VMP is NP-hard
   - Exact solutions only feasible for small instances
   - Heuristics provide good approximations

2. **Energy Efficiency**
   - Consolidation reduces number of active servers
   - Linear or cubic energy models commonly used
   - Trade-off between consolidation and performance

3. **Dynamic Environments**
   - Workloads vary over time
   - Periodic re-optimization necessary
   - VM migration has cost

### Research Gaps

1. Multi-resource consideration (CPU, memory, I/O, network)
2. Real-time dynamic placement
3. Heterogeneous infrastructure
4. Network topology awareness
5. Security and privacy constraints

### References

[To be updated with actual references]

1. Author1, Author2. (Year). "Paper Title". Conference/Journal.
2. Author3, Author4. (Year). "Paper Title". Conference/Journal.

---
*Last updated: [Date]*
