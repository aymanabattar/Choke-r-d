# 12V 5A (60W) AC-DC SMPS: Technical Plan and Requirements (v2)

Date: 2026-10-03
Revision: v2, incorporates the design review `smps_12v_5a_plan_review.md`.

---

## 0. Change Log from Review

**Accepted as written (defects in v1)**

- B1: v1 error budget was arithmetically impossible. Replaced by an explicit budget (Section 3).
- B3: rated input range and test range contradicted each other. One rated range, two test tiers (Sections 3, 9).
- B4 (GST and amortization): GST and certification payback volume were missing. Added (Section 8).
- D3: single output capacitor cannot carry secondary ripple current. Now a requirement (Section 3).
- D4: 70°C case target sat on the safety limit. Tightened (Section 6).
- M1, M3, M5, M6: load transient, capacitor life by core temperature, output grounding, cable drop. Added.
- Test-plan gaps, M3 gate loophole, missing gates, M1 blocked on a third party. Fixed (Sections 9, 11).
- Identifier collision: transformer stays T2, tests renamed TC1-TC9 and onward.

**Accepted with modification (owner decisions marked)**

- D1: architecture inverted. v1 prototype is QR flyback + optocoupler/TL431. PSR becomes a phase-2 cost-down.
- M2: rated input 150-265V proposed. Owner must confirm this marketing trade-off. Bulk capacitor range widened to 47-100 µF (the review's single figure of 47 µF is optimistic; fix it by low-line ripple simulation).
- B2: efficiency raised to ≥86% target, ≥84% floor, because it drives thermals and capacitor life. The IEC 61000-3-2 75W argument is kept as a design margin only (see below).

**Not taken as written (verify before relying on)**

- MOV class: the review suggests 385-470V class. That rating is for ~400V lines and its clamp voltage would exceed what a 400V bulk capacitor, bridge and MOSFET tolerate. v2 specifies a **300-320V rms-class** MOV, to be confirmed in the lab surge test.
- IEC 61000-3-2: the review itself notes harmonics are generally not part of BIS CRS scope. The 75W threshold and edition-specific rules are unverified here, so it is kept as a design margin and customer-audit item, not a legal blocker.
- D2 (OVP blind in PSR): the principle is sound (independent secondary OVP is good practice), but the claim that a broken sense path always causes runaway is controller-dependent. Independent OVP is still required.
- D5 (IS 15885 as the LED-driver standard) and the BIS ITE transition (IS 13252 vs IS 62368-1): both need confirmation with BIS or a lab. Treated as open items.
- BIS fee ranges (₹40,000-1,00,000+), thermal limits (70°C touch limit), surge/ESD levels and the input-sag claim (150-180V): the review's estimates; none verified here.

---

## 1. Objective and Scope

**Goal:** Design, validate and sell a branded 12V 5A (60W) AC-DC SMPS through retailers and wholesalers, with better reliability and protection than a ₹250-retail generic unit.

**Reference unit:** NEOSYS SB 5amp 60W (manufacturer: Star Bright, board ZY-S60 A35, PCB date 19-Jul-2024), purchased at retail for ₹250. Label data: input AC 100-265V, output 12V 5A, 60W max, 4 output terminals (2 x V+, 2 x V-), 3 input terminals (PE, N, L).

**Rationale:** There is demand for 12V 5A supplies in CCTV, LED strip and ESP32/IoT applications. Low-cost units commonly omit fuse, inrush limiting and proper output filtering. That gap is the differentiator.

**Success criteria**

- [ ] Output within ±5% worst case, using the error budget in Section 3, over the rated load and input range, measured 4-wire at the output terminals
  - Acceptance: every contributor in the budget is measured and the worst-case sum is ≤ ±5%
- [ ] Burn-in per Section 9 with zero failures
- [ ] BIS (CRS) registration under the seller's own brand name, with the applicable standard and CRS scope confirmed
- [ ] Positive margin at the final BOM, GST-correct price and certification payback volume (Section 8)

**Out of scope:** Using the NEOSYS or Star Bright name, marking, packaging or BIS number in any form. The circuit topology (flyback) is generic; the brand identity is not. Also out of scope: copying PCB artwork. Derive the schematic from your own measurements and do your own layout (clean-room), since layout rights are a separate question from topology.

---

## 2. Baseline Unit: Known and Unknown

The baseline establishes what the reference unit actually does before any improvement is attempted. Only top-side photos are available, so the topology is partly assumed.

| Item | Status | Detail |
| --- | --- | --- |
| Rating | Confirmed from label | 12V 5A, 60W max, AC 100-265V |
| Isolated flyback-type converter | Likely from photos | Yellow EE-core transformer T2, Y-cap CY1 across the isolation barrier |
| Bridge DB1, bulk cap EC1 (105°C) | Visible | EC1 µF/V value not legible in photos |
| Startup resistors R13, R10 | From marking (754 = 750 kΩ) | Provide startup current from the HV rail |
| RCD clamp (R15, R16, D3) | Markings read as 753 = 75 kΩ | Re-read markings with a magnifier before building the schematic on them |
| Output cap DC3 (105°C low-ESR), diode D4 | Visible | Single output cap, a defect for ripple current (Section 3) |
| Controller IC U1 or discrete RCC transistor | **Unknown** | Photo does not clearly show an IC |
| Feedback method (PSR vs optocoupler) | **Unknown** | No optocoupler/TL431 seen; PSR or RCC is a guess |
| Fuse, NTC, MOV, X-cap, CM choke | **Not seen** | May be absent from the board |
| T2 turns, core size, gap | **Unknown** | Needs physical measurement |

**Why this matters:** In a flyback converter the transformer and controller define the whole behaviour. Without their data, any optimization is an estimate.

**Baseline tasks**

- [ ] Buy 3-5 additional baseline units (approx. ₹750-1,250) and tear one down destructively
  - Acceptance: U1 or the discrete transistor is identified, and unit-to-unit variance data exists for at least 3 units
- [ ] Continuity-check every net (power off, EC1 discharged)
  - Acceptance: every schematic connection is ticked off
- [ ] Measure T2 primary, auxiliary and secondary turns and inductance (LCR meter)
  - Acceptance: turns ratio and primary inductance Lp are recorded

---

## 3. Electrical Requirements

Each target is verified by a defined test. Values are industry-typical and will be re-calibrated from the measured baseline.

**Input range decision (owner to confirm):** Proposed rated input **150-265V AC** (or 120-265V for margin). The review argues the real Indian threat is sag to roughly 150-180V, not operation at 100V. The 100V claim mainly adds bulk capacitor cost, inrush energy, current stress and heat. The trade-off is losing a "universal input" label. Performance tests run inside the rated range only; abnormal tests run at 0.9 x V_min and 1.1 x V_max.

**Output error budget (worst-case sum = ±5.0%)**

| Contributor | Allocation |
| --- | --- |
| Setpoint tolerance at 25°C, 230V, 2.5A | ±1.0% |
| Line regulation over the rated range | ±1.0% |
| Load regulation, 0-5A | ±2.0% |
| Temperature drift, 0-50°C | ±1.0% |
| **Total** | **±5.0%** |

Voltage is measured 4-wire at the output terminal screws.

| Parameter | Target | Rationale | Test method |
| --- | --- | --- | --- |
| Input range (rated) | 150-265V AC, 47-63 Hz (proposed) | Real mains sag in India; smaller bulk cap and lower stress | Variac inside the rated range |
| Output voltage | 12.0V nominal, error budget above | CCTV, LED and ESP32 loads tolerate a 12V rail | 4-wire DMM at each load point |
| Continuous current | 5A at ambient up to 50°C, derating curve above | Label claim must be true in real enclosures | 30 min on electronic load, until thermal equilibrium |
| Ripple + noise | ≤ 150 mVpp, 20 MHz BW, across 0%, 10%, 50% and 100% load | Burst-mode ripple is often worse at light load | Scope, short ground spring |
| Load transient | 50% to 100% to 50% at 1 A/µs: deviation ≤ ±5%, recovery to ±1% in ≤ 2 ms, no ringing | Core spec for noise-sensitive loads | Scope at output terminals |
| Efficiency | ≥ 86% at 230V full load (target), ≥ 84% (floor) | Heat budget (about 8-9W) and capacitor life; input power 69.8W / 71.4W stays clear of 75W | Input power meter vs output power |
| No-load power | ≤ 0.15W | Modern controllers achieve this routinely | Power meter |
| Turn-on | ≤ 1 s, monotonic, no overshoot; startup into 10,000 µF and into a constant-power DC-DC load | MCU and camera boot reliability | Scope, AC switch-on |
| Hold-up | ≥ 10 ms at 230V full load | Short mains dips (non-binding; low-line ripple sets bulk C) | Scope |
| Bulk capacitor EC1 | 47-100 µF / 400V for 150V minimum (final value from low-line ripple simulation), rated ripple current and ≥ 5,000 h at 105°C | Sets low-line operation, inrush and life | Simulation, then measurement |
| Output capacitor bank | Sized for measured secondary RMS ripple current with ≥ 30% derating, 105°C, with post-LC filter | At 5A a DCM flyback has about 7A RMS in the output cap; one cap carries about 1.5-2.2A | Measure or simulate at low line |
| Inrush | ≤ 40A peak at a stated source impedance | Life of switches, MCB and bridge | Current probe |
| Power factor | Depends on declared application (Section 7) | PFC changes BOM | PF meter |

- [ ] Measure all parameters on the baseline unit
  - Acceptance: the "Baseline" column of this table is filled
- [ ] Freeze targets from the measured baseline
  - Acceptance: every target is equal to or better than baseline, and each deviation has a written reason

---

## 4. Architecture Decision

**Recommendation (revised):** v1 prototype uses a **quasi-resonant (valley-switching) flyback controller with optocoupler + TL431 secondary-side feedback**. PSR is kept as a **phase-2 cost-down**, attempted only after the specs are proven and measurable.

| Option | Cost | Regulation | Ripple/EMI | Part count | Risk |
| --- | --- | --- | --- | --- | --- |
| Discrete RCC (ringing choke) | Lowest | Weak | High | Low | Weak reliability and EMI; common in cheap units |
| Integrated PSR flyback IC | Low-medium | Adequate at low power, degrades near 5A | Medium, poor load transient | Medium | 60W/5A is the upper edge of PSR territory; transformer and aux winding tolerance critical |
| QR flyback + optocoupler/TL431 | Medium (roughly ₹8-15 more than PSR, review estimate) | Best (±1-2%) | Low | Higher | Optocoupler CTR aging, solved by graded high-CTR parts and 50% CTR derating |

**Rationale**

- With the corrected error budget and the load-transient requirement, specs sit near the limit of what PSR delivers.
- The cost difference is small against a ₹150 BOM at ₹450-600 retail, and regulation accuracy is part of the differentiator.
- QR operation also supports the ≥86% efficiency target, which fixes the thermal and capacitor-life problems.
- Re-running milestones because PSR missed the spec costs far more than the per-unit saving.

**Switching frequency and EMI:** choose f_sw clear of the 150 kHz CISPR band edge (65-100 kHz is the usual range) and specify frequency jitter or dithering, the cheapest route to the 6 dB EMI margin.

**IC selection criteria**

- [ ] Universal input capable, 60W, integrated MOSFET or a clear external MOSFET option, QR/valley switching
- [ ] OVP, OCP, SCP and OTP in the datasheet
- [ ] Reference design with opto/TL431 feedback available for direct transformer calculation
- [ ] Available in India or by reliable import (lead time ≤ 4 weeks, tracked as a schedule floor)
  - Acceptance: shortlist of 3 ICs with datasheet, price at 100 qty and reference design link

---

## 5. Protection and Reliability

Each protection addresses a specific failure scenario.

**Input chain (order):** L → fuse → NTC → MOV + X-cap → CM choke → bridge.

| Protection | Prevents | Implementation | Acceptance test |
| --- | --- | --- | --- |
| Fuse | Fire from short or component failure | Time-lag (T) type, rated ≥ 265V, breaking capacity about 1500A, survives NTC-limited inrush and 1000 on/off cycles | Forced short: opens, no fire or smoke |
| NTC | Switch-on spike | Cold resistance such that total series R ≥ 9.4 Ω for ≤ 40A at 265V peak (375V); check steady-state self-heating at low-line RMS current | Inrush ≤ 40A, NTC temperature within rating |
| MOV | Mains surge | 300-320V rms-class (not the 275V class on a 265V input, not 385V class), surge level per IEC 61000-4-5 (e.g. 1 kV/2 kV combination wave) | Lab surge test, clamp voltage within bridge/cap/MOSFET ratings |
| CM choke + X-cap | Conducted EMI | Before the bridge | EMI pre-scan margin ≥ 6 dB |
| OVP | Output over-voltage | **Independent secondary-side OVP** (TL431 or zener-triggered), latching until AC is recycled | ≤ 14.5V peak with the feedback path open-circuited |
| OCP | Overload | Time profile (e.g. 7.5A instantaneous folding back after 100 ms, or 6A peak for 10 s), **auto-recovery, not latch** | No nuisance trip on IR-illuminator or PTZ motor surge |
| SCP | Output short | Hiccup with auto-recovery | 5 consecutive shorts, safe restart, no damage |
| OTP | Overheating | Defined trip temperature, defined sensed component, recovery behaviour | Thermocouple reference: trip below component datasheet limit |
| Output reverse voltage | Battery back-feed in CCTV sites | Output protection diode or equivalent | Reverse voltage applied, no damage |
| Output cap open/short, low-line start, brownout | Field faults | Design review and test | Safe state in each case |

**Component reliability rules**

- Capacitors: long-life 105°C low-ESR, branded, base endurance ≥ 5,000 h at 105°C in the BOM (not merely "105°C").
- Life is specified against **measured core temperature** (thermocouple on the can), not ambient. At 80°C core a 2,000 h/105°C part gives about 11,300 h; at 60°C about 45,000 h.
- Derating: capacitor voltage ≥ 1.2x worst case, MOSFET voltage ≥ 1.5x peak, diode current ≥ 2x average.
- Conformal coating for humidity and dust.
- **Y-capacitor:** a single Y-cap across a reinforced barrier must be Y1, or two Y2 in series. Size it from the touch-current limit (3.5 mA for Class I ITE, assumption to confirm; use a tighter internal limit for margin). This is the central EMI trade-off in an offline flyback.
- **Transformer construction:** reinforced insulation using triple-insulated secondary wire or three layers of barrier tape with margin tape, distance through insulation ≥ 0.4 mm (confirm in standard).

- [ ] Deliberately fail each protection and verify behaviour
  - Acceptance: every scenario ends in a safe state with no visible board damage
- [ ] Estimate ripple current and life from capacitor datasheets at measured core temperature
  - Acceptance: EC1 and DC3 life ≥ 50,000 h target at measured core temperature (verify against datasheet and Arrhenius derating)

---

## 6. Thermal and Mechanical

The reference unit uses an aluminium channel enclosure with open vents and passive cooling. At ≥86% efficiency, dissipation is about 8-9W instead of 13-15W.

**Requirements**

- Case surface ≤ 60°C at 5A and 40°C ambient (target); 70°C is the absolute never-exceed (the touch-temperature limit for metal surfaces is to be confirmed in the standard). Rated to 50°C ambient with a published derating curve above it, because installed junction boxes commonly reach 50-60°C inside.
- Hotspot components at least 20°C below datasheet limits.
- Thermal pad between the switching device and a PE-bonded case: dielectric rating ≥ 4 kV with a minimum thickness. Drain-to-PE capacitance worsens common-mode emissions, so check CM emissions with and without the case-contact scheme.
- Vent slots must keep working after dust accumulation and must not be blocked by coating.
- Primary-secondary creepage and clearance per the applicable standard (reinforced typically about 6 mm, confirm), with a PCB slot between primary and secondary. The transformer is where the barrier actually lives (Section 5).
- Terminal blocks with finger-safe covers. **Keep 4 output terminals** (2 x V+, 2 x V-), which lets an installer feed two cameras without a splice.
- **Output grounding:** output floating relative to PE (SELV) with an optional user-fittable V−-to-PE link, documented on the pack, to avoid ground-loop hum in multi-camera systems.
- **Cable voltage drop:** 0.75 mm² copper is about 0.023 Ω/m, so a 10 m run (20 m of conductor) drops about 2.3V at 5A. Publish a gauge-versus-length table on the pack and evaluate a 12.4-12.5V nominal setpoint (still inside the error budget) to pre-compensate.
- Operating/storage temperature and humidity, altitude, IP rating, mounting orientation, minimum load, audible noise at light load (transformer singing) and MTBF estimate are to be specified in the product datasheet.

- [ ] Map hotspots with a thermal camera or thermocouples, installed in a representative enclosure
  - Acceptance: every critical component temperature recorded at thermal equilibrium (rise < 2°C over 30 min) and below its limit
- [ ] Creepage/clearance and transformer insulation review before PCB fabrication
  - Acceptance: signed off by the lab or a qualified engineer

---

## 7. Safety, EMI and BIS Compliance

Selling a mains-powered SMPS requires BIS registration under the seller's own brand. The R-number on the reference unit belongs to its manufacturer and cannot be used.

**Open verification items (do these before M4)**

- [ ] Confirm whether new registrations must be filed under IS 13252 or IS 62368-1
- [ ] Confirm whether an enclosed SMPS module sold to installers is within CRS scope, and under which product category
- [ ] Declare one primary application. As general ITE/SMPS the 75W harmonics threshold and PF assumptions apply. As an LED driver, a different standard and lighting harmonics limits apply, possibly requiring active PFC. Verify the standard and the PF requirement against the declared application.
  - Acceptance: a one-page written decision from BIS or a recognised lab

**Certificate is factory-bound:** under CRS the registration is held by the manufacturer for a specific model at a specific factory, with your brand recorded on it. Switching ODMs means re-registering and re-paying. Negotiate certificate-transfer or dual-source terms up front.

**Two routes**

1. **Own BIS registration:** lab testing of your design, a manufacturing set-up, and a BIS licence.
2. **Private label via a manufacturer** that already holds BIS registration, with the registration linked to your brand.

**Technical compliance items**

- Dielectric strength: **type test** typically about 3 kV AC for reinforced insulation (confirm in the standard); **100% production test** a shortened lower-voltage test (about 1.5-2.5 kV, 1 s) so the insulation is not degraded.
- Leakage/touch current, temperature rise, abnormal condition tests.
- EMI: conducted emission pre-scan, CM choke, X-cap and Y-cap selected accordingly.
- Marking: model, rating, brand, BIS mark, batch/date code, manufacturer details under your own name.
- **Legal Metrology** (mandatory on Indian retail packs): MRP, manufacturer/importer name and address, net quantity, consumer-care contact, month/year of manufacture.
- Verify **E-Waste EPR** registration applicability, and IEC/import requirements if boards are sourced abroad.

- [ ] Written quote and process description from a BIS-recognised lab or consultant
  - Acceptance: fees, timeline and required documents on one page
- [ ] Compare route 1 and route 2 on cost, time and certificate portability
  - Acceptance: a decision note with one route and the reason
- [ ] Label and packaging draft free of any third-party brand or number, and compliant with Legal Metrology
  - Acceptance: peer review confirms

---

## 8. Cost Optimization

Measure the BOM first, then optimize. The reference unit retails at ₹250, implying roughly ₹150-170 wholesale and a rough BOM of ₹90-120 (approximate, to be replaced by teardown data).

**Pricing and tax:** state whether ₹450-600 is MRP (GST-inclusive, the normal Indian retail convention) or ex-GST. At 18% GST this is about 15% of realizable revenue.

**Certification economics:** amortize BIS cost over a realistic **lifetime volume**, not the first batch. A lab cost of ₹40,000-1,00,000+ (review estimate, get a quote) is ₹80-200 per unit over 500 units, which can exceed half the BOM. Reaching under about ₹20 per unit needs roughly 3,000-5,000 units. Treat certification as upfront capital with a stated payback volume, which is a go/no-go number at M4. This is the strongest reason to start with route A or C (Section 10).

**BOM teardown method:** record value/marking, supplier price at 100 qty and function for every part, sorted by cost. Typically the case, transformer, capacitors, terminals and IC are 70-80% of cost.

| Lever | Where it saves | Risk / trade-off |
| --- | --- | --- |
| Rate input 150-265V instead of 100-265V | Bulk capacitor (about 2-3x smaller), inrush, transformer and MOSFET stress, efficiency | Loses a "universal input" label of little value to Indian installers |
| Custom-wound or local-vendor transformer | T2 cost | Quality consistency, so test a sample batch |
| Same-spec alternate branded capacitors | Capacitors | ESR and life must be checked |
| Simplified case/channel | Aluminium | Lower thermal margin |
| Higher order volume / MOQ | All parts | Cash flow and inventory risk |
| PSR instead of QR + opto (phase 2) | Roughly ₹8-15 | Regulation and transient performance, only after specs are proven |

**Do not cut cost on:** fuse, NTC, MOV, Y1 capacitor, independent OVP, capacitor grade, or the 4 output terminals (a feature, worth more than the roughly ₹8 saved).

**Competitive risk:** the generic ₹250 competitor has room to cut price in response.

- [ ] Teardown BOM spreadsheet (part, value, qty, ₹ at 100 qty, supplier)
  - Acceptance: 100% of parts costed with a total and baseline cost figure
- [ ] Apply each cost lever one at a time and re-test
  - Acceptance: Section 3 tests pass after each change and the ₹ saving is recorded
- [ ] Unit economics sheet: BOM + assembly/test (₹30-50, estimate) + packaging (₹15-25, estimate) + certification per unit at lifetime volume + returns reserve + GST vs wholesale price
  - Acceptance: margin ≥ target (owner sets, e.g. 25%) at stated lifetime volume, and a certification payback volume is written down

---

## 9. Test and Validation Plan

Every test has a pre-defined pass/fail. The plan runs on both the reference unit and the prototype. Tests are numbered TC1 onward to avoid collision with transformer T2.

**Equipment:** isolation transformer, variac, dim-bulb tester, electronic load, oscilloscope with short-ground probe, power meter, thermocouples/thermal camera, LCR meter, hipot tester (lab), surge/ESD/EFT generators (lab).

**Power chain:** mains → isolation transformer → variac → DUT. A variac is not an isolation transformer. Use a dim-bulb tester for the first power-on.

**Performance tests** run inside the rated range only. **Abnormal tests** run at 0.9 x V_min and 1.1 x V_max and require "no damage, safe behaviour", not spec compliance.

- [ ] **TC1 Bench bring-up:** dim-bulb first power-on, then raise the variac gradually
  - Acceptance: output within the error budget, no component hot or smoking
- [ ] **TC2 Load sweep:** 0, 10%, 50%, 80%, 100% load: V_out (4-wire), ripple, efficiency, no-load power
  - Acceptance: Section 3 targets pass
- [ ] **TC3 Line sweep:** across the rated range at full load, plus abnormal tier at 0.9 x V_min and 1.1 x V_max
  - Acceptance: line regulation within budget, no oscillation or audible noise; abnormal tier safe
- [ ] **TC4 Thermal soak:** 5A, installed orientation, inside a representative enclosure, until temperature rise is < 2°C over 30 minutes
  - Acceptance: case ≤ 60°C at 40°C ambient (target), ≤ 70°C absolute, no component above datasheet limit
- [ ] **TC5 Protection tests:** every row of the Section 5 table
  - Acceptance: each row's acceptance passes
- [ ] **TC6 Inrush and switch cycling:** 1000 on/off cycles
  - Acceptance: peak ≤ 40A at the stated source impedance, no failures
- [ ] **TC7 Load transient and startup:** Section 3 transient spec, startup into 10,000 µF and constant-power load
  - Acceptance: transient spec met, starts reliably
- [ ] **TC8 Burn-in (infant-mortality and workmanship screening, not reliability demonstration):** 72 hr at 45-50°C ambient and 110% load, 5-10 units, interleaved with on/off cycling
  - Acceptance: 0 failures, output drift ≤ 1%
- [ ] **TC9 Hipot and leakage (lab):** type test
  - Acceptance: within standard limits with a lab report
- [ ] **TC10 EMI pre-scan (lab):** conducted emission, with and without the case-contact scheme
  - Acceptance: ≥ 6 dB margin to the limit (confirm against standard)
- [ ] **TC11 Surge, ESD, EFT (lab):** levels per the applicable standard (e.g. IEC 61000-4-5 1 kV/2 kV; ESD contact/air to the metal case)
  - Acceptance: performance criterion A or B as defined, with the levels written in the test report
- [ ] **TC12 Damp heat:** 40°C / 93% RH for 48 h, then re-test
  - Acceptance: TC2 results still pass
- [ ] **TC13 Transport:** drop and vibration in retail packaging
  - Acceptance: no damage or function loss
- [ ] **TC14 Dropout / brownout ride-through**
  - Acceptance: defined output behaviour at specified dips
- [ ] **Production test (pilot batch):** 30-60 min hot burn-in at full load, reduced-voltage hipot (about 1.5-2.5 kV, 1 s), per-unit test records and batch traceability
  - Acceptance: each unit has a stored record

**Safety rule:** use an isolation transformer before probing the primary side with a scope, and discharge EC1 after power-off. Clipping a scope ground onto live mains without isolation is life-threatening. Never probe live alone.

---

## 10. Sourcing, Production and Go-to-Market

Without a factory, the most practical start is an ODM or contract manufacturer. An in-house PCB assembly line can follow once volume justifies it.

| Route | When suitable | Advantage | Disadvantage |
| --- | --- | --- | --- |
| A. White-label (ODM's BIS-registered model, your brand) | Fast launch, low investment | Fast, lower BIS risk, certification cost is not yours | Limited differentiation, certificate is factory-bound |
| B. Custom design + contract manufacturing | A differentiated spec is required | Own spec and IP | BIS lab cost, NRE and time; amortization needs lifetime volume |
| C. Hybrid: ODM base + your protection upgrades (fuse, NTC, Y1, independent OVP, better caps) | Middle path | Differentiated and cost-controlled | ODM may charge MOQ/NRE; any spec change may need re-registration |

Starting with route A or C defers the large BIS and tooling spend until the first batch shows market response.

**Channel (retailers and wholesalers)**

- Positioning: "protected, low-ripple 12V 5A" for CCTV installers, LED shops and hobby electronics.
- Warranty headline: with ≥86% efficiency, ≤60°C case and ≥5,000 h capacitors, a 2-3 year warranty can become the differentiator (v1 assumed 1 year; confirm after measured life data).
- Packaging prints spec, terminal diagram, gauge-versus-length table, optional V−-to-PE link note and safety instructions, plus Legal Metrology declarations.

- [ ] RFQs to 3-5 manufacturers (spec, BIS status, MOQ, NRE, lead time, certificate-transfer terms)
  - Acceptance: a comparison sheet with one quote per supplier and a confirmed BIS-registered model
- [ ] Sample 10 units and run Section 9 TC1-TC8
  - Acceptance: all pass, otherwise written feedback to the supplier
- [ ] Pilot batch of 50-100 units with 2-3 local retailers/wholesalers
  - Acceptance: return rate ≤ 3%, defined as units returned within 60 days divided by units shipped in the same cohort (window and target adjustable by the owner)

---

## 11. Risks, Assumptions and Milestones

The largest risk is that topology and controller are not yet confirmed, so Section 3-5 targets are provisional. M1 closes that gap.

**Risks**

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Topology/IC unknown | Wrong design decisions | Buy extra units and tear one down; freeze spec after |
| BIS registration delay or cost; standard/scope unclear | Late launch, or illegal sale | Lab quote and written scope decision first; route A or C |
| Certificate is factory-bound | Re-registration when switching ODM | Negotiate transfer/dual-source terms up front |
| Certification payback volume not reached | Capital loss | Payback volume is an M4 go/no-go number |
| Mains-voltage safety during prototyping | Risk to life | Isolation transformer, dim-bulb, discharge, never probe live alone |
| Thin margin; GST ambiguity | Business not viable | Premium positioning, GST-correct unit economics first |
| Competitor price response | Margin erosion | Reliability and warranty differentiation |
| Single-source IC/transformer | Supply disruption | Alternate shortlist, two suppliers, long-lead procurement checkpoint |
| Returns cluster after warranty | Brand damage | Life specified on core temperature; warranty matched to measured life |

**Assumptions (plan changes if wrong)**

- Selling price ₹450-600, BOM/wholesale figures, BIS fee ranges, assembly and packaging costs are approximate.
- Typical targets are industry-typical and will be re-calibrated from baseline.
- Standards, thermal limits and surge/ESD levels have not been verified here.
- The 150-265V rating is an owner decision.

**Milestones (each gate must pass before the next starts)**

- [ ] **M1 Baseline complete:** extra units bought, one torn down, final schematic, T2 measured, baseline column filled
  - Gate: every schematic net verified, baseline column of Section 3 complete
- [ ] **M2 Architecture and IC chosen:** 3 candidate QR + opto ICs compared, one selected, long-lead items identified
  - Gate: transformer calculation done from the reference design
- [ ] **M2b Spec freeze:** targets, input range decision and error budget locked
  - Gate: owner sign-off on the written spec
- [ ] **M2c Safety/creepage design review before PCB fabrication**
  - Gate: signed off, so a clearance violation is not found after fab
- [ ] **M3 Prototype v1:** 5-10 units, TC1-TC8
  - Gate: all Section 3 targets pass, or each deviation has a written waiver signed by the owner with a stated commercial impact
- [ ] **M4 Compliance route decided:** route A/B/C, lab quote, standard and scope confirmed
  - Gate: BIS timeline and cost in writing, and the certification payback volume stated
- [ ] **M5 Pilot batch:** 50-100 units, retailer feedback
  - Gate: return rate within target and unit economics positive

**Open questions**

- [ ] Do you confirm the 150-265V rated input, or keep 100-265V?
- [ ] Is ₹450-600 an MRP (GST-inclusive) or ex-GST?
- [ ] Which single application is the primary declared one (ITE/SMPS or LED driver)?
- [ ] Will assembly be in-house or through a contract manufacturer?
- [ ] Target monthly and lifetime volume?
