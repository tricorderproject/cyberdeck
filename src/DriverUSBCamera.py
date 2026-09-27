# DriverUSBCamera.py

import os
import glob
import time
import threading
import numpy as np
import cv2
import sounddevice as sd


class USBCameraSensor:
    def __init__(self, device_path:str=None, timeout:float=2.0):
        self.device_path = device_path
        self.timeout = timeout

        self.device = None
        self.device_info = None
        self.camera_name = None

        self.audio_device_index = None
        self.audio_device_info = None
        self.audio_sample_rate = 44100
        self.audio_blocksize = 8192
        self.audio_channels = 1
        self.audio_stream = None

        self.latest_audio_block = None
        self.latest_audio_time = None
        self.latest_audio_status = None
        self.audio_lock = threading.Lock()

        self.frame_width = 640
        self.frame_height = 480
        self.frame_fps = 15

        self.enable_autofocus = True
        self.focus_value = None

        self.enable_auto_exposure = True
        self.exposure_value = None

        self.brightness_value = None
        self.contrast_value = None
        self.gain_value = None


    #
    #   Connect/Disconnect
    #

    # Open the device connection
    def connect(self):
        # If a specific video device path was provided, try to use that first
        if (self.device_path is not None):
            self.device = self._connect_to_source(self.device_path)
            if (self.device is None):
                print(f"Error connecting to USB camera on {self.device_path}.")
            else:
                print(f"Connected to USB camera on {self.device_path}.")
            return

        # Otherwise, auto-detect a USB webcam
        detected_path = self._autodetect_camera_source()
        if (detected_path is None):
            print("Error connecting to USB camera: could not auto-detect a camera.")
            self.device = None
            return

        self.device_path = detected_path
        self.device = self._connect_to_source(self.device_path)
        if (self.device is None):
            print(f"Error connecting to USB camera on {self.device_path}.")
        else:
            print(f"Connected to USB camera on {self.device_path}.")


    # Close the device connection
    def disconnect(self):
        if (self.audio_stream is not None):
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
                print("Disconnected from USB camera microphone.")
            except Exception as e:
                print(f"Error disconnecting USB camera microphone: {e}")
            self.audio_stream = None

        if (self.device is not None):
            try:
                self.device.release()
                print("Disconnected from USB camera.")
            except Exception as e:
                print(f"Error disconnecting USB camera: {e}")
            self.device = None


    #
    #   Start-up / initialization sequence
    #

    def initialize(self):
        # Connect to the camera
        self.connect()

        if (self.device is None):
            print("Failed to connect to USB camera.")
            return

        # Configure camera properties
        self.configure_video()

        # Try to attach to the camera microphone
        self.initialize_audio()


    #
    #   Auto-detection / low-level helpers
    #

    def _autodetect_camera_source(self):
        # Prefer Linux /dev/v4l/by-id entries because they often include the USB device name
        by_id_paths = sorted(glob.glob("/dev/v4l/by-id/*"))
        for path in by_id_paths:
            try:
                path_lower = path.lower()

                # Prefer the primary video node and skip metadata/helper nodes
                if ("index0" not in path_lower):
                    continue

                real_path = os.path.realpath(path)
                candidate = self._connect_to_source(real_path)
                if (candidate is None):
                    continue

                candidate.release()

                self.camera_name = os.path.basename(path)
                self.device_info = {
                    "by_id_path": path,
                    "real_path": real_path,
                }
                print(f"Auto-detected USB camera via {path} -> {real_path}")
                return real_path

            except Exception as e:
                print(f"Error probing camera candidate {path}: {e}")

        # Fall back to a small set of direct /dev/videoN nodes
        for path in ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]:
            if (os.path.exists(path) == False):
                continue

            try:
                candidate = self._connect_to_source(path)
                if (candidate is None):
                    continue

                candidate.release()

                self.camera_name = os.path.basename(path)
                self.device_info = {
                    "real_path": path,
                }
                print(f"Auto-detected USB camera via {path}")
                return path

            except Exception as e:
                print(f"Error probing camera candidate {path}: {e}")

        # Final fallback: try a few integer indices only
        for index in [0, 1, 2, 3]:
            try:
                candidate = self._connect_to_source(index)
                if (candidate is None):
                    continue

                candidate.release()

                self.camera_name = f"camera-index-{index}"
                self.device_info = {
                    "index": index,
                }
                print(f"Auto-detected USB camera via OpenCV index {index}")
                return index

            except Exception as e:
                print(f"Error probing camera index {index}: {e}")

        return None


    def _connect_to_source(self, source):
        try:
            cap = cv2.VideoCapture(source, cv2.CAP_V4L2)
            if (cap.isOpened() == False):
                cap.release()
                return None

            return cap
        except Exception as e:
            print(f"Error connecting to USB camera candidate on {source}: {e}")
            return None


    def _set_property(self, prop:int, value):
        if (self.device is None):
            print("USB camera is not connected. Cannot set property.")
            return False

        try:
            ok = self.device.set(prop, value)
            if (ok == False):
                print(f"Warning: failed to set camera property {prop} to {value}.")
            return ok
        except Exception as e:
            print(f"Error setting camera property {prop} to {value}: {e}")
            return False


    def _get_property(self, prop:int):
        if (self.device is None):
            print("USB camera is not connected. Cannot get property.")
            return None

        try:
            return self.device.get(prop)
        except Exception as e:
            print(f"Error getting camera property {prop}: {e}")
            return None


    def _audio_callback(self, indata, frames, time_info, status):
        with self.audio_lock:
            self.latest_audio_block = np.asarray(indata[:, 0], dtype=np.float32).copy()
            self.latest_audio_time = time.time()
            self.latest_audio_status = status


    #
    #   Video / audio configuration
    #

    def configure_video(self):
        if (self.device is None):
            print("USB camera is not connected. Cannot configure video.")
            return

        print("Configuring USB camera video settings...")

        self._set_property(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self._set_property(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self._set_property(cv2.CAP_PROP_FPS, self.frame_fps)
        self._set_property(cv2.CAP_PROP_BUFFERSIZE, 1)

        if (self.enable_autofocus is not None):
            self._set_property(cv2.CAP_PROP_AUTOFOCUS, 1 if (self.enable_autofocus == True) else 0)

        if (self.focus_value is not None):
            self._set_property(cv2.CAP_PROP_FOCUS, self.focus_value)

        if (self.enable_auto_exposure is not None):
            auto_exposure_value = 3 if (self.enable_auto_exposure == True) else 1
            self._set_property(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure_value)

        if (self.exposure_value is not None):
            self._set_property(cv2.CAP_PROP_EXPOSURE, self.exposure_value)

        if (self.brightness_value is not None):
            self._set_property(cv2.CAP_PROP_BRIGHTNESS, self.brightness_value)

        if (self.contrast_value is not None):
            self._set_property(cv2.CAP_PROP_CONTRAST, self.contrast_value)

        if (self.gain_value is not None):
            self._set_property(cv2.CAP_PROP_GAIN, self.gain_value)

        current_width = self._get_property(cv2.CAP_PROP_FRAME_WIDTH)
        current_height = self._get_property(cv2.CAP_PROP_FRAME_HEIGHT)
        current_fps = self._get_property(cv2.CAP_PROP_FPS)

        print(f"Camera configured: {current_width} x {current_height} @ {current_fps} fps")


    def initialize_audio(self):
        try:
            devices = sd.query_devices()
        except Exception as e:
            print(f"Error querying audio devices: {e}")
            return

        selected_index = None

        if (self.camera_name is not None):
            camera_name_lower = str(self.camera_name).lower()
            for i, dev in enumerate(devices):
                name_lower = str(dev["name"]).lower()
                if (dev["max_input_channels"] > 0):
                    if (self._names_look_related(camera_name_lower, name_lower) == True):
                        selected_index = i
                        break

        if (selected_index is None):
            try:
                default_input = sd.default.device[0]
                if (default_input is not None) and (default_input >= 0):
                    selected_index = int(default_input)
            except Exception:
                pass

        if (selected_index is None):
            print("Could not find an input audio device for the USB camera microphone.")
            return

        self.audio_device_index = selected_index
        self.audio_device_info = devices[selected_index]

        default_samplerate = self.audio_device_info.get("default_samplerate", self.audio_sample_rate)
        if (default_samplerate is not None):
            self.audio_sample_rate = int(default_samplerate)

        print(f"Using audio input device: {self.audio_device_info['name']}")
        print(f"Audio sample rate: {self.audio_sample_rate}")

        try:
            self.audio_stream = sd.InputStream(
                device=self.audio_device_index,
                channels=self.audio_channels,
                samplerate=self.audio_sample_rate,
                blocksize=self.audio_blocksize,
                dtype="float32",
                latency="high",
                callback=self._audio_callback,
            )
            self.audio_stream.start()
            print("USB camera microphone stream started.")
        except Exception as e:
            print(f"Error starting USB camera microphone stream: {e}")
            self.audio_stream = None


    def _names_look_related(self, camera_name_lower:str, audio_name_lower:str):
        camera_tokens = [x for x in camera_name_lower.replace("-", " ").replace("_", " ").split() if (len(x) >= 4)]
        for tok in camera_tokens:
            if (tok in audio_name_lower):
                return True
        return False


    #
    #   Specific commands (high-level interface)
    #

    def set_autofocus(self, enabled:bool):
        self.enable_autofocus = enabled
        return self._set_property(cv2.CAP_PROP_AUTOFOCUS, 1 if (enabled == True) else 0)


    def set_focus(self, value:float):
        self.focus_value = value
        return self._set_property(cv2.CAP_PROP_FOCUS, value)


    def set_auto_exposure(self, enabled:bool):
        self.enable_auto_exposure = enabled
        auto_exposure_value = 3 if (enabled == True) else 1
        return self._set_property(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure_value)


    def set_exposure(self, value:float):
        self.exposure_value = value
        return self._set_property(cv2.CAP_PROP_EXPOSURE, value)


    def set_brightness(self, value:float):
        self.brightness_value = value
        return self._set_property(cv2.CAP_PROP_BRIGHTNESS, value)


    def set_contrast(self, value:float):
        self.contrast_value = value
        return self._set_property(cv2.CAP_PROP_CONTRAST, value)


    def set_gain(self, value:float):
        self.gain_value = value
        return self._set_property(cv2.CAP_PROP_GAIN, value)


    def set_resolution(self, width:int, height:int):
        self.frame_width = width
        self.frame_height = height

        ok1 = self._set_property(cv2.CAP_PROP_FRAME_WIDTH, width)
        ok2 = self._set_property(cv2.CAP_PROP_FRAME_HEIGHT, height)
        return (ok1 and ok2)


    def set_fps(self, fps:float):
        self.frame_fps = fps
        return self._set_property(cv2.CAP_PROP_FPS, fps)


    def get_image_frame(self):
        frame_bgr = self.read_valid_frame()
        if (frame_bgr is None):
            return None

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return frame_rgb


    def get_audio_frequency_spectrum(self):
        audio_block = self.read_valid_audio_block()
        if (audio_block is None):
            return None, None

        if (len(audio_block) <= 1):
            return None, None

        window = np.hanning(len(audio_block)).astype(np.float32)
        windowed = audio_block * window

        spectrum = np.fft.rfft(windowed)
        freqs = np.fft.rfftfreq(len(windowed), d=(1.0 / float(self.audio_sample_rate)))
        magnitude = np.abs(spectrum)

        return freqs, magnitude


    #
    #   Data acquisition (low-level)
    #

    def read_valid_frame(self):
        if (self.device is None):
            return None

        start_time = time.time()

        while (True):
            try:
                ok, frame = self.device.read()
                if (ok == True) and (frame is not None):
                    return frame

                if ((time.time() - start_time) > self.timeout):
                    return None

            except Exception as e:
                print(f"Error reading USB camera frame: {e}")
                return None


    def read_valid_audio_block(self):
        if (self.audio_stream is None):
            return None

        with self.audio_lock:
            if (self.latest_audio_block is None):
                return None
            return self.latest_audio_block.copy()


    #
    #   Utility functions
    #

    def get_camera_status(self):
        return {
            "device_path": self.device_path,
            "camera_name": self.camera_name,
            "device_info": self.device_info,
            "audio_device_index": self.audio_device_index,
            "audio_device_info": self.audio_device_info,
            "frame_width": self._get_property(cv2.CAP_PROP_FRAME_WIDTH),
            "frame_height": self._get_property(cv2.CAP_PROP_FRAME_HEIGHT),
            "fps": self._get_property(cv2.CAP_PROP_FPS),
            "autofocus": self._get_property(cv2.CAP_PROP_AUTOFOCUS),
            "focus": self._get_property(cv2.CAP_PROP_FOCUS),
            "auto_exposure": self._get_property(cv2.CAP_PROP_AUTO_EXPOSURE),
            "exposure": self._get_property(cv2.CAP_PROP_EXPOSURE),
            "brightness": self._get_property(cv2.CAP_PROP_BRIGHTNESS),
            "contrast": self._get_property(cv2.CAP_PROP_CONTRAST),
            "gain": self._get_property(cv2.CAP_PROP_GAIN),
            "latest_audio_status": str(self.latest_audio_status),
        }


#
#   Example usage
#

if (__name__ == "__main__"):
    import matplotlib.pyplot as plt

    # Create an instance of the USB camera sensor
    sensor = USBCameraSensor(device_path=None, timeout=2.0)

    # Optional camera settings
    sensor.frame_width = 1280
    sensor.frame_height = 720
    sensor.frame_fps = 30

    sensor.enable_autofocus = True
    sensor.focus_value = None

    sensor.enable_auto_exposure = True
    sensor.exposure_value = None

    # Initialize the sensor
    sensor.initialize()

    print(sensor.get_camera_status())

    plt.ion()

    fig_image, ax_image = plt.subplots()
    fig_spectrum, ax_spectrum = plt.subplots()

    image_artist = None
    spectrum_line = None

    try:
        while (True):
            frame_rgb = sensor.get_image_frame()
            freqs, magnitude = sensor.get_audio_frequency_spectrum()

            if (frame_rgb is not None):
                if (image_artist is None):
                    image_artist = ax_image.imshow(frame_rgb)
                    ax_image.set_title("USB Camera Image")
                    ax_image.axis("off")
                else:
                    image_artist.set_data(frame_rgb)

            if (freqs is not None) and (magnitude is not None):
                if (spectrum_line is None):
                    spectrum_line, = ax_spectrum.plot(freqs, magnitude)
                    ax_spectrum.set_title("USB Camera Microphone Frequency Spectrum")
                    ax_spectrum.set_xlabel("Frequency (Hz)")
                    ax_spectrum.set_ylabel("Magnitude")
                    ax_spectrum.set_xlim(0, min(8000, sensor.audio_sample_rate / 2.0))
                else:
                    spectrum_line.set_xdata(freqs)
                    spectrum_line.set_ydata(magnitude)
                    ax_spectrum.relim()
                    ax_spectrum.autoscale_view(scalex=False, scaley=True)

            plt.pause(0.001)
            time.sleep(0.01)

    finally:
        sensor.disconnect()