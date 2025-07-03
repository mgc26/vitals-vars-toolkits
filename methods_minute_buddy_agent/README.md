# Buddy Agent Workflow Toolkit

This toolkit provides everything you need to implement the Buddy Agent workflow in your healthcare analytics projects.

## Quick Start

1. **Install Prerequisites**
   ```bash
   # Ensure you have Claude Code installed
   # Install Gemini CLI
   pip install google-generativeai-cli
   ```

2. **Configure API Access**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. **Run Your First Buddy Agent Task**
   ```bash
   # Example: Analyze a complex SQL schema
   python buddy_agent_orchestrator.py \
     --task "analyze_schema" \
     --context "./database/schema.sql" \
     --output "./analysis_results.md"
   ```

## What's Included

### Core Scripts
- `buddy_agent_orchestrator.py` - Main orchestration script
- `context_gatherer.py` - Utilities for collecting and formatting context
- `prompt_templates.py` - Reusable prompt patterns for common tasks

### Healthcare-Specific Templates
- `templates/ed_analysis_prompt.txt` - ED boarding analysis template
- `templates/surgical_planning_prompt.txt` - OR efficiency template  
- `templates/staffing_prediction_prompt.txt` - Nurse staffing template
- `templates/revenue_cycle_prompt.txt` - Billing automation template

### Example Workflows
- `examples/simple_analysis.md` - Basic schema analysis
- `examples/complex_refactor.md` - Multi-file refactoring project
- `examples/documentation_synthesis.md` - Policy document analysis

## Implementation Guide

### Step 1: Context Collection
The key to effective buddy agent usage is comprehensive context. Use the provided context gatherer:

```python
from context_gatherer import ContextCollector

collector = ContextCollector()
collector.add_files(["*.sql", "*.py"])  # File patterns
collector.add_documentation("./docs")    # Documentation directory
collector.add_web_research(urls)         # External resources

context = collector.build_context()
```

### Step 2: Prompt Engineering
Structure your prompts for maximum effectiveness:

```python
from prompt_templates import HealthcarePromptBuilder

prompt = HealthcarePromptBuilder()
    .set_role("senior healthcare data architect")
    .set_task("analyze ED patient flow")
    .add_requirements([
        "Identify bottlenecks",
        "Suggest metrics",
        "Provide SQL implementation"
    ])
    .build()
```

### Step 3: Orchestration
Run the buddy agent workflow:

```python
from buddy_agent_orchestrator import BuddyAgent

agent = BuddyAgent()
result = agent.analyze(
    context=context,
    prompt=prompt,
    execute=True  # Auto-execute the plan
)
```

## Best Practices

### DO:
- Gather ALL relevant context upfront
- Be specific in your prompts
- Review plans before execution
- Start with smaller tasks to build confidence
- Save successful patterns for reuse

### DON'T:
- Skip context that seems "obvious"
- Use vague instructions
- Execute without review on production systems
- Ignore validation steps
- Forget to clean up temp files

## Common Healthcare Use Cases

### 1. Schema Analysis & Optimization
```bash
python buddy_agent_orchestrator.py \
  --task "optimize_schema" \
  --context "./epic_clarity/*.sql" \
  --prompt-template "schema_optimization"
```

### 2. Metric Development
```bash
python buddy_agent_orchestrator.py \
  --task "create_metrics" \
  --context "./requirements.md,./data_dictionary.csv" \
  --prompt-template "metric_development"
```

### 3. Compliance Checking
```bash
python buddy_agent_orchestrator.py \
  --task "compliance_audit" \
  --context "./policies/*.pdf,./current_reports.sql" \
  --prompt-template "compliance_check"
```

## Troubleshooting

### Large Context Issues
If context exceeds token limits:
1. Use the `--split-strategy` flag
2. Prioritize most relevant files
3. Summarize documentation first

### Execution Failures
If plans fail to execute:
1. Check the validation log
2. Run in `--dry-run` mode first
3. Break into smaller subtasks

## Advanced Usage

### Custom Validators
Add domain-specific validation:

```python
def validate_hipaa_compliance(code):
    # Custom validation logic
    return compliance_report

agent.add_validator(validate_hipaa_compliance)
```

### Multi-Agent Patterns
Chain multiple agents for complex workflows:

```python
# First agent: Analysis
analysis = analyst_agent.analyze(context, analysis_prompt)

# Second agent: Implementation  
implementation = coder_agent.implement(analysis, coding_prompt)

# Third agent: Testing
tests = tester_agent.create_tests(implementation, test_prompt)
```

## Community Contributions

Share your healthcare-specific templates and workflows:
- Fork this repository
- Add your templates to `community/`
- Submit a pull request

## Support

- GitHub Issues: [Report bugs or request features]
- Discord: [Join our healthcare AI community]
- Email: vitals-vars@example.com

---

Remember: The buddy agent is a tool, not a replacement for domain expertise. Always validate outputs against healthcare best practices and compliance requirements.