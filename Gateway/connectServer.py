from Adafruit_IO import MQTTClient
from uart import *
import sys

clientInfo = open("./client_info.txt", "r")
AIO_FEED_IDs = ["button1", "button2", "sensor1", "sensor2", "error-detect"]
AIO_USERNAME = clientInfo.readline().strip()
AIO_KEY = clientInfo.readline().strip()

def connected(client):
    global isServerConnected
    print("Connected...")
    for feed in AIO_FEED_IDs:
        client.subscribe(feed)
    
def subscribe(client , userdata , mid , granted_qos):
    print("Subscribed...")

def disconnected(client):
    print("Disconnected...")
    sys.exit (1)

def message(client , feed_id , payload):
    # print("Value Received: " + payload + ", FeedID: " + feed_id)
    if feed_id == "button1":
        if payload == "0":
            writeData(1)
        else:
            writeData(2)
    if feed_id == "button2":
        if payload == "0":
            writeData(3)
        else:
            writeData(4)

client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()