import json
import asyncio

from config import CONFIG
from aio_pika import connect, Message, DeliveryMode, ExchangeType
from logs import log


class Broker:
    def __init__(self, host: str, port: int, login: str, password: str, exchange: str):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.exchange = exchange
        self.connection = None

    async def get_connection(self, loop: asyncio.AbstractEventLoop = None):
        """
        Get connection factory method

        Args:
            loop (asyncio.AbstractEventLoop): AsyncIO event loop

        Returns:

        """
        if self.connection:
            return self.connection
        conn = await connect(
            host=self.host,
            port=self.port,
            login=self.login,
            password=self.password,
            loop=loop
        )
        log.info("Message broker connection established")
        self.connection = conn
        return self.connection

    async def publish(self, topic: str, data: dict):
        """
        Publish message to the message broker on the given topic

        Args:
            topic (str): Publication topic
            data (dict): Message to publish

        """
        conn = await self.get_connection()
        channel = await conn.channel()
        exchange = await channel.declare_exchange(
            self.exchange, ExchangeType.DIRECT
        )
        message = Message(
            json.dumps(data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=topic)
        log.debug(f"Message published: {data} on topic: {topic}")

    async def subscribe(self, topic: str):
        """
        Subscribe to the message broker on the given topic

        Args:
            topic (str): Subscription topic

        Returns: Queue which can be iterated to get the subscribed messages

        """
        conn = await self.get_connection()
        channel = await conn.channel()

        logs_exchange = await channel.declare_exchange(
            self.exchange, ExchangeType.DIRECT
        )

        # Declaring queue
        queue = await channel.declare_queue(exclusive=True)

        # Binding the queue to the exchange
        await queue.bind(logs_exchange, routing_key=topic)

        return queue


BROKER = Broker(
    host=CONFIG["BROKER_HOST"],
    port=CONFIG["BROKER_PORT"],
    login=CONFIG["BROKER_LOGIN"],
    password=CONFIG["BROKER_PASSWORD"],
    exchange=CONFIG["BROKER_EXCHANGE"],
)
