import asyncio

HOST = "127.0.0.1"
PORT = 12001

REMOTE_HOST = HOST
REMOTE_PORT = 12000

CHUNK_SIZE = 4096


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            writer.write(await reader.read(CHUNK_SIZE))
    finally:
        writer.close()


async def proxy(local_reader, local_writer):
    try:
        remote_reader, remote_writer =await asyncio.open_connection(
            REMOTE_HOST,
            REMOTE_PORT
        )
        upstream = pipe(local_reader, remote_writer)
        downstream = pipe(remote_reader, local_writer)
        await asyncio.gather(upstream, downstream)
    finally:
        local_writer.close()


loop = asyncio.get_event_loop()
proxy_cb = asyncio.start_server(proxy, HOST, PORT)
proxy_server = loop.run_until_complete(proxy_cb)

try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Shutting proxy down')

proxy_server.close()
loop.run_until_complete(proxy_server.wait_closed())
loop.close()
