"""
Mint Scan v11.1 — Shared Widgets
3D-depth visual system: raised surfaces, bevel highlights, glow accents.
DejaVu Sans Mono fonts throughout.

Compatibility:
- Python 3.9 – 3.12
- customtkinter 5.x (any minor)
- Linux x86_64 and aarch64 (Ubuntu 20.04+, 22.04+)
- Chromebook Crostini, Kali, WSL2, Raspberry Pi OS 64-bit
- Wayland and X11
"""
import tkinter as tk
import customtkinter as ctk

# ── Theme palettes ────────────────────────────────────────────────
DARK_THEME = {
    'bg':  '#030f1c', 'sf':  '#081c2e', 's2':  '#0c2540',
    'brt': '#1e4a6a', 'brd': '#010810',
    'br':  '#163352', 'br2': '#1e4a6a',
    'ac':  '#00ffe0', 'acg': '#004d44',
    'wn':  '#ff4444', 'am':  '#ffbb33', 'ok':  '#33ff88',
    'bl':  '#44aaff', 'pu':  '#bb77ff',
    'wng': '#3d0000', 'amg': '#3d2d00', 'okg': '#003d20',
    'tx':  '#deeeff', 'mu':  '#5a90b8', 'mu2': '#7ab0d0',
}

LIGHT_THEME = {
    'bg':  '#dde4ed', 'sf':  '#eaf0f8', 's2':  '#ffffff',
    'brt': '#ffffff',  'brd': '#b0c4d8',
    'br':  '#b8cfe0',  'br2': '#8aaabf',
    'ac':  '#005fa3',  'acg': '#d0e8f8',
    'wn':  '#cc1111',  'am':  '#cc7700',  'ok':  '#117744',
    'bl':  '#1155cc',  'pu':  '#6622bb',
    'wng': '#fde8e8',  'amg': '#fff3cd',  'okg': '#d4edda',
    'tx':  '#0d1f2d',  'mu':  '#3a5a70',  'mu2': '#2d4a60',
}

NORD_THEME = {
    'bg':  '#2e3440', 'sf':  '#3b4252', 's2':  '#434c5e',
    'brt': '#4c566a', 'brd': '#242933',
    'br':  '#4c566a', 'br2': '#88c0d0',
    'ac':  '#88c0d0', 'acg': '#3b4252',
    'wn':  '#bf616a', 'am':  '#ebcb8b', 'ok':  '#a3be8c',
    'bl':  '#81a1c1', 'pu':  '#b48ead',
    'wng': '#3b4252', 'amg': '#3b4252', 'okg': '#3b4252',
    'tx':  '#eceff4', 'mu':  '#d8dee9', 'mu2': '#e5e9f0',
}

DRACULA_THEME = {
    'bg':  '#282a36', 'sf':  '#44475a', 's2':  '#6272a4',
    'brt': '#bd93f9', 'brd': '#191a21',
    'br':  '#44475a', 'br2': '#bd93f9',
    'ac':  '#bd93f9', 'acg': '#282a36',
    'wn':  '#ff5555', 'am':  '#ffb86c', 'ok':  '#50fa7b',
    'bl':  '#8be9fd', 'pu':  '#ff79c6',
    'wng': '#282a36', 'amg': '#282a36', 'okg': '#282a36',
    'tx':  '#f8f8f2', 'mu':  '#6272a4', 'mu2': '#f8f8f2',
}

CYBERPUNK_THEME = {
    'bg':  '#000b1e', 'sf':  '#00162d', 's2':  '#002142',
    'brt': '#ff00ff', 'brd': '#00050f',
    'br':  '#003d7a', 'br2': '#ff00ff',
    'ac':  '#00ff00', 'acg': '#00162d',
    'wn':  '#ff0055', 'am':  '#ffff00', 'ok':  '#00ffaa',
    'bl':  '#00ffff', 'pu':  '#ff00ff',
    'wng': '#000b1e', 'amg': '#000b1e', 'okg': '#000b1e',
    'tx':  '#00ff00', 'mu':  '#008800', 'mu2': '#00ff00',
}

THEMES = {
    'dark': DARK_THEME,
    'light': LIGHT_THEME,
    'nord': NORD_THEME,
    'dracula': DRACULA_THEME,
    'cyberpunk': CYBERPUNK_THEME,
}

C = dict(DARK_THEME)

FONT    = 'DejaVu Sans Mono'
MONO    = (FONT, 11)
MONO_SM = (FONT, 10)
MONO_LG = (FONT, 14, 'bold')
MONO_XL = (FONT, 38, 'bold')
_current_theme = 'dark'


def get_theme():
    return _current_theme


def apply_theme(name, accent=None, font_size=11):
    global _current_theme, MONO, MONO_SM, MONO_LG, MONO_XL
    _current_theme = name
    C.update(THEMES.get(name, DARK_THEME))
    if accent:
        C['ac'] = accent
    fs      = max(9, font_size)
    MONO    = (FONT, fs)
    MONO_SM = (FONT, max(8, fs - 1))
    MONO_LG = (FONT, fs + 3, 'bold')
    MONO_XL = (FONT, fs + 27, 'bold')

    # Set CTk global appearance
    ctk.set_appearance_mode('light' if name == 'light' else 'dark')

    try:
        ctk.set_appearance_mode('light' if name == 'light' else 'dark')
    except Exception:
        pass


def load_theme_settings():
    import json, os
    path = os.path.expanduser('~/.mint_scan_settings.json')
    try:
        if os.path.exists(path):
            with open(path) as f:
                s = json.load(f)
                apply_theme(s.get('theme', 'dark'),
                            s.get('accent_color'), s.get('font_size', 11))
                return s.get('ui_scale', 1.0)
    except Exception:
        pass
    apply_theme('dark')
    return 1.0


# ── ScrollableFrame ───────────────────────────────────────────────
class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        fg   = kwargs.pop('fg_color', C['bg'])
        sbc  = kwargs.pop('scrollbar_button_color', C['br2'])
        sbhc = kwargs.pop('scrollbar_button_hover_color', C['ac'])
        cr   = kwargs.pop('corner_radius', 0)
        super().__init__(master=parent, fg_color=fg,
                         scrollbar_button_color=sbc,
                         scrollbar_button_hover_color=sbhc,
                         corner_radius=cr, **kwargs)
        
        # Safe binding: only bind all when mouse is inside
        self.bind("<Enter>", self._bind_mousewheel)
        self.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event=None):
        self.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel, add="+")
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _unbind_mousewheel(self, event=None):
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        try:
            if not self.winfo_exists(): return
            if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
                self._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
                self._parent_canvas.yview_scroll(1, "units")
        except Exception:
            pass


# ── Card ──────────────────────────────────────────────────────────
class Card(ctk.CTkFrame):
    def __init__(self, parent, accent=None, **kwargs):
        fg = kwargs.pop('fg_color', C['sf'])
        cr = kwargs.pop('corner_radius', 10)
        kwargs.pop('border_color', None)
        kwargs.pop('border_width', None)
        super().__init__(parent, fg_color=fg, corner_radius=cr,
                         border_width=1, border_color=accent or C['brt'], **kwargs)

    @property
    def interior(self):
        return self


# ── SectionHeader ─────────────────────────────────────────────────
class SectionHeader(ctk.CTkFrame):
    def __init__(self, parent, num, title, **kwargs):
        fg = kwargs.pop('fg_color', 'transparent')
        super().__init__(parent, fg_color=fg, **kwargs)
        ctk.CTkLabel(
            self, text=f'// {num} — {title}',
            font=(FONT, 9, 'bold'), text_color=C['ac']
        ).pack(side='left', padx=12, pady=6)
        ctk.CTkFrame(self, height=1, fg_color=C['br'],
                     corner_radius=0).pack(
            side='left', fill='x', expand=True, padx=(0, 12))


# ── InfoGrid ──────────────────────────────────────────────────────
class InfoGrid(ctk.CTkFrame):
    def __init__(self, parent, items, columns=3, **kwargs):
        fg = kwargs.pop('fg_color', 'transparent')
        super().__init__(parent, fg_color=fg, **kwargs)
        for i, item in enumerate(items):
            if len(item) == 3:
                label, value, colour = item
            else:
                label, value = item
                colour = C['tx']
            
            cell = ctk.CTkFrame(self, fg_color=C['s2'],
                                corner_radius=6, border_width=0)
            cell.grid(row=i // columns, column=i % columns,
                      padx=4, pady=4, sticky='ew')
            self.columnconfigure(i % columns, weight=1)
            ctk.CTkLabel(cell, text=str(label),
                         font=(FONT, 8), text_color=C['mu']
                         ).pack(anchor='w', padx=8, pady=(5, 0))
            ctk.CTkLabel(cell, text=str(value),
                         font=(FONT, 10, 'bold'), text_color=colour,
                         wraplength=160
                         ).pack(anchor='w', padx=8, pady=(0, 5))


# ── ResultBox ─────────────────────────────────────────────────────
class ResultBox(ctk.CTkFrame):
    def __init__(self, parent, rtype='ok', title='', msg='', body='', height=None, **kwargs):
        # Handle 'body' as alias for 'msg'
        msg = msg or body
        fg = kwargs.pop('fg_color', C['sf'])
        super().__init__(parent, fg_color='transparent', **kwargs)
        
        if rtype == 'ok':
            col = C['ok']
        elif rtype in ('med', 'warn', 'warning'):
            col = C['am']
        elif rtype in ('info', 'blue'):
            col = C['bl']
        else:
            col = C['wn']
        
        self._card = ctk.CTkFrame(self, fg_color=fg, border_color=col, border_width=1, corner_radius=8)
        self._card.pack(fill='both', expand=True)
        
        inner = ctk.CTkFrame(self._card, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=12, pady=10)
        
        icon = '✓' if rtype == 'ok' else '⚠'
        self.title_lbl = ctk.CTkLabel(inner, text=f"{icon} {title}", 
                                      font=(FONT, 11, 'bold'), text_color=col)
        self.title_lbl.pack(anchor='w')
        
        if msg:
            self._box = ctk.CTkTextbox(inner, height=height or 60, font=(FONT, 10),
                                        fg_color='transparent', text_color=C['tx'],
                                        border_width=0, wrap='word')
            self._box.pack(fill='x', pady=(4, 0))
            self._box.insert('1.0', str(msg))
            self._box.configure(state='disabled')
        else:
            self._box = None

    def set(self, text):
        try:
            if self._box and self._box.winfo_exists():
                self._box.configure(state='normal')
                self._box.delete('1.0', 'end')
                self._box.insert('end', str(text))
                self._box.configure(state='disabled')
        except Exception: pass

    def append(self, text):
        try:
            if self._box and self._box.winfo_exists():
                self._box.configure(state='normal')
                self._box.insert('end', str(text) + '\n')
                self._box.see('end')
                self._box.configure(state='disabled')
        except Exception: pass

    def clear(self):
        try:
            if self._box and self._box.winfo_exists():
                self._box.configure(state='normal')
                self._box.delete('1.0', 'end')
                self._box.configure(state='disabled')
        except Exception: pass

    def configure(self, **kwargs):
        if 'rtype' in kwargs:
            rtype = kwargs.pop('rtype')
            col = C['ok'] if rtype == 'ok' else C['am'] if rtype in ('med', 'warn', 'warning') else C['bl'] if rtype in ('info', 'blue') else C['wn']
            self._card.configure(border_color=col)
            self.title_lbl.configure(text_color=col)
            icon = '✓' if rtype == 'ok' else '⚠'
            current_title = self.title_lbl.cget('text')
            if current_title.startswith(('✓', '⚠')):
                self.title_lbl.configure(text=f"{icon} {current_title[2:]}")
        if 'title' in kwargs:
            title = kwargs.pop('title')
            icon = '✓' if self.title_lbl.cget('text').startswith('✓') else '⚠'
            self.title_lbl.configure(text=f"{icon} {title}")
        if 'msg' in kwargs or 'body' in kwargs:
            msg = kwargs.pop('msg', kwargs.pop('body', ''))
            self.set(msg)
        return super().configure(**kwargs)


# ── LiveBadge ─────────────────────────────────────────────────────
class LiveBadge(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self._on = True
        self.dot = ctk.CTkLabel(self, text='●', font=(FONT, 14), text_color=C['ok'])
        self.dot.pack(side='left', padx=(2, 4))
        ctk.CTkLabel(self, text='LIVE', font=(FONT, 9, 'bold'), 
                     text_color=C['mu']).pack(side='left', padx=(0, 2))
        self._pulse()

    def _pulse(self):
        if not self.winfo_exists(): return
        self._on = not self._on
        col = C['ok'] if self._on else C['br']
        try:
            self.dot.configure(text_color=col)
        except Exception: pass
        self.after(800, self._pulse)


# ── Badge ──────────────────────────────────────────────────────────
class Badge(ctk.CTkFrame):
    def __init__(self, parent, text, color=None, **kwargs):
        color = color or C['ac']
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.label = ctk.CTkLabel(self, text=text, font=(FONT, 8, 'bold'), 
                                  text_color=color, fg_color='transparent',
                                  padx=6, pady=2)
        self.label.pack()
        self.configure(border_color=color, border_width=1, corner_radius=10)


# ── PortBar ───────────────────────────────────────────────────────
class PortBar(ctk.CTkFrame):
    def __init__(self, parent, port, proto, state, process, **kwargs):
        super().__init__(parent, fg_color=C['sf'], border_color=C['br'], border_width=1, corner_radius=6, **kwargs)
        col = C['ok'] if state.lower() == 'listen' else C['am']
        ctk.CTkLabel(self, text=f":{port}", font=(FONT, 11, 'bold'), text_color=C['ac'], width=60).pack(side='left', padx=10, pady=6)
        ctk.CTkLabel(self, text=proto.upper(), font=(FONT, 8), text_color=C['mu'], width=40).pack(side='left', padx=4)
        ctk.CTkLabel(self, text=state.upper(), font=(FONT, 9, 'bold'), text_color=col, width=80).pack(side='left', padx=4)
        ctk.CTkLabel(self, text=process, font=(FONT, 9), text_color=C['tx']).pack(side='left', padx=10, fill='x', expand=True)


# ── Btn ───────────────────────────────────────────────────────────
class Btn(ctk.CTkButton):
    VARIANTS = {
        'default': lambda: dict(fg_color=C['ac'],   text_color='#030f1c',
                                hover_color=C['mu2'], border_width=0),
        'primary': lambda: dict(fg_color=C['ac'],   text_color='#030f1c',
                                hover_color=C['mu2'], border_width=0),
        'success': lambda: dict(fg_color=C['ok'],   text_color='#030f1c',
                                hover_color='#2cc470', border_width=0),
        'warning': lambda: dict(fg_color=C['am'],   text_color='#030f1c',
                                hover_color='#cc9900', border_width=0),
        'ghost':   lambda: dict(fg_color='transparent', text_color=C['ac'],
                                hover_color=C['acg'], border_color=C['ac'],
                                border_width=1),
        'danger':  lambda: dict(fg_color=C['wng'],  text_color=C['wn'],
                                hover_color='#5d0000', border_color=C['wn'],
                                border_width=1),
        'blue':    lambda: dict(fg_color=C['bl'],   text_color='#030f1c',
                                hover_color='#2280cc', border_width=0),
    }

    def __init__(self, parent, text='', variant='default',
                 height=34, corner_radius=6, **kwargs):
        self._variant = variant
        style = self.VARIANTS.get(variant, self.VARIANTS['default'])()
        
        # Extract font from kwargs or use default
        font = kwargs.pop('font', (FONT, 10, 'bold'))
        
        # Build combined configuration
        config = {
            'text': text,
            'height': height,
            'font': font,
            'corner_radius': corner_radius
        }
        config.update(style)
        config.update(kwargs)
        
        super().__init__(parent, **config)

    def configure(self, **kwargs):
        if 'variant' in kwargs:
            self._variant = kwargs.pop('variant')
            style = self.VARIANTS.get(self._variant, self.VARIANTS['default'])()
            kwargs.update(style)
        return super().configure(**kwargs)
