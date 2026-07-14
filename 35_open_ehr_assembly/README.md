# The Assembly: Scored Results Toolkit (Issue 35)

Part 2 of the Open EHR Experiment. Part 1's 62-requirement matrix
(github.com/mgc26/vitals-vars-toolkits/tree/main/34_open_ehr_requirements), now SCORED
against an assembled open-source stack (Medplum CDR + domain bots + slice UI + Open
Integration Engine + a deterministic SIMULATED payer + Synthea patients).

Interactive scoreboard: https://vv-issue35-assembly.vercel.app

## Files
- `scored_matrix.csv`: all 62 rows with result, evidence level, limitation (simulated
  dependencies stated per row), in_scope flag
- `evidence_index.md`: row-by-row index of the evidence packets
- `openemr_crosswalk.csv`: the OpenEMR documentation crosswalk (claimed-only, never
  tested, no weighted score; it is not a benchmark)
- `docker-compose.yml` + `env.example`: the pinned evidence-environment stack (Medplum
  server/app, Postgres, Redis)
- `payer_rules.md`: the simulated payer's complete deterministic rule table (published
  so nobody mistakes it for real payer behavior)

## The result, in one paragraph
Preregistered before the build: with evidence capped at "demonstrated" (no load
testing), the matrix cannot be passed. The scored run landed weighted 47.8% against a
60.0% ceiling; 16 of 25 hard gates passed and all 9 failures were the preregistered
ones (zero unexpected hard-gate failures). A full re-collection reproduced the result
exactly. The three partial scores are genuine gaps in the open-source ecosystem: no
demographic-correction engine, no referral state machine, no coding/CDI engine.

## What a pass does not mean
Passing rows here is NOT ONC certification, HIPAA compliance, clinical validation, or
production readiness. The payer is simulated; mocked claims are not "revenue cycle
automation." See KNOWN_LIMITATIONS in the issue folder.
