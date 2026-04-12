#!/bin/bash
# Check daemon status

echo ""
echo "=========================================="
echo "DROPFLOW AUTO-IMPROVEMENT SYSTEM STATUS"
echo "=========================================="
echo ""

echo "DAEMONS RUNNING:"
ps aux | grep -E "media_watcher_daemon|implementation_daemon" | grep -v grep | awk '{print "  PID " $2 ": " $NF}'

echo ""
echo "MEDIA DIRECTORY:"
MEDIA_COUNT=$(ls ~/dropflow-media/*.jpg ~/dropflow-media/*.mp4 2>/dev/null | wc -l)
echo "  Files received: $MEDIA_COUNT"

echo ""
echo "REPORTS GENERATED:"
REPORTS=$(ls ~/dropflow-media/ANALYSIS_REPORT_*.json 2>/dev/null | wc -l)
IMPL=$(ls ~/dropflow-media/implementation_report_*.json 2>/dev/null | wc -l)
echo "  Analysis reports: $REPORTS"
echo "  Implementation reports: $IMPL"

echo ""
echo "COMMITS MADE:"
cd /c/Users/everd/.claude/dropflow-v2/backend
git log --oneline | head -5 | sed 's/^/  /'

echo ""
echo "=========================================="
echo "SYSTEM READY - SEND IMAGES TO TELEGRAM"
echo "=========================================="
echo ""
