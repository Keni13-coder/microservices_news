import random
import time
from fastapi import FastAPI, HTTPException
from circuitbreaker import circuit
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, _CachedRequest, _CachedRequest, _StreamingResponse, T
from starlette._utils import collapse_excgroups
from starlette.types import Message, Receive, Scope, Send
import anyio
from anyio.abc import ObjectReceiveStream, ObjectSendStream
import typing

#  типо закешировали
async def exption_call():
    return 'Был збой'
    


class TestMiddleware(BaseHTTPMiddleware):
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = _CachedRequest(scope, receive)
        wrapped_receive = request.wrapped_receive
        response_sent = anyio.Event()
        
        
        async def call_next(request: Request) -> Response:
            app_exc: typing.Optional[Exception] = None
            send_stream: ObjectSendStream[typing.MutableMapping[str, typing.Any]]
            recv_stream: ObjectReceiveStream[typing.MutableMapping[str, typing.Any]]
            send_stream, recv_stream = anyio.create_memory_object_stream()

            async def receive_or_disconnect() -> Message:
                if response_sent.is_set():
                    return {"type": "http.disconnect"}

                async with anyio.create_task_group() as task_group:

                    async def wrap(func: typing.Callable[[], typing.Awaitable[T]]) -> T:
                        result = await func()
                        task_group.cancel_scope.cancel()
                        return result

                    task_group.start_soon(wrap, response_sent.wait)
                    message = await wrap(wrapped_receive)

                if response_sent.is_set():
                    return {"type": "http.disconnect"}

                return message

            async def close_recv_stream_on_response_sent() -> None:
                await response_sent.wait()
                recv_stream.close()

            async def send_no_error(message: Message) -> None:
                try:
                    await send_stream.send(message)
                except anyio.BrokenResourceError:
                    # recv_stream has been closed, i.e. response_sent has been set.
                    return

            async def coro() -> None:
                nonlocal app_exc

                async with send_stream:
                    try:
                        await self.app(scope, receive_or_disconnect, send_no_error)
                    except Exception as exc:
                        app_exc = exc

            task_group.start_soon(close_recv_stream_on_response_sent)
            task_group.start_soon(coro)

            try:
                message = await recv_stream.receive()
                info = message.get("info", None)
                if message["type"] == "http.response.debug" and info is not None:
                    message = await recv_stream.receive()
            except anyio.EndOfStream:
                if app_exc is not None:
                    raise app_exc
                raise RuntimeError("No response returned.")

            assert message["type"] == "http.response.start"

            async def body_stream() -> typing.AsyncGenerator[bytes, None]:
                async with recv_stream:
                    async for message in recv_stream:
                        assert message["type"] == "http.response.body"
                        body = message.get("body", b"")
                        if body:
                            yield body
                        if not message.get("more_body", False):
                            break

                if app_exc is not None:
                    raise app_exc

            response = _StreamingResponse(
                status_code=message["status"], content=body_stream(), info=info
            )
            response.raw_headers = message["headers"]
            return response

        with collapse_excgroups():
            async with anyio.create_task_group() as task_group:
                response = await self.dispatch_func(request, call_next)
                await response(scope, wrapped_receive, send)
                response_sent.set()
    
    
    
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        return response
    

app = FastAPI()

app.add_middleware(TestMiddleware)

@app.get('/success')
async def success_endpoint():
    return {
        "msg": "Call to this endpoint was a smashing success."
    }, 200


@app.get('/failure')
async def faulty_endpoint():
    r = random.randint(0, 1)
    if r == 0:
        time.sleep(2)

    return {
        "msg": "I will fail."
    }, 500


@app.get('/random')
@circuit(failure_threshold=3, expected_exception=Exception)
async def fail_randomly_endpoint():
    r = random.randint(0, 1)
    if r == 0:
        return {
            "msg": "Success msg"
        }, 200

    error = 'asdasd'  + 14