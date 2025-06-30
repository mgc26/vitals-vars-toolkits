# Meta-Instruction Driver: The Buddy Agent Workflow (v2)

## 1. Overview and Purpose

This document outlines a meta-workflow for an AI agent (the "Executor") to collaborate with a powerful, large-context "Buddy Agent" (e.g., Gemini via the `gemini` CLI). The purpose of this workflow is to delegate complex research, analysis, and planning tasks to the Buddy Agent, allowing the Executor to focus on the precise, hands-on tasks of code modification and tool execution.

- **The Executor (You)**: Your primary role is to interact with the user, execute commands, and manage the local environment. You are the "hands" of the operation.
- **The Buddy Agent (e.g., Gemini)**: Its primary role is to perform deep reasoning on large amounts of provided context. It can analyze long documents, synthesize information from multiple sources, and formulate strategic plans. It is the "brain" of the operation.

**The core principle is: Use the Buddy Agent whenever the path forward requires more than simple file manipulation or direct command execution.**

## 2. Delegation Triggers: When to Use the Buddy Agent

As the Executor, you should delegate to the Buddy Agent when you encounter the following situations:

- **Complex Planning & Scaffolding**: The user asks to build a new feature, create a new application, or perform a complex refactoring.
- **Deep Document Analysis**: The user asks a question that requires understanding a large, dense document (or multiple documents).
- **Ambiguous Bug Investigation**: The user reports a vague bug, and the root cause is not immediately obvious after initial log/file review.
- **Best Practices & Architectural Decisions**: The user asks an open-ended question about the best way to implement a feature or structure code.
- **Web Research Integration**: The task requires external information like library documentation or API specifications.

## 3. The Delegation Workflow: A Step-by-Step Guide

When a trigger is met, follow this procedure:

1.  **Acknowledge and State Intent**: Inform the user that the task requires deep analysis and that you will consult your research agent. (e.g., "This task requires some planning. I will consult my research agent to formulate a robust strategy.")

2.  **Gather and Consolidate Context**: Use your tools (`read_many_files`, `glob`) to collect all relevant text. Concatenate all this information into a single temporary file named `buddy_agent_context.tmp`. Structure it with clear headings.

    ```markdown
    # CONTEXT FOR BUDDY AGENT

    ## User Request
    <User's original prompt>

    ## File: /path/to/main.py
    ```python
    <Content of main.py>
    ```

    ## File: /path/to/requirements.txt
    ```
    <Content of requirements.txt>
    ```

    ## Web Research: Some Library Docs
    <Content from web_fetch tool>
    ```

3.  **Formulate a Clear Prompt**: Create a separate, concise prompt file named `buddy_agent_prompt.txt`. This prompt should instruct the Buddy Agent on how to process the context.

    ```text
    You are a senior software architect. Your goal is to produce a step-by-step implementation plan.

    Analyze the context provided via the --file argument. Based on the user's request and the provided files, generate a detailed plan. The plan should specify which files to create or modify and include the exact code to be used.

    Output the plan in structured Markdown.
    ```

4.  **Invoke the Buddy Agent**: Use the `run_shell_command` to call the `gemini` CLI. Pass the context file using the `--file` flag and the prompt using the `--prompt` flag.

    ```bash
    gemini --prompt "$(cat buddy_agent_prompt.txt)" --file buddy_agent_context.tmp
    ```
    *(Note: The exact flags `--prompt` and `--file` are based on typical CLI design and should be verified from the official Gemini CLI documentation if available.)*

5.  **Receive and Validate the Plan**: The Buddy Agent will return a strategic plan. Review this plan for coherence and safety. Present the high-level plan to the user for confirmation before proceeding.

6.  **Execute the Plan Step-by-Step**: Once the user approves, execute the plan provided by the Buddy Agent. Treat it as a checklist. After each significant step, perform a validation check (e.g., run tests, lint the file).

7.  **Clean Up**: Remove the temporary files (`buddy_agent_context.tmp`, `buddy_agent_prompt.tmp`).

## 4. Example Scenario: Planning a New Feature

-   **User**: "I want to add OAuth2 authentication to my Python web service."
-   **Executor's Actions**:
    1.  **Acknowledge**: "Okay, adding authentication requires a careful plan. I will consult my research agent to design the best approach."
    2.  **Gather & Consolidate**: Use `read_many_files` to get the content of `main.py` and `requirements.txt`. Use `write_file` to create `buddy_agent_context.tmp` containing this information.
    3.  **Formulate Prompt**: Use `write_file` to create `buddy_agent_prompt.txt` with instructions to create a plan for adding OAuth2 to a FastAPI service.
    4.  **Invoke**: Execute `run_shell_command` with the command: `gemini --prompt "$(cat buddy_agent_prompt.txt)" --file buddy_agent_context.tmp`
    5.  **Validate & Execute**: Present the returned plan to the user. Upon approval, use `write_file` and `replace` to implement the changes.
    6.  **Clean Up**: Run `rm buddy_agent_context.tmp buddy_agent_prompt.tmp`.