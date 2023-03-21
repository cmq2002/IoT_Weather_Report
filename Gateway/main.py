import sys
import time
from Adafruit_IO import MQTTClient
from uart import *

AIO_FEED_IDs = ["button1", "button2", "sensor1", "sensor2", "sensor3"]
# AIO_USERNAME = "quang_cao2002"
# AIO_KEY = "aio_mwrr53yAXvfB6M9ypALKaEuFAEOD"

def connected(client):
    print("Connected ...")
    for feed in AIO_FEED_IDs:
        client.subscribe(feed)
    
def subscribe(client , userdata , mid , granted_qos):
    print("Subscribed ...")

def disconnected(client):
    print("Disconnected ...")
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

counter = 20
while True:
    #Read data from sensor
    counter -= 1
    if (counter <= 0):
        counter = 20
        readSerial(client)

    #Send cmd from sever to devices
    #Implement in function message
    time.sleep(1)
    pass