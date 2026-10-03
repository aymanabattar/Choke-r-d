# Design Review: 12V 5A (60W) AC-DC SMPS Technical Plan

Reviewed: 2026-10-03
Document under review: `smps_12v_5a_technical_plan.md` (dated 2026-10-03)
Reviewer role: electrical design / compliance / unit-economics review

---

## 0. Summary verdict

**Structure and process: approve.** Gated milestones, one test per requirement, explicit
`Unknown` flags on the baseline, and a clean legal boundary on the reference unit's brand and
R-number. This is better discipline than most commercial PSU specs.

**Requirements and design: do not freeze yet.** Four blocking defects (Section 1 below) where the
numbers contradict each other or contradict a regulatory threshold, plus an architecture
recommendation that is pointed at the higher-risk of the two viable options.

**Headline issues, in priority order:**

| # | Issue | Severity |
| --- | --- | --- |
| B1 | Error budget is impossible: load regulation alone consumes the entire ±5% output window | Blocking |
| B2 | Minimum efficiency target (78%) pushes input power above the 75W IEC 61000-3-2 threshold | Blocking |
| B3 | Rated input range (100-265V) and the test plan (90V / 270V) disagree | Blocking |
| B4 | BIS cost amortized over a 500-unit batch almost certainly makes the margin gate unreachable | Blocking |
| D1 | PSR-first architecture is the higher-risk path to these specs; cost delta to opto is immaterial | Major |
| D2 | OVP has a single point of failure in a PSR topology | Major |
| D3 | Single output capacitor cannot carry the secondary RMS ripple current at 5A | Major |
| D4 | Case temperature target sits exactly on the safety limit, with no margin | Major |
| D5 | Applicable standard depends on declared application; plan targets three incompatible markets | Major |
| M1 | No load-transient requirement, despite "low-ripple / noise-sensitive load" positioning | Major gap |
| M2 | No bulk capacitance requirement; "universal input" is an unexamined, costly assumption | Major gap |

---

## 1. Blocking defects

### B1. The output error budget is arithmetically impossible

Section 3 states three requirements that cannot coexist:

- Output voltage: **12.0V ±5%** → 11.40V to 12.60V, a ±0.60V window
- Line regulation: **≤ ±2%** → ±0.24V
- Load regulation: **≤ ±5%** → ±0.60V

Load regulation alone consumes 100% of the total window. That leaves zero budget for the initial
setpoint tolerance, line regulation, temperature drift, ripple, or ageing. Section 1's success
criterion ("12V ±5% across the full load range *and* input range") compounds the same error by
merging line and load into one ±5% figure.

**Fix:** write an explicit error budget that sums to the total, e.g.

| Contributor | Allocation |
| --- | --- |
| Setpoint tolerance at 25°C, 230V, 2.5A | ±1.0% |
| Line regulation over the rated range | ±1.0% |
| Load regulation, 0-5A | ±2.0% |
| Temperature drift, 0-50°C | ±1.0% |
| **Total (worst case sum)** | **±5.0%** |

Also specify **where** voltage is measured. "DMM at each load point" (T2) is ambiguous. Use a
4-wire measurement at the output terminal screws, and state it.

### B2. The minimum efficiency target breaches the IEC 61000-3-2 harmonic threshold

IEC 61000-3-2 harmonic current limits apply to equipment drawing **more than 75W active input
power**. Checking the plan's own targets:

| Efficiency | Input power at 60W out | In scope? |
| --- | --- | --- |
| 82% (target) | 73.2W | No — but only 1.8W of margin |
| 80% | 75.0W | Exactly on the threshold |
| **78% (stated minimum)** | **76.9W** | **Yes — limits apply** |

A design that only meets its stated *minimum* is a non-compliant design. And 1.8W of margin at the
*target* is inside measurement uncertainty, before accounting for the fact that input power rises
at low line.

Separately, **82% is a weak target for a 60W flyback in 2026**. A quasi-resonant or valley-switching
controller with secondary-side feedback reaches 87-89% at this power level. The efficiency target is
not just a compliance and heat question — it is the root cause of defect D4 (thermals) and a
contributor to the capacitor life problem (D3).

**Fix:** set efficiency **≥ 86% at full load, 230V, with 84% as the absolute floor** (input power
69.8W / 71.4W — comfortable margin under 75W). Set no-load power **≤ 0.15W**, not 0.5W; modern PSR
and QR controllers achieve this routinely and 0.5W is a 2010-era figure.

Note: harmonics/EMC are generally **not** part of BIS CRS scope (which covers safety). Treat this as
an export, OEM-customer and good-engineering requirement rather than a domestic legal blocker —
but do not design to breach it, because it is the kind of thing a large buyer audits.

### B3. The rated input range and the test plan contradict each other

- Section 3 requirement: input range **100-265V AC**
- Section 3 test method for the same row: "test at **90V**, 230V, **270V**"
- Section 3 line regulation row: "≤ ±2% (**90-265V**)"
- Section 9 T3: "**90**, 230, **270**V AC at full load", acceptance "line regulation ≤ ±2%"

So the regulation pass/fail is specified at 90V, which is *below* the rated minimum, and tests run
at 270V, which is *above* the rated maximum. Three different ranges appear across four lines.

This matters because safety standards test at defined multiples of the *rated* range (typically
0.9× to 1.1× of rated, so 90V and 292V for a 100-265V claim), and because the rated low-line figure
drives the bulk capacitor, transformer and MOSFET sizing — see M2, where the choice is worth real
money.

**Fix:** pick one rated range, put it on the label, and define two test tiers:

- **Performance tests** (regulation, ripple, efficiency) — inside the rated range only
- **Margin / abnormal tests** — at 0.9× V_min and 1.1× V_max, where the acceptance is "no damage,
  safe behaviour", not "meets regulation spec"

### B4. BIS amortization over 500 units breaks the margin gate

Section 8's acceptance criterion is "margin ≥ 25% at a **500-unit batch**", with unit economics
including "per-unit BIS amortization". Running those numbers:

- IS 13252 / CRS lab testing for one model: order **₹40,000-1,00,000+** (verify with a quote)
- Over 500 units: **₹80-200 per unit**
- Against a BOM of ~₹150 and a net-to-brand price of roughly ₹270-300 at ₹450 retail

Test cost alone is 30-70% of BOM at that volume. Add assembly and test (₹30-50), packaging
(₹15-25), a returns reserve, and **GST at 18% — which the plan never mentions.** If ₹450-600 is an
MRP (GST-inclusive, as Indian retail pricing normally is), realizable revenue drops ~15% before
any of this.

**Fix:**
- State whether ₹450-600 is MRP-inclusive or ex-GST. This single ambiguity is worth ~15% of revenue.
- Amortize certification over a realistic **lifetime** volume, not the first batch. Reaching
  under ₹20/unit needs roughly **3,000-5,000 units**.
- Treat certification as an upfront capital item with a stated payback volume, and make that
  volume an explicit go/no-go number in the M4 gate.
- This is the strongest argument in the document for starting with route A or C (Section 10) —
  make that linkage explicit rather than leaving it as a general preference.

---

## 2. Design-level concerns

### D1. The architecture recommendation is backwards on risk

Section 4 recommends prototyping PSR first and falling back to opto + TL431 "only if load
regulation or ripple specs are missed". Three problems:

1. **60W / 5A is at the upper edge of comfortable PSR territory.** Most PSR controllers target
   ≤45W, and PSR constant-voltage accuracy degrades as output current and transformer/auxiliary-
   winding tolerances grow. 5A is a hard case.
2. **The specs as written (after fixing B1) are near the limit of what PSR delivers**, and PSR is
   notably poor at load transients (M1) and at light-load burst-mode ripple.
3. **The cost delta is immaterial at this price point.** Opto + TL431 + bias parts is roughly
   ₹8-15. On a ₹150 BOM at ₹450-600 retail, that is noise. The plan's own Section 8 says *"do not
   cut cost on"* the differentiating parts — regulation accuracy belongs on that list.

The table also over-weights optocoupler CTR ageing as a risk. It is a well-understood, solved
problem: choose a graded high-CTR part from a reputable vendor, derate CTR by ~50% over life, and
the loop stays stable. That is routine, not a research item.

**Recommendation: invert the order.** Build v1 with a **quasi-resonant flyback controller plus
optocoupler + TL431 secondary-side feedback**. This is the low-risk path that hits the regulation,
ripple, transient *and* the ≥86% efficiency target from B2 simultaneously — and the efficiency gain
is what fixes the thermal problem in D4. Keep PSR as a **phase-2 cost-down**, attempted only once
the specs are proven and measurable, so you are optimizing against a known-good reference instead
of guessing. Re-running M2/M3 because PSR missed the spec costs far more than ₹15/unit.

Also missing from Section 4: **switching frequency selection.** Choose f_sw to stay clear of the
150 kHz CISPR band edge (65-100 kHz is the usual choice), and specify **frequency jitter /
dithering**, which is the cheapest available route to the 6 dB EMI margin that T9 asks for.

### D2. OVP has a single point of failure

Section 5 lists OVP implementation as "controller built-in or zener clamp", acceptance "open
feedback: output ≤ 15V".

In a PSR design, the controller senses output voltage **through the auxiliary winding**. If the
fault is a break in that sense path — the most likely feedback failure — the controller's built-in
OVP is blind to it and the output runs away well past 15V. "Controller built-in" and "open
feedback" are, in PSR, the same failure.

Two further points:
- **15V is too high as a limit.** Many 12V loads (CCTV cameras, LED strip controllers, ESP32 buck
  modules) use 16V-rated input capacitors. 15V leaves ~1V of margin on a part at its rating.
- The protection list omits several realistic failure modes.

**Fix:**
- Require **secondary-side OVP independent of the feedback path** — a zener/TL431-triggered
  crowbar or shutdown on the secondary, latching off until AC is recycled. Acceptance: **≤ 14.5V
  peak** with the feedback path open-circuited.
- Add to the Section 5 table: **output reverse voltage** (CCTV sites are routinely battery-backed,
  so back-feed into the output is a real condition); **output capacitor open and short**;
  **brownout / low-line startup into full load**; **startup into a large capacitive load**
  (10,000µF) and into a constant-power DC-DC load, whose negative incremental resistance can cause
  startup hiccup; **5 consecutive short-circuit applications**.
- **Specify OCP/SCP recovery behaviour explicitly: auto-recovery, not latch.** A CCTV supply that
  latches off after a transient fault means a site visit. The plan never states which it wants.

### D3. One output capacitor cannot carry the secondary ripple current

Section 2 notes "Single output cap, affects ripple" as an observation. It should be a requirement,
because the numbers are severe.

For a DCM flyback at 5A output with secondary conduction duty D' ≈ 0.45:

- Secondary peak current: I_pk = 2·I_out / D' ≈ **22A**
- Secondary RMS: I_pk·√(D'/3) ≈ **8.6A rms**
- Capacitor RMS: √(8.6² − 5²) ≈ **7A rms**

A single 1000µF/16V low-ESR 105°C capacitor handles roughly 1.5-2.2A rms. You need a **bank of 3-4
in parallel, or 2 capacitors plus a post-LC filter stage** — the latter being the better answer,
since it also buys the 150 mVpp ripple target and reduces high-frequency noise for the
"noise-sensitive load" positioning.

**Fix:** add a requirement row — *output capacitor bank sized for the measured secondary RMS ripple
current with ≥30% derating, 105°C, with a post-LC filter* — and verify I_rms by measurement or
simulation at low line, where it is worst. This is a genuine BOM addition; budget for it rather
than discovering it at T2.

### D4. The thermal target sits exactly on the safety limit

Section 6: "Case surface temperature ≤ 70°C at 5A and 40°C ambient (assumption)".

70°C is approximately the IEC 60950-1 / 62368-1 limit for a **metal** enclosure surface that may be
touched. So the design target *is* the compliance limit — zero margin. Worse, the standards' limits
are absolute temperatures evaluated at a defined test ambient. If the lab tests at 25°C and you are
rated to 40°C, a design measuring 55°C on the bench reaches ~70°C in service and fails at its own
rated ambient.

Two more thermal items the plan misses:

- **Heatsinking the primary switch to the earthed aluminium case is an EMI/safety trade-off, not
  just a thermal one.** A thermal pad from the MOSFET tab (switching node, 400-600V) to a
  PE-bonded case needs adequate dielectric strength (specify ≥4 kV and a minimum thickness), and
  the resulting drain-to-PE capacitance **directly worsens common-mode conducted emissions** —
  working against the 6 dB margin in T9. Section 6 presents case contact as pure upside.
- **Real installed ambient is not 40°C.** These units go inside dusty, unventilated CCTV junction
  boxes. Internal ambient of 50-60°C is normal.

**Fix:** target **≤ 60°C case at 40°C ambient** with 70°C as the absolute never-exceed; rate the
unit to **50°C ambient with a published derating curve** above that; fix the efficiency target per
B2 so the dissipation budget drops from ~13-15W to ~8-9W, which is what actually makes this
achievable; and specify thermal pad dielectric rating plus a CM-emissions check with and without
the case-contact scheme.

Also: **T4's 2-hour thermal soak is too short** for an aluminium-cased unit. Use *"until the
temperature rise is < 2°C over 30 minutes"*, in the final mounting orientation, installed inside a
representative enclosure.

### D5. The applicable standard depends on which market you declare

The plan markets simultaneously to **CCTV, LED strip, and ESP32/IoT**. Those are not one regulatory
product:

- As **ITE / general SMPS** → IS 13252(Part 1), harmonics threshold 75W (B2 applies as analysed)
- As an **LED driver / controlgear** → a different IS applies (the IS 15885 family), and critically
  **IEC 61000-3-2 Class C governs lighting equipment above 25W, not 75W** — which would require
  **active PFC**, directly contradicting Section 3's "Power factor: not mandated at this class"

Section 3 flags PF as an assumption to confirm, which is right, but the plan does not connect it to
the market positioning in Section 10. Declaring the product an LED driver changes the BOM.

Also, verify two things the plan does not raise:

- **BIS has been transitioning ITE from IS 13252 to IS 62368-1.** Confirm which standard *new*
  registrations must be filed under before paying for a lab slot against the older one.
- **Whether an enclosed SMPS module sold to installers is in CRS scope at all.** CRS categories are
  specified per product type ("power adaptors for IT equipment", etc.); a component-style
  industrial supply is a grey area that changes the whole route. Settle this *before* M4.

**Fix:** declare one primary application for certification purposes, verify the standard and the PF
requirement against it, and treat the other two segments as secondary markets sold under the same
certification only where that is legitimate.

---

## 3. Missing requirements

### M1. No load-transient specification

For a product positioned on noise and reliability for CCTV, LED and MCU loads, dynamic response is
a core requirement and it is entirely absent. PSR designs in particular have slow, sampled
feedback loops and respond poorly.

**Add:** load step 50% → 100% → 50% at 1A/µs; output deviation ≤ ±5%; recovery to within ±1% in
≤ 2 ms; no oscillation or ringing. Test with a scope at the output terminals.

### M2. No bulk capacitance requirement — and "universal input" is an expensive unexamined assumption

EC1's value is listed as illegible in Section 2 and never becomes a requirement anywhere, yet it
determines hold-up, low-line operation, inrush and life.

The stated hold-up requirement (**≥ 10 ms at 230V full load**) is *non-binding*:

    C = 2·P·t / (V1² − V2²) = 2(73)(0.01) / (325² − 80²) ≈ 15 µF

15µF meets it. The binding constraint is **low-line ripple**, not hold-up, and that is where the
input-range choice gets expensive:

| Rated V_min | Required bulk cap (approx.) |
| --- | --- |
| 100V AC | **82-100 µF / 400V** |
| 150V AC | **47 µF / 400V** |
| 170V AC | **33 µF / 400V** |

**This is the most valuable cost lever in the design, and Section 8 misses it entirely.** Section 3's
own rationale for the input range is *"mains variation in India"* — but the actual Indian threat is
**sag to roughly 150-180V**, not operation at 100V. A 100V claim is copied from generic universal-input
labelling and has near-zero value in the target market.

**Recommendation: rate the input 150-265V AC** (or 120-265V for a safety margin). This
simultaneously:

- Cuts the bulk capacitor ~2-3× in capacitance, cost and volume
- Reduces inrush energy
- Raises efficiency at the actual operating point, helping B2 and D4
- Relaxes the transformer and MOSFET design (lower peak primary current)
- **Retains full brownout robustness for the real Indian condition**

Cost: you lose a "universal input" marketing line that no Indian CCTV installer values. Add a bulk
capacitance requirement row derived from low-line ripple plus its RMS ripple-current rating.

### M3. Capacitor life is specified against the wrong variable

Section 5 asks for "≥ 20,000 hr at 50°C **ambient**". Life depends on **core temperature**, not
ambient, and the gap is large:

| Capacitor core temp | Life (2000 h / 105°C base part) |
| --- | --- |
| 60°C | ~45,000 h |
| **80°C** (realistic inside a 40°C-ambient metal case at 13W) | **~11,300 h** |

So the stated target is missed by roughly 2× under realistic conditions, while appearing to pass if
you only measure ambient. Note also that 20,000 h is **2.3 years of 24/7 operation** — and Section 10
offers a 1-year warranty. On a product positioned on reliability, returns will cluster just outside
the warranty window. That is the worst possible failure pattern for the brand you are building.

**Fix:**
- Specify life against **measured core temperature** (thermocouple on the can), not ambient.
- Specify the **base endurance rating in the BOM**: ≥ 5,000 h at 105°C (long-life series), not
  merely "105°C".
- Then re-derive: with ≥86% efficiency (B2), ≤60°C case (D4) and 5,000 h parts, a realistic
  **50,000 h+** becomes achievable — at which point **a 2- or 3-year warranty becomes the headline
  differentiator** against the ₹250 generic. That is a far stronger market claim than "low ripple",
  and it falls out of fixing B2 and D4 anyway.

### M4. Numeric gaps in the protection and safety requirements

- **MOV voltage rating is unspecified, and the obvious choice is wrong.** For a 265V rms maximum
  input, the varistor voltage must be ≈1.6× the rms line, i.e. a **385-470V class part**
  (S14K385 / S14K420 or equivalent). Fitting the commonly stocked 275V part on a 265V-rated input
  causes progressive MOV degradation and eventual thermal failure. State the part class and the
  surge level it must survive (e.g. IEC 61000-4-5 1 kV / 2 kV combination wave).
- **Inrush and NTC value must be consistent.** At 265V AC, peak is 375V; for ≤40A the total series
  resistance must be **≥ 9.4Ω**, so the NTC must be ≥10Ω cold. Also check the NTC's **steady-state
  dissipation**: with no PFC, power factor is ~0.5, so at low line the RMS line current is ~1.5A,
  and NTC self-heating becomes significant. Specify both cold resistance and hot-state dissipation.
  Also state the source impedance the inrush figure is measured at — otherwise the number is
  not reproducible.
- **Fuse characteristics are unspecified.** Require a **time-lag (T) type**, rated for 265V minimum
  with adequate breaking capacity (e.g. 1500A), sized to survive the NTC-limited inrush and the
  1000 cycles of T6 without fatigue.
- **Touch-current / leakage limit is not stated**, and it is what bounds Y-capacitor selection —
  which is in turn your main EMI lever. This tension (EMI wants more Y-capacitance, leakage limits
  it) is **the** central EMI trade-off in an offline flyback and the document does not mention it.
  State the limit (3.5 mA for Class I ITE; ≤0.25 mA if you want margin) and derive the maximum Y
  value from it.
- **A single Y-capacitor across a reinforced-insulation barrier must be Y1 class.** Section 2
  observes one Y-cap (CY1). A single Y2 provides basic/supplementary insulation only; reinforced
  requires **Y1, or two Y2 in series**. Make this a BOM requirement.
- **Transformer construction is unspecified.** Reinforced insulation across the barrier needs
  triple-insulated secondary wire or three layers of barrier tape with margin tape, and distance
  through insulation ≥0.4 mm. Section 6 covers PCB creepage but not the transformer, which is
  where the barrier actually lives.
- **Separate type-test from production test for hipot.** Section 7's ~3 kV AC is correct as a
  *type* test for reinforced insulation at 230V mains. A 100% production-line test is normally a
  shortened, lower-voltage test (1.5-2.5 kV, 1 s) — testing every unit at the full type-test level
  degrades the insulation you are shipping.
- **OTP acceptance is not a test.** "Heat gun test causes shutdown" is uncontrolled. Specify the
  trip temperature, the sensed component, a thermocouple reference, and that the trip occurs
  below the component's datasheet limit — plus the recovery behaviour.

### M5. Output grounding is unspecified — and it is a known CCTV failure mode

Section 6 mentions "the earth ring bonded to the chassis" but never states whether the output V− is
tied to PE or floating. This directly determines whether installations develop ground loops, a
common cause of hum bars and video noise in multi-camera CCTV systems sharing one supply.

**Add:** output floating relative to PE (confirmed SELV), with an **optional user-fittable V−-to-PE
link**, documented in the packaging. This is a real differentiator for installers.

### M6. Cable voltage drop is the actual field failure mode, and the wire spec ignores it

Section 6 specifies "≥ 0.75 mm² for 5A". The ampacity is fine; the drop is not:

    0.75 mm² copper ≈ 0.023 Ω/m → a 10 m run (20 m of conductor) ≈ 0.46 Ω
    At 5A: 2.3V drop — a 19% loss, delivering 9.7V to the camera

In practice, **cable drop, not supply failure, is the most common reason a 12V CCTV supply
"doesn't work"**. Your product will be blamed for it and returned.

**Fix:** publish a **gauge-vs-length table** on the packaging rather than a single gauge figure, and
evaluate offering a **12.4-12.5V nominal setpoint** (still inside the ±5% window) to pre-compensate
typical runs. Cheap, and it directly reduces the return rate that Section 10 gates on.

### M7. Other absent requirement categories

Operating/storage temperature and humidity range; altitude; IP rating and mounting orientation;
output overshoot and monotonicity at turn-on (matters for MCU loads); minimum load and **ripple at
no-load and 10% load** (burst-mode ripple is often *worse* at light load than at the 5A point where
the plan specifies it); **audible noise** at light load (transformer singing in burst mode is a top
complaint driver and a return cause); peak/surge load capability (see below); an MTBF estimate;
and per-unit test records plus batch traceability, without which the Section 8 returns reserve
cannot be diagnosed or improved.

**On peak load — there is a live conflict.** Section 5 sets OCP to limit or hiccup "above 6A"
(120%). But CCTV loads surge: IR illuminators switch on at dusk, PTZ motors start. A 6A threshold
will nuisance-trip on legitimate load steps. Either define OCP with a **time profile** (e.g. 7.5A
instantaneous, folding back after 100 ms) or specify a peak rating (6A for 10 s) and design for it.
As written, the protection spec fights the target application.

---

## 4. Test plan gaps

Section 9 is well constructed — numeric acceptance on every line, run on both baseline and
prototype. Gaps:

- **A variac is not an isolation transformer.** Section 9's safety rule correctly demands an
  isolation transformer, but T1 says "raise voltage gradually with a variac" without noting these
  are different instruments serving different purposes. Make the chain explicit:
  mains → isolation transformer → variac → DUT. Add a **dim-bulb tester for first power-on** — it
  prevents the spectacular first-fault failures.
- **No surge, ESD or EFT test numbers.** Section 5 says "surge test (in lab)" with no level; there
  is no T-number for it, and no ESD (contact/air discharge to the metal case, which an installer
  will touch) or EFT/burst test at all.
- **No damp-heat test**, despite the plan prescribing conformal coating specifically for humidity.
  Add 40°C / 93% RH for 48 h followed by a re-test.
- **No transport test.** A heavy aluminium-cased unit in retail packaging needs drop and vibration
  testing, or you will absorb transit damage as warranty returns.
- **No dropout / brownout ride-through test**, despite Indian mains being the stated rationale for
  the input range.
- **T7 burn-in is statistically weak.** 0 failures in 5-10 units over 72 h gives roughly 80%
  reliability at 90% confidence — nearly no information. State what it is *for*: infant-mortality
  and workmanship screening, not reliability demonstration. To make it informative, run it at
  **elevated ambient (45-50°C) and 110% load**, and separately define a **shorter 100% production
  burn-in** (30-60 min at full load, hot) for the pilot batch. Also note that on/off cycling (T6)
  surfaces more failures per hour than steady soak — consider interleaving them.
- **Section 10's "return rate ≤ 3%"** has no measurement window or denominator. Define it:
  units returned within N days ÷ units shipped in the same cohort.

---

## 5. Milestones, risks and sequencing

Milestone gating is good. Three changes:

1. **M3's gate is a loophole.** *"Section 3 targets pass, **or deviations documented**"* lets a
   failing prototype through a gate whose entire purpose is to stop one. Replace with: all targets
   pass, or each deviation has a written waiver signed by the owner with a stated commercial
   impact.
2. **Missing gates.** Add a **safety/creepage design review before PCB fabrication** (finding a
   clearance violation after fab costs a full spin and 3-4 weeks), a **spec-freeze** milestone
   between M2 and M3, and a **long-lead procurement** checkpoint — a 4-week IC lead time (Section 4)
   quietly sets the floor on the whole schedule.
3. **M1 is blocked on a third party.** The entire plan's first gate waits on someone else providing
   a solder-side photo (open question 1). **Buy 3-5 more baseline units (₹750-1,250) and tear one
   down destructively.** This unblocks M1 immediately, costs less than a day of delay, and yields
   unit-to-unit variance data the photos could never give. For a plan whose stated top risk is
   "topology/IC unknown", spending ₹1,000 to eliminate it is the highest-return action available.

**One risk to add to Section 11:** under BIS CRS the registration is held by the **manufacturer**,
for a specific model at a specific factory, with your brand recorded on it. Section 10 calls this
"supplier dependency", which understates it — **you cannot move the certificate to another
factory.** Switching ODMs means re-registering and re-paying. That belongs in the risk table with
a mitigation (e.g. negotiate certificate-transfer or dual-source terms up front), and it should
inform the route A/B/C decision at M4.

**One legal point to add to Section 7's marking list:** Legal Metrology packaged-commodity
declarations are mandatory on Indian retail packs (MRP, manufacturer/importer name and address, net
quantity, consumer-care contact, month/year of manufacture) and are actively enforced. The plan
covers BIS marking and brand cleanliness but not this. Also verify **E-Waste EPR registration**
applicability, and import/IEC requirements if boards are sourced abroad.

**Also worth a line in Section 1's out-of-scope:** the plan correctly notes the flyback topology is
generic prior art and the brand is not. Extend that to **PCB artwork** — clean-room the schematic
from your measurements and do your own layout. Copying board artwork verbatim raises a layout-rights
question that copying a topology does not, and it costs nothing to avoid.

---

## 6. Minor and editorial

- **Identifier collision:** `T2` is the transformer in Sections 2 and 6, and also "T2 Load sweep" in
  Section 9. Rename the tests `TC1`-`TC9`, or the transformer `TX1`.
- **Probable transcription error, Section 2:** startup resistors are marked `754` = 750 kΩ, correct.
  But `R15, R16 = 75 kΩ` is then given for the RCD clamp — 75 kΩ would be marked `753`. If R15/R16
  also read `754`, they are 750 kΩ. Note that **750 kΩ is implausible for an RCD clamp resistor**
  (typical 22-100 kΩ at this power), while 750 kΩ is exactly right for startup. Re-read the markings
  before building the schematic on them.
- **Section 3 frequency:** 47-63 Hz is fine and covers export, but Indian mains is 50 Hz. Harmless.
- **Section 8 cost lever "output terminals 4 → 2" is the wrong lever.** Four terminals (2× V+,
  2× V−) let a CCTV installer feed two cameras without a splice. That is a *feature* in your target
  market, worth more than the ~₹8 it saves. Keep 4; cut cost via the input-range change in M2
  instead, which is worth far more and costs you nothing a customer values.
- **Section 5 fuse/NTC/MOV ordering** is correct as described (L → fuse → MOV) but incomplete.
  State the full chain: L → fuse → NTC → MOV + X-cap → CM choke → bridge.
- The baseline-cost estimate (₹250 retail → ₹150-170 wholesale → ₹90-120 BOM) is roughly sane for
  this market; ₹110-140 factory cost / ₹80-110 BOM is my estimate. Either way it implies the
  baseline uses the cheapest possible everything, consistent with the missing fuse/NTC/MOV — and
  it means the generic competitor has room to cut price in response. Worth stating as a risk.

---

## 7. Recommended requirement changes, consolidated

| Section | Current | Change to |
| --- | --- | --- |
| 3 | Input 100-265V; tests at 90/270V | **Rate 150-265V**; performance tests in-range; margin tests at 0.9×/1.1× rated |
| 3 | Output 12.0V ±5%, line ±2%, load ±5% | Explicit error budget summing to ±5% (setpoint 1 / line 1 / load 2 / temp 1); measured 4-wire at terminals |
| 3 | Efficiency ≥82% target, ≥78% min | **≥86% target, ≥84% floor** at 230V full load |
| 3 | No-load ≤0.5W | **≤0.15W** |
| 3 | Hold-up ≥10ms @230V | Keep, but add a **bulk capacitance requirement** derived from low-line ripple + RMS ripple current |
| 3 | Ripple ≤150 mVpp at 5A | Specify **across the load range incl. no-load and 10%**; add **load-transient spec** (±5% dev, <2 ms recovery) |
| 3 | 5A continuous, no ambient stated | **5A to 50°C ambient**, with published derating curve above |
| 4 | PSR first, opto as fallback | **QR flyback + opto/TL431 for v1**; PSR as phase-2 cost-down. Specify f_sw clear of 150 kHz + dithering |
| 5 | OVP via controller, ≤15V | **Independent secondary-side OVP, latching, ≤14.5V** |
| 5 | OCP "above 6A" | OCP with a **time profile** (or a stated peak rating); **auto-recovery, not latch** |
| 5 | MOV, NTC, fuse unvalued | MOV **385-470V class**; NTC **≥10Ω cold** w/ hot dissipation checked; fuse **time-lag, 265V, 1500A breaking** |
| 5 | Life ≥20,000 h at 50°C ambient | **≥50,000 h at measured core temperature**, parts rated **≥5,000 h / 105°C** |
| 5 | — | Add **touch-current limit** bounding Y-cap; require **Y1** (or 2× Y2) across the barrier |
| 6 | Case ≤70°C at 40°C ambient | **≤60°C target, 70°C absolute**; thermal pad ≥4 kV; CM-emissions check on case-contact scheme |
| 6 | Wire ≥0.75 mm² | **Gauge-vs-length table**; evaluate 12.4V nominal setpoint |
| 6 | — | State **output floating w/ optional V−-to-PE link** |
| 7 | Hipot ~3 kV | Split **type test (~3 kV)** from **production test (1.5-2.5 kV, 1 s)**; add transformer insulation construction |
| 7 | — | Confirm **IS 13252 vs IS 62368-1** for new registrations, and **CRS scope** for this product form |
| 8 | Margin ≥25% at 500 units | Amortize certification over **lifetime volume**; state the **payback volume** as an M4 gate; resolve **GST-inclusive vs ex-GST** pricing |
| 9 | T4 soak 2 h; T7 72 h / 5-10 units | T4 **to thermal equilibrium**, installed orientation; T7 at **45-50°C / 110% load**, plus a defined production burn-in |
| 9 | — | Add **surge/ESD/EFT with levels**, damp heat, transport, dropout, startup-into-capacitive-load |

---

## 8. What the plan gets right

Worth preserving explicitly, because these are the parts most plans get wrong:

- **Every requirement has a numeric acceptance test.** Rare and valuable.
- **`Unknown` is stated as `Unknown`** rather than guessed, and Section 11 correctly names
  topology uncertainty as the top risk.
- **The legal boundary is drawn correctly** — generic topology is fair game, brand/marking/R-number
  is not, and that distinction is stated precisely.
- **"Do not cut cost on: fuse, NTC, MOV, Y-cap rating, capacitor grade"** is exactly the right
  instinct, and it is the actual business thesis.
- **The mains-safety rule** (isolation transformer, discharge the bulk cap, never probe live alone)
  is present and prominent. That is not a formality — it is the single highest-consequence line in
  the document.
- **The gated-milestone structure with a baseline-first sequence** is correct. Fix the M3 loophole
  and unblock M1 by buying teardown units, and the process is sound.
