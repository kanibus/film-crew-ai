# 🤝 Contributing to Film Crew AI

First off, thank you for considering contributing to Film Crew AI! 🎬✨

Film Crew AI is a community project, and we welcome contributions from filmmakers, developers, AI enthusiasts, and anyone passionate about the intersection of cinema and artificial intelligence.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Creating New Agents](#creating-new-agents)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)

## 📜 Code of Conduct

By participating in this project, you agree to:
- 🤝 Be respectful and inclusive
- 🎯 Focus on constructive criticism
- 🌍 Welcome newcomers and help them get started
- 🚫 Avoid harassment, discrimination, or offensive behavior

## 🎯 How Can I Contribute?

### 🐛 Reporting Bugs

Found a bug? Help us fix it:
1. Check if the bug is already reported in [Issues](https://github.com/kanibus/film-crew-ai/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Node version, etc.)
   - Screenshots if applicable

### 💡 Suggesting Features

Have an idea? We'd love to hear it:
1. Check [existing feature requests](https://github.com/kanibus/film-crew-ai/issues?q=is%3Aissue+label%3Aenhancement)
2. Create a new issue with:
   - Use case description
   - Proposed solution
   - Alternative approaches considered
   - Mockups or examples if relevant

### 🤖 Creating New Agents

Want to add a specialized film production agent? 

#### Agent Template:
```markdown
---
name: your-agent-name
description: Clear description of agent's expertise. Use PROACTIVELY when...
---

You are a [Role] who [Philosophy and Expertise].

## Core Responsibilities:

1. **Primary Task**
   - Specific approach
   - Key considerations
   - Quality standards

2. **Secondary Tasks**
   - Supporting functions
   - Integration points

## Output Format:
{
  "field1": "description",
  "field2": ["array", "of", "values"],
  "nested": {
    "subfield": "value"
  }
}
```

#### Agent Ideas We'd Love:
- 🎨 **Color Grading Specialist** - Mood through color palettes
- 🎭 **Dialogue Coach** - Natural speech patterns and delivery
- 📐 **Aspect Ratio Advisor** - Framing for different platforms
- 🎪 **VFX Coordinator** - Special effects integration
- 📍 **Location Scout** - Setting authenticity and logistics

### 🌍 Translations

Help make Film Crew AI accessible globally:
- Translate documentation
- Localize agent prompts
- Add cultural context for different film traditions

### 📚 Documentation

Improve our docs:
- Fix typos and grammar
- Add examples and tutorials
- Create video walkthroughs
- Write blog posts about your experience

## 🛠️ Development Setup

### Prerequisites

```bash
# Required
Node.js 16+
Git
npm or yarn

# Optional but recommended
GitHub CLI
Visual Studio Code
```

### Local Development

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then:
   git clone https://github.com/kanibus/film-crew-ai.git
   cd film-crew-ai
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Install dependencies**
   ```bash
   install-film-crew.bat
   # or manually:
   npm install -g @anthropic-ai/claude-code
   npm install -g claude-flow@latest
   ```

4. **Make your changes**
   - Edit agents in `templates/agents/`
   - Edit commands in `templates/commands/`
   - Update documentation

5. **Test your changes**
   ```bash
   verify-installation.bat
   # Test with a sample script
   process-scripts.bat
   ```

## 📁 Project Structure

```
Key directories for contributors:

templates/agents/        # Film production agents
templates/commands/      # Workflow commands
config/                 # Configuration files
docs/                   # Documentation
scripts/                # Test scripts
```

## 🎬 Creating New Agents

### Step 1: Design Your Agent

Consider:
- What unique expertise does it bring?
- How does it integrate with existing agents?
- What output format makes sense?

### Step 2: Create Agent File

Create `templates/agents/your-agent.md`:

```markdown
---
name: your-agent
description: Concise description. MUST BE USED for specific tasks.
---

You are an expert [Role] with deep understanding of [Domain].

## Analysis Process:

1. **Phase One**
   - Task details
   - Methodology

2. **Phase Two**
   - Integration points
   - Quality checks

## Output Format:
{
  "analysis": {},
  "recommendations": [],
  "integration_notes": ""
}
```

### Step 3: Test Your Agent

1. Copy to active directory:
   ```bash
   copy templates\agents\your-agent.md .claude\agents\
   ```

2. Run test:
   ```bash
   process-scripts.bat
   ```

### Step 4: Document Your Agent

Add to README:
- Agent name and purpose
- When to use it
- Example output
- Integration with other agents

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure quality**:
   - ✅ Code follows style guidelines
   - ✅ Tests pass
   - ✅ Documentation updated
   - ✅ Commit messages are clear

2. **Create Pull Request**:
   ```bash
   git push origin feature/your-feature
   # Then on GitHub, click "Create Pull Request"
   ```

3. **PR Description Template**:
   ```markdown
   ## Summary
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] New agent
   - [ ] Documentation
   
   ## Testing
   - [ ] Tested locally
   - [ ] Added test scripts
   - [ ] Verified with sample data
   
   ## Screenshots
   (if applicable)
   ```

## 🎨 Style Guidelines

### For Agents

- **Naming**: Use kebab-case (e.g., `color-grading-specialist`)
- **Description**: Start with role, include "Use PROACTIVELY when..."
- **Output**: Always provide JSON structure
- **Tone**: Professional but accessible

### For Code

- **Batch Files**: Include clear comments and error handling
- **JSON**: Valid formatting, descriptive keys
- **Markdown**: Use headers, lists, and code blocks appropriately

### Commit Messages

Format: `type: description`

Examples:
- `feat: add color grading agent`
- `fix: correct camera angle calculations`
- `docs: update installation guide`
- `style: format agent templates`
- `refactor: simplify prompt combination logic`

## 🎯 Priority Areas

Current areas where we especially need help:

1. **🎬 Genre-Specific Agents** - Horror, Documentary, Animation specialists
2. **🌍 Internationalization** - Multi-language support
3. **🔌 Platform Integration** - Runway, Pika, Stability AI adapters
4. **📊 Performance** - Optimize for larger scripts
5. **🧪 Testing** - Automated test suites

## 💬 Getting Help

- 💭 **Discord**: [Join our community](https://discord.gg/filmcrewai)
- 🐛 **Issues**: [GitHub Issues](https://github.com/kanibus/film-crew-ai/issues)
- 📧 **Email**: filmcrewai@example.com

## 🙏 Recognition

Contributors will be:
- Listed in our [Contributors](README.md#contributors) section
- Credited in release notes
- Invited to our private Discord channel
- Given early access to new features

---

Thank you for helping make Film Crew AI better! 🎬✨

Every contribution, no matter how small, helps democratize film production through AI.