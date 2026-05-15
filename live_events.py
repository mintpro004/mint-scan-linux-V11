"""
Mint Scan v8 — Black Box Live Events
Real-time color-coded system event visualizer.
"""
import customtkinter as ctk
import threading, subprocess, time, os, re
from widgets import (ScrollableFrame, Card, SectionHeader, 
                     Btn, C, MONO, MONO_SM)

class LiveEventsScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=C['bg'], corner_radius=0)
        self.app = app
        self._built = False
        self._monitoring = False
        self._proc = None

    def on_focus(self):
        if not self._built:
            self._build()
            self._built = True
        self._start_monitor()

    def on_blur(self):
        self._stop_monitor()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=C['sf'], height=48, corner_radius=0)
        hdr.pack(fill='x')
        ctk.CTkLabel(hdr, text='📊  LIVE EVENT VISUALIZER',
                     font=('DejaVu Sans Mono', 13, 'bold'),
                     text_color=C['ac']).pack(side='left', padx=16)

        self.status_lbl = ctk.CTkLabel(hdr, text='● LIVE', font=MONO_SM, text_color=C['ok'])
        self.status_lbl.pack(side='right', padx=16)

        self.log_box = ctk.CTkTextbox(self, font=('DejaVu Sans Mono', 10),
                                      fg_color='#010d18', text_color='#c8e6ff',
                                      border_width=0, corner_radius=0)
        self.log_box.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tags for coloring
        self.log_box.tag_config('auth', foreground=C['am'])
        self.log_box.tag_config('usb',  foreground=C['bl'])
        self.log_box.tag_config('crit', foreground=C['wn'], font=('DejaVu Sans Mono', 10, 'bold'))
        self.log_box.tag_config('net',  foreground=C['ok'])

    def _start_monitor(self):
        if self._monitoring: return
        self._monitoring = True
        self.status_lbl.configure(text='● LIVE', text_color=C['ok'])
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def _stop_monitor(self):
        self._monitoring = False
        if self._proc:
            self._proc.terminate()
            self._proc = None
        self.status_lbl.configure(text='○ PAUSED', text_color=C['mu'])

    def _monitor_loop(self):
        # Use sudo -n (non-interactive) to avoid hanging, or fallback to user journal if permitted
        cmd = "sudo -n journalctl -f -n 100 2>/dev/null || journalctl --user -f -n 50 2>/dev/null"
        
        self._safe_append("🔄 INITIALISING BLACK BOX MONITOR...\n", tag='net')
        
        try:
            self._proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, text=True,
                                          bufsize=1, universal_newlines=True)
            
            # Check if process started successfully
            time.sleep(0.5)
            if self._proc.poll() is not None:
                # Process died immediately
                err = self._proc.stderr.read()
                self._safe_append(f"❌ MONITOR FAILED TO START: {err or 'Access Denied'}\n", tag='crit')
                self._safe_append("Tip: Ensure your user is in the 'systemd-journal' group.\n", tag='net')
                return

            for line in self._proc.stdout:
                if not self._monitoring: break
                if line.strip():
                    self._safe_append(line)
                    
        except Exception as e:
            self._safe_append(f"❌ MONITOR ERROR: {e}\n", tag='crit')
        finally:
            self._monitoring = False
            self.after(0, lambda: self.status_lbl.configure(text='○ STOPPED', text_color=C['mu']))

    def _safe_append(self, line, tag=None):
        def _do():
            if not self.winfo_exists(): return
            
            # Auto-tagging logic if tag not provided
            effective_tag = tag
            if not effective_tag:
                l = line.lower()
                if 'session opened' in l or 'password' in l: effective_tag = 'auth'
                elif 'usb' in l: effective_tag = 'usb'
                elif 'error' in l or 'critical' in l or 'fail' in l: effective_tag = 'crit'
                elif 'eth0' in l or 'wlan0' in l or 'network' in l: effective_tag = 'net'
            
            self.log_box.insert('end', line, effective_tag)
            self.log_box.see('end')
            
            # Cap lines
            count = int(self.log_box.index('end').split('.')[0])
            if count > 1000:
                self.log_box.delete('1.0', '2.0')
                
        self.after(0, _do)
