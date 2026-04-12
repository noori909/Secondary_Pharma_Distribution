"""
Background scheduler — fires perform_automated_backup() every day at 22:00 (10 PM).
Runs as a daemon thread so it never blocks app startup or shutdown.
"""
import threading
import time
from datetime import datetime, timedelta


def _seconds_until(hour: int, minute: int = 0) -> float:
    """Return seconds remaining until the next occurrence of HH:MM today (or tomorrow)."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def _scheduler_loop():
    while True:
        wait = _seconds_until(22, 0)   # 10:00 PM
        print(f"[Scheduler] Next backup+report in {wait/3600:.1f} h (at 22:00)")
        time.sleep(wait)

        try:
            from logic.backup_logic import perform_automated_backup
            perform_automated_backup()
        except Exception as e:
            print(f"[Scheduler] Scheduled backup failed: {e}")

        # Sleep 70 s so we don't double-fire within the same minute
        time.sleep(70)


def start_scheduler():
    """Launch the background scheduler daemon thread. Call once from main_app.py."""
    t = threading.Thread(target=_scheduler_loop, name="DailyScheduler", daemon=True)
    t.start()
    print("[Scheduler] Daily 10 PM backup+report scheduler started.")
