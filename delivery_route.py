#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example: Delivery Route Optimization using TSP
===============================================

This example demonstrates using the Traveling Salesman Problem (TSP)
algorithm for optimizing delivery routes.

TSP vs CPP:
- TSP: Visit specific POINTS (addresses) - used here
- CPP: Traverse all STREETS - see parking_enforcement.py

Use Case: A delivery driver with 10 packages to deliver.
Goal: Find the shortest route that visits all delivery addresses.

Usage: python delivery_route.py
"""

from route_optimizer import RouteOptimizer, Zone
from shapely.geometry import Polygon
from datetime import time


def main():
    """TSP example: Optimize a delivery route for 10 packages"""
    
    print("="*70)
    print(" ROUTE OPTIMIZER - DELIVERY ROUTE (TSP)")
    print("="*70)
    print("\n📦 Scenario: A delivery driver has 10 packages to deliver.")
    print("   Goal: Find the shortest route visiting all addresses.\n")
    
    # =========================================================================
    # 1. DEFINE DELIVERY AREA
    # =========================================================================
    # The zone defines the geographic area where deliveries will be made
    delivery_zone = Zone(
        name="delivery_area",
        polygon=Polygon([
            (-57.956, -34.912),
            (-57.948, -34.912),
            (-57.948, -34.920),
            (-57.956, -34.920),
        ]),
        start_time=time(8, 0),
        end_time=time(18, 0),
        weekdays=[0, 1, 2, 3, 4, 5],  # Mon-Sat
        color="lightblue"
    )
    
    # =========================================================================
    # 2. CONFIGURE AREA AND DEPOT
    # =========================================================================
    bbox = (-57.9605, -34.9210, -57.9455, -34.9095)  # La Plata, Argentina
    depot = (-34.91719, -57.95067)  # Warehouse/starting location
    
    # =========================================================================
    # 3. CREATE OPTIMIZER AND DOWNLOAD NETWORK
    # =========================================================================
    optimizer = RouteOptimizer(
        bbox=bbox,
        start_point=depot,
        zones=[delivery_zone]
    )
    
    optimizer.download_street_network()
    optimizer.label_zones()
    
    # =========================================================================
    # 4. DEFINE DELIVERY ADDRESSES
    # =========================================================================
    # In a real scenario, you would geocode actual addresses.
    # Here we simulate 10 delivery points as coordinates.
    
    print("\n📍 Delivery addresses (10 packages):")
    
    # Simulated delivery addresses (lat, lon) - these would come from your orders
    delivery_addresses = [
        (-34.9135, -57.9530),  # Package 1: Calle 50 y 12
        (-34.9150, -57.9510),  # Package 2: Calle 51 y 11
        (-34.9165, -57.9495),  # Package 3: Calle 52 y 10
        (-34.9180, -57.9520),  # Package 4: Calle 50 y 13
        (-34.9145, -57.9545),  # Package 5: Calle 49 y 12
        (-34.9160, -57.9555),  # Package 6: Calle 48 y 13
        (-34.9175, -57.9540),  # Package 7: Calle 49 y 14
        (-34.9140, -57.9505),  # Package 8: Calle 51 y 11
        (-34.9155, -57.9525),  # Package 9: Calle 50 y 12
        (-34.9170, -57.9510),  # Package 10: Calle 51 y 13
    ]
    
    # Convert addresses to network nodes (find nearest intersection)
    import osmnx as ox
    
    delivery_nodes = []
    for i, (lat, lon) in enumerate(delivery_addresses, 1):
        node = ox.distance.nearest_nodes(optimizer.G, X=lon, Y=lat)
        delivery_nodes.append(node)
        node_data = optimizer.G.nodes[node]
        print(f"   📦 Package {i}: Node {node} ({node_data['y']:.5f}, {node_data['x']:.5f})")
    
    # Remove duplicates (some addresses may map to the same intersection)
    unique_nodes = list(dict.fromkeys(delivery_nodes))
    print(f"\n   ℹ️  {len(delivery_addresses)} addresses → {len(unique_nodes)} unique stops")
    
    # =========================================================================
    # 5. CALCULATE OPTIMAL DELIVERY ROUTE (TSP)
    # =========================================================================
    print("\n" + "="*70)
    print(" CALCULATING OPTIMAL ROUTE (TSP)")
    print("="*70)
    
    route, distance = optimizer.solve_tsp("full", nodes_to_visit=unique_nodes)
    
    print(f"\n📊 Route summary:")
    print(f"   • Packages: {len(delivery_addresses)}")
    print(f"   • Unique stops: {len(unique_nodes)}")
    print(f"   • Route nodes: {len(route)} (including path between stops)")
    print(f"   • Total distance: {distance/1000:.2f} km")
    
    # =========================================================================
    # 6. VISUALIZATIONS
    # =========================================================================
    print("\n" + "="*70)
    print(" GENERATING VISUALIZATIONS")
    print("="*70)
    
    # Visualize delivery zone
    optimizer.visualize_zones(save_path="output/tsp_zone.png")
    
    # Get filtered graph for visualization
    filtered_graph = optimizer.filter_by_route_type("full")
    
    # Static PNG with basemap
    optimizer.visualize_route(
        route, 
        filtered_graph,
        title="TSP: Delivery Route (10 packages)",
        save_path="output/tsp_route.png"
    )
    
    # Interactive HTML with playback
    optimizer.visualize_route_interactive(
        route,
        title="TSP: Delivery Route",
        save_path="output/tsp_route.html"
    )
    
    # =========================================================================
    # 7. EXPORT RESULTS
    # =========================================================================
    results = {"delivery_route": (route, distance)}
    
    optimizer.export_results(results, "output/tsp_routes.xlsx")
    
    # =========================================================================
    # 8. FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print(" FINAL SUMMARY - TSP (Traveling Salesman Problem)")
    print("="*70)
    print(f"\n✅ Delivery route optimized!")
    print(f"   • Packages: {len(delivery_addresses)}")
    print(f"   • Distance: {distance/1000:.2f} km")
    print(f"   • Estimated time: ~{distance/1000/30*60:.0f} min (at 30 km/h avg)")
    
    print(f"\n📁 Output files (all prefixed with 'tsp_'):")
    print("\n   📸 Static images:")
    print("   • tsp_zone.png   - Delivery area map")
    print("   • tsp_route.png  - Optimized route with basemap")
    print("\n   🌐 Interactive map:")
    print("   • tsp_route.html - Route with step-by-step playback")
    print("\n   📊 Data:")
    print("   • tsp_routes.xlsx - Route coordinates")
    
    print("="*70)


if __name__ == "__main__":
    main()
