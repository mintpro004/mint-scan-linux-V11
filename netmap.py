"""
Mint Scan v11.1 — Network Map
Visual representation of connected devices on the local network.
Industry-standard graph-like layout with real-time status.
"""
import tkinter as tk
import customtkinter as ctk
import threading, subprocess, re, time, os, math
from widgets import C, Btn, Card, SectionHeader
from utils import run_cmd as run
from database import db

class NetworkMapScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=C['bg'], corner_radius=0)
        self.app = app
        self._built = False
        self._scanning = False
        self._devices = []

    def on_focus(self):
        if not self._built:
            self._build()
            self._built = True
        if not self._devices:
            self._refresh_map()

    def on_blur(self):
        self._scanning = False

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=C['sf'], height=48, corner_radius=0)
        hdr.pack(fill='x')
        ctk.CTkLabel(hdr, text="🕸  NETWORK MAP", font=('DejaVu Sans Mono',13,'bold'),
                     text_color=C['ac']).pack(side='left', padx=16)

        Btn(hdr, "⟳ REFRESH", command=self._refresh_map, width=100).pack(side='right', padx=12, pady=6)

        self.canvas = tk.Canvas(self, bg=C['bg'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tooltip/Info panel
        self.info_panel = ctk.CTkFrame(self, fg_color=C['s2'], height=100, corner_radius=8)
        self.info_panel.pack(fill='x', padx=20, pady=(0,20))
        self.info_lbl = ctk.CTkLabel(self.info_panel, text="Hover over a device to see details", 
                                     font=('DejaVu Sans Mono',10), text_color=C['mu'])
        self.info_lbl.pack(pady=20)

    def _refresh_map(self):
        if self._scanning: return
        self._scanning = True
        self.canvas.delete('all')
        self.info_lbl.configure(text="🔍 Scanning network map...")
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        ip_out, _, _ = run("ip route | grep -v default | grep '/' | head -1 | awk '{print $1}'")
        subnet = ip_out.strip() or '192.168.1.0/24'
        
        # Use arp-scan or nmap -sn for fast discovery
        out, _, rc = run(f"nmap -sn {subnet} 2>/dev/null", timeout=30)
        
        devices = []
        # Get Gateway
        gw_out, _, _ = run("ip route | grep default | awk '{print $3}' | head -1")
        gateway = gw_out.strip()
        
        if rc == 0:
            cur_ip = None
            for line in out.splitlines():
                if "Nmap scan report for" in line:
                    m = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if m: cur_ip = m.group(1)
                elif "MAC Address:" in line and cur_ip:
                    m = re.search(r'([0-9A-F:]{17})', line, re.I)
                    mac = m.group(1) if m else "Unknown"
                    v_m = re.search(r'\((.+)\)', line)
                    vendor = v_m.group(1) if v_m else "Generic"
                    devices.append({'ip': cur_ip, 'mac': mac, 'vendor': vendor, 'is_gw': cur_ip == gateway})
                    cur_ip = None
        
        # Add local machine
        my_ip_out, _, _ = run("hostname -I | awk '{print $1}'")
        my_ip = my_ip_out.strip()
        devices.append({'ip': my_ip, 'mac': 'LOCAL', 'vendor': 'This Device', 'is_local': True})
        
        # Ensure Gateway is in list even if nmap missed it
        if gateway and not any(d['ip'] == gateway for d in devices):
            devices.append({'ip': gateway, 'mac': 'Unknown', 'vendor': 'Gateway', 'is_gw': True})

        self._devices = devices
        self.after(0, self._draw_map)
        self._scanning = False

    def _draw_map(self):
        self.canvas.delete('all')
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100: w = 800; h = 500 # Fallback
        
        cx, cy = w // 2, h // 2
        aliases = db.get_aliases()
        
        # Draw Gateway (Center)
        gw = next((d for d in self._devices if d.get('is_gw')), None)
        others = [d for d in self._devices if not d.get('is_gw')]
        
        # Draw connections first
        radius = min(w, h) // 3
        for i, dev in enumerate(others):
            angle = (2 * math.pi * i) / len(others) if others else 0
            dx = cx + radius * math.cos(angle)
            dy = cy + radius * math.sin(angle)
            self.canvas.create_line(cx, cy, dx, dy, fill=C['br'], width=1, dash=(4,4))

        # Draw Gateway node
        gw_ip = gw['ip'] if gw else "192.168.1.1"
        gw_mac = gw['mac'] if gw else "Unknown"
        gw_label = aliases.get(gw_mac, "GATEWAY")
        self._draw_node(cx, cy, "🌐", gw_label, gw_ip, gw_mac, is_gw=True)

        # Draw other nodes
        for i, dev in enumerate(others):
            angle = (2 * math.pi * i) / len(others)
            dx = cx + radius * math.cos(angle)
            dy = cy + radius * math.sin(angle)
            
            icon = "💻" if dev.get('is_local') else "📱"
            mac = dev.get('mac', 'Unknown')
            label = aliases.get(mac, dev['vendor'][:12])
            self._draw_node(dx, dy, icon, label, dev['ip'], mac, is_local=dev.get('is_local'))

        self.info_lbl.configure(text=f"Network map complete: Found {len(self._devices)} devices.")

    def _draw_node(self, x, y, icon, label, ip, mac, is_gw=False, is_local=False):
        r = 30
        color = C['ac'] if is_gw else C['bl'] if is_local else C['mu']
        
        # Glow
        self.canvas.create_oval(x-r-5, y-r-5, x+r+5, y+r+5, outline=color, width=1, stipple='gray50')
        
        # Circle
        node = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=C['sf'], outline=color, width=2)
        
        # Icon
        self.canvas.create_text(x, y-5, text=icon, font=('Arial', 16))
        
        # Label
        self.canvas.create_text(x, y+15, text=label, font=('DejaVu Sans Mono', 8, 'bold'), fill=C['tx'])
        
        # Bindings for info
        def _on_enter(e, ip=ip, label=label, mac=mac):
            self.info_lbl.configure(text=f"DEVICE: {label}  |  IP: {ip}  |  MAC: {mac}")
            self.canvas.itemconfig(node, fill=C['s2'], width=3)
            
        def _on_leave(e):
            self.canvas.itemconfig(node, fill=C['sf'], width=2)

        def _on_right_click(e, mac=mac, label=label):
            self._edit_alias(mac, label)

        self.canvas.tag_bind(node, '<Enter>', _on_enter)
        self.canvas.tag_bind(node, '<Leave>', _on_leave)
        self.canvas.tag_bind(node, '<Button-3>', _on_right_click) # Right click
        self.canvas.tag_bind(node, '<Button-1>', _on_enter) # Tap/Click focus

    def _edit_alias(self, mac, current_label):
        if mac == 'Unknown' or mac == 'LOCAL': return
        
        dialog = ctk.CTkInputDialog(text=f"Enter alias for {mac}:", title="Edit Device Alias")
        alias = dialog.get_input()
        if alias is not None:
            db.set_alias(mac, alias)
            self._draw_map()
