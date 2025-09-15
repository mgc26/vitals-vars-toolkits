# Coasean Build vs Buy Dashboard Template

## Dashboard Overview
This dashboard template helps visualize your organization's AI/analytics portfolio through Ronald Coase's transaction cost economics lens.

## Key Visualizations

### 1. Portfolio Quadrant Chart
**Chart Type**: Scatter Plot with Quadrants
- **X-Axis**: Total Coasean Score (0-30)
- **Y-Axis**: Annual Cost ($)
- **Size**: Team Size/Resources
- **Color**: Current Approach (Build/Buy/Hybrid)
- **Quadrants**:
  - Lower Left: "Buy Zone" (Score < 16, Low Cost)
  - Upper Left: "Strategic Buy" (Score < 16, High Cost)
  - Lower Right: "Tactical Build" (Score > 19, Low Cost)
  - Upper Right: "Strategic Build" (Score > 19, High Cost)

### 2. Transaction Cost Heat Map
**Chart Type**: Heat Map Matrix
- **Rows**: Projects/Capabilities
- **Columns**: 6 Coasean Factors
  - Spec Volatility
  - Verification Difficulty
  - Interdependence
  - Data Sensitivity
  - Supplier Power
  - Frequency/Tempo
- **Color Scale**: 1 (Green/Buy) to 5 (Red/Build)
- **Highlight**: Misaligned decisions in yellow border

### 3. Vendor Lock-in Risk Gauge
**Chart Type**: Gauge Charts Grid
- **Per Vendor**:
  - Switching Cost Multiplier (0-2x)
  - Risk Level (Green/Yellow/Red)
  - Years with Vendor
  - Integration Points Count

### 4. Build vs Buy Performance Comparison
**Chart Type**: Grouped Bar Chart
- **Metrics**:
  - Success Rate %
  - Average Cost Overrun %
  - Average Time Overrun %
  - User Satisfaction Score
- **Groups**: Build Projects vs Buy Projects
- **Reference Line**: Industry benchmarks

### 5. Hybrid Opportunity Matrix
**Chart Type**: Stacked Bar Chart
- **X-Axis**: Capability Areas
- **Y-Axis**: Component Count
- **Stack Segments**:
  - Commodity Components (Buy)
  - Proprietary Components (Build)
  - Neutral Components
- **Annotation**: Hybrid recommendation strength

### 6. Decision Alignment Tracker
**Chart Type**: Bullet Chart
- **Per Project**:
  - Current Approach
  - Recommended Approach
  - Alignment Status
  - Potential Savings

### 7. Coasean Score Distribution
**Chart Type**: Histogram with Reference Lines
- **X-Axis**: Coasean Score Bins
- **Y-Axis**: Project Count
- **Reference Lines**:
  - Buy Threshold (13)
  - Hybrid Zone (16-19)
  - Build Threshold (22)

## Key Metrics to Display

### Summary KPIs (Top of Dashboard)
1. **Portfolio Alignment Score**: % of projects following Coasean recommendation
2. **Total Potential Savings**: Sum of misalignment costs
3. **Average Transaction Cost Level**: Low/Medium/High
4. **Vendor Lock-in Exposure**: Total switching costs

### Detailed Metrics Table
| Project | Coasean Score | Current | Recommended | Annual Savings Potential |
|---------|---------------|---------|-------------|-------------------------|
| [Data]  | [Data]        | [Data]  | [Data]      | [Data]                  |

## Filter Controls
- Department/Division
- Project Type (AI/Analytics/Infrastructure)
- Budget Range
- Time Period
- Current Approach

## Drill-Down Capabilities
1. Click on project → Detailed 6-factor breakdown
2. Click on vendor → Integration dependency map
3. Click on capability → Component-level analysis

## Color Scheme
- **Green (#2ECC71)**: Buy/Low Risk/Aligned
- **Yellow (#F39C12)**: Hybrid/Medium Risk/Review
- **Red (#E74C3C)**: Build/High Risk/Misaligned
- **Blue (#3498DB)**: Current State
- **Gray (#95A5A6)**: Benchmark/Reference

## Data Refresh
- **Frequency**: Monthly
- **Sources**:
  - Project management systems
  - Vendor management database
  - Financial systems
  - User satisfaction surveys

## Implementation Notes

### For Tableau
1. Use parameter controls for Coasean weight adjustments
2. Create calculated field for dynamic score calculation
3. Use dashboard actions for drill-down navigation
4. Implement tooltips with Coase's insights

### For Power BI
1. Create measures for Coasean score calculation
2. Use slicers for interactive filtering
3. Implement bookmarks for different views
4. Use conditional formatting for risk indicators

### For Looker/Other BI Tools
1. Define LookML/semantic model for Coasean factors
2. Create derived tables for score calculations
3. Use liquid variables for dynamic thresholds
4. Implement row-level security for department views

## Dashboard Narrative
Include text box with:
"Based on Ronald Coase's 1937 insight: Organizations exist when internal coordination costs are lower than market transaction costs. This dashboard evaluates your portfolio through that lens."

## Export Capabilities
- PDF report for executive review
- Excel data dump for detailed analysis
- Scheduled email alerts for misalignments