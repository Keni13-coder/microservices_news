from py_fastapi_logging.middlewares.logging import LoggingMiddleware

from http import HTTPStatus
from io import BytesIO

from time import time
from typing import  Any

from starlette import status

from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from py_fastapi_logging.middlewares.utils.request_id import generate_request_id
from py_fastapi_logging.schemas.request import RequestPayload
from py_fastapi_logging.schemas.response import ResponsePayload
from py_fastapi_logging.utils.extra import set_progname, set_request_id




class CustomLoggingMiddleware(LoggingMiddleware):
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time: float = time()
        request_body: str

        try:
            raw_request_body: bytes = await request.body()
            await self.set_body(request, raw_request_body)
            raw_request_body = await self.get_body(request)
            request_body = raw_request_body.decode()
        except Exception:
            request_body = ""

        request_headers: dict[str, str] = dict(request.headers.items())
        request_id: str = self.get_request_id_header(request_headers) or generate_request_id(prefix=self._prefix)
        set_progname(value=self._app_name)
        set_request_id(value=request_id)

        common_extras: dict[str, str] = {"progname": self._app_name, "request_id": request_id}

        is_excluded_request = self._is_url_path_in_exclude_list(request)
        if not is_excluded_request:
            server: tuple[str, int | None] = request.get("server", ("localhost", 80))
            host_or_socket, port = server
            request_log_payload: RequestPayload = RequestPayload(
                method=request.method,
                path=request.url.path,
                params=self._convert_params_to_dict(params) if (params := request.query_params) else None,
                host=f"{host_or_socket}:{port}" if port is not None else host_or_socket,
                body=request_body,
            )
            self._filter_request_payload(request_log_payload, request.headers)
            extra_payload: dict[str, Any] = common_extras | {
                "tags": ["API", "REQUEST"],
                "payload": request_log_payload,
            }
            filtered_url = self._data_filter.filter_url_encoded_string(str(request.url))
            self._logger.info(f"REQUEST {request.method} {filtered_url}", extra=extra_payload)

        response: Response
        response_body: bytes
        try:
            response = await call_next(request)
        except Exception as exc:
            response_body = HTTPStatus.INTERNAL_SERVER_ERROR.phrase.encode()
            response = Response(
                content=response_body,
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            )
            self._logger.exception("Unexpected error", exc_info=exc)
        else:
            if isinstance(response, StreamingResponse):
                with BytesIO() as raw_buffer:
                    async for chunk in response.body_iterator:
                        if not isinstance(chunk, bytes):
                            chunk = chunk.encode(response.charset)
                        raw_buffer.write(chunk)
                    response_body = raw_buffer.getvalue()
            else:
                response_body = response.body

            response = Response(
                content=response_body,
                status_code=int(response.status_code),
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        if response.status_code >= status.HTTP_400_BAD_REQUEST or not is_excluded_request:
            duration: int = round((time() - start_time) * 1000.0)
            response_log_payload: ResponsePayload = {
                "status": response.status_code,
                "response_time": f"{duration}ms",
                # "response_body": response_body.decode(),
            }
            # self._filter_response_payload(response_log_payload)
            extra_payload = common_extras | {
                "tags": ["API", "RESPONSE"],
                "payload": response_log_payload,
            }
            filtered_url = self._data_filter.filter_url_encoded_string(str(request.url))
            self._logger.info(f"RESPONSE {response.status_code} {filtered_url}", extra=extra_payload)

        return response