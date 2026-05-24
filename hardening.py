"""
Mint Scan v11.1 — Security Hardening Profiles
Automated one-click security configurations.
"""
import customtkinter as ctk
import threading, time, os
from widgets import (ScrollableFrame, Card, SectionHeader, 
                     Btn, C, MONO, MONO_SM, ResultBox)
from utils import run_cmd

class HardeningScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=C['bg'], corner_radius=0)
        self.app = app
        self._built = False
        self._applying = False

    def on_focus(self):
        if not self._built:
            self._build()
            self._built = True

    def on_blur(self):
        pass

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=C['sf'], height=48, corner_radius=0)
        hdr.pack(fill='x')
        ctk.CTkLabel(hdr, text='🛡  SECURITY HARDENING',
                     font=('DejaVu Sans Mono', 13, 'bold'),
                     text_color=C['ac']).pack(side='left', padx=16)

        body = ScrollableFrame(self)
        body.pack(fill='both', expand=True)
        self._body_frame = body

        SectionHeader(body, '01', 'HARDENING PROFILES').pack(fill='x', padx=14, pady=(14, 4))
        
        profiles = [
            ('Standard', 'Balanced security and usability.', 'primary', [
                "sudo ufw enable",
                "sudo ufw default deny incoming",
                "sudo ufw default allow outgoing"
            ]),
            ('Work/Office', 'Restricted access for professional environments.', 'blue', [
                "sudo ufw enable",
                "sudo ufw default deny incoming",
                "sudo ufw allow 22/tcp", # Allow SSH
                "sudo ufw allow 80,443/tcp" # Allow Web
            ]),
            ('Public Wi-Fi', 'Stealth mode. All incoming blocked.', 'warning', [
                "sudo ufw enable",
                "sudo ufw default deny incoming",
                "sudo ufw logging on",
                "sudo sysctl -w net.ipv4.icmp_echo_ignore_all=1"
            ]),
            ('Paranoid', 'Maximum lockdown. Minimal services.', 'danger', [
                "sudo ufw enable",
                "sudo ufw default deny incoming",
                "sudo ufw default deny outgoing",
                "sudo ufw allow out 53,80,443/tcp", # Only DNS/Web out
                "sudo sysctl -w net.ipv4.conf.all.rp_filter=1",
                "sudo sysctl -w net.ipv4.conf.all.accept_source_route=0"
            ])
        ]

        self._p_btns = []
        for name, desc, var, cmds in profiles:
            p_card = Card(body)
            p_card.pack(fill='x', padx=14, pady=4)
            
            ctk.CTkLabel(p_card, text=name.upper(), font=('DejaVu Sans Mono', 12, 'bold'), text_color=C['ac']).pack(anchor='w', padx=12, pady=(10,2))
            ctk.CTkLabel(p_card, text=desc, font=MONO_SM, text_color=C['mu']).pack(anchor='w', padx=12, pady=(0,8))
            
            btn = Btn(p_card, f'APPLY {name.upper()} PROFILE', 
                command=lambda c=cmds, n=name: self._apply_profile(n, c),
                variant=var, width=220)
            btn.pack(anchor='w', padx=12, pady=(0,12))
            self._p_btns.append(btn)

        self.res_box = ctk.CTkFrame(body, fg_color='transparent')
        self.res_box.pack(fill='x', padx=14, pady=10)

    def _apply_profile(self, name, cmds):
        if self._applying: return
        self._applying = True
        for b in self._p_btns: b.configure(state='disabled')

        for w in self.res_box.winfo_children(): w.destroy()
        ResultBox(self.res_box, 'ac', 'APPLYING PROFILE...', f'Executing hardening rules for {name}...').pack(fill='x')
        
        def _bg():
            success = True
            for cmd in cmds:
                _, _, rc = run_cmd(cmd, timeout=10)
                if rc != 0: success = False
            
            def _done():
                self._applying = False
                for b in self._p_btns: b.configure(state='normal')
                for w in self.res_box.winfo_children(): w.destroy()
                if success:
                    ResultBox(self.res_box, 'ok', f'{name.upper()} APPLIED', 'System has been hardened successfully.').pack(fill='x')
                else:
                    ResultBox(self.res_box, 'warn', 'PARTIAL SUCCESS', 'Some rules could not be applied. Check sudo permissions.').pack(fill='x')
            
            self.after(0, _done)
            
        threading.Thread(target=_bg, daemon=True).start()
