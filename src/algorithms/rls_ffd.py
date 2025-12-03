"""
Randomized Local Search with FFD Initialization (RLS-FFD) for VM Placement
"""
import logging
import random
import math
from typing import List, Dict
from .ffd import FirstFitDecreasing

logger = logging.getLogger(__name__)


class RandomizedLocalSearchFFD:
    """
    Randomized Local Search with FFD Initialization (RLS-FFD).
    
    Strategy:
    1. Initialize with FFD solution
    2. Iteratively improve solution through local search
    3. Use random perturbations to escape local optima
    4. Accept improvements and occasionally accept worse solutions
    """
    
    def __init__(self, max_iterations=1000, temperature=1.0, cooling_rate=0.95):
        """
        Initialize RLS-FFD algorithm.
        
        Args:
            max_iterations: Maximum number of iterations
            temperature: Initial temperature for simulated annealing
            cooling_rate: Temperature reduction factor
        """
        self.name = "Randomized Local Search with FFD"
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.cooling_rate = cooling_rate
    
    def place(self, vms: List[Dict], pms: List[Dict]) -> Dict:
        """
        Place VMs using RLS-FFD algorithm.
        
        Args:
            vms: List of VM specifications
            pms: List of PM specifications
            
        Returns:
            placement: Best placement found
        """
        logger.info(f"Starting RLS-FFD for {len(vms)} VMs on {len(pms)} PMs")
        
        # Step 1: Get initial solution using FFD
        ffd = FirstFitDecreasing()
        current_solution = ffd.place(vms, pms)
        current_cost = self._evaluate_solution(current_solution)
        
        best_solution = current_solution.copy()
        best_cost = current_cost
        
        logger.info(f"Initial FFD solution cost: {current_cost}")
        
        # Step 2: Local search with random perturbations
        temperature = self.temperature
        
        for iteration in range(self.max_iterations):
            # Generate neighbor solution
            neighbor_solution = self._generate_neighbor(current_solution, vms, pms)
            
            if neighbor_solution is None:
                continue
            
            neighbor_cost = self._evaluate_solution(neighbor_solution)
            
            # Decide whether to accept neighbor
            if self._accept_solution(current_cost, neighbor_cost, temperature):
                current_solution = neighbor_solution
                current_cost = neighbor_cost
                
                # Update best solution
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
                    logger.info(f"Iteration {iteration}: New best cost = {best_cost}")
            
            # Cool down temperature
            temperature *= self.cooling_rate
            
            if iteration % 100 == 0:
                logger.debug(f"Iteration {iteration}: Current cost = {current_cost}, Best cost = {best_cost}")
        
        logger.info(f"RLS-FFD completed: Best cost = {best_cost}")
        
        return best_solution
    
    def _evaluate_solution(self, solution: Dict) -> float:
        """
        Evaluate solution quality.
        
        Lower cost is better. Cost components:
        - Number of active PMs (primary objective)
        - Resource fragmentation (secondary objective)
        """
        pm_status = solution['pm_status']
        
        # Count active PMs
        active_pms = sum(1 for pm_state in pm_status.values() if pm_state['is_active'])
        
        # Calculate fragmentation (normalized variance of utilization)
        fragmentation = 0
        for pm_state in pm_status.values():
            if pm_state['is_active']:
                # Calculate utilization variance across resources
                # (This encourages balanced resource usage)
                fragmentation += 0.1  # Placeholder for fragmentation metric
        
        # Weighted cost
        cost = active_pms * 1000 + fragmentation
        
        return cost
    
    def _generate_neighbor(self, solution: Dict, vms: List[Dict], pms: List[Dict]) -> Dict:
        """
        Generate a neighbor solution using local search operators.
        
        Operators:
        1. Move: Move a VM from one PM to another
        2. Swap: Swap two VMs between different PMs
        3. Relocate: Move multiple VMs from one PM to others
        """
        operator = random.choice(['move', 'swap', 'relocate'])
        
        if operator == 'move':
            return self._move_vm(solution, vms, pms)
        elif operator == 'swap':
            return self._swap_vms(solution, vms, pms)
        else:
            return self._relocate_vms(solution, vms, pms)
    
    def _move_vm(self, solution: Dict, vms: List[Dict], pms: List[Dict]) -> Dict:
        """Move a random VM to a different PM"""
        placement = solution['placement'].copy()
        
        # FIX: Manually deep copy pm_status to ensure 'vms' list is independent
        # Original code used shallow copy which caused list.remove() error on shared lists
        pm_status = {}
        for k, v in solution['pm_status'].items():
            new_pm = v.copy()
            new_pm['vms'] = list(v['vms'])  # Critical fix: Copy the list explicitly
            pm_status[k] = new_pm
        
        if not placement:
            return None
        
        # Select random VM
        vm_id = random.choice(list(placement.keys()))
        current_pm = placement[vm_id]
        
        # Find VM details
        vm = next((v for v in vms if v['id'] == vm_id), None)
        if vm is None:
            return None
        
        # Try to move to a different PM
        for pm in random.sample(pms, len(pms)):
            if pm['id'] != current_pm:
                # Check if VM fits on new PM
                pm_state = pm_status[pm['id']]
                if self._can_fit(vm, pm_state):
                    # Remove from old PM
                    old_pm_state = pm_status[current_pm]
                    
                    # Ensure synchronization before removing
                    if vm_id in old_pm_state['vms']:
                        old_pm_state['cpu_available'] += vm['cpu_demand']
                        old_pm_state['memory_available'] += vm['memory_demand']
                        old_pm_state['vms'].remove(vm_id)
                        if not old_pm_state['vms']:
                            old_pm_state['is_active'] = False
                        
                        # Add to new PM
                        pm_state['cpu_available'] -= vm['cpu_demand']
                        pm_state['memory_available'] -= vm['memory_demand']
                        pm_state['vms'].append(vm_id)
                        pm_state['is_active'] = True
                        
                        # Update placement
                        placement[vm_id] = pm['id']
                        
                        return {
                            'placement': placement,
                            'pm_status': pm_status,
                            'algorithm': self.name
                        }
                    else:
                        # Should not happen with correct deep copy, but safe to ignore
                        logger.warning(f"VM {vm_id} not found in PM {current_pm} during move")
                        return None
        
        return None
    
    def _swap_vms(self, solution: Dict, vms: List[Dict], pms: List[Dict]) -> Dict:
        """Swap two VMs between different PMs"""
        # TODO: Implement swap operator
        return None
    
    def _relocate_vms(self, solution: Dict, vms: List[Dict], pms: List[Dict]) -> Dict:
        """Relocate multiple VMs from one PM"""
        # TODO: Implement relocate operator
        return None
    
    def _can_fit(self, vm: Dict, pm_state: Dict) -> bool:
        """Check if VM can fit on PM"""
        return (
            vm['cpu_demand'] <= pm_state['cpu_available'] and
            vm['memory_demand'] <= pm_state['memory_available']
        )
    
    def _accept_solution(self, current_cost: float, neighbor_cost: float, temperature: float) -> bool:
        """
        Decide whether to accept neighbor solution.
        Uses simulated annealing acceptance criterion.
        """
        if neighbor_cost < current_cost:
            return True
        
        # Accept worse solution with probability based on temperature
        if temperature <= 0:
            return False
        
        delta = neighbor_cost - current_cost
        probability = random.random()
        try:
            threshold = math.exp(-delta / temperature)
        except OverflowError:
            threshold = 0
        
        return probability < threshold