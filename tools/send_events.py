#!/usr/bin/env python3
"""Send a batch of synthetic events to the ingestion endpoint.
Usage: python tools/send_events.py
"""
import asyncio
import aiohttp
import time
from datetime import datetime, timezone

ENDPOINT = "http://localhost:8004/events"
TOTAL = 300
USERS = 30
EVENT_NAMES = ["page_view", "home_button", "form_click"]
CONCURRENCY = 50


async def send_one(session, eid):
    user = f"user_{eid % USERS}"
    event = {
        "user_id": user,
        "event_name": EVENT_NAMES[eid % len(EVENT_NAMES)],
        "metadata": {"page": f"/page_{eid % 10}", "session_id": f"session_{eid % 50}"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    start = time.time()
    try:
        async with session.post(
            ENDPOINT, json=event, timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            ok = resp.status in (200, 202)
            text = await resp.text()
            return {
                "success": ok,
                "status": resp.status,
                "time": time.time() - start,
                "body": text[:200],
            }
    except Exception as e:
        return {
            "success": False,
            "status": None,
            "time": time.time() - start,
            "error": str(e),
        }


async def run():
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(TOTAL):

            async def wrapper(i=i):
                async with sem:
                    return await send_one(session, i)

            tasks.append(asyncio.create_task(wrapper()))
        results = await asyncio.gather(*tasks)
    succ = sum(1 for r in results if r.get("success"))
    fail = len(results) - succ
    avg = sum(r.get("time", 0) for r in results) / len(results)
    print(
        f"Sent {len(results)} events: {succ} succeeded, {fail} failed, avg time {avg*1000:.1f}ms"
    )
    if fail:
        print("Sample failures:")
        for r in results[:10]:
            if not r.get("success"):
                print(r)


if __name__ == "__main__":
    asyncio.run(run())