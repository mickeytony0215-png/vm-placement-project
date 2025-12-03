"""
VM Placement Algorithms
"""

from .ffd import FirstFitDecreasing
from .bfd import BestFitDecreasing
from .nlp_solver import NLPSolver
from .rls_ffd import RandomizedLocalSearchFFD

__all__ = [
    'FirstFitDecreasing',
    'BestFitDecreasing',
    'NLPSolver',
    'RandomizedLocalSearchFFD'
]
