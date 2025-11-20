# Project: videodistiller
Last Updated: 2025-11-20

## Project Overview
Video processing and distillation application

## Current Status
- Project initialized
- Hooks configured for automatic skills loading
- Superpowers and wshobson/agents marketplace available

## Architecture Overview
- Framework: TBD
- Key Dependencies: TBD
- Design Patterns: TBD

## Available Skills (Auto-Detected)

### Superpowers (Global)
- systematic-debugging - Four-phase debugging framework
- test-driven-development - RED-GREEN-REFACTOR workflow
- brainstorming - Design refinement before coding
- verification-before-completion - Evidence before assertions
- root-cause-tracing - Trace bugs to source
- requesting-code-review - Dispatch review agents
- And more workflow skills...

### wshobson/agents Marketplace (Project-Local)
- **85 specialized agents** across 63 plugins
- **47 agent skills** for progressive disclosure
- **Categories**:
  - Python (FastAPI, Django, async patterns)
  - JavaScript/TypeScript (modern ES6+, Node.js)
  - Backend (API design, microservices, GraphQL)
  - Frontend (React, mobile development)
  - Cloud (AWS, GCP, Azure, multi-cloud)
  - Kubernetes (GitOps, Helm, security)
  - CI/CD (GitHub Actions, GitLab, pipelines)
  - Security (auditing, scanning, compliance)
  - Testing (TDD, test automation)
  - LLM Apps (RAG, agents, prompt engineering)

### claude-code-plugins Marketplace (Global)
- **12 plugins** for development workflows
- agent-sdk-dev - Claude Agent SDK development
- commit-commands - Git commit automation
- feature-dev - Feature development workflows
- code-review - Code review agents
- security-guidance - Security best practices
- And more...

### anthropic-agent-skills Marketplace (Global)
- **15 official Anthropic skills**
- document-skills (xlsx, pdf, docx, pptx)
- mcp-builder - Build MCP servers
- skill-creator - Create new skills
- canvas-design - Visual design
- algorithmic-art - Generative art with p5.js
- theme-factory - Styling and themes
- webapp-testing - Playwright testing
- And more...

## Recent Changes
- 2025-11-20: Initial project setup
- 2025-11-20: Configured SessionStart hooks for automatic skill loading
- 2025-11-20: Added all marketplaces to auto-detection:
  - ✅ Superpowers (global)
  - ✅ wshobson/agents (project-local, 85 agents)
  - ✅ claude-code-plugins (global, 12 plugins)
  - ✅ anthropic-agent-skills (global, 15 skills)
- 2025-11-20: Enabled automatic skill detection protocol

## Next Steps
1. Define project requirements and architecture
2. Choose tech stack
3. Set up initial project structure
4. Begin implementation

## Notes
- NO OpenAI models to be used in this project (per CLAUDE.md)
- API keys must be stored in .env files only
