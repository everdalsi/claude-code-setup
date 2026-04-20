#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Webhook Receiver
Receives media directly from Telegram and saves to dropflow-media/
Replaces polling with webhooks for real-time delivery
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import aiohttp
import asyncio

try:
    from fastapi import FastAPI, Request, BackgroundTasks
    from uvicorn import run as uvicorn_run
except ImportError:
    print("Install: pip install fastapi uvicorn aiohttp python-telegram-bot")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramWebhookReceiver:
    """
    Receive Telegram updates via webhook instead of polling
    Faster, real-time delivery of media files
    """

    def __init__(
        self,
        bot_token: str,
        webhook_url: str,
        media_dir: str = None,
        port: int = 8001
    ):
        self.bot_token = bot_token
        self.webhook_url = webhook_url
        self.media_dir = Path(media_dir or os.path.expanduser("~/dropflow-media"))
        self.port = port
        self.app = FastAPI(title="Telegram Webhook")
        self.setup_routes()

        logger.info(f"[WEBHOOK] Bot token: {bot_token[:20]}...")
        logger.info(f"[WEBHOOK] Webhook URL: {webhook_url}")
        logger.info(f"[WEBHOOK] Media dir: {self.media_dir}")

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.post("/webhook")
        async def webhook(request: Request, tasks: BackgroundTasks):
            """Receive Telegram updates"""
            try:
                update = await request.json()
                logger.info(f"[WEBHOOK] Received update: {update.get('update_id')}")

                # Process in background
                tasks.add_task(self.process_update, update)

                return {"ok": True}

            except Exception as e:
                logger.error(f"[WEBHOOK ERROR] {e}")
                return {"ok": False, "error": str(e)}

        @self.app.get("/health")
        async def health():
            """Health check"""
            return {
                "status": "healthy",
                "webhook_url": self.webhook_url,
                "media_dir": str(self.media_dir),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/stats")
        async def stats():
            """Get webhook statistics"""
            media_files = list(self.media_dir.glob("*")) if self.media_dir.exists() else []
            return {
                "total_media": len(media_files),
                "media_files": [f.name for f in media_files],
                "media_dir": str(self.media_dir)
            }

    async def process_update(self, update: dict):
        """Process Telegram update"""
        try:
            # Check for message
            message = update.get("message", {})
            if not message:
                return

            # Get chat ID and message ID
            chat_id = message.get("chat", {}).get("id")
            message_id = message.get("message_id")

            logger.info(f"[MESSAGE] Chat: {chat_id}, Message: {message_id}")

            # Process photo
            if "photo" in message:
                await self._handle_photo(chat_id, message)

            # Process video
            elif "video" in message:
                await self._handle_video(chat_id, message)

            # Process text (TikTok link)
            elif "text" in message:
                text = message.get("text", "")
                if "tiktok.com" in text or "vm.tiktok.com" in text:
                    await self._handle_tiktok_link(chat_id, message, text)

        except Exception as e:
            logger.error(f"[PROCESS ERROR] {e}")

    async def _handle_photo(self, chat_id: int, message: dict):
        """Download and save photo"""
        try:
            photo = message["photo"][-1]  # Get highest resolution
            file_id = photo["file_id"]

            logger.info(f"[PHOTO] Downloading file_id: {file_id}")

            # Get file info
            file_info = await self._get_file_info(file_id)
            file_path = file_info.get("file_path")

            if file_path:
                # Download file
                filename = f"photo_{datetime.now().timestamp():.0f}.jpg"
                await self._download_file(file_path, filename)
                logger.info(f"[PHOTO] Saved: {filename}")

        except Exception as e:
            logger.error(f"[PHOTO ERROR] {e}")

    async def _handle_video(self, chat_id: int, message: dict):
        """Download and save video"""
        try:
            video = message["video"]
            file_id = video["file_id"]

            logger.info(f"[VIDEO] Downloading file_id: {file_id}")

            # Get file info
            file_info = await self._get_file_info(file_id)
            file_path = file_info.get("file_path")

            if file_path:
                # Download file
                filename = f"video_{datetime.now().timestamp():.0f}.mp4"
                await self._download_file(file_path, filename)
                logger.info(f"[VIDEO] Saved: {filename}")

        except Exception as e:
            logger.error(f"[VIDEO ERROR] {e}")

    async def _handle_tiktok_link(self, chat_id: int, message: dict, url: str):
        """Save TikTok link for analysis"""
        try:
            logger.info(f"[TIKTOK] Link: {url}")

            # Save link to file
            filename = f"tiktok_link_{datetime.now().timestamp():.0f}.txt"
            filepath = self.media_dir / filename

            filepath.write_text(f"{url}\n{message.get('caption', '')}")
            logger.info(f"[TIKTOK] Saved: {filename}")

            # Optional: Download video from TikTok
            # video_file = await self._download_tiktok_video(url)

        except Exception as e:
            logger.error(f"[TIKTOK ERROR] {e}")

    async def _get_file_info(self, file_id: str) -> dict:
        """Get file info from Telegram"""
        url = f"https://api.telegram.org/bot{self.bot_token}/getFile"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"file_id": file_id}) as resp:
                data = await resp.json()
                return data.get("result", {})

    async def _download_file(self, file_path: str, filename: str):
        """Download file from Telegram"""
        self.media_dir.mkdir(exist_ok=True, parents=True)

        url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
        filepath = self.media_dir / filename

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(filepath, 'wb') as f:
                    f.write(await resp.read())

        logger.info(f"[DOWNLOAD] Saved: {filepath} ({filepath.stat().st_size / 1024:.1f}KB)")

    def start(self):
        """Start webhook server"""
        logger.info("="*70)
        logger.info("[TELEGRAM WEBHOOK SERVER]")
        logger.info("="*70)
        logger.info(f"Starting on port {self.port}...")
        logger.info("")

        uvicorn_run(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )


async def setup_webhook(bot_token: str, webhook_url: str):
    """Configure webhook on Telegram server"""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"url": webhook_url}) as resp:
            result = await resp.json()
            if result.get("ok"):
                logger.info(f"[OK] Webhook configured: {webhook_url}")
            else:
                logger.error(f"[ERROR] Failed to set webhook: {result}")


def main():
    """Start webhook receiver"""
    # Get config from environment
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    port = int(os.getenv("WEBHOOK_PORT", "8001"))

    if not bot_token or not webhook_url:
        logger.error("Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_URL environment variables")
        logger.info("")
        logger.info("Example:")
        logger.info('  export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"')
        logger.info('  export TELEGRAM_WEBHOOK_URL="https://yourdomain.com/webhook"')
        return

    # Create and start receiver
    receiver = TelegramWebhookReceiver(
        bot_token=bot_token,
        webhook_url=webhook_url,
        port=port
    )

    # Setup webhook on Telegram
    asyncio.run(setup_webhook(bot_token, webhook_url))

    # Start server
    receiver.start()


if __name__ == "__main__":
    main()
