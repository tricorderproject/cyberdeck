// SensorSpecHamamatsu.h
#if !defined(SENSOR_SPEC_C12666_h) 
#define SENSOR_SPEC_C12666_h

//#include <wprogram.h>
#include <Arduino.h>

// Number of spectral channels
#define SPEC_CHANNELS    256

// Pin mappings
#define SPEC_GAIN        35
#define SPEC_EOS         39
#define SPEC_ST          18
#define SPEC_CLK         23
#define SPEC_ANALOG_IN   A4


class SensorSpecHamamatsu {
  // Variables  
  public:
  uint16_t data[SPEC_CHANNELS];
  uint16_t intTime;      // Integration (sampling) time    
  uint8_t gain;          // High/low gain
  unsigned long timeSampled;    // The time the last measurement was taken (measured with millis())

  // Constructor/Destructor
  SensorSpecHamamatsu();
  ~SensorSpecHamamatsu();
  
  // Setup methods
  boolean begin();
  void setIntTime(uint16_t time);  
  void setGain(uint8_t highLow);  
    
  // Low-level communication 
  uint16_t readAD7940();
  void readSpectrometer();
  
  void exportJSON(Stream &port);

  // Debug 
  void debugPrint();
};

#endif