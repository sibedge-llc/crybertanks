"""
    WebSocketTransporter class
"""
from logging import getLogger
from typing import Dict, List, Optional
from ssl import SSLContext, PROTOCOL_TLSv1, CERT_NONE
from json import dumps as json_dumps, loads as json_loads, JSONDecodeError

from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosedError
from websockets import InvalidURI

from .base_transport import BaseTransport, TransportError, MessageType
from .utils import add_url_parameters

# byte in Binary Frame at the end of messages
MESSAGE_TERMINATOR_SYMBOL = b'\x1E'
# Logger for test
LOGGER = getLogger(__name__)


class WebSocketTransportError(TransportError):
    """
        Error on Websocket data transfer
    """


class WebSocketsTransport(BaseTransport):
    """
        WebSockets transport class
    """
    _transport_name = 'WebSockets'

    def __init__(self, url: str, connection_id: str):
        """
            Constructor
        Args:
            url: ws url
            connection_id: session id
        """
        self._url = add_url_parameters(url, {'id': connection_id})
        self._connection = None

    async def connect(self) -> bool:
        try:
            context = SSLContext(PROTOCOL_TLSv1)
            context.verify_mode = CERT_NONE
            context.check_hostname = False

            LOGGER.debug('Connecting to %s', self._url)
            self._connection = await ws_connect(self._url, ssl=context)
        except InvalidURI as error:
            raise WebSocketTransportError(f'Wrong uri: {error}')
        except Exception as error:
            raise WebSocketTransportError(f'Unknown error: {error}')

        await self._handshake()

        return True

    async def _handshake(self):
        """
            Handshake method
        """
        LOGGER.debug('Handshaking...')
        try:
            handshake_request_data = {
                'protocol': 'json',
                'version': 1,
            }

            byte_data = bytearray(json_dumps(handshake_request_data), 'utf-8') + b'\x1E'

            await self._connection.send(bytes(byte_data))

            LOGGER.debug('Handshake sent')

            response = await self._connection.recv()
            end_code = response[-1]

            LOGGER.debug('Handshake received')

            if ord(end_code) == int.from_bytes(MESSAGE_TERMINATOR_SYMBOL, 'big'):
                answer = json_loads(response[:-1])
                if not answer:
                    # TODO add logging?
                    pass
        except JSONDecodeError as error:
            raise WebSocketTransportError(f'Handshake error on answer parsing: {error}')
        except (RuntimeError, ConnectionClosedError) as error:
            self._connection = None
            raise WebSocketTransportError(f'Handshake error on message sending: {error}')
        except Exception as error:
            raise WebSocketTransportError(f'Unknown error on handshake: {error}')

    @staticmethod
    def split_messages(message: bytes) -> List[bytes]:
        current = 0
        messages = list()
        for i, b in enumerate(message):
            if ord(b) == int.from_bytes(MESSAGE_TERMINATOR_SYMBOL, 'big'):
                messages.append(message[current: i])
                current = i + 1
        return messages

    async def recv(self) -> Optional[List[Dict]]:
        try:
            response = await self._connection.recv()
            end_code = response[-1]

            if ord(end_code) == int.from_bytes(MESSAGE_TERMINATOR_SYMBOL, 'big'):
                LOGGER.debug('Received message: %s', response[:-1])

                messages = []
                for message in self.split_messages(response):
                    messages.append(json_loads(message))

                LOGGER.debug('Parsed message: %s', str(messages))

                return messages
            raise WebSocketTransportError('Not full message')
        except (RuntimeError, ConnectionClosedError) as error:
            self._connection = None
            raise WebSocketTransportError(f'Error on message receiving: {error}')
        except JSONDecodeError as error:
            raise WebSocketTransportError(f'Message decode error on recv: {error} | {response}')

    async def send(self, data: Dict) -> None:
        try:
            serialized_data = json_dumps(data)

            LOGGER.debug('Sending message: %s', serialized_data)

            byte_data = bytearray(serialized_data, 'utf-8') + b'\x1E'

            await self._connection.send(bytes(byte_data))
        except (RuntimeError, ConnectionClosedError) as error:
            self._connection = None
            raise WebSocketTransportError(f'Error on message sending: {error}')
        except ValueError as error:
            raise WebSocketTransportError(f'Message encode error on sending: {error}')
        except Exception as error:
            raise WebSocketTransportError(f'Unknown error on sending: {error}')

    async def invoke(self, func_name: str, args: List) -> None:
        message = {
            'type': MessageType.INVOCATION.value,
            'target': func_name,
            'arguments': args,
        }
        await self.send(message)

    async def close(self) -> None:
        LOGGER.debug('Connection closed')
        await self._connection.close()

    @property
    def connected(self) -> bool:
        return self._connection is not None
