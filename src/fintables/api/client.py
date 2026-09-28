import inspect
import logging
from types import TracebackType
from typing import Any
from urllib.parse import urlparse

import httpx

try:
    from curl_cffi.requests import AsyncSession
except ImportError:
    AsyncSession = None  # type: ignore

from fintables.api.auth import login, refresh_token
from fintables.config import Settings, settings
from fintables.exceptions import APIError, AuthError, NotFoundError


_logger = logging.getLogger("fintables.client")
_ALLOWED_HOSTS = {"api.fintables.com", "gate.fintables.com"}


class FintablesClient:
    """Asynchronous HTTP client for Fintables API."""

    def __init__(
        self,
        custom_settings: Settings | None = None,
        access_token: str | None = None,
        refresh_token_val: str | None = None,
        client: Any = None,
    ):
        self.settings = custom_settings or settings
        self._access_token = access_token
        self._refresh_token = refresh_token_val
        if client is not None:
            self._client = client
            self._owns_client = False
        else:
            if AsyncSession is not None:
                self._client = AsyncSession(impersonate="chrome124", timeout=30.0)
            else:
                self._client = httpx.AsyncClient(timeout=30.0)
            self._owns_client = True

    async def __aenter__(self) -> "FintablesClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        if self._owns_client:
            if hasattr(self._client, "aclose"):
                await self._client.aclose()
            elif hasattr(self._client, "close"):
                res = self._client.close()
                if inspect.isawaitable(res):
                    await res

    async def _ensure_auth(self) -> None:
        """Ensures that client has a valid access token."""
        if self._access_token:
            return

        login_id = self.settings.email_or_username
        if login_id and self.settings.password:
            access, refresh = await login(
                self._client,
                login_id,
                self.settings.password,
                base_url=self.settings.base_url,
                headers=self.settings.default_headers,
            )
            self._access_token = access
            self._refresh_token = refresh
        else:
            raise AuthError(
                "Bu işlem için kimlik doğrulama gereklidir. "
                "Lütfen .env dosyasında FINTABLES_USERNAME veya FINTABLES_EMAIL ve FINTABLES_PASSWORD değerlerini ayarlayın."
            )

    async def _try_refresh_or_relogin(self) -> bool:
        """Attempts to refresh token or re-login. Returns True if succeeded."""
        if self._refresh_token:
            try:
                new_access = await refresh_token(
                    self._client,
                    self._refresh_token,
                    base_url=self.settings.base_url,
                    headers=self.settings.default_headers,
                )
                self._access_token = new_access
                return True
            except Exception as e:
                _logger.debug("Token refresh failed: %s", type(e).__name__)

        login_id = self.settings.email_or_username
        if login_id and self.settings.password:
            try:
                access, refresh = await login(
                    self._client,
                    login_id,
                    self.settings.password,
                    base_url=self.settings.base_url,
                    headers=self.settings.default_headers,
                )
                self._access_token = access
                self._refresh_token = refresh
                return True
            except Exception as e:
                _logger.debug("Re-login failed: %s", type(e).__name__)

        return False

    async def request(
        self,
        method: str,
        path: str,
        *,
        requires_auth: bool = False,
        is_gate: bool = False,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Sends an HTTP request with automatic headers and authentication handling."""
        base_url = self.settings.gate_url if is_gate else self.settings.base_url
        if path.startswith("http"):
            parsed = urlparse(path)
            if parsed.hostname not in _ALLOWED_HOSTS:
                raise ValueError(f"Disallowed host in URL: {parsed.hostname}")
            url = path
        else:
            url = f"{base_url}{path}"

        req_headers = dict(self.settings.gate_headers if is_gate else self.settings.default_headers)
        if headers:
            req_headers.update(headers)

        if requires_auth:
            await self._ensure_auth()
            req_headers["Authorization"] = f"Bearer {self._access_token}"

        response = await self._client.request(method, url, headers=req_headers, **kwargs)  # type: ignore[arg-type]

        if response.status_code == 401 and requires_auth:
            # Attempt refresh / re-login once
            refreshed = await self._try_refresh_or_relogin()
            if refreshed:
                req_headers["Authorization"] = f"Bearer {self._access_token}"
                response = await self._client.request(method, url, headers=req_headers, **kwargs)  # type: ignore[arg-type]
            else:
                raise AuthError("Oturum süresi doldu veya kimlik doğrulama başarısız oldu.")

        if response.status_code == 404:
            raise NotFoundError(f"İstenen kaynak bulunamadı (404): {url}")

        if response.status_code >= 400:
            resp_text = response.text
            truncated = (resp_text[:200] + "...") if len(resp_text) > 200 else resp_text
            raise APIError(
                f"API hatası ({response.status_code}): {truncated}",
                status_code=response.status_code,
                response_text=resp_text,
            )

        return response

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self.request("DELETE", path, **kwargs)
