//–– SPS30.h ––//
// PJ + ChatGPT
#ifndef SPS30_H
#define SPS30_H

#include <Arduino.h>

#define SPS30_MAX_FRAME_SIZE 256

// ERROR STATES
#define ERROR_STATE_OK                  0
#define ERROR_STATE_NO_RESPONSE         10
#define ERROR_STATE_UNEXPECTED_PACKET   11
#define ERROR_STATE_PACKET_TOO_SHORT    12
#define ERROR_STATE_UNEXPCTED_STATE     13

//--------------------------------------------------------------------------------
// 1) Structure to hold the ten unsigned‐16‐bit measurement values
//--------------------------------------------------------------------------------
typedef struct {
  float mass_PM1_0;           // µg/m³
  float mass_PM2_5;           // µg/m³
  float mass_PM4_0;           // µg/m³
  float mass_PM10;            // µg/m³
  float number_PM0_5;         // #/cm³
  float number_PM1_0;         // #/cm³
  float number_PM2_5;         // #/cm³
  float number_PM4_0;         // #/cm³
  float number_PM10;          // #/cm³
  float typical_particle_size; // nm
  unsigned long timestamp;    // milliseconds since last restart
} SPS30Measurement_t;

class SPS30 {
  public:
    // Constructor
    SPS30();

    // Initialize the UART for SPS30 (Serial1 at 115200 baud)
    void begin();

    // Read one full measurement and print via Serial
    void read_sps30();

    /// Export the current `meas` wrapped in a higher‐level JSON object:
    /// { "sensor":"sps30", "payload": { … } }
    void exportJSON(Stream &port);

    SPS30Measurement_t meas;

    int error_state;


  private:
    // Send wake-up command twice (100 ms apart)
    void sps30_wake_up();

    // Send “start measurement” command (IEEE 754 float format)
    void sps30_start_measurement();

    // Send “get latest measurement” command
    void sps30_get_measurement();

    // Low-level SHDLC receive:
    //  • waits for 0x7E … 0x7E
    //  • un-stuffs 0x7D escapes
    //  • returns “frameBuf[0..frameLen-1] = [addr, cmdEcho, lenH, lenL, … data …, state, CRC]”
    bool receiveSPS30Packet(uint8_t *frameBuf, size_t &frameLen, uint32_t timeoutMs);

    // Helper to parse big-endian IEEE 754 floats from data buffer
    float beFloat(const uint8_t *pdata, size_t offset);
};

#endif // SPS30_H
