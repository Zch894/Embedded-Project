#include "stm32f10x.h"                  // Device header
#include "Delay.h"
#include "OLED.h"
#include "Serial.h"
#include "Key.h"
#include "DMA.h"


int main(void)
{
	OLED_Init();
	Serial_Init();
	MyDMA_Init(oled_img);
	OLED_ShowString(1, 1, "ciallo!!!");
	OLED_SetCursor(0, 0);
	while (1) 
	{
		if (Serial_GetRxFlag())
		{
			for (uint16_t i = NumRxData - 128; i < NumRxData; i++) OLED_WriteData(oled_img[i]);
			OLED_SetCursor(NumRxData / 128, 0);
		}
	}
}
