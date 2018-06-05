//#include <Filters.h>
const int BUFSIZE = 1000;
volatile int SENDSIZE = 27;
static byte buf[BUFSIZE];
unsigned int data;
unsigned long t, t0;
volatile int j=0;
volatile int i=0;
byte control = 99;
int rate = 8000;
float cutoff = 5.0;
volatile bool lpfilter = false;
volatile bool collecting = false;
//FilterOnePole lowpassFilter(LOWPASS, cutoff);

//volatile bool buffselect;

void setup() {
  // put your setup code here, to run once:
  cli();
  //Set Pre-Scalar for ADC to 16
  ADCSRA |= (1 << ADPS2);
  ADCSRA &= ~(1 << ADPS1);
  ADCSRA &= ~(1 << ADPS0);

  //Select the reference voltage
//  ADMUX &= ~(1 << REFS1);
  ADMUX &= ~(1 << REFS0);

  //Select the Analog input
  ADMUX |= 1 << MUX1;
  //Select the bit order
  ADMUX |= 1 << ADLAR;
  
  //Turn on ADC
  ADCSRA |= 1 << ADEN;
  //Allow for ADC interupts
  ADCSRA |= 1 << ADIE;
   //Turn on AutoTrigger for the ADC
  ADCSRA |= 1 << ADATE;
  //Select Auto-Trigger source to be Compare Match B of Timer 1
  ADCSRB |= 101 << ADTS0;
  
  //Setup Timer 1

  //Initialize as zeros
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  //Select the reset time of trigger. 16bit int
  //[16MHz/(2*TimerPrescaler*SampleRate) - 1]/2
  //OCR1A must match OCR1B
  OCR1A = 6249;
  OCR1B = 6249;

  //Setting WGM12 to 1 and WGM10-11 to zero activates
  //Clear Timer on Compare Match B
  //Where the TOP is given in OCR1A
  TCCR1B |= 1 << WGM12;
  
  //Set COM1B1 To 1 Clears OCiB on Compare Match
  TCCR1A |= 1 << COM1B1;

  ADCSRA |= 1 << ADSC;

  //CS10-12 Sets the prescalar for the timer. 000=Time Off
  // 001 Prescaler = 1
  // 010 Prescaler = 8
  // 011 Prescaler = 64
  // 100 Prescaler = 256
  // 101 Prescaler = 1024
  TCCR1B &= ~(1 << CS12);
  TCCR1B |= (1 << CS11);
  TCCR1B &= ~(1 << CS10);
  
  sei();
  Serial.begin(2000000);
//  Serial.begin(250000);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    control = Serial.read();
  }

  if (control == '1') {
    ADCSRA |= 1 << ADATE;
    ADCSRB |= 101 << ADTS0;
    ADCSRA |= 1 << ADSC;
    
    control = 99;
  }

  if (control == '0') {
    ADCSRA &= ~(1 << ADATE);
    ADCSRA &= ~(1 << ADSC);
    control = 99;
  }

  if (control == '3') {
//    ADCSRA &= ~(1 << ADATE);
//    ADCSRA &= ~(1 << ADSC);
//    ADCSRA &= ~(1 << ADPS2);
//    ADCSRA &= ~(1 << ADPS1);
//    ADCSRA &= ~(1 << ADPS0);
//    cli();
    TIMSK1 &= ~(1 << OCIE1B);
    setup();
    while (Serial.available() == 0) {
    }
//    delay(100);
    int timerPrescaler = Serial.read();
//    TCCR1B |= timerPrescaler;

    while (Serial.available() == 0){
    }
    int top_high = Serial.read();

    while (Serial.available() == 0) {
    }
    int top_low = Serial.read();
    cli();
    int timerPrescalerValue;
    if (timerPrescaler == 2) {
      TCCR1B &= ~(1 << CS12);
      TCCR1B |= (1 << CS11);
      TCCR1B &= ~(1 << CS10);
      timerPrescalerValue = 8;
    } else if (timerPrescaler == 3) {
      TCCR1B &= ~(1 << CS12);
      TCCR1B |= (1 << CS11);
      TCCR1B |= (1 << CS10);
      timerPrescalerValue = 64;
    } else {
      TCCR1B |= (1 << CS12);
      TCCR1B &= ~(1 << CS11);
      TCCR1B &= ~(1 << CS10);
      timerPrescalerValue = 256;
    }
    float sample_rate = 16000000/(256*top_high+top_low+1)/timerPrescalerValue;
//    float sample_rate = 16000000/(256*top_high+top_low+1)/8;

    SENDSIZE = min( max(8, int(sample_rate/8)), BUFSIZE );
//      SENDSIZE = BUFSIZE;
//    OCR1AH |= top_high;
//    OCR1AL |= top_low;
//    OCR1BH |= top_high;
//    OCR1BL |= top_low;
    OCR1A = top_high*256+top_low;
    OCR1B = top_high*256+top_low;
    i=0;
    sei();
//      Serial.println(SENDSIZE);
//    Serial.println(timerPrescalerValue);
//    Serial.println(timerPrescaler);
//    Serial.println(OCR1A);
//    Serial.println(sample_rate);

//    ADCSRA |= rate1;
//    Serial.print("Rate is ");
//    Serial.println(1000000/rate);
//    Serial.print(top_high*256+top_low);
//    Serial.write(top_high);
//    Serial.write(top_low);
//    TIMSK1 |= 1 << OCIE1B;
    control = 99;    
    sei();
//    ADCSRA |= 1 << ADATE;
//    ADCSRA |= 1 << ADSC;
  }

  if (control == '4') {
    while (Serial.available() == 0) {
    }
    byte lp = Serial.read();
    if (lp == '0') {
      lpfilter = false;
    } else {
      lpfilter = true;
    }
    control = 99;
  }

  if (control == '5') {

//  cli();
  
  if (j==0) {
    t0 = micros();
    j = 1;
//    i = 0;
//    memset(buf,0,sizeof(buf));
  }
  collecting = true;
  //Set flag to allow CTC interupts on Compare Match B
  
  TCNT1 = 0;
  TIMSK1 |= 1 << OCIE1B;
  control = 99;
//  sei();
  }

  if (control == '6') {
    TIMSK1 &= ~(1 << OCIE1B);
    collecting = false;
    control = 99;
  }

  if (control == '7') {
    j = 0;
    i=0;
    control = 99;
  }

}

ISR(TIMER1_COMPB_vect){
//  Serial.println(micros());
  
}

ISR(ADC_vect) {
//  t = micros();
//  buf[i] = ADCL;
//  buf[i+1] = ADCH;

//  if (lpfilter) {
//     buf[i] = lowpassFilter.input(ADCH);
//  } else {
//    buf[i] = ADCH;
//  }
//  Serial.print("ADC=");
//  Serial.println(ADCH);
//
//  if (collecting) {
    if (i==0) {
      t = micros() - t0;
      buf[i] = t;
      buf[i+1] = (t >> 8);
      buf[i+2] = (t >> 16);
      buf[i+3] = (t >> 24);
      i = i+4;
    }
  
    buf[i] = ADCH;
//  }
//  Serial.println(i);
//  buf[i+2] = t;
//  buf[i+3] = (t >> 8);
//  buf[i+4] = (t >> 16);
//  buf[i+5] = (t>>24);
  
//  i = i+6;
//   i = i+2;
  i++;

//  delayMicroseconds(1000000/rate);
  
  if (i == SENDSIZE) {
//      Serial.println("BUF1");
//      Serial.println(i);
//      Serial.println(buf1[0]*256+buf1[1]);
//      Serial.println((buf1[2] + buf1[3]*256 + pow(buf1[4]*256,2) + pow(buf1[5]*256,3))/1000000);
    Serial.write(buf, SENDSIZE);
    i=0;
  }
}



