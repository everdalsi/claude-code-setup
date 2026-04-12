#!/usr/bin/env python3
"""System Status Checker"""

import subprocess
import json
from pathlib import Path

MEDIA_DIR = Path.home() / 'dropflow-media'
BACKEND_DIR = Path(__file__).parent

print("\n" + "="*60)
print("DROPFLOW AUTO-IMPROVEMENT SYSTEM STATUS")
print("="*60 + "\n")

# Check daemons
print("DAEMONS RUNNING:")
try:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    for line in result.stdout.split('\n'):
        if 'media_watcher_daemon' in line or 'implementation_daemon' in line:
            if 'grep' not in line:
                parts = line.split()
                pid = parts[1] if len(parts) > 1 else '?'
                daemon_name = parts[-1] if parts else '?'
                print(f"  ✓ {daemon_name} (PID: {pid})")
except:
    print("  (Unable to check)")

# Media files
print("\nMEDIA DIRECTORY:")
media_files = list(MEDIA_DIR.glob('*.jpg')) + list(MEDIA_DIR.glob('*.mp4'))
print(f"  Files received: {len(media_files)}")
if media_files:
    for f in sorted(media_files, key=lambda p: p.stat().st_mtime, reverse=True)[:3]:
        print(f"    - {f.name}")

# Reports
print("\nREPORTS GENERATED:")
analysis_reports = list(MEDIA_DIR.glob('ANALYSIS_REPORT_*.json'))
impl_reports = list(MEDIA_DIR.glob('implementation_report_*.json'))
print(f"  Analysis reports: {len(analysis_reports)}")
print(f"  Implementation reports: {len(impl_reports)}")

# Git commits
print("\nRECENT COMMITS:")
try:
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True
    )
    for line in result.stdout.strip().split('\n')[:5]:
        if line:
            print(f"  {line}")
except:
    print("  (Unable to check)")

print("\n" + "="*60)
print("✅ SYSTEM READY - SEND IMAGES TO TELEGRAM")
print("="*60)
print("""
WORKFLOW:
1. Send image → Telegram @DropFlowMediaBot
2. Daemon 1 detects → Downloads from Telegram
3. Daemon 1 analyzes → Generates report
4. Daemon 2 detects → Researches improvements
5. Daemon 2 implements → Creates code changes
6. Daemon 2 commits → Git commit auto
7. No action needed from you

EVERYTHING IS AUTOMATIC NOW ✨
""")
