# videodistiller - Claude Skills Configuration

This project has **automatic skill detection** enabled. All skills from multiple marketplaces are loaded on session start.

## 🎯 Auto-Loaded Marketplaces

### ✅ Superpowers (Global Plugin)
- **Location**: `~/.claude/plugins/cache/superpowers`
- **Type**: Global workflow skills
- **Key Skills**:
  - systematic-debugging
  - test-driven-development
  - brainstorming
  - verification-before-completion
  - root-cause-tracing
  - requesting-code-review

### ✅ wshobson/agents (Project-Local)
- **Location**: `.claude/skills/agents`
- **Type**: Comprehensive agent marketplace
- **Contains**: 85 specialized agents, 47 skills, 63 plugins
- **Categories**: Python, JS/TS, Backend, Frontend, Cloud, K8s, CI/CD, Security, Testing, LLM Apps

### ✅ claude-code-plugins (Global)
- **Location**: `~/.claude/plugins/marketplaces/claude-code-plugins`
- **Type**: Development workflow plugins
- **Contains**: 12 plugins
- **Examples**: agent-sdk-dev, commit-commands, feature-dev, code-review, security-guidance

### ✅ anthropic-agent-skills (Global)
- **Location**: `~/.claude/plugins/marketplaces/anthropic-agent-skills`
- **Type**: Official Anthropic skills
- **Contains**: 15 skills
- **Examples**: document-skills (xlsx/pdf/docx/pptx), mcp-builder, skill-creator, canvas-design

## 🤖 How It Works

### Automatic Detection
When you open this project, the SessionStart hook automatically:
1. Detects all available skill marketplaces
2. Loads awareness of all skills and agents
3. Instructs Claude to proactively detect and use relevant skills

### You Don't Need to Call Skills
Claude will automatically:
- Check if any skill matches your task
- Use the appropriate skill without being asked
- Announce which skill it's using
- Follow the skill's workflow exactly

### Example Workflows
- **Feature development** → Automatically uses: brainstorming → test-driven-development
- **Debugging** → Automatically uses: systematic-debugging
- **Git commits** → Automatically uses: commit-commands
- **Excel work** → Automatically uses: document-skills:xlsx
- **Backend APIs** → Automatically uses: backend-architect + api-design-principles

## 📁 Project Structure

```
.claude/
├── hooks/
│   ├── hooks.json              # SessionStart hook configuration
│   └── session-start.sh        # Auto-load all marketplaces script
├── skills/
│   ├── agents/                 # wshobson/agents marketplace (85 agents)
│   └── claude-cookbooks/       # Custom cookbooks
├── context.md                  # Project context and progress
└── README.md                   # This file
```

## 🔄 Session Start Behavior

Every time you open this project or start a new session:
1. Hook runs automatically
2. All 4 marketplaces are detected
3. Claude receives comprehensive skill mapping
4. Auto-detection protocol is activated

## 📝 Project Context

See `.claude/context.md` for:
- Current project status
- Architecture decisions
- Recent changes
- Next steps

## 🚀 Quick Reference

### Available Task Categories
- **Development**: Python, JS/TS, Backend, Frontend
- **Infrastructure**: Cloud, Kubernetes, CI/CD, Terraform
- **Quality**: Testing, Code Review, Security
- **Documents**: Excel, PDF, Word, PowerPoint
- **AI/ML**: LLM apps, agents, RAG systems
- **Workflows**: Git, feature development, debugging

### Skill Locations
- Global skills: `~/.claude/skills/`
- Project skills: `.claude/skills/`
- Global plugins: `~/.claude/plugins/marketplaces/`

## ⚙️ Configuration

### Project Constraints (from CLAUDE.md)
- ❌ NO OpenAI models
- ✅ API keys in .env only
- ✅ All skills auto-detected

### Customization
To modify skill auto-detection behavior, edit:
- `.claude/hooks/session-start.sh` - Hook script
- `.claude/hooks/hooks.json` - Hook configuration

---

**Status**: ✅ All marketplaces configured and auto-detection enabled
**Last Updated**: 2025-11-20
