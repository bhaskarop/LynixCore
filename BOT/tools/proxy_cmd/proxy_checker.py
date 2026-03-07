import time
import asyncio
from curl_cffi.requests import AsyncSession


async def check_single_proxy(proxy_url: str, timeout: int = 5) -> tuple:
    """
    Check a single proxy by making a request to httpbin.
    Returns (is_alive, ping_ms, rating_emoji, rating_label)
    """
    start = time.perf_counter()
    try:
        proxy_dict = {"http": proxy_url, "https": proxy_url}
        async with AsyncSession(
            proxies=proxy_dict, timeout=timeout, verify=False, impersonate="chrome120"
        ) as session:
            r = await session.get("https://httpbin.org/ip")
            if r.status_code == 200:
                ping_ms = int((time.perf_counter() - start) * 1000)
                emoji, label = _rate_ping(ping_ms)
                return True, ping_ms, emoji, label
    except Exception:
        pass

    ping_ms = int((time.perf_counter() - start) * 1000)
    return False, ping_ms, "❌", "Dead"


def _rate_ping(ping_ms: int) -> tuple:
    """Rate proxy quality based on ping latency."""
    if ping_ms < 1000:
        return "⚡", "Fast"
    elif ping_ms < 3000:
        return "✅", "Good"
    elif ping_ms < 5000:
        return "⚠️", "Slow"
    else:
        return "🐢", "Very Slow"


async def check_proxies_batch(proxy_list: list, timeout: int = 5) -> list:
    """
    Check multiple proxies concurrently.
    Returns list of (proxy_url, is_alive, ping_ms, rating_emoji, rating_label)
    """
    tasks = [check_single_proxy(proxy, timeout) for proxy in proxy_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    checked = []
    for proxy, result in zip(proxy_list, results):
        if isinstance(result, Exception):
            checked.append((proxy, False, 0, "❌", "Dead"))
        else:
            is_alive, ping_ms, emoji, label = result
            checked.append((proxy, is_alive, ping_ms, emoji, label))

    # Sort by ping (alive first, then by latency)
    checked.sort(key=lambda x: (not x[1], x[2]))
    return checked
