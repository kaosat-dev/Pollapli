#include <EEPROM.h>

char deviceId[37];
char commandBuffer[64];
int commandIndex=0 ;
int temperature=0;

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

char* parseBaseCmd(char* cmd,int size)
{
  char baseCmd[size];
  
}


void  betterParse(char* command, int size)
{
   Command parsedCommand;
   int currentElementSize=0;
   int currentElement=0;
   
   char deviceId[64];
   
   int markers[64];
   int markerCount=0;
   
   int cmd;
   int pin;
   
   for(int i=0;i<size;i++)
   {
     if (markerCount==0)//we are building the command header
     {
        cmd=cmd*10+int(command[i])-48;
     }
     if (markerCount>0)//we are in the params portion
       {
          switch(cmd)
            {
              case 0://debug  test 
                Serial.println("hello python, arduino here");
                break;
              case 1://set device id  :special case    
                   EEPROM.write(i-markers[markerCount],command[i]);
              break;
              case 2://get device id
                send_id();
              break;
              case 'l'://setting pin low
                pin=get_pin(command,size);
                digitalWrite(pin, LOW);
                Serial.print(pin);
                Serial.println("ok");
              break;
              
              case 'h': //setting pin high
                pin=get_pin(command,size);
                digitalWrite(pin, HIGH);
                Serial.print(pin);
                Serial.println("ok");
              break;
              
              case 'a'://analog read
                pin=get_pin(command,size);
                Serial.println(analogRead(pin));
              break;
              
              default:
                Serial.print(command);
                Serial.println("ok");
               break;
            }  
       }
     
     if (command[i]==' ')
     {
       markers[markerCount]=i;
       markerCount++;
     }
   }
}
//pinMode(ledPin, OUTPUT);





void parse_command(char* command,int size)
{
  char cmd= command[0];
   switch(cmd)
    {
      
      case 'a'://debug  test 
        Serial.println("hello , arduino here");
        break;
      case 'b'://debug  test 2
       Serial.println("arduino here too");
        break;
      case 's':   //set device id  
        char payload[size-2];
        for (int i=2;i<size;i++)
        {
           payload[i-2]=command[i];
        }
        set_id(payload);
      break;
      case 'i'://get device id
        send_id();
      break;
      case 'g'://get data from sensor
        Serial.print(analogRead(0));
        Serial.println(" ok");
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

