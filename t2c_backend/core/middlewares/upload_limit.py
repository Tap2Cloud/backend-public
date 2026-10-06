from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from t2c_backend.core.i18n import _
from t2c_backend.utils.enums import ErrorMessageCodes


class _UploadTooLargeError(Exception):
    pass


class UploadLimitMiddleware:
    """
    Caps the combined size of all files sent in one multipart/form-data request.

    Applies to every endpoint, including the ones inherited from the open-source
    package, so no route has to opt in. Requests are rejected up front when the
    Content-Length header already exceeds the limit, and the body is also counted
    while it streams in so chunked uploads (no Content-Length) can't slip past.

    FastAPI wraps any error raised while parsing the form into a generic 400, so
    instead of relying on the exception reaching us, the app's response is dropped
    once the limit is crossed and a 413 is sent in its place.
    """

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        if not headers.get("content-type", "").startswith("multipart/form-data"):
            await self.app(scope, receive, send)
            return

        content_length = headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > self.max_bytes:
            await self._reject(scope, receive, send)
            return

        received = 0
        too_large = False
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received, too_large
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    too_large = True
                    raise _UploadTooLargeError()
            return message

        async def guarded_send(message: Message) -> None:
            nonlocal response_started
            if too_large:
                return
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, guarded_send)
        except Exception:
            if not too_large or response_started:
                raise

        if too_large and not response_started:
            await self._reject(scope, receive, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        limit_mb = self.max_bytes // (1024 * 1024)
        response = JSONResponse(
            status_code=413,
            content={
                "msg": _("Total size of uploaded documents must not exceed %(limit)s MB.")
                % {"limit": limit_mb},
                "errorCode": ErrorMessageCodes.BAD_REQUEST,
            },
            headers={"Connection": "close"},
        )
        await response(scope, receive, send)
