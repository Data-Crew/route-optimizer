# -*- coding: utf-8 -*-
"""
Route Optimization Algorithms
=============================

This package provides different algorithms for route optimization:

- **CPP (Chinese Postman Problem)**: Traverse all edges/streets at least once
- **TSP (Traveling Salesman Problem)**: Visit all nodes/points exactly once

Usage:
    from algorithms import CPPSolver, TSPSolver
    
    # For street sweeping, enforcement, inspection
    solver = CPPSolver(graph, start_node)
    route, distance = solver.solve()
    
    # For delivery, visiting specific points
    solver = TSPSolver(graph, start_node)
    route, distance = solver.solve()
"""

from algorithms.base import BaseSolver
from algorithms.cpp.solver import CPPSolver
from algorithms.tsp.solver import TSPSolver

__all__ = ['BaseSolver', 'CPPSolver', 'TSPSolver']

