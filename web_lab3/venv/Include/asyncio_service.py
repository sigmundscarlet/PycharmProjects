import asyncio
async def dispatch(reader,writer):
    while True :
        data = await reader.readline()
        message = data.decode()
        print(message)
        if message[0]=='0':
            break
        writer.writelines([data])
        await writer.drain()
    writer.close()
if __name__=='__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch,'127.0.0.1',8080,loop=loop)
    server = loop.run_until_complete(coro)
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wai_closed())
    loop.close()