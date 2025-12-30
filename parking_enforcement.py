#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example: Parking Enforcement Route Optimization using CPP
==========================================================

This example demonstrates using the Chinese Postman Problem (CPP)
algorithm for optimizing parking enforcement patrol routes.

Use Case: Traverse ALL streets in a zone to ensure complete coverage.

Usage: python parking_enforcement.py
"""

from route_optimizer import RouteOptimizer, Zone
from shapely.geometry import Polygon
from datetime import time


def main():
    """Simple usage example"""
    
    print("="*70)
    print(" ROUTE OPTIMIZER - PARKING ENFORCEMENT (CPP)")
    print("="*70)
    
    # 1. DEFINE ZONES
    # Adjust these coordinates according to your city
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
            weekdays=[0, 1, 2, 3, 4],  # Mon-Fri
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
            weekdays=[0, 1, 2, 3, 4, 5],  # Mon-Sat
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
            weekdays=[0, 1, 2, 3, 4, 5],  # Mon-Sat
            color="violet"
        ),
    ]
    
    # 2. CONFIGURE AREA AND START POINT
    bbox = (-57.9605, -34.9210, -57.9455, -34.9095)  # La Plata, Argentina
    start_point = (-34.91719, -57.95067)  # Corner of 12th and 50th
    
    # 3. CREATE OPTIMIZER
    optimizer = RouteOptimizer(
        bbox=bbox,
        start_point=start_point,
        zones=zones
    )
    
    # 4. DOWNLOAD NETWORK AND LABEL
    optimizer.download_street_network()
    optimizer.label_zones()
    
    # 5. VISUALIZE ZONES
    optimizer.visualize_zones(
        save_path="output/cpp_zones.png"
    )
    
    # 6. CALCULATE ROUTES
    print("\n" + "="*70)
    print(" CALCULATING OPTIMAL ROUTES")
    print("="*70)
    
    results = {}
    
    # Full route (all zones)
    print("\n📍 CASE 1: Full Route")
    route_full, dist_full = optimizer.solve_cpp("full")
    results["full"] = (route_full, dist_full)
    
    # Route without courthouse zone (after 2pm)
    print("\n📍 CASE 2: No Courthouse (after 2pm)")
    route_no_court, dist_no_court = optimizer.solve_cpp("no_courthouse")
    results["no_courthouse"] = (route_no_court, dist_no_court)
    
    # Saturday route (only downtown and 12th street)
    print("\n📍 CASE 3: Saturday Route")
    route_saturday, dist_saturday = optimizer.solve_cpp("saturday")
    results["saturday"] = (route_saturday, dist_saturday)
    
    # 7. EXPORT RESULTS
    optimizer.export_results(
        results,
        "output/cpp_routes.xlsx"
    )
    
    # 8. VISUALIZE ROUTES
    print("\n" + "="*70)
    print(" GENERATING ROUTE VISUALIZATIONS")
    print("="*70)
    
    # Get filtered graphs for visualization
    graph_full = optimizer.filter_by_route_type("full")
    graph_no_court = optimizer.filter_by_route_type("no_courthouse")
    graph_saturday = optimizer.filter_by_route_type("saturday")
    
    # Generate static PNG images
    print("\n📸 Generating static images...")
    
    optimizer.visualize_route(
        route_full, graph_full,
        title="CPP: Full Route (All Zones)",
        save_path="output/cpp_route_full.png"
    )
    
    optimizer.visualize_route(
        route_no_court, graph_no_court,
        title="CPP: No Courthouse Route (After 2pm)",
        save_path="output/cpp_route_no_courthouse.png"
    )
    
    optimizer.visualize_route(
        route_saturday, graph_saturday,
        title="CPP: Saturday Route",
        save_path="output/cpp_route_saturday.png"
    )
    
    # Generate interactive HTML maps (much clearer!)
    print("\n🌐 Generating interactive maps (open in browser)...")
    
    optimizer.visualize_route_interactive(
        route_full,
        title="CPP: Full Route (All Zones)",
        save_path="output/cpp_route_full.html"
    )
    
    optimizer.visualize_route_interactive(
        route_no_court,
        title="CPP: No Courthouse Route (After 2pm)",
        save_path="output/cpp_route_no_courthouse.html"
    )
    
    optimizer.visualize_route_interactive(
        route_saturday,
        title="CPP: Saturday Route",
        save_path="output/cpp_route_saturday.html"
    )
    
    # 9. FINAL SUMMARY
    print("\n" + "="*70)
    print(" FINAL SUMMARY - CPP (Chinese Postman Problem)")
    print("="*70)
    print(f"\n✅ Full Route:      {dist_full/1000:.2f} km ({len(route_full)} nodes)")
    print(f"✅ No Courthouse:   {dist_no_court/1000:.2f} km ({len(route_no_court)} nodes)")
    print(f"✅ Saturday:        {dist_saturday/1000:.2f} km ({len(route_saturday)} nodes)")
    print(f"\n📁 Output files (all prefixed with 'cpp_'):")
    print("\n   📸 Static images (with street basemap):")
    print("   • cpp_zones.png              - Map of enforcement zones")
    print("   • cpp_route_full.png         - Full route")
    print("   • cpp_route_no_courthouse.png - Afternoon route")
    print("   • cpp_route_saturday.png     - Weekend route")
    print("\n   🌐 Interactive maps (RECOMMENDED - open in browser):")
    print("   • cpp_route_full.html        - Full route with playback")
    print("   • cpp_route_no_courthouse.html - Afternoon route")
    print("   • cpp_route_saturday.html    - Weekend route")
    print("\n   📊 Data:")
    print("   • cpp_routes.xlsx            - Route coordinates")
    print("\n💡 TIP: Open the .html files for interactive step-by-step playback!")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
