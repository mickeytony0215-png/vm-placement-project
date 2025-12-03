"""
Best Fit Decreasing (BFD) Algorithm for VM Placement
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class BestFitDecreasing:
    """
    Best Fit Decreasing (BFD) algorithm for VM placement.
    
    Strategy:
    1. Sort VMs by resource demand in decreasing order
    2. For each VM, place it in the PM with least remaining capacity that can fit it
    3. This aims to pack VMs more tightly and reduce fragmentation
    """
    
    def __init__(self):
        self.name = "Best Fit Decreasing"
    
    def place(self, vms: List[Dict], pms: List[Dict]) -> Dict:
        """
        Place VMs onto PMs using BFD algorithm.
        
        Args:
            vms: List of VM specifications with resource demands
            pms: List of PM specifications with resource capacities
            
        Returns:
            placement: Dictionary mapping VM IDs to PM IDs
        """
        logger.info(f"Starting BFD placement for {len(vms)} VMs on {len(pms)} PMs")
        
        # Initialize placement result
        placement = {}
        pm_status = self._initialize_pm_status(pms)
        
        # Sort VMs by total resource demand (decreasing order)
        sorted_vms = self._sort_vms_by_demand(vms)
        
        # Place each VM
        for vm in sorted_vms:
            vm_id = vm['id']
            best_pm = self._find_best_fit_pm(vm, pm_status)
            
            if best_pm is not None:
                # Place VM on best fitting PM
                self._allocate_vm(vm, best_pm, pm_status[best_pm])
                placement[vm_id] = best_pm
                logger.debug(f"Placed VM {vm_id} on PM {best_pm}")
            else:
                logger.warning(f"Could not place VM {vm_id} - no suitable PM found")
        
        logger.info(f"BFD placement completed: {len(placement)}/{len(vms)} VMs placed")
        
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
                'cpu_capacity': pm['cpu_capacity'],
                'memory_capacity': pm['memory_capacity'],
                'storage_capacity': pm.get('storage_capacity', float('inf')),
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
            return (
                vm['cpu_demand'] * 1.0 +
                vm['memory_demand'] * 1.0 +
                vm.get('storage_demand', 0) * 0.5
            )
        
        return sorted(vms, key=compute_demand, reverse=True)
    
    def _find_best_fit_pm(self, vm: Dict, pm_status: Dict) -> int:
        """
        Find the PM with minimum remaining capacity that can fit the VM.
        This creates tighter packing and reduces resource fragmentation.
        """
        best_pm = None
        min_remaining = float('inf')
        
        for pm_id, pm_state in pm_status.items():
            if self._can_fit(vm, pm_state):
                # Calculate remaining capacity after placing this VM
                remaining = self._calculate_remaining_capacity(vm, pm_state)
                
                if remaining < min_remaining:
                    min_remaining = remaining
                    best_pm = pm_id
        
        return best_pm
    
    def _can_fit(self, vm: Dict, pm_state: Dict) -> bool:
        """Check if VM can fit on PM"""
        return (
            vm['cpu_demand'] <= pm_state['cpu_available'] and
            vm['memory_demand'] <= pm_state['memory_available'] and
            vm.get('storage_demand', 0) <= pm_state['storage_available']
        )
    
    def _calculate_remaining_capacity(self, vm: Dict, pm_state: Dict) -> float:
        """
        Calculate total remaining capacity if VM is placed on this PM.
        Lower value means tighter fit.
        """
        cpu_remaining = pm_state['cpu_available'] - vm['cpu_demand']
        memory_remaining = pm_state['memory_available'] - vm['memory_demand']
        storage_remaining = pm_state['storage_available'] - vm.get('storage_demand', 0)
        
        # Normalize by capacity and sum
        cpu_ratio = cpu_remaining / pm_state['cpu_capacity'] if pm_state['cpu_capacity'] > 0 else 0
        memory_ratio = memory_remaining / pm_state['memory_capacity'] if pm_state['memory_capacity'] > 0 else 0
        
        return cpu_ratio + memory_ratio
    
    def _allocate_vm(self, vm: Dict, pm_id: int, pm_state: Dict):
        """Allocate VM to PM and update PM state"""
        pm_state['cpu_available'] -= vm['cpu_demand']
        pm_state['memory_available'] -= vm['memory_demand']
        pm_state['storage_available'] -= vm.get('storage_demand', 0)
        pm_state['vms'].append(vm['id'])
        pm_state['is_active'] = True
