# Evidence Index — Issue 35 scored run

Every in-scope row has a tamper-evident packet (sha256, commit-pinned) under `runs/evidence/<ID>/` in the private build repo; the scored CSV in this toolkit is the published summary. Out-of-scope rows carry their preregistered result from the frozen manifest.

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
| IDN-011 | not_tested | configured | false | - |
| IDN-012 | fail | configured | false | - |
| IDN-013 | fail | configured | false | - |
| IDN-014 | not_tested | configured | true | - |
| IDN-015 | not_tested | configured | false | - |
| SEC-001 | fail | configured | false | - |
| SEC-002 | pass | demonstrated | true | - |
| SEC-003 | fail | claimed | false | - |
| SEC-004 | pass | demonstrated | true | - |
| SEC-005 | pass | demonstrated | true | - |
| SEC-006 | pass | demonstrated | true | - |
| SEC-007 | not_tested | configured | true | simulated-adt-sender |
| SEC-008 | not_tested | claimed | true | - |
| SEC-009 | not_tested | configured | true | - |
| SEC-010 | not_tested | configured | false | - |
| SEC-011 | fail | configured | false | - |
| SEC-012 | not_tested | claimed | false | - |
| SEC-013 | not_tested | configured | false | - |
| SEC-014 | not_tested | configured | false | - |
| SEC-015 | fail | configured | false | - |
| CLN-001 | pass | demonstrated | true | - |
| CLN-002 | not_tested | configured | false | - |
| CLN-003 | pass | demonstrated | true | - |
| CLN-004 | not_tested | configured | false | - |
| CLN-005 | pass | demonstrated | true | - |
| CLN-006 | pass | demonstrated | true | - |
| CLN-007 | pass | demonstrated | true | - |
| CLN-008 | fail | configured | false | - |
| CLN-009 | fail | configured | false | - |
| CLN-010 | not_tested | configured | false | - |
| CLN-011 | not_tested | configured | false | - |
| CLN-012 | not_tested | configured | false | - |
| CLN-013 | not_tested | configured | false | - |
| CLN-014 | not_tested | claimed | false | - |
| CLN-015 | not_tested | configured | false | - |
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
| RCM-013 | not_tested | configured | false | - |
| RCM-014 | pass | demonstrated | true | simulated-payer;simulated-remittance |
| RCM-015 | fail | configured | false | - |
| IDN-016 | pass | demonstrated | true | - |
| CLN-016 | pass | demonstrated | true | simulated-transmit-endpoint |
