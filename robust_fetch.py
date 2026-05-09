import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Tuple


def _build_session(
    total_retries: int = 3,
    backoff_factor: float = 2.0,
    status_forcelist: Tuple[int, ...] = (500, 502, 503, 504),
    allowed_methods: Tuple[str, ...] = ("GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"),
    timeout: int = 60,
    user_agent: str = "ST-DailyReport/1.0"
) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": user_agent})
    # store timeout on session for convenience
    session.request_timeout = timeout  # type: ignore[attr-defined]
    return session


def robust_get(url: str, **kwargs) -> requests.Response:
    session: requests.Session = kwargs.pop("session", None) or _build_session()
    if "timeout" not in kwargs:
        kwargs["timeout"] = getattr(session, "request_timeout", 60)
    return session.get(url, **kwargs)


def robust_post(url: str, **kwargs) -> requests.Response:
    max_retries = kwargs.pop("max_retries", None)
    session: requests.Session = kwargs.pop("session", None) or _build_session(total_retries=max_retries if max_retries else 3)
    if "timeout" not in kwargs:
        kwargs["timeout"] = getattr(session, "request_timeout", 60)
    return session.post(url, **kwargs)
