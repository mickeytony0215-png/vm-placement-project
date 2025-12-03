"""
Data Loader for VM Placement Problem
"""
import json
import logging
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def load_vm_pm_data(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Load VM and PM data from file.
    
    Supports JSON format with the following structure:
    {
        "vms": [
            {"id": 0, "cpu_demand": 2, "memory_demand": 4, ...},
            ...
        ],
        "pms": [
            {"id": 0, "cpu_capacity": 16, "memory_capacity": 32, ...},
            ...
        ]
    }
    
    Args:
        file_path: Path to data file
        
    Returns:
        Tuple of (vms, pms)
    """
    logger.info(f"Loading data from {file_path}")
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    if path.suffix == '.json':
        return load_json_data(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def load_json_data(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """Load data from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    vms = data.get('vms', [])
    pms = data.get('pms', [])
    
    logger.info(f"Loaded {len(vms)} VMs and {len(pms)} PMs")
    
    return vms, pms


def save_vm_pm_data(vms: List[Dict], pms: List[Dict], file_path: str):
    """
    Save VM and PM data to JSON file.
    
    Args:
        vms: List of VM specifications
        pms: List of PM specifications
        file_path: Output file path
    """
    logger.info(f"Saving data to {file_path}")
    
    data = {
        'vms': vms,
        'pms': pms
    }
    
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {len(vms)} VMs and {len(pms)} PMs")


def load_planetlab_trace(trace_file: str, num_vms: int = None) -> List[Dict]:
    """
    Load VM workload from PlanetLab trace data.
    
    Args:
        trace_file: Path to PlanetLab trace file
        num_vms: Number of VMs to load (None = all)
        
    Returns:
        List of VM specifications with workload traces
    """
    # TODO: Implement PlanetLab trace loading
    logger.warning("PlanetLab trace loading not yet implemented")
    return []
