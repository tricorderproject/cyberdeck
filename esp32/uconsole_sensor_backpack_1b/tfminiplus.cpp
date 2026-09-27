#include <Arduino.h>

// PJ: I have no idea where this code came from.  I might have written it, or it might have come from the internet. 

// TODO: This code essentially has a sync problem -- it tries to read, and hopes that it's on the right boundary (I think).  So it fails a lot, and needs to be made more robust.
bool getTFminiPlusData(int* distance, int* strength) {

  static char i = 0;

  char j = 0;

  int checksum = 0;

  static int rx[9];

  int timeout_count = 0;

  while (timeout_count < 10000) {
  if(Serial1.available()) {  

    rx[i] = Serial1.read();

    if(rx[0] != 0x59) {

      i = 0;

    } else if(i == 1 && rx[1] != 0x59) {

      i = 0;

    } else if(i == 8) {

      for(j = 0; j < 8; j++) {

        checksum += rx[j];

      }

      if(rx[8] == (checksum % 256)) {

        *distance = rx[2] + rx[3] * 256;

        *strength = rx[4] + rx[5] * 256;

        return true;
      }

      i = 0;

    } else {

      i++;

    }

  }  
  }

  return false;

}

 
/*
void setup() {

  Serial.begin(115200);
  Serial1.begin(115200);

}

 

void loop() {

  int distance = 0;

  int strength = 0;

 

  getTFminiPlusData(&distance, &strength);

  while(!distance) {

    getTFminiPlusData(&distance, &strength);

    if(distance) {

      Serial.print(distance);

      Serial.print("cm\t");

      Serial.print("strength: ");

      Serial.println(strength);

    }

  }

}
*/
