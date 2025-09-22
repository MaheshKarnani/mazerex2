//autolindz2
#include <Servo.h>
Servo servo1;
Servo servo2;
const int servoPin1 = 11;// nano pwm 3 5 6 9 10 11
const int servoPin2 = 10;
//door angles
const int CLOSE1= 190;
const int OPEN1= 150;
const int CLOSE2= 10;
const int OPEN2= 50;
int target1=CLOSE1;
int target2=CLOSE2;
bool move1=true;
bool move2=true;
const int proxPin1 = A4; //proximity sensor for flap1
const int proxPin2 = A5;
char receivedChar;

//single pulse mazerex2 
unsigned long pulse_width = 300; //in ms  
// inputs
const int in1 = 2;// FED3 outputs duplicated
const int in2 = 3;

const int authorize_puff=13;

const int auth1=A0;
const int auth2=A1;

//outputs
const int out1 = 6;//outputs to valve switch
const int out2 = 7;

//timers
unsigned long start1=millis();
unsigned long start2=millis();

//prevstate
bool prev_in1=LOW;
bool prev_in2=LOW;

//puffstate
bool puff1=LOW;
bool puff2=LOW;

//probabilistic puffs
bool chance=LOW;

void setup()
{
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  Serial.begin(9600);//setup serial
  pinMode(proxPin1, INPUT);
  pinMode(proxPin2, INPUT);
  
  pinMode(in1, INPUT);
  pinMode(in2, INPUT);
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT); 
  
  pinMode(authorize_puff, INPUT);

  pinMode(auth1, INPUT);
  pinMode(auth2, INPUT);
  
  digitalWrite(out1, HIGH);//init
  digitalWrite(out2, HIGH);
}

void loop() {
  recvInfo();
  moveServo();
  rex();
}
void recvInfo() {
  if (Serial.available()>0)
  {
    receivedChar = Serial.read();
    if (receivedChar=='a')
    {
      servo1.write(OPEN1);move1=false;
      servo2.write(OPEN2);move2=false;
    }
    if (receivedChar=='b')
    {
      target1=CLOSE1;move1=true;
    }
    if (receivedChar=='c')
    {
      target2=CLOSE2;move2=true;
    }
  }
}

void moveServo() {
  if ((move1) && (digitalRead(proxPin1)==LOW)){servo1.write(target1);move1=false;}
  if ((move2) && (digitalRead(proxPin2)==LOW)){servo2.write(target2);move2=false;}
}

void rex() {
  prev_in1=digitalRead(in1);
  prev_in2=digitalRead(in2);

  chance=random(0,2);
  //Serial.println(chance);
  if (digitalRead(authorize_puff) == HIGH)
  {
    if ((digitalRead(in1) == HIGH) && (prev_in1 == LOW) && (chance == HIGH)) //rising edge detected
    {
        digitalWrite(out1, LOW);
        start1=millis();
        puff1=HIGH;
    }
    if ((digitalRead(in2) == HIGH) && (prev_in2 == LOW) && (chance == HIGH)) //rising edge detected
    {
        digitalWrite(out2, LOW);
        start2=millis();
        puff2=HIGH;
    }
  }

  //turn puffs off when duration elapsed
  if (puff1 == HIGH)
  {
    if(millis()>start1+pulse_width) //pulse complete
    {
        digitalWrite(out1, HIGH);
        puff1=LOW;
    }
  }

  if (puff2 == HIGH)
  {
    if(millis()>start2+pulse_width) //pulse complete
    {
        digitalWrite(out2, HIGH);
        puff2=LOW;
    }
  }

  //reminder puffs 100% likelihood if RPi commands
  if (digitalRead(auth1) == HIGH)
  {
    if ((digitalRead(in1) == HIGH) && (prev_in1 == LOW)) //rising edge detected
    {digitalWrite(out1, LOW);start1=millis();puff1=HIGH;}
  }
  if (digitalRead(auth2) == HIGH)
  {
    if ((digitalRead(in2) == HIGH) && (prev_in2 == LOW)) //rising edge detected
    {digitalWrite(out2, LOW);start2=millis();puff2=HIGH;}
  }
}
