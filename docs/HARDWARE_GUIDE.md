# 🔧 Hardware Assembly Guide

Complete guide for building the Smart Glasses hardware.

---

## 📐 Component Dimensions

Exact measurements for all components (critical for 3D design):

| Component | Dimensions (L × W × H mm) | Weight | Notes |
|-----------|---------------------------|--------|-------|
| **Raspberry Pi Zero 2W** | 65 × 30 × 5 | 11g | Includes GPIO headers (add 2mm if soldered) |
| **OV5647 Nano Camera** | 8.5 × 8.5 × 7 | ~1g | Ultra-compact nano variant (no PCB) |
| **OV5647 Standard** | 25 × 24 × 9 | ~3g | Standard module (if nano unavailable) |
| **TP4056 Module** | 25 × 19 × 1.5 | ~2g | USB-C charging module |
| **MT3608 Boost Converter** | 36 × 17 × 14 | ~3g | Step-up DC-DC converter |
| **LiPo 2000mAh Slim** | 60 × 35 × 8 | ~38g | Slim pouch cell form factor |
| **SPDT Slide Switch SS12D00** | 7 × 3 × 3 | <1g | Miniature slide switch |
| **CSI Ribbon Cable 15cm** | 150 × 16 × 0.3 | ~1g | 22-pin to 15-pin adapter for Pi Zero |
| **10µF Capacitor** | 5 × 10 (dia × height) | <1g | Electrolytic, through-hole |

**Total Component Weight:** ~59g  
**With 3D Printed Frame:** ~90-100g

---

## ⚡ Complete Wiring Diagram

### Power Circuit

```
                    ┌─────────────────┐
  USB-C Charge ────→│    TP4056      │
                    │  Battery Side   │
  LiPo 3.7V (+)───→│  B+        OUT+ │──┐
  LiPo 3.7V (-)───→│  B-        OUT- │──┼──→ To MT3608
                    └─────────────────┘  │
                                         │
                    ┌─────────────────┐  │
                    │    MT3608       │  │
      OUT+ ←────────│  Vin       Vout │──┼──→ [SPDT SWITCH]
      OUT- ←────────│  GND        GND │──┘         │
                    └─────────────────┘            │
                    ⚡ Set Vout to 5.1V!          │
                       (Use multimeter)            │
                                                    │
                                                    ↓
                    ┌──────────────────────────────────┐
                    │     Raspberry Pi Zero 2W         │
                    │                                  │
  Switch Output ───→│  Pin 2 (5V)                     │
                    │  Pin 6 (GND) ←─── GND from MT3608│
                    │  CSI Port ←─────── Camera Cable  │
                    │  GPIO/BT ←────── Bluetooth        │
                    └──────────────────────────────────┘

  ⚡ IMPORTANT: Add 10µF capacitor between MT3608 Vout+ and GND
     for stable power and noise reduction
```

### Pin Connections Summary

**TP4056 Connections:**
- **IN+**, **IN-**: USB-C input (charging)
- **B+**: Connect to LiPo positive (red wire)
- **B-**: Connect to LiPo negative (black wire)
- **OUT+**: Connect to MT3608 Vin+
- **OUT-**: Connect to MT3608 GND

**MT3608 Connections:**
- **Vin+**: From TP4056 OUT+
- **GND (input)**: From TP4056 OUT-
- **Vout+**: Through switch to Pi GPIO Pin 2 (5V)
- **GND (output)**: To Pi GPIO Pin 6 (GND) and capacitor negative

**SPDT Switch Connections:**
- **Common**: MT3608 Vout+
- **NO (Normally Open)**: Pi Pin 2 (5V)
- **NC (leave floating)**: Not connected

**Pi Zero 2W GPIO:**
- **Pin 1 (3.3V)**: Not used
- **Pin 2 (5V)**: Power input from switch
- **Pin 4 (5V)**: Tied internally to Pin 2
- **Pin 6 (GND)**: Ground from MT3608
- **Pins 9, 14, 20, 25, 30, 34, 39**: All GND (tied together)
- **CSI Port**: Camera ribbon cable

**Camera Connections:**
- **CSI Ribbon**: Connects OV5647 nano module to Pi Zero CSI port
- **Direction**: Blue tab faces away from HDMI on Pi Zero

---

## 🛠️ PCB / Perfboard Layout

Since you have a 3D printer, you can either:
1. Use perfboard to solder components together (recommended for V1)
2. Design a custom PCB (advanced, for V2)

### Perfboard Assembly (30×70mm)

```
Top View of Perfboard Layout:
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  USB-C PORT   [TP4056 Module]                                │
│     ┃                                                         │
│     ┃         OUT+ ────────────┐                             │
│     ┃         OUT- ─────┐      │                             │
│                          │      │                             │
│  [SWITCH]                │      │                             │
│    ╱╲                    │      │                             │
│   ╱  ╲                   │      │                             │
│                          ↓      ↓                             │
│                      [MT3608 Module]                          │
│                       Vout+ ──→ To Pi 5V                      │
│                       GND ────→ To Pi GND                     │
│                                                               │
│  [10µF Cap]                                                   │
│    ─┃┃─  (Between Vout+ and GND)                             │
│                                                               │
│  Solder Points:                                               │
│  • TP4056 B+ to LiPo red wire                                │
│  • TP4056 B- to LiPo black wire                              │
│  • TP4056 OUT+ to MT3608 Vin                                 │
│  • Switch common to MT3608 Vout                              │
│  • 2-pin JST connectors for Pi wires                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Soldering Order:

1. **Mount TP4056** on left side of perfboard
2. **Mount MT3608** in center
3. **Mount switch** near TP4056 (accessible from outside)
4. **Solder capacitor** across MT3608 output
5. **Solder wires**:
   - B+/B- to LiPo with JST connector
   - OUT+/OUT- from TP4056 to MT3608 input
   - Vout from MT3608 to switch common
   - Switch NO to wire → Pi Pin 2
   - MT3608 GND to wire → Pi Pin 6
6. **Use heat shrink** on all exposed connections
7. **Test voltage** with multimeter before connecting Pi

### Voltage Setting:

⚠️ **CRITICAL:** Set MT3608 output to 5.0-5.1V BEFORE connecting to Pi!

1. Connect LiPo to TP4056 B+/B-
2. Turn potentiometer on MT3608 fully counter-clockwise
3. Connect multimeter to MT3608 Vout+ and GND
4. Turn switch ON
5. Slowly turn potentiometer clockwise until reading 5.0-5.1V
6. Apply hot glue over potentiometer to prevent movement

---

## 👓 3D Printed Glasses Frame Design

### Frame Front (Lens Area)

| Measurement | Value (mm) | Notes |
|-------------|-----------|--------|
| **Total front width** | 140 | Fits average adult face |
| **Lens width (each)** | 52 | Standard glasses size |
| **Lens height** | 40 | Slightly smaller than standard |
| **Bridge width** | 18 | Comfortable nose fit |
| **Bridge height** | 10 | Adequate camera clearance |
| **Frame thickness** | 4 | Structural strength |
| **Camera hole diameter** | 9 | At right bridge corner, fits 8.5mm module |
| **Camera recess depth** | 8 | Flush mount for nano module |
| **Nose pad spacing** | 18 | Center-to-center distance |

**Design Notes:**
- Camera positioned at right side of bridge (user's left eye view)
- Hole chamfered at 45° for press-fit camera retention
- Slight forward angle (5°) prevents reflection

### Right Temple Arm (Main Electronics Bay)

| Measurement | Value (mm) | Notes |
|-------------|-----------|--------|
| **Total length** | 145 | Standard temple length to ear |
| **Width at hinge** | 12 | Structural reinforcement |
| **Width mid-section** | 10 | Houses Pi Zero |
| **Width at ear** | 8 | Tapers for comfort |
| **Thickness (max)** | 15 | At Pi Zero section (20-90mm from hinge) |
| **Thickness mid** | 12 | Transition zone |
| **Thickness at ear** | 8 | Comfortable behind ear |
| **Internal cavity** | 68 × 32 × 6 | For Pi Zero (1.5mm walls) |
| **Pi Zero position** | 20mm from hinge | Weight balance |
| **Cable channel** | 17 × 2 | From bridge to Pi cavity |
| **Access panel** | 70 × 32 | Snap-fit bottom cover |
| **Screw posts (4)** | M2 × 3mm | Optional for extra security |

**Design Features:**
- **Internal supports**: 0.5mm thick ribs every 10mm for stiffness
- **Cable strain relief**: Curved channel prevents CSI cable kinking
- **Snap tabs**: 4 tabs with 0.3mm interference fit
- **Ventilation**: 3 × 1mm holes near Pi for heat dissipation

### Left Temple Arm (Battery & Power Bay)

| Measurement | Value (mm) | Notes |
|-------------|-----------|--------|
| **Total length** | 145 | Matches right temple |
| **Width at hinge** | 10 | Slightly narrower (no Pi) |
| **Width mid-section** | 10 | Consistent |
| **Width at ear** | 8 | Matches right side |
| **Thickness (max)** | 12 | Fits battery + power board |
| **Thickness at ear** | 8 | Comfortable fit |
| **Battery cavity** | 62 × 37 × 9 | For 2000mAh LiPo (1mm clearance) |
| **Perfboard cavity** | 40 × 20 × 16 | Near hinge for TP4056+MT3608 |
| **USB-C port hole** | 9 × 3.5 | At temple end for charging |
| **Switch hole** | 7.5 × 3.5 | Near hinge, thumb-accessible |
| **Access panel** | 65 × 37 | Snap-fit, larger for battery insertion |
| **Wire channel** | 5 × 3 | From perfboard to right temple via hinge |

**Design Features:**
- **Battery retention**: Foam padding or velcro strap inside cavity
- **USB-C access**: Molded strain relief around port
- **Switch cutout**: Textured surface for tactile feedback
- **Wire routing**: Through hinge barrel hollow center (3mm diameter)

### Hinges

| Measurement | Value (mm) | Type |
|-------------|-----------|------|
| **Hinge type** | Standard barrel | Spring-loaded preferred |
| **Barrel diameter** | 3.0 | Standard eyeglass size |
| **Barrel length** | 6.0 | Total hinge width |
| **Screw size** | M1.4 × 10 | Standard eyeglass screws |
| **Insert type** | Heat-set brass M1.4 | For durability |
| **Insert depth** | 5.0 | In temple and frame |

**Assembly:**
- Use brass threaded inserts (M1.4 × 5mm × 2.5mm OD)
- Install with soldering iron at 200°C
- Apply light pressure until flush
- Allow to cool before inserting screws

### Nose Pads

| Measurement | Value (mm) | Material |
|-------------|-----------|----------|
| **Pad size** | 12 × 8 × 2 | Oval shape |
| **Material** | TPU or silicone | Flexible/soft |
| **Mounting** | Press-fit posts | 2mm diameter × 3mm tall |
| **Spacing** | 18 | Center-to-center |
| **Angle** | 15° inward | Conforms to nose |

**Nose Pad Design:**
- Print separately in TPU (95A shore hardness)
- Or use adhesive silicone pads from regular glasses
- Posts have 0.1mm interference fit for secure attachment

---

## 🖨️ 3D Printing Guide

### Print Settings

| Setting | Value | Reason |
|---------|-------|--------|
| **Material** | PETG (preferred) or ABS | Strength, durability, slight flexibility |
| **Nozzle** | 0.4mm | Standard |
| **Layer Height** | 0.15mm | Fine detail for fit and finish |
| **Initial Layer** | 0.2mm | Better bed adhesion |
| **Infill** | 50% | Balance of strength and weight |
| **Infill Pattern** | Gyroid or Cubic | Even strength distribution |
| **Wall Count** | 3 perimeters | 2mm+ wall thickness |
| **Top/Bottom Layers** | 5 layers | Solid surfaces |
| **Support** | Yes, tree support | For bridge overhang and cavities |
| **Support Density** | 15% | Easy removal |
| **Bed Adhesion** | Brim (5mm) | Prevents warping |
| **Print Speed** | 40-50 mm/s | Quality over speed |
| **Retraction** | 4mm @ 45mm/s | Reduce stringing |

### Print Orientation

**Frame Front:**
- Orient upright (as worn), with bridge on build plate
- Supports required under bridge and nose pad posts

**Right Temple:**
- Print flat with outside face down
- Internal cavity faces up (no support needed)
- Snap tabs print upward (print slowly for detail)

**Left Temple:**
- Same as right temple orientation
- Ensure USB-C port and switch holes print cleanly

**Access Panels:**
- Print flat with outer face down
- No supports needed
- Print snap tabs carefully

### Post-Processing

1. **Remove Supports**:
   - Use pliers for tree support
   - File smooth with 220-grit sandpaper

2. **Sand Surfaces**:
   - 220-grit for rough areas
   - 400-grit for visible surfaces
   - 600-grit for smooth finish (optional)

3. **Install Heat-Set Inserts**:
   - Heat soldering iron to 200°C
   - Gently push insert into pilot hole
   - Let cool completely before removing iron

4. **Test Fit Components**:
   - Ensure Pi Zero slides in smoothly
   - Check camera fits in recess
   - Verify access panels snap securely

5. **Paint (Optional)**:
   - Prime with plastic primer
   - 2-3 light coats of acrylic or spray paint
   - Clear coat for protection
   - Or use PETG in black/white for no painting

6. **Acetone Vapor Smoothing (ABS only)**:
   - Suspend parts in acetone vapor for 30-60 seconds
   - Creates glossy smooth surface
   - NOT for PETG

---

## 🔩 Complete Assembly Steps

### Tools Required:
- Small Phillips screwdriver (eyeglass screwdriver)
- Soldering iron + solder
- Heat shrink tubing + heat gun
- Multimeter
- Wire cutters/strippers
- Hot glue gun (optional)
- Tweezers

### Step-by-Step Assembly:

#### 1. Prepare 3D Printed Parts (30 min)
- [ ] Print all frame components
- [ ] Remove supports and sand
- [ ] Install heat-set brass inserts for hinges
- [ ] Test fit all components before assembly

#### 2. Assemble Power Circuit (45 min)
- [ ] Solder TP4056 to perfboard
- [ ] Solder MT3608 to perfboard
- [ ] Solder slide switch
- [ ] Add 10µF capacitor across MT3608 output
- [ ] Solder wires to JST connectors
- [ ] Set MT3608 output voltage to 5.0-5.1V
- [ ] Test circuit with multimeter
- [ ] Apply heat shrink to all connections

#### 3. Install Camera (15 min)
- [ ] Thread CSI cable through cable channel
- [ ] Insert nano camera module into bridge recess
- [ ] Secure with small drop of hot glue (optional)
- [ ] Route cable to right temple cavity
- [ ] Leave enough slack for temple movement

#### 4. Mount Pi Zero (20 min)
- [ ] Connect CSI cable to Pi Zero CSI port (blue tab away from HDMI)
- [ ] Place Pi Zero in right temple cavity
- [ ] Ensure GPIO header clears access panel area
- [ ] Mark wire entry points

#### 5. Wire Power to Pi (20 min)
- [ ] Route red wire (5V) from left temple through hinge
- [ ] Route black wire (GND) from left temple through hinge
- [ ] Solder or crimp to 2-pin header
- [ ] Connect to Pi GPIO Pin 2 (5V) and Pin 6 (GND)
- [ ] Double-check polarity before powering on

#### 6. Install Battery & Power Board (15 min)
- [ ] Place perfboard in left temple perfboard cavity
- [ ] Position USB-C port to align with cutout
- [ ] Position switch to align with cutout
- [ ] Test switch accessibility
- [ ] Connect LiPo battery to JST connector
- [ ] Secure battery in battery cavity with foam padding

#### 7. First Power-On Test (10 min)
- [ ] Switch ON
- [ ] Check Pi status LED lights up (green for activity)
- [ ] If no LED, immediately switch OFF and check wiring
- [ ] If LED OK, let boot for 1 minute
- [ ] Switch OFF

#### 8. Final Assembly (20 min)
- [ ] Route all wires neatly
- [ ] Snap on access panels (right and left temples)
- [ ] Verify panels are secure
- [ ] Attach hinges with M1.4 screws
- [ ] Attach nose pads (press-fit)
- [ ] Check temple arm flexibility

#### 9. System Setup (30 min)
- [ ] Insert flashed microSD card
- [ ] Power ON
- [ ] Connect via SSH
- [ ] Run setup script
- [ ] Copy trained models
- [ ] Start web app

#### 10. Bluetooth Pairing (10 min)
- [ ] Open web app on phone
- [ ] Navigate to Bluetooth page
- [ ] Scan for devices
- [ ] Pair and connect speaker pendant
- [ ] Test audio output

#### 11. Final Testing (15 min)
- [ ] Start inference via web app
- [ ] Test ISL sign recognition
- [ ] Verify speech output through Bluetooth speaker
- [ ] Check FPS and responsiveness
- [ ] Monitor temperature after 5 minutes
- [ ] Verify battery runtime

**Total Assembly Time:** ~3.5 hours

---

## ⚖️ Weight Distribution

| Component Location | Weight (g) | Notes |
|--------------------|-----------|--------|
| **Frame Front** | 15-20 | Camera + 3D print |
| **Right Temple** | 30-35 | Pi Zero + wiring + 3D print |
| **Left Temple** | 45-50 | Battery + power board + 3D print |
| **Total** | 90-105 | Well under 150g comfort limit |

**Balance Point:** Slightly rear-biased due to battery weight. Compensated by:
- Heavier frame front material
- Adjustable nose pads for weight distribution
- Spring-loaded hinges for secure fit

**Comparison:**
- Meta Ray-Ban: 49g (no battery, smaller frame)
- Regular sunglasses: 25-40g
- Smart Glasses V1: ~100g (acceptable for assistive device)
- Target V2: <70g with custom PCB and smaller battery

---

## 🔋 Power Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Battery Capacity** | 2000mAh @ 3.7V | 7.4Wh total energy |
| **Pi Zero 2W Idle** | 100mA @ 5V | 0.5W |
| **Pi Zero 2W Active** | 350-400mA @ 5V | 1.75-2.0W (with camera + BT) |
| **Expected Runtime** | 2.5-3 hours | Active inference |
| **Charging Time** | 2-3 hours | Via TP4056 @ 1A |
| **Boost Efficiency** | ~85% | MT3608 typical |
| **Standby Time** | 15-20 hours | Screen off, BT connected |

**Power Saving Tips:**
- Reduce camera resolution (320×240 vs 640×480)
- Lower inference frequency (10 FPS vs 15 FPS)
- Use model complexity 0 in MediaPipe
- Disable WiFi when not using web app
- Use airplane mode for collection only

---

## 🌡️ Thermal Management

**Expected Temperatures:**
- **Pi Zero 2W**: 50-60°C under load (safe, <80°C throttle point)
- **MT3608**: 40-50°C (normal)
- **TP4056**: 45-55°C while charging (normal)
- **Battery**: 30-40°C during discharge (safe, <60°C)

**Cooling Strategy:**
- 3 × 1mm ventilation holes in right temple near Pi
- Airflow through cavity gaps
- No active cooling required
- Monitor via `vcgencmd measure_temp` on Pi

**Warning Signs:**
- Pi throttling icon (thermometer) in top-right
- Significant performance drop
- Battery getting warm during discharge (not charging)

**If Overheating:**
- Add more ventilation holes
- Apply thermal tape to Pi → temple inner wall
- Reduce camera resolution
- Take breaks every hour

---

## 🛡️ Safety Considerations

### Electrical Safety
- ✅ **Overcurrent Protection**: TP4056 has built-in protection
- ✅ **Overvoltage Protection**: MT3608 regulated output
- ✅ **Reverse Polarity**: Double-check wiring before power-on
- ⚠️ **Battery Safety**: Use LiPo with built-in protection circuit
- ⚠️ **Fire Risk**: Never charge unattended, use fireproof LiPo bag

### Mechanical Safety
- ✅ **No Sharp Edges**: Sand all 3D printed surfaces
- ✅ **Secure Screws**: Use threadlocker on hinge screws
- ✅ **Battery Retention**: Ensure battery cannot shift during movement
- ⚠️ **Breakage**: PETG more impact-resistant than ABS
- ⚠️ **Allergies**: Use hypoallergenic nose pads if skin-sensitive

### Usage Safety
- ⚠️ **Do not wear while driving** — obstructs vision
- ⚠️ **Do not wear in rain** — not waterproof
- ⚠️ **Remove during sports** — risk of breakage/injury
- ✅ **Bluetooth speaker safe** — meets CE/FCC radiation standards

---

## 🔧 Troubleshooting

### Power Issues

**Pi doesn't turn on:**
- Check switch is ON
- Verify MT3608 voltage is 5.0-5.1V
- Check polarity on Pi GPIO pins
- Test battery voltage (should be >3.5V)

**Pi reboots randomly:**
- Increase MT3608 voltage to 5.1V
- Add larger capacitor (22µF or 47µF)
- Check for loose power connections

**Battery drains fast:**
- Reduce camera resolution in config
- Check for background processes
- Battery may be degraded (replace)

### Camera Issues

**Camera not detected:**
- Check CSI cable connection (blue tab orientation)
- Verify cable not damaged/kinked
- Run `vcgencmd get_camera` on Pi
- Enable camera in raspi-config

**Poor image quality:**
- Clean camera lens
- Adjust focus ring on camera module
- Check lighting conditions
- Reduce MediaPipe model_complexity

### Bluetooth Issues

**Speaker won't pair:**
- Ensure speaker in pairing mode
- Check Bluetooth enabled on Pi
- Run `bluetoothctl` manually for debugging
- Restart PulseAudio: `pulseaudio --kill && pulseaudio --start`

**Audio choppy:**
- Reduce BT distance (<5m)
- Check WiFi/BT interference
- Lower audio quality setting if available
- Try different speaker

### Mechanical Issues

**Loose hinges:**
- Tighten screws
- Apply small drop of threadlocker
- Check heat-set inserts are secure

**Access panels won't snap:**
- File snap tabs slightly
- Ensure no internal wire obstruction
- Check print accuracy (may need scaling)

---

## 📦 Alternative Components

If specified components unavailable, use these alternatives:

| Original | Alternative | Notes |
|----------|------------|-------|
| **OV5647 Nano** | OV5647 Standard | Larger, but works (adjust frame design) |
| **TP4056 USB-C** | TP4056 Micro-USB | Works fine, just different connector |
| **MT3608** | MT3410 or XL6009 | Similar boost converters |
| **Pi Zero 2W** | Pi Zero W (original) | Slower, but functional (lower FPS) |
| **2000mAh LiPo** | 1500mAh or 2500mAh | Adjust cavity size |
| **PETG** | ABS or ASA | Different post-processing |

---

## 📚 Additional Resources

- **3D Models**: [Thingiverse Link] (to be published)
- **Wiring Photos**: [GitHub Wiki] (to be published)
- **Video Assembly Guide**: [YouTube Link] (to be published)
- **Troubleshooting Forum**: [GitHub Discussions]

---

**Questions?** Open an issue on GitHub or see [docs/WEBAPP_GUIDE.md](WEBAPP_GUIDE.md) for software setup.

---

**Safety First!** Always test power circuit with multimeter before connecting to Pi. Use fireproof LiPo charging bag.
