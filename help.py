"""
Help & Troubleshooting — central documentation for common issues.
"""
import tkinter as tk
import customtkinter as ctk
from widgets import ScrollableFrame, Card, SectionHeader, Btn, C, MONO, MONO_SM, FONT

HELP_CONTENT = [
    {
        'title': 'Chromebook / Crostini Sync',
        'icon':  '📶',
        'body': (
            "Because Linux on ChromeOS runs in a container, your phone cannot see the server by default.\n\n"
            "1. Open ChromeOS Settings → Developers → Linux → Port Forwarding.\n"
            "2. Click 'Add' and enter Port 8765 (TCP).\n"
            "3. Find your Chromebook's IP in Wi-Fi settings (usually 192.168.1.x).\n"
            "4. In Mint Scan Wireless Sync, click the 'CONNECT' URL and enter that IP manually.\n"
            "5. Scan the updated QR code with your phone."
        )
    },
    {
        'title': 'Sudo & Permissions',
        'icon':  '🔑',
        'body': (
            "Most security tools require root privileges. Mint Scan tries to use 'sudo -n' (non-interactive).\n\n"
            "• If a tool fails with [SUDO REQUIRED], run Mint Scan from a terminal where you've recently used sudo.\n"
            "• Alternatively, ensure your user is in the 'sudo' or 'wheel' group.\n"
            "• Some features (like firewall control) will NEVER work without sudo."
        )
    },
    {
        'title': 'WSL2 (Windows Subsystem for Linux)',
        'icon':  '🪟',
        'body': (
            "WSL2 also uses NAT, similar to Chromebooks.\n\n"
            "• Use 'PowerShell' as Admin to forward ports: \n"
            "  netsh interface portproxy add v4tov4 listenport=8765 listenaddress=0.0.0.0 connectport=8765 connectaddress=<WSL_IP>\n"
            "• Ensure Windows Firewall allows traffic on port 8765."
        )
    },
    {
        'title': 'Database & Performance',
        'icon':  '📦',
        'body': (
            "If the app feels slow or the database file is large:\n\n"
            "1. Go to SETTINGS → MAINTENANCE.\n"
            "2. Click 'OPTIMISE DATABASE'.\n"
            "3. This will remove events older than 30 days and compact the file.\n"
            "4. Logs can also be cleared in the 'SYSTEM TWEAKS' section."
        )
    },
    {
        'title': 'Missing Tools / Dependencies',
        'icon':  '🛠',
        'body': (
            "If modules show '✗ NOT INSTALLED' or empty data:\n\n"
            "1. Go to SETTINGS → DEPENDENCIES.\n"
            "2. Click 'SCAN' to see what is missing.\n"
            "3. Click 'INSTALL MISSING' to automatically download required system packages.\n"
            "4. A stable internet connection is required."
        )
    }
]

class HelpScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=C['bg'], corner_radius=0)
        self.app = app
        self._built = False

    def on_focus(self):
        if not self._built:
            self._build()
            self._built = True

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color=C['sf'], height=48, corner_radius=0)
        hdr.pack(fill='x')
        ctk.CTkLabel(hdr, text="❓  HELP & TROUBLESHOOTING",
                     font=(FONT, 13, 'bold'), text_color=C['ac']
                     ).pack(side='left', padx=16)

        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill='both', expand=True)
        body = self.scroll

        SectionHeader(body, '01', 'COMMON SOLUTIONS').pack(fill='x', padx=14, pady=(14,4))

        for item in HELP_CONTENT:
            card = Card(body)
            card.pack(fill='x', padx=14, pady=6)
            
            title_row = ctk.CTkFrame(card, fg_color='transparent')
            title_row.pack(fill='x', padx=12, pady=(10,5))
            
            ctk.CTkLabel(title_row, text=f"{item['icon']}  {item['title']}", 
                         font=(FONT, 11, 'bold'), text_color=C['ac']).pack(side='left')
            
            ctk.CTkLabel(card, text=item['body'], font=(FONT, 10), 
                         text_color=C['tx'], justify='left', wraplength=700).pack(anchor='w', padx=12, pady=(0,12))

        # Support Note
        note = Card(body, accent=C['bl'])
        note.pack(fill='x', padx=14, pady=20)
        ctk.CTkLabel(note, text="DEVELOPER SUPPORT", font=(FONT, 10, 'bold'), text_color=C['bl']).pack(pady=(10,2))
        ctk.CTkLabel(note, text="For advanced issues, please visit our GitHub repository or contact Mint Projects PTY (Ltd) Support.\nVersion: v11.1 Ultra Professional", 
                     font=(FONT, 9), text_color=C['mu']).pack(pady=(0,10))
        
        ctk.CTkLabel(body, text="", height=20).pack()
