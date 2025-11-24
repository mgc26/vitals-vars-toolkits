/*
Redundant Documentation Detection Queries
Identifies duplicate data entry, copy-paste patterns, and information silos

IMPORTANT: Adapt to your EHR vendor's data model
These queries assume you have access to clinical documentation tables

Metrics Calculated:
1. Duplicate medication list entries across systems
2. Redundant problem list documentation
3. Copy-paste frequency and patterns
4. Information re-entry across encounters
*/

-- ==============================================================================
-- QUERY 1: Medication List Duplication Across Sources
-- ==============================================================================
-- Identifies when the same medication appears in multiple places
-- Common slop pattern: Med rec in ED, admission, pharmacy, nursing MAR

WITH medication_sources AS (
    SELECT
        patient_id,
        encounter_id,
        medication_name,
        source_system,  -- e.g., 'ED_MedRec', 'Admission_H&P', 'Pharmacy_Order', 'Nursing_MAR'
        documented_by_role,
        documented_timestamp
    FROM medication_documentation  -- Replace with your table
    WHERE documented_timestamp >= CURRENT_DATE - INTERVAL '30 days'
),

medication_duplicates AS (
    SELECT
        patient_id,
        encounter_id,
        medication_name,
        COUNT(DISTINCT source_system) AS systems_count,
        STRING_AGG(DISTINCT source_system, ', ' ORDER BY source_system) AS all_sources,
        COUNT(*) AS total_entries
    FROM medication_sources
    GROUP BY patient_id, encounter_id, medication_name
    HAVING COUNT(DISTINCT source_system) > 1  -- Same med in multiple systems
)

SELECT
    systems_count,
    COUNT(*) AS medication_instances,
    ROUND(AVG(total_entries), 1) AS avg_duplicate_entries,
    all_sources AS common_duplicate_pattern
FROM medication_duplicates
GROUP BY systems_count, all_sources
ORDER BY medication_instances DESC
LIMIT 20;

-- Summary metrics
SELECT
    COUNT(DISTINCT encounter_id) AS encounters_with_duplicates,
    COUNT(*) AS total_duplicate_medications,
    ROUND(AVG(total_entries), 1) AS avg_times_reentered,
    ROUND((COUNT(*)::NUMERIC /
           (SELECT COUNT(*) FROM medication_documentation
            WHERE documented_timestamp >= CURRENT_DATE - INTERVAL '30 days')) * 100,
          1) AS pct_all_meds_duplicated
FROM medication_duplicates;


-- ==============================================================================
-- QUERY 2: Problem List Synchronization Failures
-- ==============================================================================
-- Detects when problem lists are out of sync across departments
-- Indicates clinicians are maintaining separate, conflicting documentation

WITH problem_list_entries AS (
    SELECT
        patient_id,
        problem_description,
        department,
        documented_by,
        last_updated
    FROM problem_list  -- Replace with your table
    WHERE status = 'Active'
      AND last_updated >= CURRENT_DATE - INTERVAL '90 days'
),

patient_problem_counts AS (
    SELECT
        patient_id,
        problem_description,
        COUNT(DISTINCT department) AS departments_with_entry,
        STRING_AGG(DISTINCT department, ', ') AS all_departments,
        MAX(last_updated) - MIN(last_updated) AS staleness_range
    FROM problem_list_entries
    GROUP BY patient_id, problem_description
)

SELECT
    departments_with_entry,
    COUNT(*) AS problem_instances,
    ROUND(AVG(EXTRACT(EPOCH FROM staleness_range) / 86400), 1) AS avg_staleness_days,
    all_departments AS common_pattern
FROM patient_problem_counts
WHERE departments_with_entry > 1
GROUP BY departments_with_entry, all_departments
ORDER BY problem_instances DESC
LIMIT 20;


-- ==============================================================================
-- QUERY 3: Copy-Paste Pattern Detection
-- ==============================================================================
-- Identifies clinicians using copy-paste (potential sign of documentation burden)
-- Benchmark: 66-90% of clinicians use copy-paste (Tsou et al. 2017)

WITH note_text_analysis AS (
    SELECT
        note_id,
        encounter_id,
        note_type,
        author_id,
        author_role,
        note_timestamp,
        note_text,
        -- Calculate text similarity to previous notes by same author
        LAG(note_text) OVER (PARTITION BY author_id, note_type
                             ORDER BY note_timestamp) AS previous_note_text,
        LAG(encounter_id) OVER (PARTITION BY author_id, note_type
                                ORDER BY note_timestamp) AS previous_encounter_id
    FROM clinical_notes  -- Replace with your table
    WHERE note_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND LENGTH(note_text) > 100  -- Exclude very short notes
),

copy_paste_detection AS (
    SELECT
        note_id,
        author_id,
        author_role,
        note_type,
        encounter_id,
        -- Simple overlap detection: calculate common substring length
        -- In practice, use your EHR's copy-paste flags if available
        CASE WHEN previous_note_text IS NOT NULL
                  AND note_text LIKE '%' || SUBSTRING(previous_note_text, 1, 200) || '%'
             THEN 1 ELSE 0 END AS likely_copy_paste,
        LENGTH(note_text) AS note_length
    FROM note_text_analysis
    WHERE encounter_id != previous_encounter_id  -- Different patients
)

SELECT
    author_role,
    note_type,
    COUNT(DISTINCT author_id) AS clinician_count,
    COUNT(*) AS total_notes,
    SUM(likely_copy_paste) AS likely_copy_paste_notes,
    ROUND((SUM(likely_copy_paste)::NUMERIC / COUNT(*)) * 100, 1) AS pct_copy_paste
FROM copy_paste_detection
GROUP BY author_role, note_type
HAVING COUNT(*) > 50  -- Sufficient sample size
ORDER BY pct_copy_paste DESC;


-- ==============================================================================
-- QUERY 4: Allergy Documentation Redundancy
-- ==============================================================================
-- Allergies are often re-documented at every encounter
-- Should be "enter once, reference everywhere"

WITH allergy_documentation AS (
    SELECT
        patient_id,
        allergy_name,
        encounter_id,
        department,
        documented_by_role,
        documented_timestamp
    FROM allergy_list  -- Replace with your table
    WHERE documented_timestamp >= CURRENT_DATE - INTERVAL '30 days'
      AND status = 'Active'
),

patient_allergy_reentry AS (
    SELECT
        patient_id,
        allergy_name,
        COUNT(DISTINCT encounter_id) AS times_reentered,
        COUNT(DISTINCT department) AS departments_entered,
        STRING_AGG(DISTINCT department, ', ') AS all_departments,
        MAX(documented_timestamp) - MIN(documented_timestamp) AS time_span
    FROM allergy_documentation
    GROUP BY patient_id, allergy_name
    HAVING COUNT(DISTINCT encounter_id) > 1  -- Re-entered multiple times
)

SELECT
    times_reentered,
    departments_entered,
    COUNT(*) AS allergy_instances,
    ROUND(AVG(EXTRACT(EPOCH FROM time_span) / 86400), 1) AS avg_days_span,
    all_departments AS common_pattern
FROM patient_allergy_reentry
GROUP BY times_reentered, departments_entered, all_departments
ORDER BY allergy_instances DESC
LIMIT 20;

-- Total waste calculation
SELECT
    COUNT(*) AS total_redundant_allergy_entries,
    SUM(times_reentered - 1) AS wasted_entries,
    ROUND(SUM(times_reentered - 1)::NUMERIC /
          (SELECT COUNT(*) FROM allergy_documentation
           WHERE documented_timestamp >= CURRENT_DATE - INTERVAL '30 days') * 100,
          1) AS pct_all_entries_redundant
FROM patient_allergy_reentry;


-- ==============================================================================
-- QUERY 5: Discharge Instruction Fragmentation
-- ==============================================================================
-- Measures how many times discharge info is entered/edited before completion
-- High edit count = incomplete handoffs requiring downstream cleanup

WITH discharge_documentation AS (
    SELECT
        encounter_id,
        patient_id,
        discharge_timestamp,
        instruction_component,  -- e.g., 'Medications', 'Follow-up', 'Activity', 'Diet'
        last_edited_by_role,
        edit_count,
        completion_status
    FROM discharge_instructions  -- Replace with your table
    WHERE discharge_timestamp >= CURRENT_DATE - INTERVAL '30 days'
),

discharge_complexity AS (
    SELECT
        encounter_id,
        COUNT(DISTINCT instruction_component) AS components_count,
        SUM(edit_count) AS total_edits,
        COUNT(CASE WHEN completion_status = 'Incomplete' THEN 1 END) AS incomplete_components,
        STRING_AGG(DISTINCT last_edited_by_role, ', ') AS all_roles_involved
    FROM discharge_documentation
    GROUP BY encounter_id
)

SELECT
    CASE
        WHEN total_edits <= 5 THEN '1-5 edits'
        WHEN total_edits <= 10 THEN '6-10 edits'
        WHEN total_edits <= 20 THEN '11-20 edits'
        ELSE '21+ edits'
    END AS edit_range,
    COUNT(*) AS discharge_count,
    ROUND(AVG(incomplete_components), 1) AS avg_incomplete_components,
    ROUND((SUM(incomplete_components)::NUMERIC / SUM(components_count)) * 100, 1) AS pct_incomplete
FROM discharge_complexity
GROUP BY
    CASE
        WHEN total_edits <= 5 THEN '1-5 edits'
        WHEN total_edits <= 10 THEN '6-10 edits'
        WHEN total_edits <= 20 THEN '11-20 edits'
        ELSE '21+ edits'
    END
ORDER BY edit_range;


-- ==============================================================================
-- QUERY 6: Information Re-Entry During Transitions of Care
-- ==============================================================================
-- Detects when the same information is documented by multiple roles
-- Classic slop pattern: ED documents, admitting documents again, primary team documents again

WITH care_transition_docs AS (
    SELECT
        patient_id,
        encounter_id,
        transition_type,  -- e.g., 'ED_to_Inpatient', 'Floor_to_ICU', 'Inpatient_to_Discharge'
        data_element,     -- e.g., 'Chief_Complaint', 'HPI', 'Past_Med_History', 'Social_History'
        documented_by_role,
        documented_timestamp,
        ROW_NUMBER() OVER (PARTITION BY encounter_id, transition_type, data_element
                           ORDER BY documented_timestamp) AS entry_sequence
    FROM transition_documentation  -- Replace with your table
    WHERE documented_timestamp >= CURRENT_DATE - INTERVAL '30 days'
)

SELECT
    transition_type,
    data_element,
    COUNT(DISTINCT encounter_id) AS transitions_observed,
    ROUND(AVG(CASE WHEN entry_sequence > 1 THEN 1.0 ELSE 0.0 END) * 100, 1) AS pct_reentered,
    MAX(entry_sequence) AS max_times_entered,
    STRING_AGG(DISTINCT documented_by_role, ', ') AS roles_involved
FROM care_transition_docs
GROUP BY transition_type, data_element
HAVING AVG(CASE WHEN entry_sequence > 1 THEN 1.0 ELSE 0.0 END) > 0.2  -- >20% re-entry rate
ORDER BY pct_reentered DESC
LIMIT 30;


-- ==============================================================================
-- USAGE NOTES
-- ==============================================================================
/*
1. Data Model Assumptions:
   - These queries assume your EHR tracks documentation metadata
   - You may need to join across multiple tables to get timestamps, roles, sources
   - Some EHRs don't expose copy-paste flags; use text similarity as proxy

2. Common Table Names by Vendor:
   Epic: MEDICATION_ORDER, PROBLEM_LIST, CLARITY_NOTE
   Cerner: MED_ORDER, DIAGNOSIS, CLINICAL_NOTE
   Meditech: RX_ORDER, PROBLEM, NOTE_TEXT

3. Interpretation Benchmarks:
   - >30% of medications duplicated across sources = serious slop problem
   - >50% problem list entries appearing in multiple departments = sync failure
   - >70% copy-paste rate = documentation burden forcing shortcuts
   - >20% of discharge instructions incomplete at handoff = workflow gap

4. Action Priorities:
   - Start with medication reconciliation (high-risk, high-frequency)
   - Audit allergy documentation next (safety-critical)
   - Address discharge instruction fragmentation (impacts readmissions)
   - Implement single source of truth for problem lists

5. ROI Calculation:
   - Avg time to re-enter medication: ~2 minutes
   - If 1000 med re-entries/month eliminated: 33 hours/month saved
   - At $90/hour RN rate: $2,970/month = $35,640/year per 1000 duplicates
*/
