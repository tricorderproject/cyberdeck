#!/usr/bin/env python3

import argparse
import contextlib
import io
import math
import signal
import threading
import time
from pathlib import Path
from collections import deque

import numpy as np

try:
    import pygame
except Exception as e:
    print(f"pygame import failed: {e}")
    print("Install with: python -m pip install pygame")
    raise

try:
    from DriverESP32Sensors import *
    from DriverPomello import *
    from DriverThermalCamera import *
    from DriverUSBCamera import *
    DRIVERS_AVAILABLE = True
    DRIVER_IMPORT_ERROR = None
except Exception as e:
    DRIVERS_AVAILABLE = False
    DRIVER_IMPORT_ERROR = e


MAX_HISTORY = 240
DETAIL_SCREENS = ["overview", "environment", "magnetic", "cameras", "spectrum", "audio", "gamma", "errors"]

PAGE_TITLES = {
    "overview": "Overview",
    "environment": "Environmental",
    "magnetic": "Magnetic",
    "cameras": "Cameras",
    "spectrum": "Visible Spectrometer",
    "audio": "Audio Spectrum",
    "gamma": "Gamma Spectrum",
    "errors": "Errors / Logs",
}

PAGE_SHORT_NAMES = {
    "overview": "overview",
    "environment": "environment",
    "magnetic": "magnetic",
    "cameras": "cameras",
    "spectrum": "spectrometer",
    "audio": "audio",
    "gamma": "gamma",
    "errors": "errors",
}

ESP32_PORT_DEFAULT = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"
POMELLO_PORT_DEFAULT = "/dev/serial/by-id/usb-Pomelo_Core_00000001-if00"
THERMAL_PORT_DEFAULT = None

BG = (5, 8, 18)
PANEL = (16, 24, 45)
BORDER = (70, 91, 130)
GRID = (40, 55, 82)
TEXT = (229, 238, 255)
MUTED = (132, 151, 179)
DIM = (79, 99, 130)
CYAN = (56, 189, 248)
BLUE = (96, 165, 250)
PURPLE = (168, 85, 247)
PINK = (236, 72, 153)
GREEN = (52, 211, 153)
YELLOW = (250, 204, 21)
ORANGE = (251, 146, 60)
RED = (248, 113, 113)
WHITE = (248, 250, 252)
BLACK = (0, 0, 0)

THERMAL_STOPS = [
    (0.00, (11, 15, 31)),
    (0.10, (31, 42, 114)),
    (0.20, (36, 86, 167)),
    (0.32, (42, 150, 200)),
    (0.45, (67, 205, 162)),
    (0.60, (155, 221, 87)),
    (0.74, (221, 217, 74)),
    (0.86, (240, 163, 43)),
    (0.94, (223, 94, 37)),
    (1.00, (248, 241, 223)),
]

MAG_STOPS = [
    (0.00, (30, 64, 175)),
    (0.50, (248, 250, 252)),
    (1.00, (220, 38, 38)),
]

VISIBLE_SPEC_NM_MIN = 340.0
VISIBLE_SPEC_NM_MAX = 780.0


def safe_get(d:dict, keys:list, default=None):
    cur = d
    for k in keys:
        if (not isinstance(cur, dict)) or (k not in cur):
            return default
        cur = cur[k]
    return cur


def safe_get_any(d:dict, paths:list, default=None):
    for path in paths:
        value = safe_get(d, path, None)
        if (value is not None):
            return value
    return default


def append_history(history_dict:dict, key:str, value):
    if (value is not None):
        try:
            history_dict[key].append(float(value))
        except Exception:
            pass


def current_value(values, default=None):
    if (values is None) or (len(values) == 0):
        return default
    return values[-1]


def format_value(value, fmt:str=".1f", missing:str="--"):
    if (value is None):
        return missing
    if isinstance(value, str):
        return value
    try:
        return format(float(value), fmt)
    except Exception:
        return str(value)


def read_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read().strip()) / 1000.0
    except Exception:
        return None


def make_lut(stops):
    lut = np.zeros((256, 3), dtype=np.uint8)
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        a = int(round(t0 * 255))
        b = int(round(t1 * 255))
        if (b <= a):
            continue
        for j in range(a, b + 1):
            f = (j - a) / max(1, b - a)
            lut[j, 0] = int(round(c0[0] + f * (c1[0] - c0[0])))
            lut[j, 1] = int(round(c0[1] + f * (c1[1] - c0[1])))
            lut[j, 2] = int(round(c0[2] + f * (c1[2] - c0[2])))
    return lut


THERMAL_LUT = make_lut(THERMAL_STOPS)
MAG_LUT = make_lut(MAG_STOPS)


def normalize_array(arr):
    arr = np.asarray(arr, dtype=float)
    finite = arr[np.isfinite(arr)]
    if (finite.size == 0):
        return np.zeros_like(arr, dtype=np.uint8), None, None
    vmin = float(np.min(finite))
    vmax = float(np.max(finite))
    if (vmax <= vmin):
        return np.zeros_like(arr, dtype=np.uint8), vmin, vmax
    norm = (arr - vmin) / (vmax - vmin)
    norm[~np.isfinite(norm)] = 0.0
    idx = np.clip(np.round(norm * 255.0), 0, 255).astype(np.uint8)
    return idx, vmin, vmax


def thermal_to_rgb(frame):
    if (frame is None) or (np.asarray(frame).size == 0):
        return None, None, None
    idx, vmin, vmax = normalize_array(frame)
    return THERMAL_LUT[idx], vmin, vmax


def magnetic_to_rgb(frame):
    if (frame is None) or (np.asarray(frame).size == 0):
        return None, None, None
    arr = np.asarray(frame, dtype=float)
    finite = arr[np.isfinite(arr)]
    if (finite.size == 0):
        return None, None, None
    scale = float(np.max(np.abs(finite)))
    if (scale <= 0.0):
        scale = 1.0
    norm = np.clip((arr / scale + 1.0) * 127.5, 0, 255).astype(np.uint8)
    return MAG_LUT[norm], -scale, scale


def rgb_array_to_surface(rgb):
    if (rgb is None) or (np.asarray(rgb).size == 0):
        return None
    arr = np.asarray(rgb)
    if (arr.ndim == 2):
        arr = np.repeat(arr[:, :, None], 3, axis=2)
    if (arr.shape[2] > 3):
        arr = arr[:, :, :3]
    arr = np.ascontiguousarray(np.clip(arr, 0, 255).astype(np.uint8))
    surf = pygame.surfarray.make_surface(np.swapaxes(arr, 0, 1))
    return surf.convert()


def downsample_values(values, width:int, reducer="max"):
    if (values is None) or (len(values) == 0) or (width <= 0):
        return np.asarray([], dtype=float)
    y = np.asarray(values, dtype=float)
    y = y[np.isfinite(y)]
    if (y.size == 0):
        return np.asarray([], dtype=float)
    if (y.size <= width):
        return y
    bins = np.array_split(y, width)
    if (reducer == "mean"):
        return np.asarray([float(np.mean(b)) if b.size else 0.0 for b in bins])
    return np.asarray([float(np.max(b)) if b.size else 0.0 for b in bins])


class SensorState:
    def __init__(self, args):
        self.args = args
        self.lock = threading.Lock()
        self.io_lock = threading.RLock()
        self.running = False
        self.poll_thread = None
        self.demo_t0 = time.time()
        self.rng = np.random.default_rng(7)

        self.esp32_sensors = None
        self.pomello_sensor = None
        self.thermal_camera = None
        self.usb_camera = None

        self.history = {
            "scd4x_co2": deque(maxlen=MAX_HISTORY),
            "scd4x_temp": deque(maxlen=MAX_HISTORY),
            "scd4x_humidity": deque(maxlen=MAX_HISTORY),
            "bme688_temp": deque(maxlen=MAX_HISTORY),
            "bme688_pressure": deque(maxlen=MAX_HISTORY),
            "bme688_gas": deque(maxlen=MAX_HISTORY),
            "bme688_altitude": deque(maxlen=MAX_HISTORY),
            "mlx_x": deque(maxlen=MAX_HISTORY),
            "mlx_y": deque(maxlen=MAX_HISTORY),
            "mlx_z": deque(maxlen=MAX_HISTORY),
            "mlx_total": deque(maxlen=MAX_HISTORY),
            "sps_pm1": deque(maxlen=MAX_HISTORY),
            "sps_pm25": deque(maxlen=MAX_HISTORY),
            "sps_pm4": deque(maxlen=MAX_HISTORY),
            "sps_pm10": deque(maxlen=MAX_HISTORY),
            "gamma_cpm": deque(maxlen=MAX_HISTORY),
        }

        self.latest = {
            "spectrometer_data": None,
            "pomello_histogram": None,
            "thermal_frame": None,
            "usb_camera_frame": None,
            "usb_audio_freqs": None,
            "usb_audio_magnitude": None,
            "magnetic_tile_raw": None,
            "magnetic_tile_frame": None,
            "magnetic_tile_mode_text": "Relative (1024 ref)",
            "error_messages": [],
            "log_messages": deque(maxlen=16),
            "thermal_seq": 0,
            "camera_seq": 0,
            "magnetic_seq": 0,
        }

        self.magnetic_tile_baseline = None
        self.magnetic_display_mode = "relative"
        self.init_messages = []
        self.page = "overview"

        self.last_demo_poll = 0.0
        self.last_esp32_update_mode = None
        self.last_esp32_poll = 0.0
        self.last_pomello_poll = 0.0
        self.last_thermal_poll = 0.0
        self.last_camera_poll = 0.0
        self.last_audio_poll = 0.0
        self.last_gamma_append = 0.0

    def add_log(self, text:str):
        text = str(text).strip()
        if (len(text) == 0):
            return
        with self.lock:
            self.latest["log_messages"].append(text[:240])

    @contextlib.contextmanager
    def capture_driver_output(self, label:str):
        buf = io.StringIO()
        with self.io_lock:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                yield
        out = buf.getvalue().strip()
        if (out != ""):
            lines = [line.strip() for line in out.splitlines() if line.strip() != ""]
            for line in lines[-4:]:
                self.add_log(f"{label}: {line}")

    def initialize(self):
        if (self.args.demo == True):
            self.init_messages.append("Demo mode enabled; no hardware initialized")
            return

        if (DRIVERS_AVAILABLE == False):
            self.init_messages.append(f"Driver import failed: {DRIVER_IMPORT_ERROR}")
            self.init_messages.append("Falling back to demo mode")
            self.args.demo = True
            return

        try:
            self.esp32_sensors = SensorsESP32(port=self.args.esp32_port, baudrate=115200, max_buffer_length=1024)
            with self.capture_driver_output("ESP32 init"):
                self.esp32_sensors.initialize()
            self.init_messages.append("ESP32 connected")
        except Exception as e:
            self.init_messages.append(f"ESP32 init failed: {e}")
            self.esp32_sensors = None

        try:
            self.pomello_sensor = PomelloRadiationSensor(port=self.args.pomello_port, baudrate=921600)
            with self.capture_driver_output("Pomello init"):
                self.pomello_sensor.initialize()
            self.init_messages.append("Pomello connected")
        except Exception as e:
            self.init_messages.append(f"Pomello init failed: {e}")
            self.pomello_sensor = None

        if (self.args.no_thermal == False):
            try:
                self.thermal_camera = ThermalCameraSensor(port=self.args.thermal_port, timeout=2.0, enable_smoothing=True)
                with self.capture_driver_output("Thermal init"):
                    self.thermal_camera.initialize()
                self.init_messages.append("Thermal connected")
            except Exception as e:
                self.init_messages.append(f"Thermal init failed: {e}")
                self.thermal_camera = None
        else:
            self.init_messages.append("Thermal disabled by --no-thermal")

        if (self.args.no_camera == False):
            try:
                self.usb_camera = USBCameraSensor(device_path=None, timeout=2.0)
                self.usb_camera.frame_width = self.args.camera_width
                self.usb_camera.frame_height = self.args.camera_height
                self.usb_camera.frame_fps = self.args.camera_fps
                self.usb_camera.enable_autofocus = True
                self.usb_camera.enable_auto_exposure = True
                with self.capture_driver_output("USB camera init"):
                    self.usb_camera.initialize()
                self.init_messages.append("USB camera connected")
            except Exception as e:
                self.init_messages.append(f"USB camera init failed: {e}")
                self.usb_camera = None
        else:
            self.init_messages.append("USB camera disabled by --no-camera")

    def start(self):
        if (self.running == True):
            return
        self.running = True
        self.poll_thread = threading.Thread(target=self.poll_loop, daemon=True)
        self.poll_thread.start()

    def stop(self):
        self.running = False
        if (self.poll_thread is not None):
            self.poll_thread.join(timeout=1.0)
        for obj in [self.esp32_sensors, self.pomello_sensor, self.thermal_camera, self.usb_camera]:
            if (obj is not None):
                try:
                    with self.capture_driver_output("disconnect"):
                        obj.disconnect()
                except Exception:
                    pass

    def set_page(self, page:str):
        if (page not in DETAIL_SCREENS):
            return
        with self.lock:
            self.page = page

    def recompute_magnetic_display(self):
        raw = self.latest.get("magnetic_tile_raw", None)
        if (raw is None):
            return
        frame_np = np.asarray(raw, dtype=float)
        if (self.magnetic_display_mode == "absolute"):
            display_data = frame_np
            mode_text = "Absolute"
        else:
            if (self.magnetic_tile_baseline is None):
                display_data = frame_np - 1024.0
                mode_text = "Relative (1024 ref)"
            else:
                display_data = frame_np - self.magnetic_tile_baseline
                mode_text = "Relative (baseline)"
        self.latest["magnetic_tile_frame"] = display_data
        self.latest["magnetic_tile_mode_text"] = mode_text
        self.latest["magnetic_seq"] += 1

    def set_magnetic_baseline(self):
        with self.lock:
            raw = self.latest.get("magnetic_tile_raw", None)
            if (raw is not None):
                self.magnetic_tile_baseline = np.asarray(raw, dtype=float).copy()
                self.recompute_magnetic_display()
                self.latest["log_messages"].append("Magnetic tile baseline captured")

    def clear_magnetic_baseline(self):
        with self.lock:
            self.magnetic_tile_baseline = None
            self.recompute_magnetic_display()
            self.latest["log_messages"].append("Magnetic tile baseline cleared")

    def toggle_magnetic_mode(self):
        with self.lock:
            if (self.magnetic_display_mode == "absolute"):
                self.magnetic_display_mode = "relative"
            else:
                self.magnetic_display_mode = "absolute"
            self.recompute_magnetic_display()
            self.latest["log_messages"].append(f"Magnetic display mode: {self.magnetic_display_mode}")

    def get_esp32_update_mode_for_page(self, page:str):
        if (page == "magnetic"):
            return "magnetic_tile"
        if (page == "spectrum"):
            return "visible_spectrometer"
        return "all"

    def apply_esp32_update_mode_for_page(self, page:str):
        if (self.esp32_sensors is None):
            return

        mode = self.get_esp32_update_mode_for_page(page)
        if (mode == self.last_esp32_update_mode):
            return

        try:
            if hasattr(self.esp32_sensors, "set_update_mode"):
                with self.capture_driver_output("ESP32 mode"):
                    command = self.esp32_sensors.set_update_mode(mode)
                self.last_esp32_update_mode = mode
                self.add_log(f"ESP32 update mode: {mode} ({command})")
            else:
                self.last_esp32_update_mode = mode
                self.add_log("ESP32 driver has no set_update_mode(); update mode unchanged")
        except Exception as e:
            self._set_error("ESP32 update-mode change failed", e)


    def _set_error(self, label:str, exc:Exception):
        msg = f"{label}: {exc}"
        errs = self.latest["error_messages"]
        if (msg not in errs):
            errs.append(msg)
        if (len(errs) > 10):
            del errs[0]

    def poll_loop(self):
        while (self.running == True):
            now = time.time()
            if (self.args.demo == True):
                if ((now - self.last_demo_poll) >= 0.08):
                    self.update_demo(now)
                    self.last_demo_poll = now
                time.sleep(0.01)
                continue

            with self.lock:
                page = self.page

            self.apply_esp32_update_mode_for_page(page)

            esp32_interval = 0.25
            pomello_interval = 0.50
            thermal_interval = None
            camera_interval = None
            audio_interval = None

            if (page == "overview"):
                thermal_interval = 0.75
                camera_interval = 1.00
                audio_interval = 1.50
            elif (page == "cameras"):
                thermal_interval = 0.25
                camera_interval = 0.25
            elif (page == "audio"):
                audio_interval = 0.25
            elif (page == "gamma"):
                pomello_interval = 0.25
            elif (page == "magnetic"):
                esp32_interval = 0.15
            elif (page == "environment"):
                esp32_interval = 0.18
            elif (page == "spectrum"):
                esp32_interval = 0.18

            if (self.esp32_sensors is not None) and ((now - self.last_esp32_poll) >= esp32_interval):
                try:
                    with self.capture_driver_output("ESP32"):
                        self.esp32_sensors.poll_sensors()
                        spectrometer_data = self.esp32_sensors.get_most_recent_data("spec_cd12666ma")
                        magnetic_tile_data = self.esp32_sensors.get_most_recent_data("magnetic_tile")
                        scd4x_data = self.esp32_sensors.get_most_recent_data("scd4x")
                        bme688_data = self.esp32_sensors.get_most_recent_data("bme688")
                        mlx_data = self.esp32_sensors.get_most_recent_data("mlx90393")
                        sps30_data = self.esp32_sensors.get_most_recent_data("sps30")
                    with self.lock:
                        self.latest["spectrometer_data"] = spectrometer_data
                        self.update_histories_from_esp32(scd4x_data, bme688_data, mlx_data, sps30_data)
                        self.update_magnetic_tile(magnetic_tile_data)
                        self.last_esp32_poll = now
                except Exception as e:
                    with self.lock:
                        self._set_error("ESP32 poll failed", e)
                        self.last_esp32_poll = now

            if (self.pomello_sensor is not None) and ((now - self.last_pomello_poll) >= pomello_interval):
                try:
                    with self.capture_driver_output("Pomello"):
                        histogram_pomello = self.pomello_sensor.get_histogram()
                    with self.lock:
                        self.latest["pomello_histogram"] = histogram_pomello
                        self.last_pomello_poll = now
                        if (histogram_pomello is not None) and ((now - self.last_gamma_append) >= 1.0):
                            cpm = self.compute_gamma_cpm(histogram_pomello)
                            if (cpm is not None):
                                self.history["gamma_cpm"].append(cpm)
                                self.last_gamma_append = now
                except Exception as e:
                    with self.lock:
                        self._set_error("Pomello poll failed", e)
                        self.last_pomello_poll = now

            if (thermal_interval is not None) and (self.thermal_camera is not None) and ((now - self.last_thermal_poll) >= thermal_interval):
                try:
                    with self.capture_driver_output("Thermal"):
                        thermal_frame = self.thermal_camera.get_temperature_frame()
                    with self.lock:
                        self.latest["thermal_frame"] = thermal_frame
                        self.latest["thermal_seq"] += 1
                        self.last_thermal_poll = now
                except Exception as e:
                    with self.lock:
                        self._set_error("Thermal camera poll failed", e)
                        self.last_thermal_poll = now

            if (camera_interval is not None) and (self.usb_camera is not None) and ((now - self.last_camera_poll) >= camera_interval):
                try:
                    with self.capture_driver_output("USB camera"):
                        usb_camera_frame = self.usb_camera.get_image_frame()
                    with self.lock:
                        self.latest["usb_camera_frame"] = usb_camera_frame
                        self.latest["camera_seq"] += 1
                        self.last_camera_poll = now
                except Exception as e:
                    with self.lock:
                        self._set_error("USB camera poll failed", e)
                        self.last_camera_poll = now

            if (audio_interval is not None) and (self.usb_camera is not None) and ((now - self.last_audio_poll) >= audio_interval):
                try:
                    with self.capture_driver_output("USB audio"):
                        usb_audio_freqs, usb_audio_magnitude = self.usb_camera.get_audio_frequency_spectrum()
                    with self.lock:
                        self.latest["usb_audio_freqs"] = usb_audio_freqs
                        self.latest["usb_audio_magnitude"] = usb_audio_magnitude
                        self.last_audio_poll = now
                except Exception as e:
                    with self.lock:
                        self._set_error("USB audio poll failed", e)
                        self.last_audio_poll = now

            time.sleep(0.015)

    def compute_gamma_cpm(self, histogram_pomello:dict):
        payload = histogram_pomello.get("payload", {})
        count = payload.get("count", None)
        time_sec = payload.get("time", None)
        if (count is None) or (time_sec is None):
            return None
        try:
            count = float(count)
            time_sec = float(time_sec)
            if (time_sec <= 0.0):
                return None
            return (count / time_sec) * 60.0
        except Exception:
            return None

    def update_histories_from_esp32(self, scd4x_data, bme688_data, mlx_data, sps30_data):
        if (scd4x_data is not None):
            append_history(self.history, "scd4x_co2", safe_get(scd4x_data, ["payload", "atmospheric", "co2_ppm"]))
            append_history(self.history, "scd4x_temp", safe_get(scd4x_data, ["payload", "atmospheric", "temp_c"]))
            append_history(self.history, "scd4x_humidity", safe_get(scd4x_data, ["payload", "atmospheric", "humidity_rh_pct"]))

        if (bme688_data is not None):
            append_history(self.history, "bme688_temp", safe_get_any(bme688_data, [["payload", "environmental", "temp_c"], ["payload", "atmospheric", "temp_c"], ["payload", "magnetic", "temp_c"]]))
            append_history(self.history, "bme688_pressure", safe_get_any(bme688_data, [["payload", "environmental", "pressure_hpa"], ["payload", "atmospheric", "pressure_hpa"], ["payload", "magnetic", "pressure_hpa"]]))
            append_history(self.history, "bme688_gas", safe_get_any(bme688_data, [["payload", "environmental", "gas_resistance_kohm"], ["payload", "atmospheric", "gas_resistance_kohm"], ["payload", "magnetic", "gas_resistance_kohm"]]))
            append_history(self.history, "bme688_altitude", safe_get_any(bme688_data, [["payload", "environmental", "altitude_m"], ["payload", "atmospheric", "altitude_m"], ["payload", "magnetic", "altitude_m"]]))

        if (mlx_data is not None):
            x = safe_get(mlx_data, ["payload", "magnetic", "x_ut"])
            y = safe_get(mlx_data, ["payload", "magnetic", "y_ut"])
            z = safe_get(mlx_data, ["payload", "magnetic", "z_ut"])
            append_history(self.history, "mlx_x", x)
            append_history(self.history, "mlx_y", y)
            append_history(self.history, "mlx_z", z)
            if (x is not None) and (y is not None) and (z is not None):
                append_history(self.history, "mlx_total", math.sqrt((x * x) + (y * y) + (z * z)))

        if (sps30_data is not None):
            append_history(self.history, "sps_pm1", safe_get(sps30_data, ["payload", "mass", "PM1_0"]))
            append_history(self.history, "sps_pm25", safe_get(sps30_data, ["payload", "mass", "PM2_5"]))
            append_history(self.history, "sps_pm4", safe_get(sps30_data, ["payload", "mass", "PM4_0"]))
            append_history(self.history, "sps_pm10", safe_get(sps30_data, ["payload", "mass", "PM10"]))

    def update_magnetic_tile(self, magnetic_tile_data):
        if (magnetic_tile_data is None):
            return
        frame = safe_get(magnetic_tile_data, ["payload", "frame"], None)
        if (not isinstance(frame, list)) or (len(frame) == 0):
            return
        frame_np = np.asarray(frame, dtype=float)
        self.latest["magnetic_tile_raw"] = frame_np
        self.recompute_magnetic_display()
    def update_demo(self, now):
        t = now - self.demo_t0
        with self.lock:
            self.history["scd4x_co2"].append(520 + 80 * math.sin(t * 0.10) + self.rng.normal(0, 3))
            self.history["scd4x_temp"].append(24 + 0.8 * math.sin(t * 0.06) + self.rng.normal(0, 0.05))
            self.history["scd4x_humidity"].append(39 + 5 * math.sin(t * 0.04 + 1.7) + self.rng.normal(0, 0.1))
            self.history["bme688_temp"].append(24.3 + 0.7 * math.sin(t * 0.05))
            self.history["bme688_pressure"].append(1008 + 0.9 * math.sin(t * 0.02))
            self.history["bme688_gas"].append(42 + 9 * math.sin(t * 0.07 + 2.0))
            self.history["bme688_altitude"].append(640 + 1.2 * math.sin(t * 0.02))
            mx = 25 * math.sin(t * 0.65)
            my = 18 * math.cos(t * 0.43)
            mz = 34 + 3 * math.sin(t * 0.31)
            self.history["mlx_x"].append(mx)
            self.history["mlx_y"].append(my)
            self.history["mlx_z"].append(mz)
            self.history["mlx_total"].append(math.sqrt(mx * mx + my * my + mz * mz))
            self.history["sps_pm1"].append(1.0 + abs(0.6 * math.sin(t * 0.13)))
            self.history["sps_pm25"].append(2.2 + abs(1.2 * math.sin(t * 0.09 + 0.8)))
            self.history["sps_pm4"].append(3.5 + abs(1.5 * math.sin(t * 0.05 + 1.6)))
            self.history["sps_pm10"].append(4.5 + abs(2.2 * math.sin(t * 0.04 + 2.1)))
            self.history["gamma_cpm"].append(18 + 3 * math.sin(t * 0.08) + self.rng.normal(0, 0.5))

            px = np.arange(288)
            spec = 120 + 90 * np.exp(-((px - 78) / 16) ** 2) + 170 * np.exp(-((px - 178) / 24) ** 2)
            spec = spec + 25 * np.sin(px / 13 + t * 0.2) + self.rng.normal(0, 4, px.size)
            self.latest["spectrometer_data"] = {"payload": {"spectrum": np.clip(spec, 0, None).tolist()}}

            ch = np.arange(256)
            hist = 4 + 80 * np.exp(-((ch - 76) / 8) ** 2) + 45 * np.exp(-((ch - 169) / 14) ** 2)
            hist = hist + self.rng.poisson(2, ch.size)
            self.latest["pomello_histogram"] = {"payload": {"data": hist.tolist(), "count": float(np.sum(hist)), "time": 60.0, "temperature": 29.5 + 0.4 * math.sin(t * 0.03)}}

            yy, xx = np.mgrid[0:24, 0:32]
            thermal = 24 + 4 * np.exp(-((xx - (13 + 7 * math.sin(t * 0.12))) ** 2 + (yy - 12) ** 2) / 45)
            thermal = thermal + 0.4 * np.sin(xx / 3 + t * 0.4)
            self.latest["thermal_frame"] = thermal
            self.latest["thermal_seq"] += 1

            yy, xx = np.mgrid[0:8, 0:8]
            mag = 70 * np.exp(-((xx - (3.5 + 2.0 * math.sin(t * 0.5))) ** 2 + (yy - 4.0) ** 2) / 5.0)
            mag = mag - 40 * np.exp(-((xx - 2.0) ** 2 + (yy - 2.0) ** 2) / 3.5)
            self.latest["magnetic_tile_raw"] = mag + 1024
            self.recompute_magnetic_display()

            h, w = 180, 240
            yy, xx = np.mgrid[0:h, 0:w]
            r = np.clip(25 + 160 * xx / w + 40 * np.sin(t + yy / 18), 0, 255)
            g = np.clip(40 + 120 * yy / h + 35 * np.cos(t * 0.7 + xx / 22), 0, 255)
            b = np.clip(90 + 80 * np.sin((xx + yy) / 40 + t * 0.3), 0, 255)
            self.latest["usb_camera_frame"] = np.dstack([r, g, b]).astype(np.uint8)
            self.latest["camera_seq"] += 1

            freqs = np.linspace(0, 8000, 160)
            audio = 0.2 + 2.5 * np.exp(-((freqs - 440) / 120) ** 2) + 1.2 * np.exp(-((freqs - 1320) / 190) ** 2)
            audio = audio + 0.15 * self.rng.random(freqs.size)
            self.latest["usb_audio_freqs"] = freqs.tolist()
            self.latest["usb_audio_magnitude"] = audio.tolist()

    def snapshot(self):
        with self.lock:
            latest = dict(self.latest)
            latest["error_messages"] = list(self.latest["error_messages"])
            latest["log_messages"] = list(self.latest["log_messages"])
            return {
                "history": {k: list(v) for (k, v) in self.history.items()},
                "latest": latest,
                "init_messages": list(self.init_messages),
                "page": self.page,
            }


class PygameRenderer:
    def __init__(self, args, sensor_state):
        self.args = args
        self.sensor_state = sensor_state
        self.running = True
        self.surface_cache = {}
        self.text_cache = {}
        self.spectrum_scales = {
            "spectrum": "linear",
            "audio": "linear",
            "gamma": "linear",
        }
        self.status_message = ""
        self.status_until = 0.0
        pygame.init()
        flags = pygame.FULLSCREEN if args.fullscreen else pygame.RESIZABLE
        self.screen = pygame.display.set_mode((args.width, args.height), flags)
        pygame.display.set_caption("Sensor Console")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        self.font_tiny = pygame.font.SysFont("DejaVu Sans", 12)
        self.font_small = pygame.font.SysFont("DejaVu Sans", 15)
        self.font = pygame.font.SysFont("DejaVu Sans", 18)
        self.font_big = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
        self.font_huge = pygame.font.SysFont("DejaVu Sans", 42, bold=True)
        self.bg_surface = self.build_background(self.screen.get_size())

    def build_background(self, size):
        w, h = size
        bg = pygame.Surface(size)
        bg.fill(BG)
        for y in range(h):
            f = y / max(1, h - 1)
            c = (int(BG[0] + f * 8), int(BG[1] + f * 12), int(BG[2] + f * 26))
            pygame.draw.line(bg, c, (0, y), (w, y))
        for x in range(-w, w * 2, 54):
            pygame.draw.line(bg, (12, 25, 48), (x, 0), (x + h, h), 1)
        for x in range(0, w, 80):
            pygame.draw.line(bg, (9, 20, 39), (x, 0), (x, h), 1)
        for y in range(0, h, 80):
            pygame.draw.line(bg, (9, 20, 39), (0, y), (w, y), 1)
        pygame.draw.circle(bg, (12, 32, 58), (int(w * 0.78), int(h * 0.18)), 190, 1)
        pygame.draw.circle(bg, (18, 42, 72), (int(w * 0.78), int(h * 0.18)), 118, 1)
        pygame.draw.circle(bg, (14, 52, 73), (int(w * 0.08), int(h * 0.92)), 230, 1)
        return bg.convert()

    def text(self, s, font, color=TEXT):
        key = (str(s), id(font), color)
        surf = self.text_cache.get(key, None)
        if (surf is None):
            surf = font.render(str(s), True, color)
            if (len(self.text_cache) > 512):
                self.text_cache.clear()
            self.text_cache[key] = surf
        return surf

    def draw_text(self, target, s, pos, font=None, color=TEXT, anchor="topleft"):
        if (font is None):
            font = self.font
        surf = self.text(s, font, color)
        rect = surf.get_rect()
        setattr(rect, anchor, pos)
        target.blit(surf, rect)
        return rect

    def draw_panel(self, rect, title=None, accent=CYAN):
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER, rect, width=1, border_radius=12)
        pygame.draw.rect(self.screen, (accent[0] // 2, accent[1] // 2, accent[2] // 2), (rect.x + 1, rect.y + 1, rect.w - 2, 3), border_radius=2)
        if (title is not None):
            self.draw_text(self.screen, title.upper(), (rect.x + 12, rect.y + 9), self.font_tiny, accent)
        return pygame.Rect(rect.x + 10, rect.y + 28, rect.w - 20, rect.h - 38)

    def get_rgb_surface(self, name, rgb, seq):
        if (rgb is None) or (np.asarray(rgb).size == 0):
            return None
        key = (name, seq)
        surf = self.surface_cache.get(key, None)
        if (surf is not None):
            return surf

        arr = np.asarray(rgb)
        if (name == "camera"):
            # The USB camera is physically mounted at 90 degrees.
            # Rotate the displayed image clockwise without changing stored data.
            arr = np.rot90(arr, k=3)

        surf = rgb_array_to_surface(arr)
        if (len(self.surface_cache) > 24):
            self.surface_cache.clear()
        self.surface_cache[key] = surf
        return surf

    def get_thermal_surface(self, frame, seq):
        key = ("thermal", seq)
        cached = self.surface_cache.get(key, None)
        if (cached is not None):
            return cached
        rgb, vmin, vmax = thermal_to_rgb(frame)
        surf = rgb_array_to_surface(rgb)
        if (surf is not None):
            # Thermal camera is mirrored relative to the physical view.
            # Flip only the displayed surface, not the stored temperature data.
            surf = pygame.transform.flip(surf, True, False)
        if (len(self.surface_cache) > 24):
            self.surface_cache.clear()
        self.surface_cache[key] = (surf, vmin, vmax)
        return surf, vmin, vmax

    def get_magnetic_surface(self, frame, seq):
        key = ("magnetic", seq)
        cached = self.surface_cache.get(key, None)
        if (cached is not None):
            return cached
        rgb, vmin, vmax = magnetic_to_rgb(frame)
        surf = rgb_array_to_surface(rgb)
        if (len(self.surface_cache) > 24):
            self.surface_cache.clear()
        self.surface_cache[key] = (surf, vmin, vmax)
        return surf, vmin, vmax

    def draw_image_fit(self, surf, rect, preserve_aspect=True):
        pygame.draw.rect(self.screen, BLACK, rect, border_radius=6)
        if (surf is None):
            self.draw_text(self.screen, "NO IMAGE", rect.center, self.font, DIM, anchor="center")
            return
        sw, sh = surf.get_size()
        if (sw <= 0) or (sh <= 0):
            return
        if (preserve_aspect == True):
            scale = min(rect.w / sw, rect.h / sh)
            tw = max(1, int(sw * scale))
            th = max(1, int(sh * scale))
        else:
            tw = rect.w
            th = rect.h
        scaled = pygame.transform.scale(surf, (tw, th))
        dst = scaled.get_rect(center=rect.center)
        self.screen.blit(scaled, dst)

    def draw_header(self, snap):
        w, h = self.screen.get_size()
        rect = pygame.Rect(8, 6, w - 16, 36)
        pygame.draw.rect(self.screen, (8, 14, 28), rect, border_radius=12)
        pygame.draw.rect(self.screen, (44, 67, 102), rect, width=1, border_radius=12)
        page = snap["page"]
        page_title = PAGE_TITLES.get(page, page.title())
        cpu = read_cpu_temp()
        cpu_text = "CPU -- C" if (cpu is None) else f"CPU {cpu:.1f} C"
        self.draw_text(self.screen, "Sensor Console", (22, 16), self.font, WHITE)
        self.draw_text(self.screen, page_title, (190, 17), self.font_small, TEXT)
        self.draw_text(self.screen, cpu_text, (390, 17), self.font_small, YELLOW)

        if (self.status_message != "") and (time.time() < self.status_until):
            self.draw_text(self.screen, self.status_message, (500, 17), self.font_tiny, GREEN)
        elif (time.time() >= self.status_until):
            self.status_message = ""

        keys = "1 overview   2 env   3 mag   4 cameras   5 spectrometer   6 audio   7 gamma   8 errors   q quit   Ctrl-S save"
        if (page in self.spectrum_scales):
            keys += "   l log/linear"
        if (page == "magnetic"):
            keys += "   b baseline   m abs/rel   r clear"
        self.draw_text(self.screen, keys, (w - 22, 17), self.font_tiny, MUTED, anchor="topright")
    def draw_status_card(self, rect, title, values, unit, fmt, accent):
        pygame.draw.rect(self.screen, (14, 22, 42), rect, border_radius=12)
        pygame.draw.rect(self.screen, (54, 73, 105), rect, width=1, border_radius=12)
        self.draw_text(self.screen, title.upper(), (rect.x + 12, rect.y + 9), self.font_tiny, MUTED)
        value = current_value(values)
        self.draw_text(self.screen, format_value(value, fmt), (rect.x + 12, rect.y + 27), self.font_big, TEXT)
        self.draw_text(self.screen, unit, (rect.x + 12, rect.y + rect.h - 21), self.font_tiny, accent)
        spark_rect = pygame.Rect(rect.x + 96, rect.y + 15, rect.w - 108, rect.h - 27)
        self.draw_sparkline(spark_rect, values, accent)

    def draw_status_cards(self, history, y0):
        w, h = self.screen.get_size()
        margin = 8
        gap = 8
        card_h = 72
        card_w = (w - 2 * margin - 3 * gap) // 4
        temp_hist = history["scd4x_temp"] if (len(history["scd4x_temp"]) > 0) else history["bme688_temp"]
        cards = [
            ("CO2", history["scd4x_co2"], "ppm", ".0f", GREEN),
            ("Temp", temp_hist, "C", ".1f", RED),
            ("Humidity", history["scd4x_humidity"], "%RH", ".1f", BLUE),
            ("Pressure", history["bme688_pressure"], "hPa", ".1f", CYAN),
            ("PM2.5", history["sps_pm25"], "ug/m3", ".1f", PURPLE),
            ("VOC Gas", history["bme688_gas"], "kohm", ".1f", YELLOW),
            ("Mag Total", history["mlx_total"], "uT", ".1f", GREEN),
            ("Gamma", history["gamma_cpm"], "CPM", ".0f", CYAN),
        ]
        for i, card in enumerate(cards):
            col = i % 4
            row = i // 4
            rect = pygame.Rect(margin + col * (card_w + gap), y0 + row * (card_h + gap), card_w, card_h)
            self.draw_status_card(rect, *card)
        return y0 + 2 * card_h + gap

    def draw_sparkline(self, rect, values, color, fill=False):
        pygame.draw.rect(self.screen, (9, 15, 29), rect, border_radius=6)
        if (values is None) or (len(values) == 0):
            self.draw_text(self.screen, "NO DATA", rect.center, self.font_tiny, DIM, anchor="center")
            return
        y = np.asarray(values[-max(2, min(len(values), rect.w)):], dtype=float)
        if (y.size < 2):
            return
        finite = y[np.isfinite(y)]
        if (finite.size == 0):
            return
        ymin = float(np.min(finite))
        ymax = float(np.max(finite))
        if (ymax <= ymin):
            ymax = ymin + 1.0
        pad = 0.08 * (ymax - ymin)
        ymin -= pad
        ymax += pad
        pts = []
        for i, val in enumerate(y):
            x = rect.x + int(i * (rect.w - 1) / max(1, y.size - 1))
            yy = rect.bottom - 3 - int((val - ymin) / (ymax - ymin) * (rect.h - 7))
            pts.append((x, yy))
        if (fill == True) and (len(pts) > 1):
            poly = [(rect.x, rect.bottom - 2)] + pts + [(rect.right - 1, rect.bottom - 2)]
            pygame.draw.polygon(self.screen, (color[0] // 6, color[1] // 6, color[2] // 6), poly)
        pygame.draw.lines(self.screen, color, False, pts, 2)

    def draw_plot_frame(self, rect, title, accent):
        return self.draw_panel(rect, title, accent)

    def build_plot_rect(self, content_rect, left_pad=48, right_pad=10, top_pad=6, bottom_pad=24):
        return pygame.Rect(
            content_rect.x + left_pad,
            content_rect.y + top_pad,
            max(10, content_rect.w - left_pad - right_pad),
            max(10, content_rect.h - top_pad - bottom_pad),
        )

    def draw_plot_grid(self, plot, x_ticks=5, y_ticks=5):
        for i in range(x_ticks):
            x = plot.x + int(i * (plot.w - 1) / max(1, x_ticks - 1))
            pygame.draw.line(self.screen, GRID, (x, plot.y), (x, plot.bottom), 1)
        for i in range(y_ticks):
            y = plot.bottom - int(i * (plot.h - 1) / max(1, y_ticks - 1))
            pygame.draw.line(self.screen, GRID, (plot.x, y), (plot.right, y), 1)
        pygame.draw.rect(self.screen, (51, 68, 98), plot, width=1)

    def draw_y_ticks(self, plot, vmin, vmax, fmt=".1f", count=5):
        for i in range(count):
            frac = i / max(1, count - 1)
            y = plot.bottom - int(frac * (plot.h - 1))
            val = vmin + frac * (vmax - vmin)
            self.draw_text(self.screen, format_value(val, fmt), (plot.x - 6, y - 6), self.font_tiny, MUTED, anchor="topright")

    def draw_x_labels(self, plot, labels):
        if (labels is None) or (len(labels) == 0):
            return
        for i, label in enumerate(labels):
            x = plot.x + int(i * (plot.w - 1) / max(1, len(labels) - 1))
            self.draw_text(self.screen, label, (x, plot.bottom + 4), self.font_tiny, MUTED, anchor="midtop")

    def linear_tick_labels(self, start, end, count=5, fmt=".0f", suffix=""):
        labels = []
        for i in range(count):
            frac = i / max(1, count - 1)
            val = start + frac * (end - start)
            if (fmt == "kHz"):
                labels.append(f"{val / 1000.0:.1f} kHz")
            else:
                labels.append(f"{format_value(val, fmt)}{suffix}")
        return labels

    def relative_time_labels(self, n_points, seconds_per_point=1.0, count=5):
        if (n_points <= 1):
            return ["now"]
        span = (n_points - 1) * seconds_per_point
        labels = []
        for i in range(count):
            frac = i / max(1, count - 1)
            remaining = span * (1.0 - frac)
            if (i == count - 1):
                labels.append("now")
            elif (remaining >= 120):
                labels.append(f"-{int(round(remaining / 60.0))}m")
            else:
                labels.append(f"-{int(round(remaining))}s")
        return labels

    def draw_line_chart(self, rect, title, values, ylabel, accent, fmt=".1f", x_labels=None, seconds_per_point=None):
        content = self.draw_plot_frame(rect, title, accent)
        seam_x = rect.right - 56
        value = current_value(values)
        self.draw_text(self.screen, format_value(value, fmt), (seam_x, rect.y + 8), self.font, TEXT, anchor="topright")
        self.draw_text(self.screen, ylabel, (seam_x + 4, rect.y + 10), self.font_tiny, MUTED, anchor="topleft")
        if (seconds_per_point is not None):
            x_labels = self.relative_time_labels(len(values), seconds_per_point=seconds_per_point, count=5)
        bottom_pad = 24 if x_labels else 10
        plot = self.build_plot_rect(content, left_pad=48, right_pad=10, top_pad=6, bottom_pad=bottom_pad)
        self.draw_plot_grid(plot)
        if (values is None) or (len(values) < 2):
            self.draw_text(self.screen, "NO DATA", plot.center, self.font, DIM, anchor="center")
            return
        y = np.asarray(values, dtype=float)
        y = y[np.isfinite(y)]
        if (y.size < 2):
            return
        ymin = float(np.min(y))
        ymax = float(np.max(y))
        if (ymax <= ymin):
            ymax = ymin + 1.0
        pad = 0.08 * (ymax - ymin)
        ymin -= pad
        ymax += pad
        self.draw_y_ticks(plot, ymin, ymax, fmt=fmt, count=5)
        if (x_labels):
            self.draw_x_labels(plot, x_labels)
        y = y[-min(y.size, plot.w):]
        pts = []
        for i, val in enumerate(y):
            x = plot.x + int(i * (plot.w - 1) / max(1, y.size - 1))
            yy = plot.bottom - int((val - ymin) / (ymax - ymin) * (plot.h - 1))
            pts.append((x, yy))
        if (len(pts) >= 2):
            pygame.draw.lines(self.screen, accent, False, pts, 2)

    def draw_multi_line_chart(self, rect, title, series, ylabel, fmt=".1f", x_labels=None, seconds_per_point=None):
        content = self.draw_plot_frame(rect, title, CYAN)
        if (seconds_per_point is not None):
            longest = max([len(values) for _, values, _ in series] + [0])
            x_labels = self.relative_time_labels(longest, seconds_per_point=seconds_per_point, count=5)
        plot = self.build_plot_rect(content, left_pad=48, right_pad=10, top_pad=6, bottom_pad=(24 if x_labels else 10))
        vals = []
        for _, values, _ in series:
            if (values is not None) and (len(values) > 0):
                vals.extend(list(values))
        self.draw_plot_grid(plot)
        if (len(vals) == 0):
            self.draw_text(self.screen, "NO DATA", plot.center, self.font, DIM, anchor="center")
            return
        arr = np.asarray(vals, dtype=float)
        arr = arr[np.isfinite(arr)]
        if (arr.size == 0):
            return
        ymin = float(np.min(arr))
        ymax = float(np.max(arr))
        if (ymax <= ymin):
            ymax = ymin + 1.0
        pad = 0.08 * (ymax - ymin)
        ymin -= pad
        ymax += pad
        self.draw_y_ticks(plot, ymin, ymax, fmt=fmt, count=5)
        if (x_labels):
            self.draw_x_labels(plot, x_labels)
        for name, values, color in series:
            if (values is None) or (len(values) < 2):
                continue
            y = np.asarray(values, dtype=float)
            y = y[np.isfinite(y)]
            y = y[-min(y.size, plot.w):]
            if (y.size < 2):
                continue
            pts = []
            for i, val in enumerate(y):
                x = plot.x + int(i * (plot.w - 1) / max(1, y.size - 1))
                yy = plot.bottom - int((val - ymin) / (ymax - ymin) * (plot.h - 1))
                pts.append((x, yy))
            pygame.draw.lines(self.screen, color, False, pts, 2)
        lx = rect.x + 12
        ly = rect.y + 8
        for name, _, color in series:
            self.draw_text(self.screen, name, (lx, ly), self.font_tiny, color)
            lx += 62
        self.draw_text(self.screen, ylabel, (rect.right - 12, rect.y + 10), self.font_tiny, MUTED, anchor="topright")

    def draw_scale_buttons(self, rect, mode):
        bx_w = 52
        bx_h = 18
        gap = 4
        y = rect.y + 7
        x2 = rect.right - 12 - bx_w
        x1 = x2 - gap - bx_w
        linear_rect = pygame.Rect(x1, y, bx_w, bx_h)
        log_rect = pygame.Rect(x2, y, bx_w, bx_h)
        for label, btn_rect, active in [
            ("LINEAR", linear_rect, mode == "linear"),
            ("LOG", log_rect, mode == "log"),
        ]:
            fill = (28, 52, 84) if active else (10, 18, 34)
            border = CYAN if active else BORDER
            pygame.draw.rect(self.screen, fill, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, border, btn_rect, width=1, border_radius=5)
            self.draw_text(self.screen, label, btn_rect.center, self.font_tiny, TEXT if active else MUTED, anchor="center")
        return linear_rect, log_rect

    def save_screenshot(self):
        page = self.sensor_state.snapshot()["page"]
        short_name = PAGE_SHORT_NAMES.get(page, page)
        out_dir = Path("screenshots")
        out_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = out_dir / f"screenshot-{short_name}-{timestamp}.png"
        pygame.image.save(self.screen, str(filename))
        self.status_message = f"Saved screenshot: {filename.name}"
        self.status_until = time.time() + 2.0

    def toggle_spectrum_scale(self, page):
        if (page not in self.spectrum_scales):
            return
        if (self.spectrum_scales[page] == "linear"):
            self.spectrum_scales[page] = "log"
        else:
            self.spectrum_scales[page] = "linear"

    def draw_histogram(self, rect, title, values, ylabel, accent, reducer="max", x_labels=None, scale_mode="linear", show_scale_buttons=False):
        title_text = title if (scale_mode == "linear") else f"{title} (log)"
        content = self.draw_plot_frame(rect, title_text, accent)
        if (show_scale_buttons == True):
            self.draw_scale_buttons(rect, scale_mode)
        plot = self.build_plot_rect(content, left_pad=48, right_pad=10, top_pad=6, bottom_pad=(24 if x_labels else 10))
        self.draw_plot_grid(plot)
        max_bins = max(8, plot.w // 3)
        y_raw = downsample_values(values, max_bins, reducer=reducer)
        if (y_raw.size == 0):
            self.draw_text(self.screen, "NO DATA", plot.center, self.font, DIM, anchor="center")
            return

        y_raw = np.asarray(y_raw, dtype=float)
        y_raw[~np.isfinite(y_raw)] = 0.0
        y_raw = np.clip(y_raw, 0.0, None)
        raw_max = float(np.max(y_raw))
        if (not np.isfinite(raw_max)) or (raw_max <= 0.0):
            raw_max = 1.0

        if (scale_mode == "log"):
            y_plot = np.log10(y_raw + 1.0)
            plot_max = float(np.max(y_plot))
            if (plot_max <= 0.0):
                plot_max = 1.0
            for i in range(5):
                frac = i / 4.0
                yy = plot.bottom - int(frac * (plot.h - 1))
                tick_raw = (10 ** (frac * plot_max)) - 1.0
                self.draw_text(self.screen, format_value(tick_raw, ".0f"), (plot.x - 6, yy - 6), self.font_tiny, MUTED, anchor="topright")
        else:
            y_plot = y_raw
            plot_max = raw_max
            self.draw_y_ticks(plot, 0.0, raw_max, fmt=".0f", count=5)

        if (x_labels):
            self.draw_x_labels(plot, x_labels)

        bar_w = max(1, plot.w // y_plot.size)
        for i, val in enumerate(y_plot):
            bh = int((float(val) / plot_max) * (plot.h - 2))
            x = plot.x + i * bar_w
            bar = pygame.Rect(x, plot.bottom - bh, max(1, bar_w - 1), bh)
            pygame.draw.rect(self.screen, accent, bar)
        y_label_pos = rect.y + 30 if show_scale_buttons else rect.y + 10
        self.draw_text(self.screen, ylabel, (rect.right - 12, y_label_pos), self.font_tiny, MUTED, anchor="topright")
    def draw_thermal_legend(self, rect, vmin, vmax):
        bar_w = 18
        bar = pygame.Rect(rect.x, rect.y, bar_w, rect.h)
        grad = np.zeros((rect.h, bar_w, 3), dtype=np.uint8)
        for yy in range(rect.h):
            idx = 255 - int(255 * yy / max(1, rect.h - 1))
            grad[yy, :, :] = THERMAL_LUT[idx]
        surf = rgb_array_to_surface(grad)
        if (surf is not None):
            self.screen.blit(surf, bar)
        pygame.draw.rect(self.screen, BORDER, bar, 1)
        if (vmin is None) or (vmax is None):
            return
        ticks = [1.0, 0.75, 0.50, 0.25, 0.0]
        for frac in ticks:
            y = rect.y + int((1.0 - frac) * (rect.h - 1))
            temp = vmin + frac * (vmax - vmin)
            pygame.draw.line(self.screen, BORDER, (bar.right + 2, y), (bar.right + 8, y), 1)
            self.draw_text(self.screen, f"{temp:.1f}", (bar.right + 10, y - 6), self.font_tiny, MUTED)

    def draw_compass(self, rect, x, y):
        inner = self.draw_panel(rect, "Heading", BLUE)
        center = inner.center
        radius = min(inner.w, inner.h) // 2 - 12
        pygame.draw.circle(self.screen, (8, 15, 30), center, radius)
        pygame.draw.circle(self.screen, (56, 80, 119), center, radius, 1)
        for label, angle in [("N", -90), ("E", 0), ("S", 90), ("W", 180)]:
            a = math.radians(angle)
            tx = center[0] + int(math.cos(a) * (radius - 16))
            ty = center[1] + int(math.sin(a) * (radius - 16))
            self.draw_text(self.screen, label, (tx, ty), self.font_small, MUTED, anchor="center")
        if (x is None) or (y is None):
            self.draw_text(self.screen, "--", center, self.font_big, DIM, anchor="center")
            return
        heading = float(math.degrees(math.atan2(y, x)))
        if (heading < 0.0):
            heading += 360.0
        a = math.radians(heading - 90)
        tip = (center[0] + int(math.cos(a) * (radius - 24)), center[1] + int(math.sin(a) * (radius - 24)))
        left = (center[0] + int(math.cos(a + 2.55) * 18), center[1] + int(math.sin(a + 2.55) * 18))
        right = (center[0] + int(math.cos(a - 2.55) * 18), center[1] + int(math.sin(a - 2.55) * 18))
        pygame.draw.polygon(self.screen, CYAN, [tip, left, right])
        dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        d = dirs[int(((heading + 22.5) % 360) // 45)]
        self.draw_text(self.screen, f"{heading:.1f} deg {d}", (center[0], inner.bottom - 18), self.font_small, TEXT, anchor="center")

    def draw_overview(self, snap):
        history = snap["history"]
        latest = snap["latest"]
        w, h = self.screen.get_size()
        y = self.draw_status_cards(history, 50) + 10
        margin = 8
        gap = 8
        main_h = h - y - margin
        left_w = int((w - 2 * margin - gap) * 0.40)
        right_w = w - 2 * margin - gap - left_w
        thermal_rect = pygame.Rect(margin, y, left_w, main_h)
        right_x = margin + left_w + gap
        col_w = (right_w - gap) // 2
        row_h = (main_h - 2 * gap) // 3
        rects = []
        for r in range(3):
            for c in range(2):
                rects.append(pygame.Rect(right_x + c * (col_w + gap), y + r * (row_h + gap), col_w, row_h))

        inner = self.draw_panel(thermal_rect, "Thermal Camera", RED)
        thermal_surf, tmin, tmax = self.get_thermal_surface(latest["thermal_frame"], latest["thermal_seq"])
        self.draw_image_fit(thermal_surf, inner, preserve_aspect=True)
        if (tmin is not None):
            self.draw_text(self.screen, f"{tmin:.1f}-{tmax:.1f} C", (thermal_rect.right - 12, thermal_rect.y + 9), self.font_tiny, TEXT, anchor="topright")

        inner = self.draw_panel(rects[0], "Visible Camera", GREEN)
        cam = self.get_rgb_surface("camera", latest["usb_camera_frame"], latest["camera_seq"])
        self.draw_image_fit(cam, inner, preserve_aspect=True)

        inner = self.draw_panel(rects[1], "Magnetic Tile", PURPLE)
        mag_surf, mmin, mmax = self.get_magnetic_surface(latest["magnetic_tile_frame"], latest["magnetic_seq"])
        self.draw_image_fit(mag_surf, inner, preserve_aspect=True)
        self.draw_text(self.screen, latest["magnetic_tile_mode_text"], (rects[1].right - 12, rects[1].y + 9), self.font_tiny, TEXT, anchor="topright")

        spec_y = safe_get(latest["spectrometer_data"], ["payload", "spectrum"], [])
        rad_y = safe_get(latest["pomello_histogram"], ["payload", "data"], [])
        audio_y = latest["usb_audio_magnitude"] if (latest["usb_audio_magnitude"] is not None) else []
        self.draw_histogram(rects[2], "Visible Spectrum", spec_y, "intensity / nm", CYAN, x_labels=self.linear_tick_labels(VISIBLE_SPEC_NM_MIN, VISIBLE_SPEC_NM_MAX, 5, fmt=".0f", suffix=" nm"), scale_mode=self.spectrum_scales["spectrum"])
        self.draw_histogram(rects[3], "Gamma Histogram", rad_y, "counts / channel", YELLOW, x_labels=self.linear_tick_labels(0, max(1, len(rad_y) - 1), 5, fmt=".0f"), scale_mode=self.spectrum_scales["gamma"])
        self.draw_histogram(rects[4], "Audio Spectrum", audio_y, "magnitude / Hz", GREEN, reducer="mean", x_labels=self.linear_tick_labels(0, 8000, 5, fmt="kHz"), scale_mode=self.spectrum_scales["audio"])
        self.draw_multi_line_chart(rects[5], "Particles", [
            ("PM1", history["sps_pm1"], BLUE),
            ("PM2.5", history["sps_pm25"], PURPLE),
            ("PM4", history["sps_pm4"], PINK),
            ("PM10", history["sps_pm10"], ORANGE),
        ], "ug/m3", ".1f")
    def draw_environment(self, snap):
        history = snap["history"]
        w, h = self.screen.get_size()
        margin = 8
        gap = 8
        y = 50
        top_area_h = int((h - y - margin - gap) * 0.66)
        bottom_h = h - y - margin - gap - top_area_h
        col_w = (w - 2 * margin - 2 * gap) // 3
        row_h = (top_area_h - gap) // 2
        items = [
            ("CO2", history["scd4x_co2"], "ppm", GREEN, ".0f"),
            ("Temperature", history["scd4x_temp"] if len(history["scd4x_temp"]) else history["bme688_temp"], "C", RED, ".1f"),
            ("Humidity", history["scd4x_humidity"], "%RH", BLUE, ".1f"),
            ("Pressure", history["bme688_pressure"], "hPa", CYAN, ".1f"),
            ("VOC Gas", history["bme688_gas"], "kohm", YELLOW, ".1f"),
            ("Altitude", history["bme688_altitude"], "m", PURPLE, ".1f"),
        ]
        for i, item in enumerate(items):
            c = i % 3
            r = i // 3
            rect = pygame.Rect(margin + c * (col_w + gap), y + r * (row_h + gap), col_w, row_h)
            self.draw_line_chart(rect, item[0], item[1], item[2], item[3], item[4])
        pm_rect = pygame.Rect(margin, y + top_area_h + gap, w - 2 * margin, bottom_h)
        self.draw_multi_line_chart(pm_rect, "Air Particles", [
            ("PM1", history["sps_pm1"], BLUE),
            ("PM2.5", history["sps_pm25"], PURPLE),
            ("PM4", history["sps_pm4"], PINK),
            ("PM10", history["sps_pm10"], ORANGE),
        ], "ug/m3", ".1f")
    def draw_magnetic(self, snap):
        history = snap["history"]
        latest = snap["latest"]
        w, h = self.screen.get_size()
        margin = 8
        gap = 8
        y = 50
        left_w = int((w - 2 * margin - gap) * 0.52)
        right_w = w - 2 * margin - gap - left_w
        left = pygame.Rect(margin, y, left_w, h - y - margin)
        inner = self.draw_panel(left, "Magnetic Tile", PURPLE)
        mag_surf, mmin, mmax = self.get_magnetic_surface(latest["magnetic_tile_frame"], latest["magnetic_seq"])
        self.draw_image_fit(mag_surf, inner, preserve_aspect=True)
        baseline_text = "baseline set" if (self.sensor_state.magnetic_tile_baseline is not None) else "no baseline"
        self.draw_text(self.screen, f"{latest['magnetic_tile_mode_text']} | {baseline_text}", (left.right - 12, left.y + 9), self.font_tiny, TEXT, anchor="topright")
        x0 = margin + left_w + gap
        compass = pygame.Rect(x0, y, right_w, 190)
        remaining_h = h - y - margin - compass.h - gap
        chart_h = (remaining_h - gap) // 2
        self.draw_compass(compass, current_value(history["mlx_x"]), current_value(history["mlx_y"]))
        self.draw_multi_line_chart(pygame.Rect(x0, compass.bottom + gap, right_w, chart_h), "MLX90393 XYZ", [
            ("X", history["mlx_x"], RED),
            ("Y", history["mlx_y"], GREEN),
            ("Z", history["mlx_z"], BLUE),
        ], "uT", ".1f")
        self.draw_line_chart(pygame.Rect(x0, compass.bottom + gap + chart_h + gap, right_w, chart_h), "Field Total", history["mlx_total"], "uT", CYAN, ".1f")
    def draw_cameras(self, snap):
        latest = snap["latest"]
        w, h = self.screen.get_size()
        margin = 8
        gap = 8
        y = 50
        half_w = (w - 2 * margin - gap) // 2
        rect1 = pygame.Rect(margin, y, half_w, h - y - margin)
        rect2 = pygame.Rect(margin + half_w + gap, y, half_w, h - y - margin)
        inner = self.draw_panel(rect1, "Visible Camera", GREEN)
        cam = self.get_rgb_surface("camera", latest["usb_camera_frame"], latest["camera_seq"])
        self.draw_image_fit(cam, inner, preserve_aspect=True)
        inner = self.draw_panel(rect2, "Thermal Camera", RED)
        thermal_surf, tmin, tmax = self.get_thermal_surface(latest["thermal_frame"], latest["thermal_seq"])
        legend_w = 56
        image_rect = pygame.Rect(inner.x, inner.y, inner.w - legend_w - 6, inner.h)
        legend_rect = pygame.Rect(image_rect.right + 8, inner.y + 6, legend_w - 10, inner.h - 12)
        self.draw_image_fit(thermal_surf, image_rect, preserve_aspect=True)
        self.draw_thermal_legend(legend_rect, tmin, tmax)
        if (tmin is not None):
            self.draw_text(self.screen, f"min {tmin:.1f} C    max {tmax:.1f} C", (rect2.right - 12, rect2.y + 9), self.font_tiny, TEXT, anchor="topright")
    def draw_spectrum(self, snap):
        latest = snap["latest"]
        w, h = self.screen.get_size()
        margin = 8
        y = 50
        spec_y = safe_get(latest["spectrometer_data"], ["payload", "spectrum"], [])
        mode = self.spectrum_scales["spectrum"]
        self.draw_histogram(
            pygame.Rect(margin, y, w - 2 * margin, h - y - margin),
            "Visible Spectrometer",
            spec_y,
            "intensity / nm",
            CYAN,
            x_labels=self.linear_tick_labels(VISIBLE_SPEC_NM_MIN, VISIBLE_SPEC_NM_MAX, 5, fmt=".0f", suffix=" nm"),
            scale_mode=mode,
            show_scale_buttons=True,
        )
    def draw_audio(self, snap):
        latest = snap["latest"]
        w, h = self.screen.get_size()
        margin = 8
        y = 50
        audio_y = latest["usb_audio_magnitude"] if (latest["usb_audio_magnitude"] is not None) else []
        max_hz = 8000
        if latest["usb_audio_freqs"] is not None and len(latest["usb_audio_freqs"]) > 0:
            try:
                max_hz = float(latest["usb_audio_freqs"][-1])
            except Exception:
                pass
        mode = self.spectrum_scales["audio"]
        self.draw_histogram(
            pygame.Rect(margin, y, w - 2 * margin, h - y - margin),
            "Audio Spectrum",
            audio_y,
            "magnitude / Hz",
            GREEN,
            reducer="mean",
            x_labels=self.linear_tick_labels(0, max_hz, 5, fmt="kHz"),
            scale_mode=mode,
            show_scale_buttons=True,
        )
    def draw_gamma(self, snap):
        history = snap["history"]
        latest = snap["latest"]
        w, h = self.screen.get_size()
        margin = 8
        gap = 8
        y = 50
        left_w = 360
        left = pygame.Rect(margin, y, left_w, h - y - margin)
        right = pygame.Rect(margin + left_w + gap, y, w - 2 * margin - gap - left_w, h - y - margin)
        inner = self.draw_panel(left, "Pomello", YELLOW)
        payload = safe_get(latest["pomello_histogram"], ["payload"], {})
        rows = [
            ("Count", safe_get(payload, ["count"], None), "counts", ".0f"),
            ("Acq time", safe_get(payload, ["time"], None), "s", ".1f"),
            ("Sensor temp", safe_get(payload, ["temperature"], None), "C", ".2f"),
            ("CPM", current_value(history["gamma_cpm"]), "counts/min", ".1f"),
        ]
        ty = inner.y + 8
        for name, value, unit, fmt in rows:
            self.draw_text(self.screen, name, (inner.x + 8, ty), self.font_small, MUTED)
            self.draw_text(self.screen, f"{format_value(value, fmt)} {unit}", (inner.right - 8, ty), self.font, TEXT, anchor="topright")
            ty += 42
        spark = pygame.Rect(inner.x + 8, ty + 12, inner.w - 16, 160)
        self.draw_line_chart(spark, "CPM Trend", history["gamma_cpm"], "CPM", YELLOW, ".1f", seconds_per_point=1.0)
        rad_y = safe_get(latest["pomello_histogram"], ["payload", "data"], [])
        mode = self.spectrum_scales["gamma"]
        self.draw_histogram(
            right,
            "Gamma Spectrum",
            rad_y,
            "counts / channel",
            YELLOW,
            x_labels=self.linear_tick_labels(0, max(1, len(rad_y) - 1), 5, fmt=".0f"),
            scale_mode=mode,
            show_scale_buttons=True,
        )
    def draw_errors(self, snap):
        w, h = self.screen.get_size()
        margin = 8
        rect = pygame.Rect(margin, 50, w - 2 * margin, h - 58)
        inner = self.draw_panel(rect, "Status / Errors / Logs", RED)
        messages = []
        for msg in snap["init_messages"]:
            messages.append(("init", msg, CYAN))
        for msg in snap["latest"]["error_messages"]:
            messages.append(("error", msg, RED))
        for msg in snap["latest"]["log_messages"]:
            messages.append(("log", msg, MUTED))
        if (len(messages) == 0):
            self.draw_text(self.screen, "No status messages", inner.topleft, self.font, MUTED)
            return
        y = inner.y + 4
        for kind, msg, color in messages[-22:]:
            self.draw_text(self.screen, kind.upper(), (inner.x + 4, y), self.font_tiny, color)
            self.draw_text(self.screen, msg, (inner.x + 82, y), self.font_small, TEXT)
            y += 24
            if (y > inner.bottom - 24):
                break

    def handle_event(self, event):
        if (event.type == pygame.QUIT):
            self.running = False
        elif (event.type == pygame.VIDEORESIZE):
            if (self.args.fullscreen == False):
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.bg_surface = self.build_background(self.screen.get_size())
                self.surface_cache.clear()
        elif (event.type == pygame.KEYDOWN):
            page = self.sensor_state.snapshot()["page"]
            if (event.key == pygame.K_s) and (event.mod & pygame.KMOD_CTRL):
                self.save_screenshot()
            elif (event.key == pygame.K_q) or (event.key == pygame.K_ESCAPE):
                self.running = False
            elif (event.key == pygame.K_1):
                self.sensor_state.set_page("overview")
            elif (event.key == pygame.K_2):
                self.sensor_state.set_page("environment")
            elif (event.key == pygame.K_3):
                self.sensor_state.set_page("magnetic")
            elif (event.key == pygame.K_4):
                self.sensor_state.set_page("cameras")
            elif (event.key == pygame.K_5):
                self.sensor_state.set_page("spectrum")
            elif (event.key == pygame.K_6):
                self.sensor_state.set_page("audio")
            elif (event.key == pygame.K_7):
                self.sensor_state.set_page("gamma")
            elif (event.key == pygame.K_8):
                self.sensor_state.set_page("errors")
            elif (page in self.spectrum_scales) and (event.key == pygame.K_l):
                self.toggle_spectrum_scale(page)
            elif (page == "magnetic") and (event.key == pygame.K_b):
                self.sensor_state.set_magnetic_baseline()
            elif (page == "magnetic") and (event.key == pygame.K_r):
                self.sensor_state.clear_magnetic_baseline()
            elif (page == "magnetic") and (event.key == pygame.K_m):
                self.sensor_state.toggle_magnetic_mode()
    def draw(self, snap):
        self.screen.blit(self.bg_surface, (0, 0))
        self.draw_header(snap)
        page = snap["page"]
        if (page == "environment"):
            self.draw_environment(snap)
        elif (page == "magnetic"):
            self.draw_magnetic(snap)
        elif (page == "cameras"):
            self.draw_cameras(snap)
        elif (page == "spectrum"):
            self.draw_spectrum(snap)
        elif (page == "audio"):
            self.draw_audio(snap)
        elif (page == "gamma"):
            self.draw_gamma(snap)
        elif (page == "errors"):
            self.draw_errors(snap)
        else:
            self.draw_overview(snap)
        pygame.display.flip()
    def run(self):
        while (self.running == True):
            for event in pygame.event.get():
                self.handle_event(event)
            snap = self.sensor_state.snapshot()
            self.draw(snap)
            self.clock.tick(max(1, self.args.fps))
        pygame.quit()


def parse_args():
    parser = argparse.ArgumentParser(description="Lightweight Pygame UI for uConsole Backpack sensors")
    parser.add_argument("--esp32-port", default=ESP32_PORT_DEFAULT)
    parser.add_argument("--pomello-port", default=POMELLO_PORT_DEFAULT)
    parser.add_argument("--thermal-port", default=THERMAL_PORT_DEFAULT)
    parser.add_argument("--no-thermal", action="store_true")
    parser.add_argument("--no-camera", action="store_true")
    parser.add_argument("--camera-width", type=int, default=320)
    parser.add_argument("--camera-height", type=int, default=240)
    parser.add_argument("--camera-fps", type=int, default=5)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=680)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--demo", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    sensor_state = SensorState(args)
    renderer = PygameRenderer(args, sensor_state)

    stop_requested = False

    def handle_sigint(signum, frame):
        nonlocal stop_requested
        stop_requested = True
        renderer.running = False

    signal.signal(signal.SIGINT, handle_sigint)

    sensor_state.initialize()
    sensor_state.start()

    try:
        renderer.run()
    finally:
        sensor_state.stop()


if (__name__ == "__main__"):
    main()
