#!/usr/bin/env python3
"""
Load testing script for event processing platform
Tests 200-300 events per second bursts
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone
import statistics

async def send_event(session, event_id, semaphore):
    """Send a single event with semaphore control"""
    async with semaphore:
        event_data = {
            "user_id": f"user_{event_id % 1000}",  # 1000 different users
            "event_name": ["page_view", "click", "scroll", "form_submit"][event_id % 4],
            "metadata": {"page": f"/page_{event_id % 10}", "session_id": f"session_{event_id % 50}"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        start_time = time.time()
        try:
            async with session.post(
                "http://localhost:8004/events",
                json=event_data,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                end_time = time.time()
                return {
                    "success": response.status in (200, 202),
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "event_id": event_id
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(type(e).__name__) + ": " + str(e),
                "response_time": end_time - start_time,
                "event_id": event_id
            }

async def run_load_test(target_rps=250, duration_seconds=30):
    """Run load test at target requests per second"""
    print(f"🚀 Starting load test: {target_rps} RPS for {duration_seconds} seconds")

    semaphore = asyncio.Semaphore(target_rps * 2)  
    results = []

    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = []

        event_id = 0
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()

            batch_tasks = []
            for i in range(target_rps):
                if time.time() - start_time >= duration_seconds:
                    break
                batch_tasks.append(send_event(session, event_id, semaphore))
                event_id += 1

            if batch_tasks:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                for r in batch_results:
                    if isinstance(r, Exception):
                        results.append({
                            "success": False,
                            "error": f"Exception: {type(r).__name__}: {r}",
                            "response_time": 0.0,
                            "event_id": -1
                        })
                    else:
                        results.append(r)

            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)

    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]

    total_requests = len(results)
    success_rate = len(successful_requests) / total_requests * 100 if total_requests > 0 else 0

    response_times = [r["response_time"] for r in successful_requests]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0

    actual_rps = total_requests / duration_seconds

    print("\n📊 Load Test Results:")
    print(f"   Target RPS: {target_rps}")
    print(f"   Actual RPS: {actual_rps:.1f}")
    print(f"   Total Requests: {total_requests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Failed Requests: {len(failed_requests)}")
    print(f"   Avg Response Time: {avg_response_time*1000:.1f}ms")
    print(f"   P95 Response Time: {p95_response_time*1000:.1f}ms")
    print(f"   P95 Response Time: {p95_response_time*1000:.1f}ms")

    if failed_requests:
        print("\n❌ Sample Errors:")
        for error in failed_requests[:3]:
            print(f"   Event {error['event_id']}: {error.get('error', 'Unknown error')}")

    return {
        "success": success_rate >= 95,  
        "actual_rps": actual_rps,
        "success_rate": success_rate,
        "avg_response_time": avg_response_time,
        "p95_response_time": p95_response_time
    }

if __name__ == "__main__":
    asyncio.run(run_load_test(target_rps=250, duration_seconds=30))