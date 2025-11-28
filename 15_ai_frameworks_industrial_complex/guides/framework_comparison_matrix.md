# Framework Comparison Matrix

## How to Use This Matrix

This matrix evaluates major AI governance frameworks across dimensions that actually matter for implementation:

- **Enforcement**: Does it have teeth or is it voluntary?
- **Scope**: What does it cover?
- **Actionability**: Does it provide implementation tools or just principles?
- **Overlap**: Where does it duplicate other frameworks?
- **Verdict**: Should you prioritize it?

---

## Federal/Regulatory Frameworks

### FDA - Predetermined Change Control Plan (PCCP) Guidance
**Enforcement:** MANDATORY for AI/ML medical devices
**Scope:** Software as a Medical Device (SaMD) marketed for diagnostic, therapeutic, or monitoring purposes
**Effective Date:** December 2024
**Actionability:** HIGH - Specific requirements for change protocols, but does NOT support truly adaptive algorithms
**Key Requirements:**
- Pre-specify modification protocols (SaMD Pre-Specifications)
- Implement Algorithm Change Protocols (ACPs)
- Document performance monitoring
**Overlap:** None - unique regulatory pathway
**Gaps:** Post-market surveillance infrastructure, continuous learning systems unsupported
**Resource Burden:** HIGH - Requires substantial documentation and validation
**VERDICT:** **MANDATORY if developing/using FDA-cleared AI devices. Focus here first.**

---

### FDA - Good Machine Learning Practice (GMLP)
**Enforcement:** VOLUNTARY
**Scope:** ML development best practices
**Effective Date:** October 2021
**Actionability:** MEDIUM - 10 principles with some specificity
**Key Principles:**
- Clinical study participants/data sets representative
- Training datasets independent from test sets
- Best available reference standards
- Model design appropriate for intended use
**Overlap:** HIGH - overlaps with NIST AI RMF, ISO 42001, professional society principles
**VERDICT:** **LOW PRIORITY - Useful reference but voluntary and redundant with other frameworks.**

---

### ONC - HTI-1 Rule (Decision Support Interventions)
**Enforcement:** MANDATORY for certified health IT developers
**Scope:** "Predictive decision support interventions" within certified EHR systems
**Effective Date:** December 31, 2024 compliance deadline
**Actionability:** HIGH - Specifies 31 source attributes across 9 categories
**Key Requirements:**
- Disclose training data characteristics
- Report performance metrics (sensitivity, specificity)
- Document fairness evaluation
- Provide risk/benefit information
**Overlap:** Some overlap with FDA transparency requirements
**Gaps:** Only applies to certified health IT—third-party AI tools EXCLUDED
**Resource Burden:** HIGH - Significant documentation and disclosure requirements
**Penalties:** Information blocking penalties up to $1M per violation
**VERDICT:** **MANDATORY if you're a certified health IT developer or using certified systems with DSI. Critical compliance deadline end of 2024.**

---

### NIST AI Risk Management Framework 1.0
**Enforcement:** VOLUNTARY (no certification program)
**Scope:** Cross-sector AI risk management
**Effective Date:** January 2023
**Actionability:** LOW - High-level functions (Govern, Map, Measure, Manage) without healthcare-specific guidance
**Key Functions:**
- GOVERN: Establish AI governance culture and structure
- MAP: Context understanding and risk identification
- MEASURE: Risk assessment and analysis
- MANAGE: Risk prioritization and response
**Overlap:** VERY HIGH - Essentially every other framework borrows from NIST taxonomy
**Gaps:** No healthcare-specific profile exists; lacks clinical specificity
**Resource Burden:** LOW to MEDIUM depending on adoption depth
**VERDICT:** **LOW PRIORITY for direct compliance. Useful conceptual framework but no enforcement and highly abstract. Better to follow frameworks that operationalize NIST (like ACR's ARCH-AI).**

---

### CMS Guidance on AI Use
**Enforcement:** MEDIUM - Tied to Medicare Advantage compliance and reimbursement
**Scope:** Medicare Advantage organizations' use of AI for coverage decisions
**Effective Date:** February 2024
**Actionability:** MEDIUM - Specific prohibition on AI-only coverage denials
**Key Requirement:** AI cannot be sole basis for coverage denials; human review required
**Overlap:** Human oversight principle appears in nearly all frameworks
**VERDICT:** **MANDATORY if operating Medicare Advantage plan. Moderate priority for other entities.**

---

## International Standards

### ISO/IEC 42001:2023 - AI Management Systems
**Enforcement:** VOLUNTARY certification available
**Scope:** Organizational AI management system (cross-industry)
**Effective Date:** December 2023
**Actionability:** MEDIUM - Management system approach with audit criteria
**Key Components:**
- AI policy and objectives
- Risk assessment process
- Impact assessment for AI systems
- Data management and governance
**Overlap:** HIGH - Borrows from ISO 9001 (quality), ISO 27001 (information security)
**Conflict:** Uses High-Level Structure INCOMPATIBLE with ISO 13485 (medical devices)
**Resource Burden:** VERY HIGH - Formal management system implementation and third-party audit
**Cost:** Certification costs $15K-$50K+ depending on organization size
**VERDICT:** **LOW PRIORITY unless pursuing international markets requiring ISO certification or customers demanding it. Better to invest in operational monitoring than certification fees.**

---

### IEEE 7000-2021 - Model Process for Addressing Ethical Concerns
**Enforcement:** VOLUNTARY; CertifAIEd certification available
**Scope:** Value-based engineering for AI systems
**Effective Date:** 2021
**Actionability:** LOW - Requires specialized "Value Lead" training with limited availability
**Overlap:** HIGH - Ethical principles overlap with OECD, NIST, and professional societies
**Resource Burden:** VERY HIGH - Training, certification, and process restructuring
**Adoption:** LIMITED due to specialized requirements
**VERDICT:** **LOW PRIORITY - Academic interest but impractical for most health systems. No enforcement and resource-intensive.**

---

## Professional Society Frameworks

### AMA - Augmented Intelligence Principles
**Enforcement:** NONE (member influence only)
**Scope:** AI in clinical practice
**Actionability:** MEDIUM - Includes STEPS Forward governance toolkit
**Key Positions:**
- Prefers term "augmented intelligence" emphasizing assistive role
- Strong liability stance: Autonomous AI developers must carry medical liability insurance
- Physician judgment must be central
**Practical Tools:** STEPS Forward toolkit is most actionable among professional societies
**Overlap:** HIGH - Transparency, fairness, accountability appear in all frameworks
**VERDICT:** **LOW PRIORITY for compliance but MEDIUM PRIORITY for practical tools. STEPS Forward toolkit is useful implementation guide.**

---

### ACR - ARCH-AI and Assess-AI
**Enforcement:** NONE currently; formal accreditation targeted for 2027
**Scope:** Radiology AI governance and quality monitoring
**Actionability:** VERY HIGH - Specific infrastructure recommendations and operational registry
**Key Components:**
- **ARCH-AI (2024)**: Consensus-based infrastructure requirements
- **Assess-AI**: World's first AI quality registry for performance monitoring
**Unique Features:**
- Only framework with operational post-deployment monitoring system
- Specialty-specific protocols
- Registry allows cross-institutional performance comparison
**Overlap:** Moderate - Operationalizes principles from other frameworks
**VERDICT:** **HIGH PRIORITY - Best model for operational governance regardless of specialty. Adapt ARCH-AI approach and registry model to your context.**

---

### AMIA - 16 Principles for Health AI
**Enforcement:** NONE
**Scope:** Academic framework covering systems, organizational, and special considerations
**Actionability:** LOW - Principles without implementation tools
**Unique Contribution:** Coined "algorithmovigilance" for post-deployment monitoring (analogous to pharmacovigilance)
**Overlap:** VERY HIGH - Recycles common themes
**VERDICT:** **LOW PRIORITY - Academic framing without practical tools. Useful terminology ("algorithmovigilance") but no implementation guidance.**

---

### Other Professional Societies (ACP, ANA, HIMSS)
**Enforcement:** NONE
**Actionability:** LOW - Principles without specialty-specific protocols or tools
**Pattern:** All emphasize transparency, fairness, human oversight, accountability
**VERDICT:** **LOW PRIORITY - Safe to acknowledge existence but not prioritize for implementation. No marginal value over frameworks already covered.**

---

## Vendor Frameworks

### Microsoft Responsible AI / AWS Responsible AI / Epic AI Trust
**Enforcement:** NONE (voluntary self-regulation)
**Scope:** Vendor-specific products and services
**Actionability:** LOW - Principles without customer-facing implementation requirements
**Pattern Across All Vendors:**
- Emphasize "shared responsibility" model
- Customer assumes liability for clinical applications, data, outcomes
- Vendor responsible for infrastructure/platform only
- Limited public disclosure of audit results or validation data
**Example - AWS Terms:** "You and your end users are responsible for all decisions made, advice given, actions taken, and failures to take action based on your use of AI/ML Services"
**VERDICT:** **DO NOT PRIORITIZE - These frameworks exist for vendor liability protection, not customer safety. Demand validation data and monitoring capabilities regardless of framework claims.**

---

## Matrix Summary Table

| Framework | Enforcement | Actionability | Overlap | Priority |
|-----------|-------------|---------------|---------|----------|
| FDA PCCP | MANDATORY | HIGH | None | **CRITICAL** |
| FDA GMLP | Voluntary | MEDIUM | HIGH | LOW |
| ONC HTI-1 | MANDATORY* | HIGH | MEDIUM | **CRITICAL*** |
| NIST AI RMF | Voluntary | LOW | VERY HIGH | LOW |
| CMS Guidance | MEDIUM | MEDIUM | HIGH | MEDIUM* |
| ISO/IEC 42001 | Voluntary cert | MEDIUM | HIGH | LOW** |
| IEEE 7000 | Voluntary cert | LOW | HIGH | LOW |
| AMA Principles | None | MEDIUM | HIGH | LOW/MED*** |
| ACR ARCH-AI | None (yet) | VERY HIGH | MEDIUM | **HIGH** |
| AMIA Principles | None | LOW | VERY HIGH | LOW |
| Other Prof Soc | None | LOW | VERY HIGH | LOW |
| Vendor Frameworks | None | LOW | N/A | **AVOID** |

*If applicable to your organization type
**Unless required for international markets or customer contracts
***For practical tools, not compliance

---

## Decision Logic

### You MUST prioritize if:
- ✓ You develop or deploy FDA-cleared AI medical devices → **FDA PCCP**
- ✓ You're a certified health IT developer → **ONC HTI-1**
- ✓ You operate Medicare Advantage plans → **CMS Guidance**

### You SHOULD consider if:
- ⊙ You need operational governance model → **ACR ARCH-AI approach** (adapt to specialty)
- ⊙ You want practical implementation tools → **AMA STEPS Forward**
- ⊙ International customers require ISO certification → **ISO/IEC 42001**

### You CAN SAFELY IGNORE:
- ✗ Voluntary frameworks without implementation tools (NIST, GMLP, most professional societies)
- ✗ Vendor frameworks (these protect vendors, not you)
- ✗ Academic frameworks without operational components (IEEE 7000, AMIA principles)

---

## The Real Question

Instead of "Which frameworks do we comply with?" ask:

**"Do we have operational capabilities to:"**
1. Validate AI performance on our patient population before deployment?
2. Monitor for drift, performance degradation, and bias continuously?
3. Report and learn from near-misses and adverse events?
4. Train clinicians on automation bias and workflow integration?
5. Allocate accountability when harm occurs?

If the answer is no, compliance with 36 frameworks won't protect your patients.

If the answer is yes, you're doing governance—regardless of which framework names you cite.

---

## Redundancy Map

These framework themes appear in 10+ frameworks each:

**Transparency/Explainability:**
- NIST, FDA GMLP, ONC HTI-1, ISO 42001, IEEE 7000, AMA, AMIA, ACP, ANA, HIMSS, all vendors

**Bias/Fairness:**
- NIST, FDA GMLP, ONC HTI-1, ISO 42001, IEEE 7000, AMA, AMIA, ACP, ANA, HIMSS, ACR

**Human Oversight:**
- NIST, FDA GMLP, CMS, ISO 42001, AMA, AMIA, ACP, ANA, HIMSS, ACR, all vendors

**Accountability:**
- NIST, FDA GMLP, ISO 42001, IEEE 7000, AMA, AMIA, ACP, ANA, HIMSS

**Privacy/Security:**
- NIST, FDA GMLP, ONC HTI-1, ISO 42001, AMIA, ACP, ANA, HIMSS, all vendors

**Observation:** If a principle appears in 10+ frameworks, the marginal value of one more framework stating the same principle is approximately zero.

---

## Bottom Line

**Must do:** FDA and ONC compliance if applicable
**Should do:** Operational monitoring (ACR model)
**Can skip:** Everything else unless contractually required

Invest 70% of governance resources in operational infrastructure, 20% in mandatory compliance, 10% in one operational best-practice framework adapted to your context.

If you're doing the reverse, you're doing governance theatre.
