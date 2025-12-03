"""
First Fit Decreasing (FFD) Algorithm for VM Placement
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class FirstFitDecreasing:
    """
    First Fit Decreasing (FFD) algorithm for VM placement.
    
    Strategy:
    1. Sort VMs by resource demand in decreasing order
    2. For each VM, place it in the first PM that has enough capacity
    3. If no PM has enough capacity, activate a new PM
    """
    
    def __init__(self):
        self.name = "First Fit Decreasing"
    
    def place(self, vms: List[Dict], pms: List[Dict]) -> Dict:
        """
        Place VMs onto PMs using FFD algorithm.
        
        Args:
            vms: List of VM specifications with resource demands
            pms: List of PM specifications with resource capacities
            
        Returns:
            placement: Dictionary mapping VM IDs to PM IDs
        """
        logger.info(f"Starting FFD placement for {len(vms)} VMs on {len(pms)} PMs")
        
        # Initialize placement result
        placement = {}
        pm_status = self._initialize_pm_status(pms)
        
        # Sort VMs by total resource demand (decreasing order)
        sorted_vms = self._sort_vms_by_demand(vms)
        
        # Place each VM
        for vm in sorted_vms:
            vm_id = vm['id']
            placed = False
            
            # Try to place VM in first fitting PM
            for pm_id, pm_state in pm_status.items():
                if self._can_fit(vm, pm_state):
                    # Place VM on this PM
                    self._allocate_vm(vm, pm_id, pm_state)
                    placement[vm_id] = pm_id
                    placed = True
                    logger.debug(f"Placed VM {vm_id} on PM {pm_id}")
                    break
            
            if not placed:
                logger.warning(f"Could not place VM {vm_id} - no suitable PM found")
        
        logger.info(f"FFD placement completed: {len(placement)}/{len(vms)} VMs placed")
        
        return {
            'placement': placement,
            'pm_status': pm_status,
            'algorithm': self.name
        }
    
    def _initialize_pm_status(self, pms: List[Dict]) -> Dict:
        """Initialize PM status tracking"""
        pm_status = {}
        for pm in pms:
            pm_status[pm['id']] = {
                'cpu_available': pm['cpu_capacity'],
                'memory_available': pm['memory_capacity'],
                'storage_available': pm.get('storage_capacity', float('inf')),
                'vms': [],
                'is_active': False
            }
        return pm_status
    
    def _sort_vms_by_demand(self, vms: List[Dict]) -> List[Dict]:
        """
        Sort VMs by total resource demand in decreasing order.
        Uses weighted sum of normalized resources.
        """
        def compute_demand(vm):
            # Weighted sum of resource demands
            return (
                vm['cpu_demand'] * 1.0 +
                vm['memory_demand'] * 1.0 +
                vm.get('storage_demand', 0) * 0.5
            )
        
        return sorted(vms, key=compute_demand, reverse=True)
    
    def _can_fit(self, vm: Dict, pm_state: Dict) -> bool:
        """Check if VM can fit on PM"""
        return (
            vm['cpu_demand'] <= pm_state['cpu_available'] and
            vm['memory_demand'] <= pm_state['memory_available'] and
            vm.get('storage_demand', 0) <= pm_state['storage_available']
        )
    
    def _allocate_vm(self, vm: Dict, pm_id: int, pm_state: Dict):
        """Allocate VM to PM and update PM state"""
        pm_state['cpu_available'] -= vm['cpu_demand']
        pm_state['memory_available'] -= vm['memory_demand']
        pm_state['storage_available'] -= vm.get('storage_demand', 0)
        pm_state['vms'].append(vm['id'])
        pm_state['is_active'] = True
