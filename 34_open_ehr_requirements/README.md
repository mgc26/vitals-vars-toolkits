# Open EHR Requirements Matrix

This toolkit defines the bar that Part 2 of the Open EHR Experiment will use to assess an assembled open-source stack. It is a preregistered evaluation framework, not a feature inventory and not a promise that the stack is production-ready.

The reference buyer is a hypothetical regional integrated delivery network with two to four hospitals, a few dozen ambulatory sites, and an employed medical group. The matrix tests four pillars:

- `idn_scale`: enterprise identity, multi-site workflows, interfaces, scheduling, provenance, resilience, and reconciliation
- `security`: access control, auditability, integrity, encryption, recovery, and security operations
- `clinical`: end-to-end care workflows, including adverse and interrupted paths
- `revenue_cycle`: eligibility, charge capture, coding, claims, remittance, denials, and patient balances

The matrix is deliberately narrower than every capability an IDN might operate. Transplant, research and clinical-trial management, home health, and other specialty settings are outside this reference scope unless a reader adds them.

## Files

- `requirements_matrix.csv`: 62 individually testable requirements and their Part 2 test procedures
- `vertical_journeys.md`: 12 end-to-end workflows that connect requirements across pillars

`evidence_level`, `result`, and `limitation` are blank by design. Part 2 fills them after testing. `authority_status=verified` means the citation was checked against a live source in July 2026 (regulation text, the current ONC test method, or primary regulatory pages) or the authority is a self-labeled procurement norm making no external legal claim. Proposed rules (the January 2025 HIPAA Security NPRM, the HTI-5 deregulatory proposal) are labeled proposed wherever they appear; no proposed provision is treated as a current requirement.

## Evidence ladder

Score only the highest level supported by retained evidence. Do not award a level because a component is expected to work.

| Level | Points | What qualifies |
|---|---:|---|
| `claimed` | 1 | A project, vendor, or maintainer states that the capability exists. No working configuration or completed test is shown. |
| `configured` | 2 | The capability is installed and its relevant configuration can be inspected, but the matrix procedure has not completed successfully end to end. |
| `demonstrated` | 3 | The procedure completes in the assembled stack with synthetic data, and reproducible artifacts show the inputs, outputs, configuration, and observed behavior. |
| `load-tested` | 4 | The demonstrated capability also completes under a declared workload or failure profile, with published throughput, latency, error, loss, duplication, and recovery observations as applicable. |
| `independently validated` | 5 | A reviewer who did not build the tested path reproduces the result or validates the retained evidence against the same procedure and acceptance conditions. |

A claim and a demonstration never receive the same rating or color. Suggested display colors should therefore be discrete, not a smooth gradient that makes adjacent levels look equivalent. Blank means unassessed and scores zero.

## Scoring rules

Use these defaults unless the evaluating organization preregisters stricter rules:

1. Record `result` as `pass`, `partial`, `fail`, or `not_tested`. A row passes only when its stated procedure and locally declared acceptance conditions are met. Record unresolved defects or test constraints in `limitation`.
2. Assign evidence points from 0 to 5 using the ladder above. A successful functional walkthrough is `demonstrated`, not `load-tested`. A row whose procedure explicitly tests workload must complete that workload test to receive `pass`.
3. Weight tiers as `must=3`, `should=2`, and `nice=1`. For descriptive comparison, calculate weighted evidence as `sum(tier weight × evidence points) / sum(tier weight × 5)`. Publish the evidence-level distribution beside the percentage so the average cannot hide a pile of claims.
4. Every `must` row must reach at least `demonstrated` and receive `pass` under the toolkit default. `should` and `nice` gaps remain visible as roadmap items and lower the descriptive score.
5. Hard gates are noncompensable. Every `hard_gate=yes` row must receive `pass` at the evidence level required by its procedure. One failed, partial, or untested hard gate fails the matrix regardless of the weighted average.
6. Hard gates may be used only for patient identity, medication safety, auditability, data durability, access control, downtime recovery, or claim integrity. Each hard-gate procedure begins with `Hard-gate domain=<domain>.` so this constraint can be checked mechanically.
7. Retain evidence for every rating: stack version, configuration snapshot, synthetic fixture, execution time, raw output, expected output, observed output, and reviewer. If that packet is missing, lower the evidence level.

The weighted score ranks gaps; it does not erase them. In particular, strong scheduling or billing results cannot compensate for a failed identity merge, unsafe medication behavior, missing audit events, lost data, improper access, failed downtime recovery, or a corrupted claim.

## What a pass does not mean

Passing this matrix is **not ONC certification**. ONC certification has its own applicable criteria and editions, official test procedures, testing and certification through ONC-Authorized Certification Bodies (ONC-ACBs), and ongoing obligations. A locally assembled stack does not become certified because it passes this matrix, implements a standard, exposes FHIR endpoints, or completes a synthetic demonstration.

The matrix also does not establish HIPAA compliance, clinical validation, production operability, or institutional adoption. Those depend on organizational controls, real operating conditions, governance, support, migration, legal accountability, and other work beyond a Part 2 technical assembly.

## Adapt it for a vendor evaluation

1. **Declare the buyer and scope.** Replace the reference IDN with your hospitals, sites, employed and affiliated groups, care settings, interfaces, transaction volumes, recovery objectives, and explicit exclusions.
2. **Reconcile authorities.** Have regulatory, privacy, security, clinical, and revenue-cycle owners verify the current authority text. Change `authority_status` to `verified` only when the cited source and applicability have been checked.
3. **Change the bar before seeing products.** Add specialty requirements, remove genuinely irrelevant rows, choose tier weights, identify hard gates only from the seven allowed domains, and approve acceptance thresholds before vendor responses or demos.
4. **Make procedures local and measurable.** Replace generic fixtures with de-identified or synthetic representations of your patient identities, roles, sites, workflows, payer rules, message mix, concurrency, recovery objectives, and expected outputs. Do not put production PHI in an evaluation environment.
5. **Require an evidence packet.** Ask each vendor to map its response to the row ID and submit architecture references, configuration, test artifacts, limitations, dependencies, and the exact product version. Vendor prose alone remains `claimed`.
6. **Run adverse paths.** Evaluate the happy path and the failure path. Use the vertical journeys to test duplicate identities, interrupted work, corrections, access failures, downtime, denials, and recovery across component boundaries.
7. **Score independently.** Evaluators, not vendors, assign `evidence_level`, `result`, and `limitation`. Record mocked external dependencies as simulations. Re-run high-risk rows after upgrades or material configuration changes.

Do not collapse the output to one procurement number. Report hard-gate disposition, must-row coverage, evidence distribution, pillar scores, known limitations, and the components or external services on which each result depends.
