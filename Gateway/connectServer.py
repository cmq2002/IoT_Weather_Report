from Adafruit_IO import MQTTClient
import uart
import log
import sys

clientInfo = open("./client_info.txt", "r")
AIO_FEED_IDs = ["button1", "button2", "sensor1", "sensor2", "mcu-info", "sending_freq", "error-detect"]
AIO_USERNAME = clientInfo.readline().strip()
AIO_KEY = clientInfo.readline().strip()

def connected(client):
    for feed in AIO_FEED_IDs:
        client.subscribe(feed)
    
def subscribe(client , userdata , mid , granted_qos):
    print("Subscribed...")

def disconnected(client):
    print("Disconnected...")
    sys.exit (1)

def message(client , feed_id , payload):
    if feed_id == "button1":
        if payload == "0":
            uart.writeData("@OFF1*")
        else:
            uart.writeData("@ON1*")
    if feed_id == "button2":
        if payload == "0":
            uart.writeData("@OFF2*")
        else:
            uart.writeData("@ON2*")
    if feed_id == "sending_freq":
        print("New Operating Cycle: " + payload)
        uart.setProcDelay(int(payload))
        uart.writeData("@F:" + str(payload) + ":" + "*")
        # data = payload.replace("!", "")
        # data = payload.replace("#", "")
        # splitData = data.split(":")
        # if (splitData[0] == "!FREQ"):
        #     if (len(splitData[1]) == 1): 
        #         return
        #     else:
        #         print("New Operating Frequency: " + splitData[1])
        #         uart.setProcDelay(int(splitData[1]))
        # else:
        #     return

client = MQTTClient(AIO_USERNAME , AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
try: 
    client.connect()
except:
    print("Internet Connection Loss...")
    log.writelog("Internet Connection Loss...")
    sys.exit(1)
client.loop_background()