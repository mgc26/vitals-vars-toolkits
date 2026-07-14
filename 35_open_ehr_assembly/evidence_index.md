# Evidence Index — Issue 35 scored run (strict, post-audit)

Every in-scope row has a tamper-evident packet (sha256 over body incl. per-artifact hashes + acceptance-coverage map, commit-pinned) under `runs/evidence/<ID>/` in the private build repo. Out-of-scope rows have NO packet and score blank (0 points) under the strict rule; they carry their preregistered result for disposition only.

| Row | Result | Evidence | In scope | Simulated deps |
|---|---|---|---|---|
| IDN-001 | pass | demonstrated | true | - |
| IDN-002 | pass | demonstrated | true | - |
| IDN-003 | partial | configured | true | - |
| IDN-004 | pass | demonstrated | true | simulated-adt-sender |
| IDN-005 | not_tested | configured | true | simulated-adt-sender |
| IDN-006 | pass | demonstrated | true | - |
| IDN-007 | not_tested | configured | true | - |
| IDN-008 | partial | configured | true | - |
| IDN-009 | pass | demonstrated | true | - |
| IDN-010 | not_tested | configured | true | simulated-adt-sender;simulated-payer |
| IDN-011 | not_tested | blank (0) | false | - |
| IDN-012 | fail | blank (0) | false | - |
| IDN-013 | fail | blank (0) | false | - |
| IDN-014 | not_tested | configured | true | - |
| IDN-015 | not_tested | blank (0) | false | - |
| SEC-001 | fail | blank (0) | false | - |
| SEC-002 | pass | demonstrated | true | - |
| SEC-003 | fail | blank (0) | false | - |
| SEC-004 | pass | demonstrated | true | - |
| SEC-005 | pass | demonstrated | true | - |
| SEC-006 | pass | demonstrated | true | - |
| SEC-007 | not_tested | configured | true | simulated-adt-sender |
| SEC-008 | not_tested | configured | true | - |
| SEC-009 | not_tested | configured | true | - |
| SEC-010 | not_tested | blank (0) | false | - |
| SEC-011 | fail | blank (0) | false | - |
| SEC-012 | not_tested | blank (0) | false | - |
| SEC-013 | not_tested | blank (0) | false | - |
| SEC-014 | not_tested | blank (0) | false | - |
| SEC-015 | fail | blank (0) | false | - |
| CLN-001 | pass | demonstrated | true | - |
| CLN-002 | not_tested | blank (0) | false | - |
| CLN-003 | pass | demonstrated | true | - |
| CLN-004 | not_tested | blank (0) | false | - |
| CLN-005 | pass | demonstrated | true | - |
| CLN-006 | pass | demonstrated | true | - |
| CLN-007 | pass | demonstrated | true | - |
| CLN-008 | fail | blank (0) | false | - |
| CLN-009 | fail | blank (0) | false | - |
| CLN-010 | not_tested | blank (0) | false | - |
| CLN-011 | not_tested | blank (0) | false | - |
| CLN-012 | not_tested | blank (0) | false | - |
| CLN-013 | not_tested | blank (0) | false | - |
| CLN-014 | not_tested | blank (0) | false | - |
| CLN-015 | not_tested | blank (0) | false | - |
| RCM-001 | pass | demonstrated | true | simulated-payer;simulated-eligibility |
| RCM-002 | pass | demonstrated | true | simulated-payer;simulated-eligibility |
| RCM-003 | pass | demonstrated | true | - |
| RCM-004 | partial | configured | true | - |
| RCM-005 | pass | demonstrated | true | simulated-payer |
| RCM-006 | pass | demonstrated | true | simulated-payer |
| RCM-007 | pass | demonstrated | true | simulated-payer |
| RCM-008 | pass | demonstrated | true | simulated-payer;simulated-remittance |
| RCM-009 | not_tested | configured | true | simulated-payer;simulated-remittance |
| RCM-010 | pass | demonstrated | true | simulated-payer |
| RCM-011 | pass | demonstrated | true | simulated-payer;simulated-remittance |
| RCM-012 | not_tested | configured | true | simulated-payer;simulated-remittance |
| RCM-013 | not_tested | blank (0) | false | - |
| RCM-014 | pass | demonstrated | true | simulated-payer;simulated-remittance |
| RCM-015 | fail | blank (0) | false | - |
| IDN-016 | pass | demonstrated | true | - |
| CLN-016 | pass | demonstrated | true | simulated-transmit-endpoint |
