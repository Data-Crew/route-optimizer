# -*- coding: utf-8 -*-
"""
Base class for route optimization algorithms
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import networkx as nx


class BaseSolver(ABC):
    """
    Abstract base class for route optimization algorithms.
    
    All algorithm implementations should inherit from this class
    and implement the solve() method.
    
    Attributes:
        name: Algorithm name
        description: Brief description of what the algorithm does
        use_cases: List of typical use cases
    """
    
    name: str = "Base Solver"
    description: str = "Abstract base class for solvers"
    use_cases: List[str] = []
    
    def __init__(self, graph: nx.MultiDiGraph, start_node: int):
        """
        Initialize the solver.
        
        Args:
            graph: NetworkX graph representing the street network
            start_node: Starting node ID for the route
        """
        self.graph = graph
        self.start_node = start_node
        self._validate_graph()
    
    def _validate_graph(self):
        """Validate that the graph is suitable for solving."""
        if self.graph is None or self.graph.number_of_nodes() == 0:
            raise ValueError("Graph is empty or None")
        
        if self.start_node not in self.graph.nodes:
            raise ValueError(f"Start node {self.start_node} not in graph")
    
    @abstractmethod
    def solve(self) -> Tuple[List[int], float]:
        """
        Solve the routing problem.
        
        Returns:
            Tuple containing:
                - route: List of node IDs representing the optimal route
                - distance: Total distance of the route in meters
        """
        pass
    
    def verify_connectivity(self) -> bool:
        """
        Verify if the graph is strongly connected.
        
        Returns:
            True if the graph is strongly connected
        """
        return nx.is_strongly_connected(self.graph)
    
    def get_main_component(self) -> nx.MultiDiGraph:
        """
        Extract the largest strongly connected component.
        
        Returns:
            Subgraph containing the main strongly connected component
        """
        sccs = list(nx.strongly_connected_components(self.graph))
        
        # Find component containing start_node
        main_component = None
        for scc in sccs:
            if self.start_node in scc:
                main_component = scc
                break
        
        # If start_node not in any component, take the largest
        if main_component is None:
            main_component = max(sccs, key=len)
            # Find closest node in main component
            self._find_alternative_start(main_component)
        
        return self.graph.subgraph(main_component).copy()
    
    def _find_alternative_start(self, component: set):
        """Find an alternative start node within the component."""
        comp_nodes = list(component)
        distances = []
        
        for node in comp_nodes:
            try:
                dist = nx.shortest_path_length(
                    self.graph, self.start_node, node, weight='length'
                )
                distances.append((node, dist))
            except nx.NetworkXNoPath:
                continue
        
        if distances:
            self.start_node = min(distances, key=lambda x: x[1])[0]
            print(f"   📍 Using alternative start node: {self.start_node}")
    
    def calculate_route_distance(self, route: List[int]) -> float:
        """
        Calculate total distance of a route.
        
        Args:
            route: List of node IDs
            
        Returns:
            Total distance in meters
        """
        distance = 0.0
        
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            try:
                edge_data = self.graph.get_edge_data(u, v)
                if edge_data:
                    lengths = [data.get('length', 0) for data in edge_data.values()]
                    distance += min(lengths) if lengths else 0
            except:
                try:
                    dist = nx.shortest_path_length(self.graph, u, v, weight='length')
                    distance += dist
                except nx.NetworkXNoPath:
                    pass
        
        return distance
    
    @classmethod
    def info(cls) -> dict:
        """
        Get algorithm information.
        
        Returns:
            Dictionary with algorithm metadata
        """
        return {
            'name': cls.name,
            'description': cls.description,
            'use_cases': cls.use_cases
        }

