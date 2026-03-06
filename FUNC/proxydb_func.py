import random
import re
from mongodb import proxydb


def _normalize_proxy(raw: str) -> str | None:
    """
    Accept any common proxy format and return http://user:pass@host:port
    or http://host:port. Returns None if unparseable.

    Supported inputs:
      host:port:user:pass
      user:pass@host:port
      http://user:pass@host:port
      http://host:port
      host:port
    """
    raw = raw.strip()
    if not raw:
        return None

    if raw.startswith("http://") or raw.startswith("https://"):
        return raw

    # user:pass@host:port
    if "@" in raw:
        return f"http://{raw}"

    parts = raw.split(":")
    if len(parts) == 4:
        host, port, user, passwd = parts
        return f"http://{user}:{passwd}@{host}:{port}"
    elif len(parts) == 2:
        return f"http://{raw}"

    return None


async def get_user_proxies(user_id: str) -> list[str]:
    doc = proxydb.find_one({"user_id": user_id}, {"_id": 0})
    if doc:
        return doc.get("proxies", [])
    return []


async def add_user_proxies(user_id: str, raw_lines: list[str]) -> tuple[int, int]:
    """
    Parse and add proxies. Returns (added_count, skipped_count).
    Duplicates within the user's list are skipped.
    """
    existing = await get_user_proxies(user_id)
    existing_set = set(existing)
    added = 0
    skipped = 0

    for line in raw_lines:
        normalized = _normalize_proxy(line)
        if normalized and normalized not in existing_set:
            existing.append(normalized)
            existing_set.add(normalized)
            added += 1
        else:
            skipped += 1

    proxydb.update_one(
        {"user_id": user_id},
        {"$set": {"proxies": existing}},
        upsert=True,
    )
    return added, skipped


async def remove_user_proxy(user_id: str, index: int) -> bool:
    """Remove proxy by 1-based index. Returns True if removed."""
    existing = await get_user_proxies(user_id)
    if 1 <= index <= len(existing):
        existing.pop(index - 1)
        proxydb.update_one(
            {"user_id": user_id},
            {"$set": {"proxies": existing}},
        )
        return True
    return False


async def remove_all_user_proxies(user_id: str) -> int:
    """Remove all proxies. Returns count removed."""
    existing = await get_user_proxies(user_id)
    count = len(existing)
    if count:
        proxydb.update_one(
            {"user_id": user_id},
            {"$set": {"proxies": []}},
        )
    return count


async def get_random_user_proxy(user_id: str) -> str | None:
    """Pick a random proxy from user's list. Returns formatted URL or None."""
    proxies = await get_user_proxies(user_id)
    if proxies:
        return random.choice(proxies)
    return None
