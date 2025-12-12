# Integration Requirements Matrix

Decision framework for matching vendor architectures to rural infrastructure constraints.

---

## Part 1: Architecture Decision

### Cloud-Dependent vs. Edge/Hybrid Architecture

| Factor | Cloud-Dependent | Edge/Hybrid | Your Facility |
|--------|-----------------|-------------|---------------|
| **Connectivity required** | Continuous | Intermittent OK | |
| **Minimum bandwidth** | 50+ Mbps typical | 10 Mbps acceptable | |
| **Offline capability** | None or limited | Full or substantial | |
| **Data processing location** | Vendor servers | Local + cloud | |
| **Latency tolerance** | Low (real-time) | Higher (async OK) | |
| **Initial cost** | Lower (no hardware) | Higher (local infra) | |
| **Ongoing cost** | Higher (subscriptions) | Lower (maintenance) | |
| **Update deployment** | Automatic | Managed | |
| **Data residency control** | Limited | Full | |
| **Vendor lock-in risk** | Higher | Lower | |

### Decision Rule

**Choose Cloud-Dependent if:**
- Broadband consistently above 50 Mbps
- No critical functions require offline operation
- IT staff available for troubleshooting connectivity issues
- Budget favors lower upfront cost

**Choose Edge/Hybrid if:**
- Broadband below 50 Mbps or unreliable
- Clinical decisions must continue during outages
- Regulatory or policy requires local data control
- Long-term cost optimization preferred

**For most rural and CAH facilities:** Edge/Hybrid architecture is the safer choice.

---

## Part 2: Integration Approach

### FHIR-Based vs. Legacy Integration

| Factor | FHIR-Based | HL7 v2 | Direct/Custom | Your Facility |
|--------|------------|--------|---------------|---------------|
| **Standardization** | High | Moderate | Low | |
| **EHR support** | Epic, Cerner, modern | Most EHRs | All EHRs | |
| **Implementation time** | Weeks | Weeks-months | Months | |
| **Maintenance burden** | Low | Moderate | High | |
| **Bidirectional data** | Native | Possible | Possible | |
| **Vendor dependency** | Lower | Moderate | Higher | |
| **Future-proofing** | Strong | Moderate | Weak | |
| **Typical cost** | $ | $$ | $$$ | |

### EHR-Specific Guidance

| Your EHR | Recommended Integration | Notes |
|----------|------------------------|-------|
| Epic | FHIR (App Orchard) | Standard path, well-documented |
| Cerner (Oracle Health) | FHIR | Increasing support |
| MEDITECH Expanse | FHIR (limited) | Check specific module support |
| MEDITECH 6.x/Magic | HL7 v2 or Direct | FHIR limited or unavailable |
| CPSI | HL7 v2 or Direct | Custom build often required |
| Medhost | HL7 v2 or Direct | Limited API ecosystem |
| Evident (CPSI) | HL7 v2 | Check version-specific support |
| athenahealth | FHIR | Well-documented APIs |
| eClinicalWorks | FHIR (limited) | Check specific capabilities |

### Decision Rule

**Choose FHIR if:**
- EHR supports FHIR R4 for required data elements
- Vendor has documented FHIR implementation experience
- Future interoperability requirements expected

**Choose HL7 v2 if:**
- FHIR unavailable for your EHR
- Existing HL7 interfaces can be leveraged
- Vendor has specific experience with your EHR version

**Choose Direct/Custom if:**
- No standard interface available
- Vendor commits to building and maintaining
- Contract includes specific SLAs and support terms

---

## Part 3: Data Requirements Checklist

Identify which data elements the AI product requires and your facility's ability to provide them.

| Data Element | Required by Vendor? | Available in EHR? | Interface Method | Gap/Risk |
|--------------|--------------------|--------------------|------------------|----------|
| **Demographics** | | | | |
| Patient ID/MRN | | | | |
| Age/DOB | | | | |
| Sex/Gender | | | | |
| **Vitals** | | | | |
| Heart rate | | | | |
| Blood pressure | | | | |
| Temperature | | | | |
| Respiratory rate | | | | |
| SpO2 | | | | |
| **Labs** | | | | |
| CBC | | | | |
| BMP/CMP | | | | |
| Lactate | | | | |
| Troponin | | | | |
| **Medications** | | | | |
| Active medications | | | | |
| Administration times | | | | |
| Allergies | | | | |
| **Clinical** | | | | |
| Diagnoses/Problem list | | | | |
| Nursing assessments | | | | |
| Provider notes | | | | |
| Orders | | | | |
| **ADT** | | | | |
| Admission/Discharge | | | | |
| Transfers | | | | |
| Location/Bed | | | | |

**Risk Assessment:**
- Gaps in required data = reduced AI accuracy
- Manual data entry workarounds = workflow burden
- Missing elements = potential implementation blocker

---

## Part 4: Implementation Complexity Score

Rate your facility on each factor (1 = Simple, 3 = Complex):

| Factor | Score (1-3) | Notes |
|--------|-------------|-------|
| EHR age and version | | Newer = 1, Legacy = 3 |
| Existing interface inventory | | Many working = 1, Few/none = 3 |
| IT staff availability | | Dedicated = 1, Shared 15+ roles = 3 |
| Vendor EHR experience | | Many installs = 1, First = 3 |
| Network infrastructure | | Modern = 1, Limited = 3 |
| Data quality | | Clean = 1, Known issues = 3 |
| Staff turnover | | <15% = 1, >30% = 3 |
| Budget flexibility | | Adequate = 1, Constrained = 3 |

**Total Score:** _____ / 24

**Interpretation:**
- 8-12: Standard implementation risk
- 13-18: Elevated risk. Require extended timeline and contingency budget.
- 19-24: High risk. Consider infrastructure investment before AI deployment.

---

## Part 5: Vendor Architecture Matching

Complete this table for each vendor under consideration:

| Requirement | Your Facility | Vendor A | Vendor B | Vendor C |
|-------------|---------------|----------|----------|----------|
| **Architecture** | | | | |
| Cloud/Edge/Hybrid needed | | | | |
| Offline hours required | | | | |
| Bandwidth available | | | | |
| **Integration** | | | | |
| EHR platform | | | | |
| Integration method needed | | | | |
| Timeline acceptable | | | | |
| **Support** | | | | |
| On-site IT capacity | | | | |
| Remote support acceptable | | | | |
| Training model needed | | | | |

**Match Score:** Count requirements where vendor capability meets facility need.

| Vendor | Matches | Total | Percentage |
|--------|---------|-------|------------|
| Vendor A | | 9 | |
| Vendor B | | 9 | |
| Vendor C | | 9 | |

**Minimum threshold for consideration:** 7/9 (78%) matches

---

## Summary Decision Matrix

| Decision | Options | Your Choice | Rationale |
|----------|---------|-------------|-----------|
| Architecture | Cloud / Edge / Hybrid | | |
| Integration | FHIR / HL7 / Direct | | |
| Implementation complexity | Low / Medium / High | | |
| Preferred vendor | | | |
| Required accommodations | | | |
| Timeline estimate | | | |
| Budget impact | | | |
