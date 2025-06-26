# FCOTS Toolkit - Quick Start Guide

## What's Included

### 📊 Analysis Tools
- **Python Script** (`code/scripts/fcots_analysis.py`) - Generate visualizations and ROI calculations
- **Sample Data** (`code/data/sample_fcots.csv`) - Test data to get started

### 🔍 SQL Queries  
- **Comprehensive Queries** (`toolkit/fcots_comprehensive_queries.sql`) - 7 production-ready queries:
  1. Basic FCOTS calculation
  2. Delay reason Pareto analysis
  3. Surgeon performance scorecard
  4. Room utilization impact
  5. Trend analysis with moving average
  6. Pre-op readiness dashboard
  7. Financial ROI calculator

### 📈 Dashboard Templates
- **Power BI Guide** (`toolkit/power_bi_dashboard_guide.md`) - DAX formulas and layout
- **Tableau Template** (`toolkit/tableau_dashboard_template.md`) - Calculated fields and design

### 📋 Implementation Resources
- **90-Day Roadmap** (`toolkit/90_day_implementation_guide.md`) - Week-by-week plan
- **Morning Huddle Template** (`toolkit/morning_huddle_template.md`)
- **Evening Checklist** (`toolkit/evening_checklist.md`)
- **Patient Callback Script** (`toolkit/patient_callback_script.md`)

## Quick Start Steps

### 1. Assess Current State (Day 1)
```sql
-- Run Query #1 from fcots_comprehensive_queries.sql
-- Get your baseline FCOTS %
```

### 2. Test the Analysis (Day 2)
```bash
cd code/scripts
python fcots_analysis.py
# Check assets folder for visualizations
```

### 3. Build Your Dashboard (Week 1)
- Pick Power BI or Tableau template
- Connect to your data
- Deploy to your team

### 4. Implement Changes (Week 2+)
- Follow 90-day implementation guide
- Start with morning huddles
- Add interventions gradually

## Most Common Questions

**Q: What if our EMR schema is different?**
A: The SQL queries include notes on customization. Look for the "NOTES ON CUSTOMIZATION" section.

**Q: Can we modify the Python analysis?**
A: Yes! The code is well-commented. Adjust parameters in the `generate_mock_data()` function.

**Q: Which dashboard tool should we use?**
A: Use what your team knows. Both templates create similar dashboards.

**Q: How do we track delay reasons?**
A: See Query #2 in the SQL file for creating a delay tracking system.

## Need the Full Article?
Read the complete issue on Vitals & Variables LinkedIn Newsletter for context and case studies.

## Quick Wins
1. **Morning Huddle** - Start tomorrow, even without data
2. **Surgeon Scorecards** - Run Query #3 weekly
3. **Text Alerts** - Simple but effective at T-30

Remember: Perfect is the enemy of good. Start somewhere!