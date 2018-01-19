# -*- coding: utf-8 -*-
"""
创建日期: 2017-12-31
@author: zengbin

使用 火币网 websocket API 获取行情数据
https://github.com/huobiapi/API_Docs/wiki/WS_api_reference
===============================================================================
"""


import websocket
from datetime import datetime
import json
from io import BytesIO
import gzip
from retrying import retry

def on_message(ws, event):
    buf = BytesIO(event)
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()
    data = json.loads(data)
    if "ping" in data:
        pong = {"pong": data["ping"]}
        pong = json.dumps(pong)
        # print(pong)
        ws.send(pong)
        return
    if "status" in data:
        if data["status"] != "ok":
            print(data)
            exit(0)
        else:
            return
    print(data)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("close")

def on_open(ws, topic="market.ethusdt.kline.1min"):
    """
    topic格式：  https://github.com/huobiapi/API_Docs/wiki/WS_request#5-topic%E6%A0%BC%E5%BC%8F
    """
    print('WebSocket connect at time: ', datetime.now())
    market = {"sub": topic, "id": "kline " + str(datetime.now())}
    ws.send(json.dumps(market))

@retry(stop_max_attempt_number=6)
def ws_reciever():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.huobi.pro/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
    
if __name__ == "__main__":
    ws_reciever()
