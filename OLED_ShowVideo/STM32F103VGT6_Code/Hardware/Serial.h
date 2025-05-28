#ifndef __SERIAL_H
#define __SERIAL_H
#include <stdio.h>
extern uint8_t Serial_TxPackage[4];
extern uint8_t Serial_RxPackage[4];
extern uint8_t oled_img[1024];
void Serial_Init(void);
void Serial_SendByte(uint8_t Byte);
void Serial_SendArray(uint8_t *Array, uint16_t Length);
void Serial_SendString(char *String);
void Serial_SendNumber(uint32_t Number);
void Serial_printf(char *format, ...);
uint8_t Serial_GetRxFlag(void);
void Serial_SendPackage(uint8_t *Package);
extern uint16_t NumRxData;
extern uint8_t oled_img_old[1024];
#endif
