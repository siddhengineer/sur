#!/usr/bin/env python3
r"""
cleanup_alerts.py

Small maintenance script to remove alert clip files older than N days and optionally
to enforce a maximum total size for the alerts directory by deleting oldest files first.

Usage examples:
  # Dry-run: show what would be deleted for files older than 7 days
  python scripts/cleanup_alerts.py --days 7 --dry-run

  # Delete files older than 30 days
  python scripts/cleanup_alerts.py --days 30

  # Ensure alerts dir uses <= 10 GB by deleting oldest files
  python scripts/cleanup_alerts.py --max-total-gb 10

This script is intentionally independent so it can be scheduled (Task Scheduler, cron)
or run manually. It operates on files with common video extensions (.mp4, .avi, .mov).
"""

from pathlib import Path
import argparse
import time
import sys
import logging

VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv'}


def get_files_sorted_by_mtime(directory: Path):
    files = [p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    files.sort(key=lambda p: p.stat().st_mtime)
    return files


def bytes_to_gb(b: int) -> float:
    return b / (1024 ** 3)


def dir_size_bytes(directory: Path) -> int:
    total = 0
    for p in directory.rglob('*'):
        if p.is_file():
            try:
                total += p.stat().st_size
            except Exception:
                pass
    return total


def cleanup_by_age(directory: Path, max_age_days: int, dry_run: bool = True) -> int:
    now = time.time()
    cutoff = now - (max_age_days * 24 * 3600)
    files = get_files_sorted_by_mtime(directory)
    removed = 0
    for p in files:
        try:
            mtime = p.stat().st_mtime
        except Exception:
            continue
        if mtime < cutoff:
            if dry_run:
                logging.info(f"Would delete (age) {p} last-modified: {time.ctime(mtime)}")
            else:
                try:
                    p.unlink()
                    removed += 1
                    logging.info(f"Deleted {p}")
                except Exception as e:
                    logging.error(f"Failed to delete {p}: {e}")
    return removed


def cleanup_by_size(directory: Path, max_total_gb: float, dry_run: bool = True) -> int:
    max_bytes = int(max_total_gb * (1024 ** 3))
    current = dir_size_bytes(directory)
    if current <= max_bytes:
        logging.info(f"Directory size OK: {bytes_to_gb(current):.2f} GB <= {max_total_gb:.2f} GB")
        return 0
    files = get_files_sorted_by_mtime(directory)
    removed = 0
    for p in files:
        if current <= max_bytes:
            break
        try:
            size = p.stat().st_size
        except Exception:
            continue
        if dry_run:
            logging.info(f"Would delete (size) {p} size: {bytes_to_gb(size):.3f} GB")
            current -= size
            removed += 1
        else:
            try:
                p.unlink()
                current -= size
                removed += 1
                logging.info(f"Deleted {p}, freed {bytes_to_gb(size):.3f} GB")
            except Exception as e:
                logging.error(f"Failed to delete {p}: {e}")
    logging.info(f"Post-cleanup size: {bytes_to_gb(current):.2f} GB")
    return removed


def main(argv=None):
    parser = argparse.ArgumentParser(description="Cleanup alert clips by age and/or total size")
    parser.add_argument('--dir', '-d', default='alerts', help='Alerts directory (default: alerts)')
    parser.add_argument('--days', type=int, default=None, help='Delete files older than DAYS')
    parser.add_argument('--max-total-gb', type=float, default=None, help='Enforce max total size (GB)')
    parser.add_argument('--dry-run', action='store_true', help='Do not actually delete files (default: false)')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    alerts_dir = Path(args.dir)
    if not alerts_dir.exists() or not alerts_dir.is_dir():
        logging.error(f"Alerts directory does not exist: {alerts_dir}")
        return 2

    total_before = dir_size_bytes(alerts_dir)
    logging.info(f"Alerts dir: {alerts_dir} size: {bytes_to_gb(total_before):.2f} GB")

    total_removed = 0
    if args.days is not None:
        logging.info(f"Cleaning files older than {args.days} days (dry_run={args.dry_run})")
        total_removed += cleanup_by_age(alerts_dir, args.days, dry_run=args.dry_run)

    if args.max_total_gb is not None:
        logging.info(f"Pruning by total size to <= {args.max_total_gb} GB (dry_run={args.dry_run})")
        total_removed += cleanup_by_size(alerts_dir, args.max_total_gb, dry_run=args.dry_run)

    total_after = dir_size_bytes(alerts_dir)
    logging.info(f"Cleanup finished. Removed approx {total_removed} files. Size before: {bytes_to_gb(total_before):.2f} GB, after: {bytes_to_gb(total_after):.2f} GB")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
