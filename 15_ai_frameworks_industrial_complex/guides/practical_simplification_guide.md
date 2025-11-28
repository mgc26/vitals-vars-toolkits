# Practical Simplification Guide

## The Five-Category Operational Model

Replace 36 frameworks with five operational questions that have measurable answers. This guide shows you how.

---

## Why Five Categories?

Healthcare AI governance has proliferated into 36+ frameworks recycling the same high-level principles: transparency, fairness, accountability, human oversight. These principles appear in 10+ frameworks each.

The problem: Principles don't prevent harm. Operational capabilities do.

This guide organizes governance around **what must work** rather than **what must be documented**.

---

## The Five Categories

1. **Safety and Risk** - What can go wrong, how likely, what's the impact?
2. **Evidence and Validation** - Does this work for our patients, in our workflows?
3. **Monitoring and Maintenance** - How do we detect degradation, drift, or bias?
4. **Human Factors** - How does this integrate with clinician workflows and decision-making?
5. **Accountability** - When harm occurs, how do we learn and who's responsible?

---

## Category 1: Safety and Risk

### Core Question
**"What failure modes could cause patient harm, and how do we prevent them?"**

### Operational Requirements

#### Pre-Deployment Risk Assessment
**Required capabilities:**
- Systematic hazard analysis (not generic checklist)
- Clinical domain expertise in assessment (not just data scientists)
- Failure mode and effects analysis (FMEA) specific to AI
- Quantified risk levels with harm severity ratings

**Deliverables:**
- Risk matrix: likelihood × severity for identified hazards
- Mitigation strategies for high/medium risks
- Residual risk acceptance documentation
- Clear scope: what clinical decisions AI informs vs. determines

**Red flags:**
- Generic AI risk assessment not tailored to clinical context
- Risk assessment conducted without clinician input
- No quantified risk levels (just "low/medium/high" without definitions)
- Risk assessment done once pre-deployment, never updated

#### Specific Healthcare AI Hazards to Assess

**Dataset shift / distribution mismatch:**
- Algorithm trained on different patient population than yours
- Example: Epic sepsis model trained on one demographic, failed to generalize
- Mitigation: Mandatory local validation before deployment

**Automation bias:**
- Clinicians over-rely on algorithmic output, miss contradictory clinical signs
- Example: Radiology study showed false negative rates increased from 2.7% to 33% when AI was wrong
- Mitigation: Interface design, training, forcing functions

**Alert fatigue:**
- High false positive rates cause clinicians to ignore alerts
- Example: Clinicians override 49-96% of CDS alerts
- Mitigation: Tune sensitivity/specificity thresholds, audit override rates

**Proxy discrimination:**
- Algorithm uses seemingly neutral variable that encodes historical bias
- Example: Optum used healthcare costs as proxy for need, systematically underestimated Black patients
- Mitigation: Audit for proxy variables correlated with protected characteristics

**Feedback loops / performative prediction:**
- Algorithm's predictions alter the outcome it's predicting
- Example: Risk score influences resource allocation, which influences outcomes, which trains future model
- Mitigation: Causal analysis, monitoring for drift

**Data quality issues:**
- Training data contamination, mislabeling, artifacts
- Example: Skin lesion classifier used presence of rulers as cue for malignancy
- Mitigation: Data quality audits, artifact detection

**Adversarial inputs:**
- Malicious or unintentional inputs that cause incorrect outputs
- Example: Strategic documentation to game sepsis alerts
- Mitigation: Input validation, anomaly detection

### Measurable Outcomes
- ✓ Risk assessment completed by multi-disciplinary team including clinicians
- ✓ Quantified likelihood and severity for top 10 failure modes
- ✓ Documented mitigation strategies with responsible parties
- ✓ Risk register updated quarterly or after incidents
- ✓ Residual risks accepted by clinical leadership (not just IT)

### Resources Required
- **Personnel:** Clinical domain experts, patient safety officers, data scientists
- **Time:** 40-80 hours for initial assessment per AI system
- **Tools:** FMEA templates adapted for AI, risk scoring matrices
- **Ongoing:** Quarterly risk register review

### This Replaces Framework Requirements From:
- NIST AI RMF "Map" and "Measure" functions
- FDA GMLP risk management principles
- ISO 42001 risk assessment requirements
- Professional society risk identification recommendations

---

## Category 2: Evidence and Validation

### Core Question
**"Does this algorithm work for our patient population, in our workflows, with our data?"**

### Operational Requirements

#### Pre-Deployment Validation

**Required evidence from vendor:**
- Training data characteristics:
  - Sample size, data sources, time period
  - Patient demographics (age, sex, race/ethnicity distribution)
  - Clinical settings represented
  - Inclusion/exclusion criteria
- Validation methodology:
  - Independent test set (truly held-out, not just train/test split)
  - Performance metrics (sensitivity, specificity, PPV, NPV, AUC, calibration)
  - Performance stratified by subgroups
  - Confidence intervals
  - External validation studies (not just internal)
- Intended use and limitations:
  - Explicit clinical question addressed
  - Populations where validated vs. not validated
  - Known failure modes
  - Boundary conditions (when not to use)

**Red flags in vendor claims:**
- "Proprietary algorithm" without performance data
- Only internal validation on training institution data
- Performance metrics without confidence intervals
- No subgroup analysis (single aggregate performance number)
- Marketing claims exceed validation scope
- "AI-powered" label on deterministic rules-based system

**Local validation requirements:**
- Test on YOUR patient population before deployment
- Minimum sample size: 100-300 cases depending on prevalence
- Stratify performance by demographics available in your data
- Compare vendor-claimed performance to local performance
- **Decision rule:** If local performance diverges significantly from vendor claims, do not deploy

**Acceptable validation approaches:**
- Retrospective validation on historical data (fastest, least expensive)
- Prospective silent mode (algorithm runs but doesn't influence care; compare predictions to outcomes)
- Randomized trial (gold standard but resource-intensive; reserve for high-risk AI)

#### Integration Validation

**Workflow validation:**
- Shadow implementation period with human override
- Measure time added/saved in clinical workflow
- Assess interruption points and cognitive load
- Validate alert delivery mechanisms
- Test failure scenarios (what happens if AI is unavailable?)

**Interoperability validation:**
- Confirm data inputs available in your EHR
- Test data extraction accuracy
- Validate data format compatibility
- Assess missing data handling

### Measurable Outcomes
- ✓ Vendor provides training data characteristics and external validation
- ✓ Local validation completed on ≥100 representative cases
- ✓ Performance metrics stratified by ≥3 demographic subgroups
- ✓ Local performance within confidence intervals of vendor claims
- ✓ Workflow integration tested with end-users before live deployment
- ✓ Documented decision: deploy vs. do not deploy with justification

### Resources Required
- **Personnel:** Data analysts, clinicians for chart review, informatics team
- **Time:** 80-160 hours for comprehensive local validation
- **Data:** Access to historical patient data for retrospective validation
- **Tools:** Statistical software, EHR data extraction capability
- **Ongoing:** N/A for pre-deployment; see Category 3 for post-deployment

### Validation Decision Matrix

| Vendor External Validation | Local Validation Performance | Workflow Integration | Decision |
|-------------------------------|-------------------------------|----------------------|----------|
| Strong (published, multi-site) | Comparable to vendor claims | Positive clinician feedback | **DEPLOY** |
| Strong | Significantly worse than claims | Positive feedback | **DO NOT DEPLOY** (distribution mismatch) |
| Strong | Comparable | Negative feedback (workflow disruption) | **REDESIGN INTEGRATION** |
| Weak (internal only) | Good local performance | Positive feedback | **DEPLOY with close monitoring** |
| Weak | Weak local performance | Any | **DO NOT DEPLOY** |
| None | Any | Any | **DO NOT DEPLOY** |

### This Replaces Framework Requirements From:
- ONC HTI-1 training data and performance disclosure (vendor side)
- FDA GMLP validation principles
- Professional society validation recommendations
- NIST AI RMF "Measure" function

---

## Category 3: Monitoring and Maintenance

### Core Question
**"How do we detect when this algorithm stops working as intended?"**

### Operational Requirements

#### Continuous Performance Monitoring

**Required infrastructure:**
- **Automated monitoring pipeline** (not manual quarterly reviews)
  - Real-time or daily performance metric calculation
  - Dashboard accessible to clinical and technical teams
  - Automated alerting when performance degrades below threshold

**Metrics to monitor:**
- **Clinical performance:**
  - Sensitivity, specificity, PPV, NPV
  - Calibration (predicted probability vs. observed frequency)
  - Alert/prediction volume
  - Clinical outcome rates (if measurable)
- **Usage patterns:**
  - Alert override rates
  - Time to clinician action
  - User adoption rates
  - Near-miss captures
- **Data quality:**
  - Missing data rates
  - Data distribution drift (input feature ranges)
  - Anomalous inputs
- **Subgroup performance:**
  - Performance stratified by demographics
  - Disparity metrics (equal opportunity, demographic parity)

**Performance degradation thresholds:**

| Metric | Green (OK) | Yellow (Review) | Red (Action Required) |
|--------|------------|-----------------|----------------------|
| Sensitivity | >90% of baseline | 80-90% of baseline | <80% of baseline |
| Specificity | >90% of baseline | 80-90% of baseline | <80% of baseline |
| Alert override rate | <30% | 30-50% | >50% |
| Subgroup performance disparity | <5 percentage points | 5-10 percentage points | >10 percentage points |
| Missing data rate | <5% | 5-10% | >10% |

**Action required when red threshold crossed:**
- Immediate investigation by clinical and technical teams
- Consider temporary suspension of AI system
- Root cause analysis
- Mitigation plan before resuming use
- Update risk register

#### Drift Detection

**Types of drift to monitor:**
- **Data drift:** Input feature distributions change (e.g., different patient mix)
- **Concept drift:** Relationship between inputs and outcomes changes (e.g., treatment patterns evolve)
- **Label drift:** Outcome definitions or coding practices change

**Detection methods:**
- Statistical tests comparing current vs. baseline distributions
- Model performance tracking over time
- Clinical outcome surveillance

**Red flags indicating drift:**
- Sudden drop in performance metrics
- Increasing alert override rates
- Clinician feedback: "this seems wrong lately"
- Known clinical practice changes

#### Maintenance Requirements

**Model retraining decisions:**
- When: Performance degradation below threshold, or annually minimum
- Data: Include recent local data representing current population
- Validation: Repeat local validation process on retrained model
- Regulatory: If FDA-cleared device, retraining may require regulatory submission

**Software updates:**
- Track vendor software versions
- Require vendor to disclose what changed in updates
- Re-validate after major updates
- Be suspicious of "bug fixes" that alter algorithm behavior

#### Incident and Near-Miss Reporting

**Establish reporting mechanism:**
- Easy-to-use reporting channel for clinicians
- Non-punitive (focus on system learning, not individual blame)
- Standardized incident taxonomy
- Tracked in central database
- Regular review by governance committee

**What to report:**
- AI incorrect: Algorithm predicted X, actual outcome was Y
- AI misleading: Clinician initially followed AI, but further review revealed error
- AI unavailable: System downtime caused clinical impact
- Workflow disruption: AI interrupted critical task
- Near-miss: AI error caught before patient harm

**Incident review process:**
- Triage within 48 hours
- Investigation for high-severity incidents
- Root cause analysis
- Feedback loop to risk register and monitoring thresholds
- Share learnings (de-identified) across organization

### Measurable Outcomes
- ✓ Automated monitoring pipeline operational within 30 days of deployment
- ✓ Performance dashboard accessible to clinical champions
- ✓ Monitoring conducted daily or weekly (not quarterly)
- ✓ Defined performance thresholds with action triggers
- ✓ Subgroup performance monitored for disparities
- ✓ Incident reporting mechanism established and used
- ✓ ≥1 incident reported per 1000 AI interactions (indicates reporting culture, not absence of issues)
- ✓ Performance degradation detected and addressed within 30 days

### Resources Required
- **Personnel:** Data engineer to build pipeline, analyst to monitor dashboard, clinical champion to review
- **Time:** 120-200 hours to build initial monitoring infrastructure
- **Tools:** Data pipeline tools, visualization dashboard, statistical monitoring
- **Ongoing:** 4-8 hours/week for monitoring review and incident triage

### This Replaces Framework Requirements From:
- FDA post-market surveillance expectations
- ONC continuous quality monitoring
- ACR Assess-AI registry concept (but build it locally)
- AMIA "algorithmovigilance" principle
- Professional society continuous monitoring recommendations

**Critical insight:** This is the MOST important category and the one MOST ABSENT from current implementations. Health systems have governance committees but lack monitoring infrastructure.

---

## Category 4: Human Factors

### Core Question
**"How does AI integrate with clinician workflows and decision-making without causing automation bias or alert fatigue?"**

### Operational Requirements

#### Interface Design Principles

**Avoid "black box" presentations:**
- ❌ "Risk score: 87%" with no explanation
- ✓ "Risk score: 87% based on: elevated troponin (8.2), age >65, prior MI"

**Support critical evaluation:**
- Provide basis for predictions
- Display confidence intervals or uncertainty
- Show relevant patient data alongside prediction
- Enable easy comparison to clinical gestalt

**Prevent uncritical acceptance:**
- Avoid misleading precision (e.g., "87.3456%" implies false confidence)
- Use forcing functions for high-stakes decisions (require explicit review)
- Design "opt-in" rather than "opt-out" for recommendations
- Make override easy and non-burdensome

**Minimize interruptions:**
- Integrate alerts into existing workflow (not separate system requiring context switching)
- Use tiered alerting (reserve interruptive alerts for high-urgency)
- Allow customization of alert sensitivity per user preferences within bounds
- Respect "do not disturb" periods for focused clinical work

#### Training Requirements

**Before deployment:**
- All users complete training on:
  - What the AI does and doesn't do (scope and limitations)
  - How to interpret outputs
  - When to override or escalate
  - Automation bias awareness
  - How to report issues

**Ongoing:**
- Annual refresher training
- Training updates when AI system updated
- New user onboarding
- Feedback incorporation

**Training should include:**
- Concrete examples of AI correct and AI incorrect
- Case studies of documented failures (Epic sepsis, Optum bias)
- Hands-on practice with the tool
- Simulation of edge cases

#### Workflow Integration Assessment

**Measure:**
- Time added/saved per clinical encounter
- Number of clicks/steps required to use AI output
- Frequency of workflow interruptions
- User satisfaction scores
- Adoption rates (% of eligible encounters where AI used)

**Red flags:**
- Clinicians develop workarounds to avoid using AI
- High override rates without documented clinical reasoning
- Alert fatigue indicators (declining response times, batch dismissals)
- Excessive time required to interpret AI output
- Conflicts with existing clinical workflows

#### Automation Bias Mitigation Strategies

**Documented strategies for:**
- **Confirmatory bias prevention:** When AI agrees with initial impression, train users to actively seek disconfirming evidence
- **Anchoring prevention:** Present AI output AFTER clinician forms initial assessment (when feasible)
- **Authority gradient:** Junior clinicians should feel empowered to question AI
- **Workload management:** High cognitive load increases automation bias—monitor user workload
- **Transparency:** Explain AI limitations prominently

**Measure automation bias:**
- Chart review: Compare AI-concordant vs. AI-discordant cases for thoroughness of clinical assessment
- Simulation: Test clinicians with cases where AI is deliberately incorrect
- Survey: Self-reported reliance on AI

### Measurable Outcomes
- ✓ Interface design reviewed by human factors expert or usability testing
- ✓ 100% of users complete training before system access
- ✓ Workflow integration assessed with time-motion study or user feedback
- ✓ Override rates tracked and within expected ranges (10-30% for well-designed CDS)
- ✓ Automation bias mitigation strategies documented and implemented
- ✓ User satisfaction ≥3.5/5 or tool redesigned

### Resources Required
- **Personnel:** UX designer, clinical informaticist, training coordinator
- **Time:** 60-120 hours for interface design and usability testing
- **Training:** 30-60 minutes per user initially, 15 minutes annually
- **Tools:** Training modules, simulation cases
- **Ongoing:** Quarterly user feedback collection and workflow assessment

### This Replaces Framework Requirements From:
- "Human-in-the-loop" mandates from FDA, NIST, professional societies
- Transparency requirements from ONC, NIST, professional societies
- Training recommendations from Joint Commission/CHAI

**Critical insight:** Simply mandating "human oversight" is insufficient. Human factors engineering prevents the psychological reality of automation bias.

---

## Category 5: Accountability

### Core Question
**"When harm occurs or near-misses happen, how do we learn from them and who's responsible?"**

### Operational Requirements

#### Governance Structure

**Required components:**
- **AI Governance Committee:**
  - Multi-disciplinary: clinicians, patient safety, legal, IT, data science, ethics
  - Clear charter with decision authority (not advisory only)
  - Regular meetings (at least quarterly, more frequently if high AI deployment rate)
  - Documented decisions and rationale

- **AI Model Registry:**
  - Centralized inventory of all AI systems in use
  - For each system: intended use, risk level, validation data, responsible parties, monitoring status
  - Public or internally transparent
  - Updated in real-time (not static document)

- **Responsible Parties:**
  - Executive sponsor (accountable for oversight)
  - Clinical champion (validates clinical appropriateness)
  - Technical owner (maintains system)
  - Data steward (ensures data quality)

**Red flags:**
- Governance committee is advisory only without decision authority
- Committee lacks clinical representation
- Committee only reviews new AI (not ongoing monitoring)
- Model registry is static spreadsheet that's out of date

#### Liability and Responsibility Allocation

**Document clearly:**
- Vendor responsibilities vs. health system responsibilities
- Who validates local performance?
- Who monitors post-deployment?
- Who decides to suspend use if issues arise?
- Who is liable for harm: vendor, health system, individual clinician?

**Beware "shared responsibility" models that are actually liability displacement:**
- AWS: "You and your end users are responsible for all decisions made...based on your use of AI/ML Services"
- Epic: "shared" responsibility distributes liability
- Vendor provides platform only, you own clinical outcomes

**Ensure contracts specify:**
- Vendor must provide validation data and performance metrics
- Vendor must disclose software updates that change algorithm behavior
- Vendor must support your monitoring requirements (e.g., provide necessary data exports)
- Vendor liability for algorithmic errors vs. health system liability for implementation

**Individual clinician liability:**
- Clarify: Is clinician liable for following incorrect AI recommendation?
- AMA position: Physicians cannot be liable for misusing opaque-by-design tool
- Practical approach: Liability rests with organization if training and workflow design were adequate

#### Learning System / Feedback Loops

**Incident investigation process:**
1. Report filed (via non-punitive mechanism)
2. Triage: Low/medium/high severity
3. Investigation: Root cause analysis for medium/high severity
4. Action: Update risk register, modify monitoring thresholds, retrain users, suspend system, etc.
5. Feedback: Share learnings across organization (anonymized)
6. Follow-up: Verify effectiveness of corrective actions

**Cross-institutional learning:**
- Participate in registries (e.g., ACR Assess-AI for radiology)
- Share de-identified incident reports with specialty societies
- Contribute to building industry knowledge base
- Advocate for national AI adverse event reporting system (currently doesn't exist)

**Continuous improvement:**
- Annual review of AI governance effectiveness
- Update policies based on incidents and near-misses
- Incorporate emerging best practices
- Retire underperforming AI systems

#### Transparency and Documentation

**Internal transparency:**
- Model registry accessible to clinical staff
- Performance monitoring dashboards available
- Incident reports reviewed in quality committees
- Decision rationale documented

**External transparency (where appropriate):**
- Patients informed when AI influences their care
- Performance data published (e.g., registry participation)
- Incident patterns shared with regulatory bodies if required

**Documentation requirements:**
- Governance committee meeting minutes
- Validation study reports
- Monitoring dashboards
- Incident investigation reports
- Training completion records
- Risk register

### Measurable Outcomes
- ✓ Governance committee established with multi-disciplinary membership
- ✓ Model registry operational and current
- ✓ Responsible parties assigned for each AI system
- ✓ Vendor contracts specify liability allocation and data access rights
- ✓ Incident reporting mechanism operational with ≥1 incident per 1000 AI interactions reported
- ✓ Root cause analysis completed for all high-severity incidents within 30 days
- ✓ Corrective actions implemented and effectiveness verified
- ✓ Annual governance effectiveness review conducted

### Resources Required
- **Personnel:** Governance committee members (4-8 hours/quarter), program manager
- **Time:** 40-80 hours for initial governance structure setup
- **Tools:** Model registry database, incident tracking system
- **Ongoing:** 4-8 hours/week for governance program management

### This Replaces Framework Requirements From:
- Accountability principles from NIST, professional societies
- Governance structure recommendations from Joint Commission/CHAI, AMA, professional societies
- Transparency requirements from ONC, NIST, professional societies
- Continuous improvement from ISO 42001

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-3)
**Priority: Category 5 (Accountability) + Category 2 (Evidence and Validation)**

**Why:** Establish governance structure and validate existing AI before expanding deployment.

**Actions:**
1. Form governance committee with charter
2. Create model registry and inventory all AI systems currently in use
3. For each existing AI system:
   - Request validation data from vendor
   - Conduct local validation
   - Document responsible parties
4. Prioritize systems by risk level

**Resources:** 120-200 hours, primarily governance setup and validation studies

---

### Phase 2: Monitoring Infrastructure (Months 3-6)
**Priority: Category 3 (Monitoring and Maintenance)**

**Why:** Build capability to detect performance degradation and drift.

**Actions:**
1. Design monitoring pipeline for highest-risk AI systems
2. Build automated dashboards
3. Set performance thresholds
4. Establish incident reporting mechanism
5. Train users on reporting

**Resources:** 200-300 hours, data engineering and pipeline development

---

### Phase 3: Human Factors and Risk (Months 6-9)
**Priority: Category 4 (Human Factors) + Category 1 (Safety and Risk)

**Why:** Prevent automation bias and systematically assess failure modes.

**Actions:**
1. Conduct usability testing and time-motion studies for key AI systems
2. Redesign interfaces based on findings
3. Develop and deliver training on automation bias
4. Complete risk assessments (FMEA) for all high-risk AI systems
5. Update risk register

**Resources:** 150-250 hours, human factors expertise and clinical time

---

### Phase 4: Continuous Improvement (Months 9-12 and ongoing)
**Priority: All categories**

**Why:** Sustain and mature governance program.

**Actions:**
1. Quarterly monitoring review and dashboard updates
2. Annual validation refresh
3. Incident investigation and corrective actions
4. Governance effectiveness review
5. Policy updates based on learnings
6. Expand to additional AI systems

**Resources:** 4-8 hours/week ongoing

---

## Comparison to Framework Requirements

### What This Model Provides That Frameworks Don't:

**Operational specificity:**
- Frameworks: "Ensure fairness"
- This model: "Monitor subgroup performance weekly, trigger investigation if disparity >10 percentage points"

**Measurable outcomes:**
- Frameworks: "Maintain human oversight"
- This model: "Track override rates; if >50%, investigate for alert fatigue"

**Resource guidance:**
- Frameworks: (silent on resources)
- This model: "Expect 120-200 hours to build monitoring pipeline; 4-8 hours/week ongoing"

**Prioritization:**
- Frameworks: All principles equally emphasized
- This model: Monitoring infrastructure (Category 3) is most critical and most neglected

**Integration:**
- Frameworks: Separate documents for risk, transparency, fairness, accountability
- This model: Integrated operational workflow

---

## Self-Assessment Checklist

Use this to evaluate your current governance maturity:

### Category 1: Safety and Risk
- [ ] Risk assessment completed by multi-disciplinary team including clinicians
- [ ] Top 10 failure modes identified with quantified likelihood and severity
- [ ] Mitigation strategies documented with responsible parties
- [ ] Risk register updated at least quarterly

**Maturity: 0-1 = Beginning, 2-3 = Developing, 4 = Mature**

### Category 2: Evidence and Validation
- [ ] Vendor provides training data characteristics and external validation
- [ ] Local validation completed on ≥100 cases before deployment
- [ ] Performance stratified by demographic subgroups
- [ ] Documented decision to deploy with justification

**Maturity: 0-1 = Beginning, 2-3 = Developing, 4 = Mature**

### Category 3: Monitoring and Maintenance
- [ ] Automated monitoring pipeline operational
- [ ] Performance metrics calculated daily or weekly (not quarterly)
- [ ] Defined performance thresholds with action triggers
- [ ] Incident reporting mechanism established and used
- [ ] Performance degradation detected and addressed within 30 days

**Maturity: 0-2 = Beginning, 3-4 = Developing, 5 = Mature**

**NOTE:** Category 3 is most critical and most organizations score 0-2 here.

### Category 4: Human Factors
- [ ] Interface design includes human factors considerations
- [ ] 100% of users trained before access
- [ ] Workflow integration assessed
- [ ] Automation bias mitigation strategies implemented
- [ ] Override rates monitored and within expected ranges

**Maturity: 0-2 = Beginning, 3-4 = Developing, 5 = Mature**

### Category 5: Accountability
- [ ] Governance committee operational with decision authority
- [ ] Model registry current and accessible
- [ ] Responsible parties assigned for each AI system
- [ ] Vendor contracts specify liability allocation
- [ ] Incident reporting mechanism operational with incidents reported
- [ ] Root cause analysis completed for high-severity incidents

**Maturity: 0-3 = Beginning, 4-5 = Developing, 6 = Mature**

---

## Total Score Interpretation:

**0-8 points:** **Beginning** - You have governance documents but lack operational capabilities. High risk of governance theatre. Prioritize building monitoring infrastructure (Category 3) and conducting local validation (Category 2).

**9-16 points:** **Developing** - You have some operational capabilities but gaps remain. Focus on systematizing processes (automation, dashboards, defined thresholds) and addressing weakest category.

**17-24 points:** **Mature** - You have robust operational governance. Focus on continuous improvement, expanding to additional AI systems, and contributing to industry learning (registries, publications).

---

## Bottom Line

**Frameworks ask:** "Do you have a governance committee?"
**This model asks:** "Can you detect when your AI system's performance degrades by >10% within one week?"

**Frameworks ask:** "Have you assessed for bias?"
**This model asks:** "What is your Black patients' sensitivity compared to White patients' sensitivity for this algorithm, measured last week?"

**Frameworks ask:** "Do you maintain human oversight?"
**This model asks:** "What is your alert override rate, and what automation bias mitigation strategies have you implemented to prevent uncritical acceptance?"

This model replaces 36 framework checklists with five operational questions that have measurable answers. If you can't answer these questions, no amount of framework compliance will protect your patients.
