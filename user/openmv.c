/*视频教程链接 https://www.bilibili.com/video/BV1UL411V7XK?p=2&share_source=copy_web   昵称：海喂喂喂*/

#include "openmv.h"
#include "stm32f1xx.h"
#include "stdio.h"
#include "usart.h"
#include "bsp_led.h"
#include "adc.h"
#include "bsp_sys.h"

int GetOpenmvDataCount  = 0;
uint8_t  Num=0, LoR =0, Finded_flag = 0, FindTask = 0;     //()
u8 LastNum;
u8 NumCount = 0;

u8 sendBuf[4];

uint8_t uart3_rxbuff;

u8 RoomNum, TargetNum;
u8 TASK=1;    //这个TASK可以传输给openmv，赋值openmv上的FindTask来控制openmv模板匹配的不同模式


char TargetRoom = 0;  //A, B, C, D, E, F, G, H;    //这八个字符对应着地图实际房间，里面的数字3—8会随机对应C-H

u8 FindStartFlag;
u16 FindTimeCount;


void Openmv_Receive_Data(uint8_t com_data)
{
		uint8_t i;
		static uint8_t RxCounter1=0;//计数
		static uint16_t RxBuffer1[10]={0};
		static uint8_t RxState = 0;	
		static uint8_t RxFlag1 = 0;

		if(RxState==0&&com_data==0x2C)  //0x2c帧头
		{
			
			RxState=1;
			RxBuffer1[RxCounter1++]=com_data;  
		}

		else if(RxState==1&&com_data==0x12)  //0x12帧头
		{
			RxState=2;
			RxBuffer1[RxCounter1++]=com_data;
		}
		
		else if(RxState==2)
		{
			 
			RxBuffer1[RxCounter1++]=com_data;
			if(RxCounter1>=10||com_data == 0x5B)       //RxBuffer1接受满了,接收数据结束
			{
				RxState=3;
				RxFlag1=1;
				
				 //正常情况下,运行到这RxCounter1 == 7？  7-5 = 2    openmv发送过来的一个数据包有8个
				Num =          RxBuffer1[RxCounter1-5]; 
				LoR =          RxBuffer1[RxCounter1-4];     //-1是左， 1是右，0表示还没有识别到任何数字
				Finded_flag =  RxBuffer1[RxCounter1-3];
				FindTask =      RxBuffer1[RxCounter1-2];
				
				//RxCounter1-1是帧尾
				
				//greenLED_Toggle;    //用来看是否接收数据的,电平翻转一次则成功接收一个数据，跟下面的一个意思
		  	GetOpenmvDataCount++;      
				//用来看1秒内成功解码多少个数据包的 需要在1s钟的延时中清除，帧率越高越准确，个位数的话偏差就大了
				//不如改一下解码代码，将openmv那里的帧率直接传过来
				
			}
		}

		else if(RxState==3)		//检测是否接受到结束标志
		{
				if(RxBuffer1[RxCounter1-1] == 0x5B)
				{
							
							RxFlag1 = 0;
							RxCounter1 = 0;
							RxState = 0;
						
				}
				else   //接收错误
				{
							RxState = 0;
							RxCounter1=0;
							for(i=0;i<10;i++)
							{
									RxBuffer1[i]=0x00;      //将存放数据数组清零
							}
				}
		} 

		else   //接收异常
		{
				RxState = 0;
				RxCounter1=0;
				for(i=0;i<10;i++)
				{
						RxBuffer1[i]=0x00;      //将存放数据数组清零
				}
		}
}



void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  uint8_t tem;// 这里的是无符号的
	
	//RedSignal_Toggle;   //用来看是否接收数据的, 这里要随时都没效果的话就代表连串口3的中断都没进来
  if(huart->Instance== USART3)     //这里只能这样大写USART3
  {
		   
		//RedSignal_Toggle;   //用来看是否接收数据的, 这里要随时都没效果的话就代表连串口3的中断都没进来
		
    tem=uart3_rxbuff;
    Openmv_Receive_Data(tem);
		
  }	
   HAL_UART_Receive_IT(&huart3,&uart3_rxbuff,1); 
}



void SendDataToOpenmv(void)
{
	u8 i;
	//加上发送给openmv 的数据的代码 (帧头， 模板匹配模式选择标志位，模式2所需要匹配的数字，帧尾)   //不需要很高的发送频率
		
		
		for(i = 0; i <= 4; i++)   //将TASK和TargetNum打包一次性发送给openmv
		{
			sprintf((char *)sendBuf, "*%d%d&", TASK, TargetNum);    
				HAL_UART_Transmit(&huart3, sendBuf, sizeof(sendBuf), 1000);
			 // greenLED_on;
		}
		//greenLED_off;
}


//等待openmv识别指定数字,并设置目标房间。 只有在复位后
void SetTargetRoom(void)
{
		//查寻目标病房号的缓冲区数据，跳转任务开始函数   //重启后第一次从openmv传来的数字即为目标房号
		/*一开始识别目标房间号*/  
		if(Finded_flag == 1)
		{
			/**滤波**/ //可以但没必要
//			if(NumCount == 0)   
//			{
//				LastNum = Num;
//			}
//			
//			else if(NumCount >= 2)  //至少连续两次一样的，才判断为识别到
//			{
//				if(LastNum == Num)
//				{
//					RoomNum = Num;    //有必要用多一个变量吗？要滤波才有必要,否则直接用Num就行
//					LastNum = 0;
//					NumCount = 0;
//				}
//				
//			}
//			NumCount++;
			 RoomNum = Num;
			
		}
		
		
		else if(Finded_flag == 0)
		{
			RoomNum = 0;   
			LastNum = 0;
			NumCount = 0;
		}
	
		
	 if(RoomNum ==  1) 
	 {
		 TargetRoom = 'A';
		 TASK = 2;   
	 }
	 else if(RoomNum == 2)
	 {
		 TargetRoom = 'B';
		 TASK = 2;  
			
	 }
	 else if(RoomNum >= 3)  //不能else if(3 <= Num <= 8)
	 {
		 TargetRoom = 'G';
		 TASK = 2;  
	 }
	 
   switch(RoomNum)
		{
			case 1:
				TargetNum = 1;
			break;
			
			case 2:
				TargetNum = 2;
			break;
			
			case 3:
				TargetNum = 3;
			break;
			
			case 4:
				TargetNum = 4;
			break;
			
			case 5:
				TargetNum = 5;
			break;
			
			case 6:
				TargetNum = 6;
			break;

			case 7:
				TargetNum = 7;
			break;
			
			case 8:
				TargetNum = 8;
			break;	 		
		}
	 //识别到的数字是3-8， 默认先给  TargetRoom = RoomH
	 //根据openmv识别到的数据,在送药的函数里面进行目标值的实时更改
}
