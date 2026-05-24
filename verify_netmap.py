
import tkinter as tk
import customtkinter as ctk
import importlib
import sys
import os
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from widgets import apply_theme
from app import SCREEN_MODULES

def test_screens():
    root = ctk.CTk()
    apply_theme('dark')
    
    class MockApp:
        def __init__(self):
            self.root = root
            self._last_score = 100
            self._frames = {}
        def _show_toast(self, t, m, l): pass

    # Mock after to be synchronous or just print
    def mock_after(self, ms, func, *args):
        # We don't want to actually run loops, but for netmap we might want to see if it crashes
        # when the function is actually called.
        return "mock_job"
    
    ctk.CTkFrame.after = mock_after
    ctk.CTk.after = mock_after

    app = MockApp()
    
    results = {}
    
    for key, (mod_name, cls_name) in SCREEN_MODULES.items():
        print(f"Testing screen: {key} ({mod_name}.{cls_name})")
        try:
            mod = importlib.import_module(mod_name)
            cls = getattr(mod, cls_name)
            
            # Instantiate
            screen = cls(root, app)
            app._frames[key] = screen
            
            # Trigger lazy load
            if hasattr(screen, 'on_focus'):
                screen.on_focus()
            
            # Specific check for netmap _draw_map
            if key == 'netmap':
                print("  Testing netmap._draw_map directly...")
                # Mock devices to ensure others is not empty
                screen._devices = [{'is_gw': True, 'ip': '1.1.1.1', 'mac': 'aa'}, {'is_gw': False, 'ip': '1.1.1.2', 'mac': 'bb'}]
                # Set dummy width/height if needed
                screen.canvas = tk.Canvas(root, width=500, height=500)
                screen._draw_map()
                print("  netmap._draw_map passed.")

            results[key] = "OK"
            print(f"  {key}: OK")
            
        except Exception as e:
            results[key] = f"FAIL: {e}"
            print(f"  {key}: FAILED - {e}")
            import traceback
            traceback.print_exc()

    print("\nSummary:")
    for key, res in results.items():
        print(f"{key:15}: {res}")
    
    if all(r == "OK" for r in results.values()):
        print("\nAll screens passed basic verification.")
    else:
        print("\nSome screens FAILED verification.")
        sys.exit(1)

if __name__ == "__main__":
    # Use a timeout for the whole test to prevent hanging
    test_thread = threading.Thread(target=test_screens)
    test_thread.start()
    test_thread.join(timeout=30)
    if test_thread.is_alive():
        print("Test timed out!")
        sys.exit(1)
    sys.exit(0)
