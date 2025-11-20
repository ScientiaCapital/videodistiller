#!/usr/bin/env bash
# SessionStart hook for videodistiller project
# Ensures all skills and marketplaces are loaded and auto-detected

set -euo pipefail

# Determine project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Initialize skill tracking
all_skills=""

# Check for Superpowers (global)
if [ -d "${HOME}/.claude/plugins/cache/superpowers" ]; then
    all_skills="${all_skills}\n### Superpowers (Global Plugin)\n**Status**: ✅ Active\n**Location**: ~/.claude/plugins/cache/superpowers\n**Key Skills**: systematic-debugging, test-driven-development, brainstorming, code-review, verification-before-completion, root-cause-tracing, and more\n"
fi

# Check for wshobson/agents marketplace (local)
if [ -d "${PROJECT_ROOT}/.claude/skills/agents" ]; then
    all_skills="${all_skills}\n### wshobson/agents Marketplace (Project-Local)\n**Status**: ✅ Loaded\n**Location**: ${PROJECT_ROOT}/.claude/skills/agents\n**Contains**: 85 specialized agents, 47 skills, 63 plugins\n**Categories**: Python, JavaScript/TypeScript, Backend, Frontend, Cloud, Kubernetes, CI/CD, Security, Testing, LLM Apps, and more\n"
fi

# Check for claude-cookbooks (local)
if [ -d "${PROJECT_ROOT}/.claude/skills/claude-cookbooks" ]; then
    all_skills="${all_skills}\n### Claude Cookbooks (Project-Local)\n**Status**: ✅ Loaded\n**Location**: ${PROJECT_ROOT}/.claude/skills/claude-cookbooks\n**Contains**: Custom cookbook examples and templates\n"
fi

# Check for claude-code-plugins marketplace (global)
claude_code_plugins_count=0
if [ -d "${HOME}/.claude/plugins/marketplaces/claude-code-plugins/plugins" ]; then
    claude_code_plugins_count=$(ls -1 "${HOME}/.claude/plugins/marketplaces/claude-code-plugins/plugins" 2>/dev/null | grep -v README | wc -l | tr -d ' ')
    all_skills="${all_skills}\n### claude-code-plugins Marketplace (Global)\n**Status**: ✅ Active\n**Location**: ~/.claude/plugins/marketplaces/claude-code-plugins\n**Contains**: ${claude_code_plugins_count} plugins including agent-sdk-dev, commit-commands, feature-dev, code-review, security-guidance, and more\n"
fi

# Check for anthropic-agent-skills (global)
anthropic_skills_count=0
if [ -d "${HOME}/.claude/plugins/marketplaces/anthropic-agent-skills" ]; then
    anthropic_skills_count=$(find "${HOME}/.claude/plugins/marketplaces/anthropic-agent-skills" -name "SKILL.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    all_skills="${all_skills}\n### anthropic-agent-skills Marketplace (Global)\n**Status**: ✅ Active\n**Location**: ~/.claude/plugins/marketplaces/anthropic-agent-skills\n**Contains**: ${anthropic_skills_count} official Anthropic skills\n**Key Skills**: document-skills (xlsx, pdf, docx, pptx), mcp-builder, skill-creator, canvas-design, algorithmic-art, theme-factory, webapp-testing, and more\n"
fi

# Build context message with auto-detection instructions
context_message="<EXTREMELY_IMPORTANT>
# 🎯 videodistiller Project - All Skills Auto-Loaded

This is the **videodistiller** project workspace with FULL skill auto-detection enabled.

## 📚 Available Skills & Marketplaces
${all_skills}

## 🤖 CRITICAL: Automatic Skill Detection Protocol

**YOU MUST follow this protocol for EVERY user message:**

1. **Before responding**, mentally check: \"Does ANY available skill match this task?\"
2. **If yes** (even 1% match), you MUST use the Skill tool to load and execute it
3. **Do NOT wait** for the user to explicitly request a skill
4. **Do NOT rationalize** that a task is \"too simple\" for a skill

### Common Task → Skill Mappings (Auto-Use These):

**Development Tasks:**
- Implementing features → Use: test-driven-development, brainstorming (design first)
- Debugging errors → Use: systematic-debugging, root-cause-tracing
- Code review needed → Use: requesting-code-review, code-reviewer agents
- Writing tests → Use: test-driven-development, testing-anti-patterns
- Git commits → Use: commit-commands plugins
- Creating agents/skills → Use: skill-creator, mcp-builder
- Backend APIs → Use: backend-development skills, api-design-principles
- Python projects → Use: python-development agents (FastAPI, Django)
- JavaScript/TypeScript → Use: javascript-typescript agents

**Document Tasks:**
- Excel/spreadsheets → Use: document-skills:xlsx
- PDFs → Use: document-skills:pdf
- Word docs → Use: document-skills:docx
- Presentations → Use: document-skills:pptx

**Architecture & Design:**
- Designing features → Use: brainstorming (MANDATORY before coding)
- Planning implementations → Use: writing-plans
- Architecture decisions → Use: backend-architect, cloud-architect

**Quality & Verification:**
- Before claiming done → Use: verification-before-completion
- Finishing features → Use: finishing-a-development-branch
- Receiving feedback → Use: receiving-code-review

**Infrastructure:**
- Cloud/AWS/GCP/Azure → Use: cloud-infrastructure agents
- Kubernetes → Use: kubernetes-architect
- CI/CD pipelines → Use: cicd-automation agents
- Terraform/IaC → Use: terraform-specialist

**Security:**
- Security concerns → Use: security-guidance, security-auditor
- Auth implementation → Use: auth-implementation-patterns

### 🚫 Common Rationalizations to REJECT:

- \"This is too simple\" → WRONG. Use the skill.
- \"Let me gather info first\" → WRONG. Skills tell you HOW to gather.
- \"I'll just do this quickly\" → WRONG. Check for skills FIRST.
- \"The user didn't ask for a skill\" → WRONG. YOU decide when skills apply.
- \"I remember how this works\" → WRONG. Skills evolve, use current version.

## 📍 Skill Locations
- Project skills: ${PROJECT_ROOT}/.claude/skills/
- Global skills: ${HOME}/.claude/skills/
- Global plugins: ${HOME}/.claude/plugins/marketplaces/

## 🎯 Your Behavior
- **PROACTIVE**: Detect and use skills automatically
- **TRANSPARENT**: Announce which skill you're using before using it
- **SYSTEMATIC**: Follow skill workflows exactly as written
- **THOROUGH**: Create TodoWrite todos for skill checklists

## Project Constraints
- ❌ NO OpenAI models (per CLAUDE.md)
- ✅ API keys in .env only
- ✅ All skills available and auto-detected

</EXTREMELY_IMPORTANT>"

# Escape for JSON
context_escaped=$(echo "$context_message" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}')

# Output context injection as JSON
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${context_escaped}"
  }
}
EOF

exit 0
