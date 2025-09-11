#include <Servo.h>
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
unsigned long interval=1000;//millisec wait time for flap to drop past sensor 
unsigned long timer1=millis();
unsigned long timer2=millis();
unsigned long timer3=millis();
unsigned long timer4=millis();
const int servoPin1 = 9;// nano pwm 3 5 6 9 10 11
const int servoPin2 = 10;
const int servoPin3 = 5;// nano pwm 3 5 6 9 10 11
const int servoPin4 = 6;
//door angles
const int CLOSE1= 20;
const int OPEN1= 70;
const int CLOSE2= 170;
const int OPEN2= 120;
const int CLOSE4= 10;
const int OPEN4= 50;
const int CLOSE3= 170;
const int OPEN3= 120;
int target1=CLOSE1;
int target2=CLOSE2;
int target3=CLOSE3;
int target4=CLOSE4;
bool move1=true;
bool move2=true;
bool move3=true;
bool move4=true;
bool delay_flag1=true;
bool delay_flag2=true;
bool delay_flag3=true;
bool delay_flag4=true;
const int proxPin1 = 11; //proximity sensor for flap1
const int proxPin2 = 12;
char receivedChar;

void setup() {
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);
  Serial.begin(9600);//setup serial
  pinMode(proxPin1, INPUT);
  pinMode(proxPin2, INPUT);
}

void loop() {
  recvInfo();
  moveServo();
}

void recvInfo() {
  if (Serial.available()>0)
  {
    receivedChar = Serial.read();
    if (receivedChar=='a')
    {
      target1=OPEN1;move1=true;delay_flag1=true;
      target2=OPEN2;move2=true;delay_flag2=true;
    }
    if (receivedChar=='b')
    {
      target1=CLOSE1;move1=true;delay_flag1=true;
    }
    if (receivedChar=='c')
    {
      target2=CLOSE2;move2=true;delay_flag2=true;
    }
    if (receivedChar=='d')
    {
      target3=OPEN3;move3=true;delay_flag3=true;
      target4=OPEN4;move4=true;delay_flag4=true;
    }
    if (receivedChar=='e')
    {
      target3=CLOSE3;move3=true;delay_flag3=true;
    }
    if (receivedChar=='f')
    {
      target4=CLOSE4;move4=true;delay_flag4=true;
    }
  }
}

void moveServo() {
  if ((move1) && (delay_flag1) && (digitalRead(proxPin1)==LOW)){timer1=millis();delay_flag1=true;}
  if ((move2) && (delay_flag2) && (digitalRead(proxPin2)==LOW)){timer2=millis();delay_flag2=true;}
  if ((move1) && (delay_flag1) && (digitalRead(proxPin1)==HIGH)){timer1=millis();delay_flag1=false;}
  if ((move2) && (delay_flag2) && (digitalRead(proxPin2)==HIGH)){timer2=millis();delay_flag2=false;}
  if ((move1) && (!delay_flag1) && (timer1+interval<millis()) && (digitalRead(proxPin1)==HIGH)){servo1.write(target1);move1=false;}
  if ((move2) && (!delay_flag2) && (timer2+interval<millis()) && (digitalRead(proxPin2)==HIGH)){servo2.write(target2);move2=false;}
  

  if ((move3) && (delay_flag3)){timer3=millis();delay_flag3=false;}
  if ((move4) && (delay_flag4)){timer4=millis();delay_flag4=false;}
  if ((move3) && (!delay_flag3) && (timer3+interval<millis())){servo3.write(target3);move3=false;}
  if ((move4) && (!delay_flag4) && (timer4+interval<millis())){servo4.write(target4);move4=false;}
}
