#include "stm32f10x.h"                  // Device header
#include "Delay.h"
#include "OLED.h"
#include "Serial.h"
#include "Key.h"
uint8_t transmit_complete = 0;

int main(void)
{
	OLED_Init();
	Serial_Init();
	OLED_ShowString(1, 1, "ciallo!!!");
	OLED_SetCursor(0, 0);
	while (1) 
	{
		if (Serial_GetRxFlag())
		{
			for (uint16_t i = 0; i < 8; i++) 
			{
				OLED_SetCursor(i, 0);
				for (uint16_t j = 0; j < 128; j++)
				OLED_WriteData(oled_img[i * 128 +j]);
			}
		}
	}
}
