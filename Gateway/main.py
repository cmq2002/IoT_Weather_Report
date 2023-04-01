from connectServer import*

time.sleep(HALT_TIME)


while True:
    # Confirm UART connection
    confirmUART(client)

    #Read data from sensor
    startMeasure(client)

    #Send cmd from sever to devices
    pass