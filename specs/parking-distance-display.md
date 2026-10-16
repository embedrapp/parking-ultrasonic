# Garage parking aid: distance-display add-on board + wall case

## Intent
An add-on board for a garage parking aid. It connects a host controller (which runs the firmware, for example an Arduino, ESP32 or Pico) to an HC-SR04 ultrasonic ranger, a small OLED that shows the distance, a red/green stop LED and a piezo buzzer. It works with 3.3 V and 5 V hosts. The board sits in a 3D-printed case screwed to the garage wall, facing the car. One cable runs from the case to the host.

## Requirements
- R1 [confirmed] Ultrasonic ranging uses the SparkFun HC-SR04 module (`sparkfun-sen-15569-hc-sr04`), plugged into the board.
- R2 [confirmed] The display is the Adafruit SSD1306 OLED (`adafruit-326-ssd1306-oled`), plugged into the board.
- R3 [confirmed] Works with 3.3 V or 5 V host logic. The board takes the host's logic level from a VIO pin on the cable and level-shifts automatically, with no jumper to set.
- R4 [confirmed] The host supplies 5 V, GND and VIO on the cable. The board has no power input of its own.
- R5 [confirmed] The host connects through one locking cable connector (JST-family, 10 pins): 5V, GND, VIO, TRIG, ECHO, SDA, SCL, LED_R, LED_G, BUZZ.
- R6 [confirmed] The OLED uses I2C.
- R7 [confirmed] A 5 mm red/green bicolor through-hole stop LED shows through a window on the front. The host drives each colour from its own GPIO.
- R8 [confirmed] A passive piezo buzzer, driven by a transistor and a PWM tone from the host.
- R9 [confirmed] A small power indicator LED.
- R10 [confirmed] Board: PCBWay standard 2-layer process, bare PCB. The user hand-solders the parts, so through-hole or hand-solderable SMD only (SOT-23 or 0805 and larger, nothing fine-pitch or leadless).
- R11 [confirmed] Case: FDM 3D-printed in PETG. It has keyhole screw slots for wall mounting, and the sensor transducers, OLED and stop LED are all on the front face.
- R12 [confirmed] The host cable leaves through the bottom edge of the case.
- R13 [confirmed] Working prototype, about 5 boards (PCBWay minimum order).
- R14 [assumed] The indicator outputs must be safe on both 3.3 V and 5 V hosts. Each GPIO only drives a gate or base, so it supplies under 1 mA, and the LED and buzzer current comes from 5 V.
- R15 [assumed] Basic robustness on the cable: reverse-polarity or overcurrent protection on the 5 V input and bulk decoupling, because the cable may be several metres long.

## Decisions
- D1 Carrier architecture: the HC-SR04 and the OLED are the user's named purchased modules. They plug into female headers on the board, so they can be replaced and the board stays hand-solderable.
- D2 The host supplies 5 V and VIO, with automatic level shifting. The HC-SR04 needs 5 V. ECHO is a 5 V output and must be shifted down to VIO. TRIG is shifted up from VIO to 5 V.
- D3 The OLED runs from VIO (assumed, see To research). Its I2C pull-ups then sit at the host's logic level, and SDA/SCL need no shifter.
- D4 Indicators use direct GPIOs (10-pin cable). This keeps firmware simple and lets the host PWM the buzzer pitch, beep rate and LED brightness.
- D5 Passive piezo with a low-side logic-level MOSFET or NPN driver from 5 V. Beep pitch and rate can then change as the car gets closer.
- D6 Bicolor 5 mm LED with low-side switches from 5 V. Brightness is the same on 3.3 V and 5 V hosts, and red plus green together gives amber.
- D7 JST-family locking connector. It suits a fixed garage install and the user can crimp the cable.
- D8 PETG FDM case. It handles garage temperatures and humidity better than PLA.
- D9 Cable exits at the bottom so water can't run into the case and the cable runs neatly down the wall.

## Out of scope
- Host controller hardware and firmware. A short pin map and a usage note will be written, but no firmware unless the user asks.
- Onboard power input (USB-C or barrel jack) and onboard microcontroller.
- SMT assembly by PCBWay and PCBA sourcing.
- Weatherproofing beyond an indoor garage (no outdoor or IP rating).

## To research
- HC-SR04 (SparkFun SEN-15569): pinout and pin pitch, PCB footprint and transducer geometry (diameter, height, spacing), supply current, ECHO high level, TRIG threshold (whether 3.3 V triggers it reliably) and minimum trigger pulse.
- Adafruit 326 OLED: exact board outline, mounting holes, header pinout in I2C mode, how the I2C/SPI solder jumpers must be set, whether VIN works at 3.3 V and 5 V with its onboard regulator and level shifting, and the pull-up values on SDA/SCL. Also the active-area position, needed for the front window.
- Level shifter choice for TRIG and ECHO: BSS138 discrete versus a dual-supply buffer such as SN74LVC2T45 in a hand-solderable package. Check timing for ECHO pulse-width accuracy.
- Exact JST series (XH 2.5 mm versus PH 2.0 mm) for 10 pins, with matching housing and crimp part numbers, and the maximum practical cable length for I2C at 400/100 kHz.
- Passive piezo part: drive voltage, resonant frequency, through-hole footprint and loudness. Plus the driver MOSFET (logic-level V_GS(th) that fully turns on at 3.3 V gate drive) and a flyback or bleed resistor.
- Bicolor LED part (common cathode or common anode, which sets the switch topology), current-limit resistor values at 5 V, and viewing angle.
- 5 V input protection part (polyfuse, or reverse-polarity P-FET versus Schottky diode) and how much it drops the HC-SR04 supply.
- Wall screw size and keyhole dimensions. Whether a mesh, grille or clearance is needed in front of the ultrasonic transducers so the case doesn't cause false echoes.

## Plan
1. Parts and research: settle every "To research" item with datasheets. Select and verify exact parts (connector, level shifter, MOSFETs, LED, piezo, protection, headers) against footprints and pad numbering. Onboard any missing library parts.
2. Electrical source (`pcb/parking_ultrasonic.zen`), in this order:
   - host connector and 5 V input protection with bulk decoupling;
   - power LED;
   - TRIG/ECHO level shifting between VIO and 5 V;
   - HC-SR04 header;
   - OLED header (I2C, powered from VIO);
   - bicolor LED drivers;
   - buzzer driver.
   Check: build, lint and netlist review, and every requested function traced to a circuit.
3. Board layout: pick the outline around the front-panel features (sensor transducers, OLED window, stop LED) with the JST connector on the bottom edge. Add mounting holes for case standoffs. Place, route with Freerouting, add a ground pour. Check: runPcbChecks clean (ERC/DRC/DFM) under the PCBWay 2-layer profile.
4. Case: export the board STEP and model a two-part PETG FDM case with front openings for the transducers, OLED and LED, a buzzer sound port, keyhole slots on the back, a bottom cable exit with strain relief, and screw bosses for the PCB. Check: fit/interference check against the board STEP, DFAM check, rendered review.
5. Manufacturing: get an orderable PCBWay quote for 5 boards. Export STLs for the case, and a BOM and host pin map for the hand assembly. Physical bench test (ranging, display, indicators on both a 3.3 V and a 5 V host) stays pending for the user.