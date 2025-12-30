# 📦 Route Optimizer - Project Summary

A modular route optimization system supporting multiple algorithms for different routing problems.

## 🎯 What is Route Optimizer?

Route Optimizer is a Python framework that solves various route optimization problems using real street networks from OpenStreetMap. It's designed to be:

- **Modular**: Plug-in different algorithms based on your problem
- **Practical**: Works with real street data
- **Extensible**: Easy to add new algorithms

## 🧮 Supported Algorithms

| Algorithm | Type | Use Cases |
|-----------|------|-----------|
| **CPP** (Chinese Postman) | Edge coverage | Street sweeping, patrols, inspections |
| **TSP** (Traveling Salesman) | Node visits | Deliveries, pickups, point routing |

### Future Algorithms (Roadmap)
- VRP (Vehicle Routing Problem)
- CVRP (Capacitated VRP)
- VRPTW (VRP with Time Windows)

## 📁 Project Files

### Core Modules

| File | Description |
|------|-------------|
| `route_optimizer.py` | Main `RouteOptimizer` class |
| `config_loader.py` | JSON configuration loader |
| `zone_config.json` | Example zone configuration |

### Algorithm Implementations

```
algorithms/
├── __init__.py      # Package exports
├── base.py          # Abstract BaseSolver class
├── cpp/
│   └── solver.py    # Chinese Postman Problem
└── tsp/
    └── solver.py    # Traveling Salesman Problem
```

### Scripts & Examples

| File | Description |
|------|-------------|
| `parking_enforcement.py` | CPP example - cover all streets |
| `delivery_route.py` | TSP example - visit delivery points |
| `verify_install.py` | Verify dependencies are installed |
| `optimized_routes.py` | Notebook-style script |

### Infrastructure

| File | Description |
|------|-------------|
| `Dockerfile` | Docker image definition |
| `docker-compose.yml` | Docker Compose setup |
| `Makefile` | Common commands |
| `requirements.txt` | Python dependencies |

### Documentation

| File | Description |
|------|-------------|
| `README.md` | Complete documentation |
| `QUICKSTART.md` | Get started in 3 steps |
| `algorithms.md` | Algorithm reference |

## 🚀 Quick Start

### With Docker

```bash
make build
```

**Option A - Development (interactive shell):**
```bash
make shell
# Inside container:
python parking_enforcement.py  # CPP
python delivery_route.py       # TSP
```

**Option B - Quick execution:**
```bash
docker compose run --rm app python parking_enforcement.py
docker compose run --rm app python delivery_route.py
```

### Without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python verify_install.py

# Run examples
python parking_enforcement.py  # CPP
python delivery_route.py       # TSP
```

## 💻 Basic Usage

```python
from route_optimizer import RouteOptimizer, Zone
from shapely.geometry import Polygon
from datetime import time

# Define zone
zone = Zone(
    name="downtown",
    polygon=Polygon([(-73.99, 40.73), (-73.98, 40.73), 
                     (-73.98, 40.74), (-73.99, 40.74)]),
    start_time=time(8, 0),
    end_time=time(18, 0),
    weekdays=[0, 1, 2, 3, 4],
    color="gold"
)

# Create optimizer
optimizer = RouteOptimizer(
    bbox=(-74.00, 40.72, -73.97, 40.75),
    start_point=(40.735, -73.985),
    zones=[zone]
)

# Download and process
optimizer.download_street_network()
optimizer.label_zones()

# Solve with desired algorithm
route, distance = optimizer.solve_cpp("full")   # Cover all streets
route, distance = optimizer.solve_tsp("full")   # Visit all points
```

## 🔧 Algorithm Selection Guide

```
Do you need to cover ALL streets?
│
├─ YES → Use CPP (Chinese Postman)
│        Examples: sweeping, patrols, inspections
│        Method: optimizer.solve_cpp("zone_name")
│
└─ NO → Use TSP (Traveling Salesman)
        Examples: deliveries, pickups, visits
        Method: optimizer.solve_tsp("zone_name")
```

## 📊 Output Formats

### Excel Export
- **Summary sheet**: Route comparisons
- **Route sheets**: Detailed coordinates (sequence, node_id, lat, lon, zone)

### Visualization
- Zone maps with matplotlib
- Route visualization on street network

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              RouteOptimizer                 │
│  ┌─────────────────────────────────────┐   │
│  │  download_street_network()          │   │
│  │  label_zones()                      │   │
│  │  solve(algorithm="cpp"|"tsp")       │   │
│  │  export_results()                   │   │
│  └─────────────────────────────────────┘   │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
   ┌──────────┐        ┌──────────┐
   │ CPPSolver│        │ TSPSolver│
   │          │        │          │
   │ solve()  │        │ solve()  │
   └──────────┘        └──────────┘
         │                   │
         └─────────┬─────────┘
                   ▼
            ┌────────────┐
            │ BaseSolver │
            │  (abstract)│
            └────────────┘
```

## 🔌 Extending with New Algorithms

1. Create `algorithms/your_algo/solver.py`
2. Inherit from `BaseSolver`
3. Implement `solve()` method
4. Register in `algorithms/__init__.py`

```python
from algorithms.base import BaseSolver

class YourSolver(BaseSolver):
    name = "Your Algorithm"
    
    def solve(self):
        route = [...]  # Your logic
        distance = self.calculate_route_distance(route)
        return route, distance
```

## 📈 Example Applications

| Application | Algorithm | Description |
|-------------|-----------|-------------|
| Street sweeping | CPP | Cover all roads efficiently |
| Snow plowing | CPP | Clear all streets |
| Parking enforcement | CPP | Patrol all meters |
| Package delivery | TSP | Visit delivery addresses |
| Meter reading | TSP | Visit all meter locations |
| Sales routes | TSP | Visit customer locations |
| Garbage collection | CPP | Cover all pickup streets |
| Pipeline inspection | CPP | Inspect all lines |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| Network won't download | Check bbox coordinates |
| Disconnected graph | ✅ Handled automatically |
| Empty results | Verify zone polygons |

## 📚 Documentation Index

1. **[README.md](README.md)** - Complete documentation
2. **[QUICKSTART.md](QUICKSTART.md)** - Get started fast
3. **[algorithms.md](algorithms.md)** - Algorithm details

## 👥 Author

Developed by @PyMap from **Data Crew Consulting**

---

**Version**: 1.0.0  
**License**: MIT  
**Last Updated**: December 2025
