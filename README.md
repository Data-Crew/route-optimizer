# 🚗 Route Optimizer

A modular route optimization system supporting multiple algorithms for different routing problems.

## 📋 Description

**Route Optimizer** is a flexible framework for solving various route optimization problems using real street networks from OpenStreetMap. It provides a pluggable architecture where different algorithms can be applied depending on your use case.

### Supported Algorithms

| Algorithm | Problem Type | Best For |
|-----------|--------------|----------|
| **CPP** (Chinese Postman) | Edge coverage | Street sweeping, patrol routes, inspections |
| **TSP** (Traveling Salesman) | Node visits | Deliveries, pickups, point-to-point routes |

The system is designed to be **extensible** - new algorithms (VRP, CVRP, etc.) can be added easily.

## ✨ Features

- 🧮 **Multiple algorithms** - CPP, TSP, with extensible architecture
- 🗺️ **Real street networks** - Downloads from OpenStreetMap
- 📍 **Zone-based routing** - Define areas with polygons
- 📊 **Excel export** - Detailed route coordinates
- 🎨 **Visualization** - Map plots with matplotlib
- ⚙️ **JSON configuration** - Easy setup and maintenance
- 🐳 **Docker support** - Quick setup with all dependencies

## 🚀 Installation

### Option 1: Docker (Recommended) 🐳

Docker handles all geospatial dependencies (GDAL, GEOS, PROJ) automatically.

```bash
git clone <repository-url>
cd route-optimizer
make build
```

**Option A - Development (interactive shell):**

Best for development and experimentation. Enter the container and run scripts manually.

```bash
make shell
# Now inside the container:
python parking_enforcement.py  # CPP example
python delivery_route.py       # TSP example
```

**Option B - Quick execution (run directly):**

Best for one-off runs without entering the container.

```bash
docker compose run --rm app python parking_enforcement.py
docker compose run --rm app python delivery_route.py
```

### Option 2: Virtual Environment

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get install gdal-bin libgdal-dev libgeos-dev libproj-dev libspatialindex-dev

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify installation
python verify_install.py

# Run examples
python parking_enforcement.py  # CPP - cover all streets
python delivery_route.py       # TSP - visit points
```

See [QUICKSTART.md](QUICKSTART.md) for detailed installation instructions.

## 📁 Project Structure

```
route-optimizer/
├── algorithms/                    # 🧮 Algorithm implementations
│   ├── base.py                   # Abstract base solver
│   ├── cpp/                      # Chinese Postman Problem
│   │   └── solver.py
│   └── tsp/                      # Traveling Salesman Problem
│       └── solver.py
├── route_optimizer.py             # Main RouteOptimizer class
├── config_loader.py               # JSON configuration loader
├── zone_config.json               # Example configuration
├── parking_enforcement.py # CPP example (cover all streets)
├── delivery_route.py      # TSP example (visit points)
├── verify_install.py              # Verify dependencies
├── algorithms.md                  # Algorithm documentation
├── Dockerfile                     # Docker setup
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## 🎯 Quick Start

### Basic Usage

```python
from route_optimizer import RouteOptimizer, Zone
from shapely.geometry import Polygon
from datetime import time

# Define your area
zone = Zone(
    name="downtown",
    polygon=Polygon([
        (-73.99, 40.73), (-73.98, 40.73),
        (-73.98, 40.74), (-73.99, 40.74),
    ]),
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

# Download street network
optimizer.download_street_network()
optimizer.label_zones()

# Solve with CPP (cover all streets)
route, distance = optimizer.solve_cpp("full")

# Or solve with TSP (visit all intersections)
route, distance = optimizer.solve_tsp("full")
```

### Using JSON Configuration

```python
from config_loader import load_configuration
from route_optimizer import RouteOptimizer

bbox, start_point, zones, _ = load_configuration('zone_config.json')
optimizer = RouteOptimizer(bbox, start_point, zones)
```

## 🧮 Choosing the Right Algorithm

| Your Problem | Algorithm | Method |
|--------------|-----------|--------|
| Cover **all streets** in an area | CPP | `solve_cpp()` |
| Visit **specific points** | TSP | `solve_tsp()` |
| Patrol/sweep entire neighborhood | CPP | `solve_cpp()` |
| Deliver packages to addresses | TSP | `solve_tsp()` |
| Inspect all roads | CPP | `solve_cpp()` |
| Pick up items at locations | TSP | `solve_tsp()` |

📚 See [algorithms.md](algorithms.md) for detailed algorithm documentation.

## 📊 Example Use Cases

### 1. Street Sweeping / Snow Plowing (CPP)

Cover every street in the city with minimum repeated travel.

```python
route, distance = optimizer.solve_cpp("full")
print(f"Route covers all streets in {distance/1000:.1f} km")
```

### 2. Delivery Route (TSP)

Visit specific delivery points efficiently.

```python
delivery_points = [node1, node2, node3, node4]
route, distance = optimizer.solve_tsp("full", nodes_to_visit=delivery_points)
```

### 3. Parking Enforcement Patrol (CPP)

Ensure all parking meters are checked.

```python
route, distance = optimizer.solve_cpp("downtown_zone")
optimizer.export_results({"patrol": (route, distance)}, "patrol_routes.xlsx")
```

### 4. Utility Meter Reading (TSP)

Visit all meter locations.

```python
route, distance = optimizer.solve_tsp("full")
detailed_route = solver.get_detailed_route(route)  # Include intermediate nodes
```

## ⚙️ Configuration

### Zone Definition (JSON)

```json
{
  "configuration": {
    "bbox": {"west": -74.00, "south": 40.72, "east": -73.97, "north": 40.75},
    "start_point": {"latitude": 40.735, "longitude": -73.985}
  },
  "zones": [
    {
      "name": "downtown",
      "polygon": [[-73.99, 40.73], [-73.98, 40.73], [-73.98, 40.74], [-73.99, 40.74]],
      "schedule": {"start": "08:00", "end": "18:00"},
      "weekdays": [0, 1, 2, 3, 4],
      "color": "gold"
    }
  ],
  "route_types": {
    "full": {"zones": ["downtown", "midtown"]},
    "morning": {"zones": ["downtown"]}
  }
}
```

### Getting Coordinates

1. **Google Maps**: Right click → "What's here?"
2. **OpenStreetMap**: Shift+Click
3. **GeoJSON.io**: Draw polygon and export

⚠️ **Format**: `[longitude, latitude]` (reversed from typical lat/lon!)

## 📈 Output

### Excel Export

```python
results = {
    "full_coverage": optimizer.solve_cpp("full"),
    "delivery_route": optimizer.solve_tsp("full", nodes_to_visit=points)
}
optimizer.export_results(results, "routes.xlsx")
```

**Output sheets:**
- **Summary**: Distance comparison for all routes
- **Per-route sheets**: Sequence, Node_ID, Latitude, Longitude, Zone

### Visualization

```python
optimizer.visualize_zones(save_path="map.png")
optimizer.visualize_route(route, graph, "My Route", save_path="route.png")
```

## 🔧 Extending with New Algorithms

The system is built for extensibility. To add a new algorithm:

```python
# algorithms/vrp/solver.py
from algorithms.base import BaseSolver

class VRPSolver(BaseSolver):
    name = "Vehicle Routing Problem"
    description = "Multiple vehicles, capacity constraints"
    use_cases = ["Fleet delivery", "Logistics"]
    
    def solve(self):
        # Your implementation
        route = [...]
        distance = self.calculate_route_distance(route)
        return route, distance
```

Then register in `algorithms/__init__.py`.

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Network doesn't download | Check bbox coordinates and internet |
| "Not strongly connected" | ✅ Handled automatically |
| Empty results | Verify zone polygons cover the area |
| Import errors | Install dependencies: `pip install -r requirements.txt` |

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 3 steps
- [algorithms.md](algorithms.md) - Detailed algorithm documentation
- [SUMMARY.md](SUMMARY.md) - Project overview

## 🔜 Roadmap

- [ ] VRP (Vehicle Routing Problem) - multiple vehicles
- [ ] CVRP (Capacitated VRP) - vehicle capacity constraints
- [ ] Time windows support
- [ ] Interactive web interface
- [ ] Google Maps/Mapbox integration
- [ ] Real-time traffic consideration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your algorithm in `algorithms/your_algorithm/`
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 👥 Author

Developed by **Data Crew Consulting**

---

**Version**: 1.0.0  
**Last updated**: December 2025
