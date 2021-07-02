import asyncio
import datetime

from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from broker import BROKER
from logs import log
from config import CONFIG

app = FastAPI(docs_url="/", redoc_url=None)


async def status_event_generator(request, topic):
    log.debug("Received the request")
    while True:
        if await request.is_disconnected():
            log.debug("Request disconnected")
            break
        queue = await BROKER.subscribe(topic)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    yield {
                        "event": "update",
                        "retry": int(CONFIG["STATUS_STREAM_RETRY_TIMEOUT"]),
                        "data": message.body.decode(),
                    }
                    log.debug("Message: %s", message.body.decode())
        await asyncio.sleep(int(CONFIG["STATUS_STREAM_DELAY"]))


@app.get("/stream/{topic}")
async def get_events(
    topic: str,
    request: Request
):
    event_generator = status_event_generator(request, topic)
    return EventSourceResponse(event_generator)


@app.post("/event/{topic}")
async def post_events(
    topic: str,
    message: dict
):
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    message["__created_at"] = datetime.datetime.utcnow().isoformat()
    await BROKER.publish(topic, message)
    return {"msg": "Message published"}


origins = CONFIG["CORS_ORIGINS"].split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
