# Open Source Science Tricorder Cyberdeck

Explore alien planets with... the open source science tricorder cyberdeck!

<a href="https://youtube.com/shorts/MCvRtOt6pII"><img src="media/youtube_preview.jpg" width="640" alt="Watch the Open Source Science Tricorder Cyberdeck on YouTube"></a>

# What is this

This is the Github Repository for the **Open Source Science Tricorder Cyberdeck**, an open-source hardware tricorder-like device similar in function to some of the science tricorder devices from the science fiction series Star Trek.  These devices essentially pack a large number of scientific sensors into small hand-held devices, with the (science fiction) intent being that they would be broadly useful for exploring alien worlds, and making new scientific discoveries.


# Table of Contents

- [What is this](#what-is-this)
- [Pictures](#pictures)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Sensor/Hardware List](#sensorhardware-list)
  - [UConsole](#uconsole)
  - [Main Sensors](#main-sensors)
- [Custom PCBs](#custom-pcbs)
  - [PCB: Hamamatsu Microspectrometer Breakout](#pcb-hamamatsu-microspectrometer-breakout)
  - [PCB: ESP32 Breakout](#pcb-esp32-breakout)
  - [PCB: USB Hub Breakout](#pcb-usb-hub-breakout)
- [3D Printed Components](#3d-printed-components)
  - [3D Print: Main Body](#3d-print-main-body)
  - [3D Print: Back Plate](#3d-print-back-plate)
  - [3D Print: Magnetometer Top and Bottom](#3d-print-magnetometer-top-and-bottom)
  - [3D Print: Power Switch](#3d-print-power-switch)
- [Physical Assembly Video](#physical-assembly-video)
- [Firmware (ESP32)](#firmware-esp32)
- [User Interface (Python/UConsole)](#user-interface-pythonuconsole)
- [Design Philosophy and Iterations](#design-philosophy-and-iterations)
  - [Where it was coming from: The Arducorder Mini](#where-it-was-coming-from-the-arducorder-mini)
  - [Iteration 8: Attaching something to an iPhone](#iteration-8-attaching-something-to-an-iphone)
  - [Iteration 9: Teensycorder: Trying to make something that looked like a BlackBerry](#iteration-9-teensycorder-trying-to-make-something-that-looked-like-a-blackberry)
  - [Iteration 10: T-Deck-Corder](#iteration-10-t-deck-corder)
  - [Iteration 11: Initial Cyberdeck explorations with the BTree](#iteration-11-initial-cyberdeck-explorations-with-the-btree)
  - [Iteration 12: A smaller Cyberdeck with the Clockwork Pi PicoCalc](#iteration-12-a-smaller-cyberdeck-with-the-clockwork-pi-picocalc)
  - [Iteration 13: The Open Source Science Tricoder Cyberdeck](#iteration-13-the-open-source-science-tricoder-cyberdeck)
- [Errata](#errata)
  - [Things that are real errors](#things-that-are-real-errors)
  - [Things that I just don't like, or that aren't implemented yet](#things-that-i-just-dont-like-or-that-arent-implemented-yet)
- [AI Usage](#ai-usage)
- [License](#license)
- [Warranty](#warranty)
- [Contact](#contact)

# Pictures

| Main Screen | Spectrometer Screen | Magnetic imager in use (1) | Magnetic imager in use (2) |
| :---: | :---: | :---: | :---: |
| <a href="pictures/introductory_image1.png"><img src="pictures/introductory_image1.png" width="180" alt="Introductory image 1"></a> | <a href="pictures/introductory_image2.png"><img src="pictures/introductory_image2.png" width="180" alt="Introductory image 2"></a> | <a href="pictures/magtile_functioning1.png"><img src="pictures/magtile_functioning1.png" width="180" alt="Magnetic imaging tile in use"></a> | <a href="pictures/magtile_functioning2.png"><img src="pictures/magtile_functioning2.png" width="180" alt="Magnetic imaging tile in use"></a> |
| **Main body with components** | **Main body and back cover** | **Assembled (from back)** | |
| <a href="pictures/main_body_with_components.png"><img src="pictures/main_body_with_components.png" width="180" alt="Main body with components installed"></a> | <a href="pictures/main_body_and_back_cover.png"><img src="pictures/main_body_and_back_cover.png" width="180" alt="Main body and back cover, opened"></a> | <a href="pictures/assembled_from_back.png"><img src="pictures/assembled_from_back.png" width="180" alt="Assembled, viewed from the back"></a> | |

# Frequently Asked Questions

**Q1: What is a tricorder?**

A tricorder is a fictional device from the TV series Star Trek, that characters (like Spock) would take with them when they traveled to alien planets.  The tricorder is essentially like a box full of sensors, that would tell them all sorts of things about the environments they would travel to -- like detecting lifeforms, helping them make discoveries, or solve whatever challenges they faced.  There are nominally two kinds of tricorders in the shows -- medical tricorders (that they use for medical diagnosis), and the science tricorders, which they use for scientific/exploratory tasks. 

**Q2. What can it sense?**

This currently has the following sensing capabilities:
- **Thermal Imaging:** a 80x62 Waveshare imager, paired with a regular visible USB camera
- **Visible Spectroscopy:** a Hamamatsu C12666MA microspectrometer, with 256 spectral channels between 340nm and 780nm (in practice, the spectral resolution is about 15nm)
- **Magnetic Field Imager:** An 8x8 (64 pixel) magnetic field camera, provided by the Sparkfun Magnetic Imaging Tile. In practice this can go up to about 20KHz (i.e. 20,000 frames per second). This is also paired with a regular magnetometer (MLX90393) for magnetic field strength and direction.
- **Radiation Spectroscopy:** Where previous open source science tricorders have included radiation sensors, this version includes the Pomelo radiation spectroscopy detector, which uses a scintillation crystal and can differentiate energy levels.
- **Environmental Sensors:** CO2 level, VOC level, Air particulate matter (e.g. PM1/2.5/4/10), ambient temperature, pressure, and humidity.

**Q3: What is a cyberdeck?**

A cyberdeck is the name for essentially small handheld consoles (that include small screens and keyboards), that frequently run full operating systems, and that are often designed to be hackable/modified.  This build is based on the [UConsole by Clockwork Pi](https://www.clockworkpi.com/home-uconsole), which uses a Raspberry Pi compute module -- so it runs linux, and has several cores, about 4GB of RAM, and lots of eMMC storage. 

**Q4: Are there videos showing it functioning?**

Yes, [here is a video on Youtube](https://youtube.com/shorts/MCvRtOt6pII) showing its main functionality. 

**Q5: Is there a video of it being assembled/the inside?**

Yes!  [Here is a video of the inside being put together](https://youtube.com/shorts/LsJ3JqqFUqU), component by component.

**Q6: What does open source mean in the context of open hardware?**

Open hardware is like open source software, except that it is the designs for the device that are openly shared/distributed.  The software/firmware for the device is also included. 

**Q7: Can I build this?**

The honest answer is -- maybe.  This is a prototype, not a product, and there are lots of rough edges.  Historically, most of the utility from the past releases of the open source science tricorders seems to be educational, inspirational (i.e. a real tricorder-like device!), or derivatives (e.g. folks using part of the designs for their own work).  The devices are quite complex to build, and quite expensive.  

**Q8: Why did you build this?**

I grew up watching Star Trek, and my first career choice was always space explorer -- it just turned out that I was born a little early for that to be a common occupation.  But we're not going to get there just sitting around -- we make the future ourselves, so let's build the technology to become future explorers, and make new discoveries together.

**Q9: Who was this made by?**

The Open Source Science Tricorder Project is an open-source educational outreach by Dr. Peter Jansen, a professor at the University of Arizona.  You can learn more about me [here](https://cognitiveai.org/).

**Q10: How many past open source science tricoders have their been?**

I have made about a dozen designs, but only four (including this cyberdeck) have been official 'releases' with significant documentation, the others are generally iterations or prototypes (and some of the failed prototypes for this cyberdeck design are shown in the section below, since it's always exciting to see the development process!). I used to post a design blog on the process, but I am a little busy these days, and don't have a lot of free time, so it now takes me longer to build these things than I am willing to admit. 

The past major releases are the [Mark 1](https://tricorderproject.org/tricorder-mark1.html) and [Mark2 2](https://tricorderproject.org/tricorder-mark2.html) in 2012, the [Arducorder Mini](https://hackaday.io/project/1395-open-source-science-tricorder) in 2014, and then this Cyberdeck in 2026.  In the interim, I also worked on other educational open source hardware projects, like the open source computed tomography (CT) scanners. 

**Q11: How much did this Cyberdeck cost to build?**

The UConsole itself, CM4 compute module, and associated HackerGadgets extension boards, are likely around $300-$400, while the components and build here are likely around $1000.  The visible microspectrometer and the pomelo radiation spectrometer are by far the most expensive components.

# Sensor/Hardware List

The following is the core hardware used in this device, including links to datasheets/etc.

## UConsole

| Component | Description | Link |
| --- | --- | --- |
| UConsole | Clockwork Pi UConsole | [ClockworkPi](https://www.clockworkpi.com/home-uconsole) |
| UConsole Extension | Internal USB Hub, CM5 adapter, battery board | [Hacker Gadgets](https://hackergadgets.com/products/uconsole-upgrade-kit) |

## Main Sensors

| Component | Description | Link |
| --- | --- | --- |
| Thermal Camera | Waveshare Long-wave IR Camera (80x62, USB C) | [Waveshare](https://www.waveshare.com/thermal-camera.htm?sku=25288) |
| USB Camera | Waveshare IMX378 12MP | [Waveshare](https://www.waveshare.com/imx378-12mp-usb-camera-a.htm) |
| Microspectrometer | Hamamatsu C12666MA | [Hamamatsu](https://www.hamamatsu.com/us/en/product/optical-sensors/spectrometers/mini-spectrometer/C12666MA.html) |
| Radiation Sensor | Pomelo Spectroscopic Radiation Detector | [Crowd Supply](https://www.crowdsupply.com/pomelo-instrumentation/pomelo) |
| Air Particle Sensor | Sensirion Particulate Matter Sensor SPS30 | [Sensirion](https://sensirion.com/products/catalog/SPS30) |
| Magnetic Imaging Tile | SparkFun Magnetic Imaging Tile - 8x8 | [SparkFun](https://www.sparkfun.com/sparkfun-magnetic-imaging-tile-8x8.html) |
| Magnetometer | MLX90393 Breakout | [SparkFun](https://www.sparkfun.com/sparkfun-triple-axis-magnetometer-breakout-mlx90393-qwiic.html) |
| CO2 Sensor | SCD40 CO2/Temp/Humidity Breakout | [SparkFun](https://www.sparkfun.com/sparkfun-co2-humidity-and-temperature-sensor-scd40-qwiic.html) |
| Environmental Sensor | BME680 Temp/Pressure/Humidity/VOC | [SparkFun](https://www.sparkfun.com/sparkfun-environmental-sensor-breakout-bme680-qwiic.html) |
| QWIIC Hub | SparkFun Qwiic MultiPort | [SparkFun](https://www.sparkfun.com/sparkfun-qwiic-multiport.html) |

In addition to the hardware above, a handful of custom PCBs are used (described below).

# Custom PCBs

While effort was made to try and have everything in the device be off-the-shelf for this build, a handful of boards were used to make things a little more compact. 

## PCB: Hamamatsu Microspectrometer Breakout

This is a small breakout for the Hamamatsu CD12666MA microspectrometer, that primarily provides a low-profile connector, an op-amp buffer, and handful of filtering passives to help keep the power clean. 

| Board (front) | Board (back) | PCB (top) | PCB (bottom) |
| :---: | :---: | :---: | :---: |
| <a href="hardware/spectrometer/spectrometer_board_picture1.png"><img src="hardware/spectrometer/spectrometer_board_picture1.png" width="180" alt="Spectrometer breakout, front"></a> | <a href="hardware/spectrometer/spectrometer_board_picture2.png"><img src="hardware/spectrometer/spectrometer_board_picture2.png" width="180" alt="Spectrometer breakout, back"></a> | <a href="hardware/spectrometer/spectrometer_board_top.png"><img src="hardware/spectrometer/spectrometer_board_top.png" width="180" alt="Spectrometer breakout PCB render, top"></a> | <a href="hardware/spectrometer/spectrometer_board_bottom.png"><img src="hardware/spectrometer/spectrometer_board_bottom.png" width="180" alt="Spectrometer breakout PCB render, bottom"></a> |
| **Reflow (toaster oven)** | | | |
| <a href="pictures/pcb_in_toaster_oven.JPG"><img src="pictures/pcb_in_toaster_oven.JPG" width="180" alt="Spectrometer breakout PCB being reflowed in a toaster oven"></a> | | | |

**Design files (EAGLE 9.6.2):** [Schematic (PDF)](hardware/spectrometer/spectrometer-breakout-1c2.pdf) &middot; [Schematic (.sch)](hardware/spectrometer/spectrometer-breakout-1c2.sch) &middot; [Board (.brd)](hardware/spectrometer/spectrometer-breakout-1c2.brd) &middot; [Parts list](hardware/spectrometer/spectrometer-breakout-1b2-partslist.txt)

## PCB: ESP32 Breakout

This is an ESP32 breakout that provides a handy connection between the UConsole (over USB) to most of the other (non-USB) sensors.  The ESP32 board itself is the [Sparkfun ESP32-WROOM USB C](https://www.sparkfun.com/sparkfun-thing-plus-esp32-wroom-usb-c.html). On the left there are small-form connectors for the spectrometer, magnetic imaging tile, and a QWIIC I2C connector.  On the right side are two standard 0.1-spaced headers, one for communicating with the SPS30 air particle sensor, and the other is open, and is intended for a light source for the visible spectrometer. 

| Board | PCB (top) | PCB (bottom) |
| :---: | :---: | :---: |
| <a href="hardware/esp32_main_board/esp32_main_board_picture.png"><img src="hardware/esp32_main_board/esp32_main_board_picture.png" width="180" alt="ESP32 breakout board"></a> | <a href="hardware/esp32_main_board/esp32_main_board_top.png"><img src="hardware/esp32_main_board/esp32_main_board_top.png" width="180" alt="ESP32 breakout PCB render, top"></a> | <a href="hardware/esp32_main_board/esp32_main_board_bottom.png"><img src="hardware/esp32_main_board/esp32_main_board_bottom.png" width="180" alt="ESP32 breakout PCB render, bottom"></a> |

**Design files (EAGLE 9.6.2):** [Schematic (PDF)](hardware/esp32_main_board/clockwork-backpack-1a5.pdf) &middot; [Schematic (.sch)](hardware/esp32_main_board/clockwork-backpack-1a5.sch) &middot; [Board (.brd)](hardware/esp32_main_board/clockwork-backpack-1a5.brd) &middot; [Parts list](hardware/esp32_main_board/clockwork-backpack-1a5-partslist.txt)

## PCB: USB Hub Breakout

This is a breakout for a low-profile USB hub. USB connectors are enormous, and so this further breaks out the [Adafruit CH334F Mini 4-Port USB Hub breakout](https://www.adafruit.com/product/5997) to small JST connectors.  These, unfortunately, are the same JST connectors used by the QWIIC system, which is not a good design decision, so you need to be careful that you're not connecting QWIIC connectors to these 5V usb connections. 

| Board | PCB (top) | PCB (bottom) |
| :---: | :---: | :---: |
| <a href="hardware/usb_hub/usb_hub_board_picture.png"><img src="hardware/usb_hub/usb_hub_board_picture.png" width="180" alt="USB hub breakout board"></a> | <a href="hardware/usb_hub/usb_hub_board_top.png"><img src="hardware/usb_hub/usb_hub_board_top.png" width="180" alt="USB hub breakout PCB render, top"></a> | <a href="hardware/usb_hub/usb_hub_board_bottom.png"><img src="hardware/usb_hub/usb_hub_board_bottom.png" width="180" alt="USB hub breakout PCB render, bottom"></a> |

**Design files (EAGLE 9.6.2):** [Schematic (PDF)](hardware/usb_hub/usb-hub-1b.pdf) &middot; [Schematic (.sch)](hardware/usb_hub/usb-hub-1b.sch) &middot; [Board (.brd)](hardware/usb_hub/usb-hub-1b.brd)

# 3D Printed Components

The enclosure and sensor mounts are 3D printed. The models are authored in OpenSCAD, and both the source and exported STLs are included below.

## 3D Print: Main Body

This is the main physical component, where nearly all of the sensors mount to. It replaces the back of the uConsole, and screws to the uConsole using four M4 screws at the four corners.  Brass inserts, primarily M2.5 (but a few M2 and M3) are used to allow other components to mount to this print.

| Model | With inserts | With components |
| :---: | :---: | :---: |
| <a href="openscad/main_body.png"><img src="openscad/main_body.png" width="180" alt="Main body model render"></a> | <a href="pictures/main_body_with_inserts.png"><img src="pictures/main_body_with_inserts.png" width="180" alt="Main body with heat-set inserts"></a> | <a href="pictures/main_body_with_components.png"><img src="pictures/main_body_with_components.png" width="180" alt="Main body with components installed"></a> |

**Design files (OpenSCAD):** [Model (.stl)](openscad/main_body.stl) &middot; [Source (.scad)](openscad/osst_cyberdeck_sept2026.scad)

## 3D Print: Back Plate

The back plate mounts onto the main body, and also allows a handful of environmental sensors to be mounted. These use the Sparkfun breakout mounting pattern (which is nominally about 25x25mm). It also contains the Sparkfun QWIIC hub, which provides additional QWIIC connectors for the ESP32 breakout. 

| Model | With inserts | With components (1) | With components (2) |
| :---: | :---: | :---: | :---: |
| <a href="openscad/back_cover.png"><img src="openscad/back_cover.png" width="180" alt="Back plate model render"></a> | <a href="pictures/back_cover_with_inserts.png"><img src="pictures/back_cover_with_inserts.png" width="180" alt="Back plate with heat-set inserts"></a> | <a href="pictures/back_cover_with_components1.png"><img src="pictures/back_cover_with_components1.png" width="180" alt="Back plate with components installed"></a> | <a href="pictures/back_cover_with_components2.png"><img src="pictures/back_cover_with_components2.png" width="180" alt="Back plate with components installed"></a> |

**Design files (OpenSCAD):** [Model (.stl)](openscad/back_cover.stl) &middot; [Source (.scad)](openscad/osst_cyberdeck_sept2026.scad)

## 3D Print: Magnetometer Top and Bottom

This is a (mostly) clamshell design that encloses the magnetic imaging tile, and the magnetometer breakout board.  A handful of brass inserts are used to keep the two sides of the clamshell together. A (very technical) piece of folded paper is used to prevent the magnetometer and magnetic imaging tile boards from short circuiting each other.  The bottom of this piece also includes a hidden duct, that allows the exhaust from the SPS30 air particle sensor to leave the sensor at a right angle, away from the inlet.

| Model (front) | Model (back) | Step 1 | Step 2 |
| :---: | :---: | :---: | :---: |
| <a href="openscad/magtile_front.png"><img src="openscad/magtile_front.png" width="180" alt="Magnetometer front model render"></a> | <a href="openscad/magtile_back.png"><img src="openscad/magtile_back.png" width="180" alt="Magnetometer back model render"></a> | <a href="pictures/magtile_step1.png"><img src="pictures/magtile_step1.png" width="180" alt="Magnetometer assembly step 1"></a> | <a href="pictures/magtile_step2.png"><img src="pictures/magtile_step2.png" width="180" alt="Magnetometer assembly step 2"></a> |
| **Step 3** | **Step 4** | **Step 5** | **Step 6** |
| <a href="pictures/magtile_step3.png"><img src="pictures/magtile_step3.png" width="180" alt="Magnetometer assembly step 3"></a> | <a href="pictures/magtile_step4.png"><img src="pictures/magtile_step4.png" width="180" alt="Magnetometer assembly step 4"></a> | <a href="pictures/magtile_step5.png"><img src="pictures/magtile_step5.png" width="180" alt="Magnetometer assembly step 5"></a> | <a href="pictures/magtile_step6.png"><img src="pictures/magtile_step6.png" width="180" alt="Magnetometer assembly step 6"></a> |
| **Step 7** | **Example Function** | | |
| <a href="pictures/magtile_step7.png"><img src="pictures/magtile_step7.png" width="180" alt="Magnetometer assembly step 7"></a> | <a href="pictures/magtile_functioning1.png"><img src="pictures/magtile_functioning1.png" width="180" alt="Magnetometer tile functioning example"></a> | | |

**Design files (OpenSCAD):** [Model, front (.stl)](openscad/magtile_front.stl) &middot; [Model, back (.stl)](openscad/magtile_back.stl) &middot; [Source (.scad)](openscad/osst_cyberdeck_sept2026.scad)

## 3D Print: Power Switch

The uConsole has a somewhat hidden power switch, that becomes partically covered by the magnetometer/magnetic imaging tile print above.  This very handy print sits inside the side loop of the magnetic imaging tile print, and when you press it, it presses the real power button. 

| Model | Step 1 | Step 2 |
| :---: | :---: | :---: |
| <a href="openscad/powerbutton.png"><img src="openscad/powerbutton.png" width="180" alt="Power switch model render"></a> | <a href="pictures/powerswitch_step1.png"><img src="pictures/powerswitch_step1.png" width="180" alt="Power switch assembly step 1"></a> | <a href="pictures/powerswitch_step2.png"><img src="pictures/powerswitch_step2.png" width="180" alt="Power switch assembly step 2"></a> |

**Design files (OpenSCAD):** [Model (.stl)](openscad/powerbutton.stl) &middot; [Source (.scad)](openscad/powerbutton.scad)

# Physical Assembly Video

There's a lot of components in this device, and this short video of stills shows how most of them fit together. 

<a href="https://youtube.com/shorts/LsJ3JqqFUqU"><img src="media/youtube_preview_assembly.jpg" width="640" alt="Watch the assembly video on YouTube"></a>

# Firmware (ESP32)

The ESP32 firmware essentially periodically polls the various sensors (that are not themselves USB sensors), and then sends the measurements from those sensors down a USB-to-Serial connection to the uConsole.  The packets themselves are in `JSONL` format, like below, so they're very easy for whatever software you have on the uConsole to parse them.  For example:

```
{"sensor":"scd4x","payload":{"atmospheric":{"co2_ppm":612,"temp_c":23.4,"humidity_rh_pct":41.2},"timestamp":184532,"error_state":0}}
{"sensor":"mlx90393","payload":{"magnetic":{"x_ut":12.85,"y_ut":-31.42,"z_ut":45.10},"timestamp":184611,"error_state":0}}
{"sensor":"sps30","payload":{"mass":{"PM1_0":2.113,"PM2_5":2.472,"PM4_0":2.601,"PM10":2.665},"number":{"PM0_5":14.201,"PM1_0":16.744,"PM2_5":16.920,"PM4_0":16.951,"PM10":16.963},"timestamp":184702,"error_state":0}}
{"sensor":"magnetic_tile","payload":{"frame":[[2011,2015,...],[2009,2012,...],...],"timestamp":184730,"error_state":0}}
```

Each line is one packet: a `sensor` name, and a `payload` containing that sensor's readings, a `timestamp` (milliseconds since the ESP32 booted), and an `error_state` (0 = OK). The same format is used for the spectrometer (`spec_cd12666ma`, a 256-channel `spectrum` array), the BME688 environmental sensor (`bme688`), and a one-off `firmware` packet sent at boot with the firmware version and build time.

The ESP32 firmware is in: [esp32/uconsole_sensor_backpack_1b/uconsole_sensor_backpack_1b.ino](esp32/uconsole_sensor_backpack_1b/uconsole_sensor_backpack_1b.ino) (an Arduino sketch, with the per-sensor drivers in the same folder).

# User Interface (Python/UConsole)

The user interface on the uConsole polls the various sensors, and displays their readings in a simple user interface.  The user currently selects which screen they'd like to view using the number keys (1-7), and some of the screens have additional functionality, like allowing the user to take baseline measurements (as in for the magnetic imaging tile). 

The interface itself is written in Python, using `pygame` for rendering.

The user interface main entrypoint is here: [src/UserInterfacePygame.py](src/UserInterfacePygame.py) (see [runme.sh](runme.sh), which launches it).


# Design Philosophy and Iterations 

The design philosophy I wanted to explore with this series of iterations of the *open source science tricorder* project was to make the designs easier for others to replicate, nominally by minimizing reliance on custom printed circuit boards and other complex manufacturing processes.  Because most of the complexity comes from displays, input, and so forth, I ended up exploring this in the context of using other devices to supply the input/output, while trying to "bolt" sensors onto them.  In the end, I'm not entirely sure I met the goal -- and the device is much larger than it needs to be, because of all the space required to have all the sensors be off-the-shelf -- but ultimately, I'm pretty happy with it. 

What you mostly see is the end design, but this took **many** iterations over quite a few years to get to where it is.  Here is a sneak peak at some of those design iterations. 

## Where it was coming from: The Arducorder Mini

The Arducorder mini is a beautifully designed but entirely custom device, described here: [Arducorder Mini build logs](https://hackaday.io/project/1395-open-source-science-tricorder)

| Arducorder Mini (1) | Arducorder Mini (2) | Arducorder Mini (3) | Arducorder Mini (4) |
| :---: | :---: | :---: | :---: |
| <a href="pictures/past-iterations/arducordermini1.jpg"><img src="pictures/past-iterations/arducordermini1.jpg" width="180" alt="Arducorder Mini, picture 1"></a> | <a href="pictures/past-iterations/arducordermini2.jpg"><img src="pictures/past-iterations/arducordermini2.jpg" width="180" alt="Arducorder Mini, picture 2"></a> | <a href="pictures/past-iterations/arducordermini3.jpg"><img src="pictures/past-iterations/arducordermini3.jpg" width="180" alt="Arducorder Mini, picture 3"></a> | <a href="pictures/past-iterations/arducordermini4.jpg"><img src="pictures/past-iterations/arducordermini4.jpg" width="180" alt="Arducorder Mini, picture 4"></a> |


## Iteration 8: Attaching something to an iPhone

My first exploration was building something that would attach to the back of (my) iPhone, using a Raspberry Pi Zero W (running a webserver) to communicate with the iPhone over Wifi, and an Arduino Mini to communicate with all the sensors.  This one ended up about 90% built, but it just seemed like a giant kludge, and I discarded it before making an enclosure.

While the whole device didn't end up working out, one of the outcomes of this iteration was the development of a successful magnetic imaging tile, which ended up being used in future iterations.

The build logs of Iteration 8 are available [here on hackaday.io](https://hackaday.io/project/18518-iteration-8/log/164805-a-new-motherboard-design-now-with-more-pi), with the broader project available [here](https://hackaday.io/project/18518-iteration-8).

| Iteration 8 Prototype | Atmospheric Sensor Prototype | Magnetic Imaging Tile Prototype |
| :---: | :---: | :---: |
| <a href="pictures/past-iterations/iteration8-1.jpeg"><img src="pictures/past-iterations/iteration8-1.jpeg" width="180" alt="Iteration 8, picture 1"></a> | <a href="pictures/past-iterations/iteration8-2.jpg"><img src="pictures/past-iterations/iteration8-2.jpg" width="180" alt="Iteration 8, picture 2"></a> | <a href="pictures/past-iterations/iteration8-3.jpg"><img src="pictures/past-iterations/iteration8-3.jpg" width="180" alt="Iteration 8, picture 3"></a> |


## Iteration 9: Teensycorder: Trying to make something that looked like a BlackBerry

Then, I abandoned some of my design principles (as one sometimes does) and decided to try and make something that just used a display and keyboard that was already broken out.  

A post on the Teensycorder is available here: [build log on hackaday.io](https://hackaday.io/project/18518-iteration-8/log/213613-back-at-it-with-the-teensycorder)

| Teensycorder (1) | Teensycorder (2) | Teensycorder (3) | Teensycorder (4) |
| :---: | :---: | :---: | :---: |
| <a href="pictures/past-iterations/teensycorder0.jpeg"><img src="pictures/past-iterations/teensycorder0.jpeg" width="180" alt="Teensycorder, picture 1"></a> | <a href="pictures/past-iterations/teensycorder1.jpeg"><img src="pictures/past-iterations/teensycorder1.jpeg" width="180" alt="Teensycorder, picture 2"></a> | <a href="pictures/past-iterations/teensycorder2.jpeg"><img src="pictures/past-iterations/teensycorder2.jpeg" width="180" alt="Teensycorder, picture 3"></a> | <a href="pictures/past-iterations/teensycorder3.jpeg"><img src="pictures/past-iterations/teensycorder3.jpeg" width="180" alt="Teensycorder, picture 4"></a> |
| **Teensycorder (5)** |  |  |  |
| <a href="pictures/past-iterations/teensycorder4.jpeg"><img src="pictures/past-iterations/teensycorder4.jpeg" width="180" alt="Teensycorder, picture 5"></a> |  |  |  |


## Iteration 10: T-Deck-Corder

I liked the *idea* of the teensycorder, but I didn't really like how big it was turning out.  Around the same time, the [T-Deck (a small blackberry-like device)](https://lilygo.cc/en-us/products/t-deck-plus-1) was released, and I tinkered with making a backpack for it.  But in the end, the challenges of trying to fit so many sensors into such a small space didn't quite work out -- but I did like the form factor a great deal. 

I ended up not taking too many pictures of this one or its board.

## Iteration 11: Initial Cyberdeck explorations with the Raspberry Pi CMx Tablets

Around this time, Cyberdeck builds started to pop up -- folks were bolting found-keyboards onto found Raspberry Pi compute module-based tablets.  I had a go at building one of these, and these initial iterations are what convinced me that there might be something to the Cyberdeck format.  But there were many problems: It's such a kludge of parts, the keyboards (which are bluetooth!) often have pairing and even powering challenges when you disassemble them, and the whole thing was just *big*.  Most of the room of the huge device was spent trying to get all these large parts to fit together for the console, rather than getting sensors and such in there. 

| Tablet Prototype (1) | Tablet Prototype (2) | Many prototype prints around this time |
| :---: | :---: | :---: |
| <a href="pictures/past-iterations/btree1.JPG"><img src="pictures/past-iterations/btree1.JPG" width="180" alt="BTree Cyberdeck, picture 1"></a> | <a href="pictures/past-iterations/btree2.JPG"><img src="pictures/past-iterations/btree2.JPG" width="180" alt="BTree Cyberdeck, picture 2"></a> | <a href="pictures/past-iterations/btree3.JPG"><img src="pictures/past-iterations/btree3.JPG" width="180" alt="BTree Cyberdeck, picture 3"></a> |

## Iteration 12: A smaller Cyberdeck with the Clockwork Pi PicoCalc

Clockwork Pi released a small cyberdeck called the [PicoCalc](https://www.clockworkpi.com/picocalc), and I was actually fairly convinced that this would be the way forward.  The form factor was smaller than the "found tablet + keyboard", it had a keyboard and a display, and it was very hackable.  But it was based on a small and underpowered microcontroller, which would have significant issues for interfacing with a thermal camera, regular camera, and lots of other peripherals.  So I made a backpack that would replace the microcontroller with a Raspberry Pi Zero W, and use an Arduino as the primary sensor interface.  A 3D printed enclosure ended up being the mount for many of the sensors. 

I actually didn't hate this one, and thought it would be the release.  But the screen resolution (which I think was 320x320, or some other small resolution) ended up just being /too small/ to work with -- you really couldn't easily run X Windows, and I wanted to be able to just use standard software/UI libraries rather than writing everything from scratch again.  So I ended up abandoning this one while it was nearly 90-95% finished.

One (very interesting) aspect of this prototype was focusing on trying to have the visible spectrometer be in transmission mode by default. The big aperture in the side of the device is meant for you to slide a sample container for the spectrometer in it, with a light source on one side, and the spectrometer on the other.  If you wanted to use the spectrometer openly instead of in transmission mode, there'd be a small faux sample container that'd have a mirror in it that would point to the outside world.

There are a few early posts on this one [here on the clockwork pi forum](https://forum.clockworkpi.com/t/raspberry-pi-zero-2-on-picocalc/17946/35). 

| PicoCalc (1) | PicoCalc (2) | PicoCalc (3) | PicoCalc (4) |
| :---: | :---: | :---: | :---: |
| <a href="pictures/past-iterations/picocalc1.jpeg"><img src="pictures/past-iterations/picocalc1.jpeg" width="180" alt="PicoCalc, picture 1"></a> | <a href="pictures/past-iterations/picocalc2.JPG"><img src="pictures/past-iterations/picocalc2.JPG" width="180" alt="PicoCalc, picture 2"></a> | <a href="pictures/past-iterations/picocalc3.JPG"><img src="pictures/past-iterations/picocalc3.JPG" width="180" alt="PicoCalc, picture 3"></a> | <a href="pictures/past-iterations/picocalc4.JPG"><img src="pictures/past-iterations/picocalc4.JPG" width="180" alt="PicoCalc, picture 4"></a> |
| **PicoCalc (5)** | **PicoCalc (6)** |  |  |
| <a href="pictures/past-iterations/picocalc5.JPG"><img src="pictures/past-iterations/picocalc5.JPG" width="180" alt="PicoCalc, picture 5"></a> | <a href="pictures/past-iterations/picocalc6.JPG"><img src="pictures/past-iterations/picocalc6.JPG" width="180" alt="PicoCalc, picture 6"></a> |  |  |

## Iteration 13: The Open Source Science Tricoder Cyberdeck

Ultimately the one this repository is about ended up being the one that really worked.  Moving from the `Picocalc` to the `UConsole` provided much more display resolution, and the Raspberry Pi CM4 compute module provided much more compute power than the Raspberry Pi Zero W.  The sensors could be physically added to the back as a sort of custom backpack, rather being all over the place on the Picocalc version, which ended up working very well.

Here are a few early pictures, where I tried to attach a stock cooler -- which ended up needing a truly huge amount of space in the design (so I abandoned it for a time, thinking I wouldn't need a cooler).  It turns out it does run a little warm without a cooler, and would need some kind of cooling in a future iteration.

| Early build (1) | Early build (2) |
| :---: | :---: |
| <a href="pictures/past-iterations/cyberdeck1.JPG"><img src="pictures/past-iterations/cyberdeck1.JPG" width="180" alt="Early build, picture 1"></a> | <a href="pictures/past-iterations/cyberdeck2.JPG"><img src="pictures/past-iterations/cyberdeck2.JPG" width="180" alt="Early build, picture 2"></a> |
 




# Errata

## Things that are real errors

1. **Cooling:** The Raspberry Pi compute modules put out real heat, and while you can run them without a cooler for a while, they do get hot -- and will eventually thermally throttle.  This needs some kind of cooling solution, nominally a copper cooler that extends out with a small fan or something similar.

2. **Silkscreen Misprint:** In an earlier version of the ESP32 board (which is shown in the pictures), the white silkscreen text on the PCB swaps which connector should be for the spectrometer, and which connector should be for the magnetic imaging tile.  The connector closest to the middle of the board should be the spectrometer, and the connector closest to the corner of the board should be the magnetic imaging tile. This should be corrected on the latest board file.  

## Things that I just don't like, or that aren't implemented yet

1. **Battery:** The battery does not run for long.  You get maybe an hour or two.  Having smart power features for the sensors would be ideal.
2. **Magnetic Imaging Tile Framerate:** I designed the magnetic imaging tile to have very fast framerates (e.g. up to 20KHz), but the current refresh rate in the interface is only around 1 frame per second.  This is because it's connected to the ESP32, which is constantly polling all sensors in a round-robbin.  The ESP32 firmware needs a separate mode that allows just focusing on the imaging tile for a short while, so that it can record high-speed captures.  It's a minimal amount of work, it's just not implemented yet.
3. **Transmission spectroscopy for visible spectrometer:** I have spent more time than I'm willing to admit thinking about how to put on a proper light source that can be easily mounted/unmounted for transmission spectroscopy.  There is an unused header on the ESP32 breakout for this purpose, but I haven't found a good solution that I like yet.
4. **Wifi Antenna:** I haven't found a great place for the uConsole Wifi antenna yet, which is currently tucked (but not stuck) near the magnetic tile. 
5. **USB Connectors:** It is a genuinely poor design decision for me to use the same QWIIC connectors for the USB hub connectors, because it allows for folks to easily make costly mistakes (e.g. plugging a 3.3V QWIIC connection into a 5V USB connection, and potentially blowing up the QWIIC part).  But the QWIIC connectors and cables were readily available and easy-to-use, and I did it.  My deepest apologies.

# AI Usage

My recollection is that the ESP32 firmware is primarily human written (by me, using libraries authored by myself and others), while the Python user interface is mostly AI generated.  AI models were also used in debugging in the final stages (thank you, Claude, for noticing that I had swapped two pins on the magnetic imaging tile driver, ending my debugging session in an hour instead of many hours). 

# License

The parts of this that are non-code/physical designs (e.g. the 3D prints, the PCBs, the documentation) are licensed [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The ESP32 firmware essentially stitches together existing libraries with an interface; there is not enough substantial code there to warrant it needing a separate license.  Similarly, the Python user interface is mostly AI generated, and while this is a new legal area, my best understanding is that such code is likely not subject to copyright. 

All of the above is not meant to in any way limit the disclaimer of warranty for all aspects of this project, which is described below.

# Warranty

TLDR: This is a prototype, not a product, and the information in this repository/project may have genuine risks to use.  The author provides no warranty of any kind, and you assume all risks and responsibilities. 

The following is Section 5 of the [Creative Commons Attribution 4.0 International legal code](https://creativecommons.org/licenses/by/4.0/legalcode), reproduced verbatim, and adopted here as the warranty disclaimer for every part of this project (hardware, firmware, software, documentation, etc.):

```
Section 5 -- Disclaimer of Warranties and Limitation of Liability.

  a. UNLESS OTHERWISE SEPARATELY UNDERTAKEN BY THE LICENSOR, TO THE
     EXTENT POSSIBLE, THE LICENSOR OFFERS THE LICENSED MATERIAL AS-IS
     AND AS-AVAILABLE, AND MAKES NO REPRESENTATIONS OR WARRANTIES OF
     ANY KIND CONCERNING THE LICENSED MATERIAL, WHETHER EXPRESS,
     IMPLIED, STATUTORY, OR OTHER. THIS INCLUDES, WITHOUT LIMITATION,
     WARRANTIES OF TITLE, MERCHANTABILITY, FITNESS FOR A PARTICULAR
     PURPOSE, NON-INFRINGEMENT, ABSENCE OF LATENT OR OTHER DEFECTS,
     ACCURACY, OR THE PRESENCE OR ABSENCE OF ERRORS, WHETHER OR NOT
     KNOWN OR DISCOVERABLE. WHERE DISCLAIMERS OF WARRANTIES ARE NOT
     ALLOWED IN FULL OR IN PART, THIS DISCLAIMER MAY NOT APPLY TO YOU.

  b. TO THE EXTENT POSSIBLE, IN NO EVENT WILL THE LICENSOR BE LIABLE
     TO YOU ON ANY LEGAL THEORY (INCLUDING, WITHOUT LIMITATION,
     NEGLIGENCE) OR OTHERWISE FOR ANY DIRECT, SPECIAL, INDIRECT,
     INCIDENTAL, CONSEQUENTIAL, PUNITIVE, EXEMPLARY, OR OTHER LOSSES,
     COSTS, EXPENSES, OR DAMAGES ARISING OUT OF THIS PUBLIC LICENSE OR
     USE OF THE LICENSED MATERIAL, EVEN IF THE LICENSOR HAS BEEN
     ADVISED OF THE POSSIBILITY OF SUCH LOSSES, COSTS, EXPENSES, OR
     DAMAGES. WHERE A LIMITATION OF LIABILITY IS NOT ALLOWED IN FULL OR
     IN PART, THIS LIMITATION MAY NOT APPLY TO YOU.

  c. The disclaimer of warranties and limitation of liability provided
     above shall be interpreted in a manner that, to the extent
     possible, most closely approximates an absolute disclaimer and
     waiver of all liability.
```

# Contact

For questions, please use either Github Issues or `peter@tricorderproject.org` . 

