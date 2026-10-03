# Design Review Round 2: 12V 5A (60W) AC-DC SMPS Technical Plan v2

Reviewed: 2026-10-03
Document under review: `smps_12v_5a_technical_plan_v2.md`
Prior round: `smps_12v_5a_plan_review.md` (v1 review)

---

## 0. Verdict

**v2 closes all four blocking defects and every major concern from round 1.** The change log is
exemplary — separating *accepted* / *accepted with modification* / *not taken, with reasons* is
exactly how a review cycle should be run, and it is what surfaced an error in my own round-1
recommendation (see Section 1).

**v2 is close to spec-freeze quality.** What remains is not a repeat of round 1's problems. It is a
smaller set of **internal inconsistencies created by the new requirements themselves** — the new
numbers in Sections 3, 5, 6 and 9 do not yet all agree with each other.

| # | Issue | Severity |
| --- | --- | --- |
| C1 | Bulk capacitor specified at 400V; violates v2's own derating rule and the surge case | Blocking |
| C2 | Static error budget and load-transient spec are mutually inconsistent (B1 recurring) | Blocking |
| C3 | TC8 burn-in (110% load, 45-50°C) runs outside the product's own rated envelope | Major |
| C4 | Thermal budget stated as 8-9W; it is 9.8W at target and 11.4W at the floor | Major |
| C5 | Latching OVP at 14.5V is not coordinated with load-dump overshoot | Major |
| C6 | Fuse / NTC / MOV coordination specified part-by-part but never checked as a system | Major |
| C7 | Error budget has zero headroom and omits ripple; no stated DC-average vs instantaneous basis | Major |
| C8 | Brownout/dropout acceptance criterion is circular ("defined behaviour") | Moderate |

Items C1, C4 and C7 are arithmetic. C2, C3, C5 and C6 are requirements that contradict each other
and will be discovered at the test bench if not fixed now.

---

## 1. Where v2 corrected me

### MOV class — v2 is right, round 1 was wrong

**My round-1 recommendation of a 385-470V class MOV was incorrect.** I conflated two different
numbers: a varistor's **V_1mA (varistor voltage)** is roughly 1.5-1.6× its **V_RMS (maximum
continuous AC operating voltage)** rating — e.g. an S14K275 is rated 275V rms with V_1mA ≈ 430V.
I applied that 1.6× factor to the line voltage instead, which is the wrong place for it.

The correct selection rule is **V_RMS rating ≥ roughly 1.1 × maximum rated line rms**. For a 265V
input that is **292V minimum → a 300-320V class part**, exactly as v2 specifies. An over-rated MOV
clamps too high to protect anything, which is the real penalty.

So: **v2's 300-320V rms-class specification is correct — keep it.** The part of my finding that
survives is the narrower one: a 275V-class MOV on a 265V-rated input is only 1.04× and will degrade,
so the commonly stocked part is still the wrong choice.

One refinement on the *reasoning*, because it matters downstream. v2 justifies 300-320V by saying a
385V part's clamp voltage "would exceed what a 400V bulk capacitor, bridge and MOSFET tolerate."
The MOV rating rule above is the primary reason; the clamp-voltage concern is a secondary effect
(the MOV sits ahead of the bridge, and let-through energy reaches the bulk cap through the series
impedance of NTC, choke and bridge). But v2 has stumbled onto something important by raising it —
see **C1**, where the bulk capacitor voltage rating turns out to be a real defect.

### OVP in PSR — v2's correction accepted, and the conclusion is now stronger

v2 is right that "a broken sense path always causes runaway" is controller-dependent; many PSR
controllers detect loss of auxiliary feedback and shut down. My phrasing overstated it.

But note what the architecture change does to this argument. In the **QR + optocoupler/TL431**
topology v2 selected for v1, loss of feedback is *less* ambiguous, not more: an open optocoupler or
open TL431 sends zero feedback current, the controller reads that as "output too low," and drives
to maximum duty. That is a genuine, well-documented runaway. **v2's independent secondary-side OVP
requirement is more justified under the chosen architecture than it was under the one I was arguing
against.** Keep it, and see C5 for the threshold.

### IEC 61000-3-2 posture — accepted

Keeping the 75W threshold as a design margin and customer-audit item rather than a legal blocker is
the correct call, and I had already noted harmonics are generally outside BIS CRS scope. Since v2
raised efficiency to ≥86% / 84% floor for thermal and life reasons anyway, the engineering outcome
is identical. Input power 69.8W / 71.4W is correctly computed and clears 75W in both cases.

### Unverified estimates — accepted

BIS fee ranges, the 70°C touch limit, surge/ESD levels and the 150-180V sag figure were my
estimates and v2 is right to mark them unverified. v2's handling is safe in each case: it targets
≤60°C with 70°C as a never-exceed, so the design does not depend on which figure is correct.

---

## 2. Blocking defects in v2

### C1. The bulk capacitor voltage rating is wrong, and contradicts v2's own derating rule

Section 3 specifies: *"Bulk capacitor EC1 | 47-100 µF / **400V**"*.

At the rated maximum of 265V rms, the rectified peak is:

    265 × √2 = 375V

That is **94% of a 400V part's rating in normal steady-state operation**, before any surge. And
Section 5's own component rule states:

> Derating: capacitor voltage **≥ 1.2x worst case**

    375V × 1.2 = 450V

**Section 3 violates Section 5 by 50V.** Standard practice for any 265V-rated input is a **450V**
bulk capacitor; 400V is for 230V-only designs. v2's own MOV discussion raises exactly this concern
and then specifies the part that fails it.

The surge case makes it worse. For a 2 kV / 1 kA combination wave, the charge reaching the bulk cap
through the bridge is order 10 mC, so:

    ΔV ≈ Q/C = 10 mC / 47 µF ≈ 200V

on top of the 375V operating peak. The series impedance (NTC, CM choke) and the MOV's diversion
reduce this substantially in practice, but it shows the 25V of margin on a 400V part is not a
margin at all. **This is also the mechanism that turns a survivable surge into a dead unit** — and
the smaller bulk capacitor that the input-range reduction buys makes ΔV *larger*, not smaller. That
trade-off is not mentioned anywhere in v2.

**Fix:** specify **450V** for EC1. Cost impact is real but modest and is more than covered by the
capacitance reduction from the input-range change (82-100µF/400V → ~47-68µF/450V is still a net
saving in cost and volume). Verify the surge-induced ΔV in TC11 by scoping the bulk rail during the
surge test, not just by checking the unit still works afterwards.

### C2. The static error budget and the load-transient spec contradict each other

Two Section 3 requirements:

- Output: within **±5% worst case**, as the sum of the error budget
- Load transient: deviation **≤ ±5%**, recovery to ±1% in ≤2 ms

If the static worst case already sits at the ±5% edge, a ±5% transient excursion on top of it
reaches **±10%**. As written, these two rows cannot both be satisfied at the worst-case static
corner.

This is defect B1 from round 1 reappearing in a new place: v2 fixed the static budget's internal
arithmetic but did not reconcile it against the dynamic requirement it added at the same time.

**Fix:** make the transient allowance part of one total window, which is how it is normally
specified:

| Condition | Window |
| --- | --- |
| Static, worst-case corner (DC average) | **±4.0%** |
| Transient excursion, during a load step | **±7%** peak, returning inside ±4% within 2 ms |
| Absolute never-exceed, any condition | **±10%** (11.4V-13.2V, respecting load device ratings) |

Then re-derive the static budget to fit ±4.0% (see C7).

---

## 3. Major concerns

### C3. TC8 burn-in runs outside the product's own rated envelope

Three requirements that do not fit together:

- Section 3: **5A at ambient up to 50°C, with a derating curve above**
- Section 6: case ≤60°C at **5A and 40°C ambient**; rated to 50°C ambient **with derating above**
- TC9/TC8: burn-in at **110% load (5.5A) and 45-50°C ambient** for 72 h

At 45-50°C ambient the derating curve may already have reduced the permitted output *below* 5A, yet
TC8 demands 5.5A there for 72 hours. **The acceptance test asks for a condition the datasheet does
not promise.** As written, a unit can fail TC8 while fully meeting spec — or worse, TC8 passes and
the derating curve is quietly fiction.

**Fix:** choose one and state it explicitly.

- **Option A (recommended):** make TC8 a deliberate overstress screen, labelled as such: *"110%
  load at 45-50°C intentionally exceeds the rated envelope; it is an infant-mortality screen, not a
  demonstration of rated operation. Thermal limits may be exceeded; the acceptance is zero
  failures and ≤1% drift, not compliance with Section 6."*
- **Option B:** run TC8 at 100% load / 50°C ambient (inside the envelope) and make the overstress a
  separate, shorter HALT-style test.

Either way, define the derating curve numerically **before** TC8 is run, or the test has no
reference. Note the curve is also what the OCP threshold must sit above (see below).

### C4. The thermal budget is understated by 20-30%

Section 6 states: *"At ≥86% efficiency, dissipation is about **8-9W** instead of 13-15W."*

    At 86% (target):  60/0.86 − 60 = 9.8W
    At 84% (floor):   60/0.84 − 60 = 11.4W

So the budget is **~10W at target and ~11.4W worst case**, not 8-9W. 8-9W corresponds to 87-88%
efficiency, which is above the stated target.

This matters because the heatsinking, case contact and vent design are sized from this number, and
a design built for 8-9W that must dissipate 11.4W at the efficiency floor will miss the ≤60°C case
target — which in turn breaks the capacitor-life chain below.

**Fix:** state the thermal design point as **11.4W (the efficiency floor), not the target**. Design
for the floor; the target then gives margin rather than consuming it.

### The capacitor life chain now closes — confirm the derived number

Worth recording, because v2's changes make it work for the first time. With the ≥5,000 h / 105°C
base endurance that Section 5 now requires:

    5,000 h × 2^((105 − 72)/10) = 5,000 × 9.85 ≈ 49,250 h ≈ 50,000 h

So the ≥50,000 h target in Section 5 is achievable at a **capacitor core temperature of ≤72°C** —
which is realistic inside a ≤60°C case, but *only* if C4 is fixed and the dissipation is actually
~10W rather than 15W. The whole chain (efficiency → dissipation → case temp → core temp → life →
warranty length) is now self-consistent.

**Action:** write **"capacitor core temperature ≤ 72°C at 5A, 40°C ambient"** into Section 6 as an
explicit measured acceptance criterion. It is currently implicit, and it is the single number that
the 50,000 h life and the proposed 2-3 year warranty both rest on.

### C5. The latching OVP threshold is not coordinated with load-dump overshoot

Section 5 specifies OVP as *"latching until AC is recycled"* at *"≤14.5V peak"*. Two problems.

**First, a latching OVP that nuisance-trips is a field failure requiring a site visit** — the exact
cost v2 correctly avoids by making OCP and SCP auto-recovery. The risk case is a **load dump**: a
sudden 5A → 0A step. With the slow loop of any flyback, the output overshoots. If that overshoot
reaches the OVP threshold, a legitimate event (a camera rebooting, a relay opening) latches the
supply off until someone drives to the site.

**Second, there is no stated margin between the two.** If load dump overshoots to 13.5V and OVP
sits at 14.5V, the margin is 1.0V and depends entirely on loop compensation that has not been
designed yet.

**Fix:** make the OVP threshold a *derived* requirement with a measurement behind it:

    OVP threshold ≥ (maximum measured load-dump overshoot + 0.75V),  and ≤ 14.5V

Measure the overshoot in TC7 (add a 100% → 0% load dump to it — TC7 currently tests 50→100→50% and
startup, but not a full dump). If those two bounds cannot both be met, the correct response is to
fix the loop compensation, **not** to raise the OVP threshold — raising it pushes toward the 16V
rating of downstream load capacitors.

Also: the latch-vs-auto-recovery split between OVP (latch) and OCP/SCP (auto) is a sound and
deliberate choice, but **record the rationale in Section 5**. It reads as an inconsistency, and an
ODM or reviewer will "helpfully" make them uniform unless the reasoning is written down.

### C6. Fuse, NTC and MOV are each specified; their coordination is not

v2 now gives each input-chain part a correct individual rating, and states the chain order. But the
actual engineering is the **interaction**, and nothing in v2 checks it:

- The MOV's surge current must flow **without opening the fuse**. If a survivable 2 kV surge blows
  the fuse, a protected event becomes a warranty return.
- The fuse must open **before the MOV fails thermally** under a sustained overvoltage (e.g. a lost
  neutral putting 400V on a 230V input).
- The NTC sits between them and its cold resistance (≥9.4Ω) changes both the surge let-through and
  the fuse's I²t exposure.

These three constraints are satisfiable, but only by checking fuse I²t against the MOV's surge
current waveform and the NTC's contribution — a calculation, not a parts list.

**Fix:**
- Add a design-review item: *coordination check of fuse I²t vs MOV surge current vs NTC cold
  resistance, for the declared surge level*, as part of the M2c gate.
- Add to TC11: **5 consecutive rated surge strikes**, with acceptance *"fuse intact, MOV within
  rating, unit still meets TC2"* — not merely "survives."
- **Strongly consider a thermally-protected MOV (TMOV)** with an integral thermal disconnect. The
  known MOV end-of-life failure mode is degradation to low impedance followed by ignition — which
  is precisely the fire risk the fuse is there to prevent, arriving by a path the fuse does not
  cover well. The cost delta is small, and on a product whose entire positioning is "protected,"
  it is a cheap and genuinely defensible differentiator. This belongs on the "do not cut cost on"
  list in Section 8.

### C7. The error budget has zero headroom and omits ripple

Section 3's budget sums to exactly **±5.0%** against a ±5% limit. Two issues:

**No headroom.** A worst-case linear sum that exactly equals the limit means any single contributor
overrunning by 0.1% fails the spec, with no room for production spread, measurement uncertainty, or
a component substitution. Budget to **±4.0%** and hold **1.0% in reserve**.

Also worth stating alongside it: the linear sum is the absolute bound, not the expectation. The
realistic combined figure for independent contributors is the root-sum-square:

    √(1² + 1² + 2² + 1²) = √7 ≈ 2.65%

Quote both — RSS as the expected production figure, linear sum as the guaranteed limit. Otherwise
the design gets over-built against a corner that essentially never occurs, or someone "discovers"
the 2.65% figure and quietly removes the margin.

**Ripple is not in the budget, and the measurement basis is unstated.** 150 mVpp is 1.25% of 12V.
If the ±5% applies to the **DC average**, ripple is correctly a separate line item. If it applies
to the **instantaneous** voltage — which is what a load actually sees — then:

    5.0% (static sum) + 0.625% (half of 150 mVpp) = 5.6%  → out of spec

**Fix:** state explicitly that *"the output window applies to the DC average measured 4-wire at the
output terminals; ripple and transient excursions are specified separately."* One sentence,
prevents a bench argument.

Suggested revised budget:

| Contributor | Allocation |
| --- | --- |
| Setpoint tolerance at 25°C, 230V, 2.5A | ±0.75% |
| Line regulation over the rated range | ±0.75% |
| Load regulation, 0-5A | ±1.5% |
| Temperature drift, 0-50°C | ±1.0% |
| **Worst-case sum** | **±4.0%** |
| *Expected (RSS)* | *±2.1%* |
| **Reserve to the ±5% limit** | **1.0%** |

### C8. The brownout acceptance criterion is circular

TC14 reads: *"Dropout / brownout ride-through — Acceptance: **defined output behaviour** at
specified dips."* Neither the behaviour nor the dips are defined anywhere in the document, so the
test cannot pass or fail.

This matters more than a typical editorial gap, because the whole input-range decision rests on
sag behaviour. The specific failure mode to design against is **hiccup chatter at the UVLO
boundary**: mains sagging to just below the brownout threshold makes the controller restart
repeatedly, which stresses the NTC (its self-heating is already flagged in Section 5) and can
cook it.

**Fix:** define it numerically.

- Output stays within the error budget down to **V_min** at full load.
- Below V_min, the unit shuts down **cleanly and once** — no repetitive restart — and auto-recovers
  above **V_min + hysteresis**, with the hysteresis stated (e.g. 10V).
- Test: slow ramp down and up through the threshold at full load, plus 10, 20 and 100 ms dips to
  0V at full load, with the output behaviour recorded for each.
- Acceptance: no hiccup chatter anywhere in the ramp; recovery within one stated turn-on time.

---

## 4. Remaining open numbers I can close now

### Y-capacitor: leakage is not your binding constraint, so pick on EMI grounds

Section 5 flags the Y-cap/leakage trade-off correctly but leaves it unresolved, which blocks the EMI
design. The arithmetic resolves it:

    I_leak = 2π f C V

| Y-cap | Leakage at 265V / 50Hz | Class I ITE limit (3.5 mA) |
| --- | --- | --- |
| 2.2 nF | 0.18 mA | 5% of limit |
| 4.7 nF | 0.39 mA | 11% of limit |
| 10 nF | 0.83 mA | 24% of limit |

Because this is a **Class I (earthed)** design, leakage is nowhere near binding. You can use
**4.7 nF comfortably**, which is good for common-mode EMI, and still sit at ~11% of the limit.

This inverts v2's framing: for an earthed design, **select the Y-cap for EMI performance and then
verify leakage**, rather than treating leakage as the constraint. (The constraint only bites on a
Class II unearthed design, where the limit drops to 0.25 mA — there, 2.2 nF is already at 72%.)
Still required: Y1 class, or two Y2 in series, across a reinforced barrier.

### Input range: recommend 120-265V, not 150-265V

v2 proposes 150-265V and leaves it as an owner decision. **150V is the wrong number, because it
leaves zero margin at exactly the voltage you expect to see.** v2's own rationale cites Indian sag
to "roughly 150-180V" — a rated minimum of 150V means the product is at its limit during the normal
condition it was designed for.

The cost of margin here is small:

| Rated V_min | Bulk capacitance needed | vs 150V |
| --- | --- | --- |
| 100V | ~82-100 µF | baseline v1 |
| 120V | **~68 µF** | +₹5-8 |
| 150V | ~47 µF | v2 proposal |

**Recommend 120-265V.** You keep nearly all the saving versus v1's 100V (68µF vs 82-100µF), you
gain 30V of genuine margin against the documented sag condition, and "120-265V" still reads as a
wide-input part on a label. Paying ₹5-8 to avoid operating at the edge of the rating during normal
mains behaviour is the right trade.

Note this interacts with C1: at 68µF/450V the surge ΔV is also smaller than at 47µF, so the larger
capacitor helps twice.

### Minimum load: make it an explicit Section 3 row

Section 6 defers minimum load to the datasheet, but TC2 tests at 0% load and Section 3 requires
≤150 mVpp ripple at 0% and ≤0.15W no-load. So the answer is already **0A**, implicitly.

Promote it to Section 3, because *"0A minimum load, with ≤0.15W no-load power and ≤150 mVpp ripple
at 0A"* is a demanding combination — burst-mode operation produces low-frequency ripple precisely
at no load — and the designer needs to know it is a hard requirement before choosing the
controller, not after.

### Ripple and transient must also be tested at V_min

TC2 and TC7 test ripple and transient response, but the line condition is not stated, so it will
default to 230V. Both are **worst at low line**, where bulk-rail sag is greatest and loop gain is
lowest. Add: *"repeat ripple and load-transient measurements at V_min, full load"* to TC2 and TC7.

---

## 5. Answers to v2's open questions

**Q1 — Confirm 150-265V, or keep 100-265V?**
Neither. **120-265V**, per Section 4 above. It keeps the cost and stress reduction while removing
the zero-margin condition at the sag voltage you actually expect.

**Q2 — Is ₹450-600 MRP or ex-GST?**
Owner decision, but assume **MRP (GST-inclusive)** until proven otherwise, because that is the
Indian retail convention and it is the conservative case. At 18%, a ₹500 MRP is ₹424 ex-GST — so
build the unit-economics sheet on ₹424 and treat any ex-GST upside as a bonus. Building on ₹500 and
discovering it was inclusive removes ~15% of revenue at the worst possible moment.

**Q3 — Which single primary declared application?**
**Declare ITE / general-purpose SMPS**, and market LED-strip use as an application note rather than
a product class. Reasons: (a) it keeps the harmonics threshold at 75W rather than the 25W lighting
limit, which avoids active PFC and the BOM increase that comes with it; (b) CCTV and IoT are the
higher-margin, more reliability-sensitive channels where your differentiator is worth paying for;
(c) LED-strip buyers are the most price-sensitive segment and least likely to pay ₹450-600 over
₹250. Still confirm the CRS category in writing, per v2's existing M4 item.

**Q4 — In-house assembly or contract manufacturer?**
Follow v2's own Section 8 logic: **route A or C with a contract manufacturer first.** Certification
economics (₹80-200/unit at 500 units) make in-house assembly unviable until the payback volume is
cleared. Revisit after M5.

**Q5 — Target monthly and lifetime volume?**
This is the one answer only you can give, and it is the most important number in the document.
The threshold to work toward: certification amortizes below ~₹20/unit at roughly **3,000-5,000
lifetime units**. If the realistic lifetime volume is under ~1,500 units, route B (own design +
own registration) does not close, and route A or C is not a preference but the only option. Put
this number in the M4 gate.

---

## 6. Consolidated v2 → v3 changes

| Section | v2 | Change to |
| --- | --- | --- |
| 3 | EC1 at **400V** | **450V** (v2's own 1.2× derating rule on a 375V peak) |
| 3 | Input 150-265V (proposed) | **120-265V**; bulk C ~68 µF |
| 3 | Static ±5% sum; transient ≤±5% | Static **±4.0%** (1.0% reserve); transient **±7% peak**, back inside ±4% in 2 ms; **±10% never-exceed** |
| 3 | Budget basis unstated | State: window applies to **DC average**, 4-wire at terminals; ripple and transient specified separately. Quote RSS (±2.1%) alongside the linear sum |
| 3 | Minimum load deferred to datasheet | Explicit row: **0A minimum load** |
| 5 | OVP ≤14.5V, latching | **≥ (measured load-dump overshoot + 0.75V) and ≤14.5V**; record the latch-vs-auto rationale |
| 5 | Fuse/NTC/MOV rated individually | Add **coordination check** (fuse I²t vs MOV surge current vs NTC cold R) to the M2c gate |
| 5 | MOV 300-320V class | Keep. Add **TMOV with thermal disconnect**, and add it to "do not cut cost on" |
| 5 | Y-cap "size from touch-current limit" | **4.7 nF Y1** (0.39 mA, 11% of the 3.5 mA Class I limit); select for EMI, verify leakage |
| 6 | Dissipation "about 8-9W" | **~10W at target, 11.4W at the floor** — design to 11.4W |
| 6 | Core temperature implicit | Explicit acceptance: **capacitor core ≤72°C at 5A / 40°C ambient** (this is what 50,000 h rests on) |
| 7 | — | No change; open items are correctly scoped |
| 9 | TC7 tests 50→100→50% | Add **100% → 0% load dump**; add **ripple and transient at V_min** to TC2/TC7 |
| 9 | TC8 at 110% / 45-50°C | Label as a deliberate **overstress screen outside the rated envelope**, or move to 100% / 50°C. Define the derating curve first |
| 9 | TC11 "survives" surge | **5 consecutive rated strikes**: fuse intact, MOV in rating, TC2 still passes; scope the bulk rail during the strike |
| 9 | TC14 "defined output behaviour" | Numeric: in-regulation to V_min; clean single shutdown below; auto-recover above V_min + stated hysteresis; **no hiccup chatter**; 10/20/100 ms dip tests |

---

## 7. What v2 got right

- **The change log.** Separating accepted / modified / not-taken with reasons is the right way to
  run a review cycle, and it is what let the MOV error be caught.
- **Pushing back where the pushback was correct.** The MOV class was wrong in round 1 and v2 said
  so with a reason. The OVP-runaway qualification was also fair.
- **Not over-accepting.** Marking the BIS fees, touch limits, surge levels and sag figures as
  unverified estimates — rather than adopting them as fact — is the correct handling, and the
  design does not depend on which way they resolve.
- **The architecture inversion** (QR + opto for v1, PSR as phase-2 cost-down) with the reasoning
  recorded, and PSR kept in the cost-lever table rather than discarded.
- **The gate additions** — M2b spec freeze, M2c pre-fab safety review, M3's waiver requirement
  replacing the "or deviations documented" loophole, long-lead procurement as a schedule floor.
- **Unblocking M1** by buying teardown units instead of waiting on a third party's photo, with
  unit-to-unit variance as an added acceptance criterion.
- **The whole thermal → life → warranty chain** now closes numerically for the first time, and the
  2-3 year warranty is correctly made conditional on measured life data rather than asserted.
- **Keeping the 4 output terminals** and reclassifying them as a feature in the "do not cut" list.
- **Certificate portability** as a named risk with a mitigation, which is the strategic point route
  A/C turns on.
