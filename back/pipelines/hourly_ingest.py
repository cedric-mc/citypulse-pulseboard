from __future__ import annotations

import argparse
import asyncio
import time

from pipelines.collect_public_data import run, DEFAULT_CITIES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alimentation horaire CityPulse")
    parser.add_argument("--cities", nargs="*", default=DEFAULT_CITIES)
    parser.add_argument("--interval-seconds", type=int, default=3600)
    parser.add_argument("--once", action="store_true", help="Execute un seul cycle")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    while True:
        print("[PIPELINE] Debut cycle de collecte")
        results = asyncio.run(run(args.cities))
        print(f"[PIPELINE] Fin cycle ({len(results)} villes)")

        if args.once:
            break

        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
