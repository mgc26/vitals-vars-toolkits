#!/usr/bin/env python3
"""
Buddy Agent Orchestrator - Main implementation of the Buddy Agent workflow
for healthcare analytics tasks.
"""

import os
import sys
import subprocess
import tempfile
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime


class BuddyAgent:
    """Orchestrates collaboration between Claude Code and Gemini CLI"""
    
    def __init__(self, gemini_path: str = "gemini"):
        self.gemini_path = gemini_path
        self.temp_dir = tempfile.mkdtemp(prefix="buddy_agent_")
        self.context_file = Path(self.temp_dir) / "buddy_agent_context.tmp"
        self.prompt_file = Path(self.temp_dir) / "buddy_agent_prompt.txt"
        self.validators = []
        
    def analyze(self, context: str, prompt: str, execute: bool = False) -> Dict:
        """
        Main workflow execution
        
        Args:
            context: Consolidated context for analysis
            prompt: Instruction prompt for Gemini
            execute: Whether to auto-execute the returned plan
            
        Returns:
            Dictionary with analysis results and execution status
        """
        # Step 1: Save context and prompt
        self._save_files(context, prompt)
        
        # Step 2: Invoke Gemini
        print("🧠 Consulting research agent...")
        result = self._invoke_gemini()
        
        # Step 3: Validate the plan
        validation_results = self._validate_plan(result)
        
        # Step 4: Execute if requested
        execution_results = None
        if execute and validation_results['passed']:
            print("🤖 Executing plan...")
            execution_results = self._execute_plan(result)
            
        # Step 5: Cleanup
        self._cleanup()
        
        return {
            'plan': result,
            'validation': validation_results,
            'execution': execution_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _save_files(self, context: str, prompt: str):
        """Save context and prompt to temporary files"""
        with open(self.context_file, 'w') as f:
            f.write(context)
        with open(self.prompt_file, 'w') as f:
            f.write(prompt)
            
    def _invoke_gemini(self) -> str:
        """Call Gemini CLI with context and prompt"""
        cmd = [
            self.gemini_path,
            "--prompt", f"$(cat {self.prompt_file})",
            "--file", str(self.context_file)
        ]
        
        # Use shell=True to handle command substitution
        shell_cmd = f'{self.gemini_path} --prompt "$(cat {self.prompt_file})" --file {self.context_file}'
        
        try:
            result = subprocess.run(
                shell_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error invoking Gemini: {e}")
            print(f"stderr: {e.stderr}")
            return ""
    
    def _validate_plan(self, plan: str) -> Dict:
        """Run validation checks on the generated plan"""
        results = {
            'passed': True,
            'checks': []
        }
        
        # Basic validation
        if not plan:
            results['passed'] = False
            results['checks'].append({
                'name': 'plan_exists',
                'passed': False,
                'message': 'No plan generated'
            })
            
        # Run custom validators
        for validator in self.validators:
            check_result = validator(plan)
            results['checks'].append(check_result)
            if not check_result['passed']:
                results['passed'] = False
                
        return results
    
    def _execute_plan(self, plan: str) -> Dict:
        """Execute the generated plan step by step"""
        # This is a simplified execution - in practice, you'd parse
        # the plan and execute each step programmatically
        execution_log = {
            'steps': [],
            'success': True
        }
        
        # Log the plan for manual execution
        plan_file = Path(self.temp_dir) / "execution_plan.md"
        with open(plan_file, 'w') as f:
            f.write(plan)
            
        execution_log['steps'].append({
            'action': 'save_plan',
            'file': str(plan_file),
            'status': 'completed'
        })
        
        print(f"✅ Plan saved to: {plan_file}")
        print("📋 Review and execute the plan manually or enhance this script for auto-execution")
        
        return execution_log
    
    def _cleanup(self):
        """Remove temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            
    def add_validator(self, validator_func):
        """Add a custom validation function"""
        self.validators.append(validator_func)


class ContextCollector:
    """Utility for gathering and formatting context"""
    
    def __init__(self):
        self.sections = []
        
    def add_files(self, patterns: List[str], base_path: str = "."):
        """Add files matching patterns to context"""
        for pattern in patterns:
            files = Path(base_path).glob(pattern)
            for file in files:
                if file.is_file():
                    self.add_file(file)
                    
    def add_file(self, filepath: Path):
        """Add a single file to context"""
        try:
            content = filepath.read_text()
            self.sections.append({
                'type': 'file',
                'path': str(filepath),
                'content': content
            })
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            
    def add_documentation(self, doc_path: str):
        """Add all documentation from a directory"""
        doc_patterns = ["*.md", "*.txt", "*.rst"]
        for pattern in doc_patterns:
            self.add_files([f"{doc_path}/**/{pattern}"], ".")
            
    def add_text(self, title: str, content: str):
        """Add arbitrary text section"""
        self.sections.append({
            'type': 'text',
            'title': title,
            'content': content
        })
        
    def build_context(self) -> str:
        """Build formatted context string"""
        context_parts = ["# CONTEXT FOR BUDDY AGENT\n"]
        
        for section in self.sections:
            if section['type'] == 'file':
                context_parts.append(f"\n## File: {section['path']}")
                context_parts.append("```")
                context_parts.append(section['content'])
                context_parts.append("```")
            elif section['type'] == 'text':
                context_parts.append(f"\n## {section['title']}")
                context_parts.append(section['content'])
                
        return "\n".join(context_parts)


def main():
    parser = argparse.ArgumentParser(
        description='Buddy Agent Orchestrator for Healthcare Analytics'
    )
    parser.add_argument(
        '--task',
        required=True,
        help='Task type (analyze_schema, create_metrics, etc.)'
    )
    parser.add_argument(
        '--context',
        required=True,
        help='Files or directories to include in context (comma-separated)'
    )
    parser.add_argument(
        '--prompt-template',
        help='Use a predefined prompt template'
    )
    parser.add_argument(
        '--custom-prompt',
        help='Custom prompt text'
    )
    parser.add_argument(
        '--output',
        help='Output file for results'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Auto-execute the generated plan'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )
    
    args = parser.parse_args()
    
    # Build context
    collector = ContextCollector()
    
    # Add user request
    collector.add_text("User Request", f"Task: {args.task}")
    
    # Add context files
    context_items = args.context.split(',')
    for item in context_items:
        item = item.strip()
        if '*' in item:
            # It's a pattern
            collector.add_files([item])
        elif Path(item).is_dir():
            # It's a directory
            collector.add_documentation(item)
        elif Path(item).is_file():
            # It's a file
            collector.add_file(Path(item))
        else:
            print(f"Warning: {item} not found")
    
    context = collector.build_context()
    
    # Build prompt
    if args.prompt_template:
        # Load from template
        template_path = Path(__file__).parent / "templates" / f"{args.prompt_template}.txt"
        if template_path.exists():
            prompt = template_path.read_text()
        else:
            print(f"Error: Template {args.prompt_template} not found")
            sys.exit(1)
    elif args.custom_prompt:
        prompt = args.custom_prompt
    else:
        # Default prompt
        prompt = """You are a senior healthcare data architect. Analyze the provided context and create a detailed implementation plan.

The plan should include:
1. Understanding of the current state
2. Specific steps to achieve the goal
3. Code snippets where applicable
4. Validation steps
5. Potential risks and mitigations

Format your response as structured markdown."""
    
    # Run analysis
    agent = BuddyAgent()
    
    if args.dry_run:
        print("DRY RUN - Would analyze with:")
        print(f"Context length: {len(context)} characters")
        print(f"Prompt: {prompt[:200]}...")
    else:
        results = agent.analyze(
            context=context,
            prompt=prompt,
            execute=args.execute
        )
        
        # Save results
        if args.output:
            output_path = Path(args.output)
            if output_path.suffix == '.json':
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
            else:
                with open(output_path, 'w') as f:
                    f.write(results['plan'])
            print(f"Results saved to: {output_path}")
        else:
            print("\nGenerated Plan:")
            print("=" * 50)
            print(results['plan'])


if __name__ == "__main__":
    main()