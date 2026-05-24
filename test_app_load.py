import sys
import os
import importlib

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_preload():
    from app import SCREEN_MODULES
    for key, (mod_name, cls_name) in SCREEN_MODULES.items():
        try:
            mod = importlib.import_module(mod_name)
            cls = getattr(mod, cls_name, None)
            if not cls:
                print(f"FAILED: {key} (Class {cls_name} not found in {mod_name})")
            else:
                print(f"OK: {key}")
        except Exception as e:
            print(f"ERROR: {key} ({mod_name}): {e}")

if __name__ == "__main__":
    test_preload()
