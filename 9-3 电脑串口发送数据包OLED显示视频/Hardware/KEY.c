#include "stm32f10x.h"                  // Device header
#include "Delay.h"
uint16_t KEY_Pin_1 = GPIO_Pin_0;
uint16_t KEY_Pin_2 = GPIO_Pin_11;
void KEY_Init(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPD;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOB, &GPIO_InitStructure);
}

unsigned char GetKEYNum(void)
{
	unsigned char KEYNum=0;
	if (GPIO_ReadInputDataBit(GPIOB,KEY_Pin_1)==1){
		Delay_ms(20);
		while (GPIO_ReadInputDataBit(GPIOB,KEY_Pin_1)==1);
		Delay_ms(20);
		KEYNum=1;
	}
	if (GPIO_ReadInputDataBit(GPIOB,KEY_Pin_2)==0){
		Delay_ms(20);
		while (GPIO_ReadInputDataBit(GPIOB,KEY_Pin_2)==0);
		Delay_ms(20);
		KEYNum=2;
	}
	return KEYNum;
}

