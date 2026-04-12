#!/bin/bash

# Start Real-Time DropFlow System
# Launches: Webhook + Media Watcher + FastAPI Server

set -e

echo "[STARTUP] Starting DropFlow Real-Time System..."
echo ""

# Check environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "[ERROR] TELEGRAM_BOT_TOKEN not set"
    echo ""
    echo "Setup:"
    echo '  export TELEGRAM_BOT_TOKEN="your-bot-token"'
    echo '  export TELEGRAM_WEBHOOK_URL="https://your-domain.com/webhook"'
    echo ""
    exit 1
fi

if [ -z "$TELEGRAM_WEBHOOK_URL" ]; then
    echo "[ERROR] TELEGRAM_WEBHOOK_URL not set"
    exit 1
fi

# Create logs directory
mkdir -p logs

echo "[CONFIG]"
echo "  Bot Token: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "  Webhook URL: $TELEGRAM_WEBHOOK_URL"
echo "  Port (Webhook): ${WEBHOOK_PORT:-8001}"
echo "  Port (FastAPI): ${API_PORT:-8000}"
echo ""

# Start services
echo "[SERVICES] Starting..."
echo ""

# Terminal multiplexing options
if command -v tmux &> /dev/null; then
    echo "[TMUX] Using tmux for process management"

    # Create tmux session
    tmux new-session -d -s dropflow -x 200 -y 50

    # Pane 0: Telegram Webhook
    tmux send-keys -t dropflow "python3 telegram_webhook.py 2>&1 | tee logs/webhook.log" Enter
    sleep 1

    # Pane 1: Media Watcher
    tmux split-window -h -t dropflow
    tmux send-keys -t dropflow "python3 media_watcher_realtime.py 2>&1 | tee logs/watcher.log" Enter
    sleep 1

    # Pane 2: FastAPI Server
    tmux split-window -v -t dropflow
    tmux send-keys -t dropflow "uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload 2>&1 | tee logs/server.log" Enter
    sleep 1

    echo "[OK] All services started in tmux session 'dropflow'"
    echo ""
    echo "Commands:"
    echo "  tmux attach -t dropflow      # Attach to session"
    echo "  tmux kill-session -t dropflow # Stop all services"
    echo ""

    # Attach to session
    tmux attach -t dropflow

elif command -v screen &> /dev/null; then
    echo "[SCREEN] Using screen for process management"

    # Create screen session
    screen -dmS dropflow

    # Webhook
    screen -S dropflow -X stuff "python3 telegram_webhook.py 2>&1 | tee logs/webhook.log\n"
    sleep 1

    # New window for watcher
    screen -S dropflow -X screen -t watcher
    screen -S dropflow -X stuff "python3 media_watcher_realtime.py 2>&1 | tee logs/watcher.log\n"
    sleep 1

    # New window for server
    screen -S dropflow -X screen -t server
    screen -S dropflow -X stuff "uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload 2>&1 | tee logs/server.log\n"
    sleep 1

    echo "[OK] All services started in screen session 'dropflow'"
    echo ""
    echo "Commands:"
    echo "  screen -r dropflow          # Attach to session"
    echo "  screen -S dropflow -X quit  # Stop all services"
    echo ""

    # Attach to session
    screen -r dropflow

else
    echo "[BACKGROUND] Starting services in background..."

    # Start webhook
    echo "[WEBHOOK] Starting on port ${WEBHOOK_PORT:-8001}..."
    python3 telegram_webhook.py > logs/webhook.log 2>&1 &
    WEBHOOK_PID=$!
    sleep 2

    # Start watcher
    echo "[WATCHER] Starting media watcher..."
    python3 media_watcher_realtime.py > logs/watcher.log 2>&1 &
    WATCHER_PID=$!
    sleep 1

    # Start FastAPI server
    echo "[SERVER] Starting FastAPI on port ${API_PORT:-8000}..."
    uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload > logs/server.log 2>&1 &
    SERVER_PID=$!
    sleep 1

    echo ""
    echo "[OK] All services started:"
    echo "  Webhook: PID $WEBHOOK_PID"
    echo "  Watcher: PID $WATCHER_PID"
    echo "  Server: PID $SERVER_PID"
    echo ""
    echo "[LOGS]"
    echo "  tail -f logs/webhook.log"
    echo "  tail -f logs/watcher.log"
    echo "  tail -f logs/server.log"
    echo ""
    echo "[STOP] Press Ctrl+C to stop all services"
    echo ""

    # Trap Ctrl+C to kill all processes
    trap "echo ''; echo '[STOPPING] Shutting down...'; kill $WEBHOOK_PID $WATCHER_PID $SERVER_PID 2>/dev/null; wait; echo '[OK] All services stopped'" INT TERM

    # Wait for all processes
    wait
fi
