/*
 * led_display.c
 *
 *  Created on: Mar 24, 2023
 *      Author: acer
 */

#include "led_display.h"

void turnLedOn(void){
	HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, RESET);
}

void turnLedOff(void){
	HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, SET);
}

void toggleLed(void){
	HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
}
