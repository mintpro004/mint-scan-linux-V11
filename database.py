"""
Mint Scan v11.1 — Intelligence Foundation
Shared SQLite database for event correlation, history, and persistence.
Includes forensic encryption (tied to machine-id).
"""
import sqlite3
import os
import time
import json
import base64
import hashlib
from logger import get_logger

log = get_logger('database')

DB_PATH = os.path.expanduser('~/.mint_scan_v8.db')

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# ── Encryption Helper ─────────────────────────────────────────────
_MACHINE_KEY = b""

def _get_machine_id():
    for p in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
        if os.path.exists(p):
            with open(p, 'r') as f:
                return f.read().strip()
    return "fallback-mint-scan-key"

def _init_encryption():
    global _MACHINE_KEY
    mid = _get_machine_id()
    _MACHINE_KEY = hashlib.sha256(mid.encode()).digest()

def _xor_fallback(data, key):
    res = bytearray()
    for i in range(len(data)):
        res.append(data[i] ^ key[i % len(key)])
    return res

def _obfuscate(text):
    """Forensic resistance: AES-256 encryption tied to hardware ID."""
    if not text: return text
    if not _MACHINE_KEY: _init_encryption()
    try:
        # We use a prefix 'a8:' to denote AES-256 (GCM)
        cipher = AES.new(_MACHINE_KEY, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(text.encode())
        # Store as: a8: <nonce(16)> <tag(16)> <ciphertext>
        # Actually GCM nonce is usually 12 bytes, but we use 16 for simplicity if desired, 
        # but MODE_GCM default is 16 in some libs, let's use cipher.nonce.
        combined = cipher.nonce + tag + ciphertext
        return "a8:" + base64.b64encode(combined).decode()
    except Exception as e:
        log.error(f"Encryption error: {e}")
        return text

def _deobfuscate(text):
    """Decrypt AES-256 or fallback to XOR for legacy data."""
    if not text: return text
    if not _MACHINE_KEY: _init_encryption()
    
    if text.startswith("a8:"):
        try:
            raw = base64.b64decode(text[3:])
            nonce = raw[:16] # Default GCM nonce length in pycryptodome is 16 if not specified
            # Wait, let's be careful with nonce length.
            # If I didn't specify, it's 16 bytes.
            tag = raw[16:32]
            ciphertext = raw[32:]
            cipher = AES.new(_MACHINE_KEY, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except Exception as e:
            log.debug(f"AES decryption failed: {e}")
            return text
    
    # Legacy XOR fallback
    try:
        data = base64.b64decode(text)
        res = _xor_fallback(data, _MACHINE_KEY)
        return res.decode()
    except:
        return text

# ── Database Class ────────────────────────────────────────────────
SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source TEXT,
        level TEXT,
        event_type TEXT,
        description TEXT,
        metadata TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS system_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        cpu_pct REAL,
        mem_pct REAL,
        net_rx INTEGER,
        net_tx INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS device_aliases (
        mac TEXT PRIMARY KEY,
        alias TEXT,
        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS terminal_snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        command TEXT,
        category TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS file_baseline (
        path TEXT PRIMARY KEY,
        hash TEXT,
        last_checked DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
]

class Database:
    def __init__(self):
        self.conn = None
        self._init_db()

    def _init_db(self):
        try:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            for stmt in SCHEMA:
                cursor.execute(stmt)
            self.conn.commit()
            log.info(f"Database initialized at {DB_PATH}")
        except Exception as e:
            log.error(f"Database init error: {e}")

    def log_event(self, source, level, event_type, description, metadata=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO security_events (source, level, event_type, description, metadata) VALUES (?, ?, ?, ?, ?)",
                (source, level, event_type, _obfuscate(description), _obfuscate(json.dumps(metadata) if metadata else None))
            )
            self.conn.commit()
        except Exception as e:
            log.error(f"Event logging error: {e}")

    def get_recent_events(self, limit=50):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            res = []
            for r in rows:
                d = dict(r)
                d['description'] = _deobfuscate(d['description'])
                d['metadata']    = _deobfuscate(d['metadata'])
                res.append(d)
            return res
        except Exception as e:
            log.error(f"Error fetching events: {e}")
            return []

    def log_stats(self, cpu, mem, rx, tx):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO system_stats (cpu_pct, mem_pct, net_rx, net_tx) VALUES (?, ?, ?, ?)",
                (cpu, mem, rx, tx)
            )
            self.conn.commit()
        except Exception as e:
            log.error(f"Stats logging error: {e}")

    def get_stats_history(self, limit=24):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM system_stats ORDER BY timestamp DESC LIMIT ?", (limit,))
            return cursor.fetchall()
        except Exception as e:
            log.error(f"Error fetching stats: {e}")
            return []

    def set_alias(self, mac, alias):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO device_aliases (mac, alias) VALUES (?, ?)",
                (mac, _obfuscate(alias))
            )
            self.conn.commit()
        except Exception as e:
            log.error(f"Error setting alias: {e}")

    def get_aliases(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM device_aliases")
            return {row['mac']: _deobfuscate(row['alias']) for row in cursor.fetchall()}
        except Exception as e:
            log.error(f"Error getting aliases: {e}")
            return {}

    def save_snippet(self, name, command, category="General"):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO terminal_snippets (name, command, category) VALUES (?, ?, ?)",
                (name, _obfuscate(command), category)
            )
            self.conn.commit()
        except Exception as e:
            log.error(f"Error saving snippet: {e}")

    def get_snippets(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM terminal_snippets")
            rows = cursor.fetchall()
            return [{'id': r['id'], 'name': r['name'], 'command': _deobfuscate(r['command'])} for r in rows]
        except Exception as e:
            log.error(f"Error getting snippets: {e}")
            return []

    def maintenance(self):
        """Perform database optimization and data pruning."""
        try:
            cursor = self.conn.cursor()
            # 1. Prune old system stats (keep last 7 days)
            cursor.execute("DELETE FROM system_stats WHERE timestamp < datetime('now', '-7 days')")
            # 2. Prune old security events (keep last 30 days)
            cursor.execute("DELETE FROM security_events WHERE timestamp < datetime('now', '-30 days')")
            # 3. Optimise file structure
            cursor.execute("VACUUM")
            self.conn.commit()
            log.info("Database maintenance complete (Vacuum + Pruning)")
            return True, "Database optimised (Vacuum + Pruning complete)"
        except Exception as e:
            log.error(f"Maintenance error: {e}")
            return False, str(e)

    def close(self):
        if self.conn:
            self.conn.close()
            log.info("Database connection closed")

# Global singleton
db = Database()
