# -*- coding: utf-8 -*-
"""
Traveling Salesman Problem (TSP) Solver

The Traveling Salesman Problem finds the shortest route that visits
every node (location) exactly once and returns to the starting point.

Use cases:
- Package delivery
- Sales visits
- Equipment installation
- Tourist route planning
"""

from typing import List, Tuple, Optional
import networkx as nx
from algorithms.base import BaseSolver


class TSPSolver(BaseSolver):
    """
    Solver for the Traveling Salesman Problem.
    
    Finds the optimal route that visits ALL nodes exactly once,
    minimizing total distance.
    
    Algorithm:
        Uses NetworkX's traveling_salesman_problem approximation
        which implements Christofides algorithm (1.5-approximation)
        for metric TSP.
    
    Complexity: O(n³) for Christofides approximation
    
    Note:
        TSP is NP-hard for exact solutions. This implementation
        uses approximation algorithms suitable for practical use.
    """
    
    name = "Traveling Salesman Problem (TSP)"
    description = "Visit all nodes/points exactly once with minimum distance"
    use_cases = [
        "Package delivery",
        "Sales route optimization",
        "Equipment installation visits",
        "Tourist attraction routing",
        "Taxi pickup optimization",
        "Warehouse picking routes",
        "Field service scheduling"
    ]
    
    def __init__(self, graph: nx.MultiDiGraph, start_node: int, 
                 nodes_to_visit: Optional[List[int]] = None):
        """
        Initialize TSP solver.
        
        Args:
            graph: NetworkX graph
            start_node: Starting node ID
            nodes_to_visit: Optional list of specific nodes to visit.
                          If None, visits all nodes in the graph.
        """
        super().__init__(graph, start_node)
        self.nodes_to_visit = nodes_to_visit or list(graph.nodes())
        
        if self.start_node not in self.nodes_to_visit:
            self.nodes_to_visit.insert(0, self.start_node)
    
    def solve(self) -> Tuple[List[int], float]:
        """
        Solve the Traveling Salesman Problem.
        
        Returns:
            Tuple (route, total_distance)
        """
        print(f"\n🔄 Solving {self.name}...")
        print(f"   📍 Nodes to visit: {len(self.nodes_to_visit)}")
        
        # Ensure connectivity
        graph = self.graph
        if not self.verify_connectivity():
            print("   ⚠️  Graph not strongly connected. Extracting main component...")
            graph = self.get_main_component()
            self.graph = graph
            # Filter nodes_to_visit to only include nodes in the component
            self.nodes_to_visit = [n for n in self.nodes_to_visit if n in graph.nodes()]
        
        # Create distance matrix for nodes to visit
        print("   📊 Computing distance matrix...")
        subgraph = self._create_complete_subgraph()
        
        # Solve TSP
        print("   🔍 Finding optimal tour...")
        try:
            route = self._solve_tsp(subgraph)
        except Exception as e:
            print(f"   ⚠️  TSP solver failed: {e}")
            print("   📍 Using greedy approximation...")
            route = self._greedy_tsp()
        
        # Ensure route starts from start_node
        route = self._rotate_to_start(route)
        
        # Calculate distance using actual paths
        distance = self._calculate_actual_distance(route)
        
        # IMPORTANT: Expand route to include all intermediate nodes
        # This ensures consecutive nodes are actually connected by edges
        expanded_route = self.get_detailed_route(route)
        
        print(f"   ✅ Route found: {len(route)} stops, {len(expanded_route)} total nodes, {distance/1000:.2f} km")
        
        return expanded_route, distance
    
    def _create_complete_subgraph(self) -> nx.Graph:
        """
        Create a complete graph with shortest path distances between nodes.
        
        Returns:
            Complete weighted graph
        """
        complete = nx.Graph()
        
        for i, node_i in enumerate(self.nodes_to_visit):
            for node_j in self.nodes_to_visit[i + 1:]:
                try:
                    # Calculate shortest path distance
                    dist = nx.shortest_path_length(
                        self.graph, node_i, node_j, weight='length'
                    )
                    complete.add_edge(node_i, node_j, weight=dist)
                except nx.NetworkXNoPath:
                    # If no path, add very large weight
                    complete.add_edge(node_i, node_j, weight=float('inf'))
        
        return complete
    
    def _solve_tsp(self, complete_graph: nx.Graph) -> List[int]:
        """
        Solve TSP using NetworkX's approximation algorithm.
        
        Args:
            complete_graph: Complete weighted graph
            
        Returns:
            Ordered list of nodes
        """
        # Use Christofides algorithm (available in NetworkX)
        try:
            from networkx.algorithms.approximation import traveling_salesman_problem
            route = traveling_salesman_problem(
                complete_graph, 
                weight='weight',
                cycle=True
            )
            return route
        except ImportError:
            # Fallback to greedy if approximation module not available
            return self._greedy_tsp()
    
    def _greedy_tsp(self) -> List[int]:
        """
        Greedy nearest-neighbor TSP approximation.
        
        Returns:
            Approximate route
        """
        unvisited = set(self.nodes_to_visit)
        route = [self.start_node]
        unvisited.discard(self.start_node)
        
        current = self.start_node
        
        while unvisited:
            # Find nearest unvisited node
            nearest = None
            min_dist = float('inf')
            
            for node in unvisited:
                try:
                    dist = nx.shortest_path_length(
                        self.graph, current, node, weight='length'
                    )
                    if dist < min_dist:
                        min_dist = dist
                        nearest = node
                except nx.NetworkXNoPath:
                    continue
            
            if nearest is None:
                break
            
            route.append(nearest)
            unvisited.discard(nearest)
            current = nearest
        
        # Return to start
        route.append(self.start_node)
        
        return route
    
    def _rotate_to_start(self, route: List[int]) -> List[int]:
        """
        Rotate route so it starts from start_node.
        
        Args:
            route: Original route
            
        Returns:
            Rotated route
        """
        if self.start_node not in route:
            return route
        
        # Remove closing node if it's a cycle
        if route[0] == route[-1]:
            route = route[:-1]
        
        # Find start_node position
        idx = route.index(self.start_node)
        
        # Rotate
        rotated = route[idx:] + route[:idx]
        
        # Add closing node
        rotated.append(rotated[0])
        
        return rotated
    
    def _calculate_actual_distance(self, route: List[int]) -> float:
        """
        Calculate actual distance following shortest paths between nodes.
        
        Args:
            route: List of nodes
            
        Returns:
            Total distance in meters
        """
        distance = 0.0
        
        for i in range(len(route) - 1):
            try:
                dist = nx.shortest_path_length(
                    self.graph, route[i], route[i + 1], weight='length'
                )
                distance += dist
            except nx.NetworkXNoPath:
                pass
        
        return distance
    
    def get_detailed_route(self, route: List[int]) -> List[int]:
        """
        Expand TSP route to include all intermediate nodes.
        
        The TSP route only includes visited nodes. This method
        expands it to include all nodes along the shortest paths.
        
        Args:
            route: TSP route (visited nodes only)
            
        Returns:
            Expanded route with all intermediate nodes
        """
        if len(route) < 2:
            return route
        
        # Create undirected version for fallback
        G_undirected = self.graph.to_undirected()
        
        detailed = []
        jumps_expanded = 0
        
        for i in range(len(route) - 1):
            node_from = route[i]
            node_to = route[i + 1]
            
            path = None
            
            # Try directed graph first
            if self.graph.has_edge(node_from, node_to):
                path = [node_from, node_to]
            else:
                try:
                    path = nx.shortest_path(self.graph, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
            
            # Try undirected if directed fails
            if path is None:
                try:
                    path = nx.shortest_path(G_undirected, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
            
            if path:
                if len(path) > 2:
                    jumps_expanded += 1
                if detailed:
                    detailed.extend(path[1:])  # Skip first to avoid duplicates
                else:
                    detailed.extend(path)
            else:
                # Last resort: direct jump
                if not detailed:
                    detailed.append(node_from)
                detailed.append(node_to)
        
        if jumps_expanded > 0:
            print(f"      📍 Expanded {jumps_expanded} path segments with intermediate nodes")
        
        return detailed

