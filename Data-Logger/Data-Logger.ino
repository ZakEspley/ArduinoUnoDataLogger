const int BUFSIZE = 6*170;
static byte buf[BUFSIZE];
unsigned int data;
unsigned long t;
volatile int i=0;
byte control;
int rate = 8000;

//volatile bool buffselect;

void setup() {
  // put your setup code here, to run once:
  cli();
  ADCSRA |= 1 << ADPS2;
  ADCSRA &= ~(1 << ADPS1);
  ADCSRA &= ~(1 << ADPS0);
  ADMUX |= 1 << REFS0;
  ADMUX |= 1 << MUX0;
  ADMUX |= 1 << ADLAR;
  ADCSRA |= 1 << ADEN;
  ADCSRA |= 1 << ADIE;
  sei();
  Serial.begin(2000000);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    control = Serial.read();
  }

  if (control == '1') {
    ADCSRA |= 1 << ADATE;
    ADCSRA |= 1 << ADSC;
    control = 5;
  }

  if (control == '0') {
    ADCSRA &= ~(1 << ADATE);
    ADCSRA &= ~(1 << ADSC);
  }

  if (control == '3') {
    ADCSRA &= ~(1 << ADATE);
    ADCSRA &= ~(1 << ADSC);
    ADCSRA &= ~(1 << ADPS2);
    ADCSRA &= ~(1 << ADPS1);
    ADCSRA &= ~(1 << ADPS0);
    while (Serial.available() == 0) {
    }
//    delay(100);
    byte rate1 = Serial.read();
    ADCSRA |= rate1;
//    Serial.print("Rate is ");
//    Serial.println(1000000/rate);
    control = 5;
  }
  

}

ISR(ADC_vect) {
//  t = micros();
//  buf[i] = ADCL;
//  buf[i+1] = ADCH;
   buf[i] = ADCH;
//  buf[i+2] = t;
//  buf[i+3] = (t >> 8);
//  buf[i+4] = (t >> 16);
//  buf[i+5] = (t>>24);
  
//  i = i+6;
//   i = i+2;
  i++;

//  delayMicroseconds(1000000/rate);
  
  if (i == BUFSIZE) {
//      Serial.println("BUF1");
//      Serial.println(i);
//      Serial.println(buf1[0]*256+buf1[1]);
//      Serial.println((buf1[2] + buf1[3]*256 + pow(buf1[4]*256,2) + pow(buf1[5]*256,3))/1000000);
    Serial.write(buf, BUFSIZE);
    i=0;
  }
}

