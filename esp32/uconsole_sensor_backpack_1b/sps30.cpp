//–– SPS30.cpp ––//
// PJ + ChatGPT
#include "sps30.h"

// Constructor (no internal state to initialize here)
SPS30::SPS30() {}

//--------------------------------------------------------------------------------
// Initialize the UART for SPS30
//--------------------------------------------------------------------------------
/*
void SPS30::begin() {
  error_state = -1;
  Serial1.begin(115200);
  error_state = ERROR_STATE_OK;
}
*/
void SPS30::begin() {
  error_state = -1;
  memset(&meas, 0, sizeof(meas));

  Serial1.begin(115200);
  delay(100);

  // Clear any junk/old bytes
  while (Serial1.available() > 0) {
    Serial1.read();
  }

  // Put SPS30 into continuous measurement mode
  sps30_start_measurement();

  // Consume the ACK packet from the start-measurement command
  uint8_t frame[SPS30_MAX_FRAME_SIZE];
  size_t length = 0;
  receiveSPS30Packet(frame, length, 1000);

  // SPS30 does not have a measurement immediately after start
  delay(1000);

  error_state = ERROR_STATE_OK;
}

//--------------------------------------------------------------------------------
// Send wake-up command twice (100 ms apart)
//--------------------------------------------------------------------------------
void SPS30::sps30_wake_up() {
  uint8_t packet[] = {
    0x7E, 0x00, 0x11, 0x00, 0xEE, 0x7E
  };

  // Send the packet twice (100 ms apart)
  Serial1.write(packet, sizeof(packet));
  delay(100);
  Serial1.write(packet, sizeof(packet));
}

//--------------------------------------------------------------------------------
// Send “start measurement” command (IEEE 754 float format)
//--------------------------------------------------------------------------------
void SPS30::sps30_start_measurement() {
  // … IEEE 754 float format (0x03) …
  uint8_t packet[] = {
    0x7E, 0x00, 0x00, 0x02, 0x01, 0x03, 0xF9, 0x7E
  };

  // Send the packet
  Serial1.write(packet, sizeof(packet));
}

//--------------------------------------------------------------------------------
// Send “get latest measurement” command
//--------------------------------------------------------------------------------
void SPS30::sps30_get_measurement() {
  uint8_t packet[] = {
    0x7E, 0x00, 0x03, 0x00, 0xFC, 0x7E
  };

  // Send the packet
  Serial1.write(packet, sizeof(packet));
}

//--------------------------------------------------------------------------------
// Low‐level SHDLC‐receive function (unchanged from before)
//  • waits for 0x7E … 0x7E
//  • un‐stuffs 0x7D escapes
//  • returns “frameBuf[0..frameLen-1] = [addr, cmdEcho, lenH, lenL, … data …, state, CRC]”
//--------------------------------------------------------------------------------
bool SPS30::receiveSPS30Packet(uint8_t *frameBuf, size_t &frameLen, uint32_t timeoutMs) {
  uint32_t startTime = millis();

  // (1) Wait for start‐of‐frame (0x7E)
  while (millis() - startTime < timeoutMs) {
    if (Serial1.available()) {
      uint8_t b = Serial1.read();
      if (b == 0x7E) {
        // Found 0x7E → begin reading “raw” bytes now
        break;
      }
    }
  }
  if (millis() - startTime >= timeoutMs) {
    error_state = ERROR_STATE_NO_RESPONSE;
    return false; // no start‐frame    
  }

  // (2) Collect “stuffed” bytes until the next 0x7E
  uint8_t rawBuf[SPS30_MAX_FRAME_SIZE];
  size_t  rawLen = 0;

  while (millis() - startTime < timeoutMs && rawLen < SPS30_MAX_FRAME_SIZE) {
    if (Serial1.available()) {
      uint8_t b = Serial1.read();
      if (b == 0x7E) {
        // End‐of‐frame
        break;
      }
      rawBuf[rawLen++] = b;
    }
  }
  if (millis() - startTime >= timeoutMs || rawLen >= SPS30_MAX_FRAME_SIZE) {
    error_state = ERROR_STATE_NO_RESPONSE;
    return false; // timeout or overflow
  }

  // (3) Un‐stuff into frameBuf[]
  size_t idx = 0;
  for (size_t i = 0; i < rawLen; i++) {
    if (rawBuf[i] == 0x7D) {
      // Next byte indicates original
      if (i + 1 >= rawLen) {
        return false; // malformed escape
      }
      uint8_t esc = rawBuf[++i];
      switch (esc) {
        case 0x5E: frameBuf[idx++] = 0x7E; break;
        case 0x5D: frameBuf[idx++] = 0x7D; break;
        case 0x31: frameBuf[idx++] = 0x11; break;
        case 0x33: frameBuf[idx++] = 0x13; break;
        default:
          error_state = ERROR_STATE_UNEXPECTED_PACKET;
          return false; // invalid escape

      }
    } else {
      frameBuf[idx++] = rawBuf[i];
    }
    if (idx >= SPS30_MAX_FRAME_SIZE) {
      error_state = ERROR_STATE_UNEXPECTED_PACKET;
      return false; // overflow
    }
  }

  frameLen = idx;
  return true;
}

//--------------------------------------------------------------------------------
// Read one full measurement and print via Serial
//--------------------------------------------------------------------------------
void SPS30::read_sps30() {
  uint8_t sps30_frame[SPS30_MAX_FRAME_SIZE];
  size_t  length;

  // Request the latest measurement
  sps30_get_measurement();

  delay(20);

  //Serial.println("Waiting for one SPS30 packet…");
  if (receiveSPS30Packet(sps30_frame, length, /*timeoutMs=*/ 2000)) {
    /*
    Serial.print("Received unstuffed packet (");
    Serial.print(length);
    Serial.println(" bytes):");    
    // Print each unstuffed byte as hex
    for (size_t i = 0; i < length; i++) {
      if (sps30_frame[i] < 0x10) Serial.print('0');      
      Serial.print(sps30_frame[i], HEX);
      Serial.print(' ');
    }
    Serial.println();
    */
    // Here you can parse:
    //   packet[0]    = address (always 0x00 from SPS30)
    //   packet[1]    = echoed command 
    //   packet[2..3] = length high/low 
    //   packet[4..(4+dataLen-1)] = data 
    //   packet[...]  = state byte 
    //   (Optional CRC bytes at the end, depending on command)
  } else {
    //Serial.println("No valid packet within timeout or framing error.");
  }

  // If the frame is 5 bytes, then it's an empty frame -- skip
  if (length < 45) {
    error_state = ERROR_STATE_PACKET_TOO_SHORT;
    return;    
  }

  // If the frame is 45 bytes, then it's a full frame -- parse the data
  uint8_t  address  = sps30_frame[0];
  uint8_t  cmdEcho  = sps30_frame[1];
  uint8_t  state    = sps30_frame[2];
  uint8_t  dataLen  = sps30_frame[3];    
  uint8_t  crc      = sps30_frame[length - 1];

  // 4) Sanity checks:
  if (address != 0x00) {
    error_state = ERROR_STATE_UNEXPECTED_PACKET;
    /*
    Serial.print(F("  → Unexpected address=0x"));
    Serial.print(address, HEX);
    Serial.println(F(" (should be 0x00)."));
    */

    return;
  }
  if (cmdEcho != 0x03) {
    error_state = ERROR_STATE_UNEXPECTED_PACKET;
    /*
    Serial.print(F("  → Unexpected cmdEcho=0x"));
    Serial.print(cmdEcho, HEX);
    Serial.println(F(" (should echo 0x03)."));
    */

    return;
  }

  // 5) Check “state” byte
  if (state != 0x00) {
    error_state = ERROR_STATE_UNEXPECTED_PACKET;
    /*
    Serial.print(F("  → SPS30 error state=0x"));
    Serial.print(state, HEX);
    Serial.println(F(" (nonzero → cannot parse measurements)."));
    */
    
    return;
  }

  // 6) If dataLen == 0, no measurement data is ready
  if (dataLen == 0) {
    error_state = ERROR_STATE_UNEXPECTED_PACKET;
    //Serial.println(F("  → Received empty‐frame (no new data)."));
    return;
  }

  // 7) For “unsigned 16‐bit” format, the datasheet says:
  //    dataLen must be exactly 20 (10 × 2 bytes)
  /*
  if (dataLen != 20) {
    Serial.print(F("  → Unexpected dataLen="));
    Serial.print(dataLen);
    Serial.println(F(" (expect 20)."));
    return;
  }
  */
  /*
  if (dataLen != 40) {
    error_state = ERROR_STATE_UNEXPECTED_PACKET;
    Serial.print(F("  → Unexpected dataLen="));
    Serial.print(dataLen);
    Serial.println(F(" (expect 40)."));
    return;
  }
  */
  

  // 8) Parse the 10 × big-endian IEEE754 floats (each 4 bytes)
  //SPS30Measurement_t meas;
  uint8_t *pdata = &sps30_frame[4];

  meas.mass_PM1_0              = beFloat(pdata,  0);
  meas.mass_PM2_5              = beFloat(pdata,  4);
  meas.mass_PM4_0              = beFloat(pdata,  8);
  meas.mass_PM10               = beFloat(pdata, 12);
  meas.number_PM0_5            = beFloat(pdata, 16);
  meas.number_PM1_0            = beFloat(pdata, 20);
  meas.number_PM2_5            = beFloat(pdata, 24);
  meas.number_PM4_0            = beFloat(pdata, 28);
  meas.number_PM10             = beFloat(pdata, 32);
  meas.typical_particle_size   = beFloat(pdata, 36);

  // Add the timestamp
  meas.timestamp = millis();

  error_state = ERROR_STATE_OK;

  // 9) Print them out (or store/use as needed)
  /*
  Serial.println(F("  → Parsed SPS30 Measurement (unsigned 16-bit):"));
  Serial.print(F("       Mass [µg/m³]:  PM1.0="));   Serial.print(meas.mass_PM1_0);   Serial.print(F(",  PM2.5=")); 
  Serial.print(meas.mass_PM2_5); Serial.print(F(",  PM4.0=")); Serial.print(meas.mass_PM4_0); Serial.print(F(",  PM10=")); 
  Serial.println(meas.mass_PM10);
  Serial.print(F("       Number [#/cm³]: PM0.5="));  Serial.print(meas.number_PM0_5); Serial.print(F(",  PM1.0=")); 
  Serial.print(meas.number_PM1_0); Serial.print(F(",  PM2.5=")); Serial.print(meas.number_PM2_5); Serial.print(F(",  PM4.0=")); 
  Serial.print(meas.number_PM4_0); Serial.print(F(",  PM10=")); Serial.print(meas.number_PM10); 
  Serial.println();
  Serial.print(F("       Typical particle size [nm]: ")); Serial.println(meas.typical_particle_size);
  Serial.print("         Timestamp: "); Serial.println(meas.timestamp);
  Serial.println();
  */
}


void SPS30::exportJSON(Stream &port) {
  // Begin top‐level object
  port.print(F("{\"sensor\":\"sps30\",\"payload\":"));

  // Begin payload object
  port.print(F("{"));

  // “mass” object
  port.print(F("\"mass\":{"));
  port.print(F("\"PM1_0\":"));   port.print(meas.mass_PM1_0, 3);   port.print(F(","));
  port.print(F("\"PM2_5\":"));   port.print(meas.mass_PM2_5, 3);   port.print(F(","));
  port.print(F("\"PM4_0\":"));   port.print(meas.mass_PM4_0, 3);   port.print(F(","));
  port.print(F("\"PM10\":"));    port.print(meas.mass_PM10,  3);
  port.print(F("},"));

  // “number” object
  port.print(F("\"number\":{"));
  port.print(F("\"PM0_5\":"));   port.print(meas.number_PM0_5, 3); port.print(F(","));
  port.print(F("\"PM1_0\":"));   port.print(meas.number_PM1_0, 3); port.print(F(","));
  port.print(F("\"PM2_5\":"));   port.print(meas.number_PM2_5, 3); port.print(F(","));
  port.print(F("\"PM4_0\":"));   port.print(meas.number_PM4_0, 3); port.print(F(","));
  port.print(F("\"PM10\":"));    port.print(meas.number_PM10,  3);
  port.print(F("},"));

  // “timestamp” field
  port.print(F("\"timestamp\":"));
  port.print(meas.timestamp);
  port.print(F(","));

  // error_state field
  port.print(F("\"error_state\":"));
  port.print(error_state);

  // Close payload and top‐level
  port.print(F("}}"));
  port.println();
}


//--------------------------------------------------------------------------------
// Helper: parse big-endian IEEE754 float from pdata at given offset
//--------------------------------------------------------------------------------
float SPS30::beFloat(const uint8_t *pdata, size_t offset) {
  uint32_t asInt = (uint32_t)pdata[offset]   << 24
                 | (uint32_t)pdata[offset+1] << 16
                 | (uint32_t)pdata[offset+2] <<  8
                 | (uint32_t)pdata[offset+3];
  float f;
  memcpy(&f, &asInt, sizeof(f));
  return f;
}
