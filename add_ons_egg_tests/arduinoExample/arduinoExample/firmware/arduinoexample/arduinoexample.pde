#include <EEPROM.h>

char deviceId[37];
char commandBuffer[64];
int commandIndex=0 ;

void setup()
{
   Serial.begin(115200);
   get_id();
   //reset_id();
  Serial.println("start");   
}

void set_id(char* id)
{
  for (int i=0; i<36; i++) 
  {
    EEPROM.write(i,id[i]);
    deviceId[i]=id[i];
  }
  send_id();
}

void reset_id()
{
    for (int i=0; i<36; i++) 
  {
    EEPROM.write(i,' ');
    deviceId[i]=' ';
  } 
}
void get_id()
{ 
  for (int i=0; i<36; i++) 
  {
     deviceId[i] = EEPROM.read(i);
  }
}

void send_id()
{
   Serial.println(deviceId); 
}

void parse_command(char* command,int size)
{
  char cmd= command[0];
   switch(cmd)
    {
      case 'a':
        Serial.println("hello , arduino here");
        break;
      case 'b':
       Serial.println("arduino here too");
        break;
      case 's':
       
        char payload[size-2];
        for (int i=2;i<size;i++)
        {
           payload[i-2]=command[i];
        }
        set_id(payload);
      break;
      case 'i':
        send_id();
      break;
      default:
        Serial.print(command);
        Serial.println("ok");
       break;
    }  
  
}
void loop()
{
  
  if(Serial.available()>0)
  {
     char c=Serial.read();
    if((c == 10) || (c == 13))
    {
      parse_command(commandBuffer,commandIndex);
      for (int i=0;i<commandIndex;i++)
      {
        commandBuffer[i]=' ';
      }
      commandIndex=0;
    }
    else
    {
      commandBuffer[commandIndex]=c;
      commandIndex++;
     
    }
  }
    
}

