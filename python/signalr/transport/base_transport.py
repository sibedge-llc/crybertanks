"""
    Base Transporter class for WebSocketTransporter, LongPollingTransporter and ServerSentEventsTransporter
"""
from enum import Enum
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class MessageType(Enum):
    """
        Message type value (int) in json
    """
    INVOCATION = 1
    STREAM_ITEM = 2
    COMPLETION = 3
    STREAM_INVOCATION = 4
    CANCEL_INVOCATION = 5
    PING = 6
    CLOSE = 7


class TransportError(ConnectionError):
    """
        Error on data transfer
    """


class AutoTransport:
    """
        Factory class
    """
    _transports = {}

    @classmethod
    def create(cls, transport_name, **kwargs) -> Optional['BaseTransport']:
        """
            Returns object of class, derived from BaseTransport, or None
        Args:
            transport_name: 'WebSockets' or 'ServerSentEvents' or 'LongPolling'
            **kwargs: args, which will be sent to __init__ methods of class
        Returns:
            object of class, derived from BaseTransport
        Notes:
            Warning! Now available only WebSocket class
        """
        if transport_name not in cls._transports:
            return None

        return cls._transports.get(transport_name)(**kwargs)


class BaseTransport(ABC):
    """
        Base class for all transport classes
    """
    _transport_name = ''

    def __init_subclass__(cls, **kwargs):
        """
            Auto registration of all derived classes in a Factory's class
        """
        AutoTransport._transports[cls._transport_name] = cls

    @abstractmethod
    async def connect(self) -> bool:
        """
            Connect and handshake operations
        Raises:
            TransportError on connection errors
        """

    @abstractmethod
    async def recv(self) -> Optional[Dict]:
        """
            Receive json from transport
        Returns:
            deserialized json
        Raises:
            TransportError on connection errors
        """

    @abstractmethod
    async def send(self, data: Dict) -> None:
        """
            Sends json data
        Args:
            data: json
        Raises:
            TransportError on connection errors
        """

    @abstractmethod
    async def invoke(self, func_name: str, args: List) -> None:
        """
            Sending invocation to server
        Args:
            func_name: target name
            args: json args
        Raises:
            TransportError on connection errors
        """

    @property
    @abstractmethod
    def connected(self) -> bool:
        """
        Returns: True, if transport connected
        """

    @abstractmethod
    async def close(self) -> None:
        """
            Closes connections
        """
