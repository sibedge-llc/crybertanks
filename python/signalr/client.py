"""
    SignalR Client class
"""
from enum import Enum
from logging import getLogger
from typing import List, Any, Callable
from urllib.parse import urljoin
from collections import defaultdict

from httpx import post as rest_post
from httpx.exceptions import HTTPError

from signalr.transport import AutoTransport, TransportError, MessageType


LOGGER = getLogger(__name__)


class SpecialMethods(Enum):
    """
        Special methods targets
    """
    EXIT = '__EXIT__'
    PING = '__PING__'


class SignalRError(Exception):
    """
        Error on data transfer in SingalR
    """


class Client:
    """
        Client class
    """

    def __init__(self, url: str, hub: str):
        """
            Constructor
        Args:
            url: url to cybertanks server
            hub: hub name
        """
        self._url = url
        self._hub = hub
        self._transport = None
        self._callbacks = defaultdict(list)
        # Setting up default callback on ping signal
        self._callbacks[SpecialMethods.PING.value].append(self._default_ping_handler)

    async def connect(self):
        """
            Connection to cybertanks server
        Raises:
            SignalRError: on negotiate error, empty transport list or WS connection error
        """
        # Sending request for initialization
        negotiate_url = urljoin(self._url, f'{self._hub}/negotiate')
        try:
            response = await rest_post(
                negotiate_url,
                headers={'Content-Type': 'application/json'},
                verify=False,
            )
        except HTTPError as error:
            raise SignalRError(f'Error on negotiate request {error}')

        if response.status_code != 200:
            raise SignalRError(
                f'Negotiate error. Server returned {response.status_code} ({response.text})'
            )

        # Checking available transports
        response_json = response.json()

        # No only WebSockets available :c
        ws_connections = list(
            filter(
                lambda data: data['transport'] == 'WebSockets',
                response_json['availableTransports'],
            )
        )

        if len(ws_connections) == 0:
            raise SignalRError(f'No available ws transports on the server')

        ws_connect_url = urljoin(self._url.replace('https:', 'wss:'), self._hub)

        # Selecting transport
        self._transport = AutoTransport.create(
            'WebSockets',
            url=ws_connect_url,
            connection_id=response_json['connectionId'],
        )

        # connecting
        try:
            await self._transport.connect()
        except TransportError as error:
            raise SignalRError(f'Transport Error on connection: {error}')

    async def __call__(self, name: str, arguments: List[Any]):
        """
            Invokes function on server
        Args:
            name: function name
            arguments: arguments list

        Raises:
            SignalRError on transfer errors
        """
        LOGGER.debug('Calling %s()', name)
        if self._transport and self._transport.connected:
            await self._transport.invoke(name, arguments)
        else:
            raise SignalRError(f'Trying to invoke {name}({arguments}) before connection')

    async def receive_call(self) -> None:
        """
            Method to receive calls from server
        """
        if self._transport and self._transport.connected:
            call = await self._transport.recv()

            if call:
                if call['type'] == MessageType.INVOCATION.value:
                    LOGGER.debug('Received invokation %s()', call['target'])

                    for callback in self._callbacks[call['target']]:
                        await callback(*call['arguments'], client=self)

                elif call['type'] == MessageType.CLOSE.value:
                    LOGGER.debug('Received close')

                    for callback in self._callbacks[SpecialMethods.EXIT.value]:
                        await callback(client=self)

                elif call['type'] == MessageType.PING.value:
                    LOGGER.debug('Received ping')
                    for callback in self._callbacks[SpecialMethods.PING.value]:
                        await callback(client=self)

    async def close(self):
        """
            Close connection to server
        """
        if self._transport and self._transport.connected:
            await self._transport.close()

    def on(self, method_name: str, callback: Callable) -> None:
        """
            Registers callback on call from service receiving
        Args:
            method_name: method name
            callback: closure or function
        """
        self._callbacks[method_name].append(callback)

    def on_exit(self, callback: Callable) -> None:
        """
            Registers callback on Exit call
        Args:
            callback: closure or function
        """
        self._callbacks[SpecialMethods.EXIT.value].append(callback)

    def on_ping(self, callback: Callable) -> None:
        """
            Registers callback on Ping call
        Args:
            callback: closure or function
        """
        self._callbacks[SpecialMethods.PING.value].append(callback)

    async def _default_ping_handler(self, client: 'Client'):
        """
            This is default callback function on ping - it sends ping signal to server
        """
        if self._transport and self._transport.connected:
            await self._transport.send({'type': 6})
