# DriverThermalCamera.py

import time
import numpy as np

from senxor import list_senxor, connect



class ThermalCameraSensor:
    def __init__(self, port:str=None, timeout:float=2.0, enable_smoothing:bool=True):
        self.port = port
        self.timeout = timeout
        self.enable_smoothing = enable_smoothing

        self.device = None
        self.device_info = None
        self.module_type = None

        # On-device MI48 filtering
        self.enable_device_temporal = False
        self.enable_device_rolling = True
        self.device_filter_setting_1 = 125
        self.device_filter_setting_2 = 2

        # Optional host-side spatial smoothing
        self.use_spatial_smooth = self.enable_smoothing

    #
    #   Connect/Disconnect
    #

    # Open the device connection
    def connect(self):
        # If a specific port was provided, try to use that first
        if (self.port is not None):
            self.device = self._connect_to_port(self.port)
            if (self.device is None):
                print(f"Error connecting to Thermal Camera on {self.port}.")
            return

        # Otherwise, auto-detect the thermal camera from available Senxor serial devices
        detected_port = self._autodetect_thermal_camera_port()
        if (detected_port is None):
            print("Error connecting to Thermal Camera: could not auto-detect a thermal camera.")
            self.device = None
            return

        self.port = detected_port
        self.device = self._connect_to_port(self.port)
        if (self.device is None):
            print(f"Error connecting to Thermal Camera on {self.port}.")
        else:
            print(f"Connected to Thermal Camera on {self.port}.")


    # Close the device connection
    def disconnect(self):
        if (self.device is not None):
            try:
                self.device.close()
                print("Disconnected from Thermal Camera.")
            except Exception as e:
                print(f"Error disconnecting from Thermal Camera: {e}")


    #
    #   Start-up / initialization sequence
    #

    def initialize(self):
        # Connect to the device
        self.connect()

        if (self.device is None):
            print("Failed to connect to Thermal Camera.")
            return

        # Configure optional on-device filtering
        if (self.enable_smoothing == True):
            try:
                self.configure_device_filtering()
            except Exception as e:
                print(f"Warning: failed to configure on-device filtering: {e}")

        # Start the thermal stream
        try:
            self.device.start_stream()
            print("Thermal stream started.")
        except Exception as e:
            print(f"Error starting thermal stream: {e}")


    #
    #   Auto-detection / low-level helpers
    #

    def _autodetect_thermal_camera_port(self):
        try:
            devices = list_senxor("serial")
            print(f"Detected Senxor serial devices: {devices}")
        except Exception as e:
            print(f"Error listing Senxor serial devices: {e}")
            return None

        if (devices is None) or (len(devices) == 0):
            return None

        for devinfo in devices:
            port_name = getattr(devinfo, "port", None)
            if (port_name is None):
                continue

            candidate = self._connect_to_port(port_name)
            if (candidate is None):
                continue

            try:
                module_type = candidate.get_module_type()
                print(f"Candidate device on {port_name} reports module type: {module_type}")

                if (self._is_supported_thermal_module(module_type) == True):
                    try:
                        candidate.close()
                    except Exception:
                        pass
                    return port_name

            except Exception as e:
                print(f"Error probing candidate device on {port_name}: {e}")

            try:
                candidate.close()
            except Exception:
                pass

        return None


    def _connect_to_port(self, port:str):
        try:
            devices = list_senxor("serial")
        except Exception as e:
            print(f"Error listing Senxor serial devices: {e}")
            return None

        matching_devinfo = None
        for devinfo in devices:
            if (getattr(devinfo, "port", None) == port):
                matching_devinfo = devinfo
                break

        if (matching_devinfo is None):
            print(f"Could not find Senxor device info for port {port}.")
            return None

        try:
            device = connect(matching_devinfo)
            self.module_type = device.get_module_type()
            self.device_info = matching_devinfo
            print(f"Connected to thermal camera candidate on {port} with module type {self.module_type}.")
            return device
        except Exception as e:
            print(f"Error connecting to thermal camera candidate on {port}: {e}")
            return None


    def _is_supported_thermal_module(self, module_type:str):
        if (module_type is None):
            return False

        module_type_upper = str(module_type).upper()

        # Known Meridian / Senxor thermal module families
        if (module_type_upper.startswith("MI") == True):
            return True

        return False


    def _try_methods(self, methods:list, *args):
        last_err = None
        for meth in methods:
            if (hasattr(self.device, meth) == True):
                try:
                    return meth, getattr(self.device, meth)(*args)
                except Exception as e:
                    last_err = e

        if (last_err is not None):
            raise last_err

        raise AttributeError(f"No matching methods found: {methods}")


    def write_reg(self, reg:int, value:int):
        meth, out = self._try_methods(
            ["write_register", "write_reg", "set_register", "reg_write", "write_u8", "write8"],
            reg, value
        )
        return meth, out


    def read_reg(self, reg:int):
        meth, out = self._try_methods(
            ["read_register", "read_reg", "get_register", "reg_read", "read_u8", "read8"],
            reg
        )
        return meth, out


    def write_reg16(self, reg_lo:int, value:int):
        value = int(value) & 0xFFFF
        lo = value & 0xFF
        hi = (value >> 8) & 0xFF
        meth1, _ = self.write_reg(reg_lo, lo)
        meth2, _ = self.write_reg(reg_lo + 1, hi)
        return meth1, meth2


    #
    #   On-device filtering configuration
    #

    def configure_device_filtering(self):
        if (self.device is None):
            print("Thermal device is not connected. Cannot configure filtering.")
            return

        REG_FILTER_CONTROL = 0xD0
        REG_FILTER_SETTING_1 = 0xD1
        REG_FILTER_SETTING_2 = 0xD3

        BIT_TEMPORAL_ENABLE = 1 << 0
        BIT_TEMPORAL_INIT = 1 << 1
        BIT_ROLL_AVG_ENABLE = 1 << 2

        print("Configuring on-device thermal filtering...")

        control = 0
        if (self.enable_device_temporal == True):
            control |= BIT_TEMPORAL_ENABLE
        if (self.enable_device_rolling == True):
            control |= BIT_ROLL_AVG_ENABLE

        m1, m2 = self.write_reg16(REG_FILTER_SETTING_1, self.device_filter_setting_1)
        print(f"FILTER_SETTING_1 <- {self.device_filter_setting_1} via {m1}/{m2}")

        m3, _ = self.write_reg(REG_FILTER_SETTING_2, int(self.device_filter_setting_2) & 0xFF)
        print(f"FILTER_SETTING_2 <- {self.device_filter_setting_2} via {m3}")

        m4, _ = self.write_reg(REG_FILTER_CONTROL, control)
        print(f"FILTER_CONTROL <- {control} via {m4}")

        if (self.enable_device_temporal == True):
            m5, _ = self.write_reg(REG_FILTER_CONTROL, control | BIT_TEMPORAL_INIT)
            m6, _ = self.write_reg(REG_FILTER_CONTROL, control)
            print(f"TEMPORAL_INIT pulse via {m5}/{m6}")


    #
    #   Data acquisition (low-level)
    #

    def read_valid_frame(self):
        if (self.device is None):
            print("Thermal device is not connected. Cannot read frame.")
            return None

        while (True):
            try:
                header, frame = self.device.read()
                if (frame is not None):
                    return np.asarray(frame, dtype=np.float32)
            except Exception as e:
                print(f"Error reading thermal frame: {e}")
                return None


    #
    #   Specific commands (high-level interface)
    #

    def get_temperature_frame(self):
        frame = self.read_valid_frame()
        if (frame is None):
            return None

        if (self.use_spatial_smooth == True):
            frame = self.mean3x3(frame)

        return frame


    #
    #   Utility functions
    #

    def mean3x3(self, img:np.ndarray):
        p = np.pad(img, 1, mode="edge")
        return (
            p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
            p[1:-1, :-2] + p[1:-1, 1:-1] + p[1:-1, 2:] +
            p[2:, :-2] + p[2:, 1:-1] + p[2:, 2:]
        ) / 9.0





#
#   Example usage
#

#
#   Example usage
#

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Create an instance of the ThermalCameraSensor
    sensor = ThermalCameraSensor(port=None, timeout=2.0, enable_smoothing=True)

    # Initialize the sensor (connect, configure filtering, start stream)
    sensor.initialize()

    plt.ion()
    fig, ax = plt.subplots()
    im = None

    try:
        while (True):
            frame = sensor.get_temperature_frame()
            if (frame is None):
                continue

            if (im is None):
                im = ax.imshow(frame, cmap="inferno")
                plt.colorbar(im, ax=ax)
            else:
                im.set_data(frame)
                im.set_clim(float(np.min(frame)), float(np.max(frame)))

            ax.set_title(
                f"Thermal Camera Frame | Shape: {frame.shape} | "
                f"Min: {frame.min():.2f} C | Max: {frame.max():.2f} C"
            )

            plt.pause(0.001)

    finally:
        sensor.disconnect()