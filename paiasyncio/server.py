import asyncio
from asyncio import StreamReader, StreamWriter
import numpy as np
from log import logger

global count, recv_cnt
count = 0
recv_cnt = 0


async def always_write(writer: StreamWriter) -> None:
    global count
    data: np.uint64 = np.random.randint(0, 2**64, dtype=np.uint64)
    send = data.byteswap().tobytes()
    writer.write(send)
    await writer.drain()

    logger.info("[%d] Sent: 0x%x" % (count, data))

    count += 1

    await asyncio.sleep(1)


async def always_read(reader: StreamReader) -> None:
    global recv_cnt

    recv = await reader.read(8)
    logger.info("[%d] Received: 0x%x" % (recv_cnt, int.from_bytes(recv, "big")))
    recv_cnt += 1


async def handler(reader: StreamReader, writer: StreamWriter) -> None:
    while True:
        await always_write(writer)
        await always_read(reader)
        
        # await asyncio.gather(always_write(writer), always_read(reader))


async def main() -> None:
    server = await asyncio.start_server(handler, "127.0.0.1", 8888)

    alive = asyncio.create_task(heartbeat())

    async with server:
        await server.serve_forever()


async def heartbeat():
    while True:
        logger.info("Alive")
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted!")
    finally:
        print("Finished.")
