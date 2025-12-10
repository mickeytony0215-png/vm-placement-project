"""
PlanetLab Workload Loader 

This loader reads CPU utilization traces from PlanetLab dataset.
Designed for static VM placement problems using single time-point snapshots.
"""

import os
import random


class PlanetLabLoader:
    """Load VM workload data from PlanetLab traces"""
    
    def __init__(self, data_dir):
        """
        Initialize loader
        
        Args:
            data_dir: Path to planetlab data directory (e.g., 'data/planetlab')
        """
        self.data_dir = data_dir
    
    def get_total_vms(self, date):
        """Get total number of VMs available for a date"""
        date_dir = os.path.join(self.data_dir, date)
        if not os.path.exists(date_dir):
            raise FileNotFoundError(f"Date directory not found: {date_dir}")
        
        files = [f for f in os.listdir(date_dir) 
                if os.path.isfile(os.path.join(date_dir, f))]
        return len(files)
    
    def classify_vm_type(self, cpu_usage):
        """
        Classify VM type based on CPU usage
        
        Returns:
            tuple: (vm_type, ram_ratio)
        """
        if cpu_usage < 30:
            return 'Small', 0.5
        elif cpu_usage < 60:
            return 'Medium', 0.7
        else:
            return 'Large', 1.0
    
    def load_vms(self, date, num_vms, time_point=144, seed=42):
        """
        Load VMs from PlanetLab dataset
        
        Args:
            date: Date string (e.g., '20110303')
            num_vms: Number of VMs to load
            time_point: Time point to extract (0-287, default 144 = 12:00 noon)
            seed: Random seed for reproducibility
            
        Returns:
            list: List of VM dictionaries with 'id', 'type', 'cpu', 'ram'
        """
        random.seed(seed)
        
        date_dir = os.path.join(self.data_dir, date)
        if not os.path.exists(date_dir):
            raise FileNotFoundError(f"Date directory not found: {date_dir}")
        
        # Get all VM files
        all_files = [f for f in os.listdir(date_dir) 
                    if os.path.isfile(os.path.join(date_dir, f))]
        
        total_vms = len(all_files)
        print(f"\n📊 PlanetLab {date} Dataset:")
        print(f"  Total VMs available: {total_vms}")
        
        # Select files
        if num_vms > total_vms:
            print(f"  ⚠️  Requested {num_vms} VMs, but only {total_vms} available")
            num_vms = total_vms
        
        selected_files = random.sample(all_files, num_vms)
        print(f"  Selected: {num_vms} VMs ({num_vms/total_vms*100:.1f}% of total)")
        
        # Load VM data
        vms = []
        vm_stats = {'Small': 0, 'Medium': 0, 'Large': 0}
        skipped = 0
        
        for i, filename in enumerate(selected_files):
            filepath = os.path.join(date_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    lines = f.readlines()
                    
                    # Check if file has enough lines
                    if len(lines) <= time_point:
                        skipped += 1
                        continue
                    
                    # Read CPU usage at specified time point
                    cpu = float(lines[time_point].strip())
                    
                    # Classify VM and determine RAM
                    vm_type, ram_ratio = self.classify_vm_type(cpu)
                    vm_stats[vm_type] += 1
                    
                    vms.append({
                        'id': f'vm_{i}',
                        'name': filename,
                        'type': vm_type,
                        'cpu': cpu,
                        'ram': cpu * ram_ratio
                    })
                    
            except (ValueError, IOError) as e:
                skipped += 1
                continue
        
        if skipped > 0:
            print(f"  ⚠️  Skipped {skipped} invalid files")
        
        print(f"\n  ✓ Successfully loaded {len(vms)} VMs:")
        print(f"    Small:  {vm_stats['Small']:3d} ({vm_stats['Small']/len(vms)*100:5.1f}%)")
        print(f"    Medium: {vm_stats['Medium']:3d} ({vm_stats['Medium']/len(vms)*100:5.1f}%)")
        print(f"    Large:  {vm_stats['Large']:3d} ({vm_stats['Large']/len(vms)*100:5.1f}%)")
        
        return vms
    
    def create_workload_snapshot(self, date, num_vms, time_point=144, seed=42):
        """
        Create a workload snapshot (alias for load_vms for clarity)
        
        This is useful when you want to emphasize that you're taking
        a single time-point snapshot for static placement.
        """
        return self.load_vms(date, num_vms, time_point, seed)


# Example usage
if __name__ == "__main__":
    loader = PlanetLabLoader("../data/planetlab")
    
    # Check dataset size
    try:
        total = loader.get_total_vms('20110303')
        print(f"PlanetLab 20110303 has {total} VMs")
        
        # Load 80 VMs
        vms = loader.load_vms('20110303', num_vms=80)
        
        print(f"\nExample VMs:")
        for vm in vms[:5]:
            print(f"  {vm['id']}: {vm['type']:6s} CPU={vm['cpu']:5.1f} RAM={vm['ram']:5.1f}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease download PlanetLab dataset first:")
        print("  cd data")
        print("  git clone https://github.com/beloglazov/planetlab-workload-traces.git planetlab")