/*
 * uart_reading.c
 *
 *  Created on: Dec 22, 2022
 *      Author: acer
 */

#include "uart_reading.h"

extern UART_HandleTypeDef huart2;

extern I2C_HandleTypeDef hi2c1;

//Globally use in main to take input
uint8_t buffer_byte;
uint8_t buffer[MAX_BUFFER_SIZE];
uint8_t index_buffer = 0;
uint8_t buffer_flag = 0;

//Locally use in uart_reading
uint8_t cmdParserStatus = INIT_UART;
uint8_t cmd_data[MAX_CMD_SIZE];
uint8_t cmd_index = 0;
uint8_t buffer_idx = 0;
uint8_t cmd_flag = INIT_UART;
uint8_t counter = WAIT;

void rst_buffer(){
	for(int i=0; i<MAX_BUFFER_SIZE; i++)
		buffer[i] = ' ';
}

void rst_cmd(){
	for(int i=0; i<MAX_CMD_SIZE; i++)
		cmd_data[i] = ' ';
}

void cleanUp(){
	index_buffer = 0;
	cmd_index = 0;
	buffer_idx = 0;
	rst_buffer();
	rst_cmd();
}

void cmd_parser_fsm(){
	switch(cmdParserStatus){
		case INIT_UART:
			if (buffer[buffer_idx] == '@'){
				cmdParserStatus = READING;
				buffer_idx++;
			}
			break;
		case READING:
			if (buffer[buffer_idx] != '@' && buffer[buffer_idx] != '*'){
				cmd_data[cmd_index] = buffer[buffer_idx];
				cmd_index++;
				buffer_idx++;
			}
			else if (buffer[buffer_idx] == '@'){
				cmdParserStatus = READING;
				buffer_idx++;
			}
			else if (buffer[buffer_idx] == '*'){
				if (cmd_data[0] == 'R') cmd_flag = isRST;
				else if (cmd_data[0] == 'C') cmd_flag = isCAP;
				cmdParserStatus = INIT_UART;
				cleanUp();
			}
			break;
		default:
			break;
	}
}

//Using Scheduler to synchronize
void counter10s(){
	counter--;
}

void groupAction(){
	turnLedOn();
	dht20_output();
}

//void uart_control_fsm()
//{
//	switch (cmd_flag){
//		case INIT_UART:
//			cmd_flag = AUTO;
//			break;
//		case AUTO:
//			SCH_Add_Task(turnLedOff, 0, 300);
//			SCH_Add_Task(groupAction, 299, 300);
//			break;
//		case isCAP:
//			SCH_Add_Task(turnLedOn, 0, 0);
//			SCH_Add_Task(counter10s, 0, 0);
//			if (counter <= 0) cmd_flag = INIT_UART;
//			break;
//		case isRST:
//			counter = WAIT;
//			cmd_flag = INIT_UART;
//			break;
//		default:
//			break;
//	}
//}

//User timer to synchronize
void uart_control_fsm()
{
	switch (cmd_flag){
		case INIT_UART:
			cmd_flag = AUTO;
			setTimer2(1);
			break;
		case AUTO:
			if (timer2_flag == 1){
				turnLedOn();
				dht20_output();
				setTimer2(1000);
			}
			turnLedOff();
			break;
		case isCAP:
			setTimer3(1000);
			cmd_flag = WAIT;
			turnLedOn();
			break;
		case WAIT:
			turnLedOn();
			if (timer3_flag == 1) cmd_flag = INIT_UART;
			break;
		case isRST:
			cmd_flag = INIT_UART;
			break;
		default:
			break;
	}
}

uint32_t msgCheckSum(char* msg, uint32_t msgLen){
	uint32_t result = 0;
	for(int i=0; i<msgLen; i++){
		result += msg[i];
	}
	return result;
}

void Scan_Addr() {
    char info[] = "\r\n\r\nScanning I2C bus...\r\n";
    HAL_UART_Transmit(&huart2, (uint8_t*)info, strlen(info), HAL_MAX_DELAY);

    HAL_StatusTypeDef res;
    uint8_t device_counter = 0;
    for(uint16_t i = 0; i < 128; i++) {
        res = HAL_I2C_IsDeviceReady(&hi2c1, i << 1, 1, 10);
        if(res == HAL_OK) {
        	device_counter += 1;
            char msg[64];
            snprintf(msg, sizeof(msg), "0x%02X", i);
            HAL_UART_Transmit(&huart2, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
        }
        else {
            HAL_UART_Transmit(&huart2, (uint8_t*)".", 1, HAL_MAX_DELAY);
        }
    }

    if (device_counter == 0){
    	char msg[64] = "!ERROR:Sensor Not Found...#";
    	uint32_t checkSum = msgCheckSum(&msg[0], strlen(msg));
    	sprintf(msg, "!ERROR:Sensor Not Found...:%lu#", checkSum);
    	HAL_UART_Transmit(&huart2, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
    }
}

void Mcu_info(){
	char msg[64];
	uint32_t checkSum = msgCheckSum(&msg[0], sprintf(msg, "!INFO:MCU_VERSION-%s,FIRWARE_VERSION-%s#", MCU_VERSION, FIRMWARE_VERSION));
	sprintf(msg, "!INFO:MCU VERSION %s, FIRWARE VERSION %s:%lu#", MCU_VERSION, FIRMWARE_VERSION, checkSum);
	HAL_UART_Transmit(&huart2, (uint8_t*)msg, strlen(msg), 1000);
}
