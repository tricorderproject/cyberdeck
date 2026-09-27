// SensorSpecHamamatsu.cpp
// An Arduino/Chipkit driver for the new Hamamatsu C12666MA Micro Spectrometer (released ~December 2013)
// Peter Jansen, September/2014. 
// -------------------------------------------------------------------------------------------------------------
// Nominally, the entire measurement process can be completed in a few lines of code:
//  SensorSpecHamamatsu sensor;
//  sensor.takeMeasurement();
//  sensor.debugPrint();
// There are also methods to control the integration (sample) time, the gain, and to convert the measurement
// into a SensorBuffer storage class.
// -------------------------------------------------------------------------------------------------------------

//#include <wprogram.h>
#include <Arduino.h>
#include "SensorSpecHamamatsu.h"

// Constructor
SensorSpecHamamatsu::SensorSpecHamamatsu() {
  // Initialize arrays
  for (int i=0; i<SPEC_CHANNELS; i++) {
    data[i] = 0;     
  }    
  timeSampled = 0;
}

// Destructor
SensorSpecHamamatsu::~SensorSpecHamamatsu() {
}
  
boolean SensorSpecHamamatsu::begin(){
  // Setup pins
  
  pinMode(SPEC_EOS, INPUT);
  pinMode(SPEC_GAIN, OUTPUT);
  pinMode(SPEC_ST, OUTPUT);
  pinMode(SPEC_CLK, OUTPUT);
  
  /*
  pinMode(SPEC_ANALOG_IN, INPUT);
  */
  
  // Default settings
  digitalWrite(SPEC_GAIN, HIGH);
  digitalWrite(SPEC_ST, HIGH);  
  digitalWrite(SPEC_CLK, HIGH); 
  
  setGain(0);
  setIntTime(100);
  
  return true;
}

void SensorSpecHamamatsu::setIntTime(uint16_t time) {
  // Set the integration (or sample collection) time, in milliseconds
  // 60ms might be about the shortest integration time with the current ADC timings
  intTime = time;
}

void SensorSpecHamamatsu::setGain(uint8_t highLow) {
  // Gain is either 0 (low gain) or 1 (high gain)
  gain = highLow;
  if (gain == 0) {
    digitalWrite(SPEC_GAIN, 0);
  } else {
    digitalWrite(SPEC_GAIN, 1);
  }
}
      
// Low-level communication 
uint16_t SensorSpecHamamatsu::readAD7940() {
  //TODO: Just read the ADC 
  uint16_t raw14 = 0;
  raw14 += analogRead(SPEC_ANALOG_IN);       // 0–4095
  raw14 += analogRead(SPEC_ANALOG_IN);       // 0–4095
  raw14 += analogRead(SPEC_ANALOG_IN);       // 0–4095
  raw14 += analogRead(SPEC_ANALOG_IN);       // 0–4095
  return raw14;
}

/*
void SensorSpecHamamatsu::readSpectrometer() {
  //uint16_t data = &data;
  int delay_time = 35;     // delay per half clock (in microseconds).  This ultimately conrols thesp integration time. 
  int idx = 0;
  int read_time = 35;      // Amount of time that the readAD7940() procedure takes (in microseconds)
  
  // Set the last time sampled
  timeSampled = millis();

  // Step 1: start leading clock pulses
  for (int i=0; i<SPEC_CHANNELS; i++) {
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);  
  }
  
  // Step 2: Send start pulse to signal start of integration/light collection
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, LOW);
  delayMicroseconds(delay_time);  
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delay_time);  
  
  // Step 3: Integration time -- sample for a period of time determined by the intTime parameter
  int blockTime = delay_time * 8;
  int numIntegrationBlocks = (intTime * 1000) / blockTime;
  for (int i=0; i<numIntegrationBlocks; i++) {
    // Four clocks per pixel  
    // First block of 2 clocks -- measurement
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);      
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);    
    
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);      
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);    
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);      
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);        
  }


  // Step 4: Send start pulse to signal end of integration/light collection
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, LOW);
  delayMicroseconds(delay_time);  
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delay_time);  

  // Step 5: Read Data 2 (this is the actual read, since the spectrometer has now sampled data)
  idx = 0;
  for (int i=0; i<SPEC_CHANNELS; i++) {
    // Four clocks per pixel  
    // First block of 2 clocks -- measurement
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);      
    digitalWrite(SPEC_CLK, LOW);
    
    // Analog value is valid on low transition
    data[idx] = readAD7940();

    idx += 1;
    if (delay_time > read_time) delayMicroseconds(delay_time-read_time);     // Read takes about 135uSec    
    
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);

    // Second block of 2 clocks -- idle
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);      
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);      
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);    
  }

  // Step 6: trailing clock pulses
  for (int i=0; i<SPEC_CHANNELS; i++) {
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);  
  }
  
}
*/

void SensorSpecHamamatsu::readSpectrometer() {
  int idx = 0;
  int delay_time = 35;     // delay per half clock (in microseconds)    
  int read_time = 35;      // Amount of time that the readAD7940() procedure takes (in microseconds)

  //int delay_time = 82;     // delay per half clock (in microseconds)    
  //int read_time = 164;      // Amount of time that the readAD7940() procedure takes (in microseconds)


  // Debug timing variables
  unsigned long requestedIntTime_us = ((unsigned long)intTime) * 1000UL;
  unsigned long integrationStart_us = 0;
  unsigned long integrationEnd_us = 0;
  unsigned long actualIntegration_us = 0;
  unsigned long totalStart_us = micros();
  unsigned long totalEnd_us = 0;

  unsigned long adc_read_time_total = 0;
  unsigned long adc_read_time_start = 0;
  unsigned long adc_read_time_end = 0;

  // Set the last time sampled
  timeSampled = millis();

  // Step 1: start leading clock pulses
  for (int i=0; i<SPEC_CHANNELS; i++) {
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
  }

  // Step 2: Send start pulse to signal start of integration/light collection
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delay_time);

  // Step 3: Integration time -- sample for a period of time determined by the intTime parameter
  int blockTime = delay_time * 8;
  int numIntegrationBlocks = (intTime * 1000) / blockTime;

  integrationStart_us = micros();

  for (int i=0; i<numIntegrationBlocks; i++) {
    // Four clocks per pixel
    // First block of 2 clocks -- measurement
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);

    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
  }

  integrationEnd_us = micros();
  actualIntegration_us = integrationEnd_us - integrationStart_us;

  long total_read_time = 0;
  // Step 4: Send start pulse to signal end of integration/light collection
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, LOW);
  delayMicroseconds(delay_time);
  digitalWrite(SPEC_CLK, HIGH);
  digitalWrite(SPEC_ST, HIGH);
  delayMicroseconds(delay_time);

  // Step 5: Read Data 2
  idx = 0;
  for (int i=0; i<SPEC_CHANNELS; i++) {
    // Four clocks per pixel
    // First block of 2 clocks -- measurement
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, LOW);

    // Analog value is valid on low transition
    adc_read_time_start = micros();    
    data[idx] = readAD7940();
    adc_read_time_end = micros();
    adc_read_time_total += (adc_read_time_end - adc_read_time_start);

    idx += 1;
    if (delay_time > read_time) delayMicroseconds(delay_time-read_time);

    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);

    // Second block of 2 clocks -- idle
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
  }

  // Step 6: trailing clock pulses
  for (int i=0; i<SPEC_CHANNELS; i++) {
    digitalWrite(SPEC_CLK, LOW);
    delayMicroseconds(delay_time);
    digitalWrite(SPEC_CLK, HIGH);
    delayMicroseconds(delay_time);
  }

  totalEnd_us = micros();

/*
  Serial.print("requested_int_us: ");
  Serial.println(requestedIntTime_us);
  Serial.print("estimated_block_us: ");
  Serial.println(blockTime);
  Serial.print("num_integration_blocks: ");
  Serial.println(numIntegrationBlocks);
  Serial.print("actual_integration_us: ");
  Serial.println(actualIntegration_us);
  Serial.print("integration_error_us: ");
  Serial.println((long)actualIntegration_us - (long)requestedIntTime_us);
  Serial.print("total_measurement_us: ");
  Serial.println(totalEnd_us - totalStart_us);

  // Average read time
  float avg_read_time = (float)adc_read_time_total / (float)SPEC_CHANNELS;
  Serial.print("avg_read_time: ");
  Serial.println(avg_read_time);
*/

}
    
// Debug 
void SensorSpecHamamatsu::debugPrint() {
  Serial.println ("Spectral Channel (every 10th)");  
  for (int i=0; i<SPEC_CHANNELS; i+=10) {    
    //Serial.print(i, DEC); Serial.print(": "); 
    Serial.println(data[i], DEC);    
  }  
}

void SensorSpecHamamatsu::exportJSON(Stream &port) {
  int idx = 0;
  const int error_state = 0;  // Currently doesn't detect any error states

  // Begin top-level object
  port.print(F("{\"sensor\":\"spec_cd12666ma\",\"payload\":{"));

  // integration time and gain settings
  port.print(F("\"int_time\":")); port.print(intTime); port.print(",");
  port.print(F("\"gain\":")); port.print(gain); port.print(",");

  // "spectrum" array
  port.print(F("\"spectrum\":["));  
  for (int i = 0; i < SPEC_CHANNELS; i++) {
    port.print(data[i], DEC);
    if (i < (SPEC_CHANNELS-1)) port.print(F(","));      
  }
  port.print(F("]"));      
  port.print(F(","));

  // "timestamp" field
  port.print(F("\"timestamp\":"));
  port.print(timeSampled);       // TODO: Should be updated by the read function
  port.print(F(","));

  // "error_state" field
  port.print(F("\"error_state\":"));
  port.print(error_state);

  // Close payload and top-level object
  port.print(F("}}"));
  port.println();
}