"""
Unit tests for VM Placement algorithms
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from algorithms.ffd import FirstFitDecreasing
from algorithms.bfd import BestFitDecreasing
from algorithms.nlp_solver import NLPSolver
from utils.vm_generator import generate_vms
from utils.pm_generator import generate_pms
from evaluation.metrics import evaluate_placement


class TestVMGeneration:
    """Test VM generation functions"""
    
    def test_generate_vms_basic(self):
        """Test basic VM generation"""
        vms = generate_vms(10)
        assert len(vms) == 10
        assert all('id' in vm for vm in vms)
        assert all('cpu_demand' in vm for vm in vms)
        assert all('memory_demand' in vm for vm in vms)
    
    def test_vm_resource_demands(self):
        """Test VM resource demands are positive"""
        vms = generate_vms(20)
        for vm in vms:
            assert vm['cpu_demand'] > 0
            assert vm['memory_demand'] > 0


class TestPMGeneration:
    """Test PM generation functions"""
    
    def test_generate_pms_basic(self):
        """Test basic PM generation"""
        pms = generate_pms(5)
        assert len(pms) == 5
        assert all('id' in pm for pm in pms)
        assert all('cpu_capacity' in pm for pm in pms)
        assert all('memory_capacity' in pm for pm in pms)
    
    def test_pm_capacities(self):
        """Test PM capacities are positive"""
        pms = generate_pms(10)
        for pm in pms:
            assert pm['cpu_capacity'] > 0
            assert pm['memory_capacity'] > 0


class TestFFDAlgorithm:
    """Test First Fit Decreasing algorithm"""
    
    def test_ffd_basic_placement(self):
        """Test basic FFD placement"""
        vms = generate_vms(10, seed=42)
        pms = generate_pms(5, seed=42)
        
        ffd = FirstFitDecreasing()
        result = ffd.place(vms, pms)
        
        assert 'placement' in result
        assert 'pm_status' in result
        assert len(result['placement']) <= len(vms)
    
    def test_ffd_feasibility(self):
        """Test FFD produces feasible placement"""
        vms = generate_vms(15, seed=123)
        pms = generate_pms(10, seed=123)
        
        ffd = FirstFitDecreasing()
        result = ffd.place(vms, pms)
        
        # Check no PM is overloaded
        pm_status = result['pm_status']
        for pm_state in pm_status.values():
            if pm_state['is_active']:
                assert pm_state['cpu_available'] >= 0
                assert pm_state['memory_available'] >= 0


class TestBFDAlgorithm:
    """Test Best Fit Decreasing algorithm"""
    
    def test_bfd_basic_placement(self):
        """Test basic BFD placement"""
        vms = generate_vms(10, seed=42)
        pms = generate_pms(5, seed=42)
        
        bfd = BestFitDecreasing()
        result = bfd.place(vms, pms)
        
        assert 'placement' in result
        assert 'pm_status' in result
        assert len(result['placement']) <= len(vms)
    
    def test_bfd_vs_ffd_comparison(self):
        """Test BFD vs FFD on same instance"""
        vms = generate_vms(20, seed=456)
        pms = generate_pms(10, seed=456)
        
        ffd = FirstFitDecreasing()
        bfd = BestFitDecreasing()
        
        result_ffd = ffd.place(vms, pms)
        result_bfd = bfd.place(vms, pms)
        
        # Both should place same number of VMs
        assert len(result_ffd['placement']) == len(result_bfd['placement'])


class TestEvaluationMetrics:
    """Test evaluation metrics"""
    
    def test_evaluate_placement(self):
        """Test placement evaluation"""
        vms = generate_vms(15, seed=789)
        pms = generate_pms(8, seed=789)
        
        ffd = FirstFitDecreasing()
        result = ffd.place(vms, pms)
        
        metrics = evaluate_placement(result, vms, pms)
        
        assert 'active_pms' in metrics
        assert 'total_energy' in metrics
        assert 'avg_cpu_utilization' in metrics
        assert 'placement_rate' in metrics
        
        # Check metric ranges
        assert metrics['active_pms'] >= 0
        assert metrics['active_pms'] <= len(pms)
        assert 0 <= metrics['placement_rate'] <= 1


def test_integration_small_scale():
    """Integration test for small scale problem"""
    # Small scale: 5 PMs, 25 VMs
    vms = generate_vms(25, seed=100)
    pms = generate_pms(5, seed=100)
    
    # Test all algorithms
    algorithms = [
        FirstFitDecreasing(),
        BestFitDecreasing()
    ]
    
    for algo in algorithms:
        result = algo.place(vms, pms)
        metrics = evaluate_placement(result, vms, pms)
        
        # Basic sanity checks
        assert metrics['active_pms'] > 0
        assert metrics['placement_rate'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
