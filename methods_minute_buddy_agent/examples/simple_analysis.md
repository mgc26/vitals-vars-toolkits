# Example: Simple Schema Analysis

This example demonstrates using the Buddy Agent workflow to analyze a healthcare database schema.

## Scenario
You have a complex Epic Clarity database with 50+ tables and need to understand:
- Table relationships
- Key metrics that can be derived
- Performance optimization opportunities

## Step 1: Gather Context

```bash
# Find all SQL files
find ./clarity_views -name "*.sql" > schema_files.txt

# Create context using the orchestrator
python buddy_agent_orchestrator.py \
  --task "analyze_epic_clarity_schema" \
  --context "./clarity_views/*.sql,./data_dictionary.csv" \
  --prompt-template "schema_analysis" \
  --output "./schema_analysis_results.md"
```

## Step 2: Review Generated Plan

The Buddy Agent will return something like:

```markdown
# Epic Clarity Schema Analysis

## 1. Core Patient Flow Tables
- PAT_ENC_HSP: Primary inpatient encounters
- ED_IEV_PAT_INFO: ED-specific patient data  
- CLARITY_BED: Bed management
- CLARITY_DEP: Department definitions

## 2. Key Relationships Identified
[Detailed ER diagram in mermaid format]

## 3. Recommended Indexes
-- For ED throughput queries
CREATE INDEX idx_ed_arrivals ON ED_IEV_PAT_INFO(ARRIVAL_DTTM, PAT_ENC_CSN_ID);
CREATE INDEX idx_bed_requests ON CLARITY_BED(REQUEST_DTTM, ASSIGNED_DTTM);

## 4. Core Metrics SQL
-- Average ED boarding time
WITH BoardingTimes AS (
  SELECT 
    e.PAT_ENC_CSN_ID,
    e.ADMITTED_DTTM,
    b.ASSIGNED_DTTM,
    DATEDIFF(hour, e.ADMITTED_DTTM, b.ASSIGNED_DTTM) as boarding_hours
  FROM ED_IEV_PAT_INFO e
  LEFT JOIN CLARITY_BED b ON e.PAT_ENC_CSN_ID = b.PAT_ENC_CSN_ID
  WHERE e.ADMITTED_DTTM IS NOT NULL
)
SELECT 
  AVG(boarding_hours) as avg_boarding_hours,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY boarding_hours) as median_boarding
FROM BoardingTimes;
```

## Step 3: Execute Recommendations

1. Review the generated SQL with your DBA team
2. Test indexes in development environment
3. Validate metrics against known benchmarks
4. Deploy in phases

## Results
- Identified 15 key tables for ED analytics
- Generated 8 core metric queries
- Reduced average query time from 45s to 3s with suggested indexes
- Found 3 data quality issues to address

## Lessons Learned
- Always include the data dictionary in context
- Review generated indexes with production workload in mind
- Validate business logic with clinical staff