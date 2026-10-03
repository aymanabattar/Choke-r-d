# 12V 5A (60W) AC-DC SMPS: Technical Plan and Requirements

Date: 2026-10-03

---

## 1. Objective and Scope

**Goal:** Design, validate and sell a branded 12V 5A (60W) AC-DC SMPS through retailers and wholesalers, with better reliability and protection than a ₹250-retail generic unit.

**Reference unit:** NEOSYS SB 5amp 60W (manufacturer: Star Bright, board ZY-S60 A35, PCB date 19-Jul-2024), purchased at retail for ₹250. Label data: input AC 100-265V, output 12V 5A, 60W max, 4 output terminals (2 x V+, 2 x V-), 3 input terminals (PE, N, L).

**Rationale:** There is demand for 12V 5A supplies in CCTV, LED strip and ESP32/IoT applications. Low-cost units commonly omit fuse, inrush limiting and proper output filtering. That gap is the differentiator.

**Success criteria**

- [ ] Output 12V ±5% across the full load range (0-5A) and input range (100-265V AC)
- [ ] 72 hr full-load burn-in with zero failures
- [ ] BIS (CRS) registration under the seller's own brand name
- [ ] Positive margin at the final BOM cost and target selling price (assumption: ₹450-600 retail)

**Out of scope:** Using the NEOSYS or Star Bright name, marking, packaging or BIS number in any form. The circuit topology (flyback) is generic; the brand identity is not.

---

## 2. Baseline Unit: Known and Unknown

The baseline establishes what the reference unit actually does before any improvement is attempted. Only top-side photos are available, so the topology is partly assumed.

| Item | Status | Detail |
| --- | --- | --- |
| Rating | Confirmed from label | 12V 5A, 60W max, AC 100-265V |
| Isolated flyback-type converter | Likely from photos | Yellow EE-core transformer T2, Y-cap CY1 across the isolation barrier |
| Bridge DB1, bulk cap EC1 (105°C) | Visible | EC1 µF/V value not legible in photos |
| Startup resistors R13, R10 | From marking (754 = 750 kΩ) | Provide startup current from the HV rail |
| RCD clamp (R15, R16 = 75 kΩ, D3) | Likely from marking | Clamps the switch node voltage spike |
| Output cap DC3 (105°C low-ESR), diode D4 | Visible | Single output cap, affects ripple |
| Controller IC U1 or discrete RCC transistor | **Unknown** | Photo does not clearly show an IC |
| Feedback method (PSR vs optocoupler) | **Unknown** | No optocoupler/TL431 seen; PSR or RCC is a guess |
| Fuse, NTC, MOV, X-cap, CM choke | **Not seen** | May be absent from the board |
| T2 turns, core size, gap | **Unknown** | Needs physical measurement |

**Why this matters:** In a flyback converter the transformer and controller define the whole behaviour. Without their data, any optimization is an estimate.

**Baseline tasks**

- [ ] Obtain a clear solder-side photo and a macro photo of the U1 area
  - Acceptance: the part number or marking of U1 (or the discrete transistor) is legible
- [ ] Continuity-check every net (power off, EC1 discharged)
  - Acceptance: every schematic connection is ticked off
- [ ] Measure T2 primary, auxiliary and secondary turns and inductance (LCR meter)
  - Acceptance: turns ratio and primary inductance Lp are recorded

---

## 3. Electrical Requirements

These are design targets, each verified by a defined test. Values are industry-typical and will be re-calibrated from the measured baseline.

| Parameter | Target | Rationale | Test method |
| --- | --- | --- | --- |
| Input range | 100-265V AC, 47-63 Hz | Mains variation in India; universal input claim on the label | Variac, test at 90V, 230V, 270V |
| Output voltage | 12.0V ±5% | CCTV, LED and ESP32 loads tolerate a 12V rail | DMM at each load point |
| Continuous current | 5A with no derating (60W) | The label claim must be true | 30 min on electronic load at 5A |
| Line regulation | ≤ ±2% (90-265V) | Stable output during brownouts | Variac sweep |
| Load regulation | ≤ ±5% (0-5A) | Typically weak in PSR/RCC, so must be measured | Load sweep |
| Ripple + noise | ≤ 150 mVpp at 5A (20 MHz BW) | CCTV and audio/IoT loads are noise sensitive | Scope, short ground spring |
| Efficiency | ≥ 82% at full load (target), ≥ 78% (minimum) | Heat and efficiency requirements | Input power meter vs output power |
| No-load power | ≤ 0.5W (target) | Heat and marketing claim | Power meter |
| Turn-on time | ≤ 1 s | CCTV/IoT boot reliability | Scope, AC switch-on |
| Hold-up time | ≥ 10 ms at 230V full load | Short mains dips | Scope |
| Inrush current | ≤ 40A peak (with NTC) | Life of switches, MCB and bridge | Current probe |
| Power factor | Not mandated at this class (assumption, confirm with BIS) | PFC adds cost | PF meter |

**Note:** Efficiency, ripple and standby figures are typical targets set by the author, to be re-calibrated from baseline measurements.

- [ ] Measure all parameters above on the baseline unit
  - Acceptance: the "Baseline" column of the table is filled
- [ ] Finalize targets from the measured baseline
  - Acceptance: every target is equal to or better than baseline

---

## 4. Architecture Decision

**Recommendation:** Prototype first with an **integrated PSR flyback controller** and compare against baseline measurements. Move to secondary-side feedback (optocoupler + TL431) only if load regulation or ripple specs are missed.

| Option | Cost | Regulation | Ripple/EMI | Part count | Risk |
| --- | --- | --- | --- | --- | --- |
| Discrete RCC (ringing choke) | Lowest | Weak | High | Low | Weak reliability and EMI; common in cheap units |
| Integrated PSR flyback IC | Low-medium | Adequate (±5% typical) | Medium | Medium | Auxiliary winding and transformer design are critical |
| Secondary-side feedback (TL431 + optocoupler) with flyback IC | Medium-high | Better (±1-2%) | Low | High | Optocoupler CTR aging and extra BOM |

**Rationale**

- The baseline is probably RCC or PSR (to be confirmed). If PSR, a better IC and transformer in the same class improves cost and performance together.
- Secondary-side feedback gives the best regulation but adds BOM and board area. PSR is widely used for 60W, 12V universal-input designs.
- A quasi-resonant (valley-switching) IC helps efficiency and EMI but costs more. Evaluate in phase 2.

**IC selection criteria**

- [ ] Universal input, 60W capable, integrated MOSFET or a clear external MOSFET option
- [ ] OVP, OCP, SCP and OTP listed in the datasheet
- [ ] Reference design or application note available for direct transformer calculation
- [ ] Available in India or via reliable import (lead time ≤ 4 weeks)
  - Acceptance: shortlist of 3 candidate ICs with datasheet, price at 100 qty and reference design link

---

## 5. Protection and Reliability

This is the real differentiator, since these parts are often omitted in cheap units. Each protection addresses a specific failure scenario.

| Protection | Prevents | Implementation | Acceptance test |
| --- | --- | --- | --- |
| Input fuse (or fusible resistor) | Fire from short circuit or component failure | On primary L, correct voltage/current rating | Forced short: fuse opens, no fire or smoke |
| NTC inrush limiter | Switch-on current spike through bridge and EC1 | In series with L | Inrush ≤ 40A peak |
| MOV | Mains surge/spike | Across L-N, after the fuse | Surge test (in lab) |
| CM choke + X-cap | Conducted EMI | Before the bridge | EMI pre-scan with margin |
| OVP | Output over-voltage on feedback failure | Controller built-in or zener clamp | Open feedback: output ≤ 15V |
| OCP | Overload | Controller current sense | Output limits or hiccups above 6A |
| SCP | Output short | IC hiccup mode | Safe restart on short, no damage |
| OTP | Overheating | In IC or NTC sensor | Heat gun test causes shutdown |

**Component reliability rules**

- Capacitors: 105°C, low-ESR, branded (Rubycon, Nichicon, Chemi-Con or equivalent) only. Generic capacitors often have short life.
- Derating: capacitor voltage ≥ 1.2x worst case, MOSFET voltage ≥ 1.5x peak, diode current ≥ 2x average (standard design practice).
- Conformal coating: protects against humidity and dust (leakage and corrosion risk without it).

- [ ] Deliberately fail each protection and verify behaviour
  - Acceptance: in every scenario the output or primary reaches a safe state with no visible board damage
- [ ] Estimate ripple current and life from capacitor datasheets
  - Acceptance: estimated life of EC1 and DC3 ≥ 20,000 hr at 50°C ambient (assumption, verify against datasheet)

---

## 6. Thermal and Mechanical

The reference unit uses an aluminium channel enclosure with open vents and passive cooling. At 60W and 80% efficiency roughly 15W is dissipated, so thermal design must be addressed from the start.

**Requirements**

- Heat sources (controller/MOSFET, output diode D4, T2, bridge) contact the aluminium case through thermal pads or clips.
- Case surface temperature ≤ 70°C at 5A and 40°C ambient (assumption). Hotspot component temperature at least 20°C below its datasheet limit.
- Vent slots must keep working after dust accumulation, and coating must not enter them.
- Primary-secondary creepage and clearance per IS 13252. Reinforced insulation typically needs about 6 mm (confirm the exact value in the standard). A PCB slot between primary and secondary helps.
- Terminal blocks with finger-safe covers; screw torque and wire gauge (≥ 0.75 mm² for 5A) marked.
- Mounting: two screw points with the earth ring bonded to the chassis, as on the reference.

**Cost/function trade-off:** The aluminium case and 4-position output terminal are significant cost items. Reducing output terminals from 4 to 2 or thinning the case saves cost, but check the effect on thermals and current sharing.

- [ ] Map hotspots with a thermal camera or thermocouples
  - Acceptance: every critical component temperature is recorded at 40°C ambient and below its limit
- [ ] Review creepage and clearance in the PCB layout
  - Acceptance: primary-secondary distance ≥ standard value, signed off by the lab or an engineer

---

## 7. Safety, EMI and BIS Compliance

Selling a mains-powered SMPS requires BIS registration, and it must be under the seller's own brand. The R-number on the reference unit belongs to its manufacturer and cannot be used.

**Applicable (from the reference label):** IS 13252 (Part 1) safety standard and CRS registration. Confirm the exact standard, fees and timeline on the BIS website and with a recognised lab; this data is not verified here.

**Two routes**

1. **Own BIS registration:** lab testing of your design, a manufacturing set-up, and a BIS licence in your name.
2. **Private label via a manufacturer:** work with a manufacturer that already holds BIS registration, under a brand-owner arrangement with the registration linked to your brand. Faster, but creates supplier dependency.

**Technical compliance items**

- Dielectric strength (hipot) primary to secondary: typically around 3 kV AC (confirm the exact value in the standard).
- Leakage current, temperature rise, abnormal condition tests (short, overload).
- EMI: conducted emission pre-scan, with CM choke, X-cap and Y-cap selected accordingly.
- Marking: model, rating, brand, BIS mark, batch/date code and manufacturer details under your own name.

- [ ] Get a written quote and process description from a BIS-recognised lab or consultant
  - Acceptance: fees, timeline and required documents listed on one page
- [ ] Compare route 1 (own) vs route 2 (private label) on cost and time
  - Acceptance: a decision note with one route chosen and the reason
- [ ] Ensure label and packaging drafts contain no third-party brand or number
  - Acceptance: peer review confirms all marking is your own

---

## 8. Cost Optimization

Measure the BOM first, then optimize. Without a teardown, any cost figure is an estimate. The reference unit retails at ₹250, which implies roughly ₹150-170 wholesale and a rough BOM of ₹90-120 (approximate, to be replaced by teardown data).

**BOM teardown method:** For every part record value/marking, supplier price at 100 qty and function, then sort by cost. Typically the case, transformer, capacitors, terminals and IC make up 70-80% of cost.

**Cost levers and trade-offs**

| Lever | Where it saves | Risk / trade-off |
| --- | --- | --- |
| Custom-wound or local-vendor transformer | T2 cost | Consistency of quality, so test a sample batch |
| Same-spec alternate capacitors (branded, cheaper series) | Capacitors | ESR and life must be checked |
| Output terminals 4 to 2 | Terminal block | Less current sharing and wiring convenience |
| Simplified case/channel | Aluminium | Lower thermal margin |
| Higher order volume / MOQ | All parts | Cash flow and inventory risk |
| Integrated IC (MOSFET inside) | MOSFET and part count | IC price and single-source risk |

**Do not cut cost on:** fuse, NTC, MOV, Y-cap rating and capacitor grade. Cutting these removes the differentiator and raises BIS and safety risk.

**Target:** After adding protection parts, BOM is roughly ₹150+ (rough) with a selling price of ₹450-600 (assumption). For positive margin, include BOM, per-unit BIS amortization, packaging and a warranty-return provision.

- [ ] Build the teardown BOM spreadsheet (part, value, qty, ₹ at 100 qty, supplier)
  - Acceptance: 100% of parts costed, with a total BOM and baseline cost figure
- [ ] Apply each cost lever one at a time and re-test
  - Acceptance: Section 3 tests pass after each change and the ₹ saving is recorded
- [ ] Build a unit economics sheet: BOM + BIS per unit + packaging + returns reserve vs wholesale price
  - Acceptance: margin ≥ target (set by owner, e.g. 25%) at a 500-unit batch

---

## 9. Test and Validation Plan

Every test has a pre-defined pass/fail so decisions are numeric. The plan runs on both the reference unit and the prototype for a fair comparison.

**Equipment:** variac, electronic load (or power resistors + ammeter), oscilloscope with short-ground probe, power meter, thermocouple/thermal camera, LCR meter, hipot tester (lab).

- [ ] **T1 Bench bring-up:** raise voltage gradually with a variac for first power-on
  - Acceptance: output 12V ±5%, no component hot or smoking
- [ ] **T2 Load sweep:** 0, 1, 2.5, 4, 5A; V_out, ripple, efficiency
  - Acceptance: Section 3 targets pass
- [ ] **T3 Line sweep:** 90, 230, 270V AC at full load
  - Acceptance: line regulation ≤ ±2%, no oscillation or audible noise
- [ ] **T4 Thermal soak:** 2 hr at 5A, 40°C ambient (or room temperature plus calculated margin)
  - Acceptance: case ≤ 70°C, no component above its datasheet limit
- [ ] **T5 Protection tests:** output short, overload above 6A, feedback open, over-temperature
  - Acceptance: every row of the Section 5 table passes
- [ ] **T6 Inrush and switch cycling:** 1000 on/off cycles
  - Acceptance: peak ≤ 40A, no failures
- [ ] **T7 Burn-in:** 72 hr, full load, 5-10 units
  - Acceptance: 0 failures, output drift ≤ 1%
- [ ] **T8 Hipot and leakage (lab):** primary-secondary dielectric and leakage current
  - Acceptance: within standard limits, with a lab report
- [ ] **T9 EMI pre-scan (lab):** conducted emission
  - Acceptance: at least 6 dB margin to the limit (target, confirm against standard)

**Safety rule:** Use an isolation transformer before probing the primary side with a scope, and discharge EC1 after power-off. Clipping a scope ground onto live mains without isolation is life-threatening.

---

## 10. Sourcing, Production and Go-to-Market

Without a factory, the most practical start is an ODM or contract manufacturer. An in-house PCB assembly line can follow once volume justifies it.

| Route | When suitable | Advantage | Disadvantage |
| --- | --- | --- | --- |
| A. White-label (ODM's BIS-registered model, your brand) | Fast launch, low investment | Fast, lower BIS risk | Limited differentiation, supplier dependency |
| B. Custom design + contract manufacturing | A differentiated spec is required | Own spec and IP | Higher BIS lab cost, NRE and time |
| C. Hybrid: ODM base + your protection upgrades (fuse, NTC, better caps) | Middle path | Differentiated and cost-controlled | ODM may charge MOQ/NRE for spec changes |

Starting with route A or C defers the large BIS and tooling spend until the first batch shows market response.

**Channel (retailers and wholesalers)**

- Positioning: "protected, low-ripple 12V 5A" for CCTV installers, LED shops and hobby electronics, distinct from the generic ₹250 unit.
- Give wholesalers clear margin and MOQ. Warranty (assumption: 1-year replacement) will be under your brand, so plan return handling.
- Packaging prints spec, terminal diagram, wire gauge and safety instructions.

- [ ] Send RFQs to 3-5 manufacturers (Section 3 spec, BIS status, MOQ, NRE, lead time)
  - Acceptance: a comparison sheet with one quote per supplier and confirmed BIS-registered model
- [ ] Sample 10 units and run the Section 9 tests
  - Acceptance: T2-T7 all pass, otherwise written feedback to the supplier
- [ ] Pilot batch of 50-100 units with 2-3 local retailers/wholesalers
  - Acceptance: return rate ≤ 3% in the first 2 months (target, adjust as needed)

---

## 11. Risks, Assumptions and Milestones

The largest risk is that topology and controller are not yet confirmed, so Sections 3-5 targets are provisional. The first milestone closes that gap.

**Risks**

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Topology/IC unknown (not confirmed from photos) | Wrong design decisions | Solder-side photos and teardown first, then freeze the spec |
| BIS registration delay or cost | Late launch, or risk of illegal sale | Get a lab quote first, start with route A or C |
| Mains-voltage safety during prototyping | Risk to life | Isolation transformer, discharge, never probe live alone |
| Thin margin (₹250 market) | Business not viable | Premium positioning, unit economics sheet first |
| Single-source IC/transformer | Supply disruption | Alternate part shortlist, two suppliers |
| Warranty returns | Cost overrun | Burn-in and 100% output test before dispatch |

**Assumptions (plan changes if wrong)**

- Selling price ₹450-600 and BOM/wholesale figures are approximate.
- Typical targets (ripple, efficiency, case temperature) are industry-typical and will be re-calibrated from baseline.
- Exact BIS / IS 13252 requirements and fees are not yet verified.

**Milestones (each gate must pass before the next starts)**

- [ ] **M1 Baseline complete:** solder-side photos, final schematic, T2 measured, baseline test table filled
  - Gate: every schematic net verified, baseline column of Section 3 complete
- [ ] **M2 Architecture and IC chosen:** comparison of 3 candidate ICs, one selected
  - Gate: transformer calculation done from the reference design
- [ ] **M3 Prototype v1:** 5-10 units, tests T1-T7
  - Gate: Section 3 targets pass, or deviations documented
- [ ] **M4 Compliance route decided:** route A/B/C chosen, lab quote in hand
  - Gate: BIS timeline and cost in writing
- [ ] **M5 Pilot batch:** 50-100 units, retailer feedback
  - Gate: return rate within target and unit economics positive

**Open questions**

- [ ] When can the solder-side photo and U1 macro photo be provided?
- [ ] What target selling price and expected monthly volume?
- [ ] Will assembly be in-house or through a contract manufacturer?
