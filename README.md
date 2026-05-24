# Mint Scan v11.1 — Ultra Professional Linux Security Auditor
**Mint Projects PTY (Ltd) · Pretoria, South Africa · 2026**

Mint Scan v11.1 is the definitive security and system utility suite for Linux. Engineered for high-stakes auditing, it features a **forensically-resistant architecture**, real-time threat detection, and a unified interface for 30+ security modules.

## 🚀 NEW IN v11.1 (Ultra Professional)
- **Dependency Installer:** One-click automated setup for all system requirements.
- **Database Maintenance:** Automated pruning and VACUUM for long-term performance.
- **Help & Troubleshooting:** Comprehensive in-app guide for Chromebooks, WSL2, and Sudo issues.
- **Terminal Optimization:** High-performance buffered output for heavy system updates.
- **Wireless Sync Pro:** Enhanced support for Chromebooks with manual IP override and NAT bypass.
- **Security Hardening:** AES-256 hardware-tied encryption for all local event data.

## 📖 Comprehensive Guide
For a full walkthrough of features and advanced setup, see: **[GUIDE.md](./GUIDE.md)**

```bash
git clone https://github.com/mintpro004/mint-scan-linux-V11.git ~/mint-scan-linux
cd ~/mint-scan-linux
bash install.sh
bash run.sh          # Never: sudo bash run.sh
```

## Update & Maintenance

```bash
cd ~/mint-scan-linux
bash update.sh       # git pull + re-install deps
```
*Note: Maintenance can now be performed directly within the app under Settings -> Maintenance.*

## 32 Security Screens + 17 Pro Features

| Tab | Screen | Description |
|-----|--------|-------------|
| **Support** | **Help** | **NEW:** Comprehensive troubleshooting and networking guide |
| Dashboard | Dashboard | Live score ring, CPU/RAM charts, threat status |
| Permissions | Permissions | SUID/SGID audit, world-writable paths |
| Wi-Fi | Wi-Fi | Network scan, rogue AP detection |
| Network | Network | Analog speedometer gauges, ping graph, clipboard traffic log |
| Security | Hardening | **ClamAV + rkhunter** malware scanning |
| Settings | Settings | **NEW:** Dependency Installer & DB Maintenance |
| Wireless | Wireless | **ENHANCED:** Wi-Fi server, phone sync (Chromebook Fixed) |
| Terminal | Terminal | **ENHANCED:** Buffered high-speed pro terminal |
| VPN | VPN | WireGuard + OpenVPN (auto-detect configs) |
| IDS/IPS | IDS/IPS | Suricata + Snort integration |
| Web Monitor | Web Monitor | Remote browser dashboard (port 7777) |
| Secure Erase | Secure Erase | DoD 3-pass shredding |

## Mobile Sync

Mint Scan v11.1 supports bi-directional sync with the Mint Scan Android Companion App.
- **Wireless:** Sync calls, SMS, contacts, and battery state over local Wi-Fi.
- **USB:** High-speed ADB-based data extraction and APK management.

## Requirements

- **Python:** 3.9+
- **OS:** Chromebook (Crostini), Ubuntu 20.04+, Debian 11+, Kali Linux, WSL2, Raspberry Pi OS (64-bit)

---
© 2026 Mint Projects PTY (Ltd) · Pretoria, South Africa
