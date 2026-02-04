#!/usr/bin/env python3
"""
Simple test script to validate KWB integration setup
"""
import sys
import os

# Add the custom component to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        from kwb_heaters import DOMAIN, PLATFORMS
        print(f"✓ Main module imported successfully. Domain: {DOMAIN}, Platforms: {PLATFORMS}")
        
        from kwb_heaters.const import MANUFACTURER, DEFAULT_PORT
        print(f"✓ Constants imported. Manufacturer: {MANUFACTURER}, Default port: {DEFAULT_PORT}")
        
        from kwb_heaters.src.impl.appliance import Appliance
        print("✓ Appliance class imported successfully")
        
        from kwb_heaters.src.api.platform.sensor.sensor_coordinated import CoordinatedSensor
        print("✓ CoordinatedSensor imported successfully")
        
        from kwb_heaters.src.impl.config.sensor.entities import setup_entities
        print("✓ Entity setup function imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_pykwb_dependency():
    """Test that pykwb dependency is available"""
    try:
        from pykwb.kwb import load_signal_maps
        signal_maps = load_signal_maps()
        print(f"✓ pykwb imported and signal maps loaded: {len(signal_maps) if signal_maps else 0} maps")
        return True
    except ImportError as e:
        print(f"✗ pykwb import error: {e}")
        print("  Make sure pykwb is installed: pip install git+https://github.com/alangibson/pykwb.git@more-registers#pykwb==0.1.4")
        return False
    except Exception as e:
        print(f"✗ pykwb error: {e}")
        return False

if __name__ == "__main__":
    print("Testing KWB Home Assistant Integration...")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_pykwb_dependency()
    
    print("=" * 50)
    if success:
        print("✓ All tests passed! Integration should work correctly.")
    else:
        print("✗ Some tests failed. Check the errors above.")
        sys.exit(1)
