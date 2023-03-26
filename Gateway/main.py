from connectServer import*
from uart import*
import time

time.sleep(HALT_TIME)

state = STARTUP
connection_attemp = 0
counter = TIMEOUT
while True:
    #1-hop error control: Confirm UART connection
    if (state == DISCONNECTED or state == STARTUP):
        while(connection_attemp < MAX_CONNECTION_ATTEMP and state != CONNECTED):
            if (counter == TIMEOUT):
                print("Connection Attemps: " + str(connection_attemp + 1))
                state = openUART(client)
            if (state == DISCONNECTED):
                counter -= 1
                if (counter <=0):
                    connection_attemp += 1
                    counter = TIMEOUT
                time.sleep(1)
            else:
                connection_attemp = 0

        if connection_attemp == MAX_CONNECTION_ATTEMP:
            print("Reach Max Attemp...")
            client.publish("error-detect", "Reach Max Attemp...")
            disconnected(client)

    #Read data from sensor
    if (state == CONNECTED):
        state = readSerial(client)

    #Send cmd from sever to devices
    #Implement in function message
    pass