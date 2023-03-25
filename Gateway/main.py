import time
from connectServer import*

time.sleep(5)

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
            if (state == DISCONNECTED or state == STARTUP):
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
            sys.exit(1)

    #Read data from sensor
    if (state == CONNECTED):
        state = readSerial(client)

    #Send cmd from sever to devices
    #Implement in function message
    
    pass