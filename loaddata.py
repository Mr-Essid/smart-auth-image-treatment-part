import asyncio
import requests
import _thread


async def fun():
    print("Hello World From Fun")
    return requests.get("http://localhost/employer")


async def getFunction():
    response = await asyncio.create_task(fun())
    await asyncio.sleep(12)
    print(response)


asyncio.run(getFunction())

print("Hello World")
