#!/usr/bin/env python3
"""Simple wait-for-services script used in docker-compose for local development.

Usage: python wait_for_services.py --services host1:port host2:port --timeout 120
"""
import argparse
import socket
import time
import sys


def wait_for_host(host: str, port: int, timeout: float) -> bool:
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=3):
                return True
        except Exception:
            if time.time() - start >= timeout:
                return False
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--services", nargs="+", required=True, help="services as host:port")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    services = []
    for s in args.services:
        host, port = s.split(":")
        services.append((host, int(port)))

    for host, port in services:
        print(f"Waiting for {host}:{port} (timeout={args.timeout}s)")
        ok = wait_for_host(host, port, args.timeout)
        if not ok:
            print(f"Timed out waiting for {host}:{port}")
            sys.exit(2)
        print(f"{host}:{port} is available")

    print("All services are available")


if __name__ == "__main__":
    main()
