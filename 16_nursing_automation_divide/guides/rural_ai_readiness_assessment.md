# Rural AI Readiness Assessment

A self-assessment for rural and critical access hospitals evaluating nursing automation products.

---

## Instructions

Score each item: **0** = Not in place | **1** = Partial | **2** = Fully in place

Calculate section totals. Areas scoring below 50% indicate critical gaps that must be addressed before implementation or requirements that vendors must accommodate.

---

## Section A: Infrastructure (Max: 20 points)

| Item | Score (0-2) |
|------|-------------|
| **A1.** Broadband connectivity at 100/20 Mbps or higher consistently available | |
| **A2.** Backup internet connection (cellular, satellite) for primary outages | |
| **A3.** On-premise server capacity for local data processing | |
| **A4.** UPS/generator backup for network and computing infrastructure | |
| **A5.** Secure Wi-Fi coverage in all clinical areas | |
| **A6.** EHR system with documented API capabilities | |
| **A7.** IT support available during all clinical shifts (on-call acceptable) | |
| **A8.** Documented data backup and recovery procedures | |
| **A9.** Network monitoring for connectivity issues | |
| **A10.** Defined process for technology failure workarounds | |

**Section A Total:** _____ / 20

**Critical threshold:** Score below 10 indicates significant infrastructure risk. Require offline-first architecture from any vendor.

---

## Section B: EHR and Data Environment (Max: 16 points)

| Item | Score (0-2) |
|------|-------------|
| **B1.** EHR vendor actively maintained with current support contract | |
| **B2.** FHIR API available and enabled | |
| **B3.** HL7 interfaces operational for ADT, lab, and pharmacy | |
| **B4.** Documented data dictionary for key clinical fields | |
| **B5.** Historical data available for validation (12+ months) | |
| **B6.** Known data quality issues documented | |
| **B7.** Integration experience with third-party applications | |
| **B8.** Staff member designated for interface troubleshooting | |

**Section B Total:** _____ / 16

**Critical threshold:** Score below 8 indicates legacy system constraints. Require vendor experience with your specific EHR platform.

---

## Section C: Staffing and Workflow (Max: 18 points)

| Item | Score (0-2) |
|------|-------------|
| **C1.** Nursing staff stable (turnover below 20% annually) | |
| **C2.** Core nursing staff employed (not predominantly travelers) | |
| **C3.** Documented nursing workflows for key processes | |
| **C4.** Staff trained on current EHR functionality | |
| **C5.** Designated nursing informatics champion (formal or informal) | |
| **C6.** Protected time available for training (not just off-shift) | |
| **C7.** Experience with previous technology implementations | |
| **C8.** Defined escalation protocols when technology fails | |
| **C9.** Cross-training documentation for multi-department coverage | |

**Section C Total:** _____ / 18

**Critical threshold:** Score below 9 indicates workforce instability. Implementation timelines must account for high turnover and require simplified onboarding.

---

## Section D: Clinical Operations (Max: 14 points)

| Item | Score (0-2) |
|------|-------------|
| **D1.** Physician coverage model documented (on-site vs. on-call vs. tele) | |
| **D2.** Transfer protocols and relationships established | |
| **D3.** After-hours support resources identified | |
| **D4.** Patient population characteristics understood | |
| **D5.** Quality metrics currently tracked and reported | |
| **D6.** Incident reporting system in place | |
| **D7.** Experience with clinical decision support tools | |

**Section D Total:** _____ / 14

**Critical threshold:** Score below 7 indicates need for more explicit safety guardrails in any AI system.

---

## Section E: Governance and Resources (Max: 12 points)

| Item | Score (0-2) |
|------|-------------|
| **E1.** Executive sponsor identified for technology initiatives | |
| **E2.** Budget allocated for implementation and ongoing support | |
| **E3.** IT/informatics time available for implementation support | |
| **E4.** Legal review capacity for vendor contracts | |
| **E5.** Process for evaluating new technology outcomes | |
| **E6.** Board/leadership awareness of AI opportunities and risks | |

**Section E Total:** _____ / 12

**Critical threshold:** Score below 6 indicates governance gaps. Do not proceed without executive sponsorship and defined accountability.

---

## Summary Score

| Section | Score | Max | Percentage |
|---------|-------|-----|------------|
| A: Infrastructure | | 20 | |
| B: EHR/Data | | 16 | |
| C: Staffing/Workflow | | 18 | |
| D: Clinical Operations | | 14 | |
| E: Governance/Resources | | 12 | |
| **TOTAL** | | **80** | |

---

## Interpretation

**60-80 (75-100%):** Strong readiness. Standard vendor evaluation criteria apply. Focus on clinical fit and ROI.

**40-59 (50-74%):** Moderate readiness with gaps. Require vendors to address specific weak areas. Consider phased implementation starting with lowest-risk use cases.

**20-39 (25-49%):** Significant gaps. Require offline-first architecture, legacy system expertise, and simplified implementation. Consider infrastructure investments before AI deployment.

**Below 20 (<25%):** Critical gaps. Focus on foundational infrastructure and staffing before evaluating automation products. AI implementation likely premature.

---

## Red Flags Requiring Immediate Vendor Disclosure

Check any that apply to your facility:

- [ ] Broadband connectivity below 25/3 Mbps
- [ ] No backup internet connection
- [ ] EHR system end-of-life or unsupported
- [ ] No FHIR or HL7 integration capability
- [ ] Travel nurses exceed 40% of nursing workforce
- [ ] Single IT person managing all technology
- [ ] No on-site physician coverage overnight
- [ ] Operating margin below 1%

**If three or more boxes checked:** Require written vendor attestation that their product has been validated in similar environments. Request references from comparable facilities.

---

## Next Steps

1. Share results with executive sponsor
2. Identify top 3 gaps requiring vendor accommodation
3. Use Vendor Evaluation Questions to pressure-test claims
4. Apply Integration Requirements Matrix to architecture decisions
