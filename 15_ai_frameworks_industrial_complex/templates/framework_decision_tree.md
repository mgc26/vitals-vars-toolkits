# AI Governance Framework Decision Tree

## How to Use This Decision Tree

Answer the questions in sequence to identify which frameworks actually apply to your organization. Most health systems will find they have 2-4 mandatory frameworks and can safely ignore the other 30+.

---

## START HERE

**What is your organization type?**

→ AI/ML Medical Device Manufacturer → Go to [Section A: Device Manufacturers](#section-a-device-manufacturers)
→ EHR/Health IT Vendor → Go to [Section B: Health IT Developers](#section-b-health-it-developers)
→ Hospital/Health System → Go to [Section C: Healthcare Providers](#section-c-healthcare-providers)
→ Payer/Medicare Advantage Organization → Go to [Section D: Payers](#section-d-payers)
→ AI Tool Vendor (not device, not EHR-integrated) → Go to [Section E: Third-Party AI Vendors](#section-e-third-party-ai-vendors)

---

## Section A: Device Manufacturers

You develop AI/ML software marketed for diagnostic, therapeutic, or monitoring purposes.

### Question A1: Is your AI software a medical device under FDA jurisdiction?

**How to determine:**
- Does it diagnose, treat, cure, mitigate, or prevent disease?
- Does it analyze medical data to provide device-specific recommendations?
- Is it marketed for medical purposes?

**YES** → **MANDATORY: FDA PCCP Guidance**
- You must follow Predetermined Change Control Plan requirements
- Document SaMD Pre-Specifications and Algorithm Change Protocols
- Plan for pre-market and post-market validation
- Resource requirement: HIGH
- Timeline: Plan 6-12 months for initial compliance

**Also consider:**
- **FDA GMLP** (voluntary but demonstrates good practices)
- **ISO 13485** if pursuing international markets (medical device quality management)
- **Warning:** ISO/IEC 42001 uses incompatible structure with ISO 13485

**NO** → Your AI may not be regulated as a device. Proceed to Question A2.

---

### Question A2: Could your AI qualify for 21st Century Cures Act CDS exemption?

**Criteria for exemption:**
- Provides clinical decision support to healthcare professionals
- Displays basis for recommendations (not "black box")
- Includes relevant information about development/limitations
- Intended to enable HCPs to independently review basis

**YES** → You may be exempt from device regulation
- Still subject to FTC consumer protection laws
- No specific framework requirements but best practices recommended
- **Risk:** FDA has narrowed this exemption; monitor regulatory updates

**NO** → Consult regulatory counsel. You may be in unclear jurisdiction.

---

### Question A3: Are you pursuing international markets?

**YES** → Consider:
- **ISO/IEC 42001** if customers require AI management system certification
- **EU AI Act** compliance if marketing in European Union (risk-based requirements)
- **UK MHRA** guidance if marketing in United Kingdom
- Resource requirement: VERY HIGH for certification
- Timeline: 12-18 months for ISO certification

**NO** → Skip international standards unless customer contracts require.

---

**SECTION A SUMMARY FOR DEVICE MANUFACTURERS:**

✓ **MANDATORY:** FDA PCCP (if medical device)
✓ **RECOMMENDED:** FDA GMLP (demonstrates best practices)
✓ **IF INTERNATIONAL:** ISO 13485 (not ISO 42001 due to incompatibility)
✗ **SKIP:** NIST, professional society frameworks, vendor frameworks (not applicable to manufacturers)

---

## Section B: Health IT Developers

You develop certified health IT (e.g., EHR systems, modules seeking ONC certification).

### Question B1: Does your health IT product include predictive decision support interventions (DSI)?

**What qualifies as DSI:**
- Uses data inputs to generate outputs or predictions
- Supports clinical decision-making
- Part of certified health IT system

**Examples:** Sepsis prediction alerts, readmission risk scores, deterioration warnings

**YES** → **MANDATORY: ONC HTI-1 Rule**
- Must disclose 31 source attributes across 9 categories
- Document training data characteristics
- Report performance metrics (sensitivity, specificity, AUC)
- Include fairness evaluation
- **Compliance deadline:** December 31, 2024
- **Penalty:** Information blocking penalties up to $1M per violation
- Resource requirement: HIGH
- Timeline: If not already compliant, prioritize immediately

**NO** → ONC transparency requirements may not apply, but monitor regulatory updates.

---

### Question B2: Is your DSI also an FDA-regulated medical device?

**YES** → You face DUAL REGULATION
- Must comply with both FDA PCCP AND ONC HTI-1
- Requirements may conflict (e.g., FDA lockdown vs. ONC transparency)
- **Critical:** Map requirements to avoid conflicts
- Consult regulatory counsel for harmonization strategy
- Resource requirement: VERY HIGH

**NO** → ONC is primary regulatory concern.

---

### Question B3: Do you integrate third-party AI models?

**YES** → You are responsible for:
- Validating third-party model performance in your system
- Ensuring third-party models meet ONC transparency requirements
- Contractual liability allocation with model developers
- **Risk:** Cannot simply pass through vendor attestations

**NO** → In-house models only simplifies compliance.

---

**SECTION B SUMMARY FOR HEALTH IT DEVELOPERS:**

✓ **MANDATORY:** ONC HTI-1 (if certified health IT with DSI)
✓ **MANDATORY:** FDA PCCP (if also medical device)
✓ **RECOMMENDED:** NIST AI RMF vocabulary for internal risk management
✗ **SKIP:** Voluntary professional society frameworks, vendor frameworks

---

## Section C: Healthcare Providers

You are a hospital, health system, clinic, or practice deploying AI tools.

### Question C1: Are you deploying FDA-cleared AI medical devices?

**Examples:** AI-enabled imaging diagnostics, clinical decision support devices

**YES** → You must:
- Follow FDA's conditions of use
- Implement any required monitoring per device clearance
- Report adverse events via MAUDE if required
- **Note:** Post-market surveillance requirements are evolving
- Resource requirement: MEDIUM
- Check each device's specific clearance conditions

**NO** → Move to Question C2.

---

### Question C2: Does your EHR system include certified predictive DSI?

**YES** → Your vendor must comply with ONC HTI-1
- Request ONC-mandated source attributes from vendor
- Validate disclosed performance metrics against local population
- Document fairness evaluation for your patient demographics
- **If vendor cannot provide:** Raises serious governance concerns
- Resource requirement: MEDIUM (mostly vendor dependency)

**NO** → Move to Question C3.

---

### Question C3: Are you deploying third-party AI tools (not FDA-cleared, not ONC-certified)?

**Examples:** Ambient clinical documentation, scheduling optimization, staffing prediction

**CRITICAL FINDING:** Most clinical AI falls in this **regulatory gap**
- Not governed by FDA (not marketed as device)
- Not governed by ONC (not in certified health IT)
- **You assume ALL validation and monitoring responsibility**

**Required actions (no specific framework, but operational necessities):**
1. **Pre-deployment validation:**
   - Request training data characteristics
   - Validate on YOUR patient population
   - Test for bias in YOUR demographics
   - Assess workflow integration risk

2. **Post-deployment monitoring:**
   - Track performance degradation
   - Monitor for drift
   - Capture near-misses and adverse events
   - Establish performance thresholds for removal

3. **Human factors:**
   - Train clinicians on automation bias
   - Design workflows preventing uncritical acceptance
   - Establish escalation pathways

**Best practice framework:** Adapt **ACR ARCH-AI** approach regardless of specialty
- Establish AI governance committee
- Create model registry
- Implement performance monitoring
- Resource requirement: HIGH (build infrastructure)

**NO third-party tools** → Move to Question C4.

---

### Question C4: Do you operate a Medicare Advantage plan or participate in MA risk arrangements?

**YES** → Go to [Section D: Payers](#section-d-payers)

**NO** → Move to Question C5.

---

### Question C5: Are you in a specialty with established AI governance frameworks?

**Radiology:** **ACR ARCH-AI and Assess-AI** are most developed
- High actionability, operational tools
- Consider adopting even if voluntary

**Other specialties:** Currently lack specialty-specific operational frameworks
- Adapt ACR model to your context
- Engage specialty societies to advocate for development

---

### Question C6: Do international customers, partners, or accreditors require specific certifications?

**YES** → Evaluate on case-by-case basis:
- Some international partners may require ISO/IEC 42001
- Some contracts may specify framework adherence
- **Assess cost-benefit:** Is certification requirement worth contract value?
- Resource requirement: VERY HIGH for certification
- Timeline: 12-18 months

**NO** → Skip voluntary certifications.

---

**SECTION C SUMMARY FOR HEALTHCARE PROVIDERS:**

**MANDATORY** (if applicable):
✓ FDA device conditions of use (if deploying cleared devices)
✓ Vendor ONC compliance verification (if using certified health IT with DSI)
✓ CMS AI guidance (if operating MA plans)

**HIGHLY RECOMMENDED** (even though voluntary):
✓ ACR ARCH-AI operational approach (adapt to specialty)
✓ Establish governance infrastructure: committee, registry, monitoring

**LOWER PRIORITY:**
⊙ AMA STEPS Forward toolkit (useful implementation guide)
⊙ NIST AI RMF vocabulary (helpful framing)

**SKIP:**
✗ ISO/IEC 42001 (unless contractually required)
✗ IEEE 7000 (impractical resource requirements)
✗ AMIA/ACP/ANA principles (redundant with operational frameworks)
✗ Vendor frameworks (exist for vendor protection)

---

## Section D: Payers

You operate a Medicare Advantage plan or manage insurance coverage decisions.

### Question D1: Do you use AI algorithms to inform coverage decisions?

**YES** → **MANDATORY: CMS Guidance (February 2024)**
- AI cannot be sole basis for coverage denials
- Human review required for all denials
- Document human involvement in decision process
- **Legal risk:** Following Optum/naviHealth lawsuits
- Resource requirement: MEDIUM
- Ensure workflows enforce human override capability

**NO** → If you use NO AI in coverage decisions, CMS guidance may not apply. However, monitor for scope expansion.

---

### Question D2: Are coverage algorithms also used by provider partners?

**YES** → You may face regulatory obligations at provider level
- Algorithm may trigger ONC requirements if integrated into certified health IT
- Algorithm may trigger FDA requirements if marketed as clinical tool
- **Liability consideration:** Shared responsibility with providers

**NO** → Payer-only use simplifies regulatory picture.

---

**SECTION D SUMMARY FOR PAYERS:**

✓ **MANDATORY:** CMS AI guidance (if AI informs coverage decisions)
✓ **RECOMMENDED:** NIST AI RMF vocabulary for internal risk management
⊙ **CONSIDER:** AMA principles (understanding provider perspective)
✗ **SKIP:** Clinical frameworks (FDA, ONC) unless algorithm is dual-use clinical tool

---

## Section E: Third-Party AI Vendors

You develop AI tools for healthcare but not as FDA-regulated devices and not as ONC-certified health IT.

**Examples:** Ambient clinical documentation, scheduling optimization, revenue cycle prediction, staffing tools

### Question E1: Could your tool be construed as a medical device?

**Risk factors:**
- Makes or suggests diagnoses
- Recommends treatments
- Predicts clinical outcomes used for medical decisions
- Marketed with clinical claims

**YES or UNCERTAIN** → **HIGH LEGAL RISK**
- FDA may view as device requiring clearance
- Consult regulatory counsel immediately
- Consider 510(k) pre-submission meeting with FDA
- **Do not assume CDS exemption applies**—FDA has narrowed this

**NO** → You operate in regulatory gap. Proceed to Question E2.

---

### Question E2: Does your tool integrate with certified health IT systems?

**YES** → Your customers (health IT developers) face ONC requirements
- Customers will demand you provide:
  - Training data characteristics
  - Performance metrics
  - Fairness evaluations
  - Validation data
- **Contract terms:** Define liability allocation clearly
- Expect customers to pass through ONC compliance costs

**NO** → Standalone tool. Proceed to Question E3.

---

### Question E3: What validation data can you provide to customers?

Healthcare provider customers increasingly demand:
- Training data demographics
- External validation results
- Performance metrics on diverse populations
- Drift monitoring capabilities
- Post-deployment performance tracking

**Your competitive position depends on governance credibility:**

**Strong position:**
- External validation studies
- Published performance data
- Built-in monitoring tools
- Transparent limitations

**Weak position:**
- Internal validation only
- Undisclosed training data
- "Black box" claims
- Liability disclaimers in lieu of evidence

**Framework choice impact:**
- Adhering to FDA GMLP principles (voluntary) demonstrates rigor
- ISO/IEC 42001 certification may appeal to some customers but is expensive
- **Most impactful:** Operational validation data and monitoring capabilities

---

### Question E4: Are you pursuing international markets?

**YES** → Consider:
- **EU AI Act** (risk-based requirements; high-risk AI systems face strict requirements)
- **ISO/IEC 42001** if customers require certification
- Timeline: 12-18 months for certification

**NO** → Focus on operational validation over certification.

---

**SECTION E SUMMARY FOR THIRD-PARTY AI VENDORS:**

**CRITICAL:**
✓ Clarify FDA device status (consult counsel if uncertain)
✓ Understand if customers face ONC requirements (affects your obligations)

**RECOMMENDED:**
✓ Follow FDA GMLP principles (demonstrates rigor even if voluntary)
✓ Invest in external validation and monitoring capabilities
⊙ Consider ISO/IEC 42001 if customers demand certification

**COMPETITIVE ADVANTAGE:**
- Validation data and monitoring tools matter more than framework claims
- Providers increasingly demand evidence over attestations

**SKIP:**
✗ Professional society frameworks (not applicable to vendors)
✗ Clinical specialty frameworks (unless targeting specific specialty)

---

## FINAL DECISION SUMMARY

### If you checked ANY of these, it's MANDATORY:
- [ ] FDA-regulated medical device → **FDA PCCP**
- [ ] ONC-certified health IT with DSI → **ONC HTI-1** (Deadline: December 31, 2024)
- [ ] Medicare Advantage coverage algorithms → **CMS Guidance**

### If you checked ANY of these, it's HIGHLY RECOMMENDED:
- [ ] Healthcare provider deploying AI → **ACR ARCH-AI approach** (operational model)
- [ ] Any organization needing practical tools → **AMA STEPS Forward toolkit**

### If you checked ANY of these, EVALUATE COST-BENEFIT:
- [ ] International markets → **ISO/IEC 42001** or **EU AI Act**
- [ ] Customer contracts require certification → **ISO/IEC 42001**

### You can SKIP these regardless of organization type:
- NIST AI RMF (useful vocabulary but no enforcement)
- AMIA, ACP, ANA, HIMSS principles (redundant)
- IEEE 7000 (impractical resource requirements)
- Vendor frameworks (protect vendors, not you)

---

## Still Unsure? Use This Heuristic

**Enforcement test:** Does the framework have legal teeth?
- YES → Prioritize
- NO → Deprioritize

**Actionability test:** Does it provide implementation tools or just principles?
- TOOLS → Consider
- PRINCIPLES ONLY → Deprioritize

**Overlap test:** Does it repeat what 10 other frameworks already said?
- YES → Deprioritize
- NO (unique requirements) → Consider

**Resource test:** Can you fund this AND operational monitoring infrastructure?
- YES to both → Consider
- NO → Choose operational infrastructure over framework compliance

---

## Bottom Line

Most organizations have 1-3 mandatory frameworks and should invest remaining resources in operational capabilities:

1. **Mandatory compliance** (20% of resources)
2. **Operational monitoring infrastructure** (70% of resources)
3. **One operational best-practice framework** (10% of resources)

If you're spending 70% of resources mapping to voluntary frameworks, you're doing governance theatre instead of patient safety.

---

## Questions This Decision Tree Doesn't Answer

This tree identifies framework obligations. It does NOT tell you:
- How to technically implement monitoring systems
- Specific bias detection methods
- Legal liability allocation (consult counsel)
- Contract negotiation strategies with vendors

For operational implementation, see the **Practical Simplification Guide** in this toolkit.
