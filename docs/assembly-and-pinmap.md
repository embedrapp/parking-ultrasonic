# Parking distance display: assembly guide and host pin map

Board: `pcb/layout/layout.kicad_pcb` (64 x 66 mm, 2 layers, 1.6 mm, PCBWay standard process).
Case: `mechanical/parking-case.cad.json` → `mechanical/exports/front_shell.stl`, `mechanical/exports/back_plate.stl`.

## Host cable pin map (J1, JST XH 2.50 mm, 10 pins)

| J1 pin | Signal | Direction (host view) | Host pin type | Notes |
|---|---|---|---|---|
| 1 | GND | – | GND | |
| 2 | +5V | out | 5 V rail | 5 V, at least 200 mA. Feeds the HC-SR04, stop LED and buzzer through a 0.5 A polyfuse (F1) and a 5 V TVS diode (D2, SMAJ5.0A) |
| 3 | VIO | out | host logic rail (3.3 V or 5 V) | Sets the I/O level. Also powers the OLED and the I2C pull-ups |
| 4 | SDA | bidir | I2C SDA | 4.7 kΩ pull-up to VIO on the board. OLED address **0x3D** |
| 5 | SCL | out | I2C SCL | 4.7 kΩ pull-up to VIO |
| 6 | TRIG | out | GPIO | Pulse at least 10 µs high. Shifted up to 5 V by U1 (SN74AHCT1G125) |
| 7 | ECHO | in | GPIO (input capture / pulseIn) | Shifted down to VIO by U2 (SN74LVC1G125), 33 Ω series resistor |
| 8 | LED_R | out | GPIO / PWM | High = red on (about 14 mA from 5 V, switched by Q1). The GPIO only drives a MOSFET gate |
| 9 | LED_G | out | GPIO / PWM | High = green on (about 13 mA). Red and green together look amber |
| 10 | BUZZ | out | PWM | A 4 kHz square wave is loudest (the PS1240's resonant frequency). Low-side switch Q3 |

Every input on the board has a 100 kΩ pull-down. A host held in reset therefore leaves the LEDs and buzzer off and the sensor idle.

Firmware hints (no firmware is included):
- Distance (cm) ≈ echo pulse width (µs) / 58. Allow at least 60 ms between triggers.
- The OLED is an SSD1306, 128 x 64, at I2C address 0x3D (for example Adafruit_SSD1306 `begin(SSD1306_SWITCHCAPVCC, 0x3D)`). RST is not wired; the Adafruit board resets itself at power-up.
- Use 100 kHz I2C if the cable is longer than about 1 m.

## Cable
Board end: JST **XHP-10** housing with 10x **SXH-001T-P0.6** crimp contacts (AWG 28–22), wired pin-to-pin to the host. Use jacketed multicore cable no thicker than 8 mm OD; the bottom exit notch is 9 mm wide.

## Parts not in the board BOM

| Qty | Part | Use |
|---|---|---|
| 1 | SparkFun SEN-15569 (HC-SR04) | Plugs into the J2 right-angle socket |
| 1 | Adafruit 326 OLED (I2C default: its J1/J2 jumpers stay closed) | DS1 |
| 1 | 1x8 female header, 2.54 mm pitch, 8.5 mm body (for example Sullins PPTC081LFBN-RC) | Socket for DS1; the OLED's male header plugs into it |
| 1 | JST XHP-10 + 10x SXH-001T-P0.6 | Cable plug |
| 4 | M3 x 8 pan-head self-tapping screws | Fix the PCB to the back-plate standoffs (2.6 mm pilots) |
| 4 | M3 x 25 pan-head self-tapping screws | Fix the front shell to the back plate (2.6 mm pilots) |
| 2 | 4 mm (#8) pan-head wall screws + plugs, head 8.5 mm max | Wall keyholes |
| 1 | Cable tie, 4 mm wide max | Strain-relief bar |

## Board assembly order (hand soldering)
1. SMD parts first:
   - U1 and U2 (SOT-23-5): match the pin-1 marking.
   - Q1–Q3 and the 0805 passives.
   - F1.
   - D2: cathode band toward V5.
   - D3: cathode mark toward GND.
2. J1, the J2 socket (Sullins PPPC041LGBN-RC) and the 1x8 OLED header socket.
3. BZ1: the + lead (pin 1, square pad) goes to V5.
4. Trim every through-hole lead to 2.5 mm or less below the board. The case standoffs leave 5 mm under the board, and there is an extra relief pocket under the buzzer.
5. D1 stop LED (SunLED XLMDKVG59MCA, common anode = middle lead): **do not solder it yet** (see case assembly step 3).
6. Bench check before fitting the modules. Apply 5 V and VIO; the power LED should light. Drive LED_R, LED_G and BUZZ high one at a time and confirm each output responds.

## Case printing
- Material: PETG, 0.4 mm nozzle, 0.2 mm layers, 3 perimeters, 25 % infill.
- `front_shell.stl`: print front face down, no supports.
- `back_plate.stl`: print back face down, no supports. The keyhole pockets (9 mm) and the cable-tie bridge (10.5 mm) are short bridges.
- DfAM measurement:
  - Both parts are watertight single bodies.
  - Minimum wall is 1.22 mm on the shell (between the buzzer sound holes) and 1.5 mm on the plate.
  - Estimated support volume is 3 % of part volume or less.

## Case assembly
1. Screw the PCB onto the four back-plate standoffs (4x M3 x 8).
2. Plug in the HC-SR04 with the transducers facing outward. Its top edge rests on the two support posts. Plug in the OLED.
3. Fit the stop LED:
   - Insert D1 with full-length leads, cathode per the silkscreen.
   - Fit the front shell temporarily and push the LED up until its dome is flush in the 5.3 mm front hole.
   - Solder from the back, trim the leads and remove the shell.
4. Plug in the cable. Pass it under the tie bar, fix it with the cable tie and route it out through the bottom notch.
5. Mount on the wall:
   - Drive two wall screws 30 mm apart, leaving the heads 3 mm proud of the wall.
   - Hang the back plate on them using the keyhole slots.
   - Fit the front shell and fix it with 4x M3 x 25 from the front.

Overall size: 70.8 x 103.8 x 32.5 mm (W x H x D, including the 8 mm back plate).

## Values to verify on the first build
- **HC-SR04 height:** the case assumes the module's back face is 4.2 mm above the board bottom (taken from the right-angle socket's 3D model). That puts the transducer fronts 0.3 mm behind the front face. If they sit differently, change `hcsr04_back_z` or `front_inner_z` and rebuild.
- **OLED window:** 24 x 13.5 mm, centred on the glass. Adafruit does not dimension the active-area offset; adjust `oled_window_dy` if the image is clipped.
- **Bench test:** ranging, display and indicators still need testing on both a 3.3 V host and a 5 V host.
