import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request, status

_WINDOW = 60
_LIMIT = 5
_buckets: dict[str, deque] = defaultdict(deque)


def _key(request: Request, scope: str) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{scope}:{host}"


def check_rate_limit(request: Request, scope: str, limit: int = _LIMIT) -> None:
    key = _key(request, scope)
    now = time.time()
    bucket = _buckets[key]
    while bucket and now - bucket[0] > _WINDOW:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
    bucket.append(now)


def reset_rate_limits() -> None:
    _buckets.clear()
