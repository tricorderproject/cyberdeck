# DriverESP32Sensors.py

import json
import time
import serial       # from pyserial

import traceback


class SensorsESP32:
    def __init__(self, port:str="/dev/ttyUSB0", baudrate:int=115200, timeout:float=2.0, max_buffer_length:int=1024):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = None
        self.max_buffer_length = max_buffer_length

        # Read buffer
        self._readbuffer = ""

        self.sensor_data = {}

        # ESP32 update modes.  The firmware reads a single character from the
        # serial stream and changes which sensor subset it updates.
        #
        self.update_mode_commands = {
            "normal": "a",
            "all": "a",
            "all_sensors": "a",
            "spectrometer": "s",
            "visible_spectrometer": "s",
            "magnetic_tile": "m",
            "tile": "m",
            "magnetometer": "n",
            "mlx90393": "n",
        }

        self.current_update_mode = None

    #
    #   Connect/Disconnect
    #

    # Open the serial connection
    def connect(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Connected to ESP32 Sensors on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Error connecting to ESP32 Sensors: {e}")
            self.serial_port = None

    # Close the serial connection
    def disconnect(self):
        if (self.serial_port is not None) and (self.serial_port.is_open == True):
            self.serial_port.close()
            print("Disconnected from ESP32 Sensors.")


    #
    #   Start-up / initialization sequence
    #
    def initialize(self):
        # Connect to the device
        self.connect()

        # Wait for the device to be ready (e.g., after reboot)
        time.sleep(1)



    #
    #   ESP32 Update Mode Selection
    #

    def set_update_mode(self, mode:str):
        """
        Select which ESP32 sensor subset should be updated.

        Supported mode names:
            normal / all / all_sensors          -> 'a'
            spectrometer / visible_spectrometer -> 's'
            magnetic_tile / tile                -> 'm'
            magnetometer / mlx90393             -> 'n'

        The command is sent as a single ASCII character with no newline.
        """
        if (mode is None):
            raise ValueError("mode must be a string")

        mode_key = str(mode).strip().lower()
        if (mode_key not in self.update_mode_commands):
            valid_modes = ", ".join(sorted(self.update_mode_commands.keys()))
            raise ValueError(f"Unknown ESP32 update mode '{mode}'. Valid modes: {valid_modes}")

        command = self.update_mode_commands[mode_key]
        self.send_update_mode_command(command)
        self.current_update_mode = mode_key
        return command

    def send_update_mode_command(self, command:str):
        """
        Send a raw one-character update-mode command to the ESP32.
        """
        if (command is None):
            raise ValueError("command must be a single character")

        command = str(command)
        if (len(command) != 1):
            raise ValueError(f"ESP32 update-mode command must be exactly one character, got '{command}'")

        if (self.serial_port is None) or (self.serial_port.is_open == False):
            raise RuntimeError("ESP32 serial port is not connected/open")

        self.serial_port.write(command.encode("ascii"))
        self.serial_port.flush()

    def set_normal_mode(self):
        return self.set_update_mode("normal")

    def set_visible_spectrometer_mode(self):
        return self.set_update_mode("visible_spectrometer")

    def set_magnetic_tile_mode(self):
        return self.set_update_mode("magnetic_tile")

    def set_magnetometer_mode(self):
        return self.set_update_mode("magnetometer")


    #
    #   Polling
    #
    def poll_sensors(self):
        # Read any available lines from the serial port and parse as JSON
        if (self.serial_port is not None) and (self.serial_port.is_open == True):
            try:
                # Read any available serial information into the read buffer
                while (self.serial_port.in_waiting > 0):
                    data = self.serial_port.read(self.serial_port.in_waiting).decode('ascii', errors='ignore')
                    self._readbuffer += data

                # Check if there are whole lines in the read buffer
                while ('\n' in self._readbuffer):
                    line, self._readbuffer = self._readbuffer.split('\n', 1)
                    line = line.strip()
                    if (len(line) > 0):
                        try:
                            # Try to parse the line as JSON
                            sensor_data = json.loads(line)
                            #self.sensor_data = sensor_data
                            print("Received sensor data.")
                            #print(json.dumps(sensor_data, indent=4))

                            # Get the 'sensor' field to determine which sensor this data is from
                            sensor_name = sensor_data.get('sensor', None)
                            if (sensor_name is not None):
                                if (sensor_name not in self.sensor_data):
                                    self.sensor_data[sensor_name] = []
                                print("Received data for sensor: " + str(sensor_name))

                                # Check to see if we've exceeded the buffer length for this sensor, and if so, remove the oldest entry
                                if (len(self.sensor_data[sensor_name]) >= self.max_buffer_length):
                                    print("** Sensor buffer exceeded max length, removing oldest entry (" + str(len(self.sensor_data[sensor_name])) + " entries for sensor " + str(sensor_name) + ")")
                                    self.sensor_data[sensor_name].pop(0)

                                self.sensor_data[sensor_name].append(sensor_data)
                            else:
                                print(f"Received JSON without 'sensor' field: {line}")

                        except json.JSONDecodeError:
                            print(f"Received non-JSON line: {line}")

            except serial.SerialException as e:
                print(f"Error reading from ESP32 Sensors: {e}")
                return

            except Exception as e:
                print(f"Unexpected error while polling sensors: {e}")
                traceback.print_exc()
                return


    #
    #   Get Sensor Data
    #

    def get_most_recent_data(self, sensor_name:str):
        if (sensor_name in self.sensor_data) and (len(self.sensor_data[sensor_name]) > 0):
            return self.sensor_data[sensor_name][-1]
        else:
            print(f"No data available for sensor: {sensor_name} (number of entries: {len(self.sensor_data.get(sensor_name, []))})")
            return None

    def get_all_sensor_data(self, sensor_name:str):
        if (sensor_name in self.sensor_data) and (len(self.sensor_data[sensor_name]) > 0):
            return self.sensor_data[sensor_name]
        else:
            print(f"No data available for sensor: {sensor_name}")
            return None



#
#   Example Usage
#

if __name__ == "__main__":
    # Create an instance of the driver
    sensors = SensorsESP32(port="/dev/ttyUSB0", baudrate=115200, timeout=2.0)

    # Initialize the driver (connect to the device)
    sensors.initialize()

    # Poll sensors in a loop
    try:
        while True:
            sensors.poll_sensors()
            time.sleep(1)  # Poll every 1 second

    except KeyboardInterrupt:
        print("Stopping sensor polling...")

    # Disconnect from the device
    sensors.disconnect()