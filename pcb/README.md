# parking_ultrasonic PCB Workspace

This sidecar workspace stores native Zener (`.zen`) schematic and PCB sources for the Embedr project.

- Firmware remains managed through `embedr.yaml` and PlatformIO.
- Hardware source-of-truth for schematic and PCB work lives under `pcb/`.
- Start by editing `parking_ultrasonic.zen`, then run `embedr pcb build`, `embedr pcb test`, or `embedr pcb layout`.
