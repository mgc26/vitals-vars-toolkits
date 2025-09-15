# The Coasean Build vs. Buy Decision Toolkit for Healthcare AI

## Based on Ronald Coase's Transaction Cost Economics

This toolkit applies Nobel laureate Ronald Coase's transaction cost economics framework to help healthcare organizations make data-driven decisions about whether to buy vendor solutions or build custom AI/analytics capabilities.

## What's Included

### 1. The Coasean Calculator (`python/coasean_calculator.py`)
- **6-factor scoring model** based on transaction cost economics
- Evaluates: spec volatility, verification difficulty, interdependence, data sensitivity, supplier power, frequency/tempo
- Healthcare-specific weights (HIPAA considerations)
- Provides clear recommendations: STRONG BUY, LEAN BUY, HYBRID, LEAN BUILD, or STRONG BUILD
- Includes switching cost penalty calculations
- Run with: `python coasean_calculator.py`

### 2. Decision Analyzer (`python/decision_analyzer.py`)
- Comprehensive build vs. buy analysis framework
- TCO (Total Cost of Ownership) calculations
- Risk assessment matrices
- ROI projections with confidence intervals
- Generates detailed recommendation reports

### 3. SQL Analysis Queries (`sql/coasean_decision_analysis.sql`)
Four powerful queries to analyze your portfolio:
- **Query 1**: Project Portfolio Transaction Cost Assessment - evaluate all current projects
- **Query 2**: Vendor Lock-in Risk Assessment - calculate switching costs
- **Query 3**: Historical Performance Analysis - learn from past decisions
- **Query 4**: Hybrid Opportunity Identification - find where to split the difference

### 4. Dashboard Template (`dashboards/coasean_dashboard_template.md`)
Complete specifications for building a Coasean decision dashboard:
- 7 key visualizations including portfolio quadrants and transaction cost heat maps
- Implementation notes for Tableau, Power BI, and Looker
- KPIs focused on alignment and potential savings
- Color schemes and drill-down capabilities

### 5. Build Readiness Checklist (`guides/build_readiness_checklist.md`)
Comprehensive assessment covering:
- Technical capability evaluation
- Organizational readiness factors
- Resource availability check
- Risk evaluation framework
- Go/no-go decision criteria

## How to Use This Toolkit

### Step 1: Run the Coasean Calculator
```bash
cd python
python coasean_calculator.py
```
This will run example scenarios and show you how to score your own projects.

### Step 2: Analyze Your Portfolio
Use the SQL queries to assess your current project portfolio:
- Identify misaligned decisions
- Calculate potential savings
- Assess vendor lock-in risks

### Step 3: Build Your Dashboard
Follow the dashboard template to create visualizations that track:
- Portfolio alignment with Coasean recommendations
- Transaction cost levels across projects
- Vendor switching costs
- Historical decision performance

### Step 4: Make Data-Driven Decisions
Use the framework to evaluate new projects:
1. Score each project on the 6 Coasean factors (1-5 scale)
2. Calculate the weighted transaction cost score
3. Follow the recommendation based on thresholds
4. Consider hybrid approaches for medium scores

## The Coasean Decision Framework

### Transaction Cost Thresholds
- **Score ≤ 13**: STRONG BUY - Market transactions are efficient
- **Score 14-16**: LEAN BUY - Favor purchasing with flexibility
- **Score 17-19**: HYBRID - Buy commodities, build differentiators
- **Score 20-22**: LEAN BUILD - Consider internal development
- **Score ≥ 23**: STRONG BUILD - Internal coordination is cheaper

### The 6 Coasean Factors Explained

1. **Specification Volatility** (1-5)
   - How often do requirements change?
   - High volatility → Build (easier to adapt internally)

2. **Verification Difficulty** (1-5)
   - How hard is it to verify quality/outcomes?
   - Hard to verify → Build (better internal control)

3. **Interdependence** (1-5)
   - How tightly coupled with other systems?
   - High coupling → Build (easier integration)

4. **Data Sensitivity** (1-5, weighted 1.5x for healthcare)
   - PHI, proprietary data, regulatory requirements?
   - High sensitivity → Build (better control)

5. **Supplier Power** (1-5)
   - Risk of vendor lock-in?
   - High lock-in risk → Build (avoid dependence)

6. **Frequency/Tempo** (1-5)
   - How often is it used?
   - Constant use → Build (optimize for your needs)

## Key Insights from Coase

> "The limit to the size of the firm is set where its costs of organizing a transaction equal the cost of carrying it out in the market."

Translation for healthcare IT: Build when internal coordination is cheaper than vendor negotiations. Buy when the market has solved it efficiently.

## Quick Decision Guide

### Default to BUY when:
- It's a commodity problem (many vendors offer it)
- You need it in <6 months
- It requires regulatory approval (FDA)
- Multiple systems need the same capability

### Consider BUILD when:
- It's your unique competitive advantage
- You have proprietary data/protocols
- Integration complexity is extreme
- It's core to your mission

### Go HYBRID when:
- You can buy the platform and build the differentiators
- Some components are commodities, others are proprietary
- You need speed but also customization

## Getting Started

1. **For Python Analysis**:
   ```bash
   pip install pandas numpy
   python python/coasean_calculator.py
   ```

2. **For SQL Analysis**:
   - Adapt the queries to your database schema
   - Focus on Query 1 for initial portfolio assessment

3. **For Dashboard Creation**:
   - Start with the Portfolio Quadrant Chart
   - Add the Transaction Cost Heat Map
   - Implement filters for department/project type

## About This Framework

Based on Ronald Coase's 1937 paper "The Nature of the Firm" and subsequent transaction cost economics theory. Coase won the Nobel Prize in Economics in 1991 for this work.

The framework has been adapted for healthcare's unique considerations including HIPAA compliance, clinical validation requirements, and the critical nature of healthcare operations.

## Remember

As Coase taught us: Organizations exist because sometimes it's cheaper to coordinate internally than to use the market. Your AI strategy should follow this same principle.

**The bottom line**: Calculate your transaction costs. Let them guide your decision. Coase figured this out in 1937. What's your excuse?

---

*Part of the Vitals & Variables newsletter series on healthcare operations analytics.*