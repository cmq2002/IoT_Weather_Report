import serial.tools.list_ports

STARTUP = 0
CONNECTED = 1
DISCONNECTED = 2
MAX_CONNECTION_ATTEMP = 3
TIMEOUT = 3
HALT_TIME = 5
TEMP_LOWERBOUND = 5
TEMP_UPPERBOUND = 42
HUMID_LOWERBOUND = 10
HUMID_UPPERBOUND = 92

def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "STMicroelectronics STLink Virtual COM Port" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

def openUART(client):
    global ser
    if getPort() != "None":
        try:
            ser = serial.Serial(port=getPort(), baudrate=9600)
        except:
            print("UART Connection Loss...")
            client.publish("error-detect","UART Connection Loss...")
            return DISCONNECTED
        print("UART Connection Successful...")
        print(ser)
        client.publish("error-detect","UART Connection Successful...")
        return CONNECTED
    else:
        print("UART Connection Loss...")
        client.publish("error-detect","UART Connection Loss...")
        return DISCONNECTED

def processData(client, data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[0] == "TEMP":
            if (splitData[1] >= TEMP_LOWERBOUND and splitData[1] <= TEMP_UPPERBOUND):
                client.publish("sensor1", splitData[1])
            else:
                client.publish("error-detect", "Warning: Unexpected Temp Value...")
        elif splitData[0] == "HUMID":
            if (splitData[1] >= HUMID_LOWERBOUND and splitData[1] <= HUMID_UPPERBOUND):
                client.publish("sensor2", splitData[1])
            else:
                client.publish("error-detect", "Warning: Unexpected Humid Value...")
    except:
        pass

mess = ""
def readSerial(client):
    try:
        bytesToRead = ser.inWaiting()
    except:
        print("UART Connection Loss...")
        client.publish("error-detect","UART Connection Loss...")
        return DISCONNECTED
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(client, mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]
    return CONNECTED


def writeData(data):
    ser.write(str(data).encode())