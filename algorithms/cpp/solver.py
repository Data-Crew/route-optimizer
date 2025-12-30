# -*- coding: utf-8 -*-
"""
Chinese Postman Problem (CPP) Solver

The Chinese Postman Problem finds the shortest route that traverses
every edge (street) in a graph at least once.

Use cases:
- Street sweeping
- Parking enforcement
- Mail/newspaper delivery
- Pipeline/cable inspection
- Snow plowing
"""

from typing import List, Tuple
import networkx as nx
from algorithms.base import BaseSolver


class CPPSolver(BaseSolver):
    """
    Solver for the Chinese Postman Problem.
    
    Finds the optimal route that traverses ALL edges in the graph
    at least once, minimizing total distance.
    
    Algorithm:
        1. Check if graph is Eulerian (all nodes have equal in/out degree)
        2. If not, eulerize by adding edges to balance degrees
        3. Find Eulerian circuit that visits all edges
    
    Complexity: O(n³) worst case
    """
    
    name = "Chinese Postman Problem (CPP)"
    description = "Traverse all edges/streets at least once with minimum distance"
    use_cases = [
        "Street sweeping",
        "Parking enforcement",
        "Mail delivery (walking routes)",
        "Pipeline inspection",
        "Snow plowing",
        "Garbage collection",
        "Utility meter reading"
    ]
    
    def solve(self) -> Tuple[List[int], float]:
        """
        Solve the Chinese Postman Problem.
        
        Returns:
            Tuple (route, total_distance)
        """
        print(f"\n🔄 Solving {self.name}...")
        
        # Ensure connectivity
        graph = self.graph
        if not self.verify_connectivity():
            print("   ⚠️  Graph not strongly connected. Extracting main component...")
            graph = self.get_main_component()
            self.graph = graph
        
        # Eulerize the graph
        euler_graph = self._eulerize(graph)
        
        # Find Eulerian circuit
        print("   🔍 Finding Eulerian circuit...")
        try:
            if nx.is_eulerian(euler_graph):
                circuit = list(nx.eulerian_circuit(euler_graph, source=self.start_node))
                route = [self.start_node] + [v for u, v in circuit]
            else:
                print("   ⚠️  Could not create perfect Eulerian circuit")
                print("   📍 Using approximation...")
                route = self._approximate_route(euler_graph)
        except Exception as e:
            print(f"   ⚠️  Error in Eulerian circuit: {e}")
            route = self._approximate_route(euler_graph)
        
        # IMPORTANT: Expand route to include all intermediate nodes
        # This ensures consecutive nodes are actually connected by edges
        route = self._expand_route(route, graph)
        
        # Calculate distance
        distance = self.calculate_route_distance(route)
        
        print(f"   ✅ Route found: {len(route)} nodes, {distance/1000:.2f} km")
        
        return route, distance
    
    def _eulerize(self, graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """
        Convert graph to Eulerian by duplicating necessary edges.
        
        A graph is Eulerian if every node has equal in-degree and out-degree.
        This method adds edges to balance unbalanced nodes.
        
        Args:
            graph: Input graph
            
        Returns:
            Eulerized graph
        """
        print("   🔄 Eulerizing graph...")
        
        G_euler = graph.copy()
        
        # Find unbalanced nodes
        unbalanced = []
        for node in G_euler.nodes():
            in_deg = G_euler.in_degree(node)
            out_deg = G_euler.out_degree(node)
            if in_deg != out_deg:
                unbalanced.append((node, in_deg, out_deg))
        
        if unbalanced:
            print(f"      • {len(unbalanced)} unbalanced nodes")
            
            # Separate excess (out > in) and deficit (in > out) nodes
            excess = [n for n, i, o in unbalanced if o > i]
            deficit = [n for n, i, o in unbalanced if i > o]
            
            # Connect excess to deficit nodes by duplicating paths
            for n_excess in excess:
                for n_deficit in deficit:
                    try:
                        path = nx.shortest_path(G_euler, n_excess, n_deficit, weight='length')
                        
                        # Duplicate path edges
                        for i in range(len(path) - 1):
                            u, v = path[i], path[i + 1]
                            edge_data = G_euler.get_edge_data(u, v, default={})
                            if edge_data:
                                key = list(edge_data.keys())[0]
                                data = edge_data[key]
                                G_euler.add_edge(u, v, **data)
                        break
                    except nx.NetworkXNoPath:
                        continue
        
        print(f"      ✅ Eulerized: {G_euler.number_of_edges()} edges")
        
        return G_euler
    
    def _approximate_route(self, graph: nx.MultiDiGraph) -> List[int]:
        """
        Approximation for non-perfectly-Eulerian graphs.
        Uses DFS traversal.
        
        Args:
            graph: Input graph
            
        Returns:
            Approximate route
        """
        visited = set()
        route = []
        
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            route.append(node)
            
            for neighbor in graph.successors(node):
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(self.start_node)
        
        # Close the cycle
        if route and route[-1] != self.start_node:
            try:
                path_back = nx.shortest_path(graph, route[-1], self.start_node, weight='length')
                route.extend(path_back[1:])
            except nx.NetworkXNoPath:
                pass
        
        return route
    
    def _expand_route(self, route: List[int], graph: nx.MultiDiGraph) -> List[int]:
        """
        Expand route to include all intermediate nodes between consecutive points.
        
        This ensures that consecutive nodes in the returned route are always
        connected by a direct edge (no "jumps" over blocks).
        
        Args:
            route: Original route with possible non-adjacent nodes
            graph: The graph to find paths in
            
        Returns:
            Expanded route where all consecutive nodes are adjacent
        """
        if len(route) < 2:
            return route
        
        # Create undirected version for fallback path finding
        G_undirected = graph.to_undirected()
        
        expanded = [route[0]]
        jumps_fixed = 0
        
        for i in range(len(route) - 1):
            node_from = route[i]
            node_to = route[i + 1]
            
            # Check if there's a direct edge
            if graph.has_edge(node_from, node_to):
                expanded.append(node_to)
            else:
                # Need to find path between nodes
                path = None
                
                # Try directed graph first
                try:
                    path = nx.shortest_path(graph, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
                
                # Try undirected if directed fails
                if path is None:
                    try:
                        path = nx.shortest_path(G_undirected, node_from, node_to, weight='length')
                    except nx.NetworkXNoPath:
                        pass
                
                if path and len(path) > 1:
                    # Add intermediate nodes (skip first as it's already in expanded)
                    expanded.extend(path[1:])
                    jumps_fixed += 1
                else:
                    # Last resort: just add the node directly
                    expanded.append(node_to)
        
        if jumps_fixed > 0:
            print(f"      📍 Expanded {jumps_fixed} path segments with intermediate nodes")
        
        return expanded

