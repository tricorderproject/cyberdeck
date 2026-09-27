# DriverPomello.py

import json
import time
import serial       # from pyserial



class PomelloRadiationSensor:
    def __init__(self, port:str="/dev/ttyACM0", baudrate:int=921600, timeout:float=2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_port = None

        self.system_info = None
        self.config = None
        self.system_memory = None

    #
    #   Connect/Disconnect
    #

    # Open the serial connection
    def connect(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Connected to Pomello Radiation Sensor on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Error connecting to Pomello Radiation Sensor: {e}")
            self.serial_port = None

    # Close the serial connection
    def disconnect(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("Disconnected from Pomello Radiation Sensor.")


    #
    #   Start-up / initialization sequence
    #
    def initialize(self):
        # Connect to the device
        self.connect()

        # Wait for the device to be ready (e.g., after reboot)
        time.sleep(1)

        # Reboot
        #self.command_reboot()

        # Send these specific initialization commands:
        # z
        # 56411.816895
        # 6-122.66
        # t250
        # w-2024
        # x
        # Send the above initialization commands in sequence. Use the straight serial writes, not send_command.
        #self.deactivate_detector()   # z
        self.serial_port.write("z\n".encode('ascii'))   # z
        time.sleep(0.1)
        #self.send_command("56411.816895")   # 56411.816895
        self.serial_port.write("56411.816895\n".encode('ascii'))   # 56411.816895
        time.sleep(0.1)
        #self.send_command("6-122.66")   # 6-122.66
        self.serial_port.write("6-122.66\n".encode('ascii'))   # 6-122.66
        time.sleep(0.1)
        #self.send_command("t250")   # t250
        self.serial_port.write("t250\n".encode('ascii'))   # t250
        time.sleep(0.1)
        #self.send_command("w-2024")   # w-2024
        self.serial_port.write("w-2024\n".encode('ascii'))   # w-2024
        time.sleep(0.1)
        # self.send_command("x")   # x
        self.serial_port.write("x\n".encode('ascii'))   # x
        time.sleep(0.5)

        # Read any available information in the serial buffer to clear it out
        while (self.serial_port.in_waiting > 0):
            data = self.serial_port.read(self.serial_port.in_waiting).decode('ascii', errors='ignore')
            print(f"Initial serial data: {data}")
            time.sleep(0.1)


        # # Optionally, get system info or configuration to verify communication
        # self.system_info = self.command_get_system_info()
        # if (self.system_info is not None):
        #     print("System Information:")
        #     print(json.dumps(self.system_info, indent=4))
        # else:
        #     print("Failed to retrieve system information.")

        # # Configuration
        # self.config = self.command_get_config()
        # if (self.config is not None):
        #     print("Configuration:")
        #     print(json.dumps(self.config, indent=4))
        # else:
        #     print("Failed to retrieve configuration.")

        # # # Read the system memory
        # # self.system_memory = self.command_read_parameters()
        # # if (self.system_memory is not None):
        # #     print("System Memory:")
        # #     print(json.dumps(self.system_memory, indent=4))
        # # else:
        # #     print("Failed to read system memory.")

        # # Activate the detector
        # self.activate_detector()




    #
    #   Sending commands and receiving data (low-level)
    #

    def send_command(self, command:str, json_response:bool=False):
        if (self.serial_port is not None) and (self.serial_port.is_open == True):
            try:
                # Send the ASCII command
                self.serial_port.write(command.encode('ascii'))
                print(f"Sent command: {command}")
            except serial.SerialException as e:
                print(f"Error sending command: {e}")
        else:
            print("Serial port is not open. Cannot send command.")
            return None

        # Read the serial data until a newline character is received
        try:
            response = self.serial_port.readline().decode('ascii').strip()
            print(f"Received response: {response}")
            if (json_response == False):
                # Plain string response
                return response
            else:
                # Try to parse JSON response
                try:
                    json_data = json.loads(response)
                    return json_data
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    return None

        except serial.SerialException as e:
            print(f"Error reading response: {e}")
            return None



    #
    #   Specific commands (high-level interface)
    #

    # System-level commands

    # Command: reboot the device
    # def command_reboot(self):
    #     response = self.send_command("e")
    #     # Wait for 2 seconds
    #     time.sleep(2)

    # Command: Get system information
    def command_get_system_info(self):
        response = self.send_command("s", json_response=True)
        return response

    # Command: Get configuration
    def command_get_config(self):
        response = self.send_command("c", json_response=True)
        return response

    def command_read_parameters(self):
        response = self.send_command("r", json_response=True)
        return response


    # Sensing commands
    def activate_detector(self):
        response = self.send_command("x", json_response=True)
        return response

    def deactivate_detector(self):
        response = self.send_command("z", json_response=True)
        return response


    def get_histogram(self):
        response = self.send_command("h", json_response=True)
        return response


    # Note: Starts a new counter after reading the current dose rate.
    def get_counts_per_minute(self):
        response = self.send_command("g", json_response=False)
        # Parse as a float
        try:
            cpm_value = float(response)
            return cpm_value
        except ValueError as e:
            print(f"Error parsing CPM value: {e}")
            return None

    # Note: Starts a new counter after reading the current dose rate.
    def get_dose_rate(self):
        response = self.send_command("u", json_response=False)
        # Parse as a float
        try:
            dose_rate_value = float(response)
            return dose_rate_value
        except ValueError as e:
            print(f"Error parsing dose rate value: {e}")
            return None

    def get_dosimetry(self):
        response = self.send_command("m", json_response=True)
        return response





#
#   Example usage
#

if __name__ == "__main__":
    # Create an instance of the PomelloRadiationSensor
    sensor = PomelloRadiationSensor(port="/dev/ttyACM0", baudrate=921600, timeout=2.0)

    # Initialize the sensor (connect, reboot, get info, etc.)
    sensor.initialize()

    # # Read the histogram every 5 seconds for 60 seconds (1 minute)    (Plain text)
    # for i in range(12):
    #     histogram = sensor.get_histogram()
    #     print(f"Histogram at {i*5} seconds:")
    #     print(json.dumps(histogram, indent=4))
    #     time.sleep(5)

    # Matplotlib

    # Example data:
    #{"type":"spectrum", "payload":{"sn":"1BF4BB77515450434B202020FF141901","threshold":250,"count":528,"ecal":[-2.055550e+02,3.188124e+00,3.734000e-04],"temperature":26.64844,"time":53,"data":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,3,6,4,1,0,5,4,7,2,6,8,5,9,11,11,8,14,14,18,14,15,12,10,10,7,10,7,13,8,7,10,10,8,7,7,10,11,7,9,6,12,10,6,5,2,4,9,4,3,7,3,3,2,2,1,0,3,7,0,4,5,3,0,3,1,3,7,4,2,2,3,0,2,4,2,2,1,1,0,0,2,1,0,1,0,0,0,0,0,1,1,1,4,0,0,0,0,0,1,1,0,1,2,1,0,0,0,0,0,0,0,0,0,1,2,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,0,1,0,2,0,0,0,0,0,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]}}

    import json
    import time
    import matplotlib.pyplot as plt

    plt.ion()
    fig, ax = plt.subplots()
    fig.show()

    for i in range(12):
        histogram = sensor.get_histogram()
        print(f"Histogram at {i*5} seconds:")
        print(json.dumps(histogram, indent=4))

        if (histogram is not None):
            histogram_data = histogram.get("payload", {}).get("data", [])

            ax.cla()

            if (len(histogram_data) > 0):
                ax.bar(range(len(histogram_data)), histogram_data)
                ax.set_title(f"Histogram at {i*5} seconds")
                ax.set_xlabel("Channel")
                ax.set_ylabel("Counts")
                ax.set_ylim(0, max(histogram_data) * 1.1)

            fig.canvas.draw()
            fig.canvas.flush_events()

        time.sleep(5)

    plt.ioff()
    plt.show()


    # Disconnect when done
    sensor.disconnect()