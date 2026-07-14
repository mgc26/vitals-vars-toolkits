# Issue 34 Vertical Journeys

These 12 journeys define the end-to-end workflows Part 2 will run against the assembled open-source stack. They use synthetic patients and clearly labeled test adapters for external laboratories, pharmacies, payers, and messaging networks. Passing a component test does not pass a journey; the state and identifiers must remain coherent across every boundary.

For each run, retain the synthetic fixture, component versions, configuration snapshot, event timeline, raw messages, expected state, observed state, screenshots where useful, and known limitations.

## 1. Enterprise registration, duplicate patient, merge, and unmerge

**Matrix coverage:** IDN-001, IDN-002, IDN-003, IDN-009, SEC-005

**Happy path:** Register a new synthetic patient at Clinic A, then register the same person at Hospital B using the same demographics. The identity service returns one enterprise patient, preserves both local identifiers, displays both encounters in the longitudinal record, and logs the match decisions.

**Adverse path:** Register the same person again with a transposed birth date and an old address so a duplicate patient is created. An authorized identity steward reviews the candidates, merges the duplicate into the surviving record, verifies that allergies, notes, orders, results, and provenance remain intact, and then reverses the merge. The system must restore two coherent source records without losing or silently reassigning data. An unauthorized user must be unable to merge or unmerge them.

**Pass evidence:** Before-and-after record manifests, identifier crosswalk, match and merge audit events, and checksums showing that merge plus unmerge neither loses nor duplicates clinical data.

## 2. Enterprise appointment through ambulatory referral closure

**Matrix coverage:** IDN-006, IDN-008, IDN-009, IDN-014, CLN-001

**Happy path:** Schedule a synthetic patient at Clinic A with a provider, room, and equipment resource; check in, complete the encounter, create a specialty referral to Clinic B, schedule the referral, complete the specialty visit, and return the consult note to the referring clinician. Both sites see the same referral state and appropriate local schedule details.

**Adverse path:** Reschedule the specialty appointment across sites while one required resource is unavailable, then cancel it after an interface retry. The stack must reject the conflicting reservation, release the original resources exactly once, prevent a duplicate appointment, and retain the status history. A Clinic A scheduler must not gain permission to alter Clinic B configuration.

**Pass evidence:** Resource-calendar snapshots, referral and appointment histories, retry messages, cross-site permissions, and closure notification.

## 3. Emergency encounter and cross-site transfer

**Matrix coverage:** IDN-004, IDN-005, IDN-007, IDN-009, CLN-015

**Happy path:** Admit a synthetic patient to the Hospital A emergency department, document allergies and home medications, place laboratory and imaging orders, receive one result, and transfer the patient to an inpatient unit at Hospital B. The receiving clinician sees the active encounter context, completed result, pending orders, medication and allergy lists, sending location, receiving location, and transfer timeline.

**Adverse path:** Deliver the transfer event before a pending result and replay the transfer message. The stack must create one receiving encounter, route the late result to the correct patient and order, distinguish completed from pending work, and surface rather than discard any event it cannot correlate. A result carrying a mismatched patient identifier must be quarantined and not displayed in either chart.

**Pass evidence:** Sending and receiving manifests, ADT acknowledgements, encounter and location history, late-result correlation, quarantine record, and duplicate-event counts.

## 4. Medication order, allergy conflict, and administration

**Matrix coverage:** CLN-005, CLN-006, CLN-007, SEC-005, SEC-006

**Happy path:** Record a coded allergy, enter a complete medication order that does not conflict, sign it, verify it at administration, and document the administered dose. The active order and administration record retain patient, drug, dose, unit, route, frequency, time, prescriber, and administering user.

**Adverse path:** Order a medication that conflicts with the recorded allergy. The stack interrupts signing and requires the clinician either to choose a nonconflicting medication or enter an authorized override reason. Then attempt administration for the wrong synthetic patient and against a discontinued order; both known mismatches must be blocked or handled through the preregistered safety control, with full audit evidence.

**Pass evidence:** Order payloads, alert inputs and rule version, override authorization and reason, administration checks, blocked attempts, and audit events.

## 5. Interrupted diagnostic order and exactly-once recovery

**Matrix coverage:** IDN-007, IDN-010, CLN-004, CLN-009

**Happy path:** Place and sign a laboratory order, transmit it to the test laboratory, receive an acknowledgement, collect the specimen, and return a final result to the ordering encounter. All systems retain the same patient, encounter, order, and specimen identifiers.

**Adverse path:** Interrupt the client connection after signing but before confirmation, then interrupt the interface broker during retry. The user retries once. Recovery must leave exactly one signed order and one laboratory work item, or no active order if the transaction never committed. It must not leave a partial unsigned order, generate a duplicate specimen, or attach a result to the wrong order. Replaying the result must also remain idempotent.

**Pass evidence:** Failure-injection timestamps, transaction and message identifiers, order-state history, broker retry log, object counts, and final chart and laboratory states.

## 6. Result correction, critical notification, and acknowledgement

**Matrix coverage:** CLN-004, CLN-010, CLN-011, SEC-005

**Happy path:** Return a routine preliminary laboratory result, replace it with a final result, route it to the ordering clinician, and record acknowledgement. The chart distinguishes preliminary and final values and retains both versions and their sources.

**Adverse path:** Return a configured critical value after hours and leave the first recipient unresponsive. The declared escalation path must continue until an authorized clinician acknowledges the result. Then issue a corrected result; the correction must not erase the prior value, must reach the responsible clinician, and must not create a second unrelated order.

**Pass evidence:** Result versions, routing and escalation events, notification attempts, acknowledgement identity and time, correction linkage, and chart display.

## 7. Signed note and amended note

**Matrix coverage:** CLN-003, SEC-005, SEC-006, SEC-007

**Happy path:** Draft, sign, and release a clinical note for a synthetic encounter. Later, the original author adds an amended note with a reason. Readers can see the signed original, amendment, authors, signer, reason, and version times in sequence.

**Adverse path:** Attempt to edit the signed text directly and attempt an amendment with a user who lacks the required role. Both actions must fail without changing the original. A controlled privileged alteration test must trigger the configured integrity or tamper evidence rather than silently rewriting history.

**Pass evidence:** Original and amended note checksums, version chain, authorization outcomes, before-and-after display, and immutable audit events.

## 8. Downtime plus recovery with queued work

**Matrix coverage:** IDN-010, IDN-012, IDN-013, SEC-011, SEC-015

**Happy path:** Declare a controlled clinical API outage, follow the configured downtime workflow, restore the service, process queued ADT and result messages, and reconcile all records to the predeclared manifest. Users can identify the downtime interval and the stack returns to normal processing without manual database repair.

**Adverse path:** During an unplanned outage, interrupt the interface receiver after it accepts some messages and before it acknowledges them. Include duplicate, out-of-order, and malformed payloads in the backlog. After recovery, the stack must preserve committed records, reject or quarantine malformed work, process each valid event exactly once, restore audit search, and expose any unmet recovery objective rather than concealing it.

**Pass evidence:** Downtime declaration, recovery timeline, backup or failover evidence, queue snapshots, pre- and post-recovery manifests, checksums, duplicate and loss reconciliation, and recorded recovery-point and recovery-time observations.

## 9. Admission-to-discharge medication reconciliation

**Matrix coverage:** CLN-002, CLN-005, CLN-008, IDN-005

**Happy path:** Import a synthetic home medication list at admission, compare it with ambulatory and inpatient lists, document continue, change, substitute, and stop decisions, transfer the patient to another site, and produce a reconciled discharge list. Each item retains its source and clinical decision.

**Adverse path:** Supply duplicate brand and generic entries, conflicting doses, an unknown unit, and a medication already marked stopped at another site. The stack must not silently activate all entries. It must require explicit disposition of conflicts, reject the malformed dose from activation, and show unresolved items to the receiving and discharging clinicians.

**Pass evidence:** Imported source lists, reconciliation decisions at each transition, resulting active orders, rejected and unresolved items, discharge list, and provenance.

## 10. Eligibility through clean claim and remittance

**Matrix coverage:** RCM-001, RCM-002, RCM-003, RCM-004, RCM-005, RCM-006, RCM-007, RCM-008

**Happy path:** Register coverage, send a synthetic eligibility inquiry, ingest an active response, complete an ambulatory encounter, post linked charges, review and finalize codes, generate a professional claim, ingest acceptance acknowledgements, and post a full-payment remittance. Patient, coverage, provider, service lines, claim totals, and payment all reconcile to their source records.

**Adverse path:** Return inactive coverage and then build a claim fixture with one missing provider identifier and inconsistent line totals. The stack must preserve the eligibility response, prevent the defective claim from transmission, identify actionable errors, accept corrections with an audit trail, and avoid creating duplicate charges or claim versions during retry.

**Pass evidence:** Eligibility and claim test payloads, source-to-claim reconciliation, edit results, acknowledgement correlation, remittance posting, ledger totals, and version history.

## 11. Denied claim plus corrected resubmission

**Matrix coverage:** RCM-007, RCM-008, RCM-010, RCM-011, RCM-014

**Happy path:** Submit a clean synthetic institutional claim, receive an acceptance acknowledgement, post its remittance, and close the account with an attributable financial event history.

**Adverse path:** Submit a second claim that the test payer denies for a correctable demographic defect. The denial creates an assigned work item with its reason and due date. A biller corrects the source field, creates a replacement claim linked to the original, resubmits it, receives payment, and closes the denial. An out-of-order acknowledgement and a duplicate remittance must not overwrite claim history or post payment twice.

**Pass evidence:** Original claim, denial, work item, source correction, replacement claim reference, acknowledgements, remittance, payment ledger, duplicate control, and user-attributed audit trail.

## 12. Partial payment, reversal, and patient statement

**Matrix coverage:** RCM-008, RCM-009, RCM-012, RCM-013, RCM-014, RCM-015

**Happy path:** Post a synthetic remittance containing payer payment, contractual adjustment, deductible, and coinsurance; accept a patient payment; and generate a statement. Every statement subtotal and remaining balance reconciles to the account ledger and the original remittance reason codes remain traceable.

**Adverse path:** Reverse the patient payment, post a payer recoupment, and replay the original remittance. Only authorized roles may create reversal entries, the original events must remain visible, the replay must not double-post money, and the regenerated statement must show the corrected balance without deleting prior statement history.

**Pass evidence:** Raw remittance fixtures, posting and reversal entries, role checks, account ledger before and after, original and regenerated statements, monetary reconciliation, and audit events.

## Coverage check

The required adverse scenarios are explicit in the following journeys:

- Duplicate patient plus merge: Journey 1
- Cross-site transfer: Journey 3
- Allergy conflict: Journey 4
- Interrupted order: Journey 5
- Amended note: Journey 7
- Downtime plus recovery: Journey 8
- Denied claim plus resubmission: Journey 11
