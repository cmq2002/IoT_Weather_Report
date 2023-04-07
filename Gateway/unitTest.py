import unittest
from unittest.mock import MagicMock
from uart import* 
from connectServer import*

class TestUART(unittest.TestCase):
    def test_getPort(self):
        # Mock the os.listdir method to return some mock data
        os_listdir = MagicMock(return_value=['COM5', 'COM6'])

        # Call the getPort function with the mocked functions
        result = getPort()

        # Check that the os.listdir method was called once with the correct argument
        # os_listdir.assert_called_once_with('/dev')

        # Check that the result is equal to the first item in the mock data
        self.assertEqual(result, 'COM5')

    def test_confirmUART(self):
        # Mock the openUART function to return CONNECTED
        openUART = MagicMock(return_value=CONNECTED)

        # Mock the time.sleep function to do nothing
        time_sleep = MagicMock()

        # Mock the client.publish function to do nothing
        client_publish = MagicMock()

        # Call the confirmUART function with the mocked functions
        state = DISCONNECTED
        connection_attemp = 0
        counter = 0
        MAX_CONNECTION_ATTEMP = 3
        HOLD_TIME_LOCAL = 0
        TIMEOUT = 1
        result = confirmUART(client)

        # Check that the openUART function was called once
        # openUART.assert_called_once()

        # Check that the time.sleep function was called once with HOLD_TIME_LOCAL
        # time_sleep.assert_called_once_with(HOLD_TIME_LOCAL)

        # Check that the client.publish function was not called
        # client_publish.assert_not_called()

        # Check that the result is CONNECTED
        self.assertEqual(result, CONNECTED)

    def test_openUART(self):
        # Mock the serial.Serial constructor to return a mock object
        serial.Serial = MagicMock(return_value=MagicMock())

        # Call the openUART function with the mocked functions
        result = openUART(client)

        # Check that the serial.Serial constructor was called once with the correct arguments
        serial.Serial.assert_called_once_with(port='COM5', baudrate=9600)

        # Check that the result is not None
        self.assertIsNotNone(result)
    
    def test_confirmDataIntegrity(self):
        # Test data with correct checksum
        data1 = "!TEMP:27.0:635#"
        result1 = confirmDataIntegrity(data1)
        self.assertTrue(result1)

        # Test data with incorrect checksum
        data2 = "!TEMP:27.0:636#"
        result2 = confirmDataIntegrity(data2)
        self.assertFalse(result2)
   
    def test_processData(self):
        # Mock the client.publish function to do nothing
        client_publish = MagicMock()

        # Call the processData function with the mocked functions
        client = MagicMock()
        data = "!TEMP:27.0:635#"
        result = processData(client, data)

        # Check that the client.publish function was called once with the correct arguments
        # client_publish.assert_called_once_with("sensor1", "27.0")

        # Check that the result is None
        self.assertIsNone(result)
    
    # def test_readSerial(self):
    #     # Mock the serial.Serial.readline method to return some mock data
    #     serial_readline = MagicMock(return_value=b'!TEMP:27.0:635#\n')

    #     # Call the readSerial function with the mocked functions
    #     global ser
    #     ser = MagicMock()
    #     result = readSerial(client)

    #     # Check that the serial.Serial.readline method was called once
    #     ser.readline.assert_called_once()

    #     # Check that the result is equal to the mock data
    #     self.assertEqual(result, "!TEMP:27.0:635#")  
    
    def test_startMeasure(self):
        # Mock the readSerial function to return CONNECTED
        readSerial = MagicMock(return_value=CONNECTED)

        # Mock the time.sleep function to do nothing
        time_sleep = MagicMock()

        # Call the startMeasure function with the mocked functions
        client = MagicMock()
        global state, proc_delay, delay_counter
        state = CONNECTED
        proc_delay = 5
        delay_counter = 5
        result = startMeasure(client)

        # Check that the readSerial function was called once
        # readSerial.assert_called_once()

        # Check that the time.sleep function was called once with HOLD_TIME_LOCAL
        # time_sleep.assert_called_once_with(HOLD_TIME_LOCAL)

        # Check that the result is CONNECTED
        self.assertEqual(result, CONNECTED)
    
    def test_setProcDelay(self):
        # Test with valid input
        delay1 = 5
        result1 = setProcDelay(delay1)
        self.assertEqual(result1, delay1)

        # Test with invalid input
        delay2 = -1
        result2 = setProcDelay(delay2)
        self.assertEqual(result2, delay1)
    
    def test_writeData(self):
        # Mock the serial.Serial.write method to do nothing
        serial_write = MagicMock()

        # Call the writeData function with the mocked functions
        client = MagicMock()
        global ser
        ser = MagicMock()
        result = writeData("@ON1*")

        # Check that the serial.Serial.write method was called once with the correct arguments
        # serial_write.assert_called_once_with(b'@ON1*')

        # Check that the result is None
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()