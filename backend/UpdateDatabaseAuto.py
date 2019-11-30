'''
脚本，自动访问本地服务器，每60s发送一个请求
'''

import requests
import socket
import time


if __name__ == "__main__":
    #服务器版本
    Place = "http://thalu.starrah.cn"

    #本地版本
    #Place = "http://127.0.0.1:8080"


    URL = "changeActivityByTime"
    Destination = Place + '/' + URL

    while True:
        time.sleep(1)
        CurrentTime = int(time.time())
        if CurrentTime % 60 == 0:
            try:
                Data = {}
                Reply = requests.post(Destination, data = Data)
                print(Reply)
            except:
                donothing = True
