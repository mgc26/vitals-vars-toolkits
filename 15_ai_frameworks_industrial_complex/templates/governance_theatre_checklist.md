# Governance Theatre Red Flags Checklist

## Purpose

This checklist identifies warning signs that your organization is investing in **governance appearance** (theatre) rather than **governance substance** (patient safety).

Use this quarterly to audit your AI governance program—or when evaluating vendor governance claims.

---

## How to Use This Checklist

For each item:
- ✓ **Check if this describes your organization/vendor**
- Count total checks
- Use scoring guide at bottom to interpret

**Be honest.** Governance theatre is common and understandable given framework complexity. The goal is identification, not judgment.

---

## Red Flag Category 1: Committee Theatre

### Structure Without Function

- [ ] **We have an AI Governance Committee that meets quarterly (or less frequently)**
  - *Why it's a red flag:* AI systems can degrade in days or weeks. Quarterly oversight is too infrequent for operational governance.
  - *What substance looks like:* Monitoring dashboards reviewed weekly; committee meets monthly or when performance thresholds triggered.

- [ ] **Our governance committee is "advisory" without decision authority**
  - *Why it's a red flag:* Advisory committees can be safely ignored when business pressures mount.
  - *What substance looks like:* Committee has authority to suspend AI systems, reject deployments, mandate changes.

- [ ] **Committee meetings focus on approving new AI tools but don't review ongoing performance of deployed AI**
  - *Why it's a red flag:* Pre-deployment review alone misses the critical post-deployment phase where most failures occur.
  - *What substance looks like:* Every meeting includes monitoring dashboard review, incident reports, performance trend analysis.

- [ ] **Governance committee has no clinical representation, or clinicians attend irregularly**
  - *Why it's a red flag:* AI governance without clinical domain expertise cannot assess clinical risk or failure modes.
  - *What substance looks like:* Clinicians are permanent members with attendance expectations; clinical champions assigned per AI system.

- [ ] **Committee members haven't completed training on AI fundamentals, bias detection, or healthcare AI risks**
  - *Why it's a red flag:* Uninformed oversight cannot identify problems.
  - *What substance looks like:* All committee members complete foundational training; ongoing education on emerging issues.

- [ ] **Meeting minutes focus on framework compliance mapping ("We comply with NIST, ONC, FDA...") rather than operational metrics**
  - *Why it's a red flag:* Counting frameworks doesn't prevent harm.
  - *What substance looks like:* Minutes document performance metrics, incident reviews, corrective actions, risk register updates.

**Category 1 Score: _____ / 6**

---

## Red Flag Category 2: Documentation Theatre

### Policies Without Implementation

- [ ] **We have detailed AI governance policies (50+ pages) but no one can describe our actual validation process in 5 sentences**
  - *Why it's a red flag:* Impressive documents that don't influence behavior create false security.
  - *What substance looks like:* Brief, actionable procedures that staff can summarize; evidence of actual use.

- [ ] **Our model registry is a static spreadsheet that hasn't been updated in 3+ months**
  - *Why it's a red flag:* Static registry doesn't reflect reality; no one is maintaining it.
  - *What substance looks like:* Real-time database integrated with monitoring systems; auto-updated; regularly consulted.

- [ ] **We claim to follow 5+ frameworks but have no document mapping our processes to specific requirements**
  - *Why it's a red flag:* Generic claims without specifics suggest surface-level adoption.
  - *What substance looks like:* If claiming framework compliance, explicit mapping exists showing how each requirement is met.

- [ ] **Our policies require "local validation" but don't specify: validation sample size, required metrics, acceptance thresholds, or responsible parties**
  - *Why it's a red flag:* Vague requirements allow checkbox compliance without rigor.
  - *What substance looks like:* Specific operational requirements (e.g., "minimum 100 cases, stratified by race, sensitivity >80%").

- [ ] **We have an "AI risk assessment template" but completed risk assessments lack quantified likelihood/severity or are identical across different AI systems**
  - *Why it's a red flag:* Generic risk assessments suggest copy-paste rather than genuine analysis.
  - *What substance looks like:* Risk assessments are system-specific, quantified, and lead to different mitigation strategies.

- [ ] **Our governance documentation was created for accreditation/compliance purposes and hasn't been referenced since submission**
  - *Why it's a red flag:* Pure theatre—document exists to satisfy external requirement, not guide internal behavior.
  - *What substance looks like:* Policies and procedures are working documents consulted regularly; evidence of use (notes, updates, references).

**Category 2 Score: _____ / 6**

---

## Red Flag Category 3: Vendor Attestation Theatre

### Accepting Claims Without Evidence

- [ ] **We accept vendor attestations that their AI is "fair," "transparent," or "validated" without requesting underlying data**
  - *Why it's a red flag:* Vendors have incentive to make favorable claims; verification is your responsibility.
  - *What substance looks like:* Demand training data characteristics, validation study results, performance metrics with confidence intervals.

- [ ] **Vendor contract includes "shared responsibility" language but doesn't specify exactly what vendor vs. customer is responsible for**
  - *Why it's a red flag:* Vague "shared responsibility" often means vendor liability displacement.
  - *What substance looks like:* Contract explicitly lists vendor obligations (e.g., "provide quarterly performance reports") and customer obligations.

- [ ] **Vendor claims algorithm is "explainable" or "interpretable" but provides only post-hoc saliency maps or generic feature importance without clinical validation**
  - *Why it's a red flag:* Saliency maps can be misleading; explainability theater is common.
  - *What substance looks like:* Explanations validated with clinicians; shown to improve decision-making or catch errors.

- [ ] **We don't conduct local validation before deployment because "vendor already validated it"**
  - *Why it's a red flag:* Epic sepsis model was vendor-validated; failed in real-world deployment at 170+ hospitals.
  - *What substance looks like:* All AI systems validated locally on your patient population regardless of vendor validation.

- [ ] **Vendor emphasizes "AI-powered" in marketing but we haven't verified whether it's actually machine learning vs. rules-based system**
  - *Why it's a red flag:* "AI washing" is rampant; rules-based systems have different governance needs than ML.
  - *What substance looks like:* Understand whether AI is deterministic rules, statistical model, or neural network; govern accordingly.

- [ ] **Vendor provides "model card" or "transparency report" but it's based on pre-deployment data and hasn't been updated to reflect real-world performance**
  - *Why it's a red flag:* Static model cards don't capture drift or performance degradation.
  - *What substance looks like:* Request performance updates quarterly; conduct your own monitoring.

**Category 3 Score: _____ / 6**

---

## Red Flag Category 4: Monitoring Theatre

### Dashboards Without Action

- [ ] **We have monitoring dashboards but no one is assigned to review them regularly**
  - *Why it's a red flag:* Dashboards that aren't viewed are decorative.
  - *What substance looks like:* Named individuals responsible for weekly dashboard review; review documented.

- [ ] **Our dashboards show aggregate performance metrics but not stratified by demographics/subgroups**
  - *Why it's a red flag:* Aggregate metrics hide disparities; Optum algorithm had good aggregate performance but severe racial bias.
  - *What substance looks like:* Performance stratified by age, sex, race/ethnicity at minimum; disparity metrics tracked.

- [ ] **We monitor performance quarterly but not continuously**
  - *Why it's a red flag:* Algorithms can drift rapidly; quarterly monitoring misses problems.
  - *What substance looks like:* Automated daily or weekly metric calculation; real-time alerting when thresholds crossed.

- [ ] **We track alert volume and override rates but have no defined thresholds that trigger investigation**
  - *Why it's a red flag:* Tracking without action is theatre; numbers need to drive decisions.
  - *What substance looks like:* Clear thresholds (e.g., "override rate >50% triggers review"); documented investigations when thresholds crossed.

- [ ] **We've never suspended or removed an AI system due to performance concerns**
  - *Why it's a red flag:* If you've never stopped an AI, either (a) you're extraordinarily lucky, (b) your AI is very low-risk, or (c) your monitoring isn't sensitive enough.
  - *What substance looks like:* Evidence of systems being paused for investigation, modified, or retired based on monitoring data.

- [ ] **Our "post-market surveillance" consists of waiting for complaints rather than proactive monitoring**
  - *Why it's a red flag:* Reactive surveillance depends on clinicians noticing and reporting problems; many failures go undetected.
  - *What substance looks like:* Automated performance monitoring independent of user complaints.

**Category 4 Score: _____ / 6**

---

## Red Flag Category 5: Incident Reporting Theatre

### Reporting Mechanisms Without Reports

- [ ] **We have an AI incident reporting mechanism but have received zero reports in the past year**
  - *Why it's a red flag:* Either (a) you have no AI deployed, (b) you have perfect AI (unlikely), or (c) no one is using the reporting system.
  - *What substance looks like:* Incident reports proportional to AI deployment; ≥1 incident per 1000 AI interactions suggests healthy reporting culture.

- [ ] **Incident reports go to IT helpdesk rather than clinical quality/patient safety team**
  - *Why it's a red flag:* AI clinical incidents are patient safety issues, not IT support tickets.
  - *What substance looks like:* AI incidents triaged by patient safety or quality team; integrated with existing safety reporting.

- [ ] **We haven't conducted root cause analysis on any AI incidents because incidents are treated as "user error"**
  - *Why it's a red flag:* Blaming users prevents system learning; automation bias is a known phenomenon.
  - *What substance looks like:* Root cause analysis applies systems thinking; looks for design, training, workflow, or algorithm failures.

- [ ] **Incident reports are filed but not reviewed by governance committee or used to update risk register**
  - *Why it's a red flag:* Reporting without learning is theatre.
  - *What substance looks like:* Incidents drive governance actions; risk register updated; corrective actions implemented.

- [ ] **We have no mechanism to share learnings from AI incidents with other departments or institutions**
  - *Why it's a red flag:* Each institution learning from its own mistakes in isolation wastes opportunities for system-wide improvement.
  - *What substance looks like:* De-identified incident reports shared internally; participation in registries or specialty society learning collaboratives.

- [ ] **Clinicians fear reporting AI errors because it might reflect poorly on their judgment**
  - *Why it's a red flag:* Punitive culture suppresses reporting; true incident rate is invisible.
  - *What substance looks like:* Non-punitive reporting culture; focus on system improvement not individual blame; leadership models reporting.

**Category 5 Score: _____ / 6**

---

## Red Flag Category 6: Training Theatre

### Completion Without Comprehension

- [ ] **AI training consists of clicking through slides with no comprehension check**
  - *Why it's a red flag:* Completion ≠ learning; users may not understand limitations or how to critically evaluate AI.
  - *What substance looks like:* Training includes knowledge checks, case studies, hands-on practice.

- [ ] **Training emphasizes legal compliance ("you must use AI because it's policy") rather than clinical reasoning**
  - *Why it's a red flag:* Compliance framing encourages uncritical acceptance rather than critical evaluation.
  - *What substance looks like:* Training emphasizes when and why to override AI; builds clinical reasoning skills.

- [ ] **Users complete training once at deployment; no refreshers or updates when AI system changes**
  - *Why it's a red flag:* One-time training doesn't account for knowledge decay, staff turnover, or system updates.
  - *What substance looks like:* Annual refresher training; training updates when AI modified; new hire onboarding.

- [ ] **Training doesn't cover automation bias or include examples of AI being wrong**
  - *Why it's a red flag:* Without understanding failure modes, users over-rely on AI.
  - *What substance looks like:* Training explicitly covers documented AI failures (Epic sepsis, Optum bias); teaches skepticism.

- [ ] **Training completion rate is 100% but user satisfaction scores are low or override rates are extreme (very high or very low)**
  - *Why it's a red flag:* Completing training doesn't mean training was effective or users are using AI appropriately.
  - *What substance looks like:* Training effectiveness measured by user confidence, appropriate override rates, simulation performance.

- [ ] **Training materials are generic AI ethics content rather than specific to the AI tools deployed in your organization**
  - *Why it's a red flag:* Generic training doesn't prepare users for specific tools and workflows.
  - *What substance looks like:* Training customized to each AI system; covers specific use cases, limitations, and workflows.

**Category 6 Score: _____ / 6**

---

## Red Flag Category 7: Validation Theatre

### Studies Without Rigor

- [ ] **"Validation" consists of vendor demonstration during product demo, not independent testing**
  - *Why it's a red flag:* Vendor demos use cherry-picked cases; not representative of real-world performance.
  - *What substance looks like:* Independent testing on consecutive cases or random sample from your data.

- [ ] **Local validation uses retrospective data but we don't assess whether historical data matches current patient population**
  - *Why it's a red flag:* Dataset shift can occur over time; validating on old data doesn't guarantee current performance.
  - *What substance looks like:* Validate on recent data; monitor whether patient mix has changed since validation.

- [ ] **Validation sample size is <50 cases or not powered to detect clinically meaningful differences**
  - *Why it's a red flag:* Small samples yield wide confidence intervals; can't reliably assess performance.
  - *What substance looks like:* Power analysis determines sample size; minimum 100-300 cases depending on prevalence.

- [ ] **Validation report shows performance metrics (e.g., "AUC = 0.85") but no confidence intervals or subgroup analysis**
  - *Why it's a red flag:* Point estimates without confidence intervals obscure uncertainty; aggregate metrics hide disparities.
  - *What substance looks like:* Performance metrics with 95% CIs; stratified by age, sex, race/ethnicity.

- [ ] **We proceed with deployment despite validation showing performance significantly worse than vendor claims**
  - *Why it's a red flag:* Deploying AI that doesn't work locally is governance failure.
  - *What substance looks like:* Clear go/no-go decision criteria; deployment only if local validation meets thresholds.

- [ ] **Validation is treated as one-time pre-deployment activity; we don't re-validate after AI updates or when performance degrades**
  - *Why it's a red flag:* AI can change (software updates) or drift (population shift); one-time validation is insufficient.
  - *What substance looks like:* Re-validation after major updates, annually, or when monitoring suggests performance decline.

**Category 7 Score: _____ / 6**

---

## Red Flag Category 8: Transparency Theatre

### Disclosure Without Substance

- [ ] **We disclose to patients that "AI may be used in your care" but provide no specifics about which AI systems or what decisions they inform**
  - *Why it's a red flag:* Vague disclosure provides appearance of transparency without enabling informed consent.
  - *What substance looks like:* Specific disclosure of which AI systems used, what they predict, how outputs used in clinical decisions.

- [ ] **Our "explainable AI" shows feature importance scores but clinicians don't understand them or find them clinically useful**
  - *Why it's a red flag:* Technical explainability ≠ clinical interpretability; explanations must be actionable.
  - *What substance looks like:* Explanations validated with clinicians; shown to improve decision-making or error detection.

- [ ] **We publish "AI transparency reports" but they're marketing documents emphasizing positive results without discussing limitations or failures**
  - *Why it's a red flag:* Selective transparency that hides problems is public relations, not governance.
  - *What substance looks like:* Balanced reporting including limitations, failures, corrective actions, and ongoing challenges.

- [ ] **Internal stakeholders (e.g., clinical staff, quality team) don't have access to AI performance data—only governance committee sees it**
  - *Why it's a red flag:* Restricting access to performance data prevents distributed oversight and frontline feedback.
  - *What substance looks like:* Performance dashboards accessible to clinical champions; culture of transparency within organization.

- [ ] **We claim to have "transparent AI" but have never shown clinicians the training data characteristics, validation results, or performance trends**
  - *Why it's a red flag:* Transparency requires making information available, not just claiming it exists.
  - *What substance looks like:* Training data characteristics, validation reports, and monitoring dashboards shared with users.

- [ ] **Patients are not informed when AI contributes to a clinical decision that affects them**
  - *Why it's a red flag:* Patients have right to know what influences their care; undisclosed AI use erodes trust.
  - *What substance looks like:* Clinical notes document AI use; patients informed during shared decision-making.

**Category 8 Score: _____ / 6**

---

## Scoring Guide

**Total Score: _____ / 48**

### Score Interpretation:

**0-8 points: Governance Substance**
- You have robust operational governance with minimal theatre
- Focus on continuous improvement and expanding best practices
- Consider contributing to industry learning through publications or registry participation

**9-16 points: Mixed Governance**
- You have some operational capabilities but also areas of theatre
- Review highest-scoring categories and prioritize remediation
- Likely investing in some compliance activities that don't prevent harm
- Opportunity: Redirect resources from theatre to substance

**17-24 points: Governance Theatre Dominant**
- You have governance appearance but limited operational capability
- High risk: Documentation won't protect patients or organization
- Priority: Build monitoring infrastructure (Category 4), conduct local validation (Category 7)
- Consider: Are you spending more time mapping to frameworks than monitoring performance?

**25-32 points: Extensive Governance Theatre**
- You have impressive documents and committee structures but little operational governance
- Very high risk: False sense of security
- Urgent priority: Shift from compliance documentation to operational monitoring
- Reality check: Can you answer "What was the sensitivity of AI System X for Black patients last week?" If no, governance is theatre.

**33-48 points: Almost Pure Theatre**
- Governance exists primarily for compliance appearance
- Critical risk: No meaningful oversight of AI systems
- Immediate action: Pause new AI deployments until operational governance in place
- Consider: Is AI governance treated as checkbox for accreditation rather than patient safety program?

---

## Red Flags by Stakeholder

### For Health System Leaders:

**Warning signs your organization prioritizes theatre:**
- Governance committee reports focus on "we comply with X frameworks" rather than "we detected and fixed Y performance issues"
- Substantial budget for consultants to map frameworks; minimal budget for monitoring infrastructure
- Inability to answer: "How long would it take to detect if an AI system's performance degraded 20%?"

**Evidence of substance:**
- Operational metrics in leadership dashboards (override rates, performance trends, incident counts)
- At least one AI system paused or removed based on monitoring data
- Staff can describe validation and monitoring processes without referring to documents

---

### For Clinicians Evaluating AI Tools:

**Warning signs vendor prioritizes theatre:**
- Vendor marketing emphasizes framework compliance but won't share validation data
- "Shared responsibility" language in contract without specifying vendor obligations
- Vendor claims AI is "explainable" but provides generic post-hoc explanations not validated with clinicians
- Vendor resists providing data needed for your local validation or monitoring

**Evidence of substance:**
- Vendor provides training data demographics, external validation results, performance metrics with confidence intervals
- Vendor offers monitoring support (data exports, performance APIs, integration with your dashboards)
- Vendor contract specifies their obligation to disclose algorithm updates and support your oversight
- Vendor has published validation studies in peer-reviewed journals (not just whitepapers)

---

### For Patients and Advocates:

**Warning signs AI governance is theatre:**
- Hospital claims "rigorous AI governance" but no information available about which AI systems used or how they perform
- Generic disclosure: "AI may be used in your care" without specifics
- No mechanism for patients to opt out or ask questions about AI used in their care
- No published performance data or transparency reports

**Evidence of substance:**
- Specific disclosure of AI systems used and what clinical decisions they inform
- Published performance data (even if limited by privacy/proprietary concerns)
- Patient advisory input on AI governance policies
- Evidence of AI systems being paused or modified based on performance concerns

---

## Action Items Based on Score

### If Your Score is High (17+ points):

**Immediate actions (this month):**
1. Stop claiming compliance with frameworks you're not operationalizing
2. Identify your highest-risk AI system currently deployed
3. Conduct local validation if not already done
4. Assign named individual to review performance weekly

**Short-term actions (this quarter):**
1. Build basic monitoring dashboard for highest-risk AI
2. Establish performance thresholds that trigger investigation
3. Set up non-punitive incident reporting mechanism
4. Conduct usability testing / workflow assessment for one AI system

**Medium-term actions (this year):**
1. Extend monitoring to all deployed AI systems
2. Implement automated alerting for performance degradation
3. Develop validation and monitoring procedures that staff actually use
4. Retire or pause AI systems that don't meet performance thresholds

---

## Bottom Line Questions

**If you can't answer these questions, you're doing governance theatre:**

1. What was the sensitivity of your highest-risk AI system for each major demographic subgroup last week?
2. How many AI-related incidents were reported in the past month?
3. What percentage of alerts from your AI systems are overridden by clinicians?
4. When was the last time you suspended or modified an AI system based on monitoring data?
5. If an AI system's performance degraded 20%, how long would it take you to detect it?

**If answering these questions requires:**
- Convening a committee meeting: Theatre
- Consulting a policy document: Theatre
- Requesting data from vendor: Theatre (you should have it already)
- "We don't track that": Theatre

**If you can answer immediately with data:**
- You're doing governance.

---

## Using This Checklist for Vendor Evaluation

When evaluating AI vendors, ask them to complete this checklist **about their own internal governance.**

**Red flags if vendor:**
- Refuses to complete checklist
- Scores high on theatre indicators
- Cannot provide evidence requested in "what substance looks like"
- Becomes defensive about questions

**Green flags if vendor:**
- Transparently acknowledges governance gaps they're working on
- Provides evidence without hesitation (validation data, monitoring reports, incident learnings)
- Offers to support your governance needs (data access, performance monitoring, updates)
- Has published validation studies and discusses limitations openly

---

## Continuous Improvement

**Use this checklist:**
- Quarterly for internal governance audits
- Annually for comprehensive program review
- When evaluating new AI vendors
- After AI incidents to assess governance gaps
- When preparing for accreditation or regulatory inspection

**Goal over time:**
- Score decreases as theatre is replaced with substance
- Evidence of operational governance accumulates
- Can answer bottom-line questions immediately
- Shift from "we comply with frameworks" to "we prevented X harm by detecting Y performance issue"

---

**Remember:** The presence of governance theatre doesn't mean bad intent. Framework complexity makes theatre understandable. But recognizing theatre is the first step toward building substance.
