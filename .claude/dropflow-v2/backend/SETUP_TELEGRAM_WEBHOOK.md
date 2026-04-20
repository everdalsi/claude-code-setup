# Setup Telegram Webhook pour DropFlow
## Configuration en Temps Réel pour Recevoir les Médias

**Avantages du Webhook vs Polling:**
- ✅ Temps réel (instantané)
- ✅ Moins de latence
- ✅ Moins de charge serveur
- ✅ Scalable pour 1000+ utilisateurs

---

## Installation (5 minutes)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn aiohttp python-telegram-bot watchdog
```

### 2. Configuration des Variables d'Environnement

#### A. Récupérer le Bot Token
```bash
# Envoyez /start à @BotFather sur Telegram
# Réponse: Here is your token: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
# Sauvegardez ce token
```

#### B. Configurer le Webhook URL
Vous avez besoin d'un domaine HTTPS public. Options:

**Option 1: Using ngrok (développement local)**
```bash
# Download ngrok: https://ngrok.com/download
ngrok http 8001
# Output: https://abc123.ngrok.io

# Set env variable:
export TELEGRAM_WEBHOOK_URL="https://abc123.ngrok.io/webhook"
```

**Option 2: Using your domain**
```bash
# Si vous avez un serveur:
export TELEGRAM_WEBHOOK_URL="https://yourdomain.com/webhook"
```

#### C. Set Environment Variables
```bash
# Linux/Mac:
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
export TELEGRAM_WEBHOOK_URL="https://abc123.ngrok.io/webhook"
export WEBHOOK_PORT="8001"

# Windows (PowerShell):
$env:TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
$env:TELEGRAM_WEBHOOK_URL="https://abc123.ngrok.io/webhook"
$env:WEBHOOK_PORT="8001"
```

---

## Lancement

### Méthode A: Webhook seul
```bash
cd ~/.claude/dropflow-v2/backend

# Terminal 1: Start webhook
python3 telegram_webhook.py

# Output:
# [WEBHOOK] Bot token: 123456:ABC-DEF...
# [WEBHOOK] Webhook URL: https://abc123.ngrok.io/webhook
# [OK] Webhook configured: https://abc123.ngrok.io/webhook
# Starting on port 8001...
```

### Méthode B: Webhook + Real-Time Watcher
```bash
cd ~/.claude/dropflow-v2/backend

# Terminal 1: Start webhook
python3 telegram_webhook.py

# Terminal 2: Start media watcher
python3 media_watcher_realtime.py

# Output:
# [REAL-TIME MEDIA WATCHER]
# Watching: /home/user/dropflow-media
# Auto-analyze: True
# [OK] Watcher started - monitoring for new files...
```

### Méthode C: Combined (Recommended)
```bash
# Create startup script
cat > start_realtime_system.sh << 'EOF'
#!/bin/bash

# Start webhook in background
python3 telegram_webhook.py &
WEBHOOK_PID=$!

# Start media watcher in background
python3 media_watcher_realtime.py &
WATCHER_PID=$!

# Start FastAPI server in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

echo "All services started:"
echo "  Webhook: $WEBHOOK_PID"
echo "  Watcher: $WATCHER_PID"
echo "  Server: $SERVER_PID"

# Kill all on Ctrl+C
trap "kill $WEBHOOK_PID $WATCHER_PID $SERVER_PID" EXIT

wait
EOF

chmod +x start_realtime_system.sh
./start_realtime_system.sh
```

---

## Flux de Données

```
Telegram User
     |
     | [Send photo/video/TikTok link]
     v
Telegram Servers
     |
     | [Webhook POST to your server]
     v
Webhook Receiver (telegram_webhook.py)
     |
     | [Download file / Save link]
     v
~/dropflow-media/
     |
     | [File system event]
     v
Real-Time Watcher (media_watcher_realtime.py)
     |
     | [Detect new media]
     v
self_improvement_analyzer.py
     |
     | [Analyze and extract improvements]
     v
ANALYSIS_*.json + SELF_IMPROVEMENT_*.json
     |
     | [Claude Core ingests]
     v
System Improvements Applied
```

---

## Vérification

### 1. Test Health Endpoint
```bash
curl http://localhost:8001/health

# Response:
{
  "status": "healthy",
  "webhook_url": "https://abc123.ngrok.io/webhook",
  "media_dir": "/home/user/dropflow-media",
  "timestamp": "2026-04-12T11:15:30.123456"
}
```

### 2. Check Stats
```bash
curl http://localhost:8001/stats

# Response:
{
  "total_media": 0,
  "media_files": [],
  "media_dir": "/home/user/dropflow-media"
}
```

### 3. Test with Telegram
- Send a photo to your bot
- Check if file appears in `~/dropflow-media/`
- Watcher should detect and start analysis automatically

### 4. Monitor Logs
```bash
# Terminal 3: Watch logs
tail -f logs/dropflow.log

# Should show:
# [WEBHOOK] Received update: 123456
# [PHOTO] Downloading file_id: xyz...
# [DOWNLOAD] Saved: photo_1681234567.jpg
# [DETECTED] New media: photo_1681234567.jpg
# [ANALYZE] Starting analysis...
```

---

## Formats Supportés

### Photos
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- WebP (`.webp`)

### Vidéos
- MP4 (`.mp4`)
- MOV (`.mov`)
- WebM (`.webm`)

### Liens
- TikTok (`.com/video/xxx` ou `vm.tiktok.com/xxx`)

---

## Configuration Avancée

### Custom Analysis
Modifiez `media_watcher_realtime.py`:
```python
async def _analyze_media(self, filepath):
    # Customize analysis here
    result = await custom_analyzer(filepath)
    return result
```

### Database Integration
```python
# Save to PostgreSQL instead of JSON
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:password@localhost/dropflow')
```

### Notifications
```python
# Send analysis results back to Telegram
await send_telegram_message(chat_id, analysis_result)
```

---

## Troubleshooting

### Webhook not receiving updates
```bash
# Check webhook status
curl -X POST https://api.telegram.org/bot{TOKEN}/getWebhookInfo

# Reset webhook
curl -X POST https://api.telegram.org/bot{TOKEN}/deleteWebhook
python3 telegram_webhook.py
```

### Files not analyzing
```bash
# Check watcher logs
tail -f logs/*.log

# Manual analysis
python3 self_improvement_analyzer.py ~/dropflow-media/photo_xyz.jpg
```

### Port already in use
```bash
# Find process on port 8001
lsof -i :8001

# Kill process
kill -9 <PID>

# Or use different port
export WEBHOOK_PORT=8002
```

---

## Performance Notes

| Setting | Polling | Webhook |
|---------|---------|---------|
| Latency | 5-30s | <1s |
| API Calls | ~10/min | 0 (push) |
| Scalability | ~100 users | 10,000+ users |
| Cost | Medium | Low |

---

## Security

### 1. Verify Webhook Signature (Optional)
```python
from hashlib import sha256
import hmac

def verify_telegram_signature(body, signature, token):
    calculated = hmac.new(
        token.encode(),
        body,
        sha256
    ).hexdigest()
    return calculated == signature
```

### 2. Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook")
@limiter.limit("100/minute")
async def webhook(request: Request):
    pass
```

### 3. HTTPS Only
Webhook URL must be HTTPS (Telegram requirement)

---

## Next Steps

1. **Configure webhook** with your bot token and domain
2. **Start webhook server** and media watcher
3. **Test** by sending media to your Telegram bot
4. **Monitor** analysis results in real-time
5. **Iterate** - improvements are applied automatically

---

## Support

- Telegram Bot API: https://core.telegram.org/bots/api
- ngrok: https://ngrok.com/
- FastAPI: https://fastapi.tiangolo.com/
- Watchdog: https://watchdog.readthedocs.io/

---

**Ready to receive real-time media from Telegram!** 🚀
