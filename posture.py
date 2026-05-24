"""
Mint Scan v11.1 — Security Posture Dashboard
Unified risk scoring and strategic overview.
"""
import tkinter as tk
import customtkinter as ctk
import math, time, threading
from widgets import C, MONO, MONO_SM, FONT, ScrollableFrame, Card, SectionHeader, InfoGrid, ResultBox, Btn
from database import db
from utils import run_cmd

class PostureDial(tk.Canvas):
    def __init__(self, parent, size=280, **kwargs):
        super().__init__(parent, width=size, height=size, bg=C['bg'], 
                         highlightthickness=0, **kwargs)
        self._size = size
        self._target = 100
        self._score = 100
        self._after = None
        self._draw(100)

    def set_score(self, val):
        self._target = max(0, min(100, val))
        if self._after:
            self.after_cancel(self._after)
        self._animate()

    def _animate(self):
        diff = self._target - self._score
        if abs(diff) > 0.5:
            self._score += diff * 0.1
            self._draw(self._score)
            self._after = self.after(20, self._animate)
        else:
            self._score = self._target
            self._draw(self._score)

    def _draw(self, score):
        self.delete('all')
        s = self._size
        cx = cy = s // 2
        r = s // 2 - 30
        lw = 20

        # BG track
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=135, extent=270,
                        style='arc', outline=C['sf'], width=lw+4)
        
        # Color based on score
        t = score / 100
        if t > 0.8: col = C['ok']
        elif t > 0.5: col = C['am']
        else: col = C['wn']

        if score > 0:
            self.create_arc(cx-r, cy-r, cx+r, cy+r, start=135, extent=-(270*t),
                            style='arc', outline=col, width=lw)

        # Center Text
        self.create_text(cx, cy-15, text=f"{int(score)}%", 
                         fill=C['tx'], font=(FONT, 42, 'bold'))
        self.create_text(cx, cy+25, text="SECURITY POSTURE", 
                         fill=C['mu'], font=(FONT, 10, 'bold'))
        
        status = "EXCELLENT" if t > 0.9 else "GOOD" if t > 0.7 else "FAIR" if t > 0.5 else "CRITICAL"
        self.create_text(cx, cy+45, text=status, 
                         fill=col, font=(FONT, 12, 'bold'))

class PostureScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=C['bg'], corner_radius=0)
        self.app = app
        self._build()

    def on_focus(self):
        self._update_telemetry()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=C['sf'], height=48, corner_radius=0)
        hdr.pack(fill='x')
        ctk.CTkLabel(hdr, text="🛡  STRATEGIC RISK OVERVIEW", 
                     font=(FONT, 13, 'bold'), text_color=C['ac']).pack(side='left', padx=16)
        
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill='both', expand=True)
        body = self.scroll

        # ── Dial Section ──────────────────────────────────────────
        top_row = ctk.CTkFrame(body, fg_color='transparent')
        top_row.pack(fill='x', padx=20, pady=20)
        
        self.dial = PostureDial(top_row, size=300)
        self.dial.pack(side='left', padx=20)

        summary_card = Card(top_row)
        summary_card.pack(side='left', fill='both', expand=True, padx=(20,0))
        
        ctk.CTkLabel(summary_card, text="EXECUTIVE SUMMARY", 
                     font=(FONT, 14, 'bold'), text_color=C['ac']).pack(anchor='w', padx=15, pady=(15,5))
        
        self.summary_text = ctk.CTkLabel(summary_card, text="Analyzing system telemetry...",
                                         font=MONO_SM, text_color=C['tx'], justify='left', anchor='w')
        self.summary_text.pack(anchor='w', padx=15, pady=5)

        # ── Component Status ──────────────────────────────────────
        SectionHeader(body, '01', 'CRITICAL COMPONENTS').pack(fill='x', padx=14, pady=(10,4))
        self.comp_frame = ctk.CTkFrame(body, fg_color='transparent')
        self.comp_frame.pack(fill='x', padx=14, pady=(0,10))
        
        self.components = {}
        for key, name in [('fw', 'Firewall'), ('ids', 'IDS/IPS'), ('mal', 'Malware Scan'), ('bin', 'Binary Integrity')]:
            card = Card(self.comp_frame)
            card.pack(side='left', fill='both', expand=True, padx=4)
            ctk.CTkLabel(card, text=name, font=(FONT, 10, 'bold'), text_color=C['mu']).pack(pady=(10,2))
            lbl = ctk.CTkLabel(card, text="CHECKING...", font=(FONT, 12, 'bold'), text_color=C['tx'])
            lbl.pack(pady=(0,10))
            self.components[key] = lbl

        # ── Recent Intelligence ───────────────────────────────────
        SectionHeader(body, '02', 'LATEST INTELLIGENCE').pack(fill='x', padx=14, pady=(10,4))
        intel_card = Card(body)
        intel_card.pack(fill='x', padx=14, pady=(0,20))
        
        self.intel_box = ctk.CTkTextbox(intel_card, height=150, font=MONO_SM, 
                                         fg_color=C['bg'], text_color=C['tx'], border_width=0)
        self.intel_box.pack(fill='x', padx=10, pady=10)
        self.intel_box.configure(state='disabled')

    def _update_telemetry(self):
        threading.Thread(target=self._telemetry_worker, daemon=True).start()

    def _telemetry_worker(self):
        score = 100
        reasons = []
        
        # 1. Firewall
        fw_out, _, rc = run_cmd('ufw status')
        fw_active = (rc == 0 and 'active' in fw_out.lower())
        if not fw_active:
            score -= 25
            reasons.append("Firewall is DISABLED.")
            self.after(0, lambda: self.components['fw'].configure(text="OFFLINE", text_color=C['wn']))
        else:
            self.after(0, lambda: self.components['fw'].configure(text="SECURE", text_color=C['ok']))

        # 2. IDS/IPS
        # Simple check if Guardian is active
        guardian_active = False
        try:
            # We check the app's _frames if it's already instantiated
            if 'guardian' in self.app._frames:
                guardian_active = self.app._frames['guardian']._guardian_active
        except: pass
        
        if not guardian_active:
            score -= 15
            reasons.append("Guardian IPS is INACTIVE.")
            self.after(0, lambda: self.components['ids'].configure(text="INACTIVE", text_color=C['am']))
        else:
            self.after(0, lambda: self.components['ids'].configure(text="MONITORING", text_color=C['ok']))

        # 3. Binary Integrity
        cursor = db.conn.cursor()
        cursor.execute("SELECT count(*) as count FROM file_baseline")
        baseline_count = cursor.fetchone()['count']
        if baseline_count == 0:
            score -= 10
            reasons.append("No file baseline established.")
            self.after(0, lambda: self.components['bin'].configure(text="NOT SET", text_color=C['am']))
        else:
            self.after(0, lambda: self.components['bin'].configure(text=f"{baseline_count} FILES", text_color=C['ok']))

        # 4. Recent Events
        events = db.get_recent_events(limit=5)
        crit_count = sum(1 for e in events if e['level'] == 'CRITICAL')
        if crit_count > 0:
            score -= min(30, crit_count * 10)
            reasons.append(f"{crit_count} recent critical event(s) detected.")

        # Update UI
        self.after(0, lambda: self.dial.set_score(score))
        
        summary = "No immediate threats detected." if score > 80 else "System needs attention."
        if reasons:
            summary = "\n".join([f"• {r}" for r in reasons])
        self.after(0, lambda: self.summary_text.configure(text=summary))
        
        # Update Intel Box
        self.after(0, self._update_intel, events)

    def _update_intel(self, events):
        self.intel_box.configure(state='normal')
        self.intel_box.delete('1.0', 'end')
        if not events:
            self.intel_box.insert('end', "No security events recorded in database.")
        else:
            for e in events:
                ts = e['timestamp']
                src = e['source']
                lvl = e['level']
                msg = e['description']
                self.intel_box.insert('end', f"[{ts}] {lvl} | {src}: {msg}\n")
        self.intel_box.configure(state='disabled')
