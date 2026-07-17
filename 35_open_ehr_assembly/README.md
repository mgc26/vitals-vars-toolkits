# The Assembly: Scored Results Toolkit (Issue 35)

Part 2 of the Open EHR Experiment. Part 1's 62-requirement matrix
(github.com/mgc26/vitals-vars-toolkits/tree/main/34_open_ehr_requirements), now SCORED
against an assembled open-source stack (Medplum CDR + domain bots + slice UI + Open
Integration Engine + a deterministic SIMULATED payer + Synthea patients).

Interactive scoreboard: https://vv-issue35-assembly.vercel.app
Live synthetic-data demo of the assembled slice (same 34.5% build, read-mostly, not for
clinical use; four features are labeled CONCEPT and are not scored): https://vv-issue35-ehr.vercel.app
Part 3, the cost and plausibility calculator: https://vv-issue36-bill.vercel.app

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
testing), the matrix cannot be passed. The first scored pass said 47.8%; an
adversarial audit of the method caught it crediting the 24 never-tested rows, the
rules were tightened (no packet = no points; per-condition acceptance coverage
enforced; several real code defects fixed), and the full re-collection landed the
honest number: weighted 34.5% (302/875) against a 35.4% attainable maximum at this
evidence scope (60.0% theoretical ceiling). The hard-gate disposition was identical
in both runs: 16 of 25 hard gates passed; the other 9 were preregistered as unproven at this scope
(no test ran; per rule 5 an unproven hard gate fails the evaluation), with zero
unexpected failures. The three partial scores are genuine gaps in the open-source ecosystem:
no demographic-correction engine, no referral state machine, no coding/CDI engine.

## What a pass does not mean
Passing rows here is NOT ONC certification, HIPAA compliance, clinical validation, or
production readiness. The payer is simulated; mocked claims are not "revenue cycle
automation." See KNOWN_LIMITATIONS in the issue folder.
