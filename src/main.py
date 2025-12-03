"""
Virtual Machine Placement Problem - Main Entry Point
"""
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

from algorithms.ffd import FirstFitDecreasing
from algorithms.bfd import BestFitDecreasing
from algorithms.nlp_solver import NLPSolver
from algorithms.rls_ffd import RandomizedLocalSearchFFD
from utils.data_loader import load_vm_pm_data
from utils.vm_generator import generate_vms
from utils.pm_generator import generate_pms
from evaluation.metrics import evaluate_placement

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='VM Placement Problem Solver')
    
    parser.add_argument(
        '--algorithm',
        type=str,
        choices=['nlp', 'ffd', 'bfd', 'rls-ffd', 'all'],
        default='all',
        help='Algorithm to run'
    )
    
    parser.add_argument(
        '--scale',
        type=str,
        choices=['small', 'medium', 'all'],
        default='small',
        help='Problem scale'
    )
    
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='Path to custom data file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--run-all',
        action='store_true',
        help='Run all algorithms on all scales'
    )
    
    return parser.parse_args()


def run_algorithm(algorithm_name, vms, pms, scale):
    """Run a specific algorithm"""
    logger.info(f"Running {algorithm_name} on {scale} scale problem")
    
    # Initialize algorithm
    if algorithm_name == 'nlp':
        algorithm = NLPSolver()
    elif algorithm_name == 'ffd':
        algorithm = FirstFitDecreasing()
    elif algorithm_name == 'bfd':
        algorithm = BestFitDecreasing()
    elif algorithm_name == 'rls-ffd':
        algorithm = RandomizedLocalSearchFFD()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
    
    # Run placement
    start_time = datetime.now()
    placement = algorithm.place(vms, pms)
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Evaluate results
    metrics = evaluate_placement(placement, vms, pms)
    metrics['execution_time'] = execution_time
    metrics['algorithm'] = algorithm_name
    metrics['scale'] = scale
    
    logger.info(f"Completed {algorithm_name}: {metrics}")
    
    return placement, metrics


def generate_problem_instance(scale):
    """Generate VM and PM problem instance"""
    if scale == 'small':
        # Small scale: 5 PMs, 25 VMs
        num_pms = 5
        num_vms = 25
    elif scale == 'medium':
        # Medium scale: 15 PMs, 80 VMs
        num_pms = 15
        num_vms = 80
    else:
        raise ValueError(f"Unknown scale: {scale}")
    
    logger.info(f"Generating {scale} scale problem: {num_pms} PMs, {num_vms} VMs")
    
    vms = generate_vms(num_vms)
    pms = generate_pms(num_pms)
    
    return vms, pms


def main():
    """Main function"""
    args = parse_arguments()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine algorithms and scales to run
    if args.run_all:
        algorithms = ['nlp', 'ffd', 'bfd', 'rls-ffd']
        scales = ['small', 'medium']
    else:
        algorithms = [args.algorithm] if args.algorithm != 'all' else ['nlp', 'ffd', 'bfd', 'rls-ffd']
        scales = [args.scale] if args.scale != 'all' else ['small', 'medium']
    
    # Run experiments
    all_results = []
    
    for scale in scales:
        # Load or generate data
        if args.data_path:
            vms, pms = load_vm_pm_data(args.data_path)
        else:
            vms, pms = generate_problem_instance(scale)
        
        # Skip NLP for medium scale (too slow)
        current_algorithms = algorithms.copy()
        if scale == 'medium' and 'nlp' in current_algorithms:
            logger.warning("Skipping NLP for medium scale (computational limitation)")
            current_algorithms.remove('nlp')
        
        # Run each algorithm
        for algo in current_algorithms:
            try:
                placement, metrics = run_algorithm(algo, vms, pms, scale)
                all_results.append(metrics)
            except Exception as e:
                logger.error(f"Error running {algo} on {scale} scale: {e}")
    
    # Save results
    results_file = output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    logger.info(f"Saving results to {results_file}")
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4)
        logger.info("✅ JSON Data saved successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to save results: {e}")
    
    logger.info("All experiments completed!")


if __name__ == "__main__":
    main()
