import serial.tools.list_ports
import time
import sys

STARTUP = 0
CONNECTED = 1
DISCONNECTED = 2
MAX_CONNECTION_ATTEMP = 3
TIMEOUT = 3
HOLD_TIME_LOCAL = 1
HOLD_TIME_GLOBAL = 5
TEMP_LOWERBOUND = 5
TEMP_UPPERBOUND = 42
HUMID_LOWERBOUND = 10
HUMID_UPPERBOUND = 92
ACTIVE_CYCLE = 10
NUM_DATA_ELEMENTS = 2
ENDING_BYTE = "#"

class UART:
    def __init__(self):
        self.state = STARTUP
        self.connection_attemp = 0
        self.counter = TIMEOUT
        self.ser = None  
        self.mess = ""
        self.proc_delay = ACTIVE_CYCLE
        self.delay_counter = self.proc_delay

    def getPort():
        ports = serial.tools.list_ports.comports()
        N = len(ports)
        commPort = "None"
        for i in range(0, N):
            port = ports[i]
            strPort = str(port)
            # if "Silicon Labs CP210x USB to UART Bridge" in strPort:
            if "STMicroelectronics STLink Virtual COM Port" in strPort:
                splitPort = strPort.split(" ")
                commPort = (splitPort[0])
        return commPort

    def confirmUART(self, client):
        if (self.state == DISCONNECTED or self.state == STARTUP):
            while(self.connection_attemp < MAX_CONNECTION_ATTEMP and self.state != CONNECTED):
                if (self.counter == TIMEOUT):
                    print("Connection Attemps: " + str(self.connection_attemp + 1))
                    self.state = self.openUART(client)
                if (self.state == DISCONNECTED):
                    self.counter -= 1
                    if (self.counter <=0):
                        self.connection_attemp += 1
                        self.counter = TIMEOUT
                    time.sleep(HOLD_TIME_LOCAL)
                else:
                    self.connection_attemp = 0

            if self.connection_attemp == MAX_CONNECTION_ATTEMP:
                print("Reach Max Attemp...")
                client.publish("error-detect", "Reach Max Attemp...")
                print("Disconnected...")
                sys.exit (1)
        return self.state

    def openUART(self, client):
        if self.getPort() != "None":
            try:
                self.ser = serial.Serial(port=self.getPort(), baudrate=9600)
            except:
                print("UART Connection Loss...")
                client.publish("error-detect","UART Connection Loss...")
                return DISCONNECTED
            print("UART Connection Successful...")
            print(self.ser)
            client.publish("error-detect","UART Connection Successful...")
            return CONNECTED
        else:
            print("UART Connection Loss...")
            client.publish("error-detect","UART Connection Loss...")
            return DISCONNECTED

    def confirmDataIntegrity(self, data):
        splitData = data.split(":")
        if (len(splitData) != 3):
            return 0
        else:
            recv_checkSum = int(splitData[len(splitData)-1].replace("#", ""))
            recalc_checkSum = 0
            split = 0
            for i in range(len(data)):
                if (data[i] == ":"): split += 1
                if (split == NUM_DATA_ELEMENTS): break
                recalc_checkSum += ord(data[i])
            recalc_checkSum += ord(ENDING_BYTE)
            if (recalc_checkSum == recv_checkSum):
                return 1
            else:
                return 0

    def processData(self, client, data):
        checkSumRes = self.confirmDataIntegrity(data)
        if (checkSumRes == 0):
            print("Data Integrity Violated...")
            client.publish("error-detect", "Data Integrity Violated...")
            return
        else:
            data = data.replace("!", "")
            data = data.replace("#", "")
            splitData = data.split(":")
            print(splitData)
            try:
                if splitData[0] == "TEMP":
                    if (float(splitData[1]) >= TEMP_LOWERBOUND and float(splitData[1]) <= TEMP_UPPERBOUND):
                        client.publish("sensor1", splitData[1])
                    else:
                        client.publish("error-detect", "Warning: Unexpected Temp Value...")
                elif splitData[0] == "HUMID":
                    if (float(splitData[1]) >= HUMID_LOWERBOUND and float(splitData[1]) <= HUMID_UPPERBOUND):
                        client.publish("sensor2", splitData[1])
                    else:
                        client.publish("error-detect", "Warning: Unexpected Humid Value...")
                elif splitData[0] == "ERROR":
                    client.publish("error-detect", splitData[1])
                elif splitData[0] == "MCU":
                    client.publish("mcu-info", splitData[1])
                elif (splitData[0] == "BUTTON1" and splitData[1] == "REVERT"):
                    client.publish("button1", 0)
            except:
                pass

    def readSerial(self, client):
        try:
            bytesToRead = self.ser.inWaiting()
        except:
            print("UART Connection Loss...")
            client.publish("error-detect","UART Connection Loss...")
            return DISCONNECTED
        if (bytesToRead > 0):
            self.mess = self.mess + self.ser.read(bytesToRead).decode("UTF-8")
            while ("#" in self.mess) and ("!" in self.mess):
                start = self.mess.find("!")
                end = self.mess.find("#")
                self.processData(client, self.mess[start:end + 1])
                if (end == len(self.mess)):
                    self.mess = ""
                else:
                    self.mess = self.mess[end+1:]
        return CONNECTED

    def startMeasure(self, client):
        if (self.state == CONNECTED):
            print(self.delay_counter)
            self.delay_counter -= 1
            if (self.delay_counter <= 0): 
                self.delay_counter = self.proc_delay
                self.state = self.readSerial(client)
            time.sleep(HOLD_TIME_LOCAL)
        return self.state

    def setProcDelay(self, new_delay):
        if (new_delay < 5): new_delay = 5
        self.proc_delay = new_delay
        self.delay_counter = new_delay
        return self.proc_delay

    def writeData(self, data):
        self.ser.write(str(data).encode())






# def getPort():
#     ports = serial.tools.list_ports.comports()
#     N = len(ports)
#     commPort = "None"
#     for i in range(0, N):
#         port = ports[i]
#         strPort = str(port)
#         # if "Silicon Labs CP210x USB to UART Bridge" in strPort:
#         if "STMicroelectronics STLink Virtual COM Port" in strPort:
#             splitPort = strPort.split(" ")
#             commPort = (splitPort[0])
#     return commPort

# state = STARTUP
# connection_attemp = 0
# counter = TIMEOUT
# def confirmUART(client):
#     global state, connection_attemp, counter
#     if (state == DISCONNECTED or state == STARTUP):
#         while(connection_attemp < MAX_CONNECTION_ATTEMP and state != CONNECTED):
#             if (counter == TIMEOUT):
#                 print("Connection Attemps: " + str(connection_attemp + 1))
#                 state = openUART(client)
#             if (state == DISCONNECTED):
#                 counter -= 1
#                 if (counter <=0):
#                     connection_attemp += 1
#                     counter = TIMEOUT
#                 time.sleep(HOLD_TIME_LOCAL)
#             else:
#                 connection_attemp = 0

#         if connection_attemp == MAX_CONNECTION_ATTEMP:
#             print("Reach Max Attemp...")
#             client.publish("error-detect", "Reach Max Attemp...")
#             print("Disconnected...")
#             sys.exit (1)
#     return state

# def openUART(client):
#     global ser
#     if getPort() != "None":
#         try:
#             ser = serial.Serial(port=getPort(), baudrate=9600)
#         except:
#             print("UART Connection Loss...")
#             client.publish("error-detect","UART Connection Loss...")
#             return DISCONNECTED
#         print("UART Connection Successful...")
#         print(ser)
#         client.publish("error-detect","UART Connection Successful...")
#         return CONNECTED
#     else:
#         print("UART Connection Loss...")
#         client.publish("error-detect","UART Connection Loss...")
#         return DISCONNECTED

# def confirmDataIntegrity(data):
#     splitData = data.split(":")
#     if (len(splitData) != 3):
#         return 0
#     else:
#         recv_checkSum = int(splitData[len(splitData)-1].replace("#", ""))
#         recalc_checkSum = 0
#         split = 0
#         for i in range(len(data)):
#             if (data[i] == ":"): split += 1
#             if (split == NUM_DATA_ELEMENTS): break
#             recalc_checkSum += ord(data[i])
#         recalc_checkSum += ord(ENDING_BYTE)
#         if (recalc_checkSum == recv_checkSum):
#             return 1
#         else:
#             return 0

# def processData(client, data):
#     checkSumRes = confirmDataIntegrity(data)
#     if (checkSumRes == 0):
#         print("Data Integrity Violated...")
#         client.publish("error-detect", "Data Integrity Violated...")
#         return
#     else:
#         data = data.replace("!", "")
#         data = data.replace("#", "")
#         splitData = data.split(":")
#         print(splitData)
#         try:
#             if splitData[0] == "TEMP":
#                 if (float(splitData[1]) >= TEMP_LOWERBOUND and float(splitData[1]) <= TEMP_UPPERBOUND):
#                     client.publish("sensor1", splitData[1])
#                 else:
#                     client.publish("error-detect", "Warning: Unexpected Temp Value...")
#             elif splitData[0] == "HUMID":
#                 if (float(splitData[1]) >= HUMID_LOWERBOUND and float(splitData[1]) <= HUMID_UPPERBOUND):
#                     client.publish("sensor2", splitData[1])
#                 else:
#                     client.publish("error-detect", "Warning: Unexpected Humid Value...")
#             elif splitData[0] == "ERROR":
#                 client.publish("error-detect", splitData[1])
#             elif splitData[0] == "MCU":
#                 client.publish("mcu-info", splitData[1])
#             elif (splitData[0] == "BUTTON1" and splitData[1] == "REVERT"):
#                 client.publish("button1", 0)
#         except:
#             pass

# mess = ""
# def readSerial(client):
#     try:
#         bytesToRead = ser.inWaiting()
#     except:
#         print("UART Connection Loss...")
#         client.publish("error-detect","UART Connection Loss...")
#         return DISCONNECTED
#     if (bytesToRead > 0):
#         global mess
#         mess = mess + ser.read(bytesToRead).decode("UTF-8")
#         while ("#" in mess) and ("!" in mess):
#             start = mess.find("!")
#             end = mess.find("#")
#             processData(client, mess[start:end + 1])
#             if (end == len(mess)):
#                 mess = ""
#             else:
#                 mess = mess[end+1:]
#     return CONNECTED

# proc_delay = ACTIVE_CYCLE
# delay_counter = proc_delay
# def startMeasure(client):
#     global state, proc_delay, delay_counter
#     if (state == CONNECTED):
#         print(delay_counter)
#         delay_counter -= 1
#         if (delay_counter <= 0): 
#             delay_counter = proc_delay
#             state = readSerial(client)
#         time.sleep(HOLD_TIME_LOCAL)
#     return state

# def setProcDelay(new_delay):
#     global proc_delay, delay_counter
#     if (new_delay < 5): new_delay = 5
#     proc_delay = new_delay
#     delay_counter = new_delay
#     return proc_delay

# def writeData(data):
#     ser.write(str(data).encode())

