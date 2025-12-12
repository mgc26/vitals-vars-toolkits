# Vendor Evaluation Questions for Rural AI Deployment

32 questions to ask nursing automation vendors. Use during RFP process, demos, or contract negotiations.

---

## Instructions

- Ask all questions in relevant sections
- Request written responses for critical items (marked with *)
- Verify claims with reference customers in similar facilities
- Document answers in your evaluation file

---

## Section 1: Connectivity and Offline Operation

**1.1*** Does your product function during internet outages? Describe offline capabilities.

**1.2*** What specific features are lost when connectivity drops? For how long can the system operate offline?

**1.3** How does the system synchronize data when connectivity restores? What happens to work completed offline?

**1.4** What is the minimum bandwidth required for full functionality? For degraded functionality?

**1.5*** Have you deployed in facilities with broadband below 50 Mbps? Provide references.

**1.6** What happens if latency exceeds 500ms? 2 seconds?

**1.7** Does your pricing model penalize facilities with intermittent connectivity (e.g., per-transaction cloud fees)?

---

## Section 2: EHR Integration

**2.1*** What EHR systems have you integrated with? Specifically: MEDITECH, CPSI, Medhost, Evident?

**2.2*** For our specific EHR and version, what integration method is required? FHIR? HL7? Direct database? Custom build?

**2.3** What is the typical timeline and cost for integration with legacy (non-Epic/Cerner) systems?

**2.4** Can you provide references from facilities running our EHR platform?

**2.5** What data elements are required from the EHR? What happens if some are unavailable?

**2.6*** How do you handle facilities with incomplete or inconsistent EHR data?

**2.7** Do you require specific EHR modules or configurations that may not be in our implementation?

---

## Section 3: Training and Workforce Turnover

**3.1*** How long does initial training take for nursing staff? Can it be completed in one 8-hour shift?

**3.2** What ongoing training is required? Annual? With each update?

**3.3*** How do you handle facilities with 30-40% travel nurse workforce? Is there an expedited onboarding path?

**3.4** What happens when a new nurse encounters the system without formal training?

**3.5** Are training materials available for self-service (video, quick reference cards)?

**3.6** What is the reading level and language availability of user interfaces and help content?

**3.7** How do you measure and track user proficiency?

---

## Section 4: Clinical Safety and Validation

**4.1*** Has your product been validated on rural patient populations? Provide study details.

**4.2*** What are the false positive and false negative rates? In what populations were these measured?

**4.3** How do you detect and report when model performance degrades?

**4.4*** What happens when the system is uncertain? How does it communicate confidence levels?

**4.5** What rule-based safety guardrails exist independent of the ML model?

**4.6** How does the system perform when patient acuity exceeds training data norms?

**4.7*** In facilities without immediate physician backup, what additional safeguards exist?

**4.8** What adverse events have been reported? How were they addressed?

---

## Section 5: Implementation Requirements

**5.1*** What on-site technical resources are required for implementation?

**5.2** Can implementation be completed entirely remotely?

**5.3** What is the typical implementation timeline for a 25-bed critical access hospital?

**5.4*** What internal staff time commitment is required during implementation?

**5.5** Who provides first-line support post-go-live? What are response time SLAs?

**5.6** What happens if implementation fails or must be rolled back?

---

## Section 6: Multi-Context Workflows

**6.1** Does the system adapt when nurses float between departments (ED, med-surg, OB)?

**6.2** Can one interface support inpatient, ED, and outpatient workflows without manual mode-switching?

**6.3** How does the system handle a nurse simultaneously managing patients across multiple units?

**6.4** Does your product assume single-specialty nursing workflows?

---

## Section 7: Financial and Contractual

**7.1*** What is the total cost of ownership for a 25-bed CAH over 3 years, including implementation?

**7.2** What ongoing costs exist (subscriptions, per-user fees, API call fees, support tiers)?

**7.3*** What is the contract exit process and cost if the product does not meet expectations?

**7.4** How is liability allocated between vendor and facility for AI-related adverse events?

**7.5** What insurance do you carry for product liability?

---

## Scoring Guide

For each section, rate vendor responses:

| Score | Meaning |
|-------|---------|
| 3 | Exceeds requirements with documented evidence |
| 2 | Meets requirements with credible explanation |
| 1 | Partially meets or meets with conditions |
| 0 | Does not meet or cannot demonstrate |

**Minimum thresholds for rural deployment:**
- Section 1 (Connectivity): Average score 2.0 or higher
- Section 2 (Integration): Score of 2+ on questions 2.1, 2.2, 2.6
- Section 4 (Safety): Score of 2+ on questions 4.1, 4.4, 4.7

---

## Red Flags

Terminate evaluation if vendor:
- Cannot provide any rural or CAH references
- Requires cloud connectivity for core clinical functions
- Has no experience with your EHR platform and quotes 6+ month custom build
- Cannot articulate what happens when the system is wrong
- Places all liability on the facility
- Prices implementation at >15% of your annual IT budget

---

## Documentation Template

| Question | Vendor Response | Score (0-3) | Notes |
|----------|-----------------|-------------|-------|
| 1.1 | | | |
| 1.2 | | | |
| ... | | | |

**Total Score:** _____ / 96

**Recommendation:** [ ] Proceed [ ] Proceed with conditions [ ] Do not proceed
