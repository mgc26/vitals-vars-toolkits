# SIMULATED PAYER: the complete deterministic rule table

This is the entire adjudication logic of the simulated payer used in Part 2 scoring.
It is published so nobody mistakes it for real payer behavior.

# SIMULATED PAYER

> **SIMULATED. NOT REAL PAYER POLICY.** These deterministic rules exist only for Issue 35 test fixtures. Do not use them for coverage, coding, billing, or clinical decisions.

A Python 3.12 FastAPI service that returns deterministic X12 271, 999, 277CA-style, and 835 artifacts. The compose service name is `payer-sim`; it listens on port `8090`.

## Endpoints

- `POST /eligibility` with `{"x12": "<270>"}` returns `{"x12": "<271>"}`.
- `POST /claims` with `{"x12": "<837P-or-837I>"}` returns `{"ack999": "...", "status277": "..."}`.
- `GET /remit/{claim_control_number}` returns `{"x12": "<835>"}` after an accepted submission.
- `GET /health` returns service and validator status.

Every response carries `X-Simulated-Payer: true`. Request bodies larger than 1 MiB are rejected with HTTP 413. Accepted claim artifacts are idempotent by `CLM01` claim control number for the lifetime of the process.

## Run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
PAYER_REQUIRE_PYX12=true uvicorn app.main:app --host 0.0.0.0 --port 8090
pytest
```

The Docker image sets `PAYER_REQUIRE_PYX12=true`, so it will not start without pyx12. A structural fallback exists only so development tests can run in an offline environment where pyx12 cannot be installed; `/health` identifies the active validator.

Regenerate this file after changing `app/rules.yaml`:

```bash
python -m app.rule_docs
```

## Coverage rules

| Member ID | Status | Effective | Termination | Plan | Deductible | Remaining |
|---|---|---|---|---|---:|---:|
| `FIX-P-007` | active | 2026-01-01 | 2026-12-31 | `SIM-GOLD-2026` | $500.00 | $250.00 |
| `FIX-P-007` | active | 2027-01-01 | 2027-12-31 | `SIM-GOLD-2027` | $750.00 | $625.00 |
| `FIX-P-007-INACTIVE` | inactive | 2025-01-01 | 2025-12-31 | `SIM-TERM-2025` | $500.00 | $0.00 |

## Procedure adjudication rules

| Procedure | Outcome | Adjustment | Description |
|---|---|---|---|
| `99214` | clean_pay | n/a | Covered professional service; pay the full submitted charge. |
| `99223` | clean_pay | n/a | Covered institutional service; pay the full submitted charge. |
| `99215` | deny | `CO-50` | Simulated non-covered service denial (CO-50). |
| `99358` | deny | `CO-97` | Simulated bundled-service denial (CO-97). |
| `81001` | partial_pay | `PR-1` | Pay 70%; assign 30% to simulated deductible (PR-1). |
| `81002` | deny | `PR-1` | Deny payer payment; assign the full simulated deductible to PR-1. |

## Fixture-specific scenarios

| Claim control number | Outcome | Conditions | Description |
|---|---|---|---|
| `FIX-CLM-001` | clean_pay | none | Clean 837P payment fixture. |
| `FIX-CLM-006` | clean_pay | none | Clean 837I payment fixture. |
| `FIX-CLM-007` | deny | procedure=`99215` | Original claim denied with CO-50. |
| `FIX-CLM-009` | clean_pay | procedure=`99214`; frequency=`7`; original=`FIX-CLM-007` | Corrected replacement of FIX-CLM-007; pay after correction. |
| `FIX-CLM-008` | partial_pay | procedure=`81001` | Partial payment with PR-1 deductible responsibility. |
| `FIX-CLM-008-REV` | reversal | procedure=`81001`; frequency=`8`; original=`FIX-CLM-008` | Counter-transaction reversing FIX-CLM-008 without deleting it. |

A fixture-specific rule takes precedence over a procedure rule. If a required correction/reversal condition does not match, the simulator deterministically returns CO-97. Unknown procedure codes default to clean payment; this is simulation behavior, not a coverage assertion.
