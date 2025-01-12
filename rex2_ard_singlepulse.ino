//single pulse mazerex2 
const int pulse_width = 800; //in ms  
// inputs
const int in1 = 2;// FED3 outputs duplicated
const int in2 = 3;
const int in3 = 4;
const int in4 = 5;

//outputs
const int out1 = 38;//outputs to valve switch
const int out2 = 39;
const int out3 = 40;
const int out4 = 41;

//timers
const int start1=millis()
const int start2=millis()
const int start3=millis()
const int start4=millis()

//prevstate
const prev_in1=LOW;
const prev_in2=LOW;
const prev_in3=LOW;
const prev_in4=LOW;

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
  
  digitalWrite(out1, LOW);//init
  digitalWrite(out2, LOW);
  digitalWrite(out3, LOW);
  digitalWrite(out4, LOW);
}

void loop()
{
    prev_in1=digitalRead(in1);
    prev_in2=digitalRead(in2);
    prev_in3=digitalRead(in3);
    prev_in4=digitalRead(in4);

    if ((digitalRead(in1) == HIGH) && (prev_in1 == LOW)) //rising edge detected
    {
        digitalWrite(out1, HIGH);
        start1=millis()
    }
    if (millis()>start1+pulse_width) //pulse complete
    {
        digitalWrite(out1, LOW)
    }

    if ((digitalRead(in2) == HIGH) && (prev_in2 == LOW)) //rising edge detected
    {
        digitalWrite(out2, HIGH);
        start2=millis()
    }
    if (millis()>start2+pulse_width) //pulse complete
    {
        digitalWrite(out2, LOW)
    }
    
    if ((digitalRead(in3) == HIGH) && (prev_in3 == LOW)) //rising edge detected
    {
        digitalWrite(out3, HIGH);
        start3=millis()
    }
    if (millis()>start3+pulse_width) //pulse complete
    {
        digitalWrite(out3, LOW)
    }

    if ((digitalRead(in4) == HIGH) && (prev_in4 == LOW)) //rising edge detected
    {
        digitalWrite(out4, HIGH);
        start4=millis()
    }
    if (millis()>start4+pulse_width) //pulse complete
    {
        digitalWrite(out4, LOW)
    }
}//void loop end