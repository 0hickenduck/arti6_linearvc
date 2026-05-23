# Project Instructions & Agent Guidelines

## 🤖 Two Sets of Agents: The Mental Model
When operating in this project, you have access to two distinct sets of agents. You must choose the right one for the job to balance cognitive capability and token efficiency.

### 1. Native GPT Sub-agents (The Thinkers)
- **How to invoke:** Use your native `spawn_agent` tool (or standard subagent protocols).
- **When to use:** Complex architectural design, difficult refactoring, and tasks that require high-level reasoning.
- **Cost:** High token usage.

### 2. Gemini Sub-agents (The Worker Bees)
- **How to invoke:** Use your native `bash` tool to execute the global delegation script.
- **When to use:** Searching large codebases, reading extensive documentation, generating boilerplate, or isolated tasks that don't require your advanced reasoning.
- **Cost:** Highly efficient. Saves your context window.

#### How to Delegate to Gemini (Worker Bee)
Run the following exact command in your bash tool:

```bash
~/.gemini/extensions/superpowers/skills/delegate-to-gemini/delegate.sh --model <model> --prompt "<instructions>"
```

**Parameters:**
- `--model flash`: (`gemini-3-flash-preview`) For fast reading, searching, and simple queries.
- `--model pro`: (`gemini-3.1-pro-preview`) For heavier code generation and editing.
- `--model auto`: Default behavior.
- `--prompt`: Detailed instructions of what you want the worker bee to do.

**Behavior:**
The Gemini agent runs autonomously in the background. Your bash tool will block until it finishes. Read the stdout output, verify the results, and continue your orchestration.
