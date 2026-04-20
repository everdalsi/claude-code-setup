#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Media Watcher
Monitors ~/dropflow-media/ for new files and triggers analysis automatically
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import asyncio
import json

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("Install watchdog: pip install watchdog")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class MediaFileHandler(FileSystemEventHandler):
    """Handle media file events (create, modify)"""

    def __init__(self, callback=None):
        self.callback = callback
        self.processed = set()

    def on_created(self, event):
        """Trigger when new file created"""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process media files
        if filepath.suffix.lower() in ['.jpg', '.png', '.mp4', '.mov', '.webm']:
            logger.info(f"[NEW MEDIA] {filepath.name}")
            self.process_file(filepath)

    def on_modified(self, event):
        """Trigger when file modified (upload complete)"""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Only process media files
        if filepath.suffix.lower() in ['.jpg', '.png', '.mp4', '.mov', '.webm']:
            # Wait for file to stabilize (not being written)
            if filepath.stat().st_size > 0 and filepath not in self.processed:
                logger.info(f"[UPLOAD COMPLETE] {filepath.name} ({filepath.stat().st_size / 1024:.1f}KB)")
                self.process_file(filepath)

    def process_file(self, filepath):
        """Process file and trigger analysis"""
        self.processed.add(filepath)

        logger.info(f"[PROCESSING] {filepath.name}")

        # Trigger callback if provided
        if self.callback:
            try:
                self.callback(filepath)
            except Exception as e:
                logger.error(f"Error processing {filepath.name}: {e}")


class RealTimeMediaWatcher:
    """
    Real-time media file watcher with analysis trigger
    """

    def __init__(self, media_dir: str = None, auto_analyze: bool = True):
        self.media_dir = Path(media_dir or os.path.expanduser("~/dropflow-media"))
        self.auto_analyze = auto_analyze
        self.observer = None
        self.handler = None

    def start(self):
        """Start watching directory"""
        self.media_dir.mkdir(exist_ok=True, parents=True)

        logger.info("="*70)
        logger.info("[REAL-TIME MEDIA WATCHER]")
        logger.info("="*70)
        logger.info(f"Watching: {self.media_dir}")
        logger.info(f"Auto-analyze: {self.auto_analyze}")
        logger.info(f"Start time: {datetime.now().isoformat()}")
        logger.info("")

        # Create handler
        self.handler = MediaFileHandler(callback=self._on_media_detected)

        # Start observer
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.media_dir), recursive=False)
        self.observer.start()

        logger.info("[OK] Watcher started - monitoring for new files...")
        logger.info("")

    def stop(self):
        """Stop watching directory"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("[OK] Watcher stopped")

    def _on_media_detected(self, filepath):
        """Callback when new media detected"""
        logger.info(f"[DETECTED] New media: {filepath.name}")

        if self.auto_analyze:
            asyncio.run(self._analyze_media(filepath))

    async def _analyze_media(self, filepath):
        """Analyze media file"""
        logger.info(f"[ANALYZE] Starting analysis of {filepath.name}")

        try:
            # Import analyzer
            sys.path.insert(0, str(Path(__file__).parent))
            from self_improvement_analyzer import analyze_media_file

            # Run analysis
            result = await analyze_media_file(str(filepath))

            logger.info(f"[SUCCESS] Analysis complete for {filepath.name}")
            logger.info(f"[RESULT] {json.dumps(result, indent=2)[:500]}...")

            return result

        except Exception as e:
            logger.error(f"[ERROR] Analysis failed: {e}")
            import traceback
            traceback.print_exc()

    def get_pending_media(self):
        """Get list of media files not yet analyzed"""
        pending = []

        if not self.media_dir.exists():
            return pending

        for media_file in self.media_dir.glob("*"):
            if media_file.is_file() and media_file.suffix.lower() in ['.jpg', '.png', '.mp4', '.mov', '.webm']:
                # Check if analysis exists
                analysis_file = self.media_dir / f"ANALYSIS_{media_file.stem}.json"
                if not analysis_file.exists():
                    pending.append(media_file)

        return pending

    def get_stats(self):
        """Get watcher statistics"""
        pending = self.get_pending_media()

        return {
            "media_dir": str(self.media_dir),
            "is_watching": self.observer is not None and self.observer.is_alive() if self.observer else False,
            "auto_analyze": self.auto_analyze,
            "pending_media": len(pending),
            "pending_files": [f.name for f in pending],
            "start_time": datetime.now().isoformat()
        }


async def main():
    """Demo and continuous monitoring"""
    watcher = RealTimeMediaWatcher(auto_analyze=True)

    try:
        # Start watching
        watcher.start()

        # Keep running
        print("\n[MONITORING] Press Ctrl+C to stop\n")

        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down...\n")
        watcher.stop()
        logger.info("[OK] Monitoring stopped")


if __name__ == "__main__":
    # Run watcher
    asyncio.run(main())
