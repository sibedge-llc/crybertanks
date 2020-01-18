import asyncio
import json
from functools import partial
from signal import SIGTERM, SIGINT

from signalr import Client, SignalRError

BOARD = [
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
]


async def request_arrangement(client, *args, **kwargs):
    print('Called requestArrangement')
    await client('ReceiveArrangement', [json.dumps(BOARD)])


async def receive_message(client, *args, **kwargs):
    print('Message: {}'.format(kwargs))


async def request_step(client, *args, **kwargs):
    print('Called requestStep')
    await client('ReceiveStep', [1, 1])


async def receiving(client: Client):
    try:
        while True:
            await client.receive_call()
    except asyncio.CancelledError:
        pass


async def main():
    try:
        c = Client('https://cybertank.sibedge.com:5001', 'gameHub')

        c.on('requestArrangement', request_arrangement)
        c.on('receiveMessage', receive_message)
        c.on('requestStep', request_step)

        await c.connect()
        print('Connection successful')

        event_loop = asyncio.get_event_loop()
        recv_task = event_loop.create_task(receiving(c))

        async def server_stop(client):
            print('Game closing')
            recv_task.cancel()
            await recv_task
            await c.close()
            print('Game closed')
        c.on_exit(server_stop)

        await c('Test', ['Billie'])
        await recv_task
    except SignalRError as e:
        print(e)


if __name__ == '__main__':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        print('Stopped by user')
    finally:
        loop.close()
