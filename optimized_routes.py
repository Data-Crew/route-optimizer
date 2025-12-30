# %% [markdown]
# # 🚗 Route Optimizer - Parking Enforcement
# 
# This notebook implements the **Chinese Postman Problem** to optimize enforcement routes.
# 
# ## Key differences:
# - ❌ **TSP** (Traveling Salesman): Visits nodes → Package delivery
# - ✅ **CPP** (Chinese Postman): Traverses edges → Street sweeping
#
# ## Process:
# 1. Download street network (OpenStreetMap)
# 2. Define zones with polygons
# 3. Label nodes by zone
# 4. Solve CPP for different routes
# 5. Export results to Excel

# %% [markdown]
# ## 1️⃣ Install Dependencies

# %%
!pip install osmnx networkx pandas geopandas matplotlib shapely openpyxl -q

# %% [markdown]
# ## 2️⃣ Import Modules

# %%
import sys
sys.path.append('/home/claude')

from route_optimizer import RouteOptimizer, Zone
from config_loader import load_configuration
from shapely.geometry import Polygon
from datetime import time
import warnings
warnings.filterwarnings('ignore')

print("✅ Modules imported successfully")

# %% [markdown]
# ## 3️⃣ Zone Configuration
# 
# ### Option A: Define zones manually

# %%
# BBOX: (west, south, east, north) 
# For La Plata, Argentina
bbox = (-57.9605, -34.9210, -57.9455, -34.9095)

# Start and return point (lat, lon)
start_point = (-34.91719, -57.95067)  # Corner of 12th and 50th

# Define zones with polygons
zones = [
    Zone(
        name="courthouse",
        polygon=Polygon([
            (-57.957, -34.915),
            (-57.949, -34.915),
            (-57.949, -34.911),
            (-57.957, -34.911),
        ]),
        start_time=time(8, 0),
        end_time=time(14, 0),
        weekdays=[0, 1, 2, 3, 4],  # Monday to Friday
        color="pink"
    ),
    Zone(
        name="downtown",
        polygon=Polygon([
            (-57.955, -34.9145),
            (-57.9475, -34.9145),
            (-57.9475, -34.9185),
            (-57.955, -34.9185),
        ]),
        start_time=time(8, 0),
        end_time=time(20, 0),
        weekdays=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
        color="gold"
    ),
    Zone(
        name="12th_street",
        polygon=Polygon([
            (-57.955, -34.9125),
            (-57.952, -34.9125),
            (-57.952, -34.9195),
            (-57.955, -34.9195),
        ]),
        start_time=time(8, 0),
        end_time=time(20, 0),
        weekdays=[0, 1, 2, 3, 4, 5],  # Monday to Saturday
        color="violet"
    ),
]

print(f"✅ {len(zones)} zones configured")

# %% [markdown]
# ### Option B: Load from JSON file (alternative)

# %%
# Uncomment to use JSON configuration:
# bbox, start_point, zones, route_types = load_configuration('/home/claude/zone_config.json')
# print(f"✅ Configuration loaded from JSON")
# print(f"   • Zones: {[z.name for z in zones]}")

# %% [markdown]
# ## 4️⃣ Create Optimizer and Download Street Network

# %%
# Create optimizer
optimizer = RouteOptimizer(
    bbox=bbox,
    start_point=start_point,
    zones=zones
)

# Download street network from OpenStreetMap
optimizer.download_street_network()

# %% [markdown]
# ## 5️⃣ Label Zones

# %%
# Label nodes according to defined zones
optimizer.label_zones()

# %% [markdown]
# ## 6️⃣ Visualize Zones

# %%
# Create visual map of zones
optimizer.visualize_zones()

# Save image (optional)
# optimizer.visualize_zones(save_path="output/zone_map.png")

# %% [markdown]
# ## 7️⃣ Solve Routes
# 
# We calculate 3 types of routes:
# - **Full**: All zones (Mon-Fri 8am-8pm)
# - **No Courthouse**: For after 2pm
# - **Saturday**: Only downtown + 12th street

# %%
# Dictionary to store results
results = {}

# %% [markdown]
# ### 7.1 Full Route

# %%
print("\n" + "="*60)
print("📍 FULL ROUTE (All zones)")
print("="*60)

route_full, dist_full = optimizer.solve_cpp("full")
results["full"] = (route_full, dist_full)

print(f"\n✅ Total distance: {dist_full/1000:.2f} km")
print(f"✅ Nodes in route: {len(route_full)}")

# %% [markdown]
# ### 7.2 No Courthouse Route

# %%
print("\n" + "="*60)
print("📍 NO COURTHOUSE ROUTE (After 2pm)")
print("="*60)

route_no_court, dist_no_court = optimizer.solve_cpp("no_courthouse")
results["no_courthouse"] = (route_no_court, dist_no_court)

print(f"\n✅ Distance: {dist_no_court/1000:.2f} km")
print(f"✅ Savings vs Full: {(dist_full - dist_no_court)/1000:.2f} km")

# %% [markdown]
# ### 7.3 Saturday Route

# %%
print("\n" + "="*60)
print("📍 SATURDAY ROUTE (Downtown + 12th Street)")
print("="*60)

route_saturday, dist_saturday = optimizer.solve_cpp("saturday")
results["saturday"] = (route_saturday, dist_saturday)

print(f"\n✅ Distance: {dist_saturday/1000:.2f} km")
print(f"✅ Savings vs Full: {(dist_full - dist_saturday)/1000:.2f} km")

# %% [markdown]
# ## 8️⃣ Results Comparison

# %%
import pandas as pd

# Create comparison table
comparison = pd.DataFrame([
    {
        'Route': 'Full',
        'Distance (km)': round(dist_full/1000, 2),
        'Nodes': len(route_full),
        'Savings vs Full (km)': 0
    },
    {
        'Route': 'No Courthouse',
        'Distance (km)': round(dist_no_court/1000, 2),
        'Nodes': len(route_no_court),
        'Savings vs Full (km)': round((dist_full - dist_no_court)/1000, 2)
    },
    {
        'Route': 'Saturday',
        'Distance (km)': round(dist_saturday/1000, 2),
        'Nodes': len(route_saturday),
        'Savings vs Full (km)': round((dist_full - dist_saturday)/1000, 2)
    }
])

print("\n" + "="*60)
print("📊 ROUTE COMPARISON")
print("="*60)
print(comparison.to_string(index=False))

# %% [markdown]
# ## 9️⃣ Export Results to Excel

# %%
# Export all results to Excel file
output_path = "output/enforcement_routes.xlsx"
optimizer.export_results(results, output_path)

print(f"\n✅ Excel file generated:")
print(f"   {output_path}")

# %% [markdown]
# ## 🎯 Final Summary

# %%
print("\n" + "="*70)
print(" 🎉 PROCESS COMPLETED")
print("="*70)
print(f"\n📊 Results:")
print(f"   • Full Route:       {dist_full/1000:.2f} km")
print(f"   • No Courthouse:    {dist_no_court/1000:.2f} km (savings: {(dist_full-dist_no_court)/1000:.2f} km)")
print(f"   • Saturday:         {dist_saturday/1000:.2f} km (savings: {(dist_full-dist_saturday)/1000:.2f} km)")
print(f"\n💾 Files generated:")
print(f"   • {output_path}")
print(f"\n💡 Next steps:")
print(f"   • Review Excel file with detailed routes")
print(f"   • Adjust zone polygons if necessary")
print(f"   • Add new route types in zone_config.json")
print("="*70)

# %% [markdown]
# ## 🛠️ Debugging: Verify Connectivity
# 
# If you want to inspect graph connectivity:

# %%
# Uncomment for debugging:
# test_graph = optimizer.filter_by_route_type("saturday")
# is_connected = optimizer.verify_connectivity(test_graph)
# print(f"Is strongly connected?: {is_connected}")

# %% [markdown]
# ## 📝 Notes
# 
# - To get polygon coordinates: Google Maps → Right click → "What's here?"
# - Format: `(longitude, latitude)` ⚠️ Reversed order!
# - To add zones: Edit `zone_config.json` or create `Zone` objects directly
# - The algorithm automatically extracts the main connected component if the graph is fragmented
