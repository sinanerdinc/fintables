from typing import Any
from fintables.exceptions import AuthError
from fintables.i18n import t


async def login(
    client: Any,
    email: str,
    password: str,
    base_url: str = "https://api.fintables.com",
    headers: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Logs in using email/password and returns (access_token, refresh_token)."""
    req_headers = {
        "User-Agent": "fintables-mobile/323 (2.28.2)",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)

    payload = {"email": email, "password": password}
    try:
        resp = await client.post(
            f"{base_url}/auth/token/",
            json=payload,
            headers=req_headers,
        )
        if resp.status_code == 200:
            data = resp.json()
            access = data.get("access") or data.get("access_token")
            refresh = data.get("refresh") or data.get("refresh_token", "")
            if access:
                return access, refresh
        elif resp.status_code == 400 and "username" in getattr(resp, "text", ""):
            resp2 = await client.post(
                f"{base_url}/auth/token/",
                json={"username": email, "password": password},
                headers=req_headers,
            )
            if resp2.status_code == 200:
                data = resp2.json()
                access = data.get("access") or data.get("access_token")
                refresh = data.get("refresh") or data.get("refresh_token", "")
                if access:
                    return access, refresh
    except Exception as e:
        if isinstance(e, AuthError):
            raise
        raise AuthError(t("error.login_request_failed", error=type(e).__name__)) from e

    error_msg = resp.text if "resp" in locals() and hasattr(resp, "text") else "Unknown error"
    raise AuthError(t("error.login_failed", detail=error_msg))


async def refresh_token(
    client: Any,
    refresh: str,
    base_url: str = "https://api.fintables.com",
    headers: dict[str, str] | None = None,
) -> str:
    """Refreshes access_token using refresh_token."""
    req_headers = {
        "User-Agent": "fintables-mobile/323 (2.28.2)",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)

    try:
        resp = await client.post(
            f"{base_url}/auth/token/refresh/",
            json={"refresh": refresh},
            headers=req_headers,
        )
        if resp.status_code == 200:
            data = resp.json()
            access = data.get("access") or data.get("access_token")
            if access:
                return access
    except Exception as e:
        raise AuthError(t("error.refresh_failed", error=type(e).__name__)) from e

    raise AuthError(t("error.refresh_unsuccessful"))
