# 🧮 Available Algorithms

Route Optimizer provides multiple algorithms for different optimization problems. Choose the right algorithm based on your use case.

## Quick Reference

| Algorithm | Best For | Coverage | Complexity |
|-----------|----------|----------|------------|
| **CPP** (Chinese Postman) | Street sweeping, enforcement | All edges/streets | O(n³) |
| **TSP** (Traveling Salesman) | Delivery, point visits | All nodes/points | O(n³)* |

*Using Christofides approximation

---

## 🛣️ CPP - Chinese Postman Problem

**Module:** `algorithms.cpp`

### What it does

Finds the shortest route that **traverses every street (edge)** at least once.

```
     A -------- B
     |          |
     |          |
     C -------- D

Goal: Traverse all 4 streets
Route: A → B → D → C → A (covers edges A-B, B-D, D-C, C-A)
Result: ✅ 100% street coverage
```

### When to use CPP

| ✅ Use CPP | ❌ Don't use CPP |
|-----------|------------------|
| Street sweeping | Package delivery |
| Parking enforcement | Sales visits |
| Snow plowing | Equipment installation |
| Pipeline inspection | Tourist routes |
| Garbage collection | Taxi pickups |
| Mail delivery (walking) | Warehouse picking |

### Usage

```python
from route_optimizer import RouteOptimizer

# Using the convenience method
route, distance = optimizer.solve_cpp("full")

# Or explicitly
route, distance = optimizer.solve("full", algorithm="cpp")
```

### How it works

1. **Connectivity check**: Ensures graph is strongly connected
2. **Eulerization**: Duplicates edges to balance node degrees
3. **Eulerian circuit**: Finds path visiting all edges

### Example output

```
🔄 Solving Chinese Postman Problem (CPP)...
   ⚠️  Graph not strongly connected. Extracting main component...
   🔄 Eulerizing graph...
      • 12 unbalanced nodes
      ✅ Eulerized: 245 edges
   🔍 Finding Eulerian circuit...
   ✅ Route found: 246 nodes, 8.45 km
```

---

## 📍 TSP - Traveling Salesman Problem

**Module:** `algorithms.tsp`

### What it does

Finds the shortest route that **visits every point (node)** exactly once.

```
     A -------- B
     |          |
     |          |
     C -------- D

Goal: Visit all 4 intersections
Route: A → B → D → C → A
Result: ✅ All points visited (but not all streets!)
```

### When to use TSP

| ✅ Use TSP | ❌ Don't use TSP |
|-----------|------------------|
| Package delivery | Street sweeping |
| Sales route planning | Parking enforcement |
| Equipment installation | Snow plowing |
| Tourist attraction visits | Pipeline inspection |
| Taxi pickup optimization | Full area coverage |
| Warehouse order picking | Mail routes (walking) |

### Usage

```python
from route_optimizer import RouteOptimizer

# Visit all nodes in the filtered graph
route, distance = optimizer.solve_tsp("full")

# Or visit specific points only
priority_nodes = [123, 456, 789]  # Node IDs
route, distance = optimizer.solve_tsp("full", nodes_to_visit=priority_nodes)

# Explicit algorithm selection
route, distance = optimizer.solve("full", algorithm="tsp")
```

### How it works

1. **Distance matrix**: Computes shortest paths between all node pairs
2. **Christofides algorithm**: 1.5-approximation for metric TSP
3. **Route optimization**: Returns ordered list of nodes to visit

### Example output

```
🔄 Solving Traveling Salesman Problem (TSP)...
   📍 Nodes to visit: 45
   📊 Computing distance matrix...
   🔍 Finding optimal tour...
   ✅ Route found: 46 nodes, 3.21 km
```

### Getting detailed routes

TSP returns only visited nodes. To get all intermediate nodes:

```python
from algorithms import TSPSolver

solver = TSPSolver(graph, start_node)
route, distance = solver.solve()

# Expand to include all nodes along the path
detailed_route = solver.get_detailed_route(route)
```

---

## 📊 Comparison: CPP vs TSP

### Key difference

```
   TSP
    ├── Visits specific POINTS (e.g. delivery addresses)
    ├── Does NOT cover all streets
    └── Best for: deliveries, pickups, sales visits
    
   CPP
    ├── Traverses ALL STREETS in the zone
    ├── Guarantees complete street coverage
    └── Best for: patrol, sweeping, inspection
```

### Visual Example

Consider a 3×3 block grid:

```
   1 -------- 2 -------- 3
   |          |          |
   4 -------- 5 -------- 6
   |          |          |
   7 -------- 8 -------- 9
```

**CPP Result:**
- Traverses all 12 street segments
- Distance: ~12 units (may repeat some edges)
- Coverage: 100% of streets

**TSP Result:**
- Visits all 9 intersections once
- Distance: ~8 units
- Coverage: Only 8 of 12 streets (67%)

### Decision Matrix

| Question | If Yes → | If No → |
|----------|----------|---------|
| Must cover ALL streets? | CPP | TSP |
| Visiting specific points only? | TSP | CPP |
| Full area patrol required? | CPP | Consider TSP |
| Minimizing travel between points? | TSP | CPP |
| Delivery/pickup scenario? | TSP | CPP |
| Inspection of all roads? | CPP | TSP |

---

## 🔧 Direct Solver Usage

For advanced use cases, you can use the solvers directly:

```python
from algorithms import CPPSolver, TSPSolver
import osmnx as ox

# Download a street network
G = ox.graph_from_bbox(bbox=(-57.96, -34.92, -57.94, -34.91), network_type="drive")
start_node = list(G.nodes)[0]

# CPP: Cover all streets
cpp = CPPSolver(G, start_node)
route, distance = cpp.solve()

# TSP: Visit all intersections
tsp = TSPSolver(G, start_node)
route, distance = tsp.solve()

# TSP: Visit specific nodes only
tsp = TSPSolver(G, start_node, nodes_to_visit=[node1, node2, node3])
route, distance = tsp.solve()
```

### Algorithm Information

```python
from algorithms import CPPSolver, TSPSolver

# Get algorithm metadata
print(CPPSolver.info())
# {
#   'name': 'Chinese Postman Problem (CPP)',
#   'description': 'Traverse all edges/streets at least once...',
#   'use_cases': ['Street sweeping', 'Parking enforcement', ...]
# }
```

---

## 🚀 Adding New Algorithms

The system is designed to be extensible. To add a new algorithm:

1. Create a new directory: `algorithms/your_algorithm/`

2. Implement the solver:

```python
# algorithms/your_algorithm/solver.py
from algorithms.base import BaseSolver

class YourSolver(BaseSolver):
    name = "Your Algorithm"
    description = "What it does"
    use_cases = ["Use case 1", "Use case 2"]
    
    def solve(self):
        # Your implementation
        route = [...]
        distance = self.calculate_route_distance(route)
        return route, distance
```

3. Export in `__init__.py`:

```python
# algorithms/your_algorithm/__init__.py
from algorithms.your_algorithm.solver import YourSolver
__all__ = ['YourSolver']
```

4. Register in main `algorithms/__init__.py`:

```python
from algorithms.your_algorithm.solver import YourSolver
__all__ = [..., 'YourSolver']
```

---

## 📚 References

- [Chinese Postman Problem - Wikipedia](https://en.wikipedia.org/wiki/Chinese_postman_problem)
- [Traveling Salesman Problem - Wikipedia](https://en.wikipedia.org/wiki/Traveling_salesman_problem)
- [NetworkX Euler Documentation](https://networkx.org/documentation/stable/reference/algorithms/euler.html)
- [NetworkX TSP Documentation](https://networkx.org/documentation/stable/reference/algorithms/approximation.html)

---

**Version:** 1.0.0  
**Last Updated:** December 2025

