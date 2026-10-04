# 12 V / 5 A QR Flyback SMPS — Design Calculations and BOM

Rev v3-PRELIM · 2026-10-04
Companion to `smps_12v_5a_schematic.svg`
Derived from `smps_12v_5a_technical_plan_v2.md` plus the round-2 review

> **This is a preliminary paper design, not a validated one.** Every value below is calculated
> from first principles, none is measured. The primary side operates at up to 375 V DC. Have it
> reviewed by a qualified power-electronics engineer and validated on the bench (TC1–TC14) before
> building or selling anything from it.

---

## 1. Design inputs

Taken from the v2 plan with the round-2 corrections applied:

| Parameter | Value | Source |
| --- | --- | --- |
| Input, rated | 120–265 V AC, 47–63 Hz | Round-2 recommendation (v2 proposed 150–265 V) |
| Output | 12.0 V, 5.0 A, 60 W | v2 §3 |
| Topology | QR (valley-switching) flyback | v2 §4 |
| Feedback | Optocoupler + shunt reference, secondary side | v2 §4 |
| Efficiency | ≥ 86 % target, ≥ 84 % floor | v2 §3 |
| Output window | ±4 % static (DC average) | Round-2 C2/C7 |
| Ripple | ≤ 150 mVpp, 0–100 % load | v2 §3 |
| Transient | 50→100→50 %, ≤ ±7 % peak, ≤ 2 ms recovery | Round-2 C2 |

---

## 2. Operating point

### 2.1 Bulk rail

```
V_bulk,max = 265 × √2            = 375 V
V_bulk,min (120 V AC, full load) ≈ 140 V   (after 100 Hz ripple)
```

### 2.2 Bulk capacitance

Hold-up is **not** the binding constraint:

```
C = 2·P·t / (V1² − V2²) = 2(73)(0.01) / (325² − 80²) ≈ 15 µF   → 10 ms at 230 V is trivial
```

Low-line ripple is:

```
I_avg = P_in / V_bulk,avg = 69.8 / 135 ≈ 0.52 A
t_dis ≈ 7.5 ms (50 Hz)
ΔV_allowed = 170 − 100 = 70 V
C ≥ 0.52 × 7.5 ms / 70 V = 56 µF   → 68 µF standard
```

**EC1 = 68 µF / 450 V.** The 450 V rating (not 400 V) comes from the plan's own derating rule:
375 V × 1.2 = 450 V. Verify the ripple-current rating ≥ 1.2 A rms at 105 °C; if a single part
cannot, use 2 × 47 µF / 450 V in parallel (halves ESR, doubles ripple capability).

### 2.3 Transformer

Choose reflected voltage **V_or = 90 V** (trades MOSFET stress against secondary ripple current):

```
n = Np/Ns = V_or / (V_out + V_f) = 90 / 12.5 = 7.2  →  Np = 58, Ns = 8, n = 7.25
D_max = V_or / (V_or + V_bulk,min) = 90 / 230 = 0.39
```

Sizing Lp for critical conduction at 65 kHz, low line:

```
t_on = D/f = 0.39 / 65 kHz = 6.0 µs
P_in = ½·Lp·Ipk²·f  with  Ipk = V_in·t_on/Lp
   →  Lp = ½ (V_in·t_on)² · f / P_in
   →  Lp = ½ (140 × 6.0 µs)² × 65 000 / 69.8 = 330 µH
   →  Ipk = 140 × 6.0 µs / 330 µH = 2.56 A
   →  t_off = Lp·Ipk / V_or = 9.3 µs ;  t_on + t_off = 15.3 µs ≈ 1/65 kHz  ✓ CRM
```

At high line, t_on shortens while t_off is fixed by V_or, so **f rises to ≈ 86 kHz** — the whole
range stays below the 150 kHz CISPR band edge, which is the point of choosing 65 kHz at low line.

### 2.4 Currents

```
I_pri,rms  = Ipk·√(D/3)            = 2.56 × 0.361 = 0.92 A
I_sec,pk   = Ipk × n               = 2.56 × 7.25  = 18.6 A
I_sec,rms  = I_sec,pk·√(t_off·f/3) = 18.6 × 0.449 = 8.3 A
I_cap,rms  = √(I_sec,rms² − I_out²) = √(68.9 − 25) = 6.6 A      ← drives the output bank
```

### 2.5 Core and windings

```
B_max = Lp·Ipk / (Np·Ae) = (330 µH × 2.56) / (58 × 86 mm²) = 0.17 T
```

EER28L (Ae ≈ 86 mm², PC40/3C95). 0.17 T leaves good margin to ~0.35 T saturation at 100 °C,
which is what covers the inrush and transient peaks.

| Winding | Turns | Conductor | Notes |
| --- | --- | --- | --- |
| Np | 58 | 2 × 0.4 mm | Split into two halves, sandwiching Ns |
| Ns | 8 | 0.2 × 10 mm Cu foil | Foil keeps leakage and AC resistance down at 8.3 A rms |
| Naux | 10 | 0.3 mm | Gives V_cc ≈ 15 V; also feeds the ZCD input |

**Build order:** ½Np → 3× tape → shield (1 turn Cu foil, open, to PGND) → 3× tape → Ns foil →
3× tape → ½Np → Naux → outer tape. 3 mm margin tape each side, distance through insulation
≥ 0.4 mm. Sandwiching halves leakage inductance; the shield is what cuts common-mode noise into
the secondary. Target leakage ≤ 2 % of Lp (≈ 6 µH).

### 2.6 RCD clamp

```
P_leak = ½·L_lk·Ipk²·f = ½ × 6 µH × 2.56² × 65 kHz = 1.28 W
V_clamp = 1.5 × V_or = 135 V
R = V_clamp² / P_leak = 135² / 1.28 = 14.2 kΩ  → 18 kΩ (clamps a little higher, dissipates ~1.0 W)
C ≥ V_clamp / (ΔV·R·f) with ΔV = 10 % → 8.5 nF → 10 nF / 630 V
```

### 2.7 Device stress

```
V_ds,pk = V_bulk,max + V_clamp + ring = 375 + 135 + ~40 = 550 V
Derating rule (1.5× on 375 + 90 = 465 V)              = 700 V
```

**Q1 = 700 V**, R_ds(on) ≤ 0.45 Ω, TO-220F (isolated tab).

```
D4: V_rrm = V_out + V_bulk,max/n = 12 + 375/7.25 = 64 V → 100 V for leakage-spike margin
    I: 5 A average, rule ≥ 2× → 20 A
```

**D4 = MBR20100CT, both legs paralleled** (halves V_f, so ≈ 0.45 V at 5 A).

### 2.8 Loss budget

| Item | Loss |
| --- | --- |
| Q1 conduction (0.92² × 0.45 × 1.5 hot) | 0.57 W |
| Q1 switching (valley switching ≈ no turn-on loss) | 0.30 W |
| RCD clamp | 1.00 W |
| Bridge (2 × 0.9 V × 0.52 A) | 0.94 W |
| RT1 NTC (hot) | 0.50 W |
| EC1 ESR | 0.20 W |
| T1 copper + core | 1.50 W |
| D4 Schottky (0.45 V × 5 A) | 2.25 W |
| Output bank ESR (6.6² × 10 mΩ) | 0.44 W |
| L1 DCR (5² × 10 mΩ) | 0.25 W |
| Secondary snubber, bias, controller | 0.70 W |
| **Total** | **≈ 8.65 W → η ≈ 87 %** |

Comfortably past the 86 % target. **Size the thermal path for 11.4 W** (the 84 % floor), not for
8.65 W — the target is margin, not the design point.

### 2.9 Output capacitor bank

6.6 A rms at 30 % derating needs ≥ 9.4 A of capability. A 1000 µF / 25 V low-ESR 105 °C part
handles roughly 2.3 A rms at 100 kHz, so:

- **4 × 1000 µF / 25 V low-ESR, ≥ 5000 h @ 105 °C** → ~9.2 A, plus 2.2 µH + 470 µF post-filter
- *Alternative:* 2 × 470 µF / 25 V hybrid polymer (4–5 A rms each) — smaller, longer life, more cost

Feedback senses at the **C31–C34 node, before L1**. The L1/C35 pole sits at
1/(2π√(2.2 µH × 470 µF)) ≈ 4.9 kHz, inside the loop bandwidth, so sensing after it would
destabilise the loop. The 50 mV drop across L1 at 5 A is 0.4 % and is carried in the error budget.

### 2.10 Feedback network

Using **TLV431** (V_ref = 1.24 V, I_ka,min = 80 µA) rather than TL431 (1 mA): the bias current is
what dominates no-load power in an opto-feedback design, and 1 mA × 12 V = 12 mW before the opto
LED is even counted.

```
R43/R44 = (V_out/V_ref) − 1 = (12.0/1.24) − 1 = 8.68
  R44 = 10.0 kΩ 1 %  →  R43 = 86.6 kΩ 1 %  →  V_out = 12.00 V
  for 12.4 V (cable-drop pre-compensation): R43 = 90.9 kΩ → 12.40 V
R41 (opto LED) = (12 − 1.2 − 1.3) / 2 mA ≈ 4.7 kΩ
R42 (TLV bias) = (12 − 1.24) / 100 kΩ ≈ 108 µA  ✓ above the 80 µA minimum
R45 + C41 = 1 kΩ + 22 nF, Type-2 compensation — final values from a measured Bode plot
```

### 2.11 Independent OVP

```
R53/R54 = (14.05/1.24) − 1 = 10.33  →  R54 = 10.0 kΩ, R53 = 102 kΩ  →  trips at 14.05 V
```

Deliberately on its own divider and its own shunt reference, so a failure of U3 or U2 (the exact
case that makes the output run away) cannot also disable the protection. Latching: U5 pulls the
controller's OTP/latch pin, and the unit stays off until AC is recycled.

**Constraint from the review:** OVP must sit ≥ 0.75 V above the measured load-dump overshoot
(TC7, 100 % → 0 % step). If 14.05 V does not clear it, fix the loop compensation — do not raise
the threshold, because 16 V-rated capacitors are common in 12 V loads.

### 2.12 Inrush and surge

```
RT1 ≥ V_pk / I_inrush = 375 / 40 = 9.4 Ω  →  10 Ω / 3 A NTC
MOV1: V_RMS rating ≥ 1.1 × 265 = 292 V  →  300–320 V class
```

Note on the MOV: a varistor's V_1mA is ~1.5–1.6× its V_RMS rating. That factor relates those two
numbers — it is **not** applied to the line voltage. A 385–470 V class part would be badly
over-rated and would clamp too high to protect anything; a 275 V part on a 265 V input is only
1.04× and degrades. **300–320 V is correct**, and a thermally-protected TMOV is strongly preferred
because the MOV end-of-life mode is degradation to low impedance followed by ignition.

Surge path: once RT1 is hot (≈ 0.5 Ω) it no longer limits anything, so what keeps surge energy off
EC1 is **LF1's differential leakage inductance** (≈ 0.3 mH → ~38 Ω at an 8 µs rise). Confirm by
scoping the bulk rail during TC11 rather than assuming it.

### 2.13 Y-capacitor and touch current

```
I = 2πfCV = 2π × 50 × 4.7 nF × 265 = 0.39 mA
```

11 % of the 3.5 mA Class I limit, so for this earthed design leakage is **not** the binding
constraint — select CY1 for EMI performance and verify leakage, not the other way round. Must be
**Y1 class** (or two Y2 in series) because it bridges a reinforced-insulation barrier.

---

## 3. Bill of materials (preliminary)

### Primary

| Ref | Value | Notes |
| --- | --- | --- |
| TB1 | 3-way terminal block, 300 V | L / N / PE, finger-safe cover |
| F1 | T2A / 300 V~, 1500 A breaking | Time-lag; must survive RT1-limited inrush and 1000 cycles |
| RT1 | 10 Ω / 3 A NTC inrush limiter | Check steady-state self-heating at low line (PF ≈ 0.5) |
| MOV1 | TMOV14R300E (300 V class, thermally protected) | S14K300 is the non-protected alternative |
| CX1 | 0.47 µF X2, 310 V~ | |
| CX2 | 0.22 µF X2, 310 V~ | |
| LF1 | 2 × 15 mH common-mode choke, 1.5 A | Leakage inductance also does surge duty |
| DB1 | KBP210 / GBU4M, 1000 V 4 A | 1000 V, not 600 V: MOV clamp reaches ~775 V |
| EC1 | 68 µF / 450 V, 105 °C, ≥ 5000 h | Or 2 × 47 µF / 450 V |
| R15 | 18 kΩ, 2 W | RCD clamp |
| C13 | 10 nF / 630 V | RCD clamp |
| D3 | UF4007 | Ultrafast, RCD clamp |
| Q1 | 700 V, ≤ 0.45 Ω, TO-220F | Isolated tab; pad ≥ 4 kV if cased |
| R11 | 0.25 Ω, 2 W | Current sense (2 × 0.5 Ω parallel) |
| R12 | 10 kΩ | Gate–source pulldown |
| D5 | UF4007 | Vcc rectifier |
| C15 | 22 µF / 35 V | Vcc reservoir |
| U1 | QR flyback controller | See §4 — not yet selected |
| C11 / C12 / C14 | 100 nF / 100 pF / 1 nF | Vcc decoupling, CS filter, FB filter |
| R13 / R14 / R16 | 22 Ω / 1 kΩ / 22 kΩ | Gate, CS filter, ZCD — re-derive per IC |
| RT2 | 100 kΩ NTC, B = 4250 | OTP sense, near T1/Q1 |

### Barrier

| Ref | Value | Notes |
| --- | --- | --- |
| T1 | EER28L, Lp 330 µH ±7 % | 58 / 8 / 10 T, see §2.5 |
| CY1 | 4.7 nF **Y1** | Y1 required across reinforced insulation |
| U2, U5 | PC817C (or SFH617A-3) | High CTR grade, derate CTR 50 % over life |
| JP1 | 2-pad jumper, open by default | Optional V− to PE link |

### Secondary

| Ref | Value | Notes |
| --- | --- | --- |
| D4 | MBR20100CT, 100 V 20 A | Both legs paralleled |
| R21 / C21 | 10 Ω 1 W / 1 nF 100 V | Snubber — final values from scoped ringing |
| C31–C34 | 4 × 1000 µF / 25 V low-ESR, ≥ 5000 h | Bank must carry 6.6 A rms |
| L1 | 2.2 µH / 8 A, ≤ 10 mΩ | Post-filter |
| C35 | 470 µF / 25 V low-ESR | Post-filter |
| U3, U4 | TLV431A | Not TL431 — see §2.10 |
| R41/R42/R43/R44/R45/C41 | 4.7 k / 100 k / 86.6 k 1 % / 10.0 k 1 % / 1 k / 22 nF | Feedback |
| R51/R52/R53/R54/C51 | 4.7 k / 100 k / 102 k 1 % / 10.0 k 1 % / 100 nF | OVP |
| TB2 | 4-way terminal block | 2 × V+, 2 × V− — a feature for CCTV, keep it |

---

## 4. What this design does not yet settle

1. **U1 is not selected.** The pinout on the schematic is generic. Shortlist 3 QR controllers with
   HV start-up, an OTP/latch pin, ZCD input and **programmable OCP timing** (needed for the
   7.5 A / 100 ms profile that stops nuisance trips on CCTV IR-illuminator and PTZ surges), then
   re-derive R13/R14/R16 and the OCP threshold from the chosen datasheet. This is the M2 gate.
2. **Loop compensation (R45/C41) is a starting point**, not a result. Measure the plant with a
   network analyser or frequency-response analyser and set the crossover and phase margin from
   that. The load-dump overshoot this produces then determines whether the 14.05 V OVP threshold
   has its required 0.75 V margin.
3. **Snubber R21/C21** must be fitted from scoped ringing on the real board, not calculated.
4. **Leakage inductance** is assumed at 2 % of Lp. Measure it on the first wound sample; the RCD
   dissipation and hence R15's rating scale directly with it.
5. **Fuse / NTC / MOV coordination** is a system calculation (F1 I²t vs MOV1 surge current vs RT1
   cold resistance), still outstanding — it belongs at the M2c gate, before PCB fabrication.
6. **No PCB layout.** Creepage and clearance across the barrier, the primary loop area, the
   current-sense return, and the thermal path to the case are all layout problems this schematic
   does not address, and they decide EMI and safety more than the component values do.

---

## 5. Changes this design makes against plan v2

| Item | v2 | Here | Why |
| --- | --- | --- | --- |
| EC1 voltage | 400 V | **450 V** | 375 V peak × 1.2 derating = 450 V; v2 violated its own rule |
| Input range | 150–265 V (proposed) | **120–265 V** | 150 V leaves zero margin at the sag voltage v2 itself cites |
| Bridge | unspecified | **1000 V** | MOV clamps at ~775 V, above a 600 V bridge |
| Shunt reference | TL431 | **TLV431** | 80 µA vs 1 mA bias — what makes the no-load target reachable |
| MOV class | 300–320 V | **300–320 V, thermally protected** | v2's class is correct; TMOV adds the end-of-life fire mitigation |
| Static window | ±5 % sum | **±4 % + 1 % reserve** | v2's budget had zero headroom against its own limit |
| Y-cap | "size from touch current" | **4.7 nF Y1** | Leakage is not binding for Class I — 0.39 mA of 3.5 mA |
