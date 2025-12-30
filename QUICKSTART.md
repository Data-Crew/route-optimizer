# 🚀 Quick Start - Route Optimizer

Get up and running in 3 steps.

## ⚡ Step 1: Install

### With Docker (Recommended)

```bash
git clone <repository-url>
cd route-optimizer
make build
```

### Without Docker

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get install gdal-bin libgdal-dev libgeos-dev libproj-dev libspatialindex-dev

# macOS
brew install gdal geos proj spatialindex

# Python setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify everything works
python verify_install.py
```

---

## ⚡ Step 2: Run an Example

### Available Examples

| Example | Algorithm | Use Case |
|---------|-----------|----------|
| `parking_enforcement.py` | **CPP** | Cover all streets (patrol, sweeping) |
| `delivery_route.py` | **TSP** | Visit specific points (delivery) |

### With Docker

**Option A - Development (interactive shell):**

Enter the container and work from bash. Best for development.

```bash
make shell
# Now inside the container:
python parking_enforcement.py  # CPP
python delivery_route.py       # TSP
```

**Option B - Quick execution (run directly):**

Run scripts without entering the container. Best for one-off runs.

```bash
docker compose run --rm app python parking_enforcement.py
docker compose run --rm app python delivery_route.py
```

### Without Docker

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run examples
python parking_enforcement.py  # CPP
python delivery_route.py       # TSP
```

---

## ⚡ Step 3: Check Results

### Parking Enforcement Example (CPP)
- `output/zone_map.png` → Visual map of zones
- `output/enforcement_routes.xlsx` → Patrol routes covering all streets

### Delivery Route Example (TSP)  
- `output/delivery_routes.xlsx` → Optimized delivery sequence

---

## 🧮 Which Algorithm Do I Need?

```
Do I need to cover ALL streets?
│
├─ YES → Use CPP
│        Run: python parking_enforcement.py
│        Examples: street sweeping, patrol, inspection
│
└─ NO → Use TSP  
        Run: python delivery_route.py
        Examples: deliveries, pickups, visits
```

### In Code

```python
from route_optimizer import RouteOptimizer

# CPP: Cover all streets
route, distance = optimizer.solve_cpp("zone_name")

# TSP: Visit all points
route, distance = optimizer.solve_tsp("zone_name")

# TSP: Visit specific points only
route, distance = optimizer.solve_tsp("zone_name", nodes_to_visit=[n1, n2, n3])
```

---

## ⚙️ Customize Your Area

Edit `zone_config.json`:

```json
{
  "configuration": {
    "bbox": {
      "west": -74.00,
      "south": 40.72,
      "east": -73.97,
      "north": 40.75
    },
    "start_point": {
      "latitude": 40.735,
      "longitude": -73.985
    }
  },
  "zones": [
    {
      "name": "my_zone",
      "polygon": [
        [-73.99, 40.73],
        [-73.98, 40.73],
        [-73.98, 40.74],
        [-73.99, 40.74]
      ],
      "color": "blue"
    }
  ]
}
```

### Getting Coordinates

1. Go to **Google Maps**
2. Right click → "What's here?"
3. Copy coordinates

⚠️ **Important**: JSON format is `[longitude, latitude]` (reversed!)

---

## 🔧 Common Issues

| Problem | Solution |
|---------|----------|
| Network doesn't download | Check bbox coordinates |
| "Not strongly connected" | ✅ Handled automatically |
| Import error | Run `pip install -r requirements.txt` |
| Empty results | Check zone polygons cover streets |

---

## 📚 Next Steps

- [README.md](README.md) - Full documentation
- [algorithms.md](algorithms.md) - Algorithm details
- Customize `zone_config.json` for your area

---

**Tip**: Start with an example, then modify the configuration for your needs! 🎯
