//single pulse mazerex2 
unsigned long pulse_width = 300; //in ms  
// inputs
const int in1 = 2;// FED3 outputs duplicated
const int in2 = 3;
const int in3 = 4;
const int in4 = 5;

const int authorize_puff=13;

const int auth1=A0;
const int auth2=A1;
const int auth3=A2;
const int auth4=A3;

//outputs
const int out1 = 6;//outputs to valve switch
const int out2 = 7;
const int out3 = 8;
const int out4 = 9;

//timers
unsigned long start1=millis();
unsigned long start2=millis();
unsigned long start3=millis();
unsigned long start4=millis();

//prevstate
bool prev_in1=LOW;
bool prev_in2=LOW;
bool prev_in3=LOW;
bool prev_in4=LOW;

//puffstate
bool puff1=LOW;
bool puff2=LOW;
bool puff3=LOW;
bool puff4=LOW;

//probabilistic puffs
bool chance=LOW;

void setup()
{
  pinMode(in1, INPUT);
  pinMode(in2, INPUT);
  pinMode(in3, INPUT);
  pinMode(in4, INPUT);
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);  
  pinMode(out3, OUTPUT); 
  pinMode(out4, OUTPUT);
  
  pinMode(authorize_puff, INPUT);

  pinMode(auth1, INPUT);
  pinMode(auth2, INPUT);
  pinMode(auth3, INPUT);
  pinMode(auth4, INPUT);
  
  digitalWrite(out1, HIGH);//init
  digitalWrite(out2, HIGH);
  digitalWrite(out3, HIGH);
  digitalWrite(out4, HIGH);
  //Serial.begin(9600);
}

void loop()
{
  prev_in1=digitalRead(in1);
  prev_in2=digitalRead(in2);
  prev_in3=digitalRead(in3);
  prev_in4=digitalRead(in4);

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
    if ((digitalRead(in3) == HIGH) && (prev_in3 == LOW) && (chance == HIGH)) //rising edge detected
    {
        digitalWrite(out3, LOW);
        start3=millis();
        puff3=HIGH;
    }
    if ((digitalRead(in4) == HIGH) && (prev_in4 == LOW) && (chance == HIGH)) //rising edge detected
    {
        digitalWrite(out4, LOW);
        start4=millis();
        puff4=HIGH;
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

  if (puff3 == HIGH)
  {
    if(millis()>start3+pulse_width) //pulse complete
    {
        digitalWrite(out3, HIGH);
        puff3=LOW;
    }
  }

  if (puff4 == HIGH)
  {
    if(millis()>start4+pulse_width) //pulse complete
    {
        digitalWrite(out4, HIGH);
        puff4=LOW;
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
  if (digitalRead(auth3) == HIGH)
  {
    if ((digitalRead(in3) == HIGH) && (prev_in3 == LOW)) //rising edge detected
    {digitalWrite(out3, LOW);start3=millis();puff3=HIGH;}
  }
  if (digitalRead(auth4) == HIGH)
  {
    if ((digitalRead(in4) == HIGH) && (prev_in4 == LOW)) //rising edge detected
    {digitalWrite(out4, LOW);start4=millis();puff4=HIGH;}
  }
}//void loop end
