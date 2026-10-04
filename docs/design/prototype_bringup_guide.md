# 12 V / 5 A QR Flyback — Prototype Construction and Bench Bring-Up

Rev 1 · 2026-10-04
Companion to `smps_12v_5a_schematic.svg` and `smps_12v_5a_design_notes.md`

> The primary side of this circuit operates at up to 375 V DC and the bulk capacitor stores
> enough energy to kill. Nothing in this guide makes that safe — it makes it *manageable*, and
> only if every step is followed. If you are not confident working on live mains, stop and get
> someone who is.

---

## 0. Why not a breadboard

Two independent reasons, either one sufficient:

**Electrical.** A breadboard contact is ~10-20 nH with variable contact resistance. The primary
power loop would enclose 50-100 cm² with roughly 500 nH of stray inductance. Switching 2.56 A at
several hundred A/µs puts `V = L·di/dt` = hundreds of volts of spike on top of the 510 V the
MOSFET already sees. It fails on roughly the first switching cycle. Separately, the 640 mV
full-scale current-sense signal would be buried in noise, so OCP either nuisance-trips or does
not exist. And 2.56 A peak through a spring clip rated ~1 A melts it.

**Safety.** Contact spacing is 2.54 mm with 1-1.5 mm of effective internal creepage, against a
375 V requirement. It tracks, it arcs, and every node is exposed.

A breadboard is not an option for this circuit at any stage.

---

## 1. Construction on zero PCB

### 1.1 Board choice

Use **plain dotted general-purpose board** (individual pads), single- or double-sided.

Do **not** use stripboard/veroboard. Its long parallel copper strips give capacitive coupling
between primary switching nodes and poor creepage along the strip length — both of which matter
here and neither of which you can fix after the fact.

Lay "traces" as bare tinned copper wire soldered along the track side: **22 SWG (0.7 mm)** for
signal, **18-20 SWG** for the primary power loop and the secondary output loop.

### 1.2 The isolation slot

Cut a **physical slot right through the board** between the primary and secondary sections, with
a hacksaw blade or a rotary tool.

- Target **8 mm of air**, not the 6 mm the standard asks for. Perfboard gets scratched, fluxed
  and dusty; you will not clean it to production standard, so buy margin.
- The slot should run the full depth of the board and the full length of the barrier.
- **Only three things cross it:** CY1, U2 and U5. Nothing else — not a ground wire, not a probe
  lead, not a cable tie.

### 1.3 Loop discipline — in priority order

These three loops decide whether the thing works. Everything else is forgiving.

**1. Primary power loop** — `EC1(+) → T1 primary → Q1 drain/source → R11 → EC1(−)`
- Target under ~3 cm² enclosed area.
- EC1 within ~15 mm of T1 and Q1.
- Heavy wire, shortest possible path, go and return adjacent to each other.

**2. Gate loop** — `U1 GATE → R13 → Q1 gate` and `Q1 source → U1 GND`
- U1 within ~10 mm of Q1.
- Run the gate wire and its return together.

**3. Secondary loop** — `T1 secondary → D4 → C31 bank → T1`
- Same discipline, heavy wire. This one carries 18.6 A peak.

### 1.4 Grounding

**Star-point the current sense.** R11's low end connects directly to EC1's negative terminal. A
*separate thin wire* runs from that same physical point to U1's GND pin.

Do not let the controller's ground reference share copper with the high-current primary return.
This is the single most common cause of erratic OCP and random shutdowns on hand-built supplies.

### 1.5 Deviations from the schematic, for perfboard only

| Component | Schematic | On perfboard | Why |
| --- | --- | --- | --- |
| C12 (CS filter) | 100 pF | **470 pF** to start | You will be fighting sense noise; tighten later |
| R15 (RCD) | 18 kΩ 2 W | Keep 2 W, expect to change value | Leakage inductance is higher on perfboard |
| C13 (RCD) | 10 nF | **22 nF** to start | More clamp energy to absorb |
| Q1 | TO-220F | Fit a small heatsink | Even on the bench |
| D4 | TO-220 | Fit a small heatsink | 2.25 W |
| LF1, MOV1, CX1/CX2 | fitted | **Omit during DC bring-up** | Add before mains testing |
| F1, RT1 | fitted | **Always fit before mains** | Non-negotiable |

### 1.6 T1 — your actual blocker

You cannot buy a 58 / 8 / 10 turn EER28L off the shelf. Three routes:

1. **Local winding to spec.** The full specification is in §2.5 of the design notes. Order **3
   samples** and require the winder to report **measured Lp and measured leakage inductance** for
   each. The spread between those three is data you need.
2. **Rewind a core from a baseline unit.** You are buying 3-5 for the M1 teardown anyway. Measure
   the original first — that measurement feeds M1 regardless of whether you rewind.
3. **Adapt the design to an available transformer.** If you can source a 60 W / 12 V flyback
   transformer with published Lp and turns ratio, recompute V_or, D_max and the RCD around *it*
   rather than specifying a custom part. For a first prototype this is often the faster route.

Whichever you choose, **measure Lp and leakage on an LCR meter before powering anything.**
Leakage inductance directly sets RCD dissipation, and the design assumed 2 % of Lp.

---

## 2. Bench equipment

| Item | Spec | Notes |
| --- | --- | --- |
| Bench DC supply A | 0-60 V, 2 A, current limited | Bulk rail during DC bring-up |
| Bench DC supply B | 0-20 V, 0.5 A | Vcc during DC bring-up |
| Isolation transformer | ≥ 150 VA | **Required** before any mains step |
| Variac | ≥ 150 VA | Order: mains → variac → isolation tx → DBT → DUT |
| Dim-bulb tester | 40-60 W incandescent in series with live | First mains power-on only |
| Electronic load | 0-6 A, or power resistors + ammeter | 2.4 Ω / 60 W gives 5 A at 12 V |
| Oscilloscope | ≥ 100 MHz, short ground spring | Differential probe for primary side |
| LCR meter | — | T1 characterisation |
| Discharge tool | 10 kΩ / 5 W on insulated probes | For EC1, every single time |

**Dim-bulb tester:** an incandescent lamp in series with the live line. A dead short draws only
the lamp's current. Bright and staying bright = short; bright then dimming = normal inrush then
run. If incandescent lamps are hard to source, a 100 W halogen or a small heater element works.

**Isolation transformer:** if a proper one is out of budget, two identical 230 V : 24 V
transformers back-to-back works for low-power stages, but will sag badly at 60 W output. Budget
for the real thing before TC2.

---

## 3. Staged bring-up

**Do not build the whole board and apply mains.** Build and verify in stages. Stages 1-5 run on
bench DC at 40-60 V, where a mistake costs a MOSFET instead of your life.

### Stage 1 — Input section, no switching
Build: TB1, F1, RT1, LF1, CX1, CX2, MOV1, DB1, EC1.
Test: mains through isolation transformer + variac, no load, ramp slowly.
- **Pass:** V_bulk tracks `V_in × √2` within a few volts, nothing heats, no arcing.
- Then discharge EC1 and verify 0 V before moving on.

This is the only early stage that touches mains, and it has no switching node, so it is the
lowest-risk way to confirm your input wiring and slot clearance.

### Stage 2 — Controller alone
Build: U1, C11, C12, C14, R13, R14, R16, RT2. **Do not connect the HV pin.**
Test: feed Vcc from bench supply B at 15 V. Leave the gate unloaded.
- **Pass:** the IC starts, draws its datasheet quiescent current, and produces gate pulses (it
  will be in a fault/hiccup mode without feedback — that is expected and fine).
- Check the gate waveform is clean at the pin.

### Stage 3 — Switching stage on low-voltage DC ★
**This is the most valuable stage in the whole procedure.**

Build: add T1 primary, Q1, R11, R12, RCD clamp (D3/R15/C13).
Test setup:
- Bench supply A → **40 V** into the bulk rail, current limit **0.5 A**
- Bench supply B → 15 V into Vcc
- No secondary connected yet, no aux winding
- Scope on Q1 drain (**differential probe**, or scope ground to the primary return with the DUT
  floating on bench supplies only — no mains anywhere near the bench)

What to look for:
- **Drain waveform:** clean switching, V_ds plateau ≈ `V_in + V_or` scaled for 40 V input.
  Ringing amplitude tells you whether the RCD is right and what your real leakage inductance is.
- **Current-sense waveform** at the CS pin: a clean ramp, not a noise field. If it is noisy,
  fix the star ground before going further — do not "filter it until it looks right."
- **Gate waveform** at the MOSFET pin: fast edges, no plateau ringing into the Miller region.

Ramp the input to 60 V. Nothing should get hot. If the current limit trips, stop and find out why.

### Stage 4 — Secondary, open loop
Build: add T1 secondary, D4, R21/C21, C31-C34, L1, C35, TB2.
Test: still 40-60 V on the bulk rail, Vcc still external, **no feedback connected**.
- The output will be unregulated and may be low. That is expected.
- **Pass:** a clean DC output appears, the secondary diode waveform looks sane, nothing heats.
- Load it lightly (100-500 mA) with a resistor and confirm it holds up.

### Stage 5 — Close the loop
Build: add U2, U3, R41-R45, C41, and the divider.
Test: still on bench DC.
- **Pass:** the output regulates at 12.0 V and holds across your available input range.
- Step the load (even crudely, switching a resistor in and out) and watch for ringing or
  instability. Tune R45/C41 here, not later.

Then add U4/U5 (OVP) and verify: with the loop open (lift one end of R41), the output must
clamp and latch below **14.5 V**. Do this at low input voltage where an overshoot is survivable.

### Stage 6 — Aux winding and self-powering
Build: add Naux, D5, C15. Connect the ZCD network.
Test: still bench DC, but now disconnect supply B after start-up.
- **Pass:** Vcc self-sustains from the aux winding; the unit keeps running.
- Measure the aux voltage — it scales with output, so verify it lands near 15 V.

### Stage 7 — Mains, finally
Only now. Setup: **mains → variac → isolation transformer → dim-bulb tester → DUT.**

1. Variac to zero. Connect. Stand back.
2. Bring the variac up slowly to ~80 V AC while watching the dim-bulb lamp.
3. If the lamp glows bright and *stays* bright: kill it, you have a short.
4. If it flashes and dims: normal. Continue up to 120 V, then 230 V.
5. Remove the dim-bulb tester only once it starts cleanly twice in a row.
6. **Discharge EC1 and verify 0 V before touching anything, every time.**

---

## 4. Safety rules, non-negotiable

1. **Isolation transformer upstream of the DUT** for every mains step. A variac is *not* an
   isolation transformer — its output is still mains-referenced.
2. **Never clip a mains-referenced scope ground to the primary.** Use a differential probe. If
   you do not have one, do primary measurements on bench DC only (stages 3-6 are designed for
   exactly this).
3. **Discharge EC1 through a 10 kΩ / 5 W resistor and verify 0 V with a DMM** before touching the
   board. Every time. It holds 375 V and it holds it for minutes.
4. **One hand behind your back** when the board is live. Current across the chest is what kills.
5. **Never work on it alone.** Someone else in the room who knows where the breaker is.
6. **Enclose the board in a plastic box** with the lid on during operation; probe through holes.
   A perfboard flapping loose on the bench with 375 V on it will eventually be touched.
7. **Insulated mat, no jewellery, dry hands.**
8. **F1 and RT1 fitted before any mains step.** They are the difference between a dead MOSFET and
   a fire.

---

## 5. What this prototype will and will not tell you

### Valid on perfboard
- Does it start, regulate, and hold regulation (TC1)
- Line and load regulation across the available range (TC2, TC3)
- Protection behaviour: OCP, SCP, OVP threshold and latch, OTP (TC5)
- Transformer design verification: is V_or what you calculated, is Lp right
- Loop stability and transient response, approximately (TC7)
- Output ripple — **directionally**, it will be worse than the final build

### Meaningless on perfboard — do not bother
- **Conducted EMI.** Hand wiring will fail by 20-30 dB. The number tells you nothing about the
  final design.
- **Thermal performance.** No enclosure, no case contact, completely different airflow.
- **Absolute efficiency.** Expect **2-4 % below** the final PCB figure from longer paths and
  worse loop areas. Use it as a trend between changes, not as a pass/fail against the 86 % spec.
- **Hipot and creepage compliance.** Your slot is a prototype expedient, not a qualified barrier.
- **Burn-in and reliability.** A solder joint on perfboard is not a production joint.

### Expect these problems, they are normal
- Drain ringing larger than calculated → RCD needs retuning (that is why C13 starts at 22 nF)
- Current-sense noise → fix grounding first, filter second
- Audible noise at light load from the transformer in burst mode
- Efficiency 2-4 points low
- Occasional unexplained restarts that disappear when you shorten a wire

---

## 6. Faster alternatives worth considering

Before committing weeks to a perfboard build, two routes get you to real measurements sooner:

1. **A controller vendor's evaluation board.** Most QR flyback vendors sell a 60 W / 12 V eval
   board. You get a validated layout and a known-good transformer, and you can modify it. This
   also forces the M2 decision (controller selection) early, which is where the project should
   be anyway.
2. **Modify a baseline unit as a test mule.** You are buying 3-5 NEOSYS units for the teardown.
   Take one and add the fuse, NTC, MOV and a proper output capacitor bank. That tests *your
   differentiator* — the protection suite — without having to prove a new power stage first. It
   is the cheapest way to find out whether the protection additions do what you claim they do.

Route 2 in particular answers a business question (does the protection upgrade work and what
does it cost) much faster than route 1 answers an engineering one.
