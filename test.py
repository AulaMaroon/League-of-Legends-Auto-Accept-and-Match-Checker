from lcu_driver import Connector
import os
import keyboard
import time
from sys import exit
from pprint import pprint as pp

connector = Connector()
# fired when LCU API is ready to be used
@connector.ready
async def connect(connection):
    a = await connection.request('get', '/lol-summoner/v1/current-summoner')
    pp(await a.json())

# fired when League Client is closed (or disconnected from websocket)
@connector.close
async def disconnect(_):
    await connector.stop()



# starts the connector
connector.start()