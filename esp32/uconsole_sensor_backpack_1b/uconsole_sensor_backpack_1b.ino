// Example of testing all the sensors for the backpack


#include "tfminiplus.h"
#include <Adafruit_MLX90640.h>
#include "SparkFun_SCD4x_Arduino_Library.h" //Click here to get the library: http://librarymanager/All#SparkFun_SCD4x
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include "Adafruit_MLX90393.h"

#include "SensorBuffer.h"
#include "SensorRadiation.h"

#include "SensorSpecHamamatsu.h"


#include "sps30.h"


#define PIN_3V_ENABLE 25
#define PIN_5V_ENABLE 26

// Firmware version, reported at the end of setup()
#define FIRMWARE_VERSION "1b.1"

// SPS30 particle sensor
SPS30 sensorSPS30;

// Hamamatsu Spectrometer
SensorSpecHamamatsu sensorSpec;

/*
// Constants/Globals
Adafruit_MLX90640 mlx;
float mlx90640_frame[32*24]; // buffer for full frame of temperatures
//#define PRINT_ASCIIART
#define PRINT_TEMPERATURES
*/

SCD4x sensorSCD4x;

// BME688
#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BME680 bme(&Wire); // I2C

// MLX90393
Adafruit_MLX90393 mlx90393 = Adafruit_MLX90393();

// Radiation Watch Type 5
//SensorBuffer sbRad(100);
//SensorRadiation sensorRadiation(&sbRad);
//SensorRadiation sensorRadiation;
int DIGIPOT_UD  = 33;
int DIGIPOT_CS  = 15;


// Magnetic Imaging Tile
#define CS_INACTIVE  1
#define CS_ACTIVE    0

//Hardware connections
const byte PIN_ANALOG = A2;

// Pin mapping for the clockwork-backpack-1a4 main board with a SparkFun ESP32 Thing Plus C in the
// Feather socket.  The schematic labels the socket by Feather position (GPIO5, GPIO6, GPIO9, ...);
// the ESP32 GPIO that the Thing Plus C actually has at each of those positions is used here.
//   Feather pos.  Thing Plus C GPIO   Tile signal
//   GPIO5         14                  CLK  (counter clock)
//   GPIO6         32                  CLR  (counter clear)
//   GPIO9         15                  CS   (AD7680, unused)
//   GPIO10        33                  MISO (AD7680, unused)
//   GPIO11        27                  SCK  (AD7680, unused)
//   A2            34                  OUT  (analog)
#define PIN_CLR   32
#define PIN_CLK   14
/*
const byte AD7940_SPI_MISO = 33;
const byte AD7940_SPI_CS = 15;
const byte AD7940_SPI_CLK = 27;
*/

// Frames
//#if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)

//We have very limited RAM
//#define MAX_BASE_FRAMES  2

//#else

//Platforms like SAMD21, ChipKit, and Teensy have far more RAM
//#define MAX_BASE_FRAMES  500
//#define MAX_BASE_FRAMES  250
#define MAX_BASE_FRAMES  100
//#define _8BIT

//#endif

#ifdef _8BIT
#define MAX_FRAMES      MAX_BASE_FRAMES*2
uint8_t frames[MAX_FRAMES][64];
#else
#define MAX_FRAMES      MAX_BASE_FRAMES
uint16_t frames[MAX_FRAMES][64];
#endif


// Frame variables
// Magnetic tile reading
int pixelOrder[] = {26, 27, 18, 19, 10, 11, 2, 3, 1, 0, 9, 8, 17, 16, 25, 24};
int subtileOrder[] = {0, 2, 1, 3};
int subtileOffset[] = {0, 4, 32, 36};
uint16_t frame[64];

int numFrames = 0;
int curFrame = 0;

#define MODE_IDLE          0
#define MODE_LIVE          1
#define MODE_HIGHSPEED1    2
#define MODE_HIGHSPEED2    3
#define MODE_HIGHSPEED3    4
#define MODE_HIGHSPEED4    5
#define MODE_PIXEL         6

int curMode = MODE_IDLE;



// Variables showing whether a given sensor is present and initialized
bool SENSOR_PRESENT_MLX90640;
bool SENSOR_PRESENT_SPS30;
bool SENSOR_PRESENT_SCD4X;
bool SENSOR_PRESENT_BME688;
bool SENSOR_PRESENT_MLX90393;

// Variables showing which sensor is being focused on right now
int current_focus_sensor = 0;

#define FOCUS_SENSOR_NONE             0
#define FOCUS_SENSOR_SPECTROMETER     1
#define FOCUS_SENSOR_MAGNETIC_TILE    2
#define FOCUS_SENSOR_MAGNETOMETER     3
// None of the rest require particularly high updates


/*
 *  Radiation Watch Type 5
 */

/*
int digipotSetting = 32;

void initDigipot() {
  pinMode(DIGIPOT_UD, OUTPUT);
  pinMode(DIGIPOT_CS, OUTPUT);

  digitalWrite(DIGIPOT_CS, 1);    // Inactive
  digitalWrite(DIGIPOT_UD, 0);    // N/A
}

void incrementDigipot(int val) {
  digitalWrite(DIGIPOT_CS, 1);    // Inactive
  delayMicroseconds(10);
  digitalWrite(DIGIPOT_UD, 1);    // Set to increment
  delayMicroseconds(10);

  digitalWrite(DIGIPOT_CS, 0);    // Active
  delayMicroseconds(10);

  for (int i=0; i<val; i++) {
    // Pulse to increment
    digitalWrite(DIGIPOT_UD, 0);    
    delayMicroseconds(10);
    digitalWrite(DIGIPOT_UD, 1);    
    delayMicroseconds(10);
  }

  digitalWrite(DIGIPOT_CS, 1);    // Inactive  
  delayMicroseconds(10);
}

void decrementDigipot(int val) {
  digitalWrite(DIGIPOT_CS, 1);    // Inactive
  delayMicroseconds(10);
  digitalWrite(DIGIPOT_UD, 0);    // Set to decrement
  delayMicroseconds(10);

  digitalWrite(DIGIPOT_CS, 0);    // Active
  delayMicroseconds(10);

  for (int i=0; i<val; i++) {
    // Pulse to decrement
    digitalWrite(DIGIPOT_UD, 1);    
    delayMicroseconds(10);
    digitalWrite(DIGIPOT_UD, 0);    
    delayMicroseconds(10);
  }

  digitalWrite(DIGIPOT_CS, 1);    // Inactive  
  delayMicroseconds(10);
}


void setDigipot(int num) {
  int delta = digipotSetting - num;
  if (delta > 0) {
    incrementDigipot(delta);
  } 
  if (delta < 0) {
    decrementDigipot(-delta);
  }
  digipotSetting += delta;
}

void setDigipotAbsolute(int num) {
  incrementDigipot(64);
  decrementDigipot(64 - num);
  //digipotSetting = 32;

  //setDigipot(num);
}
*/


/*
 *  Magnetic Imaging Tile
 */
/*
   Analog Read
*/
int readMagnetometer() {
  //return 0;
  //return analogRead(PIN_ANALOG);
  return readInternalADC();
  //return readAD7940();
  //return read_ad7940();
}

// Take one measurement form the internal ADC
int readInternalADC() {
  int numSamples = 2;
  float sum = 0.0f;
  for (int i = 0; i < numSamples; i++) {
    int sensorValue = analogRead(PIN_ANALOG);
    sum += sensorValue;
  }
  sum /= numSamples;

  //return sensorValue;
  return int(floor(sum));
}


// Take one measurement from an external AD7940 14-bit ADC (SPI)
/*
uint16_t readAD7940() {
  uint16_t value = 0;
  //uint16_t delay_time = 2;

  // Idle
  digitalWrite(AD7940_SPI_CS, HIGH);
  digitalWrite(AD7940_SPI_CLK, HIGH);

  // Enable
  digitalWrite(AD7940_SPI_CS, LOW);

  // Read 16 bits
  for (int i = 0; i < 16; i++) {
    char bit = digitalRead(AD7940_SPI_MISO);
    digitalWrite(AD7940_SPI_CLK, LOW);
    //    delayMicroseconds(delay_time);

    value = value << 1;
    value = value + (bit & 0x01);
    digitalWrite(AD7940_SPI_CLK, HIGH);
    //    delayMicroseconds(delay_time);
  }
  // Disable
  digitalWrite(AD7940_SPI_CS, HIGH);
  //  delayMicroseconds(delay_time);

  return value;
}
*/

/*
   Magnetic Sensors
*/
void clearCounter() {
  digitalWrite(PIN_CLR, 0);
  delayMicroseconds(2);     // Hold the clear pulse long enough for the 74HC590A to register it
  digitalWrite(PIN_CLR, 1);
  delayMicroseconds(2);     // Recovery time before the first clock edge
}

void incrementCounter() {
  digitalWrite(PIN_CLK, 1);
  delayMicroseconds(2);     // Hold the clock pulse long enough for the 74HC590A to register it
  digitalWrite(PIN_CLK, 0);
  delayMicroseconds(2);     // Let the counter/mux settle before the next ADC read
}

/*
   Capture one frame from imaging array
*/
void readTileFrame() {

  clearCounter();
  incrementCounter();

  for (int curSubtileIdx = 0; curSubtileIdx < 4; curSubtileIdx++) {
    for (int curIdx = 0; curIdx < 16; curIdx++) {
      // Read value
      int value = readMagnetometer();

      //terminal.println(value);
      //delay(10);

      // Store value in correct frame location
      int frameOffset = pixelOrder[curIdx] + subtileOffset[subtileOrder[curSubtileIdx]];
      //terminal.println(frameOffset);
      //delay(25);
      frame[frameOffset] = value;

      // Increment to next pixel
      incrementCounter();
    }
  }
}

// Display current frame on serial console
void displayCurrentFrame() {
  // Display frame
  Serial.println ("\nCurrent Magnetic Tile Frame");
  int idx = 0;
  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      //terminal.print( frame[idx] );
      //terminal.print( " " );
      Serial.print( frame[idx] );
      Serial.print(" ");
      idx += 1;
    }
    Serial.println("");
  }
  Serial.println("*");
}


void displayCurrentFrameJSON(Stream &port) {
  int idx = 0;
  const int error_state = 0;  // Currently doesn't detect any error states

  // Begin top-level object
  port.print(F("{\"sensor\":\"magnetic_tile\",\"payload\":{"));

  // "frame" array
  port.print(F("\"frame\":["));
  for (int row = 0; row < 8; row++) {
    port.print(F("["));
    for (int col = 0; col < 8; col++) {
      port.print(frame[idx]);
      if (col < 7) port.print(F(","));
      idx++;
    }
    port.print(F("]"));
    if (row < 7) port.print(F(","));
  }
  port.print(F("],"));

  // "timestamp" field
  port.print(F("\"timestamp\":"));
  port.print(millis());       // TODO: Should be updated by the read function
  port.print(F(","));

  // "error_state" field
  port.print(F("\"error_state\":"));
  port.print(error_state);

  // Close payload and top-level object
  port.print(F("}}"));
  port.println();
}



// Record MAX_FRAMES, as fast as possible
void recordHighSpeedFrames(int frameDelayTime) {
  long startTime = millis();

  for (int curFrame = 0; curFrame < MAX_FRAMES; curFrame++) {
    // Read one frame
    readTileFrame();

    // Store frame
#ifdef _8BIT
    for (int a = 0; a < 64; a++) {
      frames[curFrame][a] = frame[a] >> 2;
    }
#else
    for (int a = 0; a < 64; a++) {
      frames[curFrame][a] = frame[a];
    }
#endif

    if (frameDelayTime > 0) {
      delay(frameDelayTime);
    }
  }

  long endTime = millis();
  Serial.print("Framerate: ");
  Serial.println((float)MAX_FRAMES / ((float)(endTime - startTime) / 1000.0f));
}

// Playback the high speed frames stored
void playbackHighSpeedFrames() {

  for (int curFrame = 0; curFrame < MAX_FRAMES; curFrame++) {
    // Display frame
    //    terminal.print ("\nFrame ");
    //    terminal.println (curFrame);

    int idx = 0;
    for (int i = 0; i < 8; i++) {
      for (int j = 0; j < 8; j++) {
        Serial.print( frames[curFrame][idx] );
        Serial.print( " " );
        idx += 1;
      }
      Serial.println("");
    }
    Serial.println("*");
    delay(50);
  }
}




/*
 *  Sensors
 */ 
/*
void readMLX90640() {

  if (mlx.getFrame(mlx90640_frame) != 0) {
    Serial.println("Failed");
    return;
  }
  Serial.println("===================================");
  Serial.print("Ambient temperature = ");
  Serial.print(mlx.getTa(false)); // false = no new frame capture
  Serial.println(" degC");
  Serial.println();
  Serial.println();
  for (uint8_t h=0; h<24; h++) {
    for (uint8_t w=0; w<32; w++) {
      float t = mlx90640_frame[h*32 + w];
#ifdef PRINT_TEMPERATURES
      Serial.print(t, 0);
      Serial.print(", ");
#endif
#ifdef PRINT_ASCIIART
      char c = '&';
      if (t < 20) c = ' ';
      else if (t < 23) c = '.';
      else if (t < 25) c = '-';
      else if (t < 27) c = '*';
      else if (t < 29) c = '+';
      else if (t < 31) c = 'x';
      else if (t < 33) c = '%';
      else if (t < 35) c = '#';
      else if (t < 37) c = 'X';
      Serial.print(c);
#endif
    }
    Serial.println();
  }

}
*/


void readSPS30() {
  sensorSPS30.read_sps30();
  sensorSPS30.exportJSON(Serial);
}



/*
void readSCD4x() {

  if (sensorSCD4x.readMeasurement()) {
    Serial.println();

    Serial.print(F("CO2(ppm):"));
    Serial.print(sensorSCD4x.getCO2());

    Serial.print(F("\tTemperature(C):"));
    Serial.print(sensorSCD4x.getTemperature(), 1);

    Serial.print(F("\tHumidity(%RH):"));
    Serial.print(sensorSCD4x.getHumidity(), 1);

    Serial.println();
  } else {
    Serial.println("SCD4x reading not available.");
  }

}
*/

void readSCD4x(Stream &port) {
  int scd4x_error_state = 0;

  if (!sensorSCD4x.readMeasurement()) {
    scd4x_error_state = 1;
  }

  // Begin top‐level object
  port.print(F("{\"sensor\":\"scd4x\",\"payload\":"));

  // Begin payload object
  port.print(F("{"));

  if (scd4x_error_state == 0) {
    port.print(F("\"atmospheric\":{"));
    port.print(F("\"co2_ppm\":"));           port.print(sensorSCD4x.getCO2());         port.print(F(","));
    port.print(F("\"temp_c\":"));            port.print(sensorSCD4x.getTemperature(), 1); port.print(F(","));
    port.print(F("\"humidity_rh_pct\":"));   port.print(sensorSCD4x.getHumidity(), 1);
    port.print(F("},"));
  }

  // “timestamp” field
  port.print(F("\"timestamp\":"));
  port.print(millis());
  port.print(F(","));

  // error_state field
  port.print(F("\"error_state\":"));
  port.print(scd4x_error_state);

  // Close payload and top‐level
  port.print(F("}}"));
  port.println();
}



void readBME688(Stream &port) {  
  int bme688_error_state = 0;
  if (! bme.performReading()) {
    //Serial.println("Failed to perform reading :(");
    bme688_error_state = 1;    
  }

  /*
  Serial.print("Temperature = ");
  Serial.print(bme.temperature);
  Serial.println(" *C");

  Serial.print("Pressure = ");
  Serial.print(bme.pressure / 100.0);
  Serial.println(" hPa");

  Serial.print("Humidity = ");
  Serial.print(bme.humidity);
  Serial.println(" %");

  Serial.print("Gas = ");
  Serial.print(bme.gas_resistance / 1000.0);
  Serial.println(" KOhms");

  Serial.print("Approx. Altitude = ");
  Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
  Serial.println(" m");

  Serial.println();
  */

  // Begin top‐level object
  port.print(F("{\"sensor\":\"bme688\",\"payload\":"));

  // Begin payload object
  port.print(F("{"));

  if (bme688_error_state == 0) {
    // “mass” object
    port.print(F("\"magnetic\":{"));
    port.print(F("\"temp_c\":"));                 port.print(bme.temperature);        port.print(F(","));
    port.print(F("\"pressure_hpa\":"));           port.print(bme.pressure / 100.0);   port.print(F(","));
    port.print(F("\"gas_resistance_kohm\":"));    port.print(bme.gas_resistance / 1000.0);   port.print(F(","));
    port.print(F("\"altitude_m\":"));             port.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
    port.print(F("},"));
  }

  // “timestamp” field
  port.print(F("\"timestamp\":"));
  port.print(millis());
  port.print(F(","));

  // error_state field
  port.print(F("\"error_state\":"));
  port.print(bme688_error_state);

  // Close payload and top‐level
  port.print(F("}}"));
  port.println();

}



void readMLX90393(Stream &port) {
  float x, y, z;
  int mag_error_state = 0;

  // get X Y and Z data at once
  if (!mlx90393.readData(&x, &y, &z)) {
      //Serial.println("MLX90393: Unable to read XYZ data from the sensor.");
      mag_error_state = 1;      
  }

  // Begin top‐level object
  port.print(F("{\"sensor\":\"mlx90393\",\"payload\":"));

  // Begin payload object
  port.print(F("{"));

  if (mag_error_state == 0) {
    // “mass” object
    port.print(F("\"magnetic\":{"));
    port.print(F("\"x_ut\":"));   port.print(x);   port.print(F(","));
    port.print(F("\"y_ut\":"));   port.print(y);   port.print(F(","));
    port.print(F("\"z_ut\":"));   port.print(z); 
    port.print(F("},"));
  }

  // “timestamp” field
  port.print(F("\"timestamp\":"));
  port.print(millis());
  port.print(F(","));

  // error_state field
  port.print(F("\"error_state\":"));
  port.print(mag_error_state);

  // Close payload and top‐level
  port.print(F("}}"));
  port.println();


}



/*
 * Setup/Main
 */ 

void setup() {
  // put your setup code here, to run once:
  
  // Serial debug console:
  Serial.begin(115200);
  Serial.println("Initializing...");
  delay(500);

  // Turn on the 3.3V regulator
  pinMode(PIN_3V_ENABLE, OUTPUT);
  digitalWrite(PIN_3V_ENABLE, HIGH);    // Enable regulator
  delay(500);

/*
  // Turn on the 5V regulator
  pinMode(PIN_5V_ENABLE, OUTPUT);
  digitalWrite(PIN_5V_ENABLE, HIGH);    // Enable 5V regulator
  delay(500);
*/

  Wire.begin();

  // TF Mini Plus initialization (Serial1)
  //Serial1.begin(115200);

/*
  // MLX90640 Thermopile Array initialization
  SENSOR_PRESENT_MLX90640 = false;
  if (!mlx.begin(MLX90640_I2CADDR_DEFAULT, &Wire)) {    
    Serial.println("MLX90640 not found!");
    SENSOR_PRESENT_MLX90640 = false;    
  } else {
    Serial.println("MLX90640 found!");
    SENSOR_PRESENT_MLX90640 = true;    
  }  

  mlx.setMode(MLX90640_CHESS);              // Set to Chess vs Interleave mode
  mlx.setResolution(MLX90640_ADC_18BIT);    // Set resolution
  //mlx.setResolution(MLX90640_ADC_16BIT);    // Set resolution
  mlx.setRefreshRate(MLX90640_2_HZ);        // Set refresh rate
  //mlx.setRefreshRate(MLX90640_4_HZ);        // Set refresh rate
*/


/*
  // Sensiron SPS30 Air Particle Detector
  SENSOR_PRESENT_SPS30 = false;
  sensirion_i2c_init();  
  for (int i=0; i<10; i++) {
    if (sps30_probe() != 0) {                
      Serial.print("SPS30 sensor probing failed\n");
      SENSOR_PRESENT_SPS30 = false;
      delay(250);      
    } else {
      Serial.println("SPS30 sensor found!");
      SENSOR_PRESENT_SPS30 = true;
      break;
    }
  }

  int16_t ret;
  uint8_t auto_clean_days = 4;
  uint32_t auto_clean;
  ret = sps30_set_fan_auto_cleaning_interval_days(auto_clean_days);

  if (ret) {
    Serial.print("error setting the auto-clean interval: ");
    Serial.println(ret);
  }

  ret = sps30_start_measurement();
  if (ret < 0) {
    Serial.print("error starting measurement\n");
  }
*/

  // Initialize the spectrometer
  Serial.println("Initializing Hamamatsu Spectrometer...");
  sensorSpec.begin();


  // SPS30 (UART driver)
  sensorSPS30.begin();


  // SCD4x CO2 sensor
  SENSOR_PRESENT_SCD4X = false;
  if (sensorSCD4x.begin() == false) {    
    Serial.println("SCD4x not detected!");    
    SENSOR_PRESENT_SCD4X = false;
  } else {
    Serial.println("SCD4x detected!");    
    SENSOR_PRESENT_SCD4X = true;
  }

  // BME688 Sensor
  if (!bme.begin(0x76)) {
    Serial.println("BME688 not found!");
    SENSOR_PRESENT_BME688 = false;
  } else {
    Serial.println("BME688 found!");
    SENSOR_PRESENT_BME688 = true;
  }

  // Set up oversampling and filter initialization
  if (SENSOR_PRESENT_BME688) {
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150); // 320*C for 150 ms
  }

  // MLX90393 Magnetometer
  if (!mlx90393.begin_I2C()) {          // hardware I2C mode, can pass in address & alt Wire  
    Serial.println("MLX90393 not found!");
    SENSOR_PRESENT_MLX90393 = false;    
  } else {
    Serial.println("MLX90393 found!");
    SENSOR_PRESENT_MLX90393 = true;

    // Set gain
    mlx90393.setGain(MLX90393_GAIN_1X);
    // Set resolution, per axis. Aim for sensitivity of ~0.3 for all axes.
    mlx90393.setResolution(MLX90393_X, MLX90393_RES_17);
    mlx90393.setResolution(MLX90393_Y, MLX90393_RES_17);
    mlx90393.setResolution(MLX90393_Z, MLX90393_RES_16);

    // Set oversampling
    mlx90393.setOversampling(MLX90393_OSR_3);

    // Set digital filtering
    mlx90393.setFilter(MLX90393_FILTER_5);

  }

/*
  Serial.print("Initializing Radiation Watch Type 5...");
  // Radiation Watch Type 5
  // Initialize the digipot
  initDigipot();
  delay(10);
  //setDigipot(10);
  setDigipotAbsolute(55);
  delay(10);
*/

  // Initialize radiation sensor
  
//  setupRadiationISR(&sensorRadiation);     // MUST be called before begin()
//  sensorRadiation.begin();  
  
  Serial.println("here1");

  delay(500);

  // Magnetic Imaging tile
  Serial.println("Initializing magnetic imaging tile...");
  // Setup pin modes
  pinMode(PIN_CLR, OUTPUT);
  pinMode(PIN_CLK, OUTPUT);
  delay(10);

  // Setup initial states
  incrementCounter();
  clearCounter();  

  //delay(100);
  delay(500);


  Serial.println("Initialization complete...");

  // Report firmware version and build time (as plain text, and as a JSON line the host driver can store)
  Serial.print("Firmware version: ");
  Serial.print(FIRMWARE_VERSION);
  Serial.print("  (built ");
  Serial.print(__DATE__);
  Serial.print(" ");
  Serial.print(__TIME__);
  Serial.println(")");
  Serial.print(F("{\"sensor\":\"firmware\",\"payload\":{\"version\":\""));
  Serial.print(FIRMWARE_VERSION);
  Serial.print(F("\",\"built\":\""));
  Serial.print(__DATE__);
  Serial.print(" ");
  Serial.print(__TIME__);
  Serial.println(F("\"}}"));

  // Set the current focus to none
  current_focus_sensor = FOCUS_SENSOR_NONE;

}

/*
int current_focus_sensor = 0;

#define FOCUS_SENSOR_NONE             0
#define FOCUS_SENSOR_SPECTROMETER     1
#define FOCUS_SENSOR_MAGNETIC_TILE    2
#define FOCUS_SENSOR_MAGNETOMETER     3
// None of the rest require particularly high updates
*/

void loop() {
  // put your main code here, to run repeatedly:

  // Read characters to select the sensor mode
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == 's') {
      current_focus_sensor = FOCUS_SENSOR_SPECTROMETER;
    } else if (c == 'm') {
      current_focus_sensor = FOCUS_SENSOR_MAGNETIC_TILE;
    } else if (c == 'n') {
      current_focus_sensor = FOCUS_SENSOR_MAGNETOMETER;
    } else if (isAlphaNumeric(c)) {
      current_focus_sensor = FOCUS_SENSOR_NONE;
    }
  }

  // Read TF Mini Plus distance
  /*
  int distance = 0;
  int strength = 0;
  bool success_tfmini = getTFminiPlusData(&distance, &strength);
  if (distance) {
    Serial.print(distance);
    Serial.print("cm\t");
    Serial.print("strength: ");
    Serial.println(strength);
  } else {
    Serial.println("No distance reading");
  }
  */

  // Read from MLX90640 thermopile array
  //readMLX90640();

  // Check the current focus sensor
  if (current_focus_sensor == FOCUS_SENSOR_SPECTROMETER) {
    // Hamamatsu Microspectrometer
    sensorSpec.readSpectrometer();
    sensorSpec.exportJSON(Serial);

  } else if (current_focus_sensor == FOCUS_SENSOR_MAGNETIC_TILE) {
    // Read from magnetic imaging tile
    readTileFrame();    
    displayCurrentFrameJSON(Serial);

    // Read from MLX90393 magnetic field sensor
    readMLX90393(Serial);

  } else if (current_focus_sensor == FOCUS_SENSOR_MAGNETOMETER) {
    // Read from MLX90393 magnetic field sensor
    readMLX90393(Serial);


  } else {
    // Focus: None/Everything
  

    // Read from SPS30 air particle sensor
    readSPS30();

    // Read from the SCD4x CO2 sensor
    readSCD4x(Serial);

    // Read from BME688 sensor
    readBME688(Serial);

    // Read from MLX90393 magnetic field sensor
    readMLX90393(Serial);

    // Read from magnetic imaging tile
    readTileFrame();
    //displayCurrentFrame();
    displayCurrentFrameJSON(Serial);

    // Hamamatsu Microspectrometer
    sensorSpec.readSpectrometer();
    sensorSpec.exportJSON(Serial);

  }
  
/*
  float cpm = sensorRadiation.calculateCPM();
  Serial.print ("CPM: ");  
  Serial.println(cpm, DEC);
  
  // Display pulse width histogram
  sensorRadiation.debugPrint();
  //sensorRadiation.exportJSON();
*/

  delay(1000);
}
