#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify Installation - Route Optimizer
======================================

This script verifies that all dependencies are correctly installed
and the main module works properly.

Usage: python verify_install.py
"""

import sys
import subprocess


def install_dependencies():
    """Install necessary dependencies"""
    print("🔧 Installing dependencies...")
    
    packages = [
        'osmnx',
        'networkx',
        'pandas',
        'geopandas',
        'matplotlib',
        'shapely',
        'openpyxl'
    ]
    
    for package in packages:
        print(f"   • Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-q", "--break-system-packages"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"     ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"     ⚠️  Error installing {package}")
    
    print("\n✅ Installation complete")


def verify_installation():
    """Verify that all modules are correctly installed"""
    print("\n🔍 Verifying installation...")
    
    modules = {
        'osmnx': 'osmnx',
        'networkx': 'networkx',
        'pandas': 'pandas',
        'geopandas': 'geopandas',
        'matplotlib': 'matplotlib.pyplot',
        'shapely': 'shapely.geometry',
        'openpyxl': 'openpyxl'
    }
    
    all_ok = True
    
    for name, import_path in modules.items():
        try:
            __import__(import_path)
            print(f"   ✅ {name}")
        except ImportError as e:
            print(f"   ❌ {name} - {e}")
            all_ok = False
    
    if all_ok:
        print("\n🎉 All dependencies are correctly installed")
    else:
        print("\n⚠️  Some dependencies are missing. Run installation again.")
    
    return all_ok


def test_module():
    """Basic test of the main module"""
    print("\n🧪 Testing route_optimizer module...")
    
    try:
        from route_optimizer import Zone, RouteOptimizer
        from shapely.geometry import Polygon
        from datetime import time
        
        # Create test zone
        test_zone = Zone(
            name='test',
            polygon=Polygon([(-57.96, -34.92), (-57.95, -34.92), 
                             (-57.95, -34.91), (-57.96, -34.91)]),
            start_time=time(8, 0),
            end_time=time(14, 0),
            weekdays=[0, 1, 2, 3, 4],
            color='blue'
        )
        
        print("   ✅ Test zone created successfully")
        print(f"      • Name: {test_zone.name}")
        print(f"      • Schedule: {test_zone.start_time} - {test_zone.end_time}")
        print(f"      • Weekdays: {test_zone.weekdays}")
        
        print("\n✅ Module works correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing module: {e}")
        return False


def show_files():
    """Display available files"""
    print("\n📁 Project files:")
    print("   • route_optimizer.py  → Main module")
    print("   • config_loader.py               → Configuration loader")
    print("   • parking_enforcement.py → CPP example (cover streets)")
    print("   • delivery_route.py      → TSP example (visit points)")
    print("   • optimized_routes.py            → Notebook as script")
    print("   • zone_config.json               → Zone configuration")
    print("   • README.md                      → Complete documentation")
    print("   • QUICKSTART.md                  → Quick start guide")


def main():
    """Main function"""
    print("="*70)
    print(" 🚗 SETUP - ROUTE OPTIMIZER")
    print("="*70)
    
    # Install dependencies
    install_dependencies()
    
    # Verify installation
    if verify_installation():
        # Test module
        if test_module():
            show_files()
            
            print("\n" + "="*70)
            print(" ✅ READY TO USE")
            print("="*70)
            print("\n📝 Next steps:")
            print("   1. Run: python parking_enforcement.py  (CPP)")
            print("      or:  python delivery_route.py       (TSP)")
            print("   2. Review: QUICKSTART.md")
            print("   3. Customize: zone_config.json")
            print("\n💡 For more details, see README.md")
            print("="*70)
        else:
            print("\n⚠️  There are issues with the main module")
    else:
        print("\n⚠️  Complete dependency installation first")


if __name__ == "__main__":
    main()
