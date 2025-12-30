# -*- coding: utf-8 -*-
"""
Module for loading zone configuration from JSON file
"""

import json
from typing import List, Dict, Tuple
from datetime import time
from shapely.geometry import Polygon
from route_optimizer import Zone


def load_configuration(json_path: str) -> Tuple[tuple, tuple, List[Zone], Dict]:
    """
    Load configuration from JSON file
    
    Args:
        json_path: Path to JSON configuration file
        
    Returns:
        Tuple (bbox, start_point, zones, route_types)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Extract bbox
    bbox_cfg = config['configuration']['bbox']
    bbox = (
        bbox_cfg['west'],
        bbox_cfg['south'],
        bbox_cfg['east'],
        bbox_cfg['north']
    )
    
    # Extract start point
    point_cfg = config['configuration']['start_point']
    start_point = (
        point_cfg['latitude'],
        point_cfg['longitude']
    )
    
    # Load zones
    zones = []
    for zone_cfg in config['zones']:
        # Parse times
        start_time = time(*map(int, zone_cfg['schedule']['start'].split(':')))
        end_time = time(*map(int, zone_cfg['schedule']['end'].split(':')))
        
        # Create polygon
        polygon = Polygon(zone_cfg['polygon'])
        
        # Create Zone object
        zone = Zone(
            name=zone_cfg['name'],
            polygon=polygon,
            start_time=start_time,
            end_time=end_time,
            weekdays=zone_cfg['weekdays'],
            prohibited_streets=zone_cfg.get('prohibited_streets', []),
            color=zone_cfg['color']
        )
        
        zones.append(zone)
    
    # Route types
    route_types = config.get('route_types', {})
    
    return bbox, start_point, zones, route_types


def save_configuration(json_path: str, bbox: tuple, start_point: tuple, 
                       zones: List[Zone], route_types: Dict = None):
    """
    Save configuration to JSON file
    
    Args:
        json_path: Path where to save JSON
        bbox: Bounding box
        start_point: Coordinates of start point
        zones: List of zones
        route_types: Dictionary of route types (optional)
    """
    config = {
        "configuration": {
            "bbox": {
                "description": "Bounding box (west, south, east, north)",
                "west": bbox[0],
                "south": bbox[1],
                "east": bbox[2],
                "north": bbox[3]
            },
            "start_point": {
                "description": "Start and return point (lat, lon)",
                "latitude": start_point[0],
                "longitude": start_point[1]
            }
        },
        "zones": []
    }
    
    # Serialize zones
    for zone in zones:
        coords = list(zone.polygon.exterior.coords[:-1])  # Exclude last coord (duplicated)
        
        zone_cfg = {
            "name": zone.name,
            "polygon": coords,
            "schedule": {
                "start": zone.start_time.strftime("%H:%M"),
                "end": zone.end_time.strftime("%H:%M")
            },
            "weekdays": zone.weekdays,
            "prohibited_streets": zone.prohibited_streets,
            "color": zone.color
        }
        
        config["zones"].append(zone_cfg)
    
    # Add route types if they exist
    if route_types:
        config["route_types"] = route_types
    
    # Save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration saved to: {json_path}")


def example_config_usage():
    """Example usage with configuration file"""
    from route_optimizer import RouteOptimizer
    
    # Load configuration
    bbox, start_point, zones, route_types = load_configuration('zone_config.json')
    
    print("📋 Configuration loaded:")
    print(f"   • Area: {bbox}")
    print(f"   • Start point: {start_point}")
    print(f"   • Zones: {[z.name for z in zones]}")
    print(f"   • Route types: {list(route_types.keys())}")
    
    # Create optimizer
    optimizer = RouteOptimizer(
        bbox=bbox,
        start_point=start_point,
        zones=zones
    )
    
    # Continue with normal process...
    optimizer.download_street_network()
    optimizer.label_zones()
    
    return optimizer, route_types


if __name__ == "__main__":
    example_config_usage()
