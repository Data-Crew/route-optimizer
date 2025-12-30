# -*- coding: utf-8 -*-
"""
Route Optimizer - Main Module
==============================

A modular route optimization system supporting multiple algorithms.

Supported algorithms:
- CPP (Chinese Postman Problem): Traverse all streets/edges
- TSP (Traveling Salesman Problem): Visit specific points/nodes

See algorithms.md for detailed algorithm documentation.
"""

import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from typing import Dict, List, Tuple, Optional, Literal
from datetime import time
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Import algorithm solvers
from algorithms import CPPSolver, TSPSolver


@dataclass
class Zone:
    """
    Class to define enforcement zones with metadata
    
    Attributes:
        name: Zone identifier
        polygon: Shapely polygon with coordinates
        start_time: Enforcement start time
        end_time: Enforcement end time
        weekdays: List of active days (0=Monday, 6=Sunday)
        prohibited_streets: List of street names where parking is not allowed
        color: Color for visualization
    """
    name: str
    polygon: Polygon
    start_time: time
    end_time: time
    weekdays: List[int]  # 0=Monday, 6=Sunday
    prohibited_streets: List[str] = None
    color: str = "lightblue"
    
    def __post_init__(self):
        if self.prohibited_streets is None:
            self.prohibited_streets = []


class RouteOptimizer:
    """
    Main class for optimizing enforcement routes
    """
    
    def __init__(self, bbox: Tuple[float, float, float, float], 
                 start_point: Tuple[float, float],
                 zones: List[Zone]):
        """
        Initialize the optimizer
        
        Args:
            bbox: Bounding box (west, south, east, north)
            start_point: Coordinates (lat, lon) of start/end point
            zones: List of Zone objects
        """
        self.bbox = bbox
        self.start_point = start_point
        self.zones = zones
        self.G = None
        self.nodes = None
        self.edges = None
        self.start_node = None
        
    def download_street_network(self):
        """Download street network from the specified area"""
        print("📥 Downloading street network...")
        self.G = ox.graph_from_bbox(bbox=self.bbox, network_type="drive")
        print(f"✅ Network downloaded: {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
        
        # Find closest node to start point
        self.start_node = ox.distance.nearest_nodes(
            self.G, 
            X=self.start_point[1], 
            Y=self.start_point[0]
        )
        print(f"📍 Start node: {self.start_node}")
        
    def label_zones(self):
        """Label nodes and edges according to defined zones"""
        print("\n🏷️  Labeling zones...")
        
        # Convert graph to GeoDataFrames
        self.nodes, self.edges = ox.graph_to_gdfs(self.G)
        
        # Initialize zone column
        self.nodes["zone"] = "outside"
        self.nodes["start_time"] = None
        self.nodes["end_time"] = None
        self.nodes["active_days"] = None
        
        # Label each zone
        for zone in self.zones:
            mask = self.nodes.geometry.within(zone.polygon)
            self.nodes.loc[mask, "zone"] = zone.name
            self.nodes.loc[mask, "start_time"] = str(zone.start_time)
            self.nodes.loc[mask, "end_time"] = str(zone.end_time)
            self.nodes.loc[mask, "active_days"] = str(zone.weekdays)
            
            count = mask.sum()
            print(f"   • {zone.name}: {count} nodes")
        
        print(f"\n📊 Zone summary:")
        print(self.nodes["zone"].value_counts())
        
    def visualize_zones(self, save_path: Optional[str] = None):
        """
        Visualize zones on a map
        
        Args:
            save_path: Path to save image (optional)
        """
        print("\n🗺️  Generating visualization...")
        
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Draw streets
        self.edges.plot(ax=ax, linewidth=0.5, edgecolor="gray", alpha=0.5)
        
        # Draw nodes by zone
        for zone in self.zones:
            subset = self.nodes[self.nodes["zone"] == zone.name]
            if not subset.empty:
                subset.plot(ax=ax, color=zone.color, markersize=15, 
                           label=f"{zone.name}", alpha=0.7)
        
        # Draw zone polygons
        for zone in self.zones:
            x, y = zone.polygon.exterior.xy
            ax.plot(x, y, linestyle="--", linewidth=2, alpha=0.8)
        
        # Start/end point
        ax.scatter(self.start_point[1], self.start_point[0], 
                  c='red', s=200, marker='*', 
                  label="Start/End", zorder=5, edgecolors='black', linewidths=2)
        
        plt.title("Parking Enforcement Zones", fontsize=16, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.axis("off")
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Map saved to: {save_path}")
        
        plt.show()
        
    def filter_by_route_type(self, route_type: str) -> nx.MultiDiGraph:
        """
        Filter graph by route type
        
        Args:
            route_type: "full", "no_courthouse", "saturday", etc.
            
        Returns:
            Filtered subgraph
        """
        # Define zones by route type
        zone_config = {
            "full": [z.name for z in self.zones],
            "no_courthouse": [z.name for z in self.zones if z.name != "courthouse"],
            "saturday": ["downtown", "12th_street"],
        }
        
        if route_type not in zone_config:
            raise ValueError(f"Unknown route type: {route_type}")
        
        allowed_zones = zone_config[route_type]
        
        # Filter nodes
        valid_nodes = self.nodes[self.nodes.zone.isin(allowed_zones)].index
        
        if len(valid_nodes) == 0:
            raise ValueError(f"⚠️  No nodes for route type '{route_type}'")
        
        # Create subgraph
        subgraph = self.G.subgraph(valid_nodes).copy()
        
        print(f"\n🔍 Route type '{route_type}':")
        print(f"   • Zones: {', '.join(allowed_zones)}")
        print(f"   • Nodes: {subgraph.number_of_nodes()}")
        print(f"   • Edges: {subgraph.number_of_edges()}")
        
        return subgraph
    
    def solve(self, route_type: str, 
              algorithm: Literal["cpp", "tsp"] = "cpp",
              nodes_to_visit: Optional[List[int]] = None) -> Tuple[List[int], float]:
        """
        Solve route optimization using the specified algorithm.
        
        Args:
            route_type: Route type to optimize ("full", "no_courthouse", etc.)
            algorithm: Algorithm to use:
                - "cpp": Chinese Postman Problem (traverse all streets)
                - "tsp": Traveling Salesman Problem (visit specific points)
            nodes_to_visit: For TSP, specific nodes to visit. 
                          If None, visits all nodes in filtered graph.
            
        Returns:
            Tuple (route, total_distance)
        """
        print(f"\n{'='*60}")
        print(f"🚀 SOLVING ROUTE: {route_type.upper()} ({algorithm.upper()})")
        print(f"{'='*60}")
        
        # Filter graph by route type
        filtered_graph = self.filter_by_route_type(route_type)
        
        # Get start node in filtered graph
        start = self.start_node
        if start not in filtered_graph.nodes:
            start = list(filtered_graph.nodes)[0]
            print(f"   ⚠️  Start node not in filtered graph. Using: {start}")
        
        # Select and run algorithm
        if algorithm.lower() == "cpp":
            solver = CPPSolver(filtered_graph, start)
        elif algorithm.lower() == "tsp":
            solver = TSPSolver(filtered_graph, start, nodes_to_visit)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}. Use 'cpp' or 'tsp'")
        
        route, distance = solver.solve()
        
        print(f"\n✅ Route calculated ({algorithm.upper()}):")
        print(f"   • Nodes visited: {len(route)}")
        print(f"   • Total distance: {distance/1000:.2f} km")
        
        return route, distance
    
    def solve_cpp(self, route_type: str) -> Tuple[List[int], float]:
        """
        Solve Chinese Postman Problem for a route type.
        
        This is a convenience method. Equivalent to:
            solve(route_type, algorithm="cpp")
        
        Use CPP when you need to traverse ALL streets (enforcement, sweeping).
        
        Args:
            route_type: Route type to optimize
            
        Returns:
            Tuple (route, total_distance)
        """
        return self.solve(route_type, algorithm="cpp")
    
    def solve_tsp(self, route_type: str, 
                  nodes_to_visit: Optional[List[int]] = None) -> Tuple[List[int], float]:
        """
        Solve Traveling Salesman Problem for a route type.
        
        This is a convenience method. Equivalent to:
            solve(route_type, algorithm="tsp", nodes_to_visit=nodes)
        
        Use TSP when you need to visit specific points (delivery, inspection points).
        
        Args:
            route_type: Route type to optimize
            nodes_to_visit: Specific nodes to visit. If None, visits all nodes.
            
        Returns:
            Tuple (route, total_distance)
        """
        return self.solve(route_type, algorithm="tsp", nodes_to_visit=nodes_to_visit)
    
    def visualize_route(self, route: List[int], graph: nx.MultiDiGraph, 
                       title: str, save_path: Optional[str] = None):
        """
        Visualize a route on the map with street basemap and direction indicators
        
        Args:
            route: List of nodes in the route
            graph: Graph used (for context, but uses self.G for plotting)
            title: Map title
            save_path: Path to save image (optional)
        """
        print(f"\n🗺️  Visualizing route: {title}")
        
        # Filter route to only include nodes that exist in the main graph
        valid_route = [n for n in route if n in self.G.nodes]
        
        if len(valid_route) < 2:
            print("   ⚠️  Not enough valid nodes to visualize")
            return
        
        # Build complete route with all intermediate nodes
        G_undirected = self.G.to_undirected()
        
        full_route_coords = []
        skipped_segments = 0
        
        for i in range(len(valid_route) - 1):
            node_from = valid_route[i]
            node_to = valid_route[i + 1]
            
            path = None
            
            if self.G.has_edge(node_from, node_to):
                path = [node_from, node_to]
            
            if path is None:
                try:
                    path = nx.shortest_path(self.G, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
            
            if path is None:
                try:
                    path = nx.shortest_path(G_undirected, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
            
            if path:
                for j, node in enumerate(path):
                    node_data = self.G.nodes[node]
                    if j == 0 and full_route_coords:
                        continue
                    full_route_coords.append((node_data['x'], node_data['y']))
            else:
                skipped_segments += 1
                from_data = self.G.nodes[node_from]
                to_data = self.G.nodes[node_to]
                if not full_route_coords:
                    full_route_coords.append((from_data['x'], from_data['y']))
                full_route_coords.append((to_data['x'], to_data['y']))
        
        if skipped_segments > 0:
            print(f"   ⚠️  {skipped_segments} segments without street path")
        
        # Create GeoDataFrame for the route (for proper projection)
        from shapely.geometry import LineString, Point
        
        route_line = LineString(full_route_coords)
        route_gdf = gpd.GeoDataFrame(geometry=[route_line], crs="EPSG:4326")
        
        # Reproject to Web Mercator for basemap
        route_gdf_wm = route_gdf.to_crs(epsg=3857)
        edges_wm = self.edges.to_crs(epsg=3857)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 14))
        
        # Plot street network first (subtle)
        edges_wm.plot(ax=ax, linewidth=0.8, edgecolor="#666666", alpha=0.3, zorder=1)
        
        # Add basemap (street tiles)
        try:
            import contextily as ctx
            ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=17)
        except ImportError:
            print("   ⚠️  contextily not installed - no basemap")
        except Exception as e:
            print(f"   ⚠️  Could not load basemap: {e}")
        
        # Convert route coords to Web Mercator for plotting
        from pyproj import Transformer
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        
        route_coords_wm = []
        for lon, lat in full_route_coords:
            x, y = transformer.transform(lon, lat)
            route_coords_wm.append((x, y))
        
        # Draw route with color gradient (green to red)
        n_points = len(route_coords_wm)
        if n_points >= 2:
            colors = plt.cm.RdYlGn_r(np.linspace(0, 1, n_points - 1))
            
            for i in range(n_points - 1):
                x1, y1 = route_coords_wm[i]
                x2, y2 = route_coords_wm[i + 1]
                ax.plot([x1, x2], [y1, y2], color=colors[i], linewidth=4, 
                       solid_capstyle='round', zorder=10)
                
                # Add arrows every ~10% of the route
                if i % max(1, n_points // 10) == 0 and i > 0:
                    dx = x2 - x1
                    dy = y2 - y1
                    if dx != 0 or dy != 0:
                        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                                   arrowprops=dict(arrowstyle='->', color=colors[i], 
                                                  lw=2.5, mutation_scale=20),
                                   zorder=11)
        
        # Mark key waypoints with numbers
        n_labels = min(10, len(valid_route))
        label_indices = [int(i * (len(valid_route) - 1) / (n_labels - 1)) for i in range(n_labels)]
        
        for idx, route_idx in enumerate(label_indices):
            node = valid_route[route_idx]
            node_data = self.G.nodes[node]
            x, y = transformer.transform(node_data['x'], node_data['y'])
            
            progress = route_idx / (len(valid_route) - 1)
            color = plt.cm.RdYlGn_r(progress)
            
            ax.scatter(x, y, c=[color], s=250, zorder=15, edgecolors='white', linewidths=2)
            ax.annotate(str(idx + 1), (x, y), fontsize=10, fontweight='bold', 
                       ha='center', va='center', color='white', zorder=16)
        
        # Start marker (green star)
        start_data = self.G.nodes[valid_route[0]]
        sx, sy = transformer.transform(start_data['x'], start_data['y'])
        ax.scatter(sx, sy, c='#22C55E', s=500, marker='*', zorder=20, 
                  edgecolors='white', linewidths=2, label='START')
        
        # End marker (if different from start)
        end_data = self.G.nodes[valid_route[-1]]
        if valid_route[-1] != valid_route[0]:
            ex, ey = transformer.transform(end_data['x'], end_data['y'])
            ax.scatter(ex, ey, c='#EF4444', s=400, marker='s', zorder=20,
                      edgecolors='white', linewidths=2, label='END')
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#22C55E', edgecolor='white', label='Start'),
            Patch(facecolor='#FBBF24', edgecolor='white', label='Middle'),
            Patch(facecolor='#EF4444', edgecolor='white', label='End'),
        ]
        
        ax.set_title(f"{title}\n({len(valid_route)} stops, follow numbers 1→{n_labels})", 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(handles=legend_elements, loc='upper right', fontsize=11,
                 facecolor='white', edgecolor='gray')
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"💾 Route saved to: {save_path}")
        
        plt.close(fig)
    
    def visualize_route_interactive(self, route: List[int], 
                                    title: str, save_path: str):
        """
        Generate an interactive HTML map of the route using Folium.
        
        Features:
        - Real street map background (OpenStreetMap)
        - Click on nodes to see sequence number
        - Color gradient showing progress (green→yellow→red)
        - Zoom and pan
        
        Args:
            route: List of nodes in the route
            title: Map title
            save_path: Path to save HTML file
        """
        try:
            import folium
            from folium.plugins import AntPath
        except ImportError:
            print("   ⚠️  Folium not installed. Run: pip install folium")
            return
        
        print(f"\n🗺️  Generating interactive map: {title}")
        
        # Filter valid nodes
        valid_route = [n for n in route if n in self.G.nodes]
        
        if len(valid_route) < 2:
            print("   ⚠️  Not enough valid nodes")
            return
        
        # Build complete route following actual streets
        # Create undirected version for path finding (streets are traversable both ways for visualization)
        G_undirected = self.G.to_undirected()
        
        route_coords = []
        skipped_segments = 0
        
        for i in range(len(valid_route) - 1):
            node_from = valid_route[i]
            node_to = valid_route[i + 1]
            
            path = None
            
            # Strategy 1: Direct edge in directed graph
            if self.G.has_edge(node_from, node_to):
                path = [node_from, node_to]
            
            # Strategy 2: Try shortest path in directed graph
            if path is None:
                try:
                    path = nx.shortest_path(self.G, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
            
            # Strategy 3: Try shortest path in undirected graph (for visualization purposes)
            if path is None:
                try:
                    path = nx.shortest_path(G_undirected, node_from, node_to, weight='length')
                except nx.NetworkXNoPath:
                    pass
            
            # Apply path or fallback to direct line
            if path:
                for j, node in enumerate(path):
                    node_data = self.G.nodes[node]
                    if j == 0 and route_coords:
                        continue  # Skip first to avoid duplicate
                    route_coords.append([node_data['y'], node_data['x']])
            else:
                # Last resort: direct line (should rarely happen)
                skipped_segments += 1
                from_data = self.G.nodes[node_from]
                to_data = self.G.nodes[node_to]
                if not route_coords:
                    route_coords.append([from_data['y'], from_data['x']])
                route_coords.append([to_data['y'], to_data['x']])
        
        if skipped_segments > 0:
            print(f"   ⚠️  {skipped_segments} segments without street path (shown as direct lines)")
        
        # Center map on route
        center_lat = sum(c[0] for c in route_coords) / len(route_coords)
        center_lon = sum(c[1] for c in route_coords) / len(route_coords)
        
        # Create map with clean tile layer
        m = folium.Map(location=[center_lat, center_lon], zoom_start=16, 
                      tiles='CartoDB positron')  # Cleaner, lighter background
        
        # Add title with clear instructions
        title_html = f'''
        <div style="position: fixed; top: 10px; left: 50px; z-index: 1000; 
                    background: white; padding: 15px; border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2); max-width: 300px;">
            <h3 style="margin: 0; color: #333;">{title}</h3>
            <p style="margin: 8px 0 0 0; font-size: 13px; color: #666;">
                📍 <b>{len(valid_route)} stops</b> | Click markers for details
            </p>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #888;">
                ➡️ Follow the animated purple line
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add animated route line (purple with white pulse - distinct from markers)
        AntPath(
            locations=route_coords,
            color='#6B46C1',  # Purple
            weight=5,
            opacity=0.9,
            delay=800,
            dash_array=[10, 15],
            pulse_color='white'
        ).add_to(m)
        
        # Get start and end coordinates
        start_node = valid_route[0]
        end_node = valid_route[-1]
        start_data = self.G.nodes[start_node]
        end_data = self.G.nodes[end_node]
        
        # BIG START MARKER - Very visible
        start_html = '''
        <div style="
            background: #22C55E;
            color: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            border: 4px solid white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.4);
        ">▶</div>
        '''
        folium.Marker(
            location=[start_data['y'], start_data['x']],
            popup=folium.Popup(
                f"<div style='text-align:center;'>"
                f"<h3 style='color:#22C55E; margin:0;'>🚀 START</h3>"
                f"<p>Begin route here</p>"
                f"<p><b>Node 1</b> of {len(valid_route)}</p>"
                f"</div>", 
                max_width=200
            ),
            tooltip="🚀 START HERE",
            icon=folium.DivIcon(html=start_html, icon_size=(50, 50), icon_anchor=(25, 25))
        ).add_to(m)
        
        # BIG END MARKER - Very visible (only if different from start)
        if end_node != start_node:
            end_html = '''
            <div style="
                background: #EF4444;
                color: white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: bold;
                border: 4px solid white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.4);
            ">⬛</div>
            '''
            folium.Marker(
                location=[end_data['y'], end_data['x']],
                popup=folium.Popup(
                    f"<div style='text-align:center;'>"
                    f"<h3 style='color:#EF4444; margin:0;'>🏁 FINISH</h3>"
                    f"<p>Route ends here</p>"
                    f"<p><b>Node {len(valid_route)}</b> of {len(valid_route)}</p>"
                    f"</div>", 
                    max_width=200
                ),
                tooltip="🏁 FINISH HERE",
                icon=folium.DivIcon(html=end_html, icon_size=(50, 50), icon_anchor=(25, 25))
            ).add_to(m)
        else:
            # Circular route - same start/end
            circular_html = '''
            <div style="
                background: linear-gradient(135deg, #22C55E, #EF4444);
                color: white;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                font-weight: bold;
                border: 4px solid white;
                box-shadow: 0 3px 10px rgba(0,0,0,0.4);
            ">🔄</div>
            '''
            # Remove the simple start marker and add circular one
            folium.Marker(
                location=[start_data['y'], start_data['x']],
                popup=folium.Popup(
                    f"<div style='text-align:center;'>"
                    f"<h3 style='margin:0;'>🔄 START & FINISH</h3>"
                    f"<p style='color:#22C55E;'><b>Route starts here</b></p>"
                    f"<p style='color:#EF4444;'><b>Route ends here</b></p>"
                    f"<p>Circular route with {len(valid_route)} stops</p>"
                    f"</div>", 
                    max_width=220
                ),
                tooltip="🔄 START & FINISH (circular route)",
                icon=folium.DivIcon(html=circular_html, icon_size=(60, 60), icon_anchor=(30, 30))
            ).add_to(m)
        
        # Add numbered waypoint markers (every ~10% of route)
        n_markers = min(10, len(valid_route))
        marker_indices = [int(i * (len(valid_route) - 1) / (n_markers - 1)) 
                         for i in range(1, n_markers - 1)]  # Skip first and last
        
        for idx, route_idx in enumerate(marker_indices, start=2):
            node = valid_route[route_idx]
            node_data = self.G.nodes[node]
            lat, lon = node_data['y'], node_data['x']
            
            # Skip if too close to start or end
            if route_idx <= 1 or route_idx >= len(valid_route) - 2:
                continue
            
            # Numbered marker
            number_html = f'''
            <div style="
                background: #3B82F6;
                color: white;
                border-radius: 50%;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            ">{idx}</div>
            '''
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(
                    f"<b>Waypoint {idx}</b><br>"
                    f"Stop {route_idx + 1} of {len(valid_route)}<br>"
                    f"<small>({int((route_idx / len(valid_route)) * 100)}% complete)</small>",
                    max_width=200
                ),
                tooltip=f"Waypoint {idx}",
                icon=folium.DivIcon(html=number_html, icon_size=(28, 28), icon_anchor=(14, 14))
            ).add_to(m)
        
        # Add subtle path dots (visible when zoomed)
        for i, node in enumerate(valid_route):
            if i == 0 or i == len(valid_route) - 1:
                continue  # Skip start/end (already have big markers)
            
            node_data = self.G.nodes[node]
            lat, lon = node_data['y'], node_data['x']
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color='#6B46C1',
                fill=True,
                fillColor='#6B46C1',
                fillOpacity=0.5,
                weight=1,
                tooltip=f"Stop {i + 1} of {len(valid_route)}"
            ).add_to(m)
        
        # Improved legend
        legend_html = f'''
        <div style="position: fixed; bottom: 30px; right: 30px; z-index: 1000;
                    background: white; padding: 15px; border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2); min-width: 180px;">
            <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 14px;">Route Guide:</p>
            
            <div style="display: flex; align-items: center; margin: 8px 0;">
                <div style="background: #22C55E; width: 24px; height: 24px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; color: white; margin-right: 10px;">▶</div>
                <span>Start</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 8px 0;">
                <div style="background: #3B82F6; width: 24px; height: 24px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; color: white; 
                            font-size: 11px; margin-right: 10px;">2</div>
                <span>Waypoints</span>
            </div>
            
            <div style="display: flex; align-items: center; margin: 8px 0;">
                <div style="background: #EF4444; width: 24px; height: 24px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; color: white; margin-right: 10px;">⬛</div>
                <span>Finish</span>
            </div>
            
            <hr style="margin: 10px 0; border: none; border-top: 1px solid #eee;">
            
            <div style="display: flex; align-items: center; margin: 8px 0;">
                <div style="background: #6B46C1; width: 30px; height: 4px; margin-right: 10px; border-radius: 2px;"></div>
                <span style="font-size: 12px;">Animated route</span>
            </div>
            
            <p style="margin: 10px 0 0 0; font-size: 11px; color: #888;">
                Total: <b>{len(valid_route)} stops</b>
            </p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add playback controls with JavaScript
        # Store route coordinates as JavaScript variable
        coords_js = str([[c[0], c[1]] for c in route_coords])
        waypoint_coords = []
        for node in valid_route:
            nd = self.G.nodes[node]
            waypoint_coords.append([nd['y'], nd['x']])
        waypoints_js = str(waypoint_coords)
        
        playback_html = f'''
        <div id="playback-panel" style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                    background: white; padding: 15px; border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2); min-width: 280px;">
            <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 14px;">🎬 Route Playback:</p>
            
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <button id="prev-btn" onclick="prevStep()" style="padding: 8px 12px; font-size: 16px; cursor: pointer; border: 1px solid #ddd; border-radius: 4px; background: #f5f5f5;">⏮️</button>
                <button id="play-btn" onclick="togglePlay()" style="padding: 8px 16px; font-size: 16px; cursor: pointer; border: none; border-radius: 4px; background: #22C55E; color: white;">▶️ Play</button>
                <button id="next-btn" onclick="nextStep()" style="padding: 8px 12px; font-size: 16px; cursor: pointer; border: 1px solid #ddd; border-radius: 4px; background: #f5f5f5;">⏭️</button>
            </div>
            
            <div style="margin-bottom: 10px;">
                <input type="range" id="progress-slider" min="0" max="{len(valid_route) - 1}" value="0" 
                       style="width: 100%;" oninput="goToStep(this.value)">
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666;">
                <span>Step: <b id="current-step">1</b> / {len(valid_route)}</span>
                <span id="progress-pct">0%</span>
            </div>
            
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee;">
                <label style="font-size: 12px; display: flex; align-items: center; gap: 5px;">
                    <input type="checkbox" id="auto-center"> Auto-center on current node
                </label>
            </div>
        </div>
        
        <style>
            #progress-slider {{
                -webkit-appearance: none;
                height: 8px;
                border-radius: 4px;
                background: linear-gradient(to right, #22C55E, #EAB308, #EF4444);
            }}
            #progress-slider::-webkit-slider-thumb {{
                -webkit-appearance: none;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: #6B46C1;
                cursor: pointer;
                border: 3px solid white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            }}
        </style>
        
        <script>
            var waypoints = {waypoints_js};
            var currentStep = 0;
            var isPlaying = false;
            var playInterval = null;
            var currentMarker = null;
            var pathLine = null;
            var visitedPath = [];
            var map = null;
            
            // Find the Leaflet map object - Folium stores it with a generated name
            function findLeafletMap() {{
                for (var key in window) {{
                    try {{
                        if (window[key] && window[key] instanceof L.Map) {{
                            return window[key];
                        }}
                    }} catch(e) {{}}
                }}
                return null;
            }}
            
            function updateDisplay() {{
                if (!map) {{
                    map = findLeafletMap();
                    if (!map) {{
                        console.error('Could not find Leaflet map');
                        return;
                    }}
                }}
                document.getElementById('current-step').textContent = currentStep + 1;
                document.getElementById('progress-slider').value = currentStep;
                var pct = Math.round((currentStep / (waypoints.length - 1)) * 100);
                document.getElementById('progress-pct').textContent = pct + '%';
                
                // Remove old current marker
                if (currentMarker) {{
                    map.removeLayer(currentMarker);
                }}
                
                // Remove old path
                if (pathLine) {{
                    map.removeLayer(pathLine);
                }}
                
                // Draw path up to current point
                visitedPath = waypoints.slice(0, currentStep + 1);
                if (visitedPath.length > 1) {{
                    pathLine = L.polyline(visitedPath, {{
                        color: '#22C55E',
                        weight: 6,
                        opacity: 0.8
                    }}).addTo(map);
                }}
                
                // Add current position marker (simple, no animation)
                var pos = waypoints[currentStep];
                var markerColor = currentStep === 0 ? '#22C55E' : 
                                  currentStep === waypoints.length - 1 ? '#EF4444' : '#FF6B00';
                
                currentMarker = L.circleMarker(pos, {{
                    radius: 10,
                    color: 'white',
                    fillColor: markerColor,
                    fillOpacity: 1,
                    weight: 3
                }}).addTo(map);
                
                currentMarker.bindTooltip('Step ' + (currentStep + 1) + ' of ' + waypoints.length, {{
                    direction: 'top',
                    offset: [0, -8]
                }});
                
                // Auto-center if enabled
                if (document.getElementById('auto-center').checked) {{
                    map.setView(pos, map.getZoom());
                }}
            }}
            
            function nextStep() {{
                if (currentStep < waypoints.length - 1) {{
                    currentStep++;
                    updateDisplay();
                }} else {{
                    stopPlay();
                }}
            }}
            
            function prevStep() {{
                if (currentStep > 0) {{
                    currentStep--;
                    updateDisplay();
                }}
            }}
            
            function goToStep(step) {{
                currentStep = parseInt(step);
                updateDisplay();
            }}
            
            function togglePlay() {{
                if (isPlaying) {{
                    stopPlay();
                }} else {{
                    startPlay();
                }}
            }}
            
            function startPlay() {{
                isPlaying = true;
                document.getElementById('play-btn').textContent = '⏸️ Pause';
                document.getElementById('play-btn').style.background = '#EAB308';
                playInterval = setInterval(function() {{
                    if (currentStep < waypoints.length - 1) {{
                        nextStep();
                    }} else {{
                        stopPlay();
                    }}
                }}, 500);  // 500ms between steps
            }}
            
            function stopPlay() {{
                isPlaying = false;
                document.getElementById('play-btn').textContent = '▶️ Play';
                document.getElementById('play-btn').style.background = '#22C55E';
                if (playInterval) {{
                    clearInterval(playInterval);
                    playInterval = null;
                }}
            }}
            
            // Initialize - wait for map to be fully loaded
            function initPlayback() {{
                map = findLeafletMap();
                if (map) {{
                    console.log('Leaflet map found, initializing playback controls');
                    updateDisplay();
                }} else {{
                    console.log('Waiting for Leaflet map...');
                    setTimeout(initPlayback, 500);
                }}
            }}
            
            // Start initialization after DOM is ready
            if (document.readyState === 'complete') {{
                setTimeout(initPlayback, 500);
            }} else {{
                window.addEventListener('load', function() {{
                    setTimeout(initPlayback, 500);
                }});
            }}
        </script>
        '''
        m.get_root().html.add_child(folium.Element(playback_html))
        
        # Save
        m.save(save_path)
        print(f"💾 Interactive map saved to: {save_path}")
        print(f"   Open in browser and use the playback controls!")
    
    def export_results(self, results: Dict[str, Tuple[List[int], float]], 
                      output_path: str):
        """
        Export results to Excel file
        
        Args:
            results: Dictionary {route_type: (route, distance)}
            output_path: Output file path
        """
        print(f"\n📊 Exporting results...")
        
        # Create DataFrame with summary
        summary_data = []
        for route_type, (route, distance) in results.items():
            summary_data.append({
                'Route_Type': route_type,
                'Node_Count': len(route),
                'Distance_KM': round(distance / 1000, 2),
                'Distance_Meters': int(distance)
            })
        
        df_summary = pd.DataFrame(summary_data)
        
        # Create DataFrames with detailed routes
        dfs_routes = {}
        for route_type, (route, distance) in results.items():
            # Get coordinates for each node
            coords_data = []
            for i, node in enumerate(route):
                node_data = self.G.nodes[node]
                coords_data.append({
                    'Sequence': i + 1,
                    'Node_ID': node,
                    'Latitude': node_data['y'],
                    'Longitude': node_data['x'],
                    'Zone': self.nodes.loc[node, 'zone'] if node in self.nodes.index else 'N/A'
                })
            
            dfs_routes[route_type] = pd.DataFrame(coords_data)
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            for route_type, df in dfs_routes.items():
                sheet_name = route_type[:31]  # Excel limits to 31 characters
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✅ Results exported to: {output_path}")
        print(f"\n📋 Summary:")
        print(df_summary.to_string(index=False))


def example_usage():
    """Example usage of the module"""
    
    # Define enforcement zones
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
    
    # Create optimizer
    optimizer = RouteOptimizer(
        bbox=(-57.9605, -34.9210, -57.9455, -34.9095),
        start_point=(-34.91719, -57.95067),
        zones=zones
    )
    
    # Download street network
    optimizer.download_street_network()
    
    # Label zones
    optimizer.label_zones()
    
    # Visualize zones
    optimizer.visualize_zones(save_path="output/zone_map.png")
    
    # Solve different route types
    route_types = ["full", "no_courthouse", "saturday"]
    results = {}
    
    for route_type in route_types:
        try:
            route, distance = optimizer.solve_cpp(route_type)
            results[route_type] = (route, distance)
            
            # Visualize route
            graph = optimizer.filter_by_route_type(route_type)
            if not nx.is_strongly_connected(graph):
                graph = optimizer.get_main_component(graph)
            
            optimizer.visualize_route(
                route, 
                graph,
                title=f"Optimal Route: {route_type.upper()}",
                save_path=f"output/route_{route_type}.png"
            )
        except Exception as e:
            print(f"❌ Error in route '{route_type}': {e}")
    
    # Export results
    if results:
        optimizer.export_results(
            results,
            "output/enforcement_routes.xlsx"
        )
    
    return optimizer, results


if __name__ == "__main__":
    optimizer, results = example_usage()
